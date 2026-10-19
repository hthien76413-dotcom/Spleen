#!/usr/bin/env python3
"""Planning list of REPORTS THAT MAY NEED AN IPD REQUEST, made BEFORE the full-text stage.

This is not a target list in the protocol's sense. A report becomes an IPD target only when both full-text screeners record
'Pending IPD' (aggregate data only, reason A) in their FT_log files. This script only helps to plan the size of the batch and the
order in which the e-mails are prepared. It uses two things:
  1. what Claude saw when the 53 hand-collected pilot papers were read in full (28 Sep 2026), from
     literature-pilot-extraction-53-papers.csv (status 'excluded/aggregate/duplicate' with 'agg(n)' in the case column);
  2. the number of patients stated in the TITLE or ABSTRACT of the 540 reports to be retrieved (digits or number words, 3 or more).
     That number can describe a bigger population than the paediatric wandering-spleen cases, and a report with a table of
     individual patients is not a target. The abstract number says nothing about whether individual data are given.

Screeners must not use this list while they screen (it hints at what a report looks like); it is for the sender of the e-mails.

Usage: python3 -I tools/make_ipd_target_candidates.py OUT_DIR       (run from the repository root; needs openpyxl)
Writes OUT_DIR/ipd_target_candidates.csv and .xlsx.
"""
import csv
import re
import sys
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

RET = "search/screening/rescreen/fulltext_retrieval_list.csv"
RIS = "search/dedup/records_deduplicated.ris"
WORK = "search/screening/fulltext/retrieval_worklist_540.csv"
PILOT = "literature-pilot-extraction-53-papers.csv"
CHECK = "tools/pilot_reference_check.py"

# Outcomes reported by the author after the 20-report full-text calibration (19 Oct 2026). Both screeners agreed after discussion
# that these reports contain per-patient data (Include, not Pending IPD), so they are NOT targets. Reported, not checked by Claude.
SCREENER_OUTCOME = {
    "WS1859": "19 Oct 2026 calibration: Include - per-patient Table 1 with 19 rows (screeners' report); not an IPD target",
    "WS0049": "19 Oct 2026 calibration: Include - 6-row per-patient table in online appendix 1 (screeners' report); not an IPD target",
}

WORDS = {"two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11,
         "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18,
         "nineteen": 19, "twenty": 20}
