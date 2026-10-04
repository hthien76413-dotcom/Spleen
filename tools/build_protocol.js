const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, AlignmentType,
  Table, TableRow, TableCell, WidthType, ShadingType,
} = require("docx");

// Output directory for protocol_raw.docx: first CLI argument, else the current directory.
const SP = process.argv[2] || ".";
const FONT = { ascii: "Times New Roman", hAnsi: "Times New Roman", cs: "Times New Roman", eastAsia: "SimSun" };
const BODY = 22, TBL = 18, CODE = 18;

// segments: string, or [[text, {bold, italics, hl, mono}], ...]
const segs = (s) => (typeof s === "string" ? [[s, {}]] : s);
const run = (t, o = {}) => new TextRun({
  text: t,
  font: o.mono ? { ascii: "Consolas", hAnsi: "Consolas", cs: "Consolas", eastAsia: "SimSun" } : FONT,
  size: o.size || BODY, bold: o.bold, italics: o.italics,
  highlight: o.hl ? "yellow" : undefined,
});
const para = (s, o = {}) => new Paragraph({
  alignment: o.align || AlignmentType.LEFT,
  indent: o.indent ? { left: o.indent } : undefined,
  spacing: { line: o.line || 300, after: o.after === undefined ? 120 : o.after, before: o.before },
  children: segs(s).map(([t, so]) => run(t, { ...(so || {}), size: (so && so.size) || o.size })),
});
const h1 = (t) => para([[t, { bold: true, size: 26 }]], { before: 320, after: 140 });
const h2 = (t) => para([[t, { bold: true }]], { before: 200, after: 80 });
const bullet = (s, lvl = 0) => {
  const sg = segs(s);
  return para([["• ", {}], ...sg], { indent: 360 + 360 * lvl, after: 60 });
};
const code = (t) => para([[t, { mono: true, size: CODE }]], { indent: 360, after: 60, line: 260 });
const HL = (t) => [t, { hl: true }];

const cell = (s, w, o = {}) => new TableCell({
  width: { size: w, type: WidthType.DXA },
  shading: o.head ? { type: ShadingType.CLEAR, fill: "E7E6E6" } : undefined,
  margins: { top: 40, bottom: 40, left: 80, right: 80 },
  children: (Array.isArray(s) && Array.isArray(s[0]) && Array.isArray(s[0][0]) ? s : [segs(s)]).map((line) => new Paragraph({
    spacing: { line: 240, after: 0 },
    children: line.map(([t, so]) => run(t, { ...(so || {}), size: TBL, bold: o.head || (so && so.bold) })),
  })),
});
const table = (widths, head, rows) => new Table({
  width: { size: widths.reduce((a, b) => a + b, 0), type: WidthType.DXA },
  columnWidths: widths,
  rows: [
    new TableRow({ tableHeader: true, children: head.map((t, i) => cell(t, widths[i], { head: true })) }),
    ...rows.map((r) => new TableRow({ children: r.map((t, i) => cell(t, widths[i])) })),
  ],
});

const ch = [];

// ---------------------------------------------------------------- cover
ch.push(para([["Systematic review protocol — PROSPERO CRD420261520329", { bold: true, size: 30 }]], { after: 160 }));
ch.push(para([["Time to surgery and splenic salvage in children with wandering spleen: a systematic review of individual patient data, with a single-centre case series", { bold: true, size: 24 }]], { after: 160 }));
ch.push(para("Version 1.2, 4 October 2026. Prepared for the review team of Wuhan Children's Hospital.", { after: 120 }));
ch.push(para([["Version history. ", { bold: true, size: 20 }], ["Version 1.0 (uploaded at registration as draft v0.1). Version 1.1: search strategies (Section 5, Appendices A and B) revised after review by a medical librarian, before the formal searches were run; eligibility criteria, exposures, outcomes and analysis are unchanged. Version 1.2 (4 October 2026): as-run details of the formal searches added to Appendices A and B; deduplication done with a documented script and checked in EndNote (Section 14, Appendix B); Embase and Google Scholar were not searched and citation searching was not completed (see Appendices A2, A8 and B); eligibility criteria, exposures, outcomes and analysis are unchanged.", { size: 20 }]], { after: 240, align: AlignmentType.JUSTIFIED }));

// ---------------------------------------------------------------- 1
ch.push(h1("1. Review title and timescale"));
ch.push(h2("Review title"));
ch.push(para("Time to surgery and splenic salvage in children with wandering spleen: a systematic review of individual patient data, with a single-centre case series"));
ch.push(h2("Anticipated start and completion dates"));
ch.push(para([["Start: 28 September 2026    Completion: 28 June 2027", {}]]));
ch.push(h2("Stage of review at time of registration"));
ch.push(table([5200, 1700, 1700], ["Review stage", "Started", "Completed"], [
  ["Preliminary searches", "Yes", "Yes"],
  ["Piloting of the study selection process", "Yes", "No"],
  ["Formal screening of search results against eligibility criteria", "No", "No"],
  ["Data extraction", "No", "No"],
  ["Risk of bias (quality) assessment", "No", "No"],
  ["Data analysis", "No", "No"],
]));
ch.push(h2("Pilot work before registration"));
ch.push(para("Before this protocol was drafted, 53 reports (47 in English and 6 in Chinese) were collected by hand, and a data-extraction form was piloted on them (76 unique paediatric patients after removal of duplicate reports). The pilot suggested that the relation between time to surgery and splenic loss may differ between the duration of the index symptomatic episode and the total length of symptom history, and this informed the choice of primary exposure. Pilot data will not enter the final analysis: all reports, including the 53 piloted, will be screened and extracted afresh by two independent reviewers according to this protocol.", { align: AlignmentType.JUSTIFIED }));

