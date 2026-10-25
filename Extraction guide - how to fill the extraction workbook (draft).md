# 儿童游走脾系统综述：数据提取操作说明
怎么填提取工作簿：规则、例子和要在校准时统一的读法

<!-- kv; widths: 17,83 -->
| 版本 | 提取操作说明 v2026-10-25c（草稿）。标 **【Claude 的读法】** 和 **【待校准】** 的内容要两位提取员和仲裁人确认后才算生效 |
| 改动（2026-10-19，分层） | 10 篇校准的分层要求（中文 3、系列 3、时间写法四种各 1、只写“脾扭转”1、未手术 1）作者 2026 年 10 月 19 日确认，抽样等全文名单出来后再做。规则没有变 |
| 改动（2026-10-19，状态） | 10 篇校准里两条选择，舒俊（E1）和卞红强（E2）都同意（作者 2026 年 10 月 19 日转告）：预试验的 53 篇不进；靠邮件拿到个体数据的报告不进，只从已发表个体数据的 Include 里抽。规则没有变 |
| 改动（2026-10-19，抽样规则） | 第 10 节第 1 步：10 篇校准的抽样规则和种子（20261019）先定下来，写成脚本 `tools/draw_extraction_calibration.py`；名单（`fulltext_included.csv`）要等全文阶段结束，所以**现在还不能抽**。其他规则没有变 |
| 改动（2026-10-25，presentation 加 NR） | 10 篇校准的两份返回文件做格式检查时，`presentation` 列没有 `NR` 选项，E2 在一篇报告里填了 `NR`（7 行报错）。作者 2026 年 10 月 25 日同意给 `presentation` 加一个值 `NR`：报告没有写发作形式时填 `NR`，不要在五个值里硬选（5.3 表、X11）。模板升到 v2026-10-25a。这是工作簿的填写约定，不改任何纳入标准或变量定义；协议附录 C 列的是五个值，`NR` 与其他列的 `NR` 一样是补充值。杨俊和卞红强是否知道这一条没有说明。 |
| 改动（2026-10-25，起始表） | 10 篇校准有现成的起始表：`extraction_E1_calibration_starter.xlsx`、`extraction_E2_calibration_starter.xlsx`（`search/extraction/calibration/`，生成脚本 `tools/make_calibration_starters.py`）。表里只预填了 10 个 WS 编号和提取员代码，另有一张 Calibration_list（编号、标题、DOI、链接）；Patients 表是空的。只是省去手工填编号，规则没有变 |
| 改动（2026-10-25，已抽样） | 全文名单已确定（269 篇纳入，`fulltext_finalize` 2026 年 10 月 25 日的结果），10 篇校准按第 10 节第 1 步抽出，种子 20261019，结果在 `search/extraction/calibration/`。名单里中文 3、系列 3 达到要求；“范围”类时间写法按摘要关键词一篇也没有找到，没有硬凑（见第 10 节）。规则没有变 |
| 改动（2026-10-19，校准之后） | 全文阶段 20 篇校准讨论后（作者转告）：`ws_basis` 的 `Imaging and operation` 只在影像和术中所见都写明脾异位或活动时才选（5.2 表）；逐例资料在线上附录里的报告，附录也要取到（2.2 清单）。没有改别的规则 |
| 改动（2026-10-19） | 提取阶段**不保存时间记录**：作者 2026 年 10 月 19 日决定删除提取工作簿里的 EX_time_log 表（提取尚未开始）。理由作者没有说明，文件里不写理由。协议 v1.6 对提取阶段没有时间记录的规定，所以协议不用改；脚本 `compare_extraction.py` 也不再检查用时。本说明里提到时间记录的四处（目录里第 2 章的说明、第 1 节第 4 步及随后的步骤编号、2.2 清单、第 10 节）已删或改，版本号随之更新，其余内容没有变 |
| 项目 | 儿童游走脾系统综述（含个体患者数据）和单中心病例系列；PROSPERO CRD420261520329；协议 v1.5 |
| 适用对象 | 舒俊（提取员 E1）、卞红强（提取员 E2）、杨俊（分歧仲裁）。Ji Wang 核查两份提取表，不提取。分工是作者 2026 年 10 月 18 日决定的；作者转告卞红强和杨俊已知道并同意（方式和日期没有说明） |
| 配套文件 | 协议 v1.5 附录 C（提取表和 9 条时间换算规则）；《提取工作簿》v2026-10-25a；比对脚本 `tools/compare_extraction.py` |
| 要提取的报告 | 全文阶段两位筛选员确认纳入的报告（名单由 `tools/finalize_fulltext.py` 生成，`fulltext_included.csv`）。2026 年 10 月 25 日 finalize 的结果是 269 篇（待 IPD 的 5 篇不在内） |
| 例子 | 本说明里所有的"例"都是**虚构的**，只用来说明规则，不是任何真实报告或患者，请不要拿它们去对照真实的报告 |

:::tip 怎么用这份说明
- 协议附录 C 告诉你"填什么"；这份说明告诉你"怎么填、遇到这种写法怎么办"。协议原文用 **【协议】** 标出；协议没有规定、由 Claude 补的读法用 **【Claude 的读法】** 标出；校准时要拿具体报告验证的用 **【待校准】** 标出。
- 两者冲突时以协议为准。说明和协议都没有答案的，按"最接近的规则 + 在 notes 里写明"处理，不要自己发明规则，也不要为了让格子不空而随便填。
- 第 12 节把所有"要统一的读法"列成清单。
:::

## 内容一览

