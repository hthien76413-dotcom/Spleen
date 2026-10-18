# PROSPERO amendment — CRD420261520329（协议 v1.5，供舒俊提交）

**修订说明（2026 年 10 月 18 日）。** 2026 年 10 月 7 日和 11 日写的两版（v1.3、v1.4）**都没有提交**。这一版把到 10 月 18 日为止的全部变化合成一次修订：检索、去重、标题摘要筛选的实际做法（含与计划不一致的地方）、全文阶段在取全文之前做出的改动、对分析计划的影响、研究阶段。**只提交这一次。**
文中的每个数字都来自项目日志、`search/` 下的检索导出和 `search/screening/` 下的筛选文件（`rescreen/` 里的汇总文件和 `fulltext_retrieval_summary.txt`）。PROSPERO 的网页读不到（crd.york.ac.uk 在这里被屏蔽），所以各字段的名称和字数限制要在页面上核对，超限就用短版，长版靠上传的 PDF。
**要上传的文件：** 协议 v1.5，由 `Systematic review protocol - PROSPERO draft.docx` 导出 PDF（Word：文件 → 另存为 → PDF）。

## 提交之前，只有团队能决定的几件事

1. **标题摘要阶段的实际做法写不写进登记。** 协议 v1.5 第 14 节如实写了：第二位评审员 10–11 日的第一轮决定是用 AI 编程助手（Codex）做的，违反了书面规则，没有使用；17 日的重筛录入速度（中位间隔 0.45 秒）与逐条阅读后录入不相容，所以不当作第二次独立阅读；最终名单靠仲裁人对所有分歧和部分一致排除记录的盲评。**这和您 10 月 17 日"不写进论文"的决定不是一回事：那条说的是论文，而这里是登记。我的建议是保留：** 登记是公开的、有日期的记录，原计划写的是"两位评审员独立筛选"，如果不说明实际做法，这句话就不再属实；Rayyan 的日志在，期刊或审稿人要求时可以调取。论文的方法部分可以比登记写得短，但不能写成"两位评审员独立阅读了每条记录"。如果您决定不保留，要删的是协议第 14 节的两段（"Title and abstract screening as carried out" 和 "How the list for full-text assessment was made"）以及本说明的第 5 节，并且同时把协议里"两位评审员独立筛选"的句子改成与实际相符的写法，否则登记与事实不符。这是您的决定，我不替您做。
2. **数据共享（邮件草稿里的 O1）。** 协议"传播计划"（第 19 节）我**没有改**，仍是"论文发表时附全部提取的个体患者数据"。但给作者的邮件按保守写法（不以逐例形式公开作者提供的数据）。这两者要统一：若采用保守写法，要在提交前把第 19 节的传播计划和第 14 节相应处改掉，并在方法部分写明。
3. **分析计划的三处改动需要统计分析负责人 Ji Wang 确认**（协议第 16、18 节）：发表年份协变量由三档改为两档（2000–2014、2015 年起）；敏感性分析 7（排除 2000 年以前的报告）因日期规则不再适用；新增一项不在注册里的附加分析（去掉"只写脾扭转、没写脾脏位置"而被纳入的病例）。这是日期规则和 D1 决定的直接后果，不是新的选择，但统计分析由 Ji Wang 负责，应当由 Ji Wang 看过。
4. **提取阶段的两位评审员还没定。** 协议 v1.5 写的是"提取开始前在 PROSPERO 记录里公布"。定了以后要再改一次记录。
5. **更换全文阶段第二评审员的理由。** 协议只写了"团队于 10 月 18 日决定"，没有写理由（您没有给过理由，我不替您编）。PROSPERO 的修订框可能要求写理由；如果要写，请您给一句话。
6. **更新检索。** 协议第 5 节写的是"若距检索超过六个月，在最终分析前重新检索"（约 2027 年 3 月底到期，计划完成日 2027 年 6 月 28 日）。这一版没有改，也没有决定。

---

## 1. Short reason for the change（"brief details of the changes made" 框）

