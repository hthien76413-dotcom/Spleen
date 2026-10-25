# 个体患者数据（IPD）索取邮件：第一批 5 篇（草稿）

项目：儿童游走脾系统综述（PROSPERO CRD420261520329）。草稿日期：2026 年 10 月 25 日。

状态：**草稿，一封都没有发出。** 方括号 [ ] 里的内容发送前要填。邮件的结构、索取的变量、隐私和数据用途的写法，沿用《IPD 索取邮件（草稿）》（以下简称"总稿"）第 3、4 节，这里只按这 5 篇各自的情况改写；第二封（4 周后）用总稿第 3.2 / 4.2 节，这里只给出要填的信息（第 4 节）。

依据：全文筛选最终名单里 5 篇记为 Pending IPD（理由 A）：WS0527、WS0616、WS1961、WS2033、WS2443（2026 年 10 月 25 日 `finalize_fulltext.py` 的结果）。其中 WS0616、WS1961、WS2443 两位筛选员一致；WS0527、WS2033 两位意见不同，由杨俊裁定为 Pending IPD。

邮件里没有任何患者信息。英文邮件和中文邮件都由 Claude 起草，没有经过母语审校。通讯作者的姓名和邮箱我们没有记录，要从论文里查（总稿第 1 节：不要猜，邮箱不写进仓库）。

---

## 1. 这 5 篇一览

<!-- widths: 11,17,30,42 -->
| 报告 | 发给谁 / 语言 | 摘要和筛选记录里能看到的 | 发信前要在全文里核对的 |
|---|---|---|---|
| WS0616　Rescorla 等，Ann Surg 2007;246(4):683-7 | 通讯作者（从论文查）；英文 | 1995–2006 年单中心 231 例儿童腹腔镜脾手术，其中 2 例因游走脾做了脾固定术；这 2 例只在汇总里，没有各自的年龄、表现、所见和结局 | 通讯作者和邮箱；确认是 2 例；确认没有线上附录 |
| WS0527　Garrett 等，J Laparoendosc Adv Surg Tech A 2011;21(10):965-7 | 通讯作者（从论文查）；英文 | 加州 Miller Children's Hospital，2009–2010 年 7 例儿童单孔腹腔镜脾手术，其中 1 例"脾扭转复位 + 脾固定术"，没有这一例的个体资料 | **两位筛选员对这一例是不是游走脾意见不同**（一位读全文认为没有游走脾，一位认为是 1 例脾扭转脾固定），所以邮件先问这一点；通讯作者和邮箱 |
| WS1961　王春喜等，中国现代手术学杂志 2015;19(4):246-50 | 通讯作者（通信作者栏）；中文，与 WS2443 合并成一封 | 1993–2013 年 11 例游走脾（腹腔内 7、盆腔 4），均脾切除，术中均见脾蒂扭转；年龄 15–35 岁、平均 23 岁；随访 2–15 年，1 例术后 2 年死于肺动脉栓塞；**没有 18 岁以下的人数** | 通讯作者和邮箱；医院全称；年龄是否真的没有逐例；两篇是否重叠 |
| WS2443　王春喜等，中国中西医结合外科杂志 2016;22(2):168-71 | 同上 | 15 例异位脾（腹腔 8、盆腔 5、腹膜后 2），均脾切除；年龄 17–35 岁、平均 29 岁；随访 1–19 年，1 例术后 2 年死于肺栓塞；**没有 18 岁以下的人数** | 同上；腹膜后的 2 例是否算游走脾 |
| WS2033　廖桦、方志红，中国实用医药 2009;4(36):63-64 | 通讯作者（通信作者栏）；中文 | 2001–2008 年脾切除手术回顾（题目 150 例）；适应证里有游走脾；筛选记录写的是游走脾 3 例（蒂扭转坏死），脾切除系列平均 40 岁，没有逐例年龄 | **例数对不上**：题目写 150 例，筛选记录写 133 例；医院全称；游走脾确是 3 例；谁能证实有无 18 岁以下 |

提醒三点：

