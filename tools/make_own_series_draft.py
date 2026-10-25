#!/usr/bin/env python3
"""Build a DRAFT extraction file for the five children of the institutional series (report_id OWN).

Every value comes from the manuscript text and tables (Table 1 and Table 4 of the EJP-version article and the draft
manuscript v0.2), not from the hospital records. A cell is left BLANK when the manuscript does not give the value (blank =
not yet extracted); NR is used only where the manuscript says the value was not recorded. Nothing identifying is written:
no names, hospital numbers, dates of birth or exact dates.

The file is a reference for checking the manuscript against the records. It is not an independent extraction and is not
to be copied into the extractors' files before they have finished their own (see the README sheet of the output).

Usage:  python3 -I tools/make_own_series_draft.py "<output>.xlsx"
        python3 -I tools/make_own_series_draft.py "<output>.xlsx" --starter E1     (or E2)
The second form writes a BLANK starter file for one extractor: only report_id, patient_id (OWN_P1-OWN_P5) and the extractor
code are filled; nothing from the manuscript is copied in. The extractors fill it from the hospital records.
Needs openpyxl; builds the template with tools/build_extraction_workbook.py first and then fills it in.
"""
import argparse
import os
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
from openpyxl import load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

HERE = os.path.dirname(os.path.abspath(__file__))
_ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
_ap.add_argument("out", nargs="?", default="Extraction draft - own series OWN (from manuscript, not chart-checked).xlsx")
_ap.add_argument("--starter", choices=["E1", "E2"], help="write a blank starter file for this extractor instead of the manuscript-derived draft")
ARGS = _ap.parse_args()
OUT = ARGS.out
FIRST = 4
MS = "Manuscript Table 1 / Table 4 / Results"

# ----------------------------------------------------------------------------- the data
REPORT = {
    "report_id": "OWN",
    "first_author": "Own institutional series",
    "year": 2026,
    "journal": "Not published (this review)",
    "country": "China",
    "language": "English",
    "design": "Case series",
    "consecutive": "Unclear",
    "institution": "Wuhan Children's Hospital",
    "study_period": "1 May 2015 - 1 May 2026",
    "n_children_individual": 5,
    "n_children_aggregate": 0,
    "notes": ("DRAFT from the manuscript text, not from the records. year = 2026 is a placeholder (the year the paper is planned "
              "to be submitted) so that pub_period can be derived; the statistician decides what period applies to the own series. "
              "consecutive = Unclear until it is documented how the five children were identified (the manuscript says all children "
              "treated surgically in the period; the identification method is still PENDING)."),
}

COMMON_SRC = {"src_age_sex": "Manuscript Table 4", "src_exposure": "Manuscript Table 1, Table 4", "src_outcome": "Manuscript Results, Table 1, Table 4"}