// ---------------------------------------------------------------- 2
ch.push(h1("2. Review team, funding and conflicts of interest"));
ch.push(h2("Named contact"));
ch.push(para("Jun Shu. Department of General Surgery, Wuhan Children's Hospital (Wuhan Maternal and Child Healthcare Hospital), Tongji Medical College, Huazhong University of Science & Technology, Wuhan 430016, Hubei, China. Email: shujunmengzhe@163.com"));
ch.push(h2("Review team members"));
ch.push(para([["Note: PROSPERO now requires the named contact who creates the account to hold an ORCID (a free, two-minute registration at orcid.org if not already held). ORCID for the other team members below is optional but recommended.", { italics: true, size: 20 }]], { after: 120 }));
ch.push(table([2400, 3600, 2600], ["Name", "Affiliation", "ORCID"], [
  ["Jun Shu", "Wuhan Children's Hospital, Tongji Medical College, HUST", "0009-0001-3003-1452"],
  ["Jun Yang", "Wuhan Children's Hospital, Tongji Medical College, HUST", "0009-0006-0669-4340"],
  ["Hongqiang Bian", "Wuhan Children's Hospital, Tongji Medical College, HUST", "—"],
  ["Fei Peng", "Wuhan Children's Hospital, Tongji Medical College, HUST", "—"],
  ["Ji Wang", "Wuhan Children's Hospital, Tongji Medical College, HUST", "—"],
]));
ch.push(para([["Roles: independent reviewer 1, Jun Shu; independent reviewer 2, Fei Peng; adjudicator, Jun Yang; statistical analysis, Ji Wang.", {}]], { before: 120 }));
ch.push(h2("Funding sources"));
ch.push(para("None."));
ch.push(h2("Conflicts of interest"));
ch.push(para("None known."));

// ---------------------------------------------------------------- 3
ch.push(h1("3. Review question"));
ch.push(para([["Primary question. ", { bold: true }], ["In children younger than 18 years who undergo surgery for wandering spleen, is a longer duration of the index symptomatic episode before operation associated with a non-viable spleen at operation?", {}]], { align: AlignmentType.JUSTIFIED }));
ch.push(para([["Secondary questions.", { bold: true }]], { after: 60 }));
[
  "Is a non-viable spleen associated with the total length of symptom history, with a missed diagnosis at an earlier healthcare contact, or with a known diagnosis for which surgery was deferred?",
  "How often does torsion occur while children with a known wandering spleen are awaiting surgery?",
  "How often is the spleen lost for reasons other than non-viability at presentation (removal of a viable spleen, or failure after splenopexy), and with which fixation techniques?",
  "Is a raised preoperative platelet count associated with a non-viable spleen?",
].forEach((t, i) => ch.push(para(`(${String.fromCharCode(97 + i)}) ${t}`, { indent: 360, after: 60, align: AlignmentType.JUSTIFIED })));

// ---------------------------------------------------------------- 4
ch.push(h1("4. Background and rationale"));
ch.push(para("Wandering spleen is rare in children, and the published experience consists almost entirely of case reports and small series. Torsion of the elongated vascular pedicle can lead to infarction, and whether the spleen can be preserved depends on its viability at operation. Delay in diagnosis and treatment is often cited as a cause of splenic loss, but this has not been examined systematically. The most recent systematic review of paediatric wandering spleen (Ganarin et al., 2021; PROSPERO CRD42018089971) pooled 197 children, 194 of them from English-language reports published between 1990 and 2018, and focused on clinical presentation and surgical technique; it did not analyse time to surgery [1]. In our own series of five children, four lost the spleen, which raised the question of how delay relates to splenic loss. This review will pool individual patient data from all published paediatric cases, including Chinese-language reports and those published since 2018, to examine that relation.", { align: AlignmentType.JUSTIFIED }));

// ---------------------------------------------------------------- 5
ch.push(h1("5. Searches"));
ch.push(para([
  ["We will search MEDLINE (via PubMed), Embase (Embase.com), Web of Science Core Collection, Scopus, China National Knowledge Infrastructure (CNKI), Wanfang Data and the China Biology Medicine database (CBM, via SinoMed) from inception to the date of search. Searches combine controlled vocabulary, where available, with free-text synonyms for wandering spleen, splenic torsion and splenopexy. No language, date, age or study-design limits will be applied to the searches. The strategies were reviewed by a medical librarian before the formal searches, and the PubMed strategy was test-run on 28 September 2026. We will also screen the first 200 Google Scholar results for the query \"wandering spleen\" children, sorted by relevance, recording the date and the number of records actually browsed; check the reference lists of all included reports and of previous reviews and larger series [1, 5–12]; and identify reports citing Ganarin et al. [1] through Web of Science or Google Scholar. For each database, the search history page showing the date and the number of records will be saved as a screenshot, and the searches will be reported according to PRISMA-S [13]. Searches will be rerun before the final analysis if more than six months have passed. Deviations from this plan: Embase and Google Scholar were not searched and citation searching was not completed (see Appendices A2, A8 and B). Full strategies are given in Appendix A, and the search log template in Appendix B.", {}],
], { align: AlignmentType.JUSTIFIED }));

// ---------------------------------------------------------------- 6-11
ch.push(h1("6. Condition or domain being studied"));
ch.push(para("Wandering spleen (splenic ectopia due to absent or lax suspensory ligaments), with or without torsion of the splenic pedicle, in children."));

ch.push(h1("7. Participants / population"));
ch.push(para([["Inclusion criteria", { bold: true }]], { after: 60 }));
[
  "Age younger than 18 years at operation (or at diagnosis, for children managed without operation).",
  "Wandering spleen confirmed by imaging and/or at operation, defined as an abnormally mobile spleen displaced from the left upper quadrant because of absent or lax suspensory ligaments, with or without pedicle torsion. Congenital and acquired forms (for example after fundoplication or nephrectomy) are both eligible; acquired cases form a subgroup.",
  "Individual data reported (or supplied by the authors) on age and, for the primary analysis, on splenic viability at operation.",
].forEach((t) => ch.push(bullet(t)));
ch.push(para([["Exclusion criteria", { bold: true }]], { after: 60, before: 80 }));
[
  "Torsion of an accessory spleen, including a wandering accessory spleen.",
  "Torsion of an orthotopic spleen without ectopia; splenosis.",
  "Patients whose age is not reported individually and cannot be established as younger than 18 years.",
].forEach((t) => ch.push(bullet(t)));
ch.push(para("Children managed without operation will be summarised descriptively; they have no operative outcome and do not enter the primary analysis.", { before: 80, align: AlignmentType.JUSTIFIED }));

