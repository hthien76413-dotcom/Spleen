// Convert a simple Markdown file (headings, paragraphs, bullet/numbered lists with one nesting level, pipe tables,
// **bold**, `code`, horizontal rules) to a Word document with docx@9.
// Usage: NODE_PATH=<dir containing docx> node md_to_docx.js input.md output.docx ["footer text"]
const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, AlignmentType, HeadingLevel,
  LevelFormat, BorderStyle, ShadingType, Footer, PageNumber,
} = require("docx");

const [, , inFile, outFile, footerText] = process.argv;
const lines = fs.readFileSync(inFile, "utf-8").replace(/\r/g, "").split("\n");

const FONT = { ascii: "Calibri", hAnsi: "Calibri", cs: "Calibri", eastAsia: "Microsoft YaHei" };
const MONO = { ascii: "Consolas", hAnsi: "Consolas", cs: "Consolas", eastAsia: "Microsoft YaHei" };
const TEXT_W = 9026; // A4 with 1-inch margins, in DXA

function runs(text, base = {}) {
  const out = [];
  const re = /(\*\*[^*]+\*\*|`[^`]+`)/g;
  let last = 0, m;
  while ((m = re.exec(text)) !== null) {
    if (m.index > last) out.push(new TextRun({ text: text.slice(last, m.index), font: FONT, ...base }));
    const tok = m[0];
    if (tok.startsWith("**")) out.push(new TextRun({ text: tok.slice(2, -2).replace(/`/g, ""), bold: true, font: FONT, ...base }));
    else out.push(new TextRun({ text: tok.slice(1, -1), font: MONO, size: (base.size || 21) - 2, shading: { type: ShadingType.CLEAR, fill: "EEEEEE" }, ...base, bold: base.bold }));
    last = m.index + tok.length;
  }
  if (last < text.length) out.push(new TextRun({ text: text.slice(last), font: FONT, ...base }));
  return out;
}

const children = [];
let numInstance = 0;
let i = 0;

function isTableLine(l) { return /^\s*\|.*\|\s*$/.test(l); }
function cells(l) { return l.trim().replace(/^\||\|$/g, "").split("|").map((c) => c.trim()); }

while (i < lines.length) {
  const l = lines[i];
  if (!l.trim()) { i++; continue; }

  if (/^---+\s*$/.test(l)) {
    children.push(new Paragraph({ border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: "999999", space: 1 } }, spacing: { before: 120, after: 120 } }));
    i++; continue;
  }
  let m;
  if ((m = l.match(/^(#{1,3})\s+(.*)$/))) {
    const lvl = m[1].length;
    children.push(new Paragraph({
      heading: [HeadingLevel.HEADING_1, HeadingLevel.HEADING_2, HeadingLevel.HEADING_3][lvl - 1],
      children: runs(m[2]), keepNext: true,
    }));
    i++; continue;
  }
  if (isTableLine(l)) {
    const rows = [];
    while (i < lines.length && isTableLine(lines[i])) { rows.push(cells(lines[i])); i++; }
    const body = rows.filter((r, idx) => !(idx === 1 && r.every((c) => /^:?-{2,}:?$/.test(c))));
    const n = body[0].length;
    const widths = n === 2 ? [4300, TEXT_W - 4300] : n === 3 ? [900, 2400, TEXT_W - 3300] : Array(n).fill(Math.floor(TEXT_W / n));
    const sum = widths.reduce((a, b) => a + b, 0);
    widths[n - 1] += TEXT_W - sum;
    const border = { style: BorderStyle.SINGLE, size: 4, color: "BBBBBB" };
    const borders = { top: border, bottom: border, left: border, right: border };
    children.push(new Table({
      width: { size: TEXT_W, type: WidthType.DXA },
      columnWidths: widths,
      rows: body.map((r, ri) => new TableRow({
        tableHeader: ri === 0,
        cantSplit: true,
        children: r.map((c, ci) => new TableCell({
          width: { size: widths[ci], type: WidthType.DXA },
          borders,
          margins: { top: 60, bottom: 60, left: 100, right: 100 },
          shading: ri === 0 ? { type: ShadingType.CLEAR, fill: "E8EEF4" } : undefined,
          children: [new Paragraph({ children: runs(c, ri === 0 ? { bold: true, size: 20 } : { size: 20 }) })],
        })),
      })),
    }));
    children.push(new Paragraph({ spacing: { after: 120 } }));
    continue;
  }
  if ((m = l.match(/^(\s*)[-*]\s+(.*)$/))) {
    const level = m[1].length >= 2 ? 1 : 0;
    children.push(new Paragraph({ numbering: { reference: "bul", level }, children: runs(m[2]), spacing: { after: 60 } }));
    i++; continue;
  }
  if ((m = l.match(/^(\s*)(\d+)\.\s+(.*)$/))) {
    // start a new numbered list instance when the previous block was not a numbered item
    const prev = children[children.length - 1];
    if (!prev || !prev.__num) numInstance++;
    const p = new Paragraph({ numbering: { reference: "num", level: m[1].length >= 2 ? 1 : 0, instance: numInstance }, children: runs(m[3]), spacing: { after: 60 } });
    p.__num = true;
    children.push(p);
    i++; continue;
  }
  // paragraph: merge following plain lines
  let text = l.trim();
  i++;
  while (i < lines.length && lines[i].trim() && !/^(#{1,3}\s|---+\s*$|\s*[-*]\s|\s*\d+\.\s|\s*\|)/.test(lines[i])) { text += lines[i].trim(); i++; }
  children.push(new Paragraph({ children: runs(text), spacing: { after: 120 } }));
}

const bulletLevels = [0, 1].map((level) => ({
  level, format: LevelFormat.BULLET, text: level === 0 ? "•" : "◦", alignment: AlignmentType.LEFT,
  style: { paragraph: { indent: { left: 540 + level * 360, hanging: 270 } } },
}));
const numLevels = [0, 1].map((level) => ({
  level, format: LevelFormat.DECIMAL, text: level === 0 ? "%1." : "%2.", alignment: AlignmentType.LEFT,
  style: { paragraph: { indent: { left: 540 + level * 360, hanging: 360 } } },
}));

const doc = new Document({
  creator: "Wandering spleen review team",
  title: "Screening guide",
  styles: {
    default: { document: { run: { font: FONT, size: 21 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 32, bold: true, font: FONT, color: "1F3A5F" }, paragraph: { spacing: { before: 120, after: 160 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 26, bold: true, font: FONT, color: "1F3A5F" }, paragraph: { spacing: { before: 280, after: 120 }, outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 23, bold: true, font: FONT, color: "333333" }, paragraph: { spacing: { before: 200, after: 80 }, outlineLevel: 2 } },
    ],
  },
  numbering: { config: [
    { reference: "bul", levels: bulletLevels },
    { reference: "num", levels: numLevels },
  ] },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1300, bottom: 1300, left: 1440, right: 1440 } } },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [
      new TextRun({ text: (footerText || "") + (footerText ? "   |   " : "") + "第 ", font: FONT, size: 17, color: "777777" }),
      new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 17, color: "777777" }),
      new TextRun({ text: " 页", font: FONT, size: 17, color: "777777" }),
    ] })] }) },
    children,
  }],
});

Packer.toBuffer(doc).then((buf) => { fs.writeFileSync(outFile, buf); console.log("written", buf.length); });