<!-- widths: 9,63,28 -->
| 章 | 内容 | 谁需要读 |
|---|---|---|
| 1 | 整个提取怎么走（一页纸） | 所有人 |
| 2 | 开始前：文件、副本、不能看什么 | 舒俊、卞红强 |
| 3 | 哪些患者要提取，哪些不提取 | 舒俊、卞红强 |
| 4 | Reports 表：一份报告填什么 | 舒俊、卞红强 |
| 5 | Patients 表：逐项说明 | 舒俊、卞红强 |
| 6 | 时间换算：9 条规则和虚构的例子 | 舒俊、卞红强、杨俊 |
| 7 | 主要结局：脾脏活力和术式 | 舒俊、卞红强、杨俊 |
| 8 | 中文报告 | 舒俊、卞红强 |
| 9 | 疑难情形速查 | 所有人 |
| 10 | 校准：先做 10 篇 | 所有人 |
| 11 | 保存前自查；两人完成后做什么 | 所有人；杨俊重点看 11.2 |
| 12 | 要在校准时统一的读法（清单） | 所有人 |
| 13 | 没有核实的 | 所有人 |

\pagebreak

## 1. 整个提取怎么走（一页纸）

1. **名单：** 全文阶段结束后，`fulltext_included.csv` 里的每一篇报告都要提取。只有汇总数据的报告（Pending IPD）等收到个体数据后再提取。
2. **各用自己的副本：** 舒俊用 `extraction_E1.xlsx`，卞红强用 `extraction_E2.xlsx`。**做完之前不看对方的文件，也不讨论具体的报告。**
3. **先读完整篇，再填表：** 先在 Reports 表填这篇报告的一行，再在 Patients 表给每名符合条件的儿童填一行。
4. **先校准：** 两人先各自提取同样的 10 篇（第 10 节），比对，讨论分歧，必要时修改这份说明和提取表，然后才开始正式提取。
5. **正式提取：** 每名儿童都由两人独立提取。做完校准和大约 30 篇时，各自运行一次 `check` 检查自己的文件（只看自己的，安全）。
6. **两人都做完：** 运行 `compare`，得到分歧清单；两人先讨论，讨论不了的交杨俊；结果写进共识文件 `extraction_consensus.xlsx`。
7. **Ji Wang** 核查两份提取表：超范围的值、单位错误、重复患者（协议 v1.5）。时间点（共识之前）和"不改数据"是 Claude 的读法。

## 2. 开始前

### 2.1 文件

<!-- widths: 30,70 -->
| 文件 | 说明 |
|---|---|
| `extraction_E1.xlsx` / `extraction_E2.xlsx` | 各人自己的提取表，从模板 `Extraction workbook - template (draft).xlsx` 另存（做 10 篇校准时，从起始表 `extraction_E?_calibration_starter.xlsx` 另存也可以，结构相同）。**不要改表头的前三行和 Lists 表** |
| 带日期的副本 | 每次用完另存一份，如 `extraction_E2_2026-12-05.xlsx`，不覆盖旧的 |
| 全文 PDF | 按 WS 编号命名（WS0123.pdf），放在自己的电脑或单位网盘。**PDF 和提取表都不放进仓库**。**【Claude 的读法，仿全文阶段】** 每人完成校准后把自己的文件交杨俊保管；Claude 核对格式时只看汇总 |
| `extraction_consensus.xlsx` | 共识文件，两人都做完并讨论后才建 |

### 2.2 清单

- [ ] 用的是**自己的**那一份提取表，表里 Reports 和 Patients 的 `extractor` 列填 E1（舒俊）或 E2（卞红强）。
- [ ] 没有打开对方的文件，也没有看预试验的提取表（`literature-pilot-extraction-53-papers.csv`）。
- [ ] 每次开始前确认手边的是**全文**（不是摘要页），并且是名单上的那一篇。
- [ ] 逐例资料在线上附录或补充材料里的报告（全文阶段 6.5 已判 Include 的），**附录也要在手边**，没有附录不要凭正文猜；附录取不到的，记下 WS 编号告诉杨俊。

:::warn 为什么不看预试验表
协议 v1.5 写明：舒俊做过预试验的提取，主要暴露是从那批结果得来的，所以提取不是对假设"盲"的。唯一的缓解办法是两人独立做，并且正式提取时不参照预试验表。预试验里的报告在正式提取中照样重新提取。
:::

### 2.3 空白和 NR 的区别

- **空白 = 还没提取。** **NR = 报告里没有这项信息。** 不要用空白表示"报告没写"。比对脚本把"一边空白"算成"还没做完"，不算分歧。
- 报告里有这项信息，你却填 NR，是错误；报告里没有，你却猜一个值，也是错误。
- 灰色列是公式，不要改。

## 3. 哪些患者要提取，哪些不提取

<!-- widths: 40,60 -->
| 情形 | 怎么办 |
|---|---|
| 报告里每名儿童都有个体描述（病例描述或一人一行的表） | 每人一行，进 Patients 表 |
| 系列里只有一部分儿童有个体描述，其余只有总数或均数 | 有个体描述的每人一行；其余的人数填 Reports 表 `n_children_aggregate`，并去 IPD_requests 表登记 |
| 只有汇总数据（"12 例，平均 7.2 岁，3 例脾切除"） | 不进 Patients 表；人数填 `n_children_aggregate`；全文阶段应已记 Pending IPD |
| 系列里混有 18 岁及以上的患者 | 成人**不提取**；儿童照常提取。按作者原来的编号保留儿童的编号（见 5.1），不重新编号 |
| 年龄只写"child / 小儿 / 患儿"，没有具体年龄 | 视为小于 18 岁，提取；`age_years` 填 NR，原文写法填 `age_verbatim`（全文指南 D2）。只写"adolescent / 青少年"、没有年龄的不能确认小于 18 岁，不提取 |
| 年龄没写，也没有任何儿童的说法 | 不能确认小于 18 岁，不提取（协议第 7 节）；在 notes 里写明 |
| 综述里有新患者 | 只提取作者自己的新患者；综述表格里别人的病例**不提取**（全文指南 D8） |
| 同一患者在两篇报告里 | 两篇都录一行，较不完整的那一行在 `same_patient_as` 里填较完整那篇里的 patient_id；协议规定用最完整的一篇、其余链接到它（见 5.1） |
| 没有手术的儿童 | 提取（描述性汇总用）：`procedure` = No operation，`viability`、`viab_basis`、`approach` = Not applicable。年龄填诊断时的年龄 |
| 本机构 5 例 | `report_id` = OWN，patient_id = OWN_P1–OWN_P5；先在 Reports 表加一行 OWN。**只录不可识别的信息，不写姓名、住院号、出生日期、具体日期**。已有一份由稿件预填的草稿 `Extraction draft - own series OWN (from manuscript, not chart-checked).xlsx`（生成脚本 `tools/make_own_series_draft.py`）：它**不是**独立提取，只用于两人从病历提取并做完共识**之后**的比对。**作者 2026 年 10 月 18 日决定：两位提取员先从病历独立提取**，用空白起始文件 `search/extraction/own_series/extraction_E1_OWN_starter.xlsx` 和 `…E2_OWN_starter.xlsx`；开始前不看草稿（若改为从草稿出发核对，这 5 例就不是独立双人提取，要在 Methods 里说明）。核对清单在草稿文件的 Chart_check 表 |