ch.push(h1("8. Exposure"));
ch.push(para([["Primary exposure: duration of the index symptomatic episode. ", { bold: true }],
  ["Time from onset of the symptoms of the presentation that led to operation until the operation, in days. Time spent in hospital before operation during the same admission is included; a planned interval between discharge and a scheduled elective operation is not (it is recorded separately as a waiting interval). Conversion rules for reported durations are given in Appendix C.", {}]], { align: AlignmentType.JUSTIFIED }));
ch.push(para([["Secondary exposures.", { bold: true }]], { after: 60 }));
[
  "Total symptom history: time from the first symptom attributed to wandering spleen, including earlier episodes, to operation.",
  "Missed diagnosis: at least one documented earlier healthcare contact at which wandering spleen was not diagnosed or an alternative diagnosis was made, including misread imaging.",
  "Known diagnosis with deferred surgery: wandering spleen diagnosed before the index episode, with surgery not performed at that time (family declined, observation advised, or elective operation scheduled).",
].forEach((t) => ch.push(bullet(t)));

ch.push(h1("9. Comparator"));
ch.push(para("For the primary exposure, the comparison is across the continuous range of duration (shorter versus longer). For binary secondary exposures, children without the exposure.", { align: AlignmentType.JUSTIFIED }));

ch.push(h1("10. Types of study to be included"));
ch.push(para("Case reports, case series, cohort studies, letters, and reviews that describe original patients, provided that individual patient data are reported or supplied by the authors. Our institutional series of five children (ethics approval 2025R156-E01) will be pooled with the published cases. Excluded: reviews without new patients (used only for reference checking), conference abstracts, and editorials without patient data. Reports with full text in English or Chinese will be extracted; reports in other languages will be listed and counted but not extracted.", { align: AlignmentType.JUSTIFIED }));

ch.push(h1("11. Context"));
ch.push(para("Any clinical setting in any country."));

// ---------------------------------------------------------------- 12-13
ch.push(h1("12. Main outcome"));
ch.push(para("Non-viable spleen at the index operation: total splenectomy, or partial splenectomy, performed because of infarction, necrosis or failure to reperfuse after detorsion, as judged at operation and/or on histology. A spleen that was viable at operation but removed for another reason counts as viable for this outcome and is reported under additional outcomes.", { align: AlignmentType.JUSTIFIED }));
ch.push(para([["Measure of effect: ", { bold: true }], ["odds ratio per doubling of the index-episode duration, with 95% confidence interval.", {}]]));

ch.push(h1("13. Additional outcomes"));
[
  "Viable spleen removed at the index operation (failure of fixation, surgeon's preference or other stated reason).",
  "Failure after splenopexy (recurrent migration, re-torsion, or ischaemia or thrombosis requiring further surgery or splenectomy), by fixation technique.",
  "Torsion occurring while a child with a known wandering spleen was awaiting surgery.",
  "Splenic status at last follow-up (preserved, partially preserved, lost) and length of follow-up.",
  "Preoperative platelet count and thrombocytosis (platelet count above 450 × 10⁹/L).",
  "Associated organ involvement (gastric volvulus, pancreatic tail torsion, bowel obstruction) and reported post-splenectomy complications.",
].forEach((t) => ch.push(bullet(t)));

// ---------------------------------------------------------------- 14
ch.push(h1("14. Data extraction (selection and coding)"));
ch.push(para([
  ["Records were deduplicated with a documented, rule-based script (identical DOI; identical title with the same first author and year; similar title with the same first author; same first author, year, volume and first page; and further rules for Chinese-language records and for differently written author names; the tiers are listed in Appendix B), and EndNote’s duplicate finder was then run on the result as a check. The deduplicated records will be screened in Rayyan. Two reviewers will independently screen titles and abstracts, then full texts, against the eligibility criteria; disagreements will be resolved by discussion or, if needed, by a third reviewer (JY). Chinese-language reports will be screened by reviewers fluent in Chinese. Before formal screening, both reviewers will screen a calibration set of 50 records and discuss discrepancies.", {}],
], { align: AlignmentType.JUSTIFIED }));
ch.push(para("Two reviewers will independently extract data for every included patient with the form in Appendix C, after calibration on 10 reports. Agreement on the primary exposure and the primary outcome will be reported as Cohen's kappa. Where a report describes several patients only in aggregate, the corresponding author will be emailed twice, four weeks apart, to request individual data; if none are supplied, the report will be described narratively.", { align: AlignmentType.JUSTIFIED }));
ch.push(para("Duplicate reports of the same patient will be identified by matching institution, study period, age, sex and clinical details. The most complete report will be used and the others linked to it.", { align: AlignmentType.JUSTIFIED }));

// ---------------------------------------------------------------- 15
ch.push(h1("15. Risk of bias (quality) assessment"));
ch.push(para("Two reviewers will independently assess each report with the tool of Murad et al. for case reports and case series [2], using the items on selection (whether the patients represent the whole experience of the investigators), ascertainment of exposure (whether the timing of symptom onset and of operation is stated precisely), ascertainment of outcome (whether splenic viability is stated, with its basis), alternative explanations, adequacy of follow-up, and sufficiency of reporting. The items on challenge–rechallenge and dose–response do not apply and will be omitted. No summary score will be calculated; a report will be judged adequate for the primary question when the exposure, outcome and reporting items are all satisfied.", { align: AlignmentType.JUSTIFIED }));

