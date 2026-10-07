"""Compare two reviewers' Rayyan decisions and prepare the adjudication list.

Inputs (from Rayyan: Review data > "..." > Review settings > Export, CSV with
decisions, exclusion reasons, labels and notes; the export gives two files):
  articles.csv            one row per record; the `notes` field carries
                          RAYYAN-INCLUSION: {"<name1>"=>"Included|Maybe|Excluded", ...}
  customizations_log.csv  event log (per-user decisions and exclusion reasons)
  records_deduplicated.ris  the file that was imported into Rayyan (WS ids)

Usage:
  python3 -I tools/screening_conflicts.py ARTICLES_CSV LOG_CSV RIS OUT_DIR \
      --name1 俊 --name2 Fei [--label1 R1_JunShu --label2 R2_FeiPeng]

--name1/--name2 are the display names Rayyan prints in RAYYAN-INCLUSION.
The log's e-mail addresses are only used in memory to tell the two users apart;
no e-mail address or Rayyan user id is written to any output file.

Outputs in OUT_DIR:
  screening_results_all.csv                one row per record
  screening_conflicts_for_adjudication.csv records where one reviewer excluded and the other did not
  screening_include_vs_maybe.csv           records where both advance but differ (reported, not adjudicated)
  screening_summary.txt                    counts, agreement, kappa, data-quality flags
"""
import argparse
import csv
import re
import sys
from collections import Counter, defaultdict

csv.field_size_limit(10 ** 9)

ap = argparse.ArgumentParser()
ap.add_argument('articles'); ap.add_argument('log'); ap.add_argument('ris'); ap.add_argument('outdir')
ap.add_argument('--name1', required=True); ap.add_argument('--name2', required=True)
ap.add_argument('--label1', default='R1'); ap.add_argument('--label2', default='R2')
a = ap.parse_args()

NAME_DEC = {'Included': 'Include', 'Maybe': 'Maybe', 'Excluded': 'Exclude'}
VAL_DEC = {'1': 'Include', '0': 'Maybe', '-1': 'Exclude'}


def norm(s):
    return re.sub(r'[^a-z0-9一-鿿]+', '', (s or '').lower())


def doi_norm(s):
    s = (s or '').strip().lower()
    return re.sub(r'^https?://(dx\.)?doi\.org/', '', s)


def first_num(s):
    m = re.search(r'\d+', s or '')
    return m.group(0) if m else ''


def surname(authors):
    first = re.split(r' and |;', authors or '')[0]
    return norm(first.split(',')[0])


# ---- the imported RIS (WS ids) ----
txt = open(a.ris, encoding='utf-8-sig').read()
ris = []
for block in txt.split('\nER  -'):
    d = defaultdict(list)
    for line in block.splitlines():
        m = re.match(r'^([A-Z][A-Z0-9])  - (.*)$', line)
        if m:
            d[m.group(1)].append(m.group(2))
    if d.get('ID'):
        ris.append(dict(id=d['ID'][0], ty=(d.get('TY') or [''])[0],
                        title=(d.get('T1') or d.get('TI') or [''])[0],
                        year=((d.get('PY') or [''])[0] or '')[:4],
                        au=surname((d.get('AU') or d.get('A1') or [''])[0]),
                        doi=doi_norm((d.get('DO') or [''])[0]),
                        vol=first_num((d.get('VL') or [''])[0]),
                        sp=first_num((d.get('SP') or [''])[0]),
                        urls={u.strip().rstrip('.,;') for u in (d.get('UR') or []) + re.findall(r'https?://\S+', ' '.join(d.get('N1') or []))}))
by_doi = defaultdict(list); by_tya = defaultdict(list); by_tyvp = defaultdict(list); by_ty = defaultdict(list)
by_url = defaultdict(list)
for r in ris:
    for u in r['urls']:
        by_url[u].append(r)
    if r['doi']:
        by_doi[r['doi']].append(r)
    by_tya[(norm(r['title']), r['year'], r['au'])].append(r)
    by_tyvp[(norm(r['title']), r['year'], r['vol'], r['sp'])].append(r)
    by_ty[(norm(r['title']), r['year'])].append(r)