## 4. Reports 表：一份报告一行

<!-- widths: 24,76 -->
| 列 | 怎么填 |
|---|---|
| `report_id` | 检索结果里的 WS 编号（如 WS0123）；本机构为 OWN |
| `first_author`、`year`、`journal` | 照全文首页抄；中文报告可以写中文姓名。不要缩写 |
| `country` | 患者就诊的机构所在国家。**【Claude 的读法】** 协议只写了 Country，没说是作者所在国还是患者就诊国；两者一般相同，不同时以就诊机构为准，并在 notes 里写明 |
| `language` | English 或 Chinese |
| `design` | Case report / Case series / Cohort / Letter / Review with new patients。给编辑的信里有患者的，选 Letter |
| `consecutive` | 系列报告是否连续纳入：Yes / No / Unclear。作者没说、只说"我院收治的"为 Unclear；单个病例报告填 Unclear（**【Claude 的读法】**，协议没有为单个病例单列一项）|
| `institution`、`study_period` | 用来核对重复报告。照原文写，不要估计；没写就写 NR |
| `linked_duplicates` | 同一患者的其他报告的 WS 编号 |
| `n_children_individual` | 这篇报告里你在 Patients 表中录了几行（应当等于 Patients 表里该 report_id 的行数，`check` 会核对） |
| `n_children_aggregate` | 只有汇总数据的儿童人数；大于 0 时去 IPD_requests 表登记 |
| `extractor`、`date_extracted` | E1 或 E2；提取日期（这一列是提取日期，不是发病或手术日期） |
| `notes` | 任何要在共识里讨论的问题 |

## 5. Patients 表：逐项说明

### 5.1 编号和重复

- **`patient_id` = 报告编号_P序号**，如 WS0123_P1。**【Claude 的读法，为了让两人的患者能对上】** 作者自己给了病例编号（Case 3、第 12 例）就用作者的号（P3、P12）；没有编号就按报告里出现的先后，从 P1 开始。成人或不符合条件的患者不提取，但**不要因此重新编号**：系列里第 1、3、7 例是符合条件的儿童，就记 P1、P3、P7。这样两个人的 patient_id 才对得上；对不上时比对脚本会显示为"只在一份文件里"，要靠讨论解决。
- **`same_patient_as`：** 与另一篇报告重复时，较完整那篇里的 patient_id；否则留空。判断重复要看机构、研究时期、年龄、性别、临床细节（协议第 14 节）。拿不准就不填，在 notes 里写"可能与 WSxxxx_Pn 是同一人"，共识时再定。
- 已知要核对的：邱江涛 2008 年的两篇（四川医学、宁夏医学杂志），Fakler 2004 年的两篇（两本德文杂志）。

### 5.2 年龄、性别、伴随疾病、病因

<!-- widths: 24,76 -->
| 列 | 怎么填 |
|---|---|
| `age_years` | **手术时的年龄**（未手术的填诊断时的年龄），岁，保留两位小数。月数 ÷ 12：8 个月 = 0.67；2 岁 3 个月 = 2.25。**【Claude 的读法】** 按天写的（如新生儿 13 天）÷ 365：13 天 = 0.04。没有写年龄填 NR。≥ 18 岁的不应出现 |
| `age_verbatim` | 原文写法，如 "8 months"、"患儿"。与 `age_years` 一起，校准时可看出换算有没有错 |
| `sex` | M / F / NR |
| `cond_gv`、`cond_goo` | 胃扭转、胃出口梗阻。作者明确写了为 Yes；明确写了没有为 No；没提为 NR |
| `cond_panc_tail`、`cond_bowel_obs` | 胰尾扭转、肠梗阻（协议第 13 节的附加结局） |
| `cond_dh` | 膈疝或膈膨升 |
| `cond_kidney` | 左肾缺如或异位 |
| `cond_prune` | 梅干腹综合征 |
| `cond_prev_surg`、`prev_surg_type` | 以前做过腹部手术，类型写在后一列，如 fundoplication |
| `cond_syndrome` | 写综合征名称（如 trisomy 21）；明确无综合征填 None；没提填 NR |
| `cond_other` | 其他伴随疾病，自由文本 |
| `aetiology`、`aetiology_cause` | Congenital / Acquired / NR。**获得性**（如胃底折叠术后、肾切除后）要写明原因。**作者没有说明先天还是获得性的填 NR，不要默认先天** |
| `ws_basis` | 报告凭什么说是游走脾（见下） |

**`ws_basis` 的五个值（全文指南 D1）：**