// ---------------------------------------------------------------- 16
ch.push(h1("16. Strategy for data synthesis"));
ch.push(para([["Descriptive analysis. ", { bold: true }], ["Characteristics of all included patients will be summarised with counts and percentages, or medians and ranges.", {}]], { align: AlignmentType.JUSTIFIED }));
ch.push(para([["Primary analysis. ", { bold: true }], ["One-stage logistic regression of a non-viable spleen on log2-transformed index-episode duration, with cluster-robust standard errors by report, adjusted for age (years) and period of publication (before 2000, 2000–2014, 2015 onward). Degree of torsion and infarction lie on the causal pathway and will not be adjusted for. If the number of events allows at least 10 events per model degree of freedom, non-linearity will be examined with a restricted cubic spline with three knots.", {}]], { align: AlignmentType.JUSTIFIED }));
ch.push(para([["Secondary analyses. ", { bold: true }], ["Index-episode duration in four categories (2 days or less, 3–7 days, 8–30 days, more than 30 days), with proportions, exact 95% confidence intervals and a test for trend. Total symptom history and the binary secondary exposures will be analysed with the same model. The proportion of children with a known diagnosis who developed torsion while awaiting surgery will be given with an exact 95% confidence interval. Failures after splenopexy will be tabulated by fixation technique.", {}]], { align: AlignmentType.JUSTIFIED }));
ch.push(para([["Missing data. ", { bold: true }], ["The primary analysis will use complete cases. Patients with and without a reported duration will be compared on characteristics and outcome, and bounding analyses will assign all missing durations first to the shortest and then to the longest category. Multiple imputation will not be used, because duration is unlikely to be missing at random: reports of successful salvage may omit the timeline.", {}]], { align: AlignmentType.JUSTIFIED }));
ch.push(para([["Reporting bias. ", { bold: true }], ["Funnel plots are not applicable. Outcomes will be compared between single case reports and series of three or more consecutive patients, which are less prone to selective reporting.", {}]], { align: AlignmentType.JUSTIFIED }));
ch.push(para([["Certainty of evidence. ", { bold: true }], ["Certainty will be described with GRADE principles; evidence drawn from case reports and series is expected to be of very low certainty.", {}]], { align: AlignmentType.JUSTIFIED }));
ch.push(para([["Software: ", { bold: true }], ["R (R Foundation for Statistical Computing, Vienna, Austria); the version used will be reported.", {}]]));

// ---------------------------------------------------------------- 17-18
ch.push(h1("17. Analysis of subgroups or subsets"));
[
  "Wandering spleen presenting with gastric volvulus or gastric outlet obstruction versus other presentations.",
  "Congenital versus acquired wandering spleen.",
  "With versus without an associated diaphragmatic anomaly (congenital diaphragmatic hernia or eventration).",
].forEach((t) => ch.push(bullet(t)));

ch.push(h1("18. Sensitivity analyses"));
[
  "Excluding our own five patients.",
  "Restricted to patients with pedicle torsion confirmed at operation.",
  "Coding partial splenectomy for partial infarction as salvage rather than as a non-viable spleen.",
  "Alternative coding of index episodes described as intermittent or worsening (Appendix C, rule 6).",
  "Restricted to reports judged adequate in the risk-of-bias assessment.",
  "Excluding Chinese-language reports.",
  "Excluding reports published before 2000.",
  "Mixed-effects logistic regression with a random intercept for each report.",
].forEach((t, i) => ch.push(para(`${i + 1}. ${t}`, { indent: 360, after: 60 })));

// ---------------------------------------------------------------- 19
ch.push(h1("19. Other registration fields"));
ch.push(table([3000, 5600], ["Field", "Entry"], [
  ["Type and method of review", "Systematic review of individual patient data extracted from published reports (or supplied by their authors), pooled with a single-centre case series; reported according to PRISMA 2020 and PRISMA-IPD [3, 4]."],
  ["Language", "English"],
  ["Country", "China"],
  ["Dissemination plans", "Publication in a peer-reviewed journal, with the full extracted individual patient dataset as supplementary material."],
  ["Keywords", "wandering spleen; splenic torsion; splenopexy; splenectomy; children; delayed diagnosis; time-to-treatment; individual patient data"],
  ["Existing review on the same topic", "Ganarin et al. 2021, PROSPERO CRD42018089971 [1]: English-language reports 1990–2018, focused on presentation and technique, with no analysis of time to surgery. This review differs in its primary question (time to surgery), in including Chinese-language reports, and in covering reports published after 2018."],
  ["Current review status", "Ongoing"],
]));

// ---------------------------------------------------------------- refs
ch.push(h1("References"));
[
  "Ganarin A, Fascetti Leon F, La Pergola E, Gamba P. Surgical approach of wandering spleen in infants and children: a systematic review. J Laparoendosc Adv Surg Tech A. 2021. doi:10.1089/lap.2020.0759",
  "Murad MH, Sultan S, Haffar S, Bazerbachi F. Methodological quality and synthesis of case series and case reports. BMJ Evid Based Med. 2018;23:60–3.",
  "Page MJ, McKenzie JE, Bossuyt PM, et al. The PRISMA 2020 statement: an updated guideline for reporting systematic reviews. BMJ. 2021;372:n71.",
  "Stewart LA, Clarke M, Rovers M, et al. Preferred reporting items for a systematic review and meta-analysis of individual participant data: the PRISMA-IPD statement. JAMA. 2015;313:1657–65.",
  "Brown CVR, Virgilio GR, Vazquez WD. Wandering spleen and its complications in children: a case series and review of the literature. J Pediatr Surg. 2003;38:1676–9.",
  "Lombardi R, Menchini L, Corneli T, et al. Wandering spleen in children: a report of 3 cases and a brief literature review underlining the importance of diagnostic imaging. Pediatr Radiol. 2014. doi:10.1007/s00247-013-2851-6",
  "Alqadi GO, Saxena AK. Is laparoscopic approach for wandering spleen in children an option? J Minim Access Surg. 2019;15:93–7.",
  "Moore E, O'Brien JW, Merali N, et al. Gastric outlet obstruction secondary to a wandering spleen: systematic review and surgical management of a case. Ann R Coll Surg Engl. 2023;105:501–6.",
  "Allen KB, Andrews G. Pediatric wandering spleen—the case for splenopexy: review of 35 reported cases in the literature. J Pediatr Surg. 1989;24:432–5.",
  "Soleimani M, Mehrabi A, Kashfi A, et al. Surgical treatment of patients with wandering spleen: report of six cases with a review of the literature. Surg Today. 2007;37:261–9.",
  "Fiquet-Francois C, Belouadah M, Ludot H, et al. Wandering spleen in children: multicenter retrospective study. J Pediatr Surg. 2010;45:1519–24.",
  "Barabino M, Luigiano C, Pellicano R, et al. “Wandering spleen” as a rare cause of recurrent abdominal pain: a systematic review. Minerva Chir. 2019;74:359–63.",
  "Rethlefsen ML, Kirtley S, Waffenschmidt S, et al. PRISMA-S: an extension to the PRISMA Statement for Reporting Literature Searches in Systematic Reviews. Syst Rev. 2021;10:39.",
].forEach((t, i) => ch.push(para(`${i + 1}. ${t}`, { after: 60, indent: 0 })));

