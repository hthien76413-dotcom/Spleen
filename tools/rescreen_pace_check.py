"""Pace and rule-likeness check of the re-screen export (new Rayyan project). Writes no e-mail addresses.

Usage (repo root):
  python3 -I tools/rescreen_pace_check.py NEW_LOG_CSV search/screening/rescreen OUT_DIR
Needs search/screening/rescreen/screening_results_all.csv (from tools/compare_rescreen.py), the RIS, and the pilot reference file.
Writes OUT_DIR/rescreen_pace_findings.txt and OUT_DIR/rescreen_decisions_log_deidentified.csv.
"""
import csv, io, re, sys, math, statistics, collections, datetime as dt
csv.field_size_limit(10 ** 9)
log_path, rs_dir, out = sys.argv[1:4]
res = list(csv.DictReader(open(rs_dir + '/screening_results_all.csv', encoding='utf-8-sig')))
byid = {r['rayyan_id'].replace('rayyan-', ''): r for r in res}
byws = {r['ws_id']: r for r in res}
ev = []
for r in csv.DictReader(io.StringIO(open(log_path, encoding='utf-8-sig').read())):
    ev.append((dt.datetime.strptime(r['created_at'], '%Y-%m-%dT%H:%M:%S.%fZ'), r['user_id'], r['article_id'], r['key'], r['value']))
ev.sort()
users = {u: 'R2_rescreen_account_%d' % i for i, u in enumerate(sorted({e[1] for e in ev}), 1)}
with open(out + '/rescreen_decisions_log_deidentified.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f); w.writerow(['created_at_utc', 'account', 'ws_id', 'key', 'value'])
    for t, u, a, k, v in ev:
        w.writerow([t.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3], users[u], byid[a]['ws_id'] if a in byid else '', k, v])
first = {}
for t, u, a, k, v in ev:
    if k == 'included' and a not in first: first[a] = (t, v)
order = sorted(first.items(), key=lambda x: x[1][0])
gaps = [(order[i][1][0] - order[i - 1][1][0]).total_seconds() for i in range(1, len(order))]
L = []
L.append('accounts with events: %d (events %d); records with a decision: %d; records decided more than once: %d' % (
    len(users), len(ev), len(order), sum(1 for c in collections.Counter(a for t, u, a, k, v in ev if k == 'included').values() if c > 1)))
L.append('first decision %s UTC, last %s UTC' % (order[0][1][0], order[-1][1][0]))
ws = [int(byid[a]['ws_id'][2:]) for a, _ in order]
L.append('strict list-order steps (WS+1): %d of %d' % (sum(1 for i in range(1, len(ws)) if ws[i] == ws[i - 1] + 1), len(ws) - 1))
L.append('gap between consecutive first decisions: median %.2f s; <=1 s %.0f%%; <=3 s %.0f%%; gaps >120 s: %d (total %.2f h)' % (
    statistics.median(gaps), 100 * sum(1 for g in gaps if g <= 1) / len(gaps), 100 * sum(1 for g in gaps if g <= 3) / len(gaps),
    sum(1 for g in gaps if g > 120), sum(g for g in gaps if g > 120) / 3600))
L.append('first 34 gaps (s): ' + ', '.join('%.1f' % g for g in gaps[:34]))
bins = collections.Counter(t.replace(minute=(t.minute // 15) * 15, second=0, microsecond=0) for t, _ in (x[1] for x in order))
L.append('decisions per 15 minutes (UTC): ' + '; '.join('%s %d' % (b.strftime('%H:%M'), bins[b]) for b in sorted(bins)))
for d, n in (('1', 'Include'), ('0', 'Maybe'), ('-1', 'Exclude')):
    g = [x for x, y in zip(gaps, [o[1][1] for o in order[1:]]) if y == d]
    L.append('median gap before %s decisions: %.2f s (n=%d)' % (n, statistics.median(g), len(g)))
ris = open('search/dedup/records_deduplicated.ris', encoding='utf-8').read().split('\nER  - ')
absl, txt = {}, {}
for r in ris:
    i = re.search(r'^ID  - (WS\d+)', r, re.M)
    if not i: continue
    t = re.search(r'^(?:TI|T1)  - (.*)$', r, re.M); a = re.search(r'^AB  - (.*?)(?=\n[A-Z][A-Z0-9]  - |\Z)', r, re.M | re.S)
    absl[i.group(1)] = len(a.group(1)) if a else 0
    txt[i.group(1)] = (t.group(1) if t else '') + ' ' + (a.group(1) if a else '')
xs = [absl[byid[order[i][0]]['ws_id']] for i in range(1, len(order))]
mx, my = sum(xs) / len(xs), sum(gaps) / len(gaps)
r_ = sum((a - mx) * (b - my) for a, b in zip(xs, gaps)) / math.sqrt(sum((a - mx) ** 2 for a in xs) * sum((b - my) ** 2 for b in gaps))
L.append('correlation between abstract length and the gap before the decision: %.3f (reading time would raise it)' % r_)
kw = re.compile(r'wander|floating spleen|ectopic spleen|pelvic spleen|movable|mobile spleen|splenoptosis|splenic ptosis|torsion|volvulus|splenopexy|游走|游动|漂浮|脾下垂|脾蒂扭转|脾扭转|异位脾', re.I)
adv = lambda d: d in ('Include', 'Maybe')
rule = {w: ('Maybe' if kw.search(t) else 'Exclude') for w, t in txt.items()}
L.append('advance-vs-exclude agreement of the re-screen with a simple keyword rule: %.3f (not a keyword rule)' % (sum(1 for r in res if adv(r['R2_FeiPeng_decision']) == adv(rule[r['ws_id']])) / len(res)))
pil = list(csv.DictReader(open('search/screening/formal/pilot_reference_set_decisions.csv', encoding='utf-8-sig')))
c = collections.Counter(byws[p['ws_id']]['R2_FeiPeng_decision'] for p in pil if p['pilot_status'] == 'IPD-included')
L.append('45 pilot reports with IPD in the re-screen: ' + str(dict(c)))
open(out + '/rescreen_pace_findings.txt', 'w', encoding='utf-8').write('\n'.join(L) + '\n')
print('\n'.join(L))
