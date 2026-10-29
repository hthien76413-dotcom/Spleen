# 给杨俊的说明：提取第三轮裁定（2026-10-29）

## 你拿到的两个文件

1. `merged_23rows_with_both_rereads_2026-10-29.csv`（23 行）：两位提取员对仍有分歧的 23 例各自复读原文后的记录（页码和原文摘录、复读结果、所用规则），并排放在一起。
2. `E1_declined_rows_for_adjudicator_2026-10-26.csv`（5 行）：第二轮裁定后，舒俊（E1）认为原文不支持裁定值、没有修改的 5 例，附他的理由。

两个文件含两位提取员的逐例数值，仅限你和两位提取员使用。请用 Excel 或 WPS 打开，另存为新文件，不要覆盖原件。

## 你要做什么

### 文件 1（23 行）
每行只填最后几列：
- `adjudicator_ruling`：你的裁定理由，写明依据的规则编号（X13–X27）和原文页码。
- `final_idx_dur_days`：最终天数，数字或 NR。
- `final_viability`：Viable / Partially non-viable / Non-viable / Not applicable / NR。
- `final_viab_basis`：Intraoperative / Histology / Both / NR。

两人读数已一致的行（23 行中有 19 行天数和活力一致），请至少核对原文确认一次，再填最终值。

需要你先定的 4 行：
- **WS0049_P5、P6**：E1 填 Non-viable（依据 Both），E2 填 NR。个体表在在线附录，本地未获取。请裁定：正文对 6 例的汇总句，以及图注里个别例的描述，能否算 X13 的“直接描述”。
- **WS0277_P1**：原文术中和病理都写“areas of infarction”。E1 按字面判 Partially non-viable，E2 判 Non-viable。请按 X23 裁定。
- **WS0493_P1**：E1 以后来切除脾的病理为准（Partially non-viable），E2 取首次开腹保脾的情形（Viable）。两人读的可能是不同手术。请先定以哪次手术为准，再填活力。

另外两项请你看全表，我没有比较：`viab_basis`（Both 与 Intraoperative/Histology 的差别，涉及 WS0642、WS0789、WS2041、WS2138）和 `lower_bound`（WS2044、WS2093）。WS0706_P1 一人填了时长类别，另一人没有。WS0771_P1 E2 多填了 intermittent=Yes。

### 文件 2（5 行）
填 `adjudicator_ruling` 和 `final_value`。五例的 E1 理由都写在 `note` 列，请对照原文裁定：
- WS0141_P1：E1 认为原文写腹痛 2～3 小时，可编码 0.1 天，不支持 NR。
- WS0734_P1：E1 认为原文只写 2 天，没有 7 天的依据。
- WS2032_P1、WS2484_P1、WS2093_P1：理由见各行 `note`。

## 注意
- 每条裁定请写依据；不要只写数值。
- 第二轮的 `discussion_conclusion` 当时是你裁定的复制，没有记录两位提取员的讨论。这一轮如果两人当面讨论过，请在裁定理由里注明。
- 填完后原样发回（CSV 或 xlsx 均可），我据此更新两份提取表，再跑检查和比对。
