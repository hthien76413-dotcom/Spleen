# 提取校准（10 篇）：分歧讨论清单
两位提取员和仲裁人对着原文逐条定的清单

<!-- kv; widths: 17,83 -->
| 版本 | 提取校准讨论清单 v2026-10-25a（草稿） |
| 依据 | 2026 年 10 月 25 日对 `extraction_E1.xlsx` 和 `extraction_E2.xlsx` 的比对（`search/extraction/calibration/compare_results/`）。作者转告杨俊已拿到两份文件。 |
| 参加 | 舒俊（E1）、卞红强（E2）、杨俊（仲裁） |
| 怎么用 | 每一条先看“现状”，打开列出的原文页，两人对着原文讨论；谈不拢的交杨俊。结论写在文末表格的最后一栏，再由 Claude 写进提取说明第 12 节。**讨论前不要改原始的两份文件**，要改的在共识时一起改。 |
| 不在这里判断的事 | 谁对谁错要看原文，Claude 打不开这 10 篇论文，所以清单只列事实和要问的问题。 |
| 逐例明细 | `search/extraction/calibration/compare_results/discussion_detail_2026-10-25.csv`：每条涉及的患儿一行，带两人的值、出处和备注，末尾三栏留给讨论结论、杨俊裁决和最终读法 |

:::tip 先看这三点
- 差异集中在 **WS1859**（一张 19 行的表，381 处差异里占 226 处）和 **WS0668**（64 处）。这两篇读清楚，大半分歧就解决了。
- 有些是**约定问题**（没提到填 No 还是 NR、什么算下限），要定一条规则；有些是**漏提或读错**（一方有阳性、另一方没有），逐例对原文改。两类分开谈。
- 两份文件都没在讨论前改动；完成度不同的字段（见第 9 条）要先补齐。
:::

## 1. 活力（viability）：只有术中描述、或没有“活力”一词时怎么填
- **现状：** 21 例活力不同。其中 18 例你（E1）填 NR：WS0668 P1-4,6；WS1859 P1,3-14；卞红强填 Non-viable 14 例（WS1859 13 例、WS0668 1 例）、Viable 4 例（WS0668）。另 3 例是别的分歧：WS0551 P1；WS1859 P16；WS1880 P1（WS0551_P1：Partially non-viable / Viable；WS1859_P16：Not applicable / Viable；WS1880_P1：Partially non-viable / Non-viable）。`viab_basis` 也不同：E1 NR、E2 Intraoperative 共 15 例。
- **要看的原文：** WS1859 的表 1 和第 2.4–2.5 节（p.371–372，E1 写的出处；E2 写“Table 1”）；WS0668 全文（E1 写 p.434–436，E2 写 p2-5，页码写法不同，请对着印刷页码）。WS0668 的 E1 备注：摘要写 3 例梗死，讨论写 4 例扭转并梗死，文章自己前后不一致，需要定以哪处为准。WS0551_P1 的 E1 备注写明：作者没有说开腹时脾的活力，是按影像上的梗死填的（脾保留）；所以问题不只是“从术式反推”，也包括“用影像上的梗死代替术中判断”。
- **指南现在：** 第 7 节：如实记录作者对脾脏活力的判断；全脾切除但没写活力 = NR，先回原文再读一遍，真的没有就留 NR。没写的是：①只有术中描述（坏死、梗死、紫黑色）、没有“活力”一词时，算不算作者的判断；②能不能从术式（脾固定、全脾切除）或影像（梗死）反推活力。
- **要问的：** 每例原文里有没有直接描述术中脾的状态？有，写进 `viability`，`viab_basis` = Intraoperative，`src_outcome` 写页码；没有，按指南留 NR。

