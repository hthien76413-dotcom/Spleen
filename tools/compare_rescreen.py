"""Compare Fei Peng's independent RE-SCREEN (new Rayyan project) with Jun Shu's recorded decisions (old project).

PRE-SPECIFIED RULE (approved by the author on 16 Oct 2026, before any re-screen decision existed):
  Jun Shu's Exclude decisions that carry NO exclusion reason are treated as Maybe in the comparison (screening guide section 3: an
  Exclude needs an applicable E1-E6, otherwise choose Maybe). His recorded decisions are not edited. The recorded decision is kept in
  the column R1_recorded_decision and a sensitivity analysis on the recorded decisions is printed as well.
  Consequence to be aware of: a reason-less Exclude that the re-screener also excludes becomes a conflict (Maybe vs Exclude).

Usage (from the repo root):
  python3 -I tools/compare_rescreen.py NEW_ARTICLES_CSV NEW_LOG_CSV RIS OLD_RESULTS_CSV OUT_DIR [--name Fei]
  NEW_ARTICLES_CSV / NEW_LOG_CSV   Rayyan export (Review data > "..." > Export, CSV) of the NEW project
  RIS                              search/dedup/records_deduplicated.ris (the file imported into the new project)
  OLD_RESULTS_CSV                  search/screening/formal/screening_results_all.csv (Jun Shu and the Codex-assisted account)
  OUT_DIR                          e.g. search/screening/rescreen
  --name                           the re-screener's display name as printed in RAYYAN-INCLUSION (default Fei)

Works on partial exports (interim check after the first 100 records): undecided records are 'pending' and left out of the statistics.
E-mail addresses in the log are only used in memory to find the deciding user; nothing identifying is written.

Outputs in OUT_DIR (same column names as the old file, so tools/make_blind_adjudication_sheet.py and
tools/blind_adjudication_analysis.py can be pointed at this folder):
  screening_results_all.csv, screening_conflicts_for_adjudication.csv, screening_include_vs_maybe.csv, rescreen_summary.txt
"""
import argparse, csv, os, re, statistics, datetime as dt
from collections import Counter, defaultdict

csv.field_size_limit(10 ** 9)
ap = argparse.ArgumentParser()
ap.add_argument('articles'); ap.add_argument('log'); ap.add_argument('ris'); ap.add_argument('old'); ap.add_argument('outdir')
ap.add_argument('--name', default='Fei')
a = ap.parse_args()

NAME_DEC = {'Included': 'Include', 'Maybe': 'Maybe', 'Excluded': 'Exclude'}
VAL_DEC = {'1': 'Include', '0': 'Maybe', '-1': 'Exclude'}
E_OK = {'E1 non-human', 'E2 not wandering spleen', 'E3 adults only', 'E4 no original patient data', 'E5 not a formal article', 'E6 other'}


def norm(s):
    return re.sub(r'[^a-z0-9一-鿿]+', '', (s or '').lower())


def doi_norm(s):
    return re.sub(r'^https?://(dx\.)?doi\.org/', '', (s or '').strip().lower())


def first_num(s):
    m = re.search(r'\d+', s or '')
    return m.group(0) if m else ''


def surname(authors):
    return norm(re.split(r' and |;', authors or '')[0].split(',')[0])


# ---- imported RIS -> WS ids (same matching as tools/screening_conflicts.py) ----
ris = []
for block in open(a.ris, encoding='utf-8-sig').read().split('\nER  -'):
    d = defaultdict(list)
    for line in block.splitlines():
        m = re.match(r'^([A-Z][A-Z0-9])  - (.*)$', line)
        if m:
            d[m.group(1)].append(m.group(2))
    if d.get('ID'):
        ris.append(dict(id=d['ID'][0], title=(d.get('T1') or d.get('TI') or [''])[0], year=((d.get('PY') or [''])[0] or '')[:4],
                        au=surname((d.get('AU') or d.get('A1') or [''])[0]), doi=doi_norm((d.get('DO') or [''])[0]),
                        vol=first_num((d.get('VL') or [''])[0]), sp=first_num((d.get('SP') or [''])[0]),
                        abstract=' '.join(d.get('AB') or []),
                        urls={u.strip().rstrip('.,;') for u in (d.get('UR') or []) + re.findall(r'https?://\S+', ' '.join(d.get('N1') or []))}))
