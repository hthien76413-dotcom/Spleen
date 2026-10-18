#!/usr/bin/env python3
"""Build the extraction / full-text workbook template for the wandering-spleen systematic review.

Source of every field and allowed value: protocol v1.4 (tools/build_protocol.js) Appendix C, Sections 8, 12, 13, 14, 16.
Everything that goes beyond Appendix C is listed on the README sheet under "Differences from Appendix C" and is
Claude's operationalisation, awaiting the three reviewers' approval.

Usage:  python3 -I tools/build_extraction_workbook.py "<output>.xlsx"
Full-text calibration workbook (FT_log + FT_time_log + the list of reports only, WS ids pre-filled; guide section 12):
        python3 -I tools/build_extraction_workbook.py "<output>.xlsx" --ft-only --reviewer R1 \
            --prefill search/screening/fulltext/calibration_20_list.csv
Requires openpyxl.
"""
import argparse
import csv
import re
import sys
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

VERSION = "v2026-10-18a"
_ap = argparse.ArgumentParser(description="Build the extraction / full-text workbook (see the module docstring).")
_ap.add_argument("out", nargs="?", default="Extraction workbook - template (draft).xlsx")
_ap.add_argument("--ft-only", action="store_true", help="only README, FT_log, FT_time_log, Calibration_list and Lists, with the WS ids of --prefill filled in")
_ap.add_argument("--reviewer", choices=["R1", "R2"], help="with --ft-only: value of the reviewer column")
_ap.add_argument("--prefill", help="with --ft-only: CSV with the columns position, ws_id, year, language, has_abstract, title, doi, url")
_ap.add_argument("--rows", type=int, default=40, help="with --ft-only: pre-formatted FT_log and FT_time_log rows (default 40)")
ARGS = _ap.parse_args()
OUT = ARGS.out
RIS = "search/dedup/records_deduplicated.ris"
REVIEWER_NAME = {"R1": "舒俊", "R2": "卞红强"}

N_PAT, N_REP, N_FT, N_IPD, N_TIME = 1500, 800, 2000, 300, 300  # pre-formatted rows
FIRST = 4  # first data row on the data sheets (rows 1-3 = header block)

# ----------------------------------------------------------------------------- lists
LISTS = {
    "yn": ["Yes", "No"],
    "yn_nr": ["Yes", "No", "NR"],
    "sex": ["M", "F", "NR"],
    "lang": ["English", "Chinese"],
    "ft_lang": ["English", "Chinese", "Other"],
    "design": ["Case report", "Case series", "Cohort", "Letter", "Review with new patients"],
    "consecutive": ["Yes", "No", "Unclear"],
    "aetiology": ["Congenital", "Acquired", "NR"],
    "ws_basis": [
        "Imaging shows ectopic position or mobility",
        "Operation shows ectopic position or mobility",
        "Imaging and operation",
        "Named wandering spleen, no detail",
        "Torsion only, position not stated",
    ],
    "presentation": ["Acute", "Chronic or intermittent", "Acute on chronic", "Asymptomatic", "Mass only"],
    "deferred_reason": ["Family declined", "Observation advised", "Elective operation scheduled", "Other", "Not applicable"],
    "torsion_awaiting": ["Yes", "No", "Not applicable"],
    "perfusion": ["Normal", "Reduced", "Absent", "NR"],
    "approach": ["Open", "Laparoscopic", "Converted", "Not applicable", "NR"],
    "viability": ["Viable", "Partially non-viable", "Non-viable", "NR", "Not applicable"],
    "viab_basis": ["Intraoperative", "Histology", "Both", "NR", "Not applicable"],
    "procedure": [
        "Detorsion only", "Splenopexy", "Partial splenectomy +/- splenopexy", "Total splenectomy",
        "Autotransplantation", "No operation", "NR",
    ],
    "fixation": [
        "Mesh", "Retroperitoneal or extraperitoneal pouch", "Omental wrap", "Direct suture",
        "Other (specify)", "Not applicable", "NR",
    ],
    "reason_removed": ["Failure of fixation", "Surgeon's preference", "Other", "Not applicable"],
    "status_fu": ["Preserved", "Partially preserved", "Lost", "NR"],
    "dur_category": ["<=2 d", "3-7 d", "8-30 d", ">30 d"],
    "units": ["hours", "days", "weeks", "months", "years"],
    "phrase": ["none", "Less than 24 hours / a few hours / overnight"],
    "extractor": ["E1", "E2", "Consensus"],
    "ft_reviewer": ["R1", "R2", "Consensus"],
    "ft_decision": ["Include", "Exclude", "Pending IPD"],
    "ft_reason": [
        "L other language", "D no full text", "E1 non-human", "E2 not wandering spleen", "E3 adults only",
        "E4 no original patient data", "E5 not a formal article", "E6 other",
        "A aggregate data only", "N age not confirmed under 18",
    ],
    "route": [
        "Publisher or open access", "Library subscription", "Interlibrary loan or document delivery",
        "CNKI or Wanfang", "Contact author", "Other", "Not obtained",
    ],
    "ipd_final": ["Pending", "Included with IPD", "Narrative only (no individual data)", "Not eligible after check"],
    "ipd_received": ["No", "Yes", "Partial"],
}
LIST_COL = {}  # list name -> column letter on the Lists sheet
LIST_RANGE = {}  # list name -> absolute range string


def list_ref(name):
    return LIST_RANGE[name]  # OOXML wants the range without a leading "="


# ----------------------------------------------------------------------------- styles
thin = Side(style="thin", color="BBBBBB")
BORDER = Border(left=thin, right=thin, top=thin, bottom=thin)
WRAP = Alignment(wrap_text=True, vertical="top")
HDR_FONT = Font(bold=True, color="FFFFFF")
GREY = PatternFill("solid", fgColor="E7E6E6")
SECTION_FILL = {
    "id": "44546A", "patient": "2F75B5", "timeline": "548235", "invest": "BF8F00",
    "oper": "C55A11", "followup": "7030A0", "source": "7F7F7F", "report": "2F75B5",
    "ft": "2F75B5", "ipd": "548235",
}


def hdr_fill(sec):
    return PatternFill("solid", fgColor=SECTION_FILL[sec])