// ---------------------------------------------------------------- Appendix A
ch.push(h1("Appendix A. Search strategies"));
ch.push(para("Each strategy is the whole search: no language, date, age or publication-type limits. Lines marked “check” depend on a controlled-vocabulary term that must be confirmed in the database's thesaurus before the search is run; drop the line if the term does not exist. The strategies below were revised after review by a medical librarian (version 1.1). In every database, the expression actually displayed after the search is run is the one to record.", { align: AlignmentType.JUSTIFIED }));

ch.push(h2("A1. MEDLINE via PubMed"));
[
  '#1  "Wandering Spleen"[Mesh]',
  '#2  "wandering spleen*"[tiab] OR "ectopic spleen*"[tiab] OR "floating spleen*"[tiab] OR "mobile spleen*"[tiab] OR "movable spleen*"[tiab] OR "displaced spleen*"[tiab] OR "pelvic spleen*"[tiab] OR "dystopic spleen*"[tiab] OR splenoptosis[tiab] OR "splenic ptosis"[tiab] OR "splenic ectopia"[tiab]',
  '#3  "splenic torsion"[tiab] OR "spleen torsion"[tiab] OR "torsion of spleen"[tiab] OR "splenic volvulus"[tiab] OR "splenic pedicle torsion"[tiab]',
  '#4  splenopex*[tiab]',
  '#5  "Torsion Abnormality"[Mesh] AND ("Spleen"[Mesh] OR spleen*[tiab] OR splenic[tiab])',
  '#6  "spleen torsion"[tiab:~2] OR "splenic torsion"[tiab:~2] OR "spleen volvulus"[tiab:~2] OR "spleen twisted"[tiab:~2] OR "splenic twisted"[tiab:~2] OR "migrating spleen"[tiab:~0] OR "migrating spleens"[tiab:~0] OR "migratory spleen"[tiab:~0]',
  '#7  #1 OR #2 OR #3 OR #4 OR #5 OR #6',
].forEach((t) => ch.push(code(t)));
ch.push(para("“Wandering Spleen”, “Torsion Abnormality” and “Spleen” are confirmed MeSH headings; MeSH has no separate heading for splenic torsion, hence #5. Eight quoted phrases in version 1.0 (“wandering splenic”, “migrating spleen*”, “lien migrans”, “splen migrans”, “lien mobilis”, “torsion of the spleen”, “volvulus of the spleen”, “torsion of the splenic pedicle”) are not in the PubMed phrase index and were silently ignored; they are replaced by the proximity searches in #6. Proximity searching ([tiab:~N]) cannot be combined with truncation (*). A distance of 2, and no proximity term pairing splenic with volvulus, avoid retrieving splenic-flexure volvulus of the colon. In the librarian's test run on 28 September 2026, #7 retrieved 1263 records, against 1187 for version 1.0, with all 1187 retained. These figures served only to check the strategy; the formal search will be run on the PubMed website, with the History and Search Details page saved and all records exported.", { indent: 360, size: 20, align: AlignmentType.JUSTIFIED }));

ch.push(h2("A2. Embase via Embase.com"));
[
  "#1  'wandering spleen'/exp                                     (check in Emtree)",
  "#2  ('wandering spleen*' OR 'wandering splenic' OR 'ectopic spleen*' OR 'floating spleen*' OR 'mobile spleen*' OR 'movable spleen*' OR 'displaced spleen*' OR 'migrating spleen*' OR 'pelvic spleen*' OR 'dystopic spleen*' OR splenoptosis OR 'splenic ptosis' OR 'splenic ectopia' OR 'lien migrans' OR 'splen migrans' OR 'lien mobilis'):ti,ab,kw",
  "#3  ('splenic torsion' OR 'spleen torsion' OR 'torsion of the spleen' OR 'torsion of spleen' OR 'splenic volvulus' OR 'volvulus of the spleen' OR 'splenic pedicle torsion' OR 'torsion of the splenic pedicle'):ti,ab,kw",
  "#4  splenopex*:ti,ab,kw",
  "#5  ((spleen* NEAR/3 (torsion* OR twist* OR volvul* OR wander* OR ectopi* OR float* OR dystop* OR ptos*)) OR (splenic NEAR/3 (torsion* OR twist* OR wander* OR dystop*))):ti,ab,kw",
  "#6  #1 OR #2 OR #3 OR #4 OR #5",
].forEach((t) => ch.push(code(t)));
ch.push(para("Before searching, confirm in Emtree that ‘wandering spleen’ is a preferred term; if it maps to another preferred term, use that term with /exp. Then look up spleen torsion, splenic torsion and splenopexy: any that is a separate preferred term is added to #1 with OR and /exp; any that is only a synonym of wandering spleen is not added. Conference abstracts are removed at screening, not by a search limit, so that their number can be reported.", { indent: 360, size: 20, align: AlignmentType.JUSTIFIED }));
ch.push(para("Status on 4 October 2026: Embase was not searched. On 29 September 2026 the Embase.com site was reached through the institutional route and the Emtree check described above was done (wandering spleen and splenopexy are preferred terms, with synonyms; spleen torsion and splenic torsion are candidate terms only), but no search was run in that session. On 4 October 2026 the site no longer recognised the institutional entitlement (the page stated that the account did not have direct access to Embase, and the Check access button did not lead to a login), and access could not be restored. No records were retrieved from Embase. If access is obtained later through a librarian or a colleague with a licence, the first line should read 'wandering spleen'/exp OR 'splenopexy'/exp, followed by lines #2 to #5 above and a final OR line, and the date, searcher and route must be logged. Otherwise this is reported as a deviation from the registered protocol, in the PROSPERO amendment, the Methods and the Limitations.", { indent: 360, size: 20, align: AlignmentType.JUSTIFIED }));