Search strategies were finalised after review by a medical librarian and run on 28–29 September 2026; the as-run searches, deduplication and screening procedure were added. Three planned sources could not be completed (Embase, Google Scholar, citation searching). The title and abstract stage is complete, and the protocol now describes how it was carried out, including where it departed from the plan; the full-text stage is described, with changes decided before any full text was sought (reports published before 2000 are not sought; second full-text reviewer; decision rules). The analysis plan is adjusted accordingly. The review question, the other eligibility criteria, exposures and outcomes are unchanged. The stage of review is updated.

（≈150 words。若框很短：）"Searches run and reported (six databases, 4,906 records); title and abstract screening complete, with departures from the plan described; full-text rules set before any full text was sought, including a date limit (no reports before 2000) and a different second full-text reviewer; analysis plan adjusted for the date limit. Question, other eligibility criteria, exposures and outcomes unchanged."

## 2. Searches（检索字段；与 v1.4 说明相同，没有变化）

Six databases were searched, without language, date or study-design limits:

| Source | Date searched | Records |
|---|---|---|
| MEDLINE via PubMed | 28 Sep 2026 | 1,263 |
| Web of Science Core Collection (institutional licence; SCI-EXPANDED 1997–, SSCI 2000–, A&HCI 2005–, CPCI-S 1998–, CPCI-SSH 2001–, ESCI 2021–, CCR-EXPANDED 1985–, IC 1993–) | 29 Sep 2026 | 750 |
| Scopus (Documents; Preprints and Secondary documents not searched) | 29 Sep 2026 | 1,563 |
| CNKI | 28 Sep 2026 | 486 |
| Wanfang Data | 28 Sep 2026 | 423 |
| China Biology Medicine database (CBM, via SinoMed) | 29 Sep 2026 | 421 |

Total before deduplication: 4,906 records. Duplicates were removed with a documented, rule-based script (2,358 duplicates removed; 2,548 records screened); EndNote's duplicate finder was run on the result as a check and flagged only distinct publications by the same authors and unrelated patents. All searches were run by Jun Shu. Strategies, hit counts and notes are in Appendices A and B of protocol version 1.5. Changes to the strategies since registration were made before any formal search: a medical librarian tested the PubMed strategy; phrases that PubMed silently ignores were replaced by proximity searches; term lists were unified across the English-language databases; thesaurus terms were confirmed; a separate exclusion check was run in CNKI (153 records, none relevant).

## 3. Eligibility criteria（"eligibility" 字段里加一句）

Add to the existing text: "Reports published before 2000 are listed and counted but not sought in full text (added 18 October 2026, before any full text was sought; the reason is feasibility). Reports in languages other than English and Chinese are listed and counted but not extracted (as registered)."

## 4. Deviations from the registered plan（"additional information"）