- **WS1961 和 WS2443 很可能是同一课题组的重叠病例**：作者相同，两篇都有一例"术后 2 年死于肺动脉栓塞"。但年龄范围不同（15–35 对 17–35），不一定是包含关系，所以邮件里请对方说明重叠情况。合并成一封信，在 IPD_requests 表里仍然每篇一行。
- **两位筛选员对 WS1961、WS2443 的汇总儿童数填的不一样**（舒俊填全部病例数 11 和 15，卞红强填 18 岁以下的最小人数 1），而现在谁也不知道 18 岁以下有几个，所以邮件里不写"儿童几例"，改成请对方告知。发信前在 IPD_requests 表里要先定一个统一的写法（下面第 5 节）。
- **WS2033 的 Pending IPD 靠舒俊一个人的记录**：卞红强这篇没取到全文，裁定是杨俊根据舒俊的记录做的。发信前请舒俊打开这篇全文，核对例数、医院和通讯作者。

---

## 2. 发送前共同要做的

按总稿第 1 节：确认通讯作者邮箱来自论文或机构网页（不猜）；一次性在同一天发出所有第一封；发出当天在 IPD_requests 表登记日期；4 周后发第二封；从第一封算起最长 8 周。**不要附任何东西。** 发件人建议舒俊，抄送杨俊（总稿 O3 还没有确认）。

数据用途一栏已按 O1 的决定写好：作者提供的个体数据只用于合并分析，不逐例公开，经原作者书面同意才给他人。

---

## 3. 第一封邮件（4 封）

### 3.1 WS0616：Rescorla 等 2007（英文）

**Subject:** Request for individual patient data: systematic review of wandering spleen in children (PROSPERO CRD420261520329); Rescorla 2007

Dear [Professor / Dr] [surname of the corresponding author],

I am writing on behalf of a research team at [full name of institution], Wuhan, China. We are conducting a systematic review of children with wandering spleen, using individual patient data, registered on PROSPERO (CRD420261520329). The main question is whether the length of the symptomatic episode before operation is associated with the state of the spleen at operation (viable or non-viable).

We read your report: Rescorla FJ, West KW, Engum SA, Grosfeld JL. Laparoscopic splenic procedures in children: experience in 231 children. Ann Surg. 2007;246(4):683-7 (doi:10.1097/sla.0b013e318155abb9). It describes 231 children who had laparoscopic splenic procedures between 1995 and 2006, including two who had a splenopexy for wandering spleen. In the published article these two children appear only in the group totals, and we could not find their ages, presentation, findings or outcomes separately. We would be very grateful if you could share de-identified, child-level data for these two children.

**What we are asking for.** Only what is in your records, and only for these two children. Please leave blank anything you do not have. The most important items are the duration of symptoms before operation and the state of the spleen at operation.

- **Child:** age at operation (years, or months for infants); sex; associated conditions (for example gastric volvulus, diaphragmatic hernia or eventration, absent or ectopic kidney, previous abdominal surgery, syndrome); congenital or acquired.
- **Timeline:** type of presentation (acute / chronic or intermittent / acute on chronic / asymptomatic); duration of the symptoms that led to this operation, in days; total length of the symptom history; number of earlier episodes; whether the diagnosis was missed at an earlier visit; whether the diagnosis was known and the operation was deferred (and why).
- **Investigations:** imaging used (ultrasound, Doppler, CT, MRI); whirl sign; splenic perfusion; preoperative platelet count.
- **Operation:** approach; torsion at operation (and degrees); splenic viability (viable / partly non-viable / non-viable) and whether this was judged at operation or on histology; procedure (detorsion, splenopexy, partial or total splenectomy); fixation technique; spleen size; reason for removing a spleen that was still viable.
- **Follow-up:** length of follow-up; recurrence or re-torsion; further surgery; splenic status at last follow-up; complications after splenectomy.

**Format and privacy.** A simple Excel or Word table with one row per child (Patient 1, 2) is perfect; any other format is fine too. **Please do not send names, hospital numbers, dates of birth or exact dates.** Ages and durations are enough. Please also check whether your institution requires any permission before de-identified data are shared.

