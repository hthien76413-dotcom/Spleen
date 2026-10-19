# 个体患者数据（IPD）索取邮件（草稿，中英文）

项目：儿童游走脾系统综述（PROSPERO CRD420261520329）。草稿日期：2026 年 10 月 18 日；10 月 19 日补充"联系不上时的途径"（第 1 节、第 5 节）（v2026-10-19a）。

状态：**草稿，一封都没有发出。** 方括号 [ ] 里的内容发送前要填；第 2 节是需要作者决定的事项（邮件正文里已按保守的写法写好，决定后再改）。

依据：协议第 14 节（向通讯作者发邮件索取个体数据，间隔 4 周发两封，索取不到就做叙述性描述）；全文筛选指南第 8 节（2026 年 10 月 5 日决定：到全文阶段一次性批量索取；D6：第二封后再等 4 周，从第一封算起最长 8 周）。索取的变量取自协议附录 C。

邮件里没有任何患者信息。中文邮件由 Claude 起草，没有经过母语审校，称呼和措辞请按您的习惯改。

---

## 1. 每一篇发送前要做的事

- **先核对全文再发（指南第 8 节）：** 确实只有汇总数据、没有个体层面的表格或图？确实是游走脾？确实有儿童？两位全文筛选员都记 Pending IPD（理由 A）并达成一致，才进入名单。名单定下来以后**同一天一次性发出所有第一封**。
- **找通讯作者的邮箱：** 从论文的通讯作者栏或作者所在机构的网页上找；不要猜。邮箱**不写进仓库**；提取工作簿的 IPD_requests 表里只登记姓名和邮箱的来源（论文 / 机构网页 / 其他）。
- **联系不上时的途径（2026 年 10 月 19 日补充，按顺序试）：**
  1. 论文里印的通讯作者邮箱（中文文章看"通信作者"栏）。退信或论文没有印邮箱，才走下一步。
  2. 作者所在医院或科室的公开页面上的联系方式。
  3. 期刊编辑部转交：请编辑部把邮件转给通讯作者，并说明这是系统综述的数据索取。编辑部是否肯转交，没有核实。
  4. 熟人转达：请认识该科室的小儿外科同行转交邮件或引荐。有没有这样的人，由舒俊、杨俊自己判断。

  无论走哪条途径，转出去的都是同一封邮件，不另写说明，不附任何东西。**8 周的期限不因此延长**（从第一封算起，见下面的时间表）。第 2 步以后每走一步，都在 IPD_requests 表里登记（见第 5 节）。
- **谁发：** 建议由舒俊发出（PROSPERO 联系人；协议里登记的联系邮箱是 shujunmengzhe@163.com），抄送杨俊（通讯作者）。有单位邮箱的话，用单位邮箱发更容易被对方信任。发件人、抄送和回复地址请作者确认（第 2 节 O3）。
- **用哪种语言：** 报告是中文的，发中文邮件（第 4 节）；报告是英文的，发英文邮件（第 3 节）。作者是中国人但发表在英文期刊上的，可以发英文，也可以把中文版附在英文之后，按您的习惯。
- **同一位作者有几篇：** 一封邮件里把几篇都列出来，但在 IPD_requests 表里每篇一行。
- **时间表（D6）：** 第一封发出当天登记日期；4 周后发第二封（第 3.2 / 4.2 节）；第二封之后再等 4 周；到期仍没有数据的，最终状态定为"只做叙述性描述"（FT_log 记 Exclude，理由 A）。从第一封算起最长 8 周，不让 Pending 一直悬着。
- **不要附任何东西。** 邮件里不放我们自己的病例，也不放别人的数据。

## 2. 需要作者决定的事项

- **O1　个体数据怎么用、公不公开——已决定（2026 年 10 月 18 日，分层）：** 从已发表文章提取的去标识逐例数据，标明来源报告，放公共数据库（作者报告：期刊把去标识逐例表算作"个体参与者详细信息"，所以不放附加文件）；**作者提供的个体数据不逐例公开，只用于合并分析，经原作者书面同意才给他人**；本院 5 例按家属同意的范围。邮件正文的写法与此一致，不用再改；协议"传播计划"已按此改写（协议 v1.5）。
- **O2　对作者的回报。** 邮件里写了"在致谢中列出您的姓名（经您同意）"，**没有承诺署名**。是否给署名要按期刊的作者资格标准和四位作者共同决定；不确定的话，这一句也可以删掉。
- **O3　发件人、抄送、回复地址。** 见第 1 节。
- **O4　是否承诺把稿子发给对方看。** 邮件里放了一个可选句（方括号），不想承诺就删。
- **O5　PROSPERO 链接。** 邮件里只写注册号 CRD420261520329，没有写网址（新版 PROSPERO 的链接格式我没有核实过）。想放链接，请您在网站上复制。