<!-- widths: 40,60 -->
| 值 | 什么时候选 |
|---|---|
| Imaging shows ectopic position or mobility | 影像（超声、CT、MRI）写了脾在异位或活动 |
| Operation shows ectopic position or mobility | 手术中见到脾在异位或活动、蒂长 |
| Imaging and operation | 影像和术中所见**都**写明了脾异位或活动（脾不在脾窝、蒂长、韧带缺如或松弛等）。手术只是治疗性切除、没有描述脾位置或活动度的，不算，选 Imaging 那一项（全文指南 6.7，2026 年 10 月 19 日校准讨论） |
| Named wandering spleen, no detail | 作者只写了"游走脾"，没有说凭什么 |
| Torsion only, position not stated | 儿童脾蒂扭转，没有写脾的位置和韧带（全文阶段按 D1 宽松纳入的就是这一类） |

### 5.3 呈现和主要暴露

**`presentation` 的五个值加 `NR`**（五个值来自协议附录 C；`NR` 是 2026 年 10 月 25 日作者同意加的补充值）。**【Claude 的读法】**

<!-- widths: 22,48,30 -->
| 值 | 什么时候选 | 虚构例 |
|---|---|---|
| Acute | 这次急性发作是第一次，此前没有类似症状 | 左上腹突发剧痛 6 小时，既往无类似症状 |
| Chronic or intermittent | 反复发作或长期症状，因这些症状（常为择期）手术 | 反复腹痛 8 个月，影像检查后择期脾固定术 |
| Acute on chronic | 有长期或反复的症状，这次因新的急性发作而手术 | 反复腹痛 8 个月，近 2 天加重，急诊手术 |
| Asymptomatic | 没有症状，偶然发现 | 因其他原因做超声时发现脾脏活动度大 |
| Mass only | 只有腹部包块，没有疼痛 | 发现左腹包块 1 个月，无腹痛 |
| NR | 报告没有写这次的发作形式，也无法从病史推断；在 notes 里写明 | 只写“因游走脾行脾固定术”，没有症状和病程 |

**主要暴露（协议第 8 节）：** 从**导致手术的这一次发作**的症状开始，到手术的时间，单位是天。同一次住院里手术前在医院的时间**算**；出院后到择期手术之间的计划间隔**不算**（记为等待间隔）。换算按第 6 节的 9 条规则。

<!-- widths: 28,72 -->
| 列 | 怎么填 |
|---|---|
| `idx_dur_verbatim` | 原文写法，如 "abdominal pain for 3 days"、"病程 2 天"。**必填**（有天数时） |
| `idx_dur_days` | 天（按第 6 节）；含糊或没有写填 NR；只有报告里根本没有症状时间的也填 NR。不要写成 "2 days" 这样的文字，只写数字 |
| `idx_dur_rules` | 用了第几条规则，如 `1;9`。报告直接给了天数、没用任何规则的留空 |
| `idx_dur_intermittent` | 规则 6：间歇性或加重的发作填 Yes，否则 No |
| `idx_dur_alt_days` | 规则 6 的备选编码（加重的那一段）；没有则留空 |
| `idx_dur_lower_bound` | 规则 9：用了入院时的持续时间并作为下限，填 Yes |
| `idx_dur_cat_imprecise` | 规则 5：天数填 NR、但所有合理理解都在同一类别时，填那个类别 |
| `idx_dur_category` | 灰色，公式，不要填 |
| `src_exposure` | 页、表或图。**有天数时必填** |

### 5.4 次要暴露和等待

<!-- widths: 28,72 -->
| 列 | 怎么填 |
|---|---|
| `total_hist_verbatim`、`total_hist_days` | 从**第一次**归因于游走脾的症状到手术的总病程（包括此前的发作）。换算同第 6 节。没有写填 NR |
| `n_earlier_episodes` | 此前发作的次数（整数）；只写"反复发作"、没有次数填 NR |
| `missed_dx` | 至少有一次**有记录的**此前就诊，当时没有诊断游走脾或做了别的诊断（包括影像误读）：Yes。明确写了此前诊断正确、没有漏诊：No。没提：NR |
| `missed_dx_alt`、`missed_dx_contact` | 当时做了什么诊断；发生在哪一次就诊。自由文本 |
| `known_dx_deferred` | 本次发作之前已经诊断游走脾，当时没有手术（家属拒绝、建议观察、或已排期择期手术）：Yes |
| `deferred_reason` | Family declined / Observation advised / Elective operation scheduled / Other / Not applicable |
| `waiting_interval_days` | 等待间隔（天，规则 7）。**【待校准】** 协议没有说测到哪一天：**【Claude 的读法】** 从做出诊断并推迟手术那一天，到这次发作开始那天（若没有发生急性发作，则到择期手术那天）；报告怎么写的原文放进 notes |
| `torsion_awaiting` | 已知诊断、等待手术期间发生了扭转：Yes。已知诊断、等待期间没有扭转：No。没有已知诊断的：Not applicable |

### 5.5 检查

- `img_us`、`img_doppler`、`img_ct`、`img_mri`：做了的 Yes；报告明确没做的 No；没提 NR。
- `whirl_sign`：影像上有旋涡征（whirl sign）为 Yes。
- `perfusion`：术前影像上脾的灌注：Normal / Reduced / Absent / NR（如增强 CT 脾不强化为 Absent）。
- `platelets`：**手术前**最近一次的血小板计数，×10⁹/L，只写数字。只写"正常"、没有数值的填 NR，并在 notes 里写"reported as normal"。`thrombocytosis`（> 450）是灰色公式。

### 5.6 手术和主要结局