**How we will use the data.** The data will be used only for the pooled analysis in this review. We will not pass your child-level data to anyone else or publish them at child level without your written permission. [Optional: With your permission, we would name you in the Acknowledgements.] [Optional: We would be glad to send you the draft before submission.]

If you could reply within four weeks, that would help us a great deal. If we do not receive child-level data, we will describe your report in the text of the review only and will not include it in the quantitative analysis. If you are not the right person to ask, or prefer not to share, please let us know and, if possible, tell us whom to contact.

Thank you very much for your time and for your work on this rare condition.

With kind regards,

[Name]

[Position], Department of General Surgery

[Full name of institution], Wuhan 430016, Hubei, China

E-mail: [address]

On behalf of the review team: Jun Shu, Jun Yang, Hongqiang Bian, Fei Peng, Ji Wang

### 3.2 WS0527：Garrett 等 2011（英文）

**Subject:** Request for individual patient data: systematic review of wandering spleen in children (PROSPERO CRD420261520329); Garrett 2011

Dear [Professor / Dr] [surname of the corresponding author],

I am writing on behalf of a research team at [full name of institution], Wuhan, China. We are conducting a systematic review of children with wandering spleen, using individual patient data, registered on PROSPERO (CRD420261520329). The main question is whether the length of the symptomatic episode before operation is associated with the state of the spleen at operation (viable or non-viable).

We read your report: Garrett D, Emami C, Anselmo DM, Torres MB, Nguyen N. Single-incision laparoscopic approach to management of splenic pathology in children: an early experience. J Laparoendosc Adv Surg Tech A. 2011;21(10):965-7 (doi:10.1089/lap.2011.0148). It describes seven children operated on at Miller Children's Hospital between January 2009 and December 2010, one of whom had reduction of a splenic torsion and splenopexy. From the published article we could not find the findings for this child separately. We would be very grateful if you could tell us about this child and, if possible, share de-identified, child-level data.

**First, one question.** Was the spleen of this child in an abnormal position or abnormally mobile (a wandering spleen), or was the torsion of a spleen in its usual position? Our review includes only children with a wandering spleen, so your answer tells us whether this child belongs in it.

**If the child had a wandering spleen, what we are asking for.** Only what is in your records, and only for this child. Please leave blank anything you do not have. The most important items are the duration of symptoms before operation and the state of the spleen at operation.

- **Child:** age at operation (years, or months for infants); sex; associated conditions (for example gastric volvulus, diaphragmatic hernia or eventration, absent or ectopic kidney, previous abdominal surgery, syndrome); congenital or acquired.
- **Timeline:** type of presentation (acute / chronic or intermittent / acute on chronic / asymptomatic); duration of the symptoms that led to this operation, in days; total length of the symptom history; number of earlier episodes; whether the diagnosis was missed at an earlier visit; whether the diagnosis was known and the operation was deferred (and why).
- **Investigations:** imaging used (ultrasound, Doppler, CT, MRI); whirl sign; splenic perfusion; preoperative platelet count.
- **Operation:** approach; torsion at operation (and degrees); splenic viability (viable / partly non-viable / non-viable) and whether this was judged at operation or on histology; procedure (detorsion, splenopexy, partial or total splenectomy); fixation technique; spleen size; reason for removing a spleen that was still viable.
- **Follow-up:** length of follow-up; recurrence or re-torsion; further surgery; splenic status at last follow-up; complications after splenectomy.

**Format and privacy.** A short reply or a simple table is perfect; any other format is fine too. **Please do not send names, hospital numbers, dates of birth or exact dates.** Ages and durations are enough. Please also check whether your institution requires any permission before de-identified data are shared.

**How we will use the data.** The data will be used only for the pooled analysis in this review. We will not pass your child-level data to anyone else or publish them at child level without your written permission. [Optional: With your permission, we would name you in the Acknowledgements.] [Optional: We would be glad to send you the draft before submission.]

