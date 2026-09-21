# Project notes — wandering spleen manuscript

## Manuscript
"Wandering spleen in children: a novel splenopexy technique" (Jun Shu, Jun Yang [corresponding], Hongqiang Bian, Fei Peng, Ji Wang — Wuhan Children's Hospital, Tongji Medical College, HUST).

- Original 4-case submission: `Wandering spleen in children A novel splenopexy technique.docx`
- Revised 5-case version (adds Patient 5, updates follow-up): `Wandering spleen in children A novel splenopexy technique - 5 cases revised.docx`
- **EJP Original Article (the version to submit): `Wandering spleen in children - EJP original article.docx`** — 2477 words, Table 1 (per encounter), 5 figures, 20 references, structured abstract, What is Known/What is New box
- EJP Brief Report (fallback if the editor asks to downgrade): `Wandering spleen in children - EJP brief report.docx` — 1188 words, 1 table, 1 figure, 12 references

## Submission history
- **International Journal of Surgery** (IJS-D-26-02226): rejected 21 Sep 2026 after ~7-month review. Reviewers #1/#2 positive; Reviewer #3 gave "Major revision" and flagged: overstated efficacy of the reinforced-fixation technique (n=1, 6-month follow-up), wrong manuscript type (filed as Quality Improvement Study, is actually a retrospective case series), and heterogeneous outcomes (3/4 original patients lost the spleen). IJS offered an automatic transfer to Annals of Medicine and Surgery / Medicine — **declined**: IJS and AMSU are both part of the Riaz Agha journal group currently under a Clarivate citation-manipulation hold (Retraction Watch, Mar 2026); not pursuing either.

## Target journal decision
**Decided: submit to European Journal of Pediatrics** (Springer). IF 2.9, JCR Q1; Aims & Scope explicitly lists "pediatric surgery" as a covered field. Manuscript types are original articles/reviews/mini-reviews/brief reports — no dedicated case-series category, so the case-history sections should be tightened toward a brief-report style before submission.

Other journals evaluated and set aside: Journal of Pediatric Surgery (Q2, IF 2.3 — good fallback), BMC Pediatrics / Frontiers in Pediatrics–Pediatric Surgery section (Q2, ~1.9–2.2 — good fallback), Surgical Endoscopy (Q1, IF ~2.7 — stretch, scope less specific), Frontiers in Medicine (Q1, IF 3.6 — rejected, no pediatric-surgery section, poor scope fit), The Journal of Pediatrics (Q1, IF 3.6 — rejected, general-pediatrics scope, ~15% acceptance rate, Brief Report format capped at 1000 words/2 illustrations which would gut the case detail).

## Data confirmed by the author (21 Sep 2026) — all applied, highlights cleared
1. Case 4 (reinforced splenopexy) follow-up: **13 months** — confirmed correct.
2. Patient 5 preoperative platelet count: **normal** (no exact figure available; tables read "PC normal").
3. Patient 5 did receive postoperative oral dipyridamole — confirmed.
4. Ethics approval has been supplemented to cover Patient 5. Both manuscripts still cite **2025R156-E01**; update if the supplementary approval carries its own number.

## Outstanding before submission
- Figs. 11–12 of the full version (Patient 5 CT whirl sign / intraoperative photo) — legend placeholders only, images not yet supplied. These are still highlighted yellow in the 5-case .docx.

## Article type — decided
**Original Article.** EJP allows 3000 words and ~6 tables/figures (excess to supplementary); Brief Report allows only 1500 words, one table and/or figure, and 12 references. The figures are the paper's strongest asset (praised by IJS Reviewer #1), the rare-disease value lies in the longitudinal detail, and an editor can downgrade a submission to Brief Report but never upgrade one. The Brief Report version is kept as the fallback.

Both EJP versions are reframed around **delay, not technique, as the determinant of splenic loss**, with the reinforced two-pole fixation presented as a preliminary technical description. This answers IJS Reviewer #3's two heaviest criticisms directly.

## Data corrections applied
- **Case 3's interval from first presentation to splenic surgery is 62 months** (4.5 → 9.67 years), not 36 months. The "36 months" in the original case history is the gap between her *second* and *third* encounters and is correct there. The three-case mean of 32 months (16 + 19 + 62) is unchanged.

## Title — decided (both EJP versions)
**"Wandering spleen in children: delay determines splenic loss, and a reinforced two-pole splenopexy technique"** — author wanted the technique named in the title; combined with the delay finding for search visibility and impact. Applied to both `EJP original article.docx` and `EJP brief report.docx`.

## Case 5 imaging — pending, author will supply
Author sent two candidate whirl-sign CT photos (phone photos of a screen — not PACS exports). Neither clearly shows a diagnostic whirl sign on visual review by Claude: one is a low pelvic-level slice showing the ectopic spleen mass itself but below the pedicle level; the other is a higher slice showing indeterminate mesenteric/perisplenic stranding, not a clear spiral vessel pattern. Recommended: author to get a proper PACS export (PNG/TIFF, de-identified) of the splenic hilar level, and have the whirl sign confirmed by radiology before use. **Author says the whirl-sign image will be supplied "tomorrow."** Neither the Original Article nor the Brief Report currently uses any Case 5 image — both are already fully self-contained with Figs. 1–5 (Original Article) / Fig. 1 (Brief Report), none tied to Case 5. If a good Case 5 image arrives, the plan discussed is to swap out Fig. 1 (Case 2 infarct CT, most replaceable — Table 1 already carries that data) to stay within EJP's ~6 table/figure guidance.

## Still open
- Whether to soften "demonstrates safety and feasibility" / drop the "giant wandering spleen" claim in the conclusion of the **full 5-case version** (both EJP versions already use tempered wording) — not yet actioned.
- Ethics approval number: both EJP versions cite 2025R156-E01; replace if the supplementary approval has its own number.
- Case 5 whirl-sign figure: awaiting a proper PACS export from the author.

## Repo / PR
- Working branch: `claude/trusting-davinci-70prup`
- PR #1 (draft): adds the 5-case revised manuscript, all 10 original figures and formatting preserved, schema-validated.