<!-- widths: 26,74 -->
| 列 | 怎么填 |
|---|---|
| `approach` | Open / Laparoscopic / Converted（腹腔镜中转开腹）/ NR；未手术填 Not applicable |
| `torsion_at_op`、`torsion_degrees` | 手术中见到蒂扭转 Yes/No/NR；度数（如 720）。度数不确定（"多圈"）填 NR |
| `viability` | **主要结局。** Viable / Partially non-viable / Non-viable / NR；未手术填 Not applicable。见第 7 节 |
| `viab_basis` | 依据：Intraoperative（术中所见）/ Histology（病理）/ Both / NR；未手术 Not applicable |
| `procedure` | Detorsion only / Splenopexy / Partial splenectomy +/- splenopexy / Total splenectomy / Autotransplantation / No operation / NR |
| `procedure_other` | 同时做的其他手术，如胃固定术、疝修补 |
| `fixation`、`fixation_other` | 固定方法：Mesh / Retroperitoneal or extraperitoneal pouch / Omental wrap / Direct suture / Other (specify) / Not applicable / NR。**没有做固定的（脾切除、未手术）填 Not applicable** |
| `spleen_size_cm` | 最长径，厘米，取术前影像或手术中的测量值；只写"增大"、没有数值填 NR |
| `reason_viable_removed` | **脾是有活力的、却被切除了**，原因：Failure of fixation / Surgeon's preference / Other；其他情形 Not applicable。原因是"脾太大无法固定"这类的选 Other，并在 notes 里写明 |
| `src_outcome` | 页、表或图。`viability` 有内容（不是 NR / Not applicable）时必填 |

**"index operation"（指数手术）：** 协议主要结局写的是"在 index operation 时脾无活力"。**【Claude 的读法，待校准】** 指数手术 = 结束这次指数发作的**第一次**为游走脾做的手术。之后的手术（复发再手术、补做脾切除）写进 `further_surgery`、`recurrence_details`，不改 `viability` 和 `procedure`。

### 5.7 随访

<!-- widths: 26,74 -->
| 列 | 怎么填 |
|---|---|
| `followup_months` | 手术到末次随访的月数；年 × 12；天 ÷ 30.4（同规则 2 的月长）。没有写填 NR |
| `recurrence`、`further_surgery`、`recurrence_details` | 复发或再扭转；是否再次手术；细节自由文本 |
| `status_last_fu` | 末次随访时脾的状态：Preserved（保留，位置和灌注正常）/ Partially preserved / Lost（已切除）/ NR。做过全脾切除的是 Lost；脾固定后又因缺血切除的也是 Lost |
| `post_splenectomy_compl` | 脾切除后的并发症，自由文本 |
| `src_age_sex`、`src_other` | 出处（页、表、图） |

## 6. 时间换算：9 条规则和虚构的例子

下面的 9 条规则来自**协议附录 C**（个别规则的举例略去，完整原文见协议；中文是说明）。例子是虚构的。工作簿的 Duration_calc 表只是计算器，处理不了含糊的说法和规则 6–9 的判断，**最后以人工判断为准**。

<!-- widths: 8,45,47 -->
| 规则 | 内容 | 说明 |
|---|---|---|
| 1 | Hours are converted to days (hours ÷ 24, one decimal). | 小时 ÷ 24，保留一位小数。**【Claude 的读法】** 第二位小数是 5 时进位（0.25 → 0.3） |
| 2 | Weeks × 7; months × 30.4; years × 365. | 周 × 7；月 × 30.4；年 × 365。不用再取整 |
| 3 | Ranges take the midpoint. | 范围取中点，如 3–5 天记 4 天 |
| 4 | "Less than 24 hours", "a few hours" or "overnight" is coded as 0.5 days. | 这三种说法记 0.5 天 |
| 5 | Imprecise terms are coded as missing on the continuous scale, and assigned a category only if every plausible reading falls in the same category. | 含糊说法的天数填 NR；只有所有合理理解都落在同一类别时，才填类别 |
| 6 | Intermittent or worsening presentations: the primary coding uses the whole stated period; the alternative coding uses the period of worsening. | 间歇或加重：主要编码用整个时段；备选编码用加重的那一段 |
| 7 | A planned interval between discharge and a scheduled elective operation is excluded from the index episode and recorded as the waiting interval. | 出院后到择期手术之间的计划间隔不计入，另记为等待间隔 |
| 8 | When dates of symptom onset and of operation are both given, the interval is calculated exactly. | 同时给出症状开始和手术的日期时，按日期精确计算 |
| 9 | When a report gives symptom duration at admission but not the timing of operation within the admission: an operation described as immediate or emergency adds nothing; an operation on hospital day N adds N days; otherwise the duration at admission is used and flagged as a lower bound. | 只给了入院时的症状时间、没给入院后手术的时间：急诊或立即手术不加；第 N 个住院日手术加 N 天；都没写就用入院时的时间并标为下限 |

### 6.1 例子（虚构）