# ----------------------------------------------------------------------------- column specs
# kind: text | date | int | num_nr | int_nr | ("list", name) | ("formula", key)
# (code, appendix-C label, hint (Chinese + allowed values), kind, width, section)
PATIENT_COLS = [
    ("patient_id", "Patient ID", "报告编号_P序号，如 WS0123_P1；本机构为 OWN_P1–OWN_P5", "text", 14, "id"),
    ("report_id", "Report ID", "WS 编号（Reports 表里要有同一编号）；本机构病例用 OWN", "text", 11, "id"),
    ("extractor", "Extractor", "E1 = 舒俊，E2 = 卞红强，Consensus = 共识", ("list", "extractor"), 11, "id"),
    ("date_extracted", "Date extracted", "yyyy-mm-dd", "date", 12, "id"),
    ("own_patient", "Own patient (derived)", "公式，勿改：report_id 为 OWN 时为 Yes（敏感性分析 1）", ("formula", "own"), 10, "id"),
    ("same_patient_as", "Same patient as", "与另一报告重复时，填更完整那篇里的 patient_id；否则留空", "text", 14, "id"),
    # B. Patient
    ("age_years", "Age at operation", "岁，两位小数（月数 ÷ 12）；未报告填 NR。≥18 的不应出现在此表", "num_nr", 9, "patient"),
    ("age_verbatim", "Age (verbatim)", "原文写法，如 '3 months'、'患儿'", "text", 16, "patient"),
    ("sex", "Sex", "M / F / NR", ("list", "sex"), 6, "patient"),
    ("cond_gv", "Gastric volvulus", "Yes / No / NR", ("list", "yn_nr"), 8, "patient"),
    ("cond_goo", "Gastric outlet obstruction", "Yes / No / NR", ("list", "yn_nr"), 9, "patient"),
    ("cond_panc_tail", "Pancreatic tail torsion", "第 13 节；Yes / No / NR", ("list", "yn_nr"), 9, "patient"),
    ("cond_bowel_obs", "Bowel obstruction", "第 13 节；Yes / No / NR", ("list", "yn_nr"), 9, "patient"),
    ("cond_dh", "Diaphragmatic hernia or eventration", "Yes / No / NR", ("list", "yn_nr"), 10, "patient"),
    ("cond_kidney", "Absent or ectopic left kidney", "Yes / No / NR", ("list", "yn_nr"), 10, "patient"),
    ("cond_prune", "Prune belly syndrome", "Yes / No / NR", ("list", "yn_nr"), 8, "patient"),
    ("cond_prev_surg", "Previous abdominal surgery", "Yes / No / NR", ("list", "yn_nr"), 9, "patient"),
    ("prev_surg_type", "Previous abdominal surgery (type)", "手术类型，如 fundoplication；无则留空", "text", 16, "patient"),
    ("cond_syndrome", "Syndrome", "如 trisomy 21；无综合征填 None，未报告填 NR", "text", 14, "patient"),
    ("cond_other", "Other associated condition", "其他，自由文本", "text", 16, "patient"),
    ("aetiology", "Aetiology", "Congenital / Acquired / NR", ("list", "aetiology"), 11, "patient"),
    ("aetiology_cause", "Aetiology (cause)", "获得性时写明原因", "text", 14, "patient"),
    ("ws_basis", "Basis for wandering spleen (added)", "报告凭什么说是游走脾（待确认，见 README 差异 A5）", ("list", "ws_basis"), 22, "patient"),
    # C. Timeline
    ("presentation", "Presentation", "Acute / Chronic or intermittent / Acute on chronic / Asymptomatic / Mass only", ("list", "presentation"), 16, "timeline"),
    ("idx_dur_verbatim", "Index-episode duration (verbatim)", "原文写法", "text", 20, "timeline"),
    ("idx_dur_days", "Index-episode duration (days)", "天，按下方 Rules 表规则；含糊或没有填 NR", "num_nr", 10, "timeline"),
    ("idx_dur_rules", "Rule(s) applied", "用了第几条换算规则，如 2;3", "text", 9, "timeline"),
    ("idx_dur_intermittent", "Intermittent / worsening flag", "Yes / No（规则 6）", ("list", "yn"), 11, "timeline"),
    ("idx_dur_alt_days", "Alternative coding (days)", "规则 6 的备选编码（加重时段）；没有则留空", "num_nr", 11, "timeline"),
    ("idx_dur_lower_bound", "Lower-bound flag", "规则 9：用入院时持续时间并作为下限时填 Yes", ("list", "yn"), 10, "timeline"),
    ("idx_dur_cat_imprecise", "Category if duration imprecise", "规则 5：只有所有合理理解都在同一类别时才填", ("list", "dur_category"), 11, "timeline"),
    ("idx_dur_category", "Duration category (derived)", "公式，勿改：<=2 d / 3-7 d / 8-30 d / >30 d", ("formula", "cat"), 11, "timeline"),
    ("total_hist_verbatim", "Total symptom history (verbatim)", "原文写法", "text", 20, "timeline"),
    ("total_hist_days", "Total symptom history (days)", "天；没有填 NR", "num_nr", 10, "timeline"),
    ("n_earlier_episodes", "Number of earlier episodes", "整数 / NR", "int_nr", 9, "timeline"),
    ("missed_dx", "Missed diagnosis", "Yes / No / NR", ("list", "yn_nr"), 9, "timeline"),
    ("missed_dx_alt", "Alternative diagnosis made", "当时做了什么诊断", "text", 18, "timeline"),
    ("missed_dx_contact", "Contact at which missed", "在哪一次就诊", "text", 16, "timeline"),
    ("known_dx_deferred", "Known diagnosis, surgery deferred", "Yes / No / NR", ("list", "yn_nr"), 11, "timeline"),
    ("deferred_reason", "Reason for deferral", "Family declined / Observation advised / Elective operation scheduled / Other / Not applicable", ("list", "deferred_reason"), 16, "timeline"),
    ("waiting_interval_days", "Waiting interval (days)", "天；规则 7；没有填 NR 或留空", "num_nr", 10, "timeline"),
    ("torsion_awaiting", "Torsion while awaiting surgery", "Yes / No / Not applicable", ("list", "torsion_awaiting"), 12, "timeline"),
    # D. Investigations
    ("img_us", "Imaging: US", "Yes / No / NR", ("list", "yn_nr"), 7, "invest"),
    ("img_doppler", "Imaging: Doppler US", "Yes / No / NR", ("list", "yn_nr"), 8, "invest"),
    ("img_ct", "Imaging: CT", "Yes / No / NR", ("list", "yn_nr"), 7, "invest"),
    ("img_mri", "Imaging: MRI", "Yes / No / NR", ("list", "yn_nr"), 7, "invest"),
    ("whirl_sign", "Whirl sign", "Yes / No / NR", ("list", "yn_nr"), 8, "invest"),
    ("perfusion", "Splenic perfusion", "Normal / Reduced / Absent / NR", ("list", "perfusion"), 10, "invest"),
    ("platelets", "Preoperative platelet count", "×10⁹/L；NR", "num_nr", 10, "invest"),
    ("thrombocytosis", "Thrombocytosis (derived)", "公式，勿改：>450 ×10⁹/L 为 Yes", ("formula", "plt"), 11, "invest"),
    # E. Operation
    ("approach", "Approach", "Open / Laparoscopic / Converted；未手术填 Not applicable", ("list", "approach"), 13, "oper"),
    ("torsion_at_op", "Torsion at operation", "Yes / No / NR", ("list", "yn_nr"), 9, "oper"),
    ("torsion_degrees", "Degrees of torsion", "度数；NR", "num_nr", 8, "oper"),
    ("viability", "Splenic viability (primary outcome)", "Viable / Partially non-viable / Non-viable / NR；未手术填 Not applicable", ("list", "viability"), 16, "oper"),
    ("viab_basis", "Basis of viability", "Intraoperative / Histology / Both / NR", ("list", "viab_basis"), 13, "oper"),
    ("procedure", "Procedure", "协议五项加 No operation（第 7 节）与 NR", ("list", "procedure"), 24, "oper"),
    ("procedure_other", "Other procedures", "如 gastropexy、hernia repair；自由文本", "text", 18, "oper"),
    ("fixation", "Fixation technique", "Mesh / pouch / Omental wrap / Direct suture / Other / Not applicable / NR", ("list", "fixation"), 22, "oper"),
    ("fixation_other", "Fixation technique (specify)", "选 Other 时写明", "text", 16, "oper"),
    ("spleen_size_cm", "Spleen size (longest dimension, cm)", "厘米；NR", "num_nr", 10, "oper"),
    ("reason_viable_removed", "Reason for removing a viable spleen", "Failure of fixation / Surgeon's preference / Other / Not applicable", ("list", "reason_removed"), 16, "oper"),
    ("primary_outcome", "Primary outcome (derived)", "公式，勿改：见 Rules 表 D3；Review 的由共识解决", ("formula", "outcome"), 16, "oper"),
    # F. Follow-up
    ("followup_months", "Length of follow-up", "月；NR", "num_nr", 9, "followup"),
    ("recurrence", "Recurrence or re-torsion", "Yes / No / NR", ("list", "yn_nr"), 10, "followup"),
    ("further_surgery", "Further surgery", "Yes / No / NR", ("list", "yn_nr"), 9, "followup"),
    ("recurrence_details", "Recurrence / further surgery details", "自由文本", "text", 20, "followup"),
    ("status_last_fu", "Splenic status at last follow-up", "Preserved / Partially preserved / Lost / NR", ("list", "status_fu"), 13, "followup"),
    ("post_splenectomy_compl", "Post-splenectomy complications", "自由文本", "text", 20, "followup"),
    # sources and notes
    ("src_age_sex", "Source: age, sex", "页 / 表 / 图", "text", 12, "source"),
    ("src_exposure", "Source: duration, history", "页 / 表 / 图（主要暴露的出处必填）", "text", 12, "source"),
    ("src_outcome", "Source: viability, procedure", "页 / 表 / 图（主要结局的出处必填）", "text", 12, "source"),
    ("src_other", "Source: other items", "页 / 表 / 图", "text", 12, "source"),
    ("notes", "Notes", "任何需要共识讨论的问题", "text", 30, "source"),
]