PATIENTS = [
    {   # Case 1
        "patient_id": "OWN_P1", "report_id": "OWN",
        "age_years": 5.08, "age_verbatim": "5.08 years at the index operation", "sex": "M",
        "ws_basis": "Imaging shows ectopic position or mobility",
        "presentation": "Acute on chronic",
        "idx_dur_verbatim": "abdominal pain and fever, 1 day (second encounter)", "idx_dur_days": 1,
        "idx_dur_rules": "9", "idx_dur_intermittent": "No", "idx_dur_lower_bound": "Yes",
        "total_hist_verbatim": "first episode 2 days before the first presentation; index operation 16 months after the first presentation",
        "total_hist_days": 488.4, "n_earlier_episodes": 1,
        "missed_dx": "No", "known_dx_deferred": "Yes", "deferred_reason": "Family declined",
        "waiting_interval_days": 486.4, "torsion_awaiting": "Yes",
        "img_us": "Yes", "img_ct": "Yes",
        "platelets": 428,
        "approach": "Open", "viability": "Non-viable",
        "procedure": "Total splenectomy", "fixation": "Not applicable", "reason_viable_removed": "Not applicable",
        "status_last_fu": "Lost",
        "post_splenectomy_compl": "Postoperative thrombocytosis, normalised on oral dipyridamole; no overwhelming infection, thromboembolism or pulmonary hypertension (manuscript states this for the four splenectomised children together)",
        "notes": "DRAFT, see Chart_check. Index operation = second encounter (CT: pedicle torsion with splenic infarction).",
    },
    {   # Case 2
        "patient_id": "OWN_P2", "report_id": "OWN",
        "age_years": 7.08, "age_verbatim": "7.08 years at the index operation", "sex": "F",
        "presentation": "Acute on chronic",
        "idx_dur_verbatim": "abdominal pain, 1 day (second encounter)", "idx_dur_days": 1,
        "idx_dur_rules": "9", "idx_dur_intermittent": "No", "idx_dur_lower_bound": "Yes",
        "total_hist_verbatim": "first episode 2 days before the first presentation; index operation 19 months after the first presentation",
        "total_hist_days": 579.6, "n_earlier_episodes": 1,
        "missed_dx": "No", "known_dx_deferred": "Yes", "deferred_reason": "Family declined",
        "waiting_interval_days": 577.6, "torsion_awaiting": "Yes",
        "img_ct": "Yes",
        "platelets": 525,
        "approach": "Converted", "viability": "Non-viable",
        "procedure": "Total splenectomy", "fixation": "Not applicable", "reason_viable_removed": "Not applicable",
        "status_last_fu": "Lost",
        "post_splenectomy_compl": "Postoperative thrombocytosis, normalised on oral dipyridamole; no overwhelming infection, thromboembolism or pulmonary hypertension (manuscript states this for the four splenectomised children together)",
        "notes": "DRAFT, see Chart_check. Index operation = second encounter (CT: pedicle torsion with splenic infarction); laparoscopy converted to laparotomy.",
    },
    {   # Case 3
        "patient_id": "OWN_P3", "report_id": "OWN",
        "age_years": 9.67, "age_verbatim": "9.67 years at the index operation", "sex": "F",
        "ws_basis": "Imaging shows ectopic position or mobility",
        "presentation": "Chronic or intermittent",
        "idx_dur_verbatim": "intermittent abdominal pain, 9 days (third encounter)", "idx_dur_days": 9,
        "idx_dur_rules": "6", "idx_dur_intermittent": "Yes",
        "total_hist_verbatim": "first episode 1 day before the first presentation; index operation 62 months after the first presentation",
        "total_hist_days": 1885.8, "n_earlier_episodes": 2,
        "missed_dx": "No", "known_dx_deferred": "Yes", "deferred_reason": "Family declined",
        "waiting_interval_days": 1884.8,
        "img_us": "Yes", "img_ct": "Yes",
        "platelets": 172,
        "approach": "Laparoscopic", "viability": "Partially non-viable", "viab_basis": "Intraoperative",
        "procedure": "Partial splenectomy +/- splenopexy",
        "procedure_other": "subperitoneal pouch made first and abandoned because the spleen did not fit",
        "fixation": "Direct suture",
        "fixation_other": "upper pole to diaphragm, lower pole to lateral peritoneum, 5-0 silk, Hem-o-lok clips added",
        "spleen_size_cm": 17.3, "reason_viable_removed": "Not applicable",
        "recurrence": "Yes", "further_surgery": "Yes",
        "recurrence_details": ("recurrent migration of the spleen 1 month after the index operation (16.6 x 7.6 cm, anteromedial rotation of the body and "
                               "tail of the pancreas on CT); total splenectomy with omental autotransplantation (3-cm slices)"),
        "status_last_fu": "Lost",
        "post_splenectomy_compl": "Postoperative thrombocytosis, normalised on oral dipyridamole; no overwhelming infection, thromboembolism or pulmonary hypertension (manuscript states this for the four splenectomised children together)",
        "cond_other": "marked gastric distension with vomiting at the first two encounters (the manuscript does not call it gastric volvulus)",
        "notes": "DRAFT, see Chart_check. Index operation = third encounter (first splenic operation, 62 months after the first presentation).",
    },
    {   # Case 4
        "patient_id": "OWN_P4", "report_id": "OWN",
        "age_years": 2.75, "age_verbatim": "2 years 9 months", "sex": "M",
        "cond_gv": "Yes",
        "cond_other": "gastric perforation (2 cm, posterior wall of the antrum), repaired at the same operation",
        "ws_basis": "Imaging and operation",
        "presentation": "Acute",
        "idx_dur_verbatim": "abdominal distension, 2 hours", "idx_dur_days": 0.1,
        "idx_dur_rules": "1;9", "idx_dur_intermittent": "No", "idx_dur_lower_bound": "No",
        "total_hist_verbatim": "single episode, 2 hours", "total_hist_days": 0.1, "n_earlier_episodes": 0,
        "missed_dx": "No", "known_dx_deferred": "No", "deferred_reason": "Not applicable", "torsion_awaiting": "Not applicable",
        "img_ct": "Yes", "perfusion": "Normal",
        "platelets": 177,
        "approach": "Open", "viability": "Viable", "viab_basis": "Intraoperative",
        "procedure": "Splenopexy",
        "procedure_other": "repair of the gastric perforation",
        "fixation": "Other (specify)",
        "fixation_other": ("reinforced two-pole fixation: 2-0 non-absorbable silk through absorbable haemostatic gauze and the full thickness of the "
                           "parenchyma, upper pole to the diaphragmatic muscle, lower pole to the left lateral abdominal wall"),
        "spleen_size_cm": 8.4, "reason_viable_removed": "Not applicable",
        "followup_months": 13, "recurrence": "No",
        "recurrence_details": "normally positioned spleen on CT at 13 months, asymptomatic",
        "status_last_fu": "Preserved",
        "notes": "DRAFT, see Chart_check. Operated at the first presentation, because of the gastric perforation.",
    },
    {   # Case 5
        "patient_id": "OWN_P5", "report_id": "OWN",
        "age_years": 13.08, "age_verbatim": "13 years (13.08 in Table 4)", "sex": "M",
        "ws_basis": "Imaging shows ectopic position or mobility",
        "presentation": "Acute",
        "idx_dur_verbatim": "continuous periumbilical pain 18 hours before presentation; laparotomy 2.5 hours after presentation",
        "idx_dur_days": 0.9, "idx_dur_rules": "1;8", "idx_dur_intermittent": "No", "idx_dur_lower_bound": "No",
        "missed_dx": "Yes", "missed_dx_alt": "acute gastritis",
        "missed_dx_contact": "admission to another hospital one week before presentation",
        "known_dx_deferred": "No", "deferred_reason": "Not applicable", "torsion_awaiting": "Not applicable",
        "img_ct": "Yes", "whirl_sign": "Yes",
        "platelets": "NR",
        "approach": "Open", "torsion_at_op": "Yes", "torsion_degrees": 720,
        "viability": "Non-viable", "viab_basis": "Intraoperative",
        "procedure": "Total splenectomy", "procedure_other": "separate double ligation of the splenic artery",
        "fixation": "Not applicable", "spleen_size_cm": "NR", "reason_viable_removed": "Not applicable",
        "followup_months": 5, "status_last_fu": "Lost",
        "post_splenectomy_compl": "Thrombocytosis 918 x10^9/L on postoperative day 9, normalised on oral dipyridamole; no overwhelming infection, thromboembolism or pulmonary hypertension",
        "notes": ("DRAFT, see Chart_check. Platelet count reported as normal, exact value not recorded (manuscript). Spleen described as enlarged, no size. "
                  "Index operation 20.5 hours after the onset of the continuous pain (18 h + 2.5 h = 0.9 day)."),
    },
]
for p in PATIENTS:
    p.update(COMMON_SRC)

