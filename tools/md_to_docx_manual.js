// Convert the screening-manual Markdown to a Word document with docx@9.
// Based on md_to_docx.js (used for the screening guide) and extended with:
//   # title            first H1 = document title (the paragraph right after it = subtitle)
//   ## / ### / ####    Heading 1 / 2 / 3
//   :::warn Title ... :::   callout boxes: warn | tip | verify | rule | suggest (inner Markdown allowed)
//   - [ ] text         checklist item
//   ![alt|width](path) image (PNG), width in px at 96 dpi (default 600); path relative to the .md file
//   > text             caption (centred, small)
//   \pagebreak         page break
//   <!-- widths: 20,30,50 -->  or  <!-- kv; widths: 20,80 -->   hint for the NEXT table (percent widths; kv = key/value table without header)
//   <br> inside a table cell = new paragraph in the cell
//   @@GUIDE_TABLE <heading prefix>@@   copies the first table under that heading from the guide .md
// Usage: NODE_PATH=<dir containing docx> node md_to_docx_manual.js input.md output.docx "footer text" [guide.md]
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, AlignmentType, HeadingLevel,
  LevelFormat, BorderStyle, ShadingType, Footer, PageNumber, ImageRun, PageBreak, Tab, TabStopType, VerticalAlign,
} = require("docx");

const [, , inFile, outFile, footerText, guideFile] = process.argv;
const baseDir = path.dirname(path.resolve(inFile));
const lines = fs.readFileSync(inFile, "utf-8").replace(/\r/g, "").split("\n");
const guideLines = guideFile ? fs.readFileSync(guideFile, "utf-8").replace(/\r/g, "").split("\n") : [];

const FONT = { ascii: "Calibri", hAnsi: "Calibri", cs: "Calibri", eastAsia: "Microsoft YaHei" };
const MONO = { ascii: "Consolas", hAnsi: "Consolas", cs: "Consolas", eastAsia: "Microsoft YaHei" };
const SYMBOL = { ascii: "Segoe UI Symbol", hAnsi: "Segoe UI Symbol", cs: "Segoe UI Symbol", eastAsia: "MS Gothic" };
const TEXT_W = 9026; // A4 with 1-inch side margins, in DXA
const TBL_SIZE = 19; // 9.5 pt

const CALLOUTS = {
  warn: { fill: "FDECEA", bar: "C0392B", label: "注意" },
  tip: { fill: "EAF2FB", bar: "2E75B6", label: "提示" },
  verify: { fill: "FFF6DD", bar: "C99700", label: "待核实" },
  rule: { fill: "EAF6EA", bar: "2E8B57", label: "规则" },
  suggest: { fill: "F1ECFA", bar: "7E57C2", label: "建议" },
};

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