<!-- widths: 36,16,8,40 -->
| 原文（虚构） | `idx_dur_days` | 规则 | 说明 |
|---|---|---|---|
| 腹痛 36 小时后入院，当晚手术（入院后 4 小时）| 1.7 | 1 | 给了入院后手术的时间，按时间精确算：36 + 4 = 40 小时 ÷ 24 = 1.67 → 1.7。**不用规则 9**（规则 9 只用于没给手术时间的情形） |
| 突发腹痛 2 小时，急诊手术 | 0.1 | 1 | 2 ÷ 24 = 0.083 → 0.1 |
| 腹痛 14 小时，入院后即刻手术，没写具体时间 | 0.6 | 1、9 | 14 ÷ 24 = 0.583 → 0.6；"即刻手术"不加时间，也不标下限 |
| 腹痛 3 天后入院；入院第 2 天手术 | 5 | 9 | 3 + 2 = 5。注意"第 N 个住院日"的算法见下面的【待校准】 |
| 腹痛 3 天后入院，手术（没有写什么时候做）| 3 | 9 | 用入院时的 3 天，`idx_dur_lower_bound` = Yes |
| 症状 2 周 | 14 | 2 | 2 × 7 |
| 症状 3 个月 | 91.2 | 2 | 3 × 30.4 |
| 症状半年 | 182.4 | 2 | 6 × 30.4 |
| 症状 2 年 | 730 | 2 | 2 × 365 |
| 腹痛 3–5 天 | 4 | 3 | 中点 |
| 腹痛 1–2 周 | 10.5 | 2、3 | (7 + 14) ÷ 2 |
| 腹痛 2–3 个月 | 76 | 2、3 | (60.8 + 91.2) ÷ 2 |
| 夜间腹痛（"overnight"）| 0.5 | 4 | |
| 腹痛"数天" | NR | 5 | "数天"可以是 3 天也可以是 10 天，跨类别，不填类别 |
| 腹痛"数月" | NR（`idx_dur_cat_imprecise` = >30 d） | 5 | 所有合理理解（2 个月到 11 个月）都在 30 天以上，填类别 >30 d |
| 腹痛"10 余天" | NR（`idx_dur_cat_imprecise` = 8-30 d） | 5 | 10–19 天都在 8–30 天，填类别。**【待校准】** 也可以认为"10 余天"是近似值，按 10 天填；校准时统一 |
| 间歇腹痛 1 周，近 2 天加重 | 7；`idx_dur_alt_days` = 2；间歇 = Yes | 6 | 主要编码用整个时段 7 天，备选编码用加重的 2 天 |
| 反复腹痛 8 个月，近 1 天剧烈 | 1；`total_hist_days` = 243.2 | 2（总病程）| 呈现 = Acute on chronic。主要暴露取导致手术的这一次发作；总病程是从第一次症状算起 |
| 3 月 3 日 22:00 起病，3 月 5 日 10:00 手术 | 1.5 | 8、1 | 36 小时 = 1.5 天。**只写天数，不要把日期写进表里** |

:::warn 要注意的三件事
- **日期不进表。** 提取表和共识文件里只有天数，没有任何具体日期（`date_extracted` 是你提取的日期，不算）。
- **不要用规则 9 去"补"没给时间的手术。** 只有入院时的症状时间、完全没写什么时候手术的，才用规则 9。
- **规则没覆盖的说法**（如"昨天起"、"数小时前开始"）：不要自己发明规则。按最接近的规则填，在 notes 里写明；拿不准就填 NR，校准时讨论。
:::

**【待校准】第 N 个住院日：** 规则 9 写"手术在第 N 个住院日，加 N 天"。入院当天算第 1 日还是第 0 日，协议没有说。**【Claude 的读法】** 照字面：报告写"入院第 2 天手术"就加 2 天；写"入院后次日手术"按第 2 个住院日？还是第 1 天？——这类写法在 notes 里写明原文，校准时统一。

### 6.2 例子（虚构）：等待手术期间发生扭转

> 虚构例：超声诊断游走脾，门诊医生建议择期手术，已排期 6 周后；排期第 5 周，患儿突然腹痛，当晚急诊手术，症状 8 小时。

- `known_dx_deferred` = Yes；`deferred_reason` = Elective operation scheduled
- `torsion_awaiting` = Yes
- `idx_dur_days` = 0.3（8 ÷ 24 = 0.333 → 0.3）；规则 1。**6 周的计划等待不计入主要暴露**（规则 7）
- `waiting_interval_days`：按上面的读法，从诊断到这次发作开始约 5 周 = 35 天；原文写在 notes
- `presentation` = Acute（这次发作是急性的）；`missed_dx` = No

## 7. 主要结局：脾脏活力和术式

**【协议第 12 节】** 主要结局是指数手术时脾**无活力**：因梗死、坏死或复位后灌注不恢复而做了全脾或部分脾切除，由手术所见和/或病理判断。**脾有活力但因别的原因被切除，算"有活力"**，在附加结局里另报。

提取员只需要如实记录两件事：**作者对脾脏活力的判断**（`viability`）和**做了什么手术**（`procedure`）。`primary_outcome` 是灰色公式，会按下面的规则自动得出。

<!-- widths: 34,22,22,22 -->
| `viability` | `procedure` | 公式得出的 `primary_outcome` | 说明 |
|---|---|---|---|
| Non-viable | 任何 | Non-viable | |
| Viable | 任何（包括脾切除）| Viable | 有活力的脾被切除也算有活力；要填 `reason_viable_removed` |
| Partially non-viable | 全脾或部分脾切除 | Non-viable | 协议：因梗死做部分脾切除算无活力（敏感性分析 3 把它改算保脾） |
| Partially non-viable | 脾固定、仅复位、其他 | Review | 公式不下结论，共识时判断 |
| NR | 全脾或部分脾切除 | NR - removed, check reason | 要回到原文看有没有写切除的原因 |
| NR | 其他 | NR | |
| Not applicable（未手术）| No operation | Not applicable | |

### 7.1 例子（虚构）

<!-- widths: 40,60 -->
| 原文（虚构） | 怎么填 |
|---|---|
| 脾脏呈紫黑色，复位后颜色未恢复，行全脾切除 | `viability` = Non-viable；`viab_basis` = Intraoperative；`procedure` = Total splenectomy；`torsion_at_op` = Yes |
| 蒂扭转 360°，复位后脾脏转红润，行脾固定术（腹膜后袋）| Viable；Intraoperative；Splenopexy；`fixation` = Retroperitoneal or extraperitoneal pouch；`torsion_degrees` = 360 |
| 脾上极梗死，切除上极，剩余脾脏固定 | Partially non-viable；Partial splenectomy +/- splenopexy；公式得出 Non-viable |
| 脾脏有活力，但长 16 cm，网袋放不下，行全脾切除 | Viable；Total splenectomy；`reason_viable_removed` = Other（notes 写"too large to fix"）；`spleen_size_cm` = 16 |
| 行全脾切除，没有写脾脏活力 | `viability` = NR；公式得出"NR - removed, check reason"。**先回到原文再看一遍**，作者的描述（如"脾脏梗死"）可能写在讨论里；真的没有就留 NR |
| 术中看起来有活力，术后病理报告为出血性梗死 | **【待校准】** 术中判断和病理不一致：填报告最后的结论，`viab_basis` = Both，把冲突写进 notes，共识时讨论 |
| 超声诊断游走脾，观察随访，没有手术 | `procedure` = No operation；`viability`、`viab_basis`、`approach` = Not applicable；`fixation` = Not applicable |
| 首次手术脾固定（有活力），6 个月后因再次扭转缺血切除 | 指数手术：Viable、Splenopexy。`recurrence` = Yes；`further_surgery` = Yes；`recurrence_details` 写后来的经过；`status_last_fu` = Lost |