# ---- the Rayyan export ----
arts = list(csv.DictReader(open(a.articles, encoding='utf-8-sig', newline='')))
rows = []
for art in arts:
    aid = art['key'].replace('rayyan-', '')
    m = re.search(r'RAYYAN-INCLUSION: (\{.*?\})', art['notes'])
    inc = dict(re.findall(r'"([^"]+)"=>"([^"]+)"', m.group(1))) if m else {}
    t, y = norm(art['title']), art['year']
    cand, how = [], ''
    d = doi_norm(art['doi'])
    if d and len(by_doi.get(d, [])) == 1:
        cand, how = by_doi[d], 'doi'
    if not cand:
        urls = {u.strip().rstrip('.,;') for u in [art['url']] + re.findall(r'https?://\S+', art['notes'])}
        hit = {r['id']: r for u in urls for r in by_url.get(u, [])}
        if len(hit) == 1:
            cand, how = list(hit.values()), 'url'
    if not cand and len(by_tya.get((t, y, surname(art['authors'])), [])) == 1:
        cand, how = by_tya[(t, y, surname(art['authors']))], 'title+year+author'
    if not cand and len(by_tyvp.get((t, y, first_num(art['volume']), first_num(art['pages'])), [])) == 1:
        cand, how = by_tyvp[(t, y, first_num(art['volume']), first_num(art['pages']))], 'title+year+vol+page'
    if not cand and len(by_ty.get((t, y), [])) == 1:
        cand, how = by_ty[(t, y)], 'title+year'
    rows.append(dict(rayyan_id=aid, title=art['title'], year=y, abstract=art['abstract'], language=art['language'],
                     inc1=NAME_DEC.get(inc.get(a.name1, ''), 'NONE'), inc2=NAME_DEC.get(inc.get(a.name2, ''), 'NONE'),
                     ws=cand[0]['id'] if cand else '', ty=cand[0]['ty'] if cand else '', how=how or 'UNMATCHED'))

# ---- reasons per reviewer from the log (user identity only in memory) ----
events = sorted(csv.DictReader(open(a.log, encoding='utf-8-sig', newline='')), key=lambda e: e['created_at'])
users = sorted({e['user_email'] for e in events})
final_dec = {u: {} for u in users}; reasons = {u: defaultdict(dict) for u in users}
for e in events:
    u, k, v, art_id = e['user_email'], e['key'], e['value'], e['article_id']
    if k == 'included':
        final_dec[u][art_id] = None if v == 'deleted' else VAL_DEC.get(v)
    elif '__EXR__' in k:
        reasons[u][art_id][k.strip('"').replace('__EXR__', '')] = v
score = {}
for u in users:
    for nm, key in ((a.name1, 'inc1'), (a.name2, 'inc2')):
        score[(u, nm)] = sum(1 for r in rows if final_dec[u].get(r['rayyan_id']) == r[key] and r[key] != 'NONE')
u1 = max(users, key=lambda u: score[(u, a.name1)] - score[(u, a.name2)])
u2 = max(users, key=lambda u: score[(u, a.name2)] - score[(u, a.name1)])
assert u1 != u2, 'could not tell the two reviewers apart in the log'
for r in rows:
    r['rea1'] = '; '.join(sorted(n for n, v in reasons[u1][r['rayyan_id']].items() if v == '1'))
    r['rea2'] = '; '.join(sorted(n for n, v in reasons[u2][r['rayyan_id']].items() if v == '1'))
    r['log_ok'] = (final_dec[u1].get(r['rayyan_id'], 'NONE') == r['inc1']) and (final_dec[u2].get(r['rayyan_id'], 'NONE') == r['inc2'])


def cat(r):
    x, y = r['inc1'], r['inc2']
    if 'NONE' in (x, y):
        return 'pending (a reviewer has not decided)'
    if x == y:
        return 'agree-' + x.lower()
    if 'Exclude' in (x, y):
        return 'CONFLICT advance-vs-exclude'
    return 'include-vs-maybe (both advance)'


for r in rows:
    r['category'] = cat(r)