---

## 3. 英文邮件

### 3.1 第一封

**Subject:** Request for individual patient data: systematic review of wandering spleen in children (PROSPERO CRD420261520329); [first author, year]

Dear [Professor / Dr] [surname],

I am writing on behalf of a research team at [full name of institution], Wuhan, China. We are conducting a systematic review of children with wandering spleen, using individual patient data, registered on PROSPERO (CRD420261520329). The main question is whether the length of the symptomatic episode before operation is associated with the state of the spleen at operation (viable or non-viable).

We read your report: [citation, with DOI if available]. It describes [N] children, but from the published article we could not find the results for each child separately [state what is missing, for example: "the operative findings and the duration of symptoms are given only as group totals"]. We would be very grateful if you could share de-identified, child-level data for these patients.

**What we are asking for.** Only what is in your records, and only for the children in this report. Please leave blank anything you do not have. The most important items are the duration of symptoms before operation and the state of the spleen at operation.

- **Child:** age at operation (years, or months for infants); sex; associated conditions (for example gastric volvulus, diaphragmatic hernia or eventration, absent or ectopic kidney, previous abdominal surgery, syndrome); congenital or acquired.
- **Timeline:** type of presentation (acute / chronic or intermittent / acute on chronic / asymptomatic); duration of the symptoms that led to this operation, in days; total length of the symptom history; number of earlier episodes; whether the diagnosis was missed at an earlier visit; whether the diagnosis was known and the operation was deferred (and why).
- **Investigations:** imaging used (ultrasound, Doppler, CT, MRI); whirl sign; splenic perfusion; preoperative platelet count.
- **Operation:** approach; torsion at operation (and degrees); splenic viability (viable / partly non-viable / non-viable) and whether this was judged at operation or on histology; procedure (detorsion, splenopexy, partial or total splenectomy); fixation technique; spleen size; reason for removing a spleen that was still viable.
- **Follow-up:** length of follow-up; recurrence or re-torsion; further surgery; splenic status at last follow-up; complications after splenectomy.

**Format and privacy.** A simple Excel or Word table with one row per child (Patient 1, 2, 3 …) is perfect; any other format is fine too. **Please do not send names, hospital numbers, dates of birth or exact dates.** Ages and durations are enough. Please also check whether your institution requires any permission before de-identified data are shared.

**How we will use the data.** The data will be used only for the pooled analysis in this review. We will not pass your child-level data to anyone else or publish them at child level without your written permission. [Optional: With your permission, we would name you in the Acknowledgements.] [Optional: We would be glad to send you the draft before submission.]

If you could reply within four weeks, that would help us a great deal. If we do not receive child-level data, we will describe your report in the text of the review only and will not include it in the quantitative analysis. If you are not the right person to ask, or prefer not to share, please let us know, and, if possible, tell us whom to contact.

Thank you very much for your time and for your work on this rare condition.

With kind regards,

[Name]

[Position], Department of General Surgery

[Full name of institution], Wuhan 430016, Hubei, China

E-mail: [address]

On behalf of the review team: Jun Shu, Jun Yang, Hongqiang Bian, Fei Peng, Ji Wang


### 3.2 Second email (four weeks after the first)

**Subject:** Reminder: request for individual patient data, wandering spleen in children (PROSPERO CRD420261520329); [first author, year]

Dear [Professor / Dr] [surname],

On [date of the first e-mail] I wrote to ask whether you could share child-level data from your report [short citation] for our systematic review of wandering spleen in children (PROSPERO CRD420261520329). I am sorry to write again, and I understand that you may be very busy or that the data may not be available.

If you are able to help, we need only the items in my first message (the most important are the duration of symptoms before operation and the state of the spleen at operation), in any format, without names, hospital numbers or exact dates. A short reply saying that you cannot share the data would also help us.

If we have not heard from you by [date, four weeks from now], we will describe your report in the review without including it in the quantitative analysis.

Thank you again.

With kind regards,

[Name and signature as in the first e-mail]

### 3.3 Short replies

**On receiving data:** Dear [name], thank you very much, we have received the table. We will check it against your published report and write to you only if something is unclear. [Optional: We will send you the rows we have extracted so that you can confirm them.] [Optional: With your permission we will name you in the Acknowledgements.]

