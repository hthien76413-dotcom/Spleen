#!/usr/bin/env python3
"""Write the two starter workbooks for the 10-report extraction calibration (extraction guide section 10).

Each starter is the normal extraction template with FT_log and IPD_requests removed, the 10 report ids and the extractor code
filled into the Reports sheet, a Calibration_list sheet (the 10 reports with title, DOI and link, no strata) and a README for
the calibration. Patients is left empty: the children are unknown until the full text has been read. Nothing else is filled
in; in particular no value from the database records, the full-text logs or the pilot table is copied in.

Usage:  python3 -I tools/make_calibration_starters.py [LIST_CSV] [--out-dir DIR]
Default LIST_CSV: search/extraction/calibration/calibration_10_list.csv (written by tools/draw_extraction_calibration.py).
Writes extraction_E1_calibration_starter.xlsx and extraction_E2_calibration_starter.xlsx into DIR (default: the folder of the
list). Needs openpyxl; builds the template with tools/build_extraction_workbook.py first.
"""
import argparse
import csv
import os
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
from openpyxl import load_workbook
from openpyxl.styles import Alignment, Font, PatternFill

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
_ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
_ap.add_argument("list_csv", nargs="?", default=os.path.join(ROOT, "search", "extraction", "calibration", "calibration_10_list.csv"))
_ap.add_argument("--out-dir", default=None)
ARGS = _ap.parse_args()
OUT_DIR = ARGS.out_dir or os.path.dirname(os.path.abspath(ARGS.list_csv))
FIRST = 4
NAMES = {"E1": "舒俊", "E2": "卞红强"}

README = [
    ("title", "提取校准：先做 10 篇（起始表）"),
    ("warn", "这份文件里只有 10 篇报告的编号和提取员代码，没有任何数据。请只根据全文填写；做完之前不要打开对方的文件，也不要看预试验提取表，不要讨论具体的报告。"),
    ("h", "要做什么"),
    ("b", "提取员：E1 = 舒俊，E2 = 卞红强（Reports 表的 extractor 列已填好；Patients 表里新增的每一行也要填上）。一人一份，另存为自己的副本（`extraction_E1.xlsx` 或 `extraction_E2.xlsx`），每次用完另存带日期的副本，不覆盖旧的。"),
    ("b", "Calibration_list 表是这 10 篇的名单（编号、标题、DOI、链接）。用自己电脑里已有的全文，按 WS 编号命名（如 WS0159.pdf）；PDF 和提取表都不要放进仓库。逐例资料在线上附录或补充材料里的，附录也要取到，取不到的告诉杨俊。"),
    ("b", "先读完整篇，再填表。Reports 表：每篇一行（已建好 10 行，其余列自己填）。Patients 表：每名符合条件的儿童一行，patient_id 写成 WS0159_P1、WS0159_P2…，report_id 填 WS 编号，extractor 填 E1 或 E2。"),
    ("b", "哪些儿童提取、哪些不提取：只提取 18 岁以下、报告里有个体描述的儿童；成人不提取；只有汇总数据的，人数填 Reports 表 n_children_aggregate，不进 Patients 表（提取说明第 3 节）。"),
    ("b", "两个关键变量：指数发作的持续天数（按 9 条换算规则，同时填 idx_dur_verbatim 原文写法和出处 src_exposure）；脾脏术中是否存活（viability，同时填依据 viab_basis 和出处 src_outcome）。规则和例子见提取说明第 5–8 节。"),
    ("b", "空白 = 还没提取；NR = 报告里没有这项信息。不要凭印象猜一个值，也不要用空白表示'报告没写'。拿不准的写在 notes，留待共识讨论。"),
    ("b", "灰色列是公式，不要改；表头前三行和 Lists 表不要改。下拉列表的格子不要手打列表以外的值。"),
    ("b", "只录不可识别的信息：不写姓名、住院号、出生日期、具体日期。"),
    ("b", "【不是提取规则，是请求】抽样时按摘要关键词没有找到用'范围'写法（如'2–3 个月'）表示病程的报告。若读全文时发现哪篇用了这种写法，请在该篇 notes 里写 range-wording，并把 WS 编号告诉杨俊。"),
    ("h", "做完以后"),
    ("b", "保存前对照提取说明第 11.1 节的自查清单；然后运行 `python3 -I tools/compare_extraction.py check 你的文件.xlsx --extractor E1`（E2 同理），把格式错误改掉。check 只看格式，不看对错，也不显示对方的任何内容。"),
    ("b", "把自己的文件交杨俊保管（提取说明第 2.1 节）。两人都交了以后，由杨俊决定谁运行 `compare`；分歧清单发给两位提取员，先讨论，讨论不了的交杨俊，把统一的读法写进提取说明第 12 节。"),
    ("b", "校准只有 10 篇，患者可能只有二三十人，kappa 不可靠，主要看分歧清单。校准用的 10 篇在正式提取里照样再做一遍，用校准后的规则。"),
    ("h", "没有验证的事"),
    ("b", "这份文件没有在 Excel 或 WPS 里打开过；下拉列表和版面实际是否正常没有验证。"),
]