ch.push(h2("A3. Web of Science Core Collection (Advanced Search)"));
ch.push(code('TS=("wandering spleen*" OR "wandering splenic" OR "ectopic spleen*" OR "floating spleen*" OR "mobile spleen*" OR "movable spleen*" OR "displaced spleen*" OR "migrating spleen*" OR "pelvic spleen*" OR "dystopic spleen*" OR splenoptosis OR "splenic ptosis" OR "splenic ectopia" OR "lien migrans" OR "splen migrans" OR "lien mobilis" OR "splenic torsion" OR "spleen torsion" OR "torsion of the spleen" OR "torsion of spleen" OR "splenic volvulus" OR "volvulus of the spleen" OR "splenic pedicle torsion" OR "torsion of the splenic pedicle" OR splenopex* OR (spleen* NEAR/3 (torsion* OR twist* OR volvul* OR wander* OR ectopi* OR float* OR dystop* OR ptos*)) OR (splenic NEAR/3 (torsion* OR twist* OR wander* OR dystop*)))'));
ch.push(para("As run on 29 September 2026 (Jun Shu; institutional account; Advanced Search; Web of Science Core Collection, Editions = All, no date range set): 750 records. The subscription covers eight indexes, each from the year shown: SCI-EXPANDED 1997, SSCI 2000, A&HCI 2005, CPCI-S 1998, CPCI-SSH 2001, ESCI 2021, CCR-EXPANDED 1985 and IC 1993 (no Book Citation Index). Coverage is therefore limited by the licence and is not \"inception\". All 750 records were exported in RIS format (unique accession numbers 750); the export count equals the hit count. Recall check against the 47 English-language pilot reports (first author and year ±1): 40 found; the other 7 (Steinberg 2002, Parisinos 2011, Goyal 2014, Rellum 2014, Torri 2015, Cantone 2016, Umeda 2020) are indexed in PubMed but are not in the Web of Science result set. A title-phrase search for these seven papers in the same editions on 29 September 2026, together with one control title known to be in the export, retrieved only the control, so the seven are not indexed in this subscription's Core Collection and the gap is one of coverage, not of the search string.", { indent: 360, size: 20, align: AlignmentType.JUSTIFIED }));

ch.push(h2("A4. Scopus (Advanced Search)"));
ch.push(code('TITLE-ABS-KEY("wandering spleen*" OR "wandering splenic" OR "ectopic spleen*" OR "floating spleen*" OR "mobile spleen*" OR "movable spleen*" OR "displaced spleen*" OR "migrating spleen*" OR "pelvic spleen*" OR "dystopic spleen*" OR splenoptosis OR "splenic ptosis" OR "splenic ectopia" OR "lien migrans" OR "splen migrans" OR "lien mobilis" OR "splenic torsion" OR "spleen torsion" OR "torsion of the spleen" OR "torsion of spleen" OR "splenic volvulus" OR "volvulus of the spleen" OR "splenic pedicle torsion" OR "torsion of the splenic pedicle" OR splenopex* OR (spleen* W/3 (torsion* OR twist* OR volvul* OR wander* OR ectopi* OR float* OR dystop* OR ptos*)) OR (splenic W/3 (torsion* OR twist* OR wander* OR dystop*)))'));
ch.push(para("In the proximity terms of A2–A4, spleen* does not match splenic, so splenic is searched separately; it is paired only with torsion*, twist*, wander* and dystop*, because pairing it with volvul* retrieves splenic-flexure volvulus of the colon.", { indent: 360, size: 20, align: AlignmentType.JUSTIFIED }));
ch.push(para("As run on 29 September 2026 (Jun Shu; accessed through VPN; Scopus advanced query, Documents tab only; no date, language, document-type or other limits set): 1,563 records. The Preprints and Secondary documents tabs were not searched. All 1,563 records were exported in RIS format (1,563 unique Scopus identifiers); the export count equals the hit count. Recall check against the 47 English-language pilot reports (first author and year ±1): 43 found; the other 4 (Goyal 2014, Rellum 2014, Cantone 2016, Bhambu 2023) are indexed in PubMed but are not in the Scopus result set. A title-phrase search for the four papers on 29 September 2026, together with one control title known to be in the export, retrieved only the control, so the four are not covered by Scopus (Documents) and the gap is one of coverage, not of the search string.", { indent: 360, size: 20, align: AlignmentType.JUSTIFIED }));

ch.push(h2("A5. CNKI 中国知网（专业检索）"));
ch.push(code("TKA=('游走脾'+'异位脾'+'漂浮脾'+'脾下垂'+'脾异位'+'脾脏异位'+'脾扭转'+'脾脏扭转'+'脾蒂扭转'+'脾固定术'+'脾脏固定术'+'脾固定'+'脾脏固定')"));
ch.push(para("TKA 为“篇关摘”（篇名、关键词、摘要）；符号一律用英文半角。如运行时报错，改为逐词用 OR 连接（OR 前后留空格）：TKA='游走脾' OR TKA='异位脾' OR …。不用“游离脾”：“游离脾扭转”“游离脾蒂扭转”已被‘脾扭转’‘脾蒂扭转’覆盖，且单独检索显示“游离脾”这一字符串主要命中两类无关文献——结直肠癌手术中“游离结肠脾曲”（脾曲为解剖部位，非脾脏本身）的操作表述，以及脾切除、肝移植、胃癌手术中“脾脏游离”的操作描述。正式检索时另单独运行 TKA='游离脾'（2026-09-28，舒俊检索，共153条），浏览全部标题确认均为上述两类无关文献，不并入正式结果。", { indent: 360, size: 20, align: AlignmentType.JUSTIFIED }));

