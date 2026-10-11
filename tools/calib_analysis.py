import csv, sys, json, re, statistics
from collections import Counter, defaultdict
from datetime import datetime

articles_path, log_path, ids_path, out_results, out_log = sys.argv[1:6]
csv.field_size_limit(10**9)

# --- articles (key, title, year, notes) ---
arts = list(csv.DictReader(open(articles_path, encoding='utf-8-sig', newline='')))
art_by_id = {a['key'].replace('rayyan-', ''): a for a in arts}

# --- ids/titles of the calibration set (WS IDs) ---
ids = list(csv.DictReader(open(ids_path, encoding='utf-8-sig', newline='')))

def norm(s):
    return re.sub(r'[^a-z0-9一-鿿]+', '', s.lower())

ws_by_title = defaultdict(list)
for r in ids:
    ws_by_title[(norm(r['title']), r['year'])].append(r['final_id'])

# --- event log: last event per (user, article, key) wins ---
events = list(csv.DictReader(open(log_path, encoding='utf-8-sig', newline='')))
users = sorted({e['user_email'] for e in events}, key=lambda u: min(e['created_at'] for e in events if e['user_email'] == u))
assert len(users) == 2, users
label = {users[0]: 'R1_JunShu', users[1]: 'R2_FeiPeng'}
print('first-event order of users ->', {u[:3] + '***': label[u] for u in users})

dec = {u: {} for u in users}        # article -> value (1/0/-1) or None if deleted
rea = {u: defaultdict(dict) for u in users}  # article -> reason -> 1/deleted
times = {u: [] for u in users}
for e in sorted(events, key=lambda e: e['created_at']):
    u, a, k, v = e['user_email'], e['article_id'], e['key'], e['value']
    times[u].append(datetime.strptime(e['created_at'], '%Y-%m-%dT%H:%M:%S.%fZ'))
    if k == 'included':
        dec[u][a] = None if v == 'deleted' else int(v)
    elif k.startswith('"__EXR__') or k.startswith('__EXR__'):
        name = k.strip('"').replace('__EXR__', '')
        rea[u][a][name] = v

NAME = {1: 'Include', 0: 'Maybe', -1: 'Exclude'}
def final_reasons(u, a):
    return sorted(n for n, v in rea[u][a].items() if v == '1')

ids50 = sorted(art_by_id)
assert len(ids50) == 50
rows = []
bad = 0
for a in ids50:
    art = art_by_id[a]
    ws = ws_by_title.get((norm(art['title']), art['year']), [])
    if len(ws) != 1:
        # try title only
        cands = [r['final_id'] for r in ids if norm(r['title']) == norm(art['title'])]
        ws = cands
    m = re.search(r'RAYYAN-INCLUSION: (\{.*?\})', art['notes'])
    inc = dict(re.findall(r'"([^"]+)"=>"([^"]+)"', m.group(1))) if m else {}
    r1 = dec[users[0]].get(a); r2 = dec[users[1]].get(a)
    # cross-check with articles.csv
    chk1 = inc.get('俊'); chk2 = inc.get('Fei')
    ok = (chk1 == {1: 'Included', 0: 'Maybe', -1: 'Excluded'}.get(r1)) and (chk2 == {1: 'Included', 0: 'Maybe', -1: 'Excluded'}.get(r2))
    if not ok:
        bad += 1
        print('MISMATCH', a, r1, r2, inc)
    rows.append(dict(
        rayyan_id=a, final_id=';'.join(ws), year=art['year'], title=art['title'],
        R1_JunShu_decision=NAME.get(r1, 'NONE'), R1_reason='; '.join(final_reasons(users[0], a)),
        R2_FeiPeng_decision=NAME.get(r2, 'NONE'), R2_reason='; '.join(final_reasons(users[1], a)),
        has_abstract='yes' if art['abstract'].strip() else 'no', language=art['language'],
        user_notes_in_export=('yes' if 'RAYYAN-LABELS' in art['notes'] or 'RAYYAN-USER-NOTES' in art['notes'] else '')))
print('articles.csv cross-check mismatches:', bad)
print('WS ID mapping: unique matches', sum(1 for r in rows if r['final_id'] and ';' not in r['final_id']),
      '| none', sum(1 for r in rows if not r['final_id']), '| ambiguous', sum(1 for r in rows if ';' in r['final_id']))

# --- counts ---
for lab, key in (('R1', 'R1_JunShu_decision'), ('R2', 'R2_FeiPeng_decision')):
    print(lab, dict(Counter(r[key] for r in rows)))
for lab, key in (('R1', 'R1_reason'), ('R2', 'R2_reason')):
    print(lab, 'exclusion reasons', dict(Counter(r[key] for r in rows if r[key])))