by_doi, by_tya, by_tyvp, by_ty, by_url = (defaultdict(list) for _ in range(5))
for r in ris:
    for u in r['urls']:
        by_url[u].append(r)
    if r['doi']:
        by_doi[r['doi']].append(r)
    by_tya[(norm(r['title']), r['year'], r['au'])].append(r)
    by_tyvp[(norm(r['title']), r['year'], r['vol'], r['sp'])].append(r)
    by_ty[(norm(r['title']), r['year'])].append(r)
abstract_of = {r['id']: r['abstract'] for r in ris}

arts = list(csv.DictReader(open(a.articles, encoding='utf-8-sig', newline='')))
new = {}      # ws -> dict(rayyan_id, dec, how)
unmatched = []
for art in arts:
    aid = art['key'].replace('rayyan-', '')
    m = re.search(r'RAYYAN-INCLUSION: (\{.*?\})', art.get('notes') or '')
    inc = dict(re.findall(r'"([^"]+)"=>"([^"]+)"', m.group(1))) if m else {}
    t, y = norm(art['title']), art['year']
    cand, how = [], ''
    d = doi_norm(art.get('doi'))
    if d and len(by_doi.get(d, [])) == 1:
        cand, how = by_doi[d], 'doi'
    if not cand:
        urls = {u.strip().rstrip('.,;') for u in [art.get('url', '')] + re.findall(r'https?://\S+', art.get('notes') or '')}
        hit = {r['id']: r for u in urls for r in by_url.get(u, [])}
        if len(hit) == 1:
            cand, how = list(hit.values()), 'url'
    if not cand and len(by_tya.get((t, y, surname(art.get('authors'))), [])) == 1:
        cand, how = by_tya[(t, y, surname(art.get('authors')))], 'title+year+author'
    if not cand and len(by_tyvp.get((t, y, first_num(art.get('volume')), first_num(art.get('pages'))), [])) == 1:
        cand, how = by_tyvp[(t, y, first_num(art.get('volume')), first_num(art.get('pages')))], 'title+year+vol+page'
    if not cand and len(by_ty.get((t, y), [])) == 1:
        cand, how = by_ty[(t, y)], 'title+year'
    if cand:
        new[cand[0]['id']] = dict(rayyan_id=aid, dec=NAME_DEC.get(inc.get(a.name, ''), 'NONE'), how=how)
    else:
        unmatched.append((aid, art['title'][:60]))

# ---- log: find the deciding user (identity only in memory), reasons, labels, pace ----
events = sorted(csv.DictReader(open(a.log, encoding='utf-8-sig', newline='')), key=lambda e: e['created_at'])
cnt = Counter(e['user_email'] for e in events if e['key'] == 'included')
user = cnt.most_common(1)[0][0] if cnt else None
others = [u for u, n in cnt.items() if u != user and n >= 5]
final_dec, reasons, labels = {}, defaultdict(dict), Counter()
first_ts, inc_events = {}, []
for e in events:
    if e['user_email'] != user:
        continue
    k, v, aid = e['key'], e['value'], e['article_id']
    ts = dt.datetime.strptime(e['created_at'][:23], '%Y-%m-%dT%H:%M:%S.%f') if '.' in e['created_at'] else dt.datetime.strptime(e['created_at'][:19], '%Y-%m-%dT%H:%M:%S')
    if k == 'included':
        final_dec[aid] = None if v == 'deleted' else VAL_DEC.get(v)
        first_ts.setdefault(aid, ts)
        inc_events.append((ts, aid, v))
    elif '__EXR__' in k:
        reasons[aid][k.strip('"').replace('__EXR__', '')] = v
    else:
        labels[k.strip('"')] += 1 if v == '1' else 0
ws_of = {v['rayyan_id']: w for w, v in new.items()}
for w, v in new.items():
    v['rea'] = '; '.join(sorted(n for n, x in reasons[v['rayyan_id']].items() if x == '1'))
    v['log_dec'] = final_dec.get(v['rayyan_id'])

