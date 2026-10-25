# 提取阶段 10 篇校准：讨论与裁定结果（2026-10-25）

来源：作者 2026 年 10 月 25 日转来的 `discussion_detail_2026-10-25_adjudicated.csv`（讨论清单第 1–8 点的 332 行明细，`discussion_conclusion`、`adjudicator_ruling`、`final_reading` 三列已由两位提取员和杨俊填写）。
这里只记录文件里的内容。Claude 没有打开这些报告的原文，没有核对任何一条裁定是否符合原文。原始明细表（含逐例的 E1/E2 值、出处和备注）在作者和杨俊手里；仓库里的 `discussion_detail_2026-10-25.csv` 是裁定之前的版本。

| 点 | 通用读法（`discussion_conclusion`，原文） | 登记为 | 裁定后的最终值（`final_reading`，从明细表读出） |
|---|---|---|---|
| 1 | 仅采纳作者对术中脾状态的直接描述；不由术式或影像反推。 | X13 | `viability`、`viab_basis` 为 NR：WS0551_P1、WS0668_P1–P4 和 P6、WS1859_P1、P3–P14、P16（共 20 名）。WS1880_P1：Partially non-viable，`viab_basis` = Intraoperative。`procedure`：WS1859_P12 Detorsion only、WS1859_P13 Autotransplantation、WS1859_P16 No operation（`torsion_at_op` No）。WS0551_P1 的 `torsion_at_op` 为 NR |
| 2 | 未提及填 NR；只有原文明确否定时才填 No。 | X14 | 原来填 No 而原文未提的项目全部改为 NR（伴随疾病各项、`known_dx_deferred`、`missed_dx`、`recurrence`、`further_surgery`）。保留 Yes：`cond_gv` WS1859_P4、P19；`cond_panc_tail` WS0668_P4、WS1859_P1、P8；`known_dx_deferred` WS1367_P2；`missed_dx` WS0668_P4–P7 |
| 3 | 不把指数发作时长或未说明的既往发作自动写成总病程或 0。 | X15 | `total_hist_days` 全部 NR；`n_earlier_episodes` 除 WS0668_P4 = 1、P5 = 1、P6 = 2 外全部 NR |
| 4 | 仅有至就诊或入院前时长、未给手术时间时，标为下限。 | X16 | `idx_dur_lower_bound` = Yes：WS0159_P1–P3、WS0732_P1、WS1859_P1–P16（20 名） |
| 5 | 按原文可确定的症状起点和手术日期提取；不精确时仅记录时长类别。 | X17 | WS0551_P1 = 8 天；WS1903_P1 = 4 天；WS1367_P2：天数 NR，`idx_dur_cat_imprecise` = >30 d |
| 6 | 影像和术中证据按文中可对应信息逐例判定；影像汇总仅在范围可完全对应时适用。 | X18 | `img_us`：WS0159_P3 NR；WS1859_P1–P15、P18、P19 Yes。`ws_basis`：WS0159_P2、P3 Imaging shows；WS0668_P1、P5–P7 Imaging and operation；WS0732_P1 Operation shows；WS1859_P1–P16 Imaging and operation，P18、P19 Imaging shows |
| 7 | 无游走脾诊断或脾蒂活动／扭转描述的个案不进入 Patients 表。 | X19 | WS1859_P17 不进 Patients 表；`n_children_individual` = 18；报告层 notes 记录不符合条件 |
| 8 | 无法一一对应的可能重复仅在报告层说明，不填写 `same_patient_as`。 | X20 | WS0668：`linked_duplicates` = WS0741；`same_patient_as` 留空；可能重叠写在报告层 notes |

第 9 点（只有一位提取员填的项目）和第 10 点（其余单项差异）不在这份明细表里，没有裁定结果。

## Claude 注意到、需要团队看的几处（不是裁定结果）

1. **WS1859_P16：** 裁定是 `procedure` = No operation、`viability`/`viab_basis` = NR。提取说明原来对未手术的儿童写的是 Not applicable。差别在于明细表备注里这名儿童开过腹（胃造瘘时发现脾已自行复位），只是脾上没有手术。说明 7.1 加了一行按裁定写，标【Claude 的读法，待确认】。
2. **X13 的后果：** 20 名儿童的活力裁定为 NR（WS1859 占 14 名）。这些儿童在主要结局里是 NR，做了脾切除的会得到“NR - removed, check reason”。协议没有规定结局缺失怎么处理；是否另做一个“脾切除即无活力”的补充分析（那是推断，不是注册的分析）由 Ji Wang 和作者决定。
3. **X20 的后果：** WS0668 和 WS0741 的可能重叠不填 `same_patient_as`，两篇的儿童在分析里会各占一行，最多 5 名可能重复计算。需要 Ji Wang 在核查重复患者时决定怎么处理（例如各去掉其中一篇做敏感性分析）。
4. **X19 的后果：** WS1859 进入 Patients 表的儿童数是 18，不是全文阶段登记的 19；全文筛选记录里这篇的 `n_children_individual` 是按表格行数填的，提取后以 Patients 表为准。
5. **WS0668 和 WS0741 的重叠**是 E1 在备注里写的（“5 例此前已报告，很可能是 WS0741”），E2 没有记录；备注里还写了摘要和讨论对梗死例数的说法不一致（3 例对 4 例），这一点没有裁定。