# --- agreement ---
def kappa(pairs):
    n = len(pairs)
    cats = sorted({x for p in pairs for x in p})
    po = sum(1 for a, b in pairs if a == b) / n
    pe = sum((sum(1 for a, _ in pairs if a == c) / n) * (sum(1 for _, b in pairs if b == c) / n) for c in cats)
    return po, (po - pe) / (1 - pe) if pe < 1 else float('nan'), pe

pairs3 = [(r['R1_JunShu_decision'], r['R2_FeiPeng_decision']) for r in rows]
po, k, pe = kappa(pairs3)
print(f'3-category (Include/Maybe/Exclude): agree {sum(1 for a,b in pairs3 if a==b)}/50 = {po:.3f}; kappa {k:.3f} (pe {pe:.3f})')
coll = lambda x: 'Exclude' if x == 'Exclude' else 'Advance'
pairs2 = [(coll(a), coll(b)) for a, b in pairs3]
po2, k2, pe2 = kappa(pairs2)
print(f'2-category (Exclude vs Include/Maybe): agree {sum(1 for a,b in pairs2 if a==b)}/50 = {po2:.3f}; kappa {k2:.3f} (pe {pe2:.3f})')
print('contingency (R1 rows x R2 cols):')
for a in ('Include', 'Maybe', 'Exclude'):
    print(' ', a.ljust(8), [sum(1 for x, y in pairs3 if x == a and y == b) for b in ('Include', 'Maybe', 'Exclude')])

# --- disagreements ---
print('\nDISAGREEMENTS (decision):')
for r in rows:
    if r['R1_JunShu_decision'] != r['R2_FeiPeng_decision']:
        print(f"  {r['final_id']:7} #{r['rayyan_id']} R1={r['R1_JunShu_decision']}({r['R1_reason']}) R2={r['R2_FeiPeng_decision']}({r['R2_reason']}) abstract={r['has_abstract']} | {r['title'][:90]}")
print('\nREASON DIFFERENCES among both-Exclude:')
for r in rows:
    if r['R1_JunShu_decision'] == r['R2_FeiPeng_decision'] == 'Exclude' and r['R1_reason'] != r['R2_reason']:
        print(f"  {r['final_id']:7} R1={r['R1_reason']!r} R2={r['R2_reason']!r} | {r['title'][:80]}")
print('\nBOTH-EXCLUDE with reason lists:')
print(Counter((r['R1_reason'], r['R2_reason']) for r in rows if r['R1_JunShu_decision'] == r['R2_FeiPeng_decision'] == 'Exclude'))

# --- timing ---
for u in users:
    t = times[u]
    print(f'{label[u]}: first event {min(t):%Y-%m-%d %H:%M:%S}Z, last {max(t):%H:%M:%S}Z, span {(max(t)-min(t)).total_seconds()/60:.1f} min, events {len(t)}')
# per-article time between consecutive first decisions
for u in users:
    firsts = {}
    for e in sorted(events, key=lambda e: e['created_at']):
        if e['user_email'] == u and e['key'] == 'included' and e['article_id'] not in firsts:
            firsts[e['article_id']] = datetime.strptime(e['created_at'], '%Y-%m-%dT%H:%M:%S.%fZ')
    ts = sorted(firsts.values())
    gaps = [(b - a).total_seconds() for a, b in zip(ts, ts[1:])]
    print(f'{label[u]}: first-decision span {(ts[-1]-ts[0]).total_seconds()/60:.1f} min for {len(ts)} records; median gap {statistics.median(gaps):.0f}s; gaps >120s: {sum(1 for g in gaps if g>120)}')
    redo = [a for a in {e["article_id"] for e in events if e["user_email"] == u} if sum(1 for e in events if e["user_email"] == u and e["article_id"] == a and e["key"] == "included") > 1]
    print(f'  records with more than one "included" event: {len(redo)} -> {sorted(redo)}')

# --- default Rayyan reasons used? ---
allr = Counter()
for u in users:
    for a in rea[u]:
        for n, v in rea[u][a].items():
            allr[(label[u], n, v)] += 1
print('\nall reason events:', dict(allr))

# --- write outputs (no e-mail addresses, no Rayyan user ids) ---
cols = ['final_id', 'rayyan_id', 'year', 'title', 'R1_JunShu_decision', 'R1_reason', 'R2_FeiPeng_decision', 'R2_reason', 'has_abstract', 'language']
with open(out_results, 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.DictWriter(f, fieldnames=cols, extrasaction='ignore'); w.writeheader()
    for r in sorted(rows, key=lambda r: r['final_id']): w.writerow(r)
with open(out_log, 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.writer(f); w.writerow(['created_at_utc', 'reviewer', 'rayyan_article_id', 'key', 'value'])
    for e in sorted(events, key=lambda e: e['created_at']):
        w.writerow([e['created_at'], label[e['user_email']], e['article_id'], e['key'], e['value']])
print('written', out_results, out_log)