## 2. “没提”填 No 还是 NR；一方有阳性、另一方没有
- **2a 约定：** 指南 2.3、5.2、5.4 写的是明确写了没有 = No，没提 = NR。你的文件里下面几项在原文没提的患儿上填了 No，卞红强填 NR：`cond_gv` 15、`cond_panc_tail` 16、`cond_dh` 18、`known_dx_deferred` 34、`missed_dx` 8（E1 No、E2 NR 的例数）。`known_dx_deferred` 和 `recurrence`、`further_surgery` 指南没有写 No/NR 的规则（只定义了 Yes）：`known_dx_deferred` 你填 No、他填 NR（35 例，10 篇都有）；`recurrence` 18 例（E1 NR/E2 No 16，E1 No/E2 NR 2）、`further_surgery` 16 例（E1 NR/E2 No）。
- **2b 逐例看原文：** 一方记了阳性（Yes）、另一方是 NR，共 10 例，这不是约定问题，是有一方漏提取或没读到：`cond_gv` 2 例（WS1859 P4,19）；`cond_panc_tail` 3 例（WS0668 P4；WS1859 P1,8）；`known_dx_deferred` 1 例（WS1367 P2）；`missed_dx` 4 例（WS0668 P4-7）。
- **要问的：** ①指南补一条：没提 = NR；`known_dx_deferred`、`recurrence`、`further_surgery` 的 No 什么时候可以填（例如随访明确写了无复发）。②2b 的每一例回原文，改对的那一方的值，不对的那一方改正。

## 3. 总病程和此前发作次数
- **现状：** `total_hist_days` 不同 30 例（WS1859 17 例），`n_earlier_episodes` 不同 15 例（WS0668 6 例），都是你给了数字、卞红强填 NR；你的 `n_earlier_episodes` 多是 0。
- **指南现在：** 第 5.4 节：总病程从第一次归因于游走脾的症状算起，没写填 NR；`n_earlier_episodes` 只写“反复发作”没有次数填 NR。没写：原文只描述了这一次发作、没说此前有没有发作时，是 0 还是 NR；总病程是否等于指数发作时长。
- **要问的：** 原文没提早期发作时，两个字段填 NR 还是 0 / 等于指数时长？定一条规则。逐例明细里有两人的 `total_hist_verbatim`。

## 4. 什么时候标“下限”（`idx_dur_lower_bound`，规则 9）
- **现状：** 20 例你填 Yes、卞红强填 No（WS1859 16 例、WS0159 3 例、WS0732 1 例）。
- **指南现在：** 第 5.4 节：用入院时的持续时间并作为下限填 Yes；第 6 节例子互相矛盾：“腹痛 3 天后入院，手术（没有写什么时候做）”标下限；“腹痛 14 小时，入院后即刻手术，没写具体时间”不标。
- **要问的：** 表里只有入院前时长、没有手术时间的，是不是都标 Yes？“即刻手术”“当天手术”这类算有手术时间吗？

## 5. 三例主要暴露（时长）的分歧
- **WS0551_P1：** 原文“palpable left abdominal mass at 1 day of life; laparotomy at day 9”（p.302–303）。E1 填 8 天，E2 填 NR。
- **WS1903_P1：** 原文“腹痛伴发热4 d”（p.239）。E1 填 4 天，E2 填 NR（E2 写的出处 p1-2）。
- **WS1367_P2：** 原文“persistent abdominal pain until elective splenectomy”（E1 写 p.3，E2 写 p2-3）。两人天数都是 NR；E1 按规则 5 另填了类别 >30 d，E2 没填类别（`idx_dur_cat_imprecise` 空）。
- **要问的：** 新生儿“出生时发现包块、第 9 天手术”算 8 天还是 NR？“腹痛伴发热 4 d”的 4 天是腹痛的时长吗？WS1367_P2 原文哪里能支持 >30 d？

## 6. WS1859 的影像和 `ws_basis`
- **现状：** `img_us`：你填 NR、卞红强填 Yes 共 18 例（WS1859 17 例，WS0159 1 例）；`ws_basis` 不同 25 例（WS1859 18、WS0668 4、WS0159 2、WS0732 1）：你多填 Operation shows…（16 例）或 Imaging shows…（8 例），他填 Imaging and operation；1 例他填 Torsion only。
- **指南现在：** 提取说明 5.2 和全文指南 6.7：影像和术中所见都写明脾异位或活动时才选 Imaging and operation；一句“术中所见与超声诊断一致”也算术中证据。
- **要问的：** 读一遍 WS1859 表 1 里关于影像和术中所见的列，再决定 `img_us`、`img_ct` 和 `ws_basis`；两人各自补全 `img_*`。WS0668、WS0159、WS0732 的 `ws_basis` 同样逐例对。