# patient, field, value in the draft, what to check in the records
CHART_CHECK = [
    ("all", "dates and times", "-", "Exact dates and times of onset, admission and operation for the index episode of every child (rule 8). Cases 1, 2 and 4: the manuscript has the duration at presentation only (Table 4 footnote a) and so adds no time to operation; Cases 1 and 2 are flagged as a lower bound (rule 9)."),
    ("all", "presentation", "see Patients", "The five values of presentation are a reading of the guide (5.3) applied to the manuscript wording; check against the history."),
    ("all", "imaging columns", "pooled over all encounters", "The guide does not say whether img_us / img_ct count all encounters or the index episode only; the draft pools all encounters. Doppler and MRI are left blank because the manuscript does not mention them."),
    ("all", "follow-up", "Cases 4 and 5 only", "Length of follow-up for Cases 1, 2 and 3 is not in the manuscript. Cases 4 (13 months) and 5 (5 months) are as of the September 2026 manuscript; update to the date of the last review."),
    ("all", "after splenectomy", "-", "Whether vaccination and antibiotic prophylaxis after splenectomy are documented (the manuscript does not say)."),
    ("all", "viab_basis", "see Patients", "Cases 4 and 5 (and 3) are marked Intraoperative from the operative description; check the operative note and whether histology exists. Cases 1 and 2: the manuscript gives CT infarction only, so viab_basis is blank."),
    ("all", "associated conditions", "blank", "Gastric volvulus / outlet obstruction, pancreatic tail, bowel obstruction, diaphragm, kidney, syndrome, previous surgery and aetiology are blank where the manuscript is silent. A blank here means not yet extracted; the record may allow Yes / No."),
    ("OWN_P1", "waiting_interval_days, total_hist_days", "486.4; 488.4", "Computed from the stated 16 months (x30.4) plus 2 days; the guide measures the waiting interval from the day the diagnosis was made and surgery deferred to the start of the index episode. Replace with the exact interval from the dates."),
    ("OWN_P2", "ws_basis", "blank", "Table 1 says only 'CT: pedicle torsion' for this child. Check the CT report and the operative note for the position or mobility of the spleen."),
    ("OWN_P2", "waiting_interval_days, total_hist_days", "577.6; 579.6", "As for OWN_P1 (19 months)."),
    ("OWN_P2", "approach", "Converted", "Reason for conversion from laparoscopy to laparotomy (not in the manuscript)."),
    ("OWN_P3", "idx_dur_days", "9 (intermittent)", "Duration of any worsening within the nine days, for the alternative coding of rule 6 (idx_dur_alt_days). Whether the time from presentation to operation is known (rule 9)."),
    ("OWN_P3", "viability, viab_basis", "Partially non-viable, Intraoperative", "Extent of the infarction at operation and whether histology exists; whether the spleen removed at the second operation (total splenectomy after recurrence) was viable. Primary outcome under the protocol definition = Non-viable (partial splenectomy for infarction); sensitivity analysis 3 counts it as salvage."),
    ("OWN_P3", "torsion_at_op, cond_panc_tail", "blank", "Whether the pedicle was twisted at the index operation; the pancreatic rotation was seen on CT at the fourth encounter, after the index operation, so cond_panc_tail was left blank."),
    ("OWN_P3", "fixation", "Direct suture", "Capsular sutures to the diaphragm and lateral peritoneum with clips after an abandoned pouch; the choice between Direct suture and Other is a reading."),
    ("OWN_P3", "waiting_interval_days, total_hist_days", "1884.8; 1885.8", "As for OWN_P1 (62 months; first episode 1 day before the first presentation)."),
    ("OWN_P4", "torsion_at_op", "blank", "CT showed pedicle torsion; the operative description says the spleen was held only by its pedicle but does not give torsion at operation."),
    ("OWN_P4", "recurrence / further surgery", "No / blank", "Recurrence = No from the CT at 13 months; further surgery is not stated."),
    ("OWN_P5", "idx_dur_days", "0.9", "The child was admitted to another hospital one week before presentation and treated as acute gastritis. If the abdominal symptoms were continuous over that week, the index episode is about 7 days (and total history longer); if not, 0.9 stands. Decide from the history in the records."),
    ("OWN_P5", "n_earlier_episodes, total_hist_days", "blank", "Left blank because of the point above."),
    ("OWN_P5", "platelets", "NR", "Reported as normal; the exact value was not recorded (manuscript). Check whether the laboratory system has it."),
    ("OWN_P5", "spleen_size_cm", "NR", "The spleen is described as enlarged; no measurement in the manuscript."),
]