REPORT_COLS = [
    ("report_id", "Report ID", "WS 编号；本机构用 OWN", "text", 11, "id"),
    ("first_author", "First author", "", "text", 16, "report"),
    ("year", "Year", "发表年份", "int", 7, "report"),
    ("journal", "Journal", "", "text", 24, "report"),
    ("country", "Country", "", "text", 12, "report"),
    ("language", "Language", "English / Chinese", ("list", "lang"), 10, "report"),
    ("design", "Design", "Case report / Case series / Cohort / Letter / Review with new patients", ("list", "design"), 20, "report"),
    ("consecutive", "Consecutive series", "Yes / No / Unclear", ("list", "consecutive"), 11, "report"),
    ("institution", "Institution", "用于重复核对", "text", 26, "report"),
    ("study_period", "Study period", "用于重复核对", "text", 14, "report"),
    ("linked_duplicates", "Linked duplicate reports", "同一患者的其他报告 WS 编号", "text", 16, "report"),
    ("n_children_individual", "Children with individual data", "整数", "int", 11, "report"),
    ("n_children_aggregate", "Children aggregate-only", "整数；>0 时去 IPD_requests 表登记", "int", 11, "report"),
    ("pub_period", "Period of publication (derived)", "公式，勿改：before 2000 / 2000-2014 / 2015 onward（第 16 节）", ("formula", "period"), 14, "report"),
    ("extractor", "Extractor", "E1 = 舒俊，E2 = 卞红强，Consensus", ("list", "extractor"), 11, "id"),
    ("date_extracted", "Date extracted", "yyyy-mm-dd", "date", 12, "id"),
    ("notes", "Notes", "", "text", 30, "source"),
]

FT_COLS = [
    ("ws_id", "WS ID", "WS 编号", "text", 10, "id"),
    ("citation", "First author, year", "便于核对，如 Smith 2015", "text", 20, "ft"),
    ("language", "Language", "English / Chinese / Other（Other 单独计数，不提取）", ("list", "ft_lang"), 10, "ft"),
    ("reviewer", "Reviewer", "R1 = 舒俊，R2 = 卞红强（全文阶段），Consensus", ("list", "ft_reviewer"), 10, "id"),
    ("date", "Date", "yyyy-mm-dd", "date", 12, "id"),
    ("fulltext_obtained", "Full text obtained", "Yes / No", ("list", "yn"), 9, "ft"),
    ("route", "Route", "最终取得或最后尝试的途径", ("list", "route"), 26, "ft"),
    ("routes_tried", "Routes tried", "没拿到全文（D）时写明试过什么", "text", 26, "ft"),
    ("decision", "Decision", "Include / Exclude / Pending IPD（只有汇总数据，已或将索取）", ("list", "ft_decision"), 12, "ft"),
    ("reason", "Reason", "Exclude 必选；Pending IPD 选 A；Include 留空", ("list", "ft_reason"), 28, "ft"),
    ("n_children_individual", "Children with individual data", "整数", "int", 10, "ft"),
    ("n_children_aggregate", "Children aggregate-only", "整数", "int", 10, "ft"),
    ("ws_basis", "Basis for wandering spleen", "仅 Include 时填（指南 D1 已决定：宽松加标记）", ("list", "ws_basis"), 24, "ft"),
    ("duplicate_of", "Duplicate of (WS ID)", "与哪篇重复患者；仍是 Include，只是链接", "text", 12, "ft"),
    ("note", "Note", "E6 的具体说明、争议点", "text", 36, "source"),
]

FT_TIME_COLS = [
    ("date", "Date", "yyyy-mm-dd", "date", 12, "id"),
    ("reviewer", "Reviewer", "R1 = 舒俊，R2 = 卞红强（全文阶段）", ("list", "ft_reviewer"), 10, "id"),
    ("start", "Session start", "开始时间 hh:mm（本地时间）", "text", 12, "ft"),
    ("end", "Session end", "结束时间 hh:mm", "text", 12, "ft"),
    ("n_reports", "Reports handled", "这一段时间处理了多少篇（整数）", "int", 12, "ft"),
    ("note", "Note", "例如中断原因、遇到的疑问", "text", 40, "source"),
]