CN = {"二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9, "十": 10}
NOUN = r"(?:consecutive\s+|paediatric\s+|pediatric\s+|female\s+|male\s+|adult\s+|young\s+)?(?:children|child|patients|cases|infants|girls|boys|neonates|adolescents|individuals|dogs)"
EN_NUM = re.compile(r"\b(\d{1,3}|%s)\s+%s\b" % ("|".join(WORDS), NOUN), re.I)
EN_SERIES = re.compile(r"\b(?:series|cohort)\s+of\s+(\d{1,3}|%s)\b" % "|".join(WORDS), re.I)
CN_NUM = re.compile(r"(\d{1,3}|[二三四五六七八九十]{1,2})\s*(?:例|名)(?:患儿|患者|儿童|病例)?")
SERIES_WORDS = re.compile(r"\b(series|cohort|retrospective|multicent|experience with|our experience)\b|回顾|病例分析|病例系列", re.I)
SINGLE = re.compile(r"\b(a|an|one|single)\s+(?:rare\s+)?(?:case|child|patient|girl|boy|infant)\b(?!\s+series)|\bcase report\b|\b1 case\b|一例|1\s*例|\bwe (?:report|describe|present)\s+(?:a|an|the case of)\b", re.I)


def read_ris(path):
    recs, cur = {}, None
    for line in open(path, encoding="utf-8-sig"):
        m = re.match(r"^([A-Z][A-Z0-9])  - ?(.*)$", line.rstrip("\n"))
        if not m:
            continue
        tag, val = m.groups()
        if tag == "TY":
            cur = {}
        cur.setdefault(tag, []).append(val)
        if tag == "ID":
            recs[val] = cur
    return recs


def num(tok):
    tok = tok.lower()
    if tok.isdigit():
        return int(tok)
    if tok in WORDS:
        return WORDS[tok]
    if tok in CN:
        return CN[tok]
    if len(tok) == 2 and tok[0] == "十" and tok[1] in CN:
        return 10 + CN[tok[1]]
    if len(tok) == 2 and tok[1] == "十" and tok[0] in CN:
        return CN[tok[0]] * 10
    return None


LIT = re.compile(r"additional|in the literature|reported (?:so far|worldwide|to date)|worldwide|world-wide|so far|to date|to (?:the best of )?our knowledge|previously (?:reported|described)|described previously|PubMed|MEDLINE|searched|fewer than|less than|全球|世界|文献报道|报道了|报告了|检索|至今|已有", re.I)
WS_CUE = re.compile(r"wander|ectopic|floating|movable|mobile spleen|pelvic spleen|splenic torsion|torsion of (?:the )?spleen|splenopex|spleen fixation|游走|异位脾|游动|漂浮脾|脾扭转|脾蒂扭转|脾固定|脾下垂", re.I)
REVIEW_CUE = re.compile(r"systematic review|meta-analysis|narrative review|pictorial review|综述|系统评价|进展", re.I)


def counts(text):
    """Patient counts of 3 or more found in the text: (n, phrase, taken_from_literature_context)."""
    found = []
    for rx in (EN_NUM, EN_SERIES, CN_NUM):
        for m in rx.finditer(text):
            n = num(m.group(1))
            if n and n >= 3:
                s, e = max(0, m.start() - 70), min(len(text), m.end() + 70)
                ctx = text[s:e].replace("\n", " ")
                found.append((n, ctx, bool(LIT.search(ctx))))
    return found


MANUAL_A = {
    "31": "pilot: Lombardi 2014 is a case series of 3 plus an imaging review of 55 children (2002-12) at the same hospital; the 55 are described in aggregate (pilot file, design column); one of its 3 cases duplicates Di Crosta 2009",
    "35": "pilot: Cohen 2018 lists five children in the pilot file (three usable, two duplicates of another paper); the paper's total and what it gives per child were not recorded in the pilot file - check the full text",
}


def pilot_map():
    src = open(CHECK, encoding="utf-8").read()
    m = re.search(r"^M = (\{.*\})\s*$", src, re.M)
    return eval(m.group(1), {"__builtins__": {}})  # a literal dict of paper_no -> WS id, written by us


def main(out_dir):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    recs = read_ris(RIS)
    work = {r["WS id"]: r for r in csv.DictReader(open(WORK, encoding="utf-8-sig"))}
    retr = {r["ws_id"]: r for r in csv.DictReader(open(RET, encoding="utf-8-sig"))}
    pm = pilot_map()
    ws2paper = {v: k for k, v in pm.items()}
    pil = list(csv.DictReader(open(PILOT, encoding="utf-8-sig")))
    agg_rows = {}
    for r in pil:
        if r["status"] != "IPD-included" and "agg(" in r["case"]:
            agg_rows.setdefault(r["paper_no"], []).append(r)

    rows = []
    for ws, w in work.items():
        rec = recs[ws]
        title = rec.get("TI", [""])[0]
        abst = " ".join(rec.get("AB", []))
        text = title + " " + abst
        cs = counts(text)
        own = [(n, c) for n, c, lit in cs if not lit]
        nmax = max((n for n, _ in own), default=0)
        snippet = next((c for n, c in own if n == nmax), "")
        lit_nums = sorted({n for n, _, lit in cs if lit}, reverse=True)
        paper = ws2paper.get(ws)
        ws_cue = bool(WS_CUE.search(title)) or len(WS_CUE.findall(text)) >= 2
        review_text = bool(REVIEW_CUE.search(text)) and not SINGLE.search(title)
        tier, basis = "", ""
        if paper in agg_rows or paper in MANUAL_A:
            tier = "A"
            if paper in agg_rows:
                r0 = agg_rows[paper][0]
                basis = "pilot: read in full on 28 Sep 2026, no individual data for these patients (%s; %s)" % (r0["case"], r0["notes"][:110])
            else:
                basis = MANUAL_A[paper]
        elif not ws_cue:
            continue
        elif review_text:
            tier = "R"
            basis = "review/synthesis cue in title or abstract; numbers in it usually describe other authors' patients (not a target unless it reports own patients)"
        elif nmax >= 3 and not (SINGLE.search(title) and nmax < 5):
            tier = "B"
            basis = "title/abstract states %d patients (phrase: ...%s...)" % (nmax, snippet)
        elif SERIES_WORDS.search(text) and not SINGLE.search(title):
            tier = "C"
            basis = "title/abstract uses a series/cohort/retrospective word, no own number of 3 or more found"
        if not tier:
            continue
        review_cue = tier == "R"
        rows.append({
            "tier": tier, "ws_id": ws, "worklist_no": w["No."], "citation": "%s %s" % (w["First author"], w["Year"]),
            "year": w["Year"], "language": w["Language"], "has_abstract": w["Abstract in database record"],
            "n_stated_in_text": nmax or "", "numbers_taken_from_literature_context": ",".join(map(str, lit_nums)),
            "review_cue_in_title": "yes" if review_cue else "", "wandering_spleen_word_in_title": "yes" if WS_CUE.search(title) else "no",
            "basis": basis, "title": title, "journal": w["Journal"],
            "link": w["PubMed link"] or w["DOI link"] or w["CNKI link"] or w["Wanfang link"] or w["Scopus link"],
            "calibration_report": w["Calibration report"],
        })
    # pilot aggregate papers that are NOT in the 540 (and why)
    not_in = []
    for paper, rs in agg_rows.items():
        ws = pm[paper]
        cls = retr.get(ws, {}).get("retrieval_class", "not on the full-text list")
        if ws not in work:
            not_in.append((paper, rs[0]["study"], ws, cls, rs[0]["case"]))
    order = {"A": 0, "B": 1, "C": 2, "R": 3}
    rows.sort(key=lambda r: (order[r["tier"]], -(r["n_stated_in_text"] or 0), r["ws_id"]))

    cols = list(rows[0].keys()) + ["corresponding_author (name only)", "where_address_found (not the address)", "decided_by_screeners"]
    with open(out / "ipd_target_candidates.csv", "w", newline="", encoding="utf-8-sig") as f:
        w_ = csv.writer(f)
        w_.writerow(cols)
        for r in rows:
            w_.writerow(list(r.values()) + ["", "", SCREENER_OUTCOME.get(r["ws_id"], "")])

    wb = Workbook()
    rd = wb.active
    rd.title = "README"
    tc = {t: sum(1 for r in rows if r["tier"] == t) for t in "ABCR"}
    lines = [
        "IPD 索取邮件：目标候选清单（全文阶段之前的规划用表，草稿，2026-10-19）",
        "",
        "这不是协议意义上的目标清单。一篇报告成为 IPD 索取对象，要等两位全文筛选员都在各自的 FT_log 里记 Pending IPD（只有汇总数据，理由 A），再经比对和分歧解决（tools/finalize_fulltext.py 输出 fulltext_pending_ipd.csv）。这张表只用来估计这一批邮件有多少封、先准备哪几封。",
        "两位筛选员在做全文筛选的过程中不要看这张表（它会提示哪些报告‘像系列报告’）。它给发邮件的人用。",
        "",
        "来源和分层：",
        "A（%d 篇）：28 日预试验的 53 篇里，Claude 通读全文后认为没有逐例数据的报告，且在 540 篇名单里。这是 Claude 单人阅读的判断，不是两位筛选员的决定。" % tc["A"],
        "B（%d 篇）：标题或摘要里写了 3 例（人）以上。这个数字可能是更大的人群（例如所有脾脏手术），也可能这篇有逐例表格；摘要不能说明有没有个体数据。" % tc["B"],
        "C（%d 篇）：标题或摘要里有 series / cohort / retrospective / 回顾 等字样，但没有找到 3 例以上的数字。" % tc["C"],
        "R（%d 篇）：标题或摘要有综述 / 系统评价 / 文献复习的字样；里面的数字多半是别人的病例，除非本文另有自己的病例，否则不是索取对象，列出来只是避免漏看。" % tc["R"],
        "所有 B、C、R 都要求标题里有游走脾 / 异位脾 / 脾扭转 / 脾固定等词，或标题加摘要里至少出现两次；n_stated_in_text 不含出现在‘文献报道、全球、迄今’等语境里的数字（列在 numbers_taken_from_literature_context）。",
        "数字由关键词和正则从标题、摘要里读出，没有一篇逐篇人工核对；中文表达（‘十余例’等）可能漏掉。没有摘要的 178 篇只有标题可用，大概率漏掉。",
        "",
        "不在这张表里的已知聚合性报告（预试验读过全文）：",
    ]
    for paper, study, ws, cls, case in not_in:
        lines.append("  - %s（%s，预试验第 %s 篇，%s）：全文清单分类 = %s" % (study, ws, paper, case, cls))
    lines += [
        "",
        "decided_by_screeners 列：已经有两位筛选员全文判断的报告写在这里。2026 年 10 月 19 日 20 篇校准后（作者转告，Claude 没有打开论文核对）：WS1859 有 19 行逐例表，WS0049 的逐例资料在线上附录 1（6 行），两篇都判 Include，不是 IPD 索取对象。它们仍留在表里，只为保留规划时的记录。",
        "邮箱地址不要写进这张表或仓库：只写通讯作者姓名和‘在哪里找到地址’（论文 / 机构网页 / 其他）。",
        "发邮件前仍要先核对全文：确实只有汇总数据、确实是游走脾、确实有儿童（IPD 邮件草稿第 1 节的清单）。",
        "一次性批量发出；第一封后 4 周发第二封；再等 4 周；从第一封起最多 8 周（D6）。IPD_requests 表（提取工作簿）记录进度。",
    ]
    for i, t in enumerate(lines, 1):
        c = rd.cell(row=i, column=1, value=t)
        c.alignment = Alignment(wrap_text=True, vertical="top")
        if i == 1:
            c.font = Font(bold=True, size=13)
    rd.column_dimensions["A"].width = 150
    ws_ = wb.create_sheet("Candidates")
    fills = {"A": "E2EFDA", "B": "FFF2CC", "C": "EDEDED", "R": "F2DCDB"}
    for ci, h in enumerate(cols, 1):
        c = ws_.cell(row=1, column=ci, value=h)
        c.font = Font(bold=True)
        c.fill = PatternFill("solid", fgColor="D9E1F2")
        c.alignment = Alignment(wrap_text=True, vertical="center")
    widths = {"tier": 6, "ws_id": 9, "worklist_no": 8, "citation": 18, "year": 6, "language": 9, "has_abstract": 9, "n_stated_in_text": 9,
              "review_cue_in_title": 9, "wandering_spleen_word_in_title": 10, "basis": 60, "title": 55, "journal": 24, "link": 16, "calibration_report": 10}
    for ci, h in enumerate(cols, 1):
        ws_.column_dimensions[get_column_letter(ci)].width = widths.get(h, 24)
    for ri, r in enumerate(rows, 2):
        vals = list(r.values()) + ["", "", SCREENER_OUTCOME.get(r["ws_id"], "")]
        for ci, v in enumerate(vals, 1):
            c = ws_.cell(row=ri, column=ci, value=v)
            c.alignment = Alignment(wrap_text=True, vertical="top")
            if ci == 1:
                c.fill = PatternFill("solid", fgColor=fills[r["tier"]])
    ws_.freeze_panes = "C2"
    ws_.auto_filter.ref = "A1:%s%d" % (get_column_letter(len(cols)), len(rows) + 1)
    wb.save(out / "ipd_target_candidates.xlsx")
    print("candidates:", tc, "total", len(rows))
    print("pilot aggregate papers not on the 540 list:", [(p, s, ws, c) for p, s, ws, c, _ in not_in])


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "search/ipd")