README = [
    ("title", "草稿：本院 5 例（OWN）的提取表，由稿件预填，没有对照病历"),
    ("warn", "这不是一份独立提取。每个值都来自稿件正文和 Table 1、Table 4（EJP 版文章和 Manuscript draft v0.2），不是来自住院病历。稿件里没写的项目是空白（空白 = 还没提取），只有稿件明确说'没有记录'的项才填 NR（如病例 5 的血小板数值、脾脏大小）。"),
    ("h", "怎么用（建议）"),
    ("b", "提取员（E1 舒俊、E2 卞红强）各自从病历提取这 5 名儿童，填进自己的提取表（OWN_P1–OWN_P5），在两人都完成之前不看这份草稿，也不看对方的文件。这样本院 5 例和已发表的报告一样是独立双人提取。"),
    ("b", "两人完成并做完共识以后，把共识的 OWN 行和这份草稿对照：不一致之处说明稿件和病历不一样，要查原因，必要时改稿件（例如第 3 例从首次就诊到第一次脾手术的间隔是 62 个月，而第二次到第三次就诊之间的 36 个月曾被误当作这个间隔，后来才改正）。"),
    ("b", "2026 年 10 月 18 日作者决定：按上面的建议，两位提取员先从病历独立提取，空白起始文件在 `search/extraction/own_series/`（`extraction_E1_OWN_starter.xlsx`、`extraction_E2_OWN_starter.xlsx`）。卞红强是否已知道这一决定没有确认。若改为从草稿出发逐格核对，这 5 例就不再是独立双人提取，要在 Methods 里说明，且应事先由三位定下。"),
    ("b", "核对清单见 Chart_check 表（每个病例要在病历里查什么）。"),
    ("h", "草稿里的编码规则"),
    ("b", "主要暴露、主要结局的编码与稿件 Table 4 一致：指数发作 1 天、1 天、9 天（间歇性，规则 6）、0.1 天、0.9 天；脾脏在指数手术时无活力：病例 1、2、5，以及（协议主要定义下，因梗死做部分脾切除）病例 3；病例 4 有活力。"),
    ("b", "病例 1、2 的'指数发作'是第二次就诊；病例 3 是第三次就诊（首次脾手术）。之后的手术（病例 3 复发后的全脾切除）写在 further_surgery 和 recurrence_details，不改 viability 和 procedure（提取说明 5.6）。"),
    ("b", "等待间隔和总病程是用稿件给的月数（月 × 30.4）加症状天数算的近似值，要用病历里的日期替换。"),
    ("b", "year = 2026 只是占位，使 pub_period 能算出来；本院病例适用什么发表时期由统计分析负责人定。"),
    ("b", "extractor 和 date_extracted 故意留空，因为这不是提取。灰色列是公式，不要改。"),
    ("h", "没有验证的事"),
    ("b", "这份文件没有在 Excel 或 WPS 里打开过（容器里没有）；下拉列表和版面实际是否正常没有验证。"),
    ("b", "文件里没有姓名、住院号、出生日期或具体日期。若在病历核对时发现这些，不要写进这份文件或仓库。"),
]


