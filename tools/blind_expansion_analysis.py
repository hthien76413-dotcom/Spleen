"""Analyse the third reviewer's judgements on the second (expansion) blind sheet and write the final full-text list.

Usage (from the repo root): python3 -I tools/blind_expansion_analysis.py FILLED.xlsx [FOLDER]    (FOLDER default search/screening/rescreen/)
Reads  FILLED.xlsx (sheet '判断': blind_id, 决定, 理由, 备注), FOLDER/blind_expansion_key.csv, FOLDER/fulltext_list_after_adjudication.csv
Writes FOLDER/blind_expansion_decisions.csv, FOLDER/blind_expansion_summary.txt, FOLDER/fulltext_list_final.csv
Final list = the list after the first adjudication + expansion records the third reviewer advanced (Include or Maybe).
"""
import csv, math, sys, collections
from openpyxl import load_workbook

filled = sys.argv[1]
F = sys.argv[2].rstrip('/') + '/' if len(sys.argv) > 2 else 'search/screening/rescreen/'
ADV = ('Include', 'Maybe')
key = {r['blind_id']: r for r in csv.DictReader(open(F + 'blind_expansion_key.csv', encoding='utf-8-sig'))}
ws = load_workbook(filled, data_only=True)['判断']
dec, problems = {}, []
for row in ws.iter_rows(min_row=2, values_only=True):
    bid, d, why, note = row[0], row[5], row[6], row[7]
    if bid not in key:
        problems.append(f'unknown blind id {bid}')
        continue
    if d not in ('Include', 'Maybe', 'Exclude'):
        problems.append(f'{bid}: missing or invalid decision {d!r}')
        continue
    if d == 'Exclude' and not why:
        problems.append(f'{bid}: Exclude without a reason')
    dec[bid] = (d, why or '', note or '')
missing = [b for b in key if b not in dec]
for b in missing:
    problems.append(f'{b}: no usable judgement')
with open(F + 'blind_expansion_decisions.csv', 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f)
    w.writerow(['blind_id', 'ws_id', 'R1_decision', 'R1_reason', 'R2_decision', 'R2_reason', 'JY_decision', 'JY_reason', 'JY_note'])
    for b, k in key.items():
        d = dec.get(b, ('', '', ''))
        w.writerow([b, k['ws_id'], k['R1_decision'], k['R1_reason'], k['R2_decision'], k['R2_reason'], *d])
n = len(key)
adv = [b for b in key if dec.get(b, ('',))[0] in ADV]
cnt = collections.Counter(dec[b][0] for b in dec)
base = list(csv.DictReader(open(F + 'fulltext_list_after_adjudication.csv', encoding='utf-8-sig')))
have = {r['ws_id'] for r in base}
dup = [b for b in adv if key[b]['ws_id'] in have]
new = [b for b in adv if key[b]['ws_id'] not in have]
res = {r['ws_id']: r for r in csv.DictReader(open(F + 'screening_results_all.csv', encoding='utf-8-sig'))}
with open(F + 'fulltext_list_final.csv', 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f)
    w.writerow(['ws_id', 'year', 'title', 'language', 'source'])
    for r in base:
        w.writerow([r['ws_id'], r['year'], r['title'], r['language'], r['source']])
    for b in new:
        r = res[key[b]['ws_id']]
        w.writerow([r['ws_id'], r['year'], r['title'], r['language'], 'both excluded (E2/E3), third reviewer advanced in the expansion sheet'])
p = len(adv) / n if n else float('nan')
with open(F + 'blind_expansion_summary.txt', 'w', encoding='utf-8') as f:
    f.write(f'Expansion sheet: {n} records; usable judgements {len(dec)}; problems {len(problems)}\n')
    for x in problems[:30]:
        f.write('  ' + x + '\n')
    f.write(f'Third reviewer decisions: {dict(cnt)}\n')
    f.write(f'Advanced to full text: {len(adv)} of {n} ({100 * p:.1f}%); already on the list: {len(dup)}; added: {len(new)}\n')
    f.write(f'Final full-text list: {len(base) + len(new)} records (before the list after the first adjudication: {len(base)})\n')
print(open(F + 'blind_expansion_summary.txt', encoding='utf-8').read())