## 8. 中文报告

### 8.1 术语对照

<!-- widths: 24,34,42 -->
| 中文 | 英文 | 提取时怎么用 |
|---|---|---|
| 游走脾、游动脾、异位脾、漂浮脾 | wandering / floating / ectopic spleen | `ws_basis` 的依据 |
| 脾蒂扭转、脾扭转 | splenic pedicle torsion | 只写扭转、没写位置的是 Torsion only |
| 脾梗死、脾坏死、脾脏呈紫黑色 | infarction / necrosis | 倾向 Non-viable，看复位后有没有恢复 |
| 复位后血运恢复、颜色转红 | reperfusion after detorsion | 倾向 Viable |
| 脾固定术、全脾切除、部分脾切除、脾脏自体移植 | splenopexy / total / partial splenectomy / autotransplantation | `procedure` |
| 腹腔镜、中转开腹 | laparoscopic / converted | `approach` |
| 术中见、术后病理 | intraoperative / histology | `viab_basis` |
| 起病、病程、入院、术前 | onset / duration / admission / preoperative | 时间换算 |
| 反复发作、间歇性、阵发性 | recurrent / intermittent | 规则 6，`idx_dur_intermittent` = Yes |
| 误诊、漏诊、外院诊断为…… | misdiagnosis | `missed_dx` = Yes |
| 余、左右、约 | about / more than | 见 8.2 |

### 8.2 中文里常见的时间写法（虚构例）

<!-- widths: 32,22,46 -->
| 原文（虚构） | `idx_dur_days` | 说明 |
|---|---|---|
| 腹痛 2 天 | 2 | 直接给了天数 |
| 病程 3 周 | 21 | 规则 2 |
| 腹痛 3～5 天 | 4 | 规则 3，中点 |
| 腹痛 1 年余 | NR；类别 >30 d | 规则 5：1 年多，所有合理理解都在 30 天以上 |
| 反复腹痛半年，加重 3 天 | 间歇 = Yes；主要 182.4；备选 3 | 规则 6 和 2；呈现 = Acute on chronic 或 Chronic，看手术是否因这次加重而急诊 |
| 外院诊断为"肠痉挛"，次日转入我院 | `missed_dx` = Yes；`missed_dx_alt` = 肠痉挛 | 中文原文可以直接抄进自由文本 |

## 9. 疑难情形速查

<!-- widths: 36,64 -->
| 情形 | 怎么办 |
|---|---|
| 一篇报告里有多名儿童，只有一人符合（其余是成人、副脾扭转等）| 只录符合的一人；其余在 notes 里写"n 名不符合条件的未提取" |
| 有的患者被报告写成了"游走脾"，但描述更像副脾 | 照作者的诊断提取，`ws_basis` 如实选，notes 里写你的怀疑；不要自己排除（全文阶段已经决定纳入） |
| 同一名患者有两次入院 | 一行；指数发作是导致第一次脾手术的那一次 |
| 综述里有作者自己的新患者，也引用了别人的病例 | 只提取作者自己的新患者 |
| 表格里有的格子是"-"或空 | 报告没写：NR，不是空白 |
| 同一篇报告里不同地方对同一数字说法不同（正文 3 天、表格 4 天）| 填表格或正文里更具体的那个，另一个写进 notes；两个出处都写在 `src_exposure` |
| 作者提供了个体数据（IPD）| 提取时用作者提供的数据；来源写在 notes 里；数据文件放在仓库外面，位置写在 IPD_requests 表 |
| 数据看起来不可能（年龄 200 岁、手术前 5 年的"急性"发作）| 抄原文，notes 里写"原文如此，疑有误"，不要自己改 |
| 报告里没有任何时间信息 | `idx_dur_days` = NR，`idx_dur_verbatim` 空；该患者不进主要分析，但仍然提取 |

## 10. 校准：先做 10 篇

**【协议第 14 节】** 正式提取前，两位提取员先各自提取同样的 10 篇报告，比较，讨论分歧，必要时改提取表和规则。

1. **选哪 10 篇：** 全文阶段结束、纳入名单确定以后，用 `tools/draw_extraction_calibration.py` 从 `fulltext_included.csv` 里抽。**种子 20261019 是 2026 年 10 月 19 日定的，早于任何全文决定，抽样结果因此不会受筛选结果的影响；名单已于 2026 年 10 月 25 日确定（269 篇），当天抽出了 10 篇。** 只从已发表个体数据的 Include 里抽（靠邮件拿到个体数据的不进校准，以后正式提取时再做；两位提取员都同意）；预试验的 53 篇不进（舒俊预试验时提取过，不算没看过的报告；**舒俊和卞红强都同意**；要放进去就加 `--keep-pilot`）。要求至少包括：中文 3 篇、系列报告 3 篇、写法各异的时间（小时、周、范围、含糊说法各至少 1 篇）、只写"脾扭转"的 D1 类 1 篇、有未手术或未切除的 1 篇（作者 2026 年 10 月 19 日确认这些分层要求）。中文、系列和 D1 用全文筛选记录里的值；**时间写法和未手术这几层只读数据库摘要里的关键词，很粗，没有摘要的报告配不上**；哪一层凑不够，脚本在设计文件里写明，不硬凑；这次“范围”一层在候选里按摘要关键词一篇也没有，所以没有凑够。本院 5 例（OWN）另外提取，不在这 10 篇里。给提取员的只有 `calibration_10_list.csv`，分层标记的 `calibration_10_key.csv` 两人都做完之前不打开。
2. **各自提取**，互不查看。
3. **各自运行 `check`**，把格式错误改掉。
4. **运行 `compare`**（由杨俊决定谁来运行；Claude 只处理杨俊交来的文件，并且两人都做完之后才看逐条结果），分歧清单发给两位提取员。校准只有 10 篇，患者可能只有二三十人，**kappa 不可靠，主要看分歧清单**。
5. **讨论每一条分歧**，把"统一的读法"（第 12 节）写下来，更新这份说明；需要时改提取表。
6. 校准用的 10 篇在正式提取里照样再做一遍，用校准后的规则。