STARTER_NAME = {"E1": "舒俊", "E2": "卞红强"}
STARTER_README = [
    ("title", "本院 5 例（OWN）的提取表：空白起始文件，从病历提取"),
    ("warn", "这份文件里只有编号和提取员代码，没有任何数据。请只根据住院病历填写，不要参照稿件、不要打开那份由稿件预填的草稿，也不要打开对方的文件。"),
    ("h", "要做什么"),
    ("b", "提取员：E1 = 舒俊，E2 = 卞红强（Reports 和 Patients 表的 extractor 列已填好）。一人一份，另存为自己的副本（建议 `extraction_E1_OWN.xlsx` 或 `extraction_E2_OWN.xlsx`），每次用完另存带日期的副本，不覆盖旧的。"),
    ("b", "Patients 表里的 OWN_P1–OWN_P5 对应稿件 Table 1 的 Case 1–5。病历和编号的对应表由舒俊保管，放在仓库之外，不要写进这份文件。"),
    ("b", "逐项怎么填、9 条时间换算规则、疑难情形，见《提取操作说明》（`Extraction guide - how to fill the extraction workbook (draft)`）。其中几条对本院病例特别要紧：指数手术 = 结束这次指数发作的第一次为游走脾做的手术（第 5.6 节）；之后的手术写进 further_surgery 和 recurrence_details，不改 viability 和 procedure；空白 = 还没提取，NR = 病历里没有这项信息（第 2.3 节）。"),
    ("b", "每名儿童可能有多次就诊。主要暴露只看导致指数手术的那一次发作；更早的发作写进 n_earlier_episodes、总病程和等待间隔（第 5.3、5.4 节）。"),
    ("b", "Reports 表的 OWN 行请自己填完整（first_author 可写 Own institutional series，year、institution、study_period、n_children_individual 等照提取说明第 4 节）。year 对本院病例只用来推算发表时期：协议 v1.8 已定本院 5 例属于“2015 年及以后”，分析脚本不读 OWN 行的 year，填 2026 即可，不必再商量。"),
    ("b", "本院 5 例不做偏倚风险评价，所以不需要和偏倚风险表合并阅读；正式提取的 269 篇才合并（《提取操作说明》第 1 节第 3 步）。"),
    ("b", "只录不可识别的信息：不写姓名、住院号、出生日期、具体日期。用日期算出的间隔，只写间隔本身（如'症状开始 18 小时后入院，入院 2.5 小时后手术'），把天数换算写进 idx_dur_verbatim 或 notes，不写日历日期。"),
    ("b", "病历里没有或看不清的项目，不要凭印象或稿件补：写 NR，并在 notes 里说明。拿不准的写在 notes，留待共识讨论。"),
    ("h", "做完以后"),
    ("b", "运行 `python3 -I tools/compare_extraction.py check 你的文件.xlsx`，把格式错误改掉。"),
    ("b", "把自己的文件交杨俊保管（提取说明第 2.1 节）；两人都交了以后才运行 `compare`，再讨论分歧、建共识文件。"),
    ("b", "共识之后，才把共识的 OWN 行和由稿件预填的草稿对照（`python3 -I tools/compare_extraction.py compare 共识文件.xlsx 草稿.xlsx --out 文件夹`；输出里的 E1 指共识文件，E2 指草稿，草稿的 extractor 列是空的，会有警告），用来发现稿件和病历不一致的地方。"),
    ("h", "没有验证的事"),
    ("b", "这份文件没有在 Excel 或 WPS 里打开过；下拉列表和版面实际是否正常没有验证。"),
]