function vlen(s) {
  let n = 0;
  for (const ch of s.replace(/\*\*|`/g, "")) n += /[⺀-鿿＀-￯]/.test(ch) ? 2 : 1;
  return n;
}

function pngSize(buf) {
  if (buf.length < 24 || buf.readUInt32BE(0) !== 0x89504e47) throw new Error("only PNG images are supported");
  return { w: buf.readUInt32BE(16), h: buf.readUInt32BE(20) };
}

const isTableLine = (l) => /^\s*\|.*\|\s*$/.test(l);
const splitCells = (l) => l.trim().replace(/^\||\|$/g, "").split("|").map((c) => c.trim());
const BLOCK_START = /^(#{1,4}\s|---+\s*$|\s*[-*]\s|\s*\d+\.\s|\s*\||:::|!\[|>|@@|<!--|\\pagebreak|```)/;

let numInstance = 0;

function guideTable(prefix) {
  let idx = guideLines.findIndex((l) => /^#{1,4}\s/.test(l) && l.replace(/^#{1,4}\s+/, "").startsWith(prefix));
  if (idx < 0) throw new Error("guide heading not found: " + prefix);
  while (idx < guideLines.length && !isTableLine(guideLines[idx])) idx++;
  const rows = [];
  while (idx < guideLines.length && isTableLine(guideLines[idx])) { rows.push(splitCells(guideLines[idx])); idx++; }
  return rows;
}

function makeTable(rows, opts) {
  const body = rows.filter((r, idx) => !(idx === 1 && r.every((c) => /^:?-{2,}:?$/.test(c))));
  const n = body[0].length;
  let widths;
  if (opts.widths && opts.widths.length === n) {
    const total = opts.widths.reduce((a, b) => a + b, 0);
    widths = opts.widths.map((p) => Math.round((p / total) * TEXT_W));
  } else {
    const weight = Array.from({ length: n }, (_, c) => {
      const lens = body.map((r) => vlen(r[c] || ""));
      const avg = lens.reduce((a, b) => a + b, 0) / lens.length;
      return Math.min(70, Math.max(7, 0.6 * avg + 0.4 * Math.min(Math.max(...lens), 60)));
    });
    const tw = weight.reduce((a, b) => a + b, 0);
    widths = weight.map((w) => Math.max(Math.round((w / tw) * TEXT_W), 900));
  }
  const diff = TEXT_W - widths.reduce((a, b) => a + b, 0);
  widths[n - 1] += diff;
  const border = { style: BorderStyle.SINGLE, size: 4, color: "BBBBBB" };
  const borders = { top: border, bottom: border, left: border, right: border };
  const cellParas = (text, base) => text.split(/<br\s*\/?>/i).map((part, k, arr) =>
    new Paragraph({ children: runs(part.trim(), base), spacing: { after: k < arr.length - 1 ? 40 : 0 } }));
  return new Table({
    width: { size: TEXT_W, type: WidthType.DXA },
    columnWidths: widths,
    rows: body.map((r, ri) => {
      const isHead = !opts.kv && ri === 0;
      return new TableRow({
        tableHeader: isHead,
        cantSplit: true,
        children: Array.from({ length: n }, (_, ci) => {
          const c = r[ci] || "";
          const keyCol = opts.kv && ci === 0;
          return new TableCell({
            width: { size: widths[ci], type: WidthType.DXA },
            borders,
            verticalAlign: VerticalAlign.TOP,
            margins: { top: 55, bottom: 55, left: 95, right: 95 },
            shading: isHead ? { type: ShadingType.CLEAR, fill: "E8EEF4" } : keyCol ? { type: ShadingType.CLEAR, fill: "F2F5F9" } : undefined,
            children: cellParas(c, isHead || keyCol ? { bold: true, size: TBL_SIZE } : { size: TBL_SIZE }),
          });
        }),
      });
    }),
  });
}

function callout(type, title, inner) {
  const st = CALLOUTS[type];
  const kids = [new Paragraph({ children: [new TextRun({ text: title || st.label, bold: true, font: FONT, size: 21, color: st.bar })], spacing: { after: 60 }, keepNext: true }), ...inner];
  if (!(kids[kids.length - 1] instanceof Paragraph)) kids.push(new Paragraph({ children: [] }));
  const thin = { style: BorderStyle.SINGLE, size: 4, color: "D9D9D9" };
  return [
    new Table({
      width: { size: TEXT_W, type: WidthType.DXA },
      columnWidths: [TEXT_W],
      rows: [new TableRow({ cantSplit: false, children: [new TableCell({
        width: { size: TEXT_W, type: WidthType.DXA },
        borders: { top: thin, bottom: thin, right: thin, left: { style: BorderStyle.SINGLE, size: 24, color: st.bar } },
        shading: { type: ShadingType.CLEAR, fill: st.fill },
        margins: { top: 90, bottom: 90, left: 160, right: 140 },
        children: kids,
      })] })],
    }),
    new Paragraph({ spacing: { after: 100 }, children: [] }),
  ];
}

function parseBlocks(src) {
  const out = [];
  let i = 0;
  let pending = {};
  let titleDone = false;
  while (i < src.length) {
    const l = src[i];
    if (!l.trim()) { i++; continue; }
    let m;

    if (/^```/.test(l)) {
      i++;
      const code = [];
      while (i < src.length && !/^```/.test(src[i])) { code.push(src[i]); i++; }
      i++; // closing fence
      code.forEach((cl, k) => out.push(new Paragraph({
        spacing: { after: k === code.length - 1 ? 140 : 0, line: 260 },
        shading: { type: ShadingType.CLEAR, fill: "F2F2F2" },
        indent: { left: 200, right: 200 },
        children: [new TextRun({ text: cl === "" ? " " : cl, font: MONO, size: 18 })],
      })));
      continue;
    }
    if (/^\\pagebreak\s*$/.test(l.trim())) { out.push(new Paragraph({ children: [new PageBreak()] })); i++; continue; }
    if ((m = l.match(/^<!--\s*(.*?)\s*-->\s*$/))) {
      pending = { kv: /\bkv\b/.test(m[1]) };
      const w = m[1].match(/widths:\s*([\d.,\s]+)/);
      if (w) pending.widths = w[1].split(",").map((x) => parseFloat(x));
      i++; continue;
    }
    if (/^---+\s*$/.test(l)) {
      out.push(new Paragraph({ border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: "999999", space: 1 } }, spacing: { before: 120, after: 120 } }));
      i++; continue;
    }
    if ((m = l.match(/^:::(\w+)\s*(.*)$/)) && CALLOUTS[m[1]]) {
      const type = m[1], title = m[2].trim();
      const inner = [];
      i++;
      while (i < src.length && src[i].trim() !== ":::") { inner.push(src[i]); i++; }
      i++; // closing :::
      out.push(...callout(type, title, parseBlocks(inner)));
      continue;
    }
    if ((m = l.match(/^(#{1,4})\s+(.*)$/))) {
      const lvl = m[1].length;
      if (lvl === 1 && !titleDone) {
        titleDone = true;
        out.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 400, after: 160 }, children: [new TextRun({ text: m[2], bold: true, size: 48, color: "1F3A5F", font: FONT })] }));
        i++;
        while (i < src.length && !src[i].trim()) i++;
        if (i < src.length && !BLOCK_START.test(src[i])) {
          out.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 360 }, children: [new TextRun({ text: src[i].trim(), size: 26, color: "555555", font: FONT })] }));
          i++;
        }
        continue;
      }
      const level = [HeadingLevel.HEADING_1, HeadingLevel.HEADING_1, HeadingLevel.HEADING_2, HeadingLevel.HEADING_3][lvl - 1];
      out.push(new Paragraph({ heading: level, children: runs(m[2]), keepNext: true, keepLines: true }));
      i++; continue;
    }
    if ((m = l.match(/^!\[(.*?)(?:\|(\d+))?\]\((.+?)\)\s*$/))) {
      const file = path.resolve(baseDir, m[3]);
      const data = fs.readFileSync(file);
      const { w, h } = pngSize(data);
      const width = parseInt(m[2] || "600", 10);
      out.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 120, after: 60 }, keepNext: true, children: [
        new ImageRun({ type: "png", data, transformation: { width, height: Math.round((width * h) / w) }, altText: { title: m[1], description: m[1], name: path.basename(file) } }),
      ] }));
      i++; continue;
    }
    if ((m = l.match(/^>\s?(.*)$/))) {
      out.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 160 }, children: runs(m[1], { size: 18, color: "666666" }) }));
      i++; continue;
    }
    if ((m = l.match(/^@@GUIDE_TABLE\s+(.+?)@@\s*$/))) {
      out.push(makeTable(guideTable(m[1]), pending)); pending = {};
      out.push(new Paragraph({ spacing: { after: 120 }, children: [] }));
      i++; continue;
    }
    if (isTableLine(l)) {
      const rows = [];
      while (i < src.length && isTableLine(src[i])) { rows.push(splitCells(src[i])); i++; }
      out.push(makeTable(rows, pending)); pending = {};
      out.push(new Paragraph({ spacing: { after: 120 }, children: [] }));
      continue;
    }
    if ((m = l.match(/^(\s*)[-*]\s+\[( |x)\]\s+(.*)$/))) {
      out.push(new Paragraph({
        tabStops: [{ type: TabStopType.LEFT, position: 560 }],
        indent: { left: 560, hanging: 380 }, spacing: { after: 70 },
        children: [new TextRun({ text: m[2] === "x" ? "☑" : "☐", font: SYMBOL, size: 22 }), new TextRun({ children: [new Tab()] }), ...runs(m[3])],
      }));
      i++; continue;
    }
    if ((m = l.match(/^(\s*)[-*]\s+(.*)$/))) {
      out.push(new Paragraph({ numbering: { reference: "bul", level: m[1].length >= 2 ? 1 : 0 }, children: runs(m[2]), spacing: { after: 60 } }));
      i++; continue;
    }
    if ((m = l.match(/^(\s*)(\d+)\.\s+(.*)$/))) {
      const prev = out[out.length - 1];
      if (!prev || !prev.__num) numInstance++;
      const p = new Paragraph({ numbering: { reference: "num", level: m[1].length >= 2 ? 1 : 0, instance: numInstance }, children: runs(m[3]), spacing: { after: 60 } });
      p.__num = true;
      out.push(p);
      i++; continue;
    }
    let text = l.trim();
    i++;
    while (i < src.length && src[i].trim() && !BLOCK_START.test(src[i])) { text += src[i].trim(); i++; }
    out.push(new Paragraph({ children: runs(text), spacing: { after: 120 } }));
  }
  return out;
}

const children = parseBlocks(lines);

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
  title: "筛选操作手册",
  styles: {
    default: { document: { run: { font: FONT, size: 21 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 32, bold: true, font: FONT, color: "1F3A5F" }, paragraph: { spacing: { before: 360, after: 160 }, outlineLevel: 0 } },
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
      new TextRun({ text: " 页 / 共 ", font: FONT, size: 17, color: "777777" }),
      new TextRun({ children: [PageNumber.TOTAL_PAGES], font: FONT, size: 17, color: "777777" }),
      new TextRun({ text: " 页", font: FONT, size: 17, color: "777777" }),
    ] })] }) },
    children,
  }],
});

Packer.toBuffer(doc).then((buf) => { fs.writeFileSync(outFile, buf); console.log("written", buf.length); });
