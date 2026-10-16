"""Build the blind third-reviewer sheet for the formal title/abstract screening (14 Oct 2026).

Why: the two reviewers disagreed on 642 records (advance vs exclude) and the independence of the second reviewer's
decisions is in doubt (see CLAUDE.md, 12 and 14 Oct paragraphs). The third reviewer (Jun Yang) judges, blind to both
decisions and to why a record is in the sheet:
  1. 'conflict'      all records where one reviewer advanced (Include or Maybe) and the other excluded;
  2. 'targeted'      records both reviewers excluded that look relevant by simple word rules (a wandering/torsion word and a
                     child word in title or abstract) or have no abstract, except records both reviewers excluded as
                     non-human (E1 by both) or as not a formal article (E5 by both);
  3. 'random'        a random sample of the remaining both-excluded records (quality-control sample).
All records are shuffled into one list with a blind id; the key (blind id -> WS id, stratum, both decisions) is a separate file
that must not be given to the third reviewer.

Usage (from the repo root): python3 -I tools/make_blind_adjudication_sheet.py [FOLDER]
  FOLDER defaults to search/screening/formal/ (first round); after the re-screen use the folder written by tools/compare_rescreen.py
Reads  search/screening/formal/screening_results_all.csv and search/dedup/records_deduplicated.ris
Writes search/screening/formal/blind_adjudication_sheet.xlsx   (for the third reviewer)
       search/screening/formal/blind_adjudication_key.csv      (NOT for the third reviewer)
       search/screening/formal/blind_adjudication_design.txt   (sizes, seed, pre-specified triggers)
Needs openpyxl.
"""
import csv, random, re, collections, sys
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation

SEED = 20261014
N_RANDOM = 60
F = sys.argv[1].rstrip('/') + '/' if len(sys.argv) > 1 else 'search/screening/formal/'   # folder with screening_results_all.csv; outputs go there too

res = list(csv.DictReader(open(F + 'screening_results_all.csv', encoding='utf-8-sig')))
body, title, abstract = {}, {}, {}
for blk in open('search/dedup/records_deduplicated.ris', encoding='utf-8-sig').read().split('\nER  -'):
    m = re.search(r'^ID  - (.*)$', blk, re.M)
    if not m:
        continue
    ti = ' '.join(re.findall(r'^TI  - (.*)$', blk, re.M))
    ab = ' '.join(re.findall(r'^AB  - (.*)$', blk, re.M)).strip()
    title[m.group(1)], abstract[m.group(1)], body[m.group(1)] = ti, ab, ti + ' ' + ab

WS_RE = re.compile(r'wander|floating spleen|ptosic|ptotic|splenoptosis|ectopic spleen|pelvic spleen|migrat|torsion|twist|volvulus|游走脾|游动脾|漂浮脾|脾下垂|脾蒂|扭转|异位脾', re.I)
CHILD_RE = re.compile(r'child|pediatric|paediatric|infant|neonat|newborn|toddler|\bboy\b|\bgirl\b|adolescen|儿童|小儿|患儿|婴|幼儿|新生儿|少儿|\b(?:[0-9]|1[0-7])[- ]?(?:year|yr|month|week|day)s?[- ]?old|\b(?:[0-9]|1[0-7])岁|(?:[0-9]|1[0-7])个月', re.I)


def adv(d):
    return d in ('Include', 'Maybe')


conflict, agreed = [], []
for r in res:
    a1, a2 = adv(r['R1_JunShu_decision']), adv(r['R2_FeiPeng_decision'])
    if a1 != a2:
        conflict.append(r)
    elif not a1 and not a2:
        agreed.append(r)


def both_have(r, code):
    return code in r['R1_JunShu_reason'] and code in r['R2_FeiPeng_reason']


clear = [r for r in agreed if both_have(r, 'E1') or both_have(r, 'E5')]
pool = [r for r in agreed if r not in clear]
flagged = [r for r in pool if WS_RE.search(body[r['ws_id']]) and CHILD_RE.search(body[r['ws_id']])]
fl_ids = {r['ws_id'] for r in flagged}
noabs = [r for r in pool if r['ws_id'] not in fl_ids and not abstract[r['ws_id']]]
na_ids = {r['ws_id'] for r in noabs}
rest = [r for r in pool if r['ws_id'] not in fl_ids and r['ws_id'] not in na_ids]
rng = random.Random(SEED)
sample = rng.sample(rest, N_RANDOM)