EX_TIME_COLS = [
    ("date", "Date", "yyyy-mm-dd", "date", 12, "id"),
    ("extractor", "Extractor", "E1 = 舒俊，E2 = 卞红强", ("list", "extractor"), 10, "id"),
    ("start", "Session start", "开始时间 hh:mm（本地时间）", "text", 12, "ft"),
    ("end", "Session end", "结束时间 hh:mm", "text", 12, "ft"),
    ("n_reports", "Reports worked on", "这一段时间处理了多少篇报告（整数）", "int", 12, "ft"),
    ("n_patients", "Patients entered", "这一段时间录入了多少名患者（整数）", "int", 12, "ft"),
    ("note", "Note", "例如中断原因、遇到的疑问", "text", 40, "source"),
]

IPD_COLS = [
    ("ws_id", "WS ID", "WS 编号", "text", 10, "id"),
    ("citation", "First author, year", "", "text", 20, "ipd"),
    ("n_children_aggregate", "Children aggregate-only", "整数", "int", 10, "ipd"),
    ("corresponding_author", "Corresponding author", "姓名（不要在仓库里写邮箱）", "text", 20, "ipd"),
    ("email_source", "Where the address was found", "论文 / 机构网页 / 其他", "text", 18, "ipd"),
    ("email1_date", "First e-mail sent", "yyyy-mm-dd", "date", 12, "ipd"),
    ("email2_date", "Second e-mail sent", "yyyy-mm-dd（第一封后 4 周）", "date", 12, "ipd"),
    ("reply_date", "Reply received", "yyyy-mm-dd", "date", 12, "ipd"),
    ("data_received", "Individual data received", "Yes / No / Partial", ("list", "ipd_received"), 11, "ipd"),
    ("data_location", "Where the data file is kept", "不要放进仓库；只写位置说明", "text", 24, "ipd"),
    ("final_status", "Final status", "Pending / Included with IPD / Narrative only / Not eligible after check", ("list", "ipd_final"), 24, "ipd"),
    ("notes", "Notes", "", "text", 30, "source"),
]


# ----------------------------------------------------------------------------- build helpers
def build_header(ws, cols, widths_row_heights=(22, 62, 100)):
    for ci, (code, label, hint, kind, width, sec) in enumerate(cols, start=1):
        c1 = ws.cell(row=1, column=ci, value=code)
        c2 = ws.cell(row=2, column=ci, value=label)
        c3 = ws.cell(row=3, column=ci, value=hint)
        for c in (c1, c2, c3):
            c.border = BORDER
            c.alignment = Alignment(wrap_text=True, vertical="top")
        for c in (c1, c2):
            c.fill = hdr_fill(sec)
            c.font = HDR_FONT
        c3.font = Font(italic=True, size=9, color="404040")
        c3.fill = PatternFill("solid", fgColor="F2F2F2")
        ws.column_dimensions[get_column_letter(ci)].width = width
    for r, h in zip((1, 2, 3), widths_row_heights):
        ws.row_dimensions[r].height = h


def column_letters(cols):
    return {code: get_column_letter(i) for i, (code, *_rest) in enumerate(cols, start=1)}


def add_validations(ws, cols, n_rows, formulas):
    """Apply data validation and grey fill for formula columns; write formulas."""
    letters = column_letters(cols)
    last = FIRST + n_rows - 1
    for ci, (code, label, hint, kind, width, sec) in enumerate(cols, start=1):
        L = get_column_letter(ci)
        rng = f"{L}{FIRST}:{L}{last}"
        if isinstance(kind, tuple) and kind[0] == "list":
            dv = DataValidation(type="list", formula1=list_ref(kind[1]), allow_blank=True,
                                showErrorMessage=True, errorStyle="warning",
                                errorTitle="Not in list", error="值不在列表里。请从下拉列表选择；确需例外请在 Notes 里说明。")
            ws.add_data_validation(dv)
            dv.add(rng)
        elif kind == "num_nr":
            dv = DataValidation(type="custom", formula1=f'OR(ISNUMBER({L}{FIRST}),{L}{FIRST}="NR")', allow_blank=True,
                                showErrorMessage=True, errorStyle="warning",
                                errorTitle="Number or NR", error="请填数字；报告里没有请填 NR。")
            ws.add_data_validation(dv)
            dv.add(rng)
        elif kind == "int_nr":
            dv = DataValidation(type="custom", formula1=f'OR(AND(ISNUMBER({L}{FIRST}),{L}{FIRST}=INT({L}{FIRST}),{L}{FIRST}>=0),{L}{FIRST}="NR")',
                                allow_blank=True, showErrorMessage=True, errorStyle="warning",
                                errorTitle="Integer or NR", error="请填整数；报告里没有请填 NR。")
            ws.add_data_validation(dv)
            dv.add(rng)
        elif kind == "int":
            dv = DataValidation(type="whole", operator="greaterThanOrEqual", formula1="0", allow_blank=True,
                                showErrorMessage=True, errorStyle="warning",
                                errorTitle="Integer", error="请填非负整数。")
            ws.add_data_validation(dv)
            dv.add(rng)
        elif kind == "date":
            for r in range(FIRST, last + 1):
                ws.cell(row=r, column=ci).number_format = "yyyy-mm-dd"
        elif isinstance(kind, tuple) and kind[0] == "formula":
            f = formulas[kind[1]]
            for r in range(FIRST, last + 1):
                c = ws.cell(row=r, column=ci, value=f(r, letters))
                c.fill = GREY
    # age must be < 18 (warning only)
    if "age_years" in letters:
        L = letters["age_years"]
        dv = DataValidation(type="custom",
                            formula1=f'OR(AND(ISNUMBER({L}{FIRST}),{L}{FIRST}>=0,{L}{FIRST}<18),{L}{FIRST}="NR")',
                            allow_blank=True, showErrorMessage=True, errorStyle="warning",
                            errorTitle="Age", error="年龄应为小于 18 的数字，或 NR。≥18 岁的患者不符合纳入标准。")
        ws.add_data_validation(dv)
        dv.add(f"{L}{FIRST}:{L}{last}")
        # replace the generic num_nr rule on this column: remove it so only the stricter one stays
        ws.data_validations.dataValidation = [
            d for d in ws.data_validations.dataValidation
            if not (str(d.sqref) == f"{L}{FIRST}:{L}{last}" and d.error.startswith("请填数字"))
        ]
    # freeze the code and label rows (1-2) and the first two columns; the hint row (3) scrolls with the data
    ws.freeze_panes = ws.cell(row=3, column=3)