If you could reply within four weeks, that would help us a great deal. If we do not receive child-level data, we will describe your report in the text of the review only and will not include it in the quantitative analysis. If you are not the right person to ask, or prefer not to share, please let us know and, if possible, tell us whom to contact.

Thank you very much for your time and for your work.

With kind regards,

[Name]

[Position], Department of General Surgery

[Full name of institution], Wuhan 430016, Hubei, China

E-mail: [address]

On behalf of the review team: Jun Shu, Jun Yang, Hongqiang Bian, Fei Peng, Ji Wang

### 3.3 WS1961 + WS2443：王春喜等 2015、2016（中文，一封信）

**主题：** 恳请提供个体患者数据：儿童游走脾系统综述（PROSPERO CRD420261520329）；王春喜等 2015、2016

尊敬的[姓]教授 / [姓]医生：

您好！

我们是[单位全称（中文）]的研究团队，正在做一项关于儿童游走脾的系统综述，需要用到患者个体层面的数据，该综述已在 PROSPERO 注册（注册号 CRD420261520329）。我们主要想了解：术前症状持续的时间，与手术时脾脏的状态（是否已经坏死）是否相关。

我们读到了您课题组的两篇论文：

1. 王春喜，陈婧如，宋清彬，王琦，张勇，牛磊．游走性脾脏并扭转的手术治疗．中国现代手术学杂志，2015，19(4)：246-250（DOI：10.16260/j.cnki.1009-2188.2015.04.002）。文中报告了 1993 年 1 月至 2013 年 1 月收治的 11 例游走性脾脏，年龄 15–35 岁，平均 23 岁。
2. 王春喜，李忠明，夏绍友，陈婧如，宋清斌，牛磊．15 例异位脾脏的诊断和外科治疗．中国中西医结合外科杂志，2016，22(2)：168-171。文中报告了 15 例异位脾脏，年龄 17–35 岁，平均 29 岁。

我们的综述只纳入手术时**不满 18 岁**的患儿。两篇文章里只有汇总的年龄，没有逐例的年龄和结果，所以我们没办法判断其中有没有、有几例不满 18 岁的患儿。想请教您三件事：

- **一、不满 18 岁的患者：** 两篇文章里，手术时不满 18 岁的患者各有几例？
- **二、两篇的病例是否重叠：** 两篇文章里的病例（例如两篇都提到的"术后 2 年死于肺动脉栓塞"的一例）是不是有一部分是同一批患者？
- **三、逐例数据：** 如果有不满 18 岁的患者，恳请您提供这些患儿**去标识的、逐例的数据**。

**我们需要的内容。** 只要病历里有的，并且只限不满 18 岁的患儿；没有的请留空。**最重要的两项是：手术前症状持续的时间，以及手术时脾脏的状态。**

- **患儿情况：** 手术时年龄（岁；婴儿用月）；性别；伴随疾病（如胃扭转、膈疝或膈膨升、肾缺如或异位、既往腹部手术、综合征等）；先天性还是后天性。
- **病程：** 就诊表现（急性 / 慢性或间歇性 / 慢性急性发作 / 无症状）；导致本次手术的症状持续了多少天；症状总病史多长；之前发作过几次；之前就诊时是否漏诊；诊断明确后手术是否被推迟（原因）。
- **检查：** 影像检查方式（超声、多普勒超声、CT、MRI）；有无漩涡征；脾脏血流灌注情况；术前血小板计数。
- **手术：** 手术方式（开放 / 腹腔镜 / 中转）；脾脏所在的位置（腹腔内 / 盆腔 / 腹膜后），脾蒂是否过长；术中扭转情况（圈数或度数）；脾脏活力（存活 / 部分坏死 / 完全坏死），是术中判断还是病理判断；术式（单纯复位、脾固定术、部分脾切除、全脾切除）；固定方法；脾脏大小；脾脏仍有活力却被切除的原因。
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

### 3.4 WS2033：廖桦、方志红 2009（中文）

**主题：** 恳请提供个体患者数据：儿童游走脾系统综述（PROSPERO CRD420261520329）；廖桦、方志红 2009