**If the author declines or cannot share:** Dear [name], thank you for letting us know. We understand. We will describe your report from the published article only.

---

## 4. 中文邮件

### 4.1 第一封

**主题：** 恳请提供个体患者数据：儿童游走脾系统综述（PROSPERO CRD420261520329）；[第一作者，年份]

尊敬的[姓]教授 / [姓]医生：

您好！

我们是[单位全称（中文）]的研究团队，正在做一项关于儿童游走脾的系统综述，需要用到患者个体层面的数据，该综述已在 PROSPERO 注册（注册号 CRD420261520329）。我们主要想了解：术前症状持续的时间，与手术时脾脏的状态（是否已经坏死）是否相关。

我们读到了您的论文：[文献信息，有 DOI 的附上]。文中报告了 [N] 例患儿，但我们在已发表的文章里没有找到每一例患儿各自的结果[写明缺什么，例如："手术所见和症状持续时间只有汇总数字"]。如果方便，恳请您提供这些患儿**去标识的、逐例的数据**。

**我们需要的内容。** 只要病历里有的，并且只限这篇报告里的患儿；没有的请留空。**最重要的两项是：手术前症状持续的时间，以及手术时脾脏的状态。**

- **患儿情况：** 手术时年龄（岁；婴儿用月）；性别；伴随疾病（如胃扭转、膈疝或膈膨升、肾缺如或异位、既往腹部手术、综合征等）；先天性还是后天性。
- **病程：** 就诊表现（急性 / 慢性或间歇性 / 慢性急性发作 / 无症状）；导致本次手术的症状持续了多少天；症状总病史多长；之前发作过几次；之前就诊时是否漏诊；诊断明确后手术是否被推迟（原因）。
- **检查：** 影像检查方式（超声、多普勒超声、CT、MRI）；有无漩涡征；脾脏血流灌注情况；术前血小板计数。
- **手术：** 手术方式（开放 / 腹腔镜 / 中转）；术中扭转情况（圈数或度数）；脾脏活力（存活 / 部分坏死 / 完全坏死），是术中判断还是病理判断；术式（单纯复位、脾固定术、部分脾切除、全脾切除）；固定方法；脾脏大小；脾脏仍有活力却被切除的原因。
- **随访：** 随访时间；有无复发或再次扭转；是否再次手术；末次随访时脾脏的状态；脾切除后的并发症。

**格式与隐私。** 用一张简单的 Excel 或 Word 表格，每行一例患儿（病例 1、2、3……）就可以，别的格式也行。**请不要提供姓名、住院号、出生日期和具体日期**，只要年龄和持续天数即可。另外，请您确认贵单位对共享去标识数据是否有相关规定、是否需要审批。

**数据的用途。** 数据只用于本综述的合并分析。未经您的书面同意，我们不会把您提供的逐例数据转给他人，也不会以逐例的形式发表。[可选：经您同意，我们会在致谢中列出您的姓名。][可选：投稿前我们很乐意把稿件发给您过目。]

如果您能在四周内回复，对我们帮助很大。如果没有收到逐例数据，我们在综述正文中只对您的报告作叙述性描述，不纳入定量分析。如果您不是合适的联系人，或者不方便共享，也请告诉我们一声，若方便，还请告知应该联系谁。

非常感谢您抽出时间，也感谢您对这种罕见疾病所做的工作。

此致
敬礼！

[姓名]

[职称]，普外科

[单位全称（中文）]　湖北省武汉市 430016

电子邮箱：[邮箱]

代表研究团队：舒俊、杨俊、卞红强、彭飞、Ji Wang


### 4.2 第二封（第一封后 4 周）

**主题：** 再次恳请：儿童游走脾系统综述的个体患者数据（PROSPERO CRD420261520329）；[第一作者，年份]

尊敬的[姓]教授 / [姓]医生：

您好！

[第一封邮件的日期]，我们曾致信请教您能否提供[简短文献信息]中患儿的逐例数据，用于我们的儿童游走脾系统综述（PROSPERO CRD420261520329）。再次打扰，十分抱歉；我们也理解您可能工作繁忙，或者这些数据已经无法提供。

如果您可以帮忙，只需要第一封邮件里列出的内容（最重要的是术前症状持续的时间和手术时脾脏的状态），格式不限，不需要姓名、住院号和具体日期。如果您无法提供，哪怕简单回复一句，也对我们很有帮助。