# ---- join with the old results ----
old = list(csv.DictReader(open(a.old, encoding='utf-8-sig', newline='')))
rows = []
for o in old:
    n = new.get(o['ws_id'])
    d2 = n['dec'] if n else 'NONE'
    r1rec, r1rea = o['R1_JunShu_decision'], o['R1_JunShu_reason']
    rule = (r1rec == 'Exclude' and not r1rea)
    r1eff = 'Maybe' if rule else r1rec
    rows.append(dict(ws_id=o['ws_id'], rayyan_id=n['rayyan_id'] if n else '', year=o['year'], title=o['title'], language=o['language'],
                     type=o['type'], r1=r1eff, r1rec=r1rec, r1rea=r1rea, rule=rule, r2=d2, r2rea=n['rea'] if n else '',
                     codex=o['R2_FeiPeng_decision'], codexrea=o['R2_FeiPeng_reason'], how=n['how'] if n else 'NOT IN EXPORT',
                     log_ok=(n is None) or (n['log_dec'] == n['dec'] or (n['dec'] == 'NONE' and n['log_dec'] is None))))


def cat(x, y):
    if 'NONE' in (x, y):
        return 'pending (not yet decided in the re-screen)'
    if x == y:
        return 'agree-' + x.lower()
    if 'Exclude' in (x, y):
        return 'CONFLICT advance-vs-exclude'
    return 'include-vs-maybe (both advance)'


for r in rows:
    r['category'] = cat(r['r1'], r['r2'])
    r['category_rec'] = cat(r['r1rec'], r['r2'])


def kappa(pairs):
    n = len(pairs)
    if not n:
        return float('nan'), float('nan')
    cats = sorted({x for p in pairs for x in p})
    po = sum(1 for p, q in pairs if p == q) / n
    pe = sum((sum(1 for p, _ in pairs if p == c) / n) * (sum(1 for _, q in pairs if q == c) / n) for c in cats)
    return po, ((po - pe) / (1 - pe) if pe < 1 else float('nan'))


os.makedirs(a.outdir, exist_ok=True)
cols = ['ws_id', 'rayyan_id', 'year', 'title', 'language', 'type', 'R1_JunShu_decision', 'R1_JunShu_reason', 'R2_FeiPeng_decision',
        'R2_FeiPeng_reason', 'category', 'R1_recorded_decision', 'R1_rule_applied', 'R2_codex_decision', 'R2_codex_reason']


def line(r):
    return dict(zip(cols, [r['ws_id'], r['rayyan_id'], r['year'], r['title'], r['language'], r['type'], r['r1'], r['r1rea'], r['r2'], r['r2rea'],
                           r['category'], r['r1rec'], 'yes' if r['rule'] else '', r['codex'], r['codexrea']]))