1. **Embase was not searched.** Embase.com was reachable through the institutional route on 29 September 2026 and the Emtree check was done, but no search was run. On 4 October 2026 the institutional entitlement was no longer recognised and access could not be restored. If a librarian or a colleague with a licence runs the search later, the record will be amended again.
2. **Google Scholar was not searched.** Google returned its unusual-traffic block page and no results were seen.
3. **Citation searching was not completed.** The lists of documents citing Ganarin et al. 2021 were viewed in Web of Science and Scopus on 4 October 2026 (13 documents in each) but were not exported or screened. A limited check of the reference lists of the previous reviews named in the protocol (except Allen and Andrews 1989, which falls under the date limit) is planned for the full-text stage: references are matched automatically against the 2,548 screened records and only unmatched references are read. It has not been done. Whether the reference lists of included reports will be checked has not been decided; the final report will say whether it was done.
4. **Date limit.** Reports published before 2000 are not sought in full text. The registered criteria had no date limit. The reason is feasibility: 296 of the 485 affected records have no abstract, and such reports are expected to be difficult to retrieve. It was decided on 17–18 October 2026, before any full text was sought and before any data were extracted. One of the 45 piloted reports with individual patient data (1998; one child) falls under it. The effect on the results is unknown.
5. **Title and abstract screening was not carried out as planned** (details in section 5 below).
6. **Records assessed in full text beyond the adjudicator's decisions.** 27 records that the adjudicator excluded as "no original patient data" but the second reviewer had advanced are assessed in full text, because a judgement about study design made on an abstract can hide a case series.
7. **Second full-text reviewer.** Full-text assessment is done by Jun Shu and Hongqiang Bian, with Jun Yang as adjudicator, instead of Jun Shu and Fei Peng. The two reviewers for data extraction have not yet been chosen and will be named in the record before extraction starts.
8. **Full-text records kept in a spreadsheet, not in Rayyan.** Each full-text reviewer keeps a separate spreadsheet log and a log of working times; neither sees the other's file until both have finished; each gives the adjudicator the file after the first 50 reports. A calibration on 20 reports (drawn at random, seed 20261018) comes first.
9. **Decision rules for full text** (protocol Section 14): fixed order of exclusion reasons; two Exclude decisions with different reasons are not a disagreement, but Include against Pending IPD is; a full text is declared unobtainable only if both reviewers tried all routes and both failed; a report with the spleen only herniated into the chest or displaced by a mass, without a diagnosis of wandering spleen, is excluded; splenic pedicle torsion in a child without a stated position of the spleen is included and flagged; patients described only as children are taken to be younger than 18 years, those described only as adolescents are not.
10. **Requests for individual data**: sent on one day for all reports with aggregate data only, repeated after four weeks, with a final status at most eight weeks after the first email.

What the omitted sources mean: all 47 English-language reports from the pre-registration pilot were retrieved by the PubMed search (47/47); the Web of Science and Scopus searches retrieved 40/47 and 43/47, and title searches showed that the missing reports are not indexed in those subscriptions. The pilot is a hand-collected sample, not an independent test of sensitivity. The effect of the omitted sources on the reports found has not been tested and will be stated as a limitation.

## 5. Title and abstract screening: what was done（研究选择字段 / protocol Section 14）