# ----------------------------------------------------------------------------- derived-variable formulas
P_NONVIABLE = LISTS["viability"][2]
P_VIABLE = LISTS["viability"][0]
P_PARTIAL = LISTS["viability"][1]
PROC_TOTAL = LISTS["procedure"][3]
PROC_PARTIAL = LISTS["procedure"][2]


def f_own(r, L):
    rid = f'{L["report_id"]}{r}'
    return f'=IF({rid}="","",IF({rid}="OWN","Yes","No"))'


def f_cat(r, L):
    d = f'{L["idx_dur_days"]}{r}'
    c = f'{L["idx_dur_cat_imprecise"]}{r}'
    c1, c2, c3, c4 = LISTS["dur_category"]
    return (f'=IF(ISNUMBER({d}),IF({d}<=2,"{c1}",IF({d}<=7,"{c2}",IF({d}<=30,"{c3}","{c4}"))),'
            f'IF({c}<>"",{c},IF({d}="NR","NR","")))')


def f_plt(r, L):
    p = f'{L["platelets"]}{r}'
    return f'=IF(ISNUMBER({p}),IF({p}>450,"Yes","No"),IF({p}="NR","NR",""))'


def f_outcome(r, L):
    v = f'{L["viability"]}{r}'
    p = f'{L["procedure"]}{r}'
    removal = f'OR({p}="{PROC_TOTAL}",{p}="{PROC_PARTIAL}")'
    return (f'=IF({v}="","",IF({v}="{P_NONVIABLE}","Non-viable",IF({v}="{P_VIABLE}","Viable",'
            f'IF({v}="{P_PARTIAL}",IF({removal},"Non-viable","Review"),'
            f'IF({v}="NR",IF({removal},"NR - removed, check reason","NR"),"Not applicable")))))')


def f_period(r, L):
    y = f'{L["year"]}{r}'
    return f'=IF(ISNUMBER({y}),IF({y}<2000,"before 2000",IF({y}<=2014,"2000-2014","2015 onward")),"")'


FORMULAS = {"own": f_own, "cat": f_cat, "plt": f_plt, "outcome": f_outcome, "period": f_period}

# ----------------------------------------------------------------------------- README / Rules content
README_LINES = [
    ("title", f"数据提取工作簿（模板，草稿）{VERSION} — 儿童游走脾系统综述（PROSPERO CRD420261520329）"),
    ("p", "依据：协议 v1.5（`Systematic review protocol - PROSPERO draft.docx`）附录 C 的提取表和编码规则，以及第 8、12、13、14、16 节。本工作簿只是把协议落成可填写的表，不改变协议。凡超出附录 C 的地方都列在下面'与附录 C 的差异'里，是 Claude 的操作化建议，三位确认后才生效。"),
    ("h", "1. 怎么用"),
    ("b", "提取员：E1 = 舒俊，E2 = 卞红强，分歧由杨俊仲裁；Ji Wang 核查两份提取表但不提取（作者 2026 年 10 月 18 日决定，已写入协议 v1.5）。每位提取员各用自己的一份副本（文件名建议 extraction_E1.xlsx、extraction_E2.xlsx，共识文件 extraction_consensus.xlsx）。独立提取完成之前，不看对方的文件。"),
    ("b", "表头三行：第 1 行是字段代码（分析时用），第 2 行是协议附录 C 的项目名称，第 3 行是填写说明和允许值。数据从第 4 行开始，请不要在表头上方或表头里插行。"),
    ("b", "Reports 表一行一篇报告；Patients 表一行一名患者，用 report_id 对应。report_id 就是 records_deduplicated.ris 里的 WS 编号；本机构 5 例用 OWN（先在 Reports 表里加一行 OWN），患者编号 OWN_P1–OWN_P5。"),
    ("b", "**空白和 NR 的区别：** 空白 = 还没提取；NR = 报告里没有这项信息（协议：'Record NR when an item is not reported'）。不要用空白表示没报告。"),
    ("b", "灰色列是公式，不要改，也不要手填。下拉列表的值不在列表里时 Excel 会警告但允许保存；确需例外，请在 Notes 列写明。"),
    ("b", "关键项要记出处（页、表或图）：协议要求；至少主要暴露（时间）和主要结局（脾脏存活）的出处必填。"),
    ("b", "时间换算按 Rules 表的 9 条规则；Duration_calc 表只是计算器，处理不了含糊说法和规则 6–9 的判断，最终以人工判断为准。"),
    ("b", "本机构病例只录不可识别的信息：不要写姓名、住院号、出生日期、具体日期。已发表报告的患者也不要抄原文里的姓名缩写。"),
    ("b", "校准：正式提取前，两位提取员先各自提取同样的 10 篇报告，比较，讨论分歧，必要时改这份表和规则（协议第 14 节）。10 篇建议涵盖中英文、个案和系列、时间写法各异的报告，在全文名单确定后再选。"),
    ("b", "两人完成后比较、做共识：用 `tools/compare_extraction.py`（`check` 查一份文件的格式和进度，`compare` 比两份文件并出分歧清单）。协议只说'报告主要暴露和主要结局的 kappa'，没有规定连续变量怎么算——脚本对时间类别（四类加缺失）和脾脏存活各算一个 kappa，天数另报一致范围（这是 Claude 的读法，待确认）。"),
    ("h", "2. 各表"),
    ("b", "FT_log：全文筛选的正式记录（指南 D4，2026 年 10 月 17 日决定：全文阶段不用 Rayyan）。每位筛选员用自己的一份副本，两人都完成之前互不查看。详细规则见《全文筛选指南》。"),
    ("b", "FT_time_log：全文筛选的时间记录。每次开始和结束都写一行（日期、起止时间、处理的篇数），用来代替 Rayyan 的时间戳日志。"),
    ("b", "Reports、Patients：数据提取。"),
    ("b", "EX_time_log：数据提取的时间记录，和 FT_time_log 一样，每次开始和结束都写一行（日期、起止时间、处理的报告数和录入的患者数）。这是 Claude 的建议，待确认；没有它，电子表格里看不出每份记录是怎么做出来的。"),
    ("b", "IPD_requests：向只有汇总数据的报告的作者索取个体数据的登记（协议第 14 节：两封邮件，间隔 4 周）。"),
    ("b", "Rules：时间换算 9 条规则、衍生变量定义、主要暴露和结局的协议原文。"),
    ("b", "Duration_calc：时间换算计算器。Lists：下拉列表（请勿改动，改了会影响所有表）。"),
    ("h", "3. 与附录 C 的差异（Claude 的操作化，待三位确认）"),
    ("b", "A1  附录 C 的 A 部分（报告）单独放在 Reports 表，B–F 部分在 Patients 表；项目一个不少，只是不在每个患者行里重复。"),
    ("b", "A2  '伴随疾病'多选项拆成独立的 Yes/No/NR 列；影像学检查方式拆成 US、Doppler US、CT、MRI 四列。另外加了胰尾扭转、肠梗阻两列，因为协议第 13 节的附加结局列了它们。"),
    ("b", "A3  Procedure 在协议五项之外加了 No operation（协议第 7 节：未手术的儿童做描述性汇总）和 NR；Fixation technique 加了 Not applicable 和 NR；Approach、Viability、Basis of viability 加了 Not applicable（未手术）。"),
    ("b", "A4  加了衍生列（灰色）：own_patient（敏感性分析 1）、idx_dur_category（四类，边界见 Rules D2）、thrombocytosis（>450）、primary_outcome（Rules D3）、pub_period（第 16 节的发表时期）。这些是 Claude 对协议第 12、16 节的读法，须三位确认。"),
    ("b", "A5  ws_basis：记录报告凭什么说是游走脾（影像显示异位或活动、手术所见、只写了游走脾、只写了脾扭转而没写位置）。这是为了在全文指南 D1 的'宽松加标记'方案下，将来能做'只看有明确异位依据的'敏感分析；该敏感分析不在已注册的 8 个里，若要做须作为新增分析声明。"),
    ("b", "A6  加了 extractor、date_extracted、same_patient_as、idx_dur_rules、idx_dur_lower_bound、idx_dur_cat_imprecise（规则 5 和 9 要求标记）、src_* 出处列。"),
    ("b", "A7  Age 的取值：协议写'年，两位小数（月数 ÷ 12）'；未报告填 NR；原文写法另存 age_verbatim。只写'child'或'患儿'而没有具体年龄的，年龄填 NR（见全文指南 D2）。"),
    ("h", "4. 没有验证的事"),
    ("b", "灰色列的公式用 Python 的 formulas 库按公式文本计算过（九行虚构的测试数据，覆盖各分支，没有保存）；容器里没有 Excel，也没有 LibreOffice 的 Calc，所以文件没有在 Excel 或 WPS 里打开过，下拉列表和版面实际是否正常没有验证。第一次用时请随便填几行试一下，有问题告诉 Claude。"),
]