如果到 [日期（从现在起 4 周）] 仍没有收到您的回复，我们在综述中将只对您的报告作叙述性描述，不纳入定量分析。

再次感谢您！

此致
敬礼！

[姓名和署名同第一封]

### 4.3 简短回复

**收到数据时：** [姓名]老师，您好！非常感谢，表格我们已经收到。我们会对照您已发表的文章核对，如有不清楚的地方再向您请教。[可选：我们整理出的数据行会发给您确认。][可选：经您同意，我们会在致谢中列出您的姓名。]

**对方不方便提供时：** [姓名]老师，您好！感谢您告知，我们理解。我们将仅根据已发表的文章对您的报告作描述。

---

## 5. 发出之后

- **登记：** 提取工作簿的 IPD_requests 表（每篇一行）：第一封和第二封的发出日期、回复日期、是否收到（Yes / No / Partial）、数据文件保存在哪里、最终状态。收到的数据文件**不放进仓库**，只记保存位置。
- **联系途径的登记（2026 年 10 月 19 日补充）：** 每次联系记一行：日期、谁联系的、用了哪条途径（论文邮箱 / 机构页面 / 编辑部转交 / 熟人转达）、结果（已送达 / 退信 / 没有回音 / 已回复）。邮箱地址本身不记；退信只记日期和原因，退信邮件不放进仓库。
- **收到数据后：** 先核对例数与文章是否一致、是否有重复患者（同一患者在别的报告里已经出现）、有没有留下识别信息；有疑问写信请教。然后按附录 C 的同样规则（含时间换算 9 条规则）由两位提取员各自独立提取。
- **最终状态：** 收到逐例数据 → 该报告 Include（全文筛选 FT_log 里的 Pending IPD 改为 Include）；到期没有 → Exclude，理由 A，在 PRISMA 图里注明"已索取，未收到个体数据"，正文做叙述性描述。
- **方法部分要写的数字：** 发出几封邮件、几位作者回复、几位提供了数据、各占多少儿童；有没有作者拒绝或表示无法提供；有几位作者各条途径都联系不上（退信、没有邮箱、没有回音），以及用过哪些途径（一句话）。这些数字要等真的发完才有，现在不能写。

## 6. 已知的两个重点系列（只看过摘要，未核对全文）

**2026 年 10 月 19 日补充：** 全文阶段之前的规划用候选清单在 `search/ipd/ipd_target_candidates.xlsx`（脚本 `tools/make_ipd_target_candidates.py`）：540 篇待取全文的报告里，预试验读过全文、没有逐例数据的 4 篇（A 层）、标题或摘要写了 3 例以上的 26 篇（B 层）、有 series/回顾等字样但没有数字的 3 篇（C 层）、综述类 3 篇（R 层）。它只用来估计这一批邮件有多少封，**不是目标清单**：目标清单要等两位全文筛选员都记 Pending IPD（理由 A）并解决分歧之后，由 `fulltext_pending_ipd.csv` 给出。下面这两个系列都在候选清单的 B 层。

下面的信息来自检索结果里的摘要和本仓库的记录，**不是**全文核对的结论。是否只有汇总数据、是否是游走脾、是否为儿童，都要在全文里确认以后才能发信（第 1 节第一条）。通讯作者的姓名和邮箱我们没有记录，要从论文里查。

| 报告 | 摘要里能看到的 | 全文要核对什么 |
|---|---|---|
| 李拴玲等，发育医学电子杂志 2024，首都医科大学附属北京儿童医院 | 2007–2024 年单中心回顾性，19 例儿童脾扭转（不含副脾扭转）；症状到就诊的间隔 1 天至 1 年；14 例脾切除、3 例保脾、2 例未手术 | 有没有逐例表；是不是游走脾（"脾扭转"没写脾脏位置时，按全文指南 D1 宽松纳入并加标记）；发表年份 2024，不受 2000 年规则影响 |
| 赵娜等，中华医学杂志 2025，天津市儿童医院 | 6 例经手术或病理证实的脾扭转，年龄 1–14 岁，有超声表现 | 同上 |

## 7. 这份草稿没有核实、没有做到的

- 没有试发给任何作者，回复率和对方的反应都不知道，不能预设。
- 没有核实 PROSPERO 的网址格式，也没有核实两份中文邮件是否合乎对方的习惯（由 Claude 起草，未经母语审校）。
- 单位的中文全称、发件人的职称和邮箱，都要您填。
- Word 文件的版面没有在 Word 里看过。