rows = [(r, 'conflict') for r in conflict] + [(r, 'targeted_flag') for r in flagged] + [(r, 'targeted_noabstract') for r in noabs] + [(r, 'random_qc') for r in sample]
rng.shuffle(rows)
n = len(rows)

# ------------------------------------------------------------------ key (not for the third reviewer)
with open(F + 'blind_adjudication_key.csv', 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f)
    w.writerow(['blind_id', 'ws_id', 'stratum', 'R1_decision', 'R1_reason', 'R2_decision', 'R2_reason'])
    for i, (r, s) in enumerate(rows, start=1):
        w.writerow([f'B{i:04d}', r['ws_id'], s, r['R1_JunShu_decision'], r['R1_JunShu_reason'], r['R2_FeiPeng_decision'], r['R2_FeiPeng_reason']])

# ------------------------------------------------------------------ sheet for the third reviewer
wb = Workbook()
ws0 = wb.active
ws0.title = '说明'
lines = [
    ('t', '第三位评审：标题摘要盲评表（儿童游走脾系统综述，PROSPERO CRD420261520329）'),
    ('p', f'本表共 {n} 条记录，已随机排序。表里没有任何人的决定，也没有说明为什么某条记录在这张表里。请逐条独立判断，不要向舒俊或彭飞询问，也不要去看他们的决定。'),
    ('h', '一、怎么判断（完整规则见《筛选指南（标题和摘要）》；下面是摘要）'),
    ('b', '只依据标题和摘要判断，不要上网查全文或作者信息，也不要用任何 AI 工具或翻译工具辅助决定（协议写明不使用 AI）。'),
    ('b', '三种决定：Include（明确符合）、Maybe（拿不准，进入全文再看）、Exclude（明确不符合）。Include 和 Maybe 都进入全文。拿不准就选 Maybe。'),
    ('b', '纳入条件：游走（异位、可移动）脾，伴或不伴脾蒂扭转，先天性或获得性都符合；患者小于 18 岁；病例报告、病例系列、队列研究，或描述了原始患者的信件和综述。摘要里看不出年龄或是否有个体数据时，不要因此排除，选 Maybe。'),
    ('b', 'Exclude 必须同时在"理由"列选一个固定理由；说不出适用哪一条，就不要 Exclude，改选 Maybe。理由只有这六个：E1 non-human（动物、兽医、实验）；E2 not wandering spleen（副脾含游走副脾、脾种植、正常位置脾脏扭转、脾异位妊娠、移植脾、保脾手术等）；E3 adults only（全部患者 ≥18 岁）；E4 no original patient data（无新病例的综述、社论、评论）；E5 not a formal article（只有摘要的会议报告、专利、报纸）；E6 other（在备注写一句具体说明）。一条记录符合两条理由时任选一条。'),
    ('b', '没有摘要的记录（摘要栏写"（无摘要）"）：只选 Maybe 或 Exclude，不选 Include；只有标题明确符合某条理由时才 Exclude，其他选 Maybe。'),
    ('b', '"脾扭转""异位脾"没有说明脾脏位置是否正常、患者是否成人时，选 Maybe。'),
    ('h', '二、怎么填'),
    ('b', '在"判断"表里，每条记录填"决定"（下拉选择）和需要时的"理由"（下拉选择）；备注可写一句话，也可留空。请按表里的顺序做，不要漏行。'),
    ('b', '请在"时间日志"表里记录每次开始和结束的时间以及做到第几条；这是为了在方法部分说明评审用时。'),
    ('b', '做完后把整个文件发给舒俊（不要改列名、不要删行）。'),
]
ws0.column_dimensions['A'].width = 130
for i, (k, t) in enumerate(lines, start=1):
    c = ws0.cell(row=i, column=1, value=('• ' + t) if k == 'b' else t)
    c.alignment = Alignment(wrap_text=True, vertical='top')
    if k == 't':
        c.font = Font(bold=True, size=14)
    elif k == 'h':
        c.font = Font(bold=True, color='FFFFFF')
        c.fill = PatternFill('solid', fgColor='2F75B5')

