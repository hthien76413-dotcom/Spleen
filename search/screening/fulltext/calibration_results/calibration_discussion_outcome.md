# Full-text calibration (20 reports): what the two screeners agreed after discussion

Date of the report: 19 October 2026. Source: the author's message of that day (item 2 of it speaks of 舒俊 in the third person). **Claude has not opened any of these papers** (publisher, CNKI and Wanfang hosts are blocked here), so the statements about what the papers contain are the screeners' report, not checked.

The files next to this one (`ft_compare_all.csv`, `ft_conflicts_for_discussion.csv`, `ft_detail_differences.csv`, `ft_compare_summary.txt`) are the comparison of the two independently filled FT_log files **before** the discussion and are not changed. In the formal screening these 20 reports are screened again by each reviewer independently, so the outcomes below are not pre-set decisions for them.

## 1. The two Include-versus-Pending-IPD conflicts

| WS | Report | Before discussion | After discussion (reported) | Consequence |
|---|---|---|---|---|
| WS1859 | 李拴玲 2024, Beijing Children's Hospital | R1 Include (19 individual); R2 Pending IPD | **Include.** Full text has a 19-row per-patient table (Table 1). | Not an IPD target. |
| WS0049 | 赵娜 2025, Tianjin Children's Hospital | R1 Include (4 individual, 2 aggregate); R2 Pending IPD | **Include.** The PDF body has no per-patient table; figure legends give 4 children; online appendix 1 has a 6-row per-patient table (checked by the screeners). | Not an IPD target. The online appendix is needed for extraction. |

Both screeners agreed after discussion; nothing was passed to the adjudicator (杨俊). Basis stated by the author: guide 6.4 and 6.5. Guide 6.5 did not mention online appendices; v2026-10-19g adds that a per-patient table in an online appendix counts as individual data once the appendix has been opened and checked.

Pointer for the extraction stage (not a full-text decision): R1's pre-discussion note on WS0049 says one of the six children (case 2, a 1-year-old girl) had the spleen in its normal fossa (torsion of an orthotopic spleen). Whether that child is extracted is decided under the extraction guide (section 3), not at this stage.

## 2. `ws_basis` differences among reports both screeners included

Principle stated in the report: `Imaging and operation` is chosen only when both the imaging and the intraoperative findings establish the ectopic position or mobility; an operation that was only the treatment (e.g. splenectomy) and did not describe the position does not count as operation evidence. Written into the full-text guide as 6.7 (v2026-10-19g).

| WS | R1 before | R2 before | Reported outcome |
|---|---|---|---|
| WS0709 | Imaging and operation | Torsion only, position not stated | R2 changes to Imaging and operation |
| WS0780 | Imaging and operation | Named wandering spleen, no detail | R2 changes to Imaging and operation |
| WS1339 | Imaging and operation | Imaging shows ectopic position or mobility | R2 changes to Imaging and operation |
| WS2116 | Imaging and operation | Imaging shows ectopic position or mobility | R2 changes to Imaging and operation; the question whether the one-sentence operative confirmation is enough was answered later on 19 October: **maintained as Imaging and operation** (author's report) |
| WS2145 | Imaging and operation | Operation shows ectopic position or mobility | R2 keeps "Operation shows ectopic position or mobility" (series confirmed mainly at operation). **R1 (舒俊) agrees to change to "Operation shows ectopic position or mobility"** (author's report, later on 19 October). All five differences are now settled. |
| WS1908 | Imaging shows ectopic position or mobility | same | Unchanged (agreed before): the operation was only a therapeutic resection |
| WS1367 | Imaging shows ectopic position or mobility | same | Unchanged (agreed before): same reason |

Observations (Claude's, from R1's pre-discussion notes in `ft_compare_all.csv`; not decisions):
- WS2145 (settled): R1's note said that ultrasound was available only for case 3 of the three children; R1 then agreed to the operation-only value. The general question remains open: `ws_basis` has one value per report in FT_log but is per patient in the extraction workbook, so a series with mixed evidence has no rule yet (guide 6.7 says so).
- WS2116 (settled): R1's note says the intraoperative text is a single sentence ("consistent with the ultrasound diagnosis") with no description of ligaments or pedicle. The screeners maintained Imaging and operation. Guide 6.7 (v2026-10-19i) now says that an explicit statement that the operative findings agree with the imaging diagnosis counts as operation evidence; that generalisation is Claude's reading and is marked as awaiting confirmation.

## 3. Unchanged

WS0018 (both Exclude, E3 versus E4): by the D3 order the reason is E4; it was never a conflict.

The raw agreement before discussion stays as reported: 18 of 20 (90.0%); the two disagreements are the two conflicts above.