def put_readme(ws, lines):
    ws.delete_rows(1, ws.max_row + 5)
    ws.column_dimensions["A"].width = 150
    r = 1
    for kind, text in lines:
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
        r += 1


def main_starter():
    tmp = tempfile.mkdtemp(prefix="ownsrc_")
    tpl = os.path.join(tmp, "template.xlsx")
    subprocess.run([sys.executable, "-I", os.path.join(HERE, "build_extraction_workbook.py"), tpl], check=True, stdout=subprocess.DEVNULL)
    wb = load_workbook(tpl)
    for name in ("FT_log", "IPD_requests"):
        del wb[name]

    def fill(ws, rows):
        codes = {ws.cell(row=1, column=c).value: c for c in range(1, ws.max_column + 1) if ws.cell(row=1, column=c).value}
        for i, rec in enumerate(rows):
            for k, v in rec.items():
                ws.cell(row=FIRST + i, column=codes[k], value=v)

    fill(wb["Reports"], [{"report_id": "OWN", "extractor": ARGS.starter}])
    fill(wb["Patients"], [{"patient_id": p["patient_id"], "report_id": "OWN", "extractor": ARGS.starter} for p in PATIENTS])
    put_readme(wb["README"], STARTER_README)
    wb["Reports"].sheet_properties.tabColor = "C00000"
    wb["Patients"].sheet_properties.tabColor = "C00000"
    wb.active = 0
    wb.properties.title = "Extraction OWN starter %s (blank)" % ARGS.starter
    wb.properties.creator = "Wandering spleen SR team"
    wb.save(OUT)
    print("saved", OUT, "| starter for", ARGS.starter, "(" + STARTER_NAME[ARGS.starter] + ") | patient rows", len(PATIENTS))