RULES_ROWS_DURATION = [
    (1, "Hours are converted to days (hours ÷ 24, one decimal).", "小时换算为天（小时 ÷ 24，保留一位小数）。"),
    (2, "Weeks × 7; months × 30.4; years × 365.", "周 × 7；月 × 30.4；年 × 365。"),
    (3, "Ranges take the midpoint (for example, 3–5 days is coded as 4 days).", "范围取中点（如 3–5 天记为 4 天）。"),
    (4, "“Less than 24 hours”, “a few hours” or “overnight” is coded as 0.5 days.", "'不足 24 小时''几小时''一夜'记为 0.5 天。"),
    (5, "Imprecise terms (“several days”, “some weeks”, “a long history”) are coded as missing on the continuous scale, and assigned a category only if every plausible reading falls in the same category.", "含糊说法（'数天''数周''病史很长'）在连续尺度上记为缺失（idx_dur_days 填 NR）；只有所有合理理解都落在同一类别时，才在 idx_dur_cat_imprecise 里指定类别。"),
    (6, "Intermittent or worsening presentations (for example, “intermittent pain for one week, worse for two days”): the primary coding uses the whole stated period of the current presentation (7 days); the alternative coding uses the period of worsening (2 days) and is used in sensitivity analysis 4.", "间歇或加重型表现（如'间歇腹痛一周，最近两天加重'）：主要编码用当前这次发作的整个叙述时段（7 天）；备选编码用加重时段（2 天），填在 idx_dur_alt_days，用于敏感性分析 4；同时 idx_dur_intermittent 填 Yes。"),
    (7, "A planned interval between discharge and a scheduled elective operation is excluded from the index episode and recorded as the waiting interval.", "出院后到择期手术之间的计划间隔不计入指数发作，另记为 waiting_interval_days。"),
    (8, "When dates of symptom onset and of operation are both given, the interval is calculated exactly.", "报告同时给出症状开始日期和手术日期时，按日期精确计算。"),
    (9, "When a report gives symptom duration at admission but not the timing of operation within the admission: an operation described as immediate or emergency adds nothing; an operation on hospital day N adds N days; otherwise the duration at admission is used and flagged as a lower bound.", "报告给了入院时的症状持续时间，但没给入院后手术的时间：描述为'立即/急诊'手术的不加天数；'住院第 N 天手术'加 N 天；其他情况用入院时的持续时间，并在 idx_dur_lower_bound 标为 Yes。"),
]

RULES_DEFINITIONS = [
    ("Primary exposure (protocol Section 8)", "Time from onset of the symptoms of the presentation that led to operation until the operation, in days. Time spent in hospital before operation during the same admission is included; a planned interval between discharge and a scheduled elective operation is not (it is recorded separately as a waiting interval).", "指数发作时长：导致手术的这次发作的症状开始到手术的天数；同一次住院期间手术前的住院时间计入；出院后到择期手术之间的计划间隔不计入，另记为等待间隔。"),
    ("Secondary exposures (Section 8)", "Total symptom history; missed diagnosis; known diagnosis with deferred surgery.", "总症状史；漏诊；已知诊断但推迟手术。"),
    ("Primary outcome (Section 12)", "Non-viable spleen at the index operation: total splenectomy, or partial splenectomy, performed because of infarction, necrosis or failure to reperfuse after detorsion, as judged at operation and/or on histology. A spleen that was viable at operation but removed for another reason counts as viable for this outcome and is reported under additional outcomes.", "主要结局：指数手术时脾脏已无活力（因梗死、坏死或松解后未恢复灌注而做全脾或部分脾切除，由术中和/或组织学判断）。手术时有活力但因其他原因被切除的脾脏，对本结局算有活力，在附加结局里另报。"),
]

DERIVED = [
    ("D1 own_patient", "report_id = OWN → Yes，否则 No。用于敏感性分析 1（排除本机构 5 例）。"),
    ("D2 idx_dur_category", "按 idx_dur_days：<=2 d；大于 2 且 <=7 → 3-7 d；大于 7 且 <=30 → 8-30 d；大于 30 → >30 d。协议的四类是按整数天写的（2 天及以下、3–7 天、8–30 天、30 天以上），非整数天（如 2.5、7.5）的归类是 Claude 的读法：边界值归较低一类（2.0 → <=2 d；7.0 → 3-7 d；30.0 → 8-30 d）。idx_dur_days 为 NR 时，用 idx_dur_cat_imprecise；两者都没有则显示 NR。"),
    ("D3 primary_outcome", "viability = Non-viable → Non-viable；Viable → Viable（即使被切除，也按协议算有活力）；Partially non-viable 且做了全脾或部分脾切除 → Non-viable（协议第 12 节：因梗死做部分脾切除算无活力；敏感性分析 3 把它改算保脾）；Partially non-viable 但没有切除 → Review（由共识判断）；NR 且做了切除 → 'NR - removed, check reason'（要回原文看是否因为无活力）；其他 NR；Not applicable（未手术）。这是 Claude 对第 12 节的读法，须三位确认。"),
    ("D4 thrombocytosis", "platelets > 450 ×10⁹/L → Yes（协议第 13 节）。"),
    ("D5 pub_period", "year < 2000 → before 2000；2000–2014 → 2000-2014；>= 2015 → 2015 onward（协议第 16 节主要分析的校正变量）。"),
]