ws1 = wb.create_sheet('判断')
heads = ['blind_id', '年份', '语种', '标题', '摘要', '决定', '理由', '备注']
widths = [9, 7, 7, 46, 100, 11, 26, 30]
for j, (h, w_) in enumerate(zip(heads, widths), start=1):
    c = ws1.cell(row=1, column=j, value=h)
    c.font = Font(bold=True, color='FFFFFF')
    c.fill = PatternFill('solid', fgColor='2F75B5')
    ws1.column_dimensions[chr(64 + j)].width = w_
for i, (r, s) in enumerate(rows, start=2):
    ab = abstract[r['ws_id']] or '（无摘要）'
    vals = [f'B{i - 1:04d}', r['year'] or '', r['language'][:3], title[r['ws_id']], ab, None, None, None]
    for j, v in enumerate(vals, start=1):
        c = ws1.cell(row=i, column=j, value=v)
        c.alignment = Alignment(wrap_text=True, vertical='top')
ws1.freeze_panes = 'D2'
dv1 = DataValidation(type='list', formula1='"Include,Maybe,Exclude"', allow_blank=True)
dv2 = DataValidation(type='list', formula1='"E1 non-human,E2 not wandering spleen,E3 adults only,E4 no original patient data,E5 not a formal article,E6 other"', allow_blank=True)
ws1.add_data_validation(dv1)
ws1.add_data_validation(dv2)
dv1.add(f'F2:F{n + 1}')
dv2.add(f'G2:G{n + 1}')

ws2 = wb.create_sheet('时间日志')
for j, (h, w_) in enumerate(zip(['日期', '开始时间', '结束时间', '从第几条（blind_id）', '到第几条', '本次完成条数', '备注'], [12, 11, 11, 20, 12, 14, 30]), start=1):
    c = ws2.cell(row=1, column=j, value=h)
    c.font = Font(bold=True)
    ws2.column_dimensions[chr(64 + j)].width = w_
wb.properties.title = 'Blind adjudication sheet'
wb.save(F + 'blind_adjudication_sheet.xlsx')

# ------------------------------------------------------------------ design note
cnt = collections.Counter(s for _, s in rows)
with open(F + 'blind_adjudication_design.txt', 'w', encoding='utf-8') as f:
    f.write(f'''Blind third-reviewer sheet, built 14 Oct 2026 by tools/make_blind_adjudication_sheet.py (random seed {SEED}).
Records in the sheet: {n}
  conflict (advance vs exclude)                         {cnt['conflict']}
  targeted: both excluded, word-flagged                 {cnt['targeted_flag']}   (wandering/torsion word AND child word in title/abstract)
  targeted: both excluded, no abstract, not flagged     {cnt['targeted_noabstract']}
  random QC sample of the other both-excluded records   {cnt['random_qc']}   (from {len(rest)} records)
Both-excluded records in total: {len(agreed)}; left out as clear by type (both reviewers gave E1, or both gave E5): {len(clear)}.

Pre-specified triggers (fixed before the third reviewer starts):
  1. If the third reviewer advances (Include or Maybe) more than 10% of the targeted records ({cnt['targeted_flag'] + cnt['targeted_noabstract']}), or
  2. advances 2 or more of the {N_RANDOM} random QC records,
  then he also judges ALL remaining both-excluded records with reason E2 or E3 from either reviewer (list written by tools/blind_adjudication_analysis.py).
Final list for full text = records both reviewers advanced + conflicts the third reviewer advanced + QC records the third reviewer advanced.
The key file (blind_adjudication_key.csv) must not be given to the third reviewer.
''')
print('sheet rows', n, dict(cnt), '| both-excluded', len(agreed), 'clear', len(clear), 'pool', len(pool), 'flagged', len(flagged), 'noabs', len(noabs), 'rest', len(rest))