def main():
    if ARGS.starter:
        return main_starter()
    tmp = tempfile.mkdtemp(prefix="ownsrc_")
    tpl = os.path.join(tmp, "template.xlsx")
    subprocess.run([sys.executable, "-I", os.path.join(HERE, "build_extraction_workbook.py"), tpl], check=True, stdout=subprocess.DEVNULL)
    wb = load_workbook(tpl)
    for name in ("FT_log", "IPD_requests"):
        del wb[name]

    def fill(ws, rows):
        codes = {ws.cell(row=1, column=c).value: c for c in range(1, ws.max_column + 1) if ws.cell(row=1, column=c).value}
        for i, rec in enumerate(rows):
            for k, v in rec.items():
                if k not in codes:
                    raise SystemExit("unknown column %r on sheet %s" % (k, ws.title))
                ws.cell(row=FIRST + i, column=codes[k], value=v)

    fill(wb["Reports"], [REPORT])
    fill(wb["Patients"], PATIENTS)

    # README replaced
    ws = wb["README"]
    ws.delete_rows(1, ws.max_row + 5)
    ws.column_dimensions["A"].width = 150
    r = 1
    for kind, text in README:
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
        r += 1

    # Chart_check sheet
    cc = wb.create_sheet("Chart_check", 1)
    heads = ["patient_id", "field(s)", "value in the draft", "what to check in the records"]
    widths = [12, 30, 26, 110]
    for ci, (h, w) in enumerate(zip(heads, widths), start=1):
        c = cc.cell(row=1, column=ci, value=h)
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor="C55A11")
        cc.column_dimensions[get_column_letter(ci)].width = w
    for ri, row in enumerate(CHART_CHECK, start=2):
        for ci, v in enumerate(row, start=1):
            c = cc.cell(row=ri, column=ci, value=v)
            c.alignment = Alignment(wrap_text=True, vertical="top")
        cc.row_dimensions[ri].height = max(18, 15 * (-(-len(row[3]) // 100)))
    cc.freeze_panes = "A2"
    cc.sheet_properties.tabColor = "C55A11"
    wb["Reports"].sheet_properties.tabColor = "C00000"
    wb["Patients"].sheet_properties.tabColor = "C00000"
    wb.active = 0
    wb.properties.title = "Extraction DRAFT own series (from manuscript, not chart-checked)"
    wb.properties.creator = "Wandering spleen SR team"
    wb.save(OUT)
    print("saved", OUT, "| patients", len(PATIENTS), "| chart-check rows", len(CHART_CHECK))


if __name__ == "__main__":
    main()