ch.push(h2("A6. 万方数据（专业检索）"));
ch.push(code('主题:("游走脾" or "异位脾" or "漂浮脾" or "脾下垂" or "脾异位" or "脾脏异位" or "脾扭转" or "脾脏扭转" or "脾蒂扭转" or "脾固定术" or "脾脏固定术" or "脾固定" or "脾脏固定")'));
ch.push(para("“主题”字段包括题名、关键词和摘要；双引号表示精确匹配；冒号、括号、引号均用英文半角。", { indent: 360, size: 20, align: AlignmentType.JUSTIFIED }));

ch.push(h2("A7. 中国生物医学文献数据库 CBM（SinoMed）"));
[
  '#1  "游走脾"[不加权:扩展]',
  '#2  "游走脾"[常用字段:智能] OR "异位脾"[常用字段:智能] OR "漂浮脾"[常用字段:智能] OR "脾下垂"[常用字段:智能] OR "脾异位"[常用字段:智能] OR "脾脏异位"[常用字段:智能] OR "脾扭转"[常用字段:智能] OR "脾脏扭转"[常用字段:智能] OR "脾蒂扭转"[常用字段:智能] OR "脾固定术"[常用字段:智能] OR "脾脏固定术"[常用字段:智能] OR "脾固定"[常用字段:智能] OR "脾脏固定"[常用字段:智能]',
  '#3  (#2) OR (#1)',
].forEach((t) => ch.push(code(t)));
ch.push(para("按实际检索顺序列出（2026-09-29，舒俊）：#1 为主题词“游走脾”，于 SinoMed“主题检索”中确认存在（款目词与主题词均为“游走脾”，主题词表显示 61 篇），检索史中生成 \"游走脾\"[不加权:扩展]，61 条；#2 为自由词，在高级检索中输入，421 条；#3 为二者合并，421 条。主题词一行未增加任何记录（其 61 条均已包含在 #2 中）。年代栏为空，未勾选二次检索，“限定检索”中文献类型、年龄组、性别、对象类型、其它各项均未勾选。", { indent: 360, size: 20, align: AlignmentType.JUSTIFIED }));

ch.push(h2("A8. Supplementary sources"));
[
  "Google Scholar: query \"wandering spleen\" children (with the quotation marks) — first 200 records sorted by relevance; record the date of the search and the number of records actually browsed.",
  "Backward citation searching: reference lists of all included reports and of previous reviews and larger series — Allen and Andrews 1989 [9], Brown et al. 2003 [5], Soleimani et al. 2007 [10], Fiquet-Francois et al. 2010 [11], Lombardi et al. 2014 [6], Alqadi and Saxena 2019 [7], Barabino et al. 2019 [12], Ganarin et al. 2021 [1] and Moore et al. 2023 [8]. Ganarin et al. searched English-language reports from 1990 to 2018 with the single term wandering spleen, so its included studies serve only as a supplementary source.",
  "Forward citation searching: reports citing Ganarin et al. 2021 [1], via Web of Science or Google Scholar.",
  "Authors of series reported only in aggregate: individual data requested by email (Section 14).",
].forEach((t) => ch.push(bullet(t)));
ch.push(para("Status on 4 October 2026: the supplementary sources were not completed. (1) Google Scholar was not searched: Google returned its unusual-traffic block page and no results were seen. (2) Forward citation searching of Ganarin et al. 2021 was started on 4 October 2026 (Jun Shu): the cited-by lists in Web of Science and in Scopus each showed 13 documents, but the lists were not exported and therefore were not screened. (3) Backward citation searching of the reference lists of the previous reviews listed above was not done. (4) Backward citation searching of the included reports depends on the final included set and has not started. No record from these sources entered the screening set, which consists of the six database searches in A1 and A3 to A7. The omissions are reported as deviations from the registered protocol in the PROSPERO amendment, the Methods and the Limitations.", { indent: 360, size: 20, align: AlignmentType.JUSTIFIED }));

// ---------------------------------------------------------------- Appendix B
ch.push(h1("Appendix B. Search log"));
ch.push(para("Complete one row per source on the day of the search, and save a screenshot of each database's search history page showing the date and the number of records. These records feed the PRISMA flow diagram and the PRISMA-S checklist [13].", { align: AlignmentType.JUSTIFIED }));
const blank = ["", "", "", "", "", ""];
ch.push(table([2000, 1500, 1200, 1300, 1300, 1300], ["Source", "Platform / interface", "Date searched", "Coverage (from–to)", "Records retrieved", "Searcher"], [
  ["MEDLINE", "PubMed", "2026-09-28", "inception–2026-09-28", "1263", "Jun Shu"],
  ["Embase", "Embase.com — NOT SEARCHED: institutional access not available on 4 October 2026 (Emtree check only, 29 September 2026); see note under A2", "", "", "0", ""],
  ["Web of Science Core Collection", "Clarivate, institutional account; Editions = All: SCI-EXPANDED 1997–, SSCI 2000–, A&HCI 2005–, CPCI-S 1998–, CPCI-SSH 2001–, ESCI 2021–, CCR-EXPANDED 1985–, IC 1993–", "2026-09-29", "by index (see left)–2026-09-29", "750", "Jun Shu"],
  ["Scopus", "Elsevier, VPN; advanced query, Documents tab only (Preprints and Secondary documents not searched); no filters", "2026-09-29", "no date limit–2026-09-29", "1563", "Jun Shu"],
  ["CNKI 中国知网", "kns.cnki.net", "2026-09-28", "inception–2026-09-28", "486", "Jun Shu"],
  ["CNKI check: TKA='游离脾'", "153 records, not merged; all titles browsed — mostly \"结肠脾曲\" (colonic splenic flexure) mobilisation in colorectal surgery, and splenectomy/transplant \"脾脏游离\" operative steps, none on wandering spleen", "2026-09-28", "", "153", "Jun Shu"],
  ["万方数据", "wanfangdata.com.cn", "2026-09-28", "inception–2026-09-28", "423", "Jun Shu"],
  ["CBM", "SinoMed", "2026-09-29", "inception–2026-09-29", "421", "Jun Shu"],
  ["Google Scholar", "NOT SEARCHED — blocked by Google (unusual-traffic page); no results seen", "2026-10-04", "", "0", ""],
  ["Citation searching", "Forward (Ganarin 2021 cited-by): lists viewed in WoS (13) and Scopus (13), not exported or screened; backward: not done", "2026-10-04", "", "0", "Jun Shu"],
  ["Records after deduplication", "Rule-based script (tools/dedup.py; tiers: DOI, title+author+year, similar title, author+year+volume+page, title+volume+pages, Chinese title+year+journal+pages, title+year+journal+volume), 4 October 2026; 4,906 identified, 2,358 duplicates removed; EndNote duplicate finder (default criteria) flagged only known distinct publications by the same authors and bee-keeping patents; looser check done by script", "2026-10-04", "", "2548", ""],
]));