## 7. WS1859_P17：要不要提取
- **现状：** 只有 E1 有这一行（E1 报告 19 例，E2 18 例，`n_children_individual` 也是 19 对 18）。E1 备注：脾疝入胸腔，合并膈疝或膈膨升、胃绞窄破裂，作者把它算在 19 例脾扭转里；术中没有描述脾的位置或蒂扭转；已死亡（手术后撤除治疗）；“按作者报告纳入，共识时再核资格”。
- **指南现在：** 全文指南：脾只是疝入胸腔、作者没有诊断游走脾也没有描述蒂活动的，排除（E2）；作者诊断游走脾并膈疝的，纳入。提取说明 3 节没有给“同一系列里个别患儿不符合”的写法。
- **要问的：** P17 按这条规则提取还是不提取？不提取的话 E1 的 `n_children_individual` 改成 18，P17 的行怎么留痕（建议在 notes 记一句，不进 Patients 表）。

## 8. WS0668 和 WS0741 可能是同一批患儿
- **现状：** E1 在 WS0668 的 `linked_duplicates` 填了 WS0741，备注：7 例里 5 例此前已报告（可能是 Steinberg 2002，即 WS0741，原文里的参考文献编号不清楚），不知道是哪 5 例，所以 `same_patient_as` 留空。E2 没记。WS0741 也在纳入名单里，5 例。
- **指南现在：** 提取说明 5.1：重复时两篇都录，较不完整的那行在 `same_patient_as` 填较完整那篇的 patient_id；拿不准就不填，notes 写“可能与 WSxxxx_Pn 是同一人”，共识时再定。Ji Wang 在共识前核查重复患者。
- **要问的：** 原文能不能认出是哪几例？认不出时，分析里怎么算人数（这 7 例里最多 5 例与 WS0741 重复）？请 Ji Wang 一起看。

## 9. 有一方还没填的字段（不算分歧，但共识前要补）
- 卞红强没填：`post_splenectomy_compl` 35 例（全部）、`cond_other` 26 例、`procedure_other` 7 例、`missed_dx_alt` 和 `missed_dx_contact` 各 4 例、`fixation_other`、`idx_dur_cat_imprecise`、`recurrence_details` 各 1 例。
- 舒俊没填：`waiting_interval_days` 34 例（卞红强填 NR）。
- 补填前请先按各自的原文，不要抄对方的。

## 10. 其余的单项差异：对着原文逐条改
- 除上面各条外还有 100 处单项差异，最多的是：`torsion_degrees` 17 例（15 例在 WS1859，E1 有度数、E2 NR）、`cond_other` 9、`presentation` 8、`perfusion` 7、`status_last_fu` 6、`followup_months` 5、`approach` 4、`torsion_at_op` 4、`spleen_size_cm` 4、`age_years` 3、`procedure` 3。全部在 `ex_field_differences.csv`。
- 这些多半对着原文就能定，不需要新规则；遇到新的约定问题再加进来。

## 决定表（讨论后填写）
<!-- widths: 6,40,28,26 -->
| 编号 | 要决定的一句话 | 讨论结论 | 杨俊裁决（谈不拢才填） |
|---|---|---|---|
| 1 | 只有术中描述、没有“活力”一词时 `viability` 怎么填；能否从术式反推 |  |  |
| 2a | 没提到时填 No 还是 NR（含 `known_dx_deferred`、`recurrence`、`further_surgery`） |  |  |
| 2b | 一方有阳性、另一方 NR 的逐例改正 |  |  |
| 3 | 原文没提早期发作时 `n_earlier_episodes`、`total_hist_days` 填什么 |  |  |
| 4 | `idx_dur_lower_bound` 什么时候填 Yes |  |  |
| 5 | WS0551_P1、WS1903_P1、WS1367_P2 的时长 |  |  |
| 6 | WS1859 的影像、`ws_basis`；WS0668、WS0159、WS0732 的 `ws_basis` |  |  |
| 7 | WS1859_P17 提取与否，`n_children_individual` |  |  |
| 8 | WS0668 与 WS0741 的重复患儿怎么记、怎么数 |  |  |
| 9 | 补填字段的负责人和时间 |  |  |
| 10 | 其余单项差异改完 |  |  |

## 没有验证的
- 以上内容来自两份文件和比对输出，没有对照任何一篇原文；谁对谁错必须由你们对着论文定。出处页码是各自填的原话，E1 与 E2 的页码写法不一致（印刷页 / 文件页）。
- 这份清单的 Word 版本没有在 Word 里打开看过版面。