def kappa(pairs):
    n = len(pairs)
    cats = sorted({x for p in pairs for x in p})
    po = sum(1 for p, q in pairs if p == q) / n
    pe = sum((sum(1 for p, _ in pairs if p == c) / n) * (sum(1 for _, q in pairs if q == c) / n) for c in cats)
    return po, ((po - pe) / (1 - pe) if pe < 1 else float('nan'))


import os
os.makedirs(a.outdir, exist_ok=True)
cols = ['ws_id', 'rayyan_id', 'year', 'title', 'language', 'type', f'{a.label1}_decision', f'{a.label1}_reason',
        f'{a.label2}_decision', f'{a.label2}_reason', 'category']


def line(r):
    return dict(zip(cols, [r['ws'], r['rayyan_id'], r['year'], r['title'], r['language'], r['ty'], r['inc1'], r['rea1'],
                           r['inc2'], r['rea2'], r['category']]))


srt = sorted(rows, key=lambda r: r['ws'])
with open(f'{a.outdir}/screening_results_all.csv', 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader()
    for r in srt:
        w.writerow(line(r))
conf = [r for r in srt if r['category'].startswith('CONFLICT')]
ccols = ['ws_id', 'year', 'title', 'language', 'abstract', f'{a.label1}_decision', f'{a.label1}_reason',
         f'{a.label2}_decision', f'{a.label2}_reason', 'discussion_agreed_decision', 'discussion_note',
         'adjudicator_decision', 'adjudicator_note', 'final_decision']
with open(f'{a.outdir}/screening_conflicts_for_adjudication.csv', 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.writer(f); w.writerow(ccols)
    for r in conf:
        w.writerow([r['ws'], r['year'], r['title'], r['language'], r['abstract'], r['inc1'], r['rea1'], r['inc2'], r['rea2'], '', '', '', '', ''])
with open(f'{a.outdir}/screening_include_vs_maybe.csv', 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader()
    for r in srt:
        if r['category'].startswith('include-vs-maybe'):
            w.writerow(line(r))

dec = [r for r in rows if 'NONE' not in (r['inc1'], r['inc2'])]
out = []
out.append(f'records in export: {len(rows)}; decided by both reviewers: {len(dec)}')
out.append(f'{a.label1} undecided: {sum(1 for r in rows if r["inc1"]=="NONE")}; {a.label2} undecided: {sum(1 for r in rows if r["inc2"]=="NONE")}')
out.append('matching to WS ids: ' + str(dict(Counter(r['how'] for r in rows))))
out.append(f'{a.label1}: {dict(Counter(r["inc1"] for r in rows))}')
out.append(f'{a.label2}: {dict(Counter(r["inc2"] for r in rows))}')
if dec:
    po, k = kappa([(r['inc1'], r['inc2']) for r in dec])
    po2, k2 = kappa([('Exclude' if r['inc1'] == 'Exclude' else 'Advance', 'Exclude' if r['inc2'] == 'Exclude' else 'Advance') for r in dec])
    out.append(f'3-category agreement {po:.3f}, kappa {k:.3f}; advance-vs-exclude agreement {po2:.3f}, kappa {k2:.3f}')
out.append('categories: ' + str(dict(Counter(r['category'] for r in rows))))
out.append(f'conflicts to adjudicate (advance-vs-exclude): {len(conf)}')
nr = [r for r in rows if r['inc1'] == 'Exclude' and not r['rea1']]
nr2 = [r for r in rows if r['inc2'] == 'Exclude' and not r['rea2']]
out.append(f'Exclude decisions WITHOUT an exclusion reason: {a.label1} {len(nr)}, {a.label2} {len(nr2)} (the guide requires a reason)')
bad = [r for r in rows if not r['log_ok']]
out.append(f'records where the event log and the export disagree: {len(bad)}')
un = [r for r in rows if r['how'] == 'UNMATCHED']
out.append(f'UNMATCHED to a WS id: {len(un)}' + (' -> ' + '; '.join(f"#{r['rayyan_id']} {r['title'][:50]}" for r in un[:10]) if un else ''))
open(f'{a.outdir}/screening_summary.txt', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print('\n'.join(out))