// ---------------------------------------------------------------- Appendix C
ch.push(h1("Appendix C. Data-extraction form and coding rules"));
ch.push(para("One row per patient. Record “NR” when an item is not reported, and note the page, table or figure from which each key item was taken.", { align: AlignmentType.JUSTIFIED }));
const W3 = [1500, 2600, 4500];
ch.push(table(W3, ["Section", "Item", "Coding"], [
  ["A. Report", "Report ID; first author; year; journal", "Free text"],
  ["", "Country; language", "Country; English / Chinese"],
  ["", "Design", "Case report / case series / cohort / letter / review with new patients"],
  ["", "Consecutive series", "Yes / No / Unclear"],
  ["", "Institution and study period", "For duplicate checking"],
  ["", "Linked duplicate reports", "Report IDs"],
  ["B. Patient", "Age at operation", "Years, two decimals (months ÷ 12)"],
  ["", "Sex", "M / F / NR"],
  ["", "Associated conditions", "Gastric volvulus; gastric outlet obstruction; diaphragmatic hernia or eventration; absent or ectopic left kidney; prune belly syndrome; previous abdominal surgery (type); syndrome (e.g. trisomy 21); other"],
  ["", "Aetiology", "Congenital / acquired (state cause)"],
  ["C. Timeline", "Presentation", "Acute / chronic or intermittent / acute on chronic / asymptomatic / mass only"],
  ["", "Index-episode duration", "Days (rules below); verbatim text; intermittent flag; alternative coding (rule 6)"],
  ["", "Total symptom history", "Days (rules below); verbatim text"],
  ["", "Number of earlier episodes", "Integer / NR"],
  ["", "Missed diagnosis", "Yes / No / NR; alternative diagnosis made and at which contact"],
  ["", "Known diagnosis, surgery deferred", "Yes / No / NR; reason (family declined / observation advised / elective operation scheduled / other); waiting interval in days"],
  ["", "Torsion while awaiting surgery", "Yes / No / Not applicable"],
  ["D. Investigations", "Imaging", "US / Doppler US / CT / MRI; whirl sign Yes / No / NR; splenic perfusion normal / reduced / absent / NR"],
  ["", "Preoperative platelet count", "× 10⁹/L / NR"],
  ["E. Operation", "Approach", "Open / laparoscopic / converted"],
  ["", "Torsion at operation", "Yes / No / NR; degrees"],
  ["", "Splenic viability (primary outcome)", "Viable / partially non-viable / non-viable / NR; basis: intraoperative / histology / both"],
  ["", "Procedure", "Detorsion only / splenopexy / partial splenectomy ± splenopexy / total splenectomy / autotransplantation"],
  ["", "Fixation technique", "Mesh / retroperitoneal or extraperitoneal pouch / omental wrap / direct suture / other (specify)"],
  ["", "Spleen size", "Longest dimension, cm"],
  ["", "Reason for removing a viable spleen", "Failure of fixation / surgeon's preference / other / not applicable"],
  ["F. Follow-up", "Length of follow-up", "Months"],
  ["", "Recurrence or re-torsion; further surgery", "Yes / No / NR; details"],
  ["", "Splenic status at last follow-up", "Preserved / partially preserved / lost"],
  ["", "Post-splenectomy complications", "Free text"],
]));
ch.push(h2("Rules for converting reported durations"));
[
  "Hours are converted to days (hours ÷ 24, one decimal).",
  "Weeks × 7; months × 30.4; years × 365.",
  "Ranges take the midpoint (for example, 3–5 days is coded as 4 days).",
  "“Less than 24 hours”, “a few hours” or “overnight” is coded as 0.5 days.",
  "Imprecise terms (“several days”, “some weeks”, “a long history”) are coded as missing on the continuous scale, and assigned a category only if every plausible reading falls in the same category.",
  "Intermittent or worsening presentations (for example, “intermittent pain for one week, worse for two days”): the primary coding uses the whole stated period of the current presentation (7 days); the alternative coding uses the period of worsening (2 days) and is used in sensitivity analysis 4.",
  "A planned interval between discharge and a scheduled elective operation is excluded from the index episode and recorded as the waiting interval.",
  "When dates of symptom onset and of operation are both given, the interval is calculated exactly.",
  "When a report gives symptom duration at admission but not the timing of operation within the admission: an operation described as immediate or emergency adds nothing; an operation on hospital day N adds N days; otherwise the duration at admission is used and flagged as a lower bound.",
].forEach((t, i) => ch.push(para(`${i + 1}. ${t}`, { indent: 360, after: 60, align: AlignmentType.JUSTIFIED })));

const doc = new Document({
  creator: "Wuhan Children's Hospital",
  title: "Systematic review protocol - wandering spleen",
  styles: { default: { document: { run: { font: FONT, size: BODY } } } },
  sections: [{ properties: { page: { margin: { top: 1300, right: 1300, bottom: 1300, left: 1300 } } }, children: ch }],
});
Packer.toBuffer(doc).then((b) => {
  fs.writeFileSync(`${SP}/protocol_raw.docx`, b);
  console.log("written", b.length);
});