with open(f'{a.outdir}/screening_results_all.csv', 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader()
    for r in sorted(rows, key=lambda r: r['ws_id']):
        w.writerow(line(r))
conf = [r for r in sorted(rows, key=lambda r: r['ws_id']) if r['category'].startswith('CONFLICT')]
with open(f'{a.outdir}/screening_conflicts_for_adjudication.csv', 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.writer(f)
    w.writerow(['ws_id', 'year', 'title', 'language', 'abstract', 'R1_JunShu_decision', 'R1_JunShu_reason', 'R2_FeiPeng_decision', 'R2_FeiPeng_reason',
                'discussion_agreed_decision', 'discussion_note', 'adjudicator_decision', 'adjudicator_note', 'final_decision'])
    for r in conf:
        w.writerow([r['ws_id'], r['year'], r['title'], r['language'], abstract_of.get(r['ws_id'], ''), r['r1'], r['r1rea'], r['r2'], r['r2rea'], '', '', '', '', ''])
with open(f'{a.outdir}/screening_include_vs_maybe.csv', 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader()
    for r in sorted(rows, key=lambda r: r['ws_id']):
        if r['category'].startswith('include-vs-maybe'):
            w.writerow(line(r))

# ---- summary ----
out = []
P = out.append
dec = [r for r in rows if r['r2'] != 'NONE']
P(f'records in the old results: {len(rows)}; in the new export: {len(new)}; decided in the re-screen: {len(dec)}; not matched to a WS id: {len(unmatched)} {unmatched[:5]}')
P('matching: ' + str(dict(Counter(r["how"] for r in rows))))
P(f'deciding user found in the log: {"yes" if user else "NO"}; other users with >=5 decisions in the new log: {len(others)} (the owner should have none)')
P(f'rule applied: {sum(1 for r in rows if r["rule"])} reason-less Jun Shu Excludes treated as Maybe; '
  f'among the decided records {sum(1 for r in dec if r["rule"])}')
P(f'Jun Shu (effective) on decided records: {dict(Counter(r["r1"] for r in dec))}')
P(f'Fei Peng re-screen: {dict(Counter(r["r2"] for r in dec))}')
for label, key1 in (('EFFECTIVE (rule applied)', 'r1'), ('RECORDED (sensitivity)', 'r1rec')):
    if dec:
        po, k = kappa([(r[key1], r['r2']) for r in dec])
        po2, k2 = kappa([('Exclude' if r[key1] == 'Exclude' else 'Adv', 'Exclude' if r['r2'] == 'Exclude' else 'Adv') for r in dec])
        P(f'agreement, Jun Shu {label}: 3-category {po:.3f} (kappa {k:.3f}); advance-vs-exclude {po2:.3f} (kappa {k2:.3f})')
        P('   categories: ' + str(dict(Counter(r["category"] if key1 == "r1" else r["category_rec"] for r in dec))))
if dec:
    codex = [(r['codex'], r['r2']) for r in dec]
    po, k = kappa(codex)
    P(f'for information: Codex-assisted decisions (10-11 Oct) vs the re-screen: agreement {po:.3f}, kappa {k:.3f} (these decisions are not used)')
P(f'conflicts to adjudicate (advance-vs-exclude, rule applied): {len(conf)}; of these caused by the rule (recorded decision was Exclude): {sum(1 for r in conf if r["rule"])}')
P(f'Exclude decisions in the re-screen WITHOUT an exclusion reason: {sum(1 for r in dec if r["r2"] == "Exclude" and not r["r2rea"])}')
P(f'reasons outside E1-E6 (Rayyan defaults etc.): {sum(1 for r in dec if r["r2rea"] and any(x not in E_OK for x in r["r2rea"].split("; ")))}')
P(f'Include on a record without abstract: {sum(1 for r in dec if r["r2"] == "Include" and not abstract_of.get(r["ws_id"], ""))}')
P(f'records where the event log and the export disagree: {sum(1 for r in rows if not r["log_ok"])}')

# ---- process integrity of the re-screen ----
P('\nPROCESS CHECK OF THE RE-SCREEN (pace and bulk actions)')
firsts = sorted(first_ts.values())
gaps = [(b - c).total_seconds() for c, b in zip(firsts, firsts[1:])]
if gaps:
    P(f'first decision {firsts[0]} UTC, last {firsts[-1]} UTC; records with a decision event: {len(firsts)}')
    P(f'gap between consecutive first decisions: median {statistics.median(gaps):.1f} s; share <=3 s {100 * sum(1 for g in gaps if g <= 3) / len(gaps):.0f}%; '
      f'share <=1 s {100 * sum(1 for g in gaps if g <= 1) / len(gaps):.0f}%; active time (gaps <=120 s) {sum(g for g in gaps if g <= 120) / 3600:.1f} h')
    sec = Counter(ts.strftime('%Y-%m-%dT%H:%M:%S') for ts, _, _ in inc_events)
    P(f'seconds with >=5 decision events (bulk): {sum(1 for v in sec.values() if v >= 5)}; maximum in one second: {max(sec.values())}')
    P('labels set in the re-screen: ' + (str(dict(labels)) if labels else 'none') + ('  <-- check any AI-looking label' if any('ai' in k.lower() for k in labels) else ''))
    P('decisions per 100 records (median gap in seconds):')
    for i in range(0, len(gaps), 100):
        blk = gaps[i:i + 100]
        P(f'   records {i + 1}-{i + len(blk)}: median gap {statistics.median(blk):.1f} s, share <=3 s {100 * sum(1 for g in blk if g <= 3) / len(blk):.0f}%')
    P('reference: Jun Shu median 9.4 s (7.5 h active for 2,548); the Codex-assisted account 1.9 s with 61 bulk seconds and 358 AI-prescreen events')
open(f'{a.outdir}/rescreen_summary.txt', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print('\n'.join(out))