def put_readme(ws):
    ws.column_dimensions["A"].width = 150
    r = 1
    for kind, text in README_LINES:
        c = ws.cell(row=r, column=1, value=("• " + text) if kind == "b" else text)
        c.alignment = Alignment(wrap_text=True, vertical="top")
        if kind == "title":
            c.font = Font(bold=True, size=14)
        elif kind == "h":
            c.font = Font(bold=True, size=12, color="FFFFFF")
            c.fill = PatternFill("solid", fgColor="2F75B5")
        # crude row-height estimate for wrapped lines (≈ 70 full-width characters per line at width 150)
        n = max(1, -(-len(text) // 70))
        ws.row_dimensions[r].height = 18 * n if kind != "title" else 24
        r += 1


def put_rules(ws):
    ws.column_dimensions["A"].width = 24
    ws.column_dimensions["B"].width = 70
    ws.column_dimensions["C"].width = 70
    r = 1
    ws.cell(row=r, column=1, value="Rules for converting reported durations (protocol Appendix C, verbatim) / 时间换算规则").font = Font(bold=True, size=12)
    r += 1
    for j, h in enumerate(["Rule", "Protocol text", "中文说明"], start=1):
        c = ws.cell(row=r, column=j, value=h)
        c.font = HDR_FONT
        c.fill = hdr_fill("patient")
        c.border = BORDER
    r += 1
    for n, en, cn in RULES_ROWS_DURATION:
        for j, v in enumerate([n, en, cn], start=1):
            c = ws.cell(row=r, column=j, value=v)
            c.alignment = WRAP
            c.border = BORDER
        ws.row_dimensions[r].height = 16 * max(2, -(-len(en) // 62), -(-len(cn) // 30))
        r += 1
    r += 1
    ws.cell(row=r, column=1, value="Definitions (protocol, abridged) / 协议里的定义").font = Font(bold=True, size=12)
    r += 1
    for name, en, cn in RULES_DEFINITIONS:
        for j, v in enumerate([name, en, cn], start=1):
            c = ws.cell(row=r, column=j, value=v)
            c.alignment = WRAP
            c.border = BORDER
        ws.row_dimensions[r].height = 16 * max(2, -(-len(en) // 62), -(-len(cn) // 30))
        r += 1
    r += 1
    ws.cell(row=r, column=1, value="Derived columns (grey) / 衍生列（Claude 的读法，待三位确认）").font = Font(bold=True, size=12)
    r += 1
    for name, txt in DERIVED:
        c1 = ws.cell(row=r, column=1, value=name)
        c2 = ws.cell(row=r, column=2, value=txt)
        ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=3)
        for c in (c1, c2):
            c.alignment = WRAP
            c.border = BORDER
        ws.row_dimensions[r].height = 16 * max(2, -(-len(txt) // 60))
        r += 1


def put_lists(wb):
    ws = wb.create_sheet("Lists")
    for ci, (name, vals) in enumerate(LISTS.items(), start=1):
        L = get_column_letter(ci)
        ws.cell(row=1, column=ci, value=name).font = Font(bold=True)
        for ri, v in enumerate(vals, start=2):
            ws.cell(row=ri, column=ci, value=v)
        LIST_COL[name] = L
        LIST_RANGE[name] = f"Lists!${L}$2:${L}${len(vals) + 1}"
        ws.column_dimensions[L].width = max(14, min(44, max(len(v) for v in vals) + 2))
    return ws


def put_duration_calc(ws):
    heads = ["Verbatim text", "Low value", "High value (if a range)", "Unit", "Phrase (rule 4)", "Days (calculated)", "Category (calculated)"]
    widths = [34, 11, 14, 11, 38, 14, 16]
    ws.cell(row=1, column=1, value="Duration calculator — 辅助工具，规则 1–4 的机械换算；含糊说法、规则 5–9 的判断请人工处理，把结果抄到 Patients 表。").font = Font(bold=True)
    for ci, (h, w) in enumerate(zip(heads, widths), start=1):
        c = ws.cell(row=2, column=ci, value=h)
        c.font = HDR_FONT
        c.fill = hdr_fill("patient")
        c.border = BORDER
        c.alignment = Alignment(wrap_text=True, vertical="top")
        ws.column_dimensions[get_column_letter(ci)].width = w
    n = 40
    dv_unit = DataValidation(type="list", formula1=list_ref("units"), allow_blank=True)
    dv_phr = DataValidation(type="list", formula1=list_ref("phrase"), allow_blank=True)
    ws.add_data_validation(dv_unit)
    ws.add_data_validation(dv_phr)
    dv_unit.add(f"D3:D{2 + n}")
    dv_phr.add(f"E3:E{2 + n}")
    c1, c2, c3, c4 = LISTS["dur_category"]
    for r in range(3, 3 + n):
        mid = f'IF(C{r}="",B{r},(B{r}+C{r})/2)'
        factor = f'IF(D{r}="hours",1/24,IF(D{r}="days",1,IF(D{r}="weeks",7,IF(D{r}="months",30.4,IF(D{r}="years",365,"")))))'
        ws.cell(row=r, column=6, value=(
            f'=IF(E{r}="{LISTS["phrase"][1]}",0.5,IF(OR(B{r}="",D{r}=""),"",ROUND({mid}*{factor},1)))')).fill = GREY
        ws.cell(row=r, column=7, value=(
            f'=IF(ISNUMBER(F{r}),IF(F{r}<=2,"{c1}",IF(F{r}<=7,"{c2}",IF(F{r}<=30,"{c3}","{c4}"))),"")')).fill = GREY
        for ci in range(1, 8):
            ws.cell(row=r, column=ci).border = BORDER
    ws.freeze_panes = "A3"


FT_ONLY_README = [
    ("title", "全文筛选校准用工作簿（20 篇）— 筛选员 {rev}（{name}）{ver}"),
    ("p", "这是《全文筛选指南》第 12 节的 20 篇校准。FT_log 里已经填好 WS 编号、第一作者和年份、语种和筛选员代号（灰色列，不要改）；其余列由你自己填。"),
    ("h", "1. 怎么用"),
    ("b", "你的代号是 {rev}，reviewer 列已填好。"),
    ("b", "Calibration_list 表里有 20 篇的标题、年份、DOI 和链接，用它们去找全文。找全文的途径和记录方法见指南第 4 节。"),
    ("b", "FT_log 每篇一行：按指南第 6 节的顺序回答问题，填 decision（Include / Exclude / Pending IPD）和 reason（用下拉列表，名称一字不差）；Include 要填 ws_basis 和儿童数。发表早于 2000 年的报告不在这 20 篇里。"),
    ("b", "FT_time_log 表：每次开始和结束都写一行（日期、开始和结束时间、这一段处理了几篇）。"),
    ("b", "两人都完成之前，不看对方的文件，不讨论具体的篇目。完成后另存为 FT_cal_{rev}.xlsx，交给杨俊保管；两人都完成后再比对。"),
    ("b", "不要改表头、列的顺序和下拉列表（Lists 表）。不要删除 FT_log 里已填好的行；多出来的行留空即可。"),
    ("h", "2. 说明"),
    ("b", "这 20 篇在正式的全文筛选里还会再处理一遍。校准只记一致率，kappa 在 20 篇上没有意义（指南 D5）。"),
    ("b", "指南没写清楚的情形，请记下 WS 编号和你的做法，在讨论时提出。"),
    ("b", "这个文件没有在 Excel 或 WPS 里打开测试过：下拉列表和灰色列的显示如有问题，请告诉舒俊。"),
]


def first_authors(ids):
    """First author's surname (or the whole name for Chinese authors) for each WS id, from the deduplicated RIS."""
    want, out = set(ids), {}
    for blk in open(RIS, encoding="utf-8-sig").read().split("\nER  -"):
        m = re.search(r"^ID  - (.*)$", blk, re.M)
        if m and m.group(1) in want:
            a = re.search(r"^AU  - (.*)$", blk, re.M)
            out[m.group(1)] = a.group(1).split(",")[0].strip() if a else ""
    return out


def main_ft_only():
    if not (ARGS.reviewer and ARGS.prefill):
        raise SystemExit("--ft-only needs --reviewer and --prefill")
    rows = list(csv.DictReader(open(ARGS.prefill, encoding="utf-8-sig")))
    authors = first_authors([r["ws_id"] for r in rows])
    n_rows = max(ARGS.rows, len(rows) + 10)
    wb = Workbook()
    ws_readme = wb.active
    ws_readme.title = "README"
    ws_ft = wb.create_sheet("FT_log")
    ws_time = wb.create_sheet("FT_time_log")
    ws_list = wb.create_sheet("Calibration_list")
    put_lists(wb)
    global README_LINES
    README_LINES = [(k, v.format(rev=ARGS.reviewer, name=REVIEWER_NAME[ARGS.reviewer], ver=VERSION)) for k, v in FT_ONLY_README]
    put_readme(ws_readme)
    for ws, cols in ((ws_ft, FT_COLS), (ws_time, FT_TIME_COLS)):
        build_header(ws, cols)
        add_validations(ws, cols, n_rows, FORMULAS)
    letters = column_letters(FT_COLS)
    for k, r in enumerate(rows):
        row = FIRST + k
        cit = ("%s %s" % (authors.get(r["ws_id"], ""), r["year"])).strip() if authors.get(r["ws_id"]) else "(no author) %s" % r["year"]
        for code, val in (("ws_id", r["ws_id"]), ("citation", cit), ("language", r["language"]), ("reviewer", ARGS.reviewer)):
            c = ws_ft["%s%d" % (letters[code], row)]
            c.value = val
            c.fill = GREY
    heads = ["position", "ws_id", "year", "language", "has_abstract", "title", "doi", "url"]
    widths = [9, 9, 7, 10, 12, 80, 28, 50]
    for ci, (h, w) in enumerate(zip(heads, widths), start=1):
        c = ws_list.cell(row=1, column=ci, value=h)
        c.font = HDR_FONT
        c.fill = hdr_fill("id")
        ws_list.column_dimensions[get_column_letter(ci)].width = w
    for ri, r in enumerate(rows, start=2):
        for ci, h in enumerate(heads, start=1):
            c = ws_list.cell(row=ri, column=ci, value=r[h])
            c.alignment = WRAP
    ws_list.freeze_panes = "A2"
    for ws, col in ((ws_readme, "7F7F7F"), (ws_ft, "2F75B5"), (ws_time, "2F75B5"), (ws_list, "548235")):
        ws.sheet_properties.tabColor = col
    wb["Lists"].sheet_properties.tabColor = "BBBBBB"
    wb.properties.title = "Full-text calibration workbook %s %s" % (ARGS.reviewer, VERSION)
    wb.properties.creator = "Wandering spleen SR team"
    wb.save(OUT)
    print("saved", OUT, "reviewer", ARGS.reviewer, "prefilled rows", len(rows), "FT_log rows formatted", n_rows)


def main():
    if ARGS.ft_only:
        return main_ft_only()
    wb = Workbook()
    ws_readme = wb.active
    ws_readme.title = "README"
    ws_ft = wb.create_sheet("FT_log")
    ws_time = wb.create_sheet("FT_time_log")
    ws_rep = wb.create_sheet("Reports")
    ws_pat = wb.create_sheet("Patients")
    ws_extime = wb.create_sheet("EX_time_log")
    ws_ipd = wb.create_sheet("IPD_requests")
    ws_rules = wb.create_sheet("Rules")
    ws_calc = wb.create_sheet("Duration_calc")
    put_lists(wb)  # also fills LIST_RANGE used below

    put_readme(ws_readme)
    put_rules(ws_rules)
    put_duration_calc(ws_calc)

    for ws, cols, n in ((ws_ft, FT_COLS, N_FT), (ws_time, FT_TIME_COLS, N_TIME), (ws_rep, REPORT_COLS, N_REP), (ws_pat, PATIENT_COLS, N_PAT), (ws_extime, EX_TIME_COLS, N_TIME), (ws_ipd, IPD_COLS, N_IPD)):
        build_header(ws, cols)
        add_validations(ws, cols, n, FORMULAS)

    # sheet tab colours
    for ws, col in ((ws_readme, "7F7F7F"), (ws_ft, "2F75B5"), (ws_time, "2F75B5"), (ws_rep, "2F75B5"), (ws_pat, "2F75B5"), (ws_extime, "2F75B5"),
                    (ws_ipd, "548235"), (ws_rules, "7F7F7F"), (ws_calc, "7F7F7F")):
        ws.sheet_properties.tabColor = col
    wb["Lists"].sheet_properties.tabColor = "BBBBBB"

    wb.properties.title = f"Extraction workbook template {VERSION}"
    wb.properties.creator = "Wandering spleen SR team"
    wb.save(OUT)
    print("saved", OUT, "patients cols", len(PATIENT_COLS), "report cols", len(REPORT_COLS), "ft cols", len(FT_COLS))


if __name__ == "__main__":
    main()