The title and abstract stage of the 2,548 deduplicated records was completed on 17 October 2026 in Rayyan (blind mode on until each round was finished; author and journal hidden). Before the formal stage the two reviewers (Jun Shu, Fei Peng) screened a calibration set of 50 records and agreed on 45 (90.0%; Cohen's kappa 0.83); all five disagreements were among the 11 records without an abstract; author and journal details were visible to both reviewers during part of the calibration. A written screening guide, revised after the calibration, applied the registered eligibility criteria without changing them. It departed from the plan in two respects:

(1) **First round, 7–12 October 2026.** The first reviewer recorded decisions one at a time at a median interval of 9.4 seconds. The second reviewer's account recorded about 2,370 of its 2,548 first decisions between 10 and 11 October at a median interval of about 2 seconds, in list order and partly as multi-record actions. The second reviewer reported that an AI coding agent (Codex) had been used to make these decisions, contrary to the written rules. They were not used to decide which records go forward and are kept as a separate dataset.

(2) **Re-screen, 17 October 2026, in a new blind Rayyan project.** The second reviewer was asked to re-screen all records by reading each title and abstract without any AI tool. The log shows decisions received at a median interval of 0.45 seconds (88% within one second; about 2,500 decisions within 76 minutes), which is not compatible with reading each record at the time of entry. The second reviewer reports reading while clicking and using no AI tool; the log can neither confirm nor refute this. The re-screen is therefore not treated as a second independent reading. After the first project was unblinded on 12 October the second reviewer could have seen the first reviewer's decisions; whether this happened has not been established.

**How the full-text list was made.** On 16 October 2026, before any re-screen decision, the team fixed that the first reviewer's 310 Exclude decisions without an exclusion reason would be treated as Maybe in the comparison (as the guide requires); the recorded decisions were not edited. The adjudicator then judged, blind to both reviewers' decisions: all 734 records on which one reviewer excluded and the other did not (248 advanced); 192 records excluded by both and flagged as possibly relevant by a word rule (93) or lacking an abstract (99) (42 advanced); and a random sample of 60 of the other records excluded by both (none advanced). A rule fixed beforehand (more than 10% of the 192, or at least 2 of the 60, advanced) was met, so the adjudicator also judged a further 616 records excluded by both for which either reviewer's reason was "not wandering spleen" or "adults only" (12 advanced); the 184 records excluded by both as "non-human" or "not a formal article" were not re-judged. In total 1,064 records go to full-text assessment (762 advanced by both reviewers; 248 + 54 advanced by the adjudicator) and 1,484 were excluded; with the 27 records of deviation 6 the full-text list has 1,091 records (540 to retrieve, 485 published before 2000, 66 in other languages). The list rests on the reviewers' agreed advances and on the adjudicator's blind judgement of every disagreement and of checks on agreed exclusions, not on two independent readings of every record. The adjudicator is one person and the judgements are not a reference standard. Agreement between the two reviewers will be reported with these caveats. The full screening log is Appendix D of the protocol.

## 6. Review team and roles（团队字段）

Team members are unchanged (Jun Shu, Jun Yang, Hongqiang Bian, Fei Peng, Ji Wang). Roles: title and abstract stage, reviewers Jun Shu and Fei Peng, adjudicator Jun Yang; full-text stage, reviewers Jun Shu and Hongqiang Bian, adjudicator Jun Yang; data extraction, reviewers to be named before extraction starts; statistical analysis, Ji Wang.

## 7. Analysis plan（数据综合字段，三处改动）

(a) The period-of-publication covariate in the primary model has two levels (2000–2014, 2015 onward) instead of three, because reports before 2000 are not sought. (b) Sensitivity analysis 7 ("excluding reports published before 2000") no longer applies. (c) One additional analysis, not in the registered plan and reported as such: omitting patients included on the basis of splenic pedicle torsion without a stated position of the spleen. The primary analysis, the exposures and the outcomes are unchanged. **（提交前请 Ji Wang 确认，见上面第 3 条。）**

## 8. Stage of review（勾选项，截至 2026 年 10 月 18 日）

| Stage | Started | Completed |
|---|---|---|
| Preliminary searches | Yes | Yes |
| Piloting of the study selection process (title and abstract stage: calibration on 50 records) | Yes | Yes |
| Formal screening of search results against eligibility criteria | Yes | No |
| Data extraction | No | No |
| Risk of bias (quality) assessment | No | No |
| Data analysis | No | No |

标题摘要阶段已完成，全文阶段尚未开始（20 篇校准已准备、尚未做），所以"正式筛选"勾 Started / Not completed。提交那天如果有别的阶段已经开始，按实际勾。

## 9. 没有改变的

综述问题、主要暴露（索引发作的症状持续时间）、次要暴露、主要结局、提取表、偏倚风险方法、合成方法（除第 7 节三处）、传播计划（见上面第 2 条，待决定）、时间表（开始 2026 年 9 月 28 日，计划完成 2027 年 6 月 28 日）。

## 10. 舒俊在网站上的步骤

资料来源：2026 年 10 月 7 日网络检索到的第三方说明和 PROSPERO 自己的指引 PDF（网站本身没有读到）：登录 → My PROSPERO records → 打开已保存的记录 → 修改 → Submit → 填写修改内容简述；每一次修改都有日期，并显示在公开的变更记录里。这条路径对"检索方法"的改动会不会让您在"minor amendment / major revision"之间选，没有核实，按页面提示走。

- [ ] 用拥有 CRD420261520329 的账号登录（舒俊，关联 ORCID）。
- [ ] 打开记录 → 编辑。
- [ ] 检索字段用第 2 节；eligibility 字段加第 3 节的句子；additional information 用第 4 节；研究选择字段用第 5 节；团队角色用第 6 节；数据综合字段用第 7 节；阶段勾选用第 8 节。上传 v1.5 的 PDF，替换旧的。
- [ ] 不要改研究问题、主要暴露、主要结局和日期。
- [ ] 把第 1 节贴进修订原因框，提交。
- [ ] 如果 PROSPERO 给其他团队成员发审批邮件，请他们点链接。
- [ ] 保留提交页面和版本历史的截图，发给 Claude，更新日志和方法部分（例如"amended on [日期]"）。