尊敬的[姓]教授 / [姓]医生：

您好！

我们是[单位全称（中文）]的研究团队，正在做一项关于儿童游走脾的系统综述，需要用到患者个体层面的数据，该综述已在 PROSPERO 注册（注册号 CRD420261520329）。我们主要想了解：术前症状持续的时间，与手术时脾脏的状态（是否已经坏死）是否相关。

我们读到了您的论文：廖桦，方志红．150 例脾切除手术回顾性分析．中国实用医药，2009，4(36)：63-64（DOI：10.3969/j.issn.1673-7555.2009.36.037）。文中汇总了贵院 2001 年 7 月至 2008 年 7 月的脾切除手术 [150 / 133：请按全文核对] 例，其中包括游走脾 [3：请按全文核对] 例。文章里没有这些游走脾患者各自的年龄和结果，所以我们没办法判断其中有没有手术时**不满 18 岁**的患儿。

我们想请教两件事：

- **一、年龄：** 这 [3] 例游走脾患者手术时各是多大？其中有没有不满 18 岁的？
- **二、逐例数据：** 如果有不满 18 岁的患儿，恳请您提供这些患儿**去标识的、逐例的数据**。如果没有，只要告诉我们一声就可以，我们就不再打扰了。

**我们需要的内容。** 只要病历里有的，并且只限不满 18 岁的游走脾患儿；没有的请留空。**最重要的两项是：手术前症状持续的时间，以及手术时脾脏的状态。**

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

---

## 4. 第二封（4 周后）要填的信息

用总稿第 3.2 节（英文）或第 4.2 节（中文）的正文，只换下面的内容。方括号里的日期按实际发出日填。

<!-- widths: 12,40,48 -->
| 报告 | 主题行里的第一作者和年份 | "简短文献信息"（正文里填） |
|---|---|---|
| WS0616 | Rescorla 2007 | Rescorla et al., Ann Surg 2007;246:683-7 |
| WS0527 | Garrett 2011 | Garrett et al., J Laparoendosc Adv Surg Tech A 2011;21:965-7 |
| WS1961 + WS2443 | 王春喜等 2015、2016 | 王春喜等，中国现代手术学杂志 2015；中国中西医结合外科杂志 2016（两篇） |
| WS2033 | 廖桦、方志红 2009 | 廖桦、方志红，中国实用医药 2009;4(36):63-64 |

---

## 5. 发出后在 IPD_requests 表登记的内容

每篇一行。第一封发出当天填 `email1_date`、`delivery_result`；通讯作者只填姓名，邮箱不写；联系途径按总稿第 5 节登记。

<!-- widths: 10,24,22,44 -->
| ws_id | citation | n_children_aggregate | 说明 |
|---|---|---|---|
| WS0616 | Rescorla 2007 | 2 | 两位筛选员一致 |
| WS0527 | Garrett 2011 | 1 | 筛选员对这一例是不是游走脾意见不同，先问清楚（见邮件 3.2） |
| WS1961 | 王春喜 2015 | **先定** | 舒俊填 11（全部病例），卞红强填 1（18 岁以下的最小人数）；现在 18 岁以下人数未知。建议在 `notes` 写明"18 岁以下人数待作者回复"，数字等回复后再填 |
| WS2443 | 王春喜 2016 | **先定** | 同上，舒俊填 15，卞红强填 1；与 WS1961 在 `duplicate_of` 里互相链接 |
| WS2033 | 廖桦 2009 | 3 | 游走脾 3 例，年龄未知 |

---

## 6. 没有核实、没有做到的

- 5 篇的通讯作者、邮箱和医院全称，我们都没有；中文论文的医院名称检索记录里没有。
- WS2033 的例数（150 对 133）和游走脾 3 例是舒俊的筛选记录，没有核对全文；WS1961、WS2443 的年龄范围和病例数来自摘要和两位筛选员的记录。
- 没有试发给任何作者，回复率和对方的反应不知道。
- 中文邮件没有经母语审校，称呼和措辞请按您的习惯改。
- Word 文件的版面没有在 Word 里看过。