## 11. 保存前自查；两人完成后

### 11.1 每次保存前

- [ ] 每名儿童都有 `patient_id`，格式 WS0123_P1 或 OWN_P1，没有重复。
- [ ] `report_id` 在 Reports 表里有对应的行；`n_children_individual` 等于 Patients 表里这篇的行数。
- [ ] `age_years` 是数字或 NR，且小于 18。
- [ ] 有天数就有 `idx_dur_verbatim` 和出处 `src_exposure`；有活力判断就有 `src_outcome`。
- [ ] 下拉列表的格子没有手打的、不在列表里的值。
- [ ] 没有写进任何姓名、住院号、出生日期或具体日期。
- [ ] 灰色列没有改动。
- [ ] 运行：`python3 -I tools/compare_extraction.py check extraction_E1.xlsx --extractor E1`（E2 同理）。

### 11.2 两人都做完以后

1. **比对：** `python3 -I tools/compare_extraction.py compare extraction_E1.xlsx extraction_E2.xlsx --out <目录>`。加 `--aggregate-only` 只打印数字、不生成文件。
2. **比对脚本看什么：**
   - 患者按 patient_id 配对；只在一份文件里的患者、两边儿童数不同的报告，单独列出。
   - **主要暴露的 kappa**：四个时间类别（<=2 天、3–7 天、8–30 天、>30 天）加 NR；类别由脚本从天数重新算，不读 Excel 里的公式列。
   - **主要结局的 kappa**：无活力 / 有活力 / 其他（NR、Review、Not applicable）；另报原始 `viability` 一栏的一致率。
   - 天数：差值在容差内算一致（0.5 天或 10%，取较大者）。
   - 所有编码字段的一致率；自由文本、出处、灰色列不比较。
3. **分歧清单：** `ex_primary_disagreements.csv`（主要暴露和主要结局的分歧，带出处和讨论列）、`ex_field_differences.csv`（所有字段的差异）。
4. **两人先讨论；讨论不了的交杨俊**，填 `agreed_value`、`adjudicator_value`；结果写入共识文件。
5. **Ji Wang** 在共识前核查两份提取表（范围、单位、重复患者；协议 v1.5 的规定）。**【Claude 的读法】** 发现的问题交回提取员去改，Ji Wang 自己不改数据，这样每个值仍然只来自提取员。
6. **记录并在方法里报告：** 校准结果、kappa（主要暴露、主要结局）、分歧条数、讨论解决和仲裁的条数。

## 12. 要在校准时统一的读法（清单）

<!-- widths: 6,56,38 -->
| 编号 | 事项 | 现在的写法 |
|---|---|---|
| X1 | 规则 1 的小数进位 | 第二位小数是 5 时进位（0.25 → 0.3）。【Claude 的读法】 |
| X2 | 规则 9 里入院当天算第几个住院日 | 照字面；写法不清时原文放进 notes。【待校准】 |
| X3 | 规则 5："10 余天"这类近似说法 | 按含糊说法填 NR + 类别；也可按近似值 10 天。【待校准】 |
| X4 | "昨天起"、"数小时前"等规则没覆盖的说法 | 不自己发明规则：按最近的规则，或 NR，notes 写明。【待校准】 |
| X5 | 等待间隔测到哪一天 | 从诊断并推迟手术那天，到这次发作开始那天（或择期手术那天）。【待校准】 |
| X6 | "指数手术"的定义 | 结束这次指数发作的第一次为游走脾做的手术。【待校准】 |
| X7 | 术中判断和病理不一致时的活力 | 填报告的最后结论，`viab_basis` = Both，冲突写进 notes。【待校准】 |
| X8 | `country` | 患者就诊机构所在国家。【Claude 的读法】 |
| X9 | 新生儿按天写的年龄 | 天 ÷ 365，两位小数。【Claude 的读法】 |
| X10 | `patient_id` 的编号 | 用作者的病例号，没有就按出现顺序；不重新编号。【Claude 的读法】 |
| X11 | `presentation` 五个值的边界，以及没写时填 `NR` | 见 5.3 的表；`NR` 已由作者同意加入（2026-10-25）。五个值的边界仍是【Claude 的读法】 |
| X12 | 比对时的容差和类别 | 天数 0.5 天或 10%；主要结局三类。【Claude 的读法】 |

## 13. 没有核实的

- 这份说明里的所有例子都是虚构的，没有对照过任何真实报告；规则的原文来自协议 v1.5 附录 C，工作簿的列名和下拉值来自模板 v2026-10-25a。
- 提取工作簿从来没有在 Excel 或 WPS 里打开过：下拉框、公式列和版面的实际表现没有验证。
- `compare_extraction.py` 只用虚构数据试过，没有在真实的提取文件上运行过。
- 卞红强和杨俊是否同意提取阶段的分工：作者转告两位已知道并同意，方式和日期没有说明，没有书面确认。
- 一份报告里有多少名儿童要提取，要等全文阶段结束才知道；工作量没有估计。