def put_readme(ws, lines):
    ws.delete_rows(1, ws.max_row + 5)
    ws.column_dimensions["A"].width = 150
    for r, (kind, text) in enumerate(lines, start=1):
        c = ws.cell(row=r, column=1, value=("• " + text) if kind == "b" else text)
        c.alignment = Alignment(wrap_text=True, vertical="top")
        if kind == "title":
            c.font = Font(bold=True, size=14)
        elif kind == "warn":
            c.font = Font(bold=True, color="C00000")
            c.fill = PatternFill("solid", fgColor="FDE9D9")
        elif kind == "h":
            c.font = Font(bold=True, size=12, color="FFFFFF")
            c.fill = PatternFill("solid", fgColor="2F75B5")
        ws.row_dimensions[r].height = max(18, 16 * (-(-len(text) // 70)))


def read_list():
    with open(ARGS.list_csv, encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))
    need = ["position", "ws_id", "year", "language", "has_abstract", "title", "doi", "url"]
    if not rows or list(rows[0].keys()) != need:
        sys.exit("The list must have exactly the columns %s (found %s)" % (need, list(rows[0].keys()) if rows else "no rows"))
    return rows


def main():
    rows = read_list()
    tmp = tempfile.mkdtemp(prefix="calstart_")
    tpl = os.path.join(tmp, "template.xlsx")
    subprocess.run([sys.executable, "-I", os.path.join(HERE, "build_extraction_workbook.py"), tpl], check=True, stdout=subprocess.DEVNULL)
    os.makedirs(OUT_DIR, exist_ok=True)
    for code in ("E1", "E2"):
        wb = load_workbook(tpl)
        for name in ("FT_log", "IPD_requests"):
            if name in wb.sheetnames:
                del wb[name]
        ws = wb["Reports"]
        codes = {ws.cell(row=1, column=c).value: c for c in range(1, ws.max_column + 1) if ws.cell(row=1, column=c).value}
        for i, rec in enumerate(rows):
            ws.cell(row=FIRST + i, column=codes["report_id"], value=rec["ws_id"])
            ws.cell(row=FIRST + i, column=codes["extractor"], value=code)
        put_readme(wb["README"], README)
        cl = wb.create_sheet("Calibration_list", 1)
        heads = ["No.", "WS ID", "Year", "Language", "Abstract in database record", "Title", "DOI", "Link"]
        for j, h in enumerate(heads, start=1):
            c = cl.cell(row=1, column=j, value=h)
            c.font = Font(bold=True, color="FFFFFF")
            c.fill = PatternFill("solid", fgColor="2F75B5")
        for i, rec in enumerate(rows, start=2):
            vals = [int(rec["position"]), rec["ws_id"], rec["year"], rec["language"], rec["has_abstract"], rec["title"], rec["doi"], rec["url"]]
            for j, v in enumerate(vals, start=1):
                cl.cell(row=i, column=j, value=v).alignment = Alignment(wrap_text=(j == 6), vertical="top")
        for col, w in zip("ABCDEFGH", (6, 10, 7, 10, 12, 70, 34, 60)):
            cl.column_dimensions[col].width = w
        cl.freeze_panes = "A2"
        wb["Reports"].sheet_properties.tabColor = "C00000"
        wb["Patients"].sheet_properties.tabColor = "C00000"
        wb.active = 0
        wb.properties.title = "Extraction calibration starter %s (blank)" % code
        wb.properties.creator = "Wandering spleen SR team"
        out = os.path.join(OUT_DIR, "extraction_%s_calibration_starter.xlsx" % code)
        wb.save(out)
        print("saved", out, "| starter for", code, "(" + NAMES[code] + ") |", len(rows), "report rows")


if __name__ == "__main__":
    main()
