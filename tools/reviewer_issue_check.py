"""Per-reviewer problem check of the formal title/abstract screening (16 Oct 2026).

Usage (from the repo root):  python3 -I tools/reviewer_issue_check.py
Reads   search/screening/formal/screening_results_all.csv, formal_decisions_log_deidentified.csv, search/dedup/records_deduplicated.ris
Writes  search/screening/formal/reviewer_issue_check.txt  (summary)  and  reviewer_issue_records.csv  (one row per flagged record and issue)

The checks are of two kinds:
  GUIDE   = mechanical breaches of the written screening guide (reason missing, default reason, leftover reason, Include without abstract, ...);
  PROXY   = keyword heuristics on title/abstract (an animal word, an adult age, a child word, a wandering/torsion word). These are NOT ground
            truth; they only point to records worth looking at, and the numbers are reported as such.
No e-mail addresses are read or written.
"""
import csv, re, collections, math, datetime as dt

F = 'search/screening/formal/'
ADV = ('Include', 'Maybe')
DEFAULTS_OK = {'E1 non-human', 'E2 not wandering spleen', 'E3 adults only', 'E4 no original patient data', 'E5 not a formal article', 'E6 other'}

res = list(csv.DictReader(open(F + 'screening_results_all.csv', encoding='utf-8-sig')))
log = list(csv.DictReader(open(F + 'formal_decisions_log_deidentified.csv', encoding='utf-8-sig')))
title, abstract, rtype = {}, {}, {}
for blk in open('search/dedup/records_deduplicated.ris', encoding='utf-8-sig').read().split('\nER  -'):
    m = re.search(r'^ID  - (.*)$', blk, re.M)
    if not m:
        continue
    i = m.group(1)
    title[i] = ' '.join(re.findall(r'^TI  - (.*)$', blk, re.M))
    abstract[i] = ' '.join(re.findall(r'^AB  - (.*)$', blk, re.M)).strip()
    mt = re.search(r'^TY  - (.*)$', blk, re.M)
    rtype[i] = mt.group(1).strip() if mt else ''

ANIMAL = re.compile(r'\b(dog|dogs|canine|canines|cat|cats|feline|horse|horses|equine|pig|pigs|piglet|piglets|porcine|swine|bovine|cattle|cow|cows|calf|calves|sheep|ovine|goat|rat|rats|mice|mouse|murine|rabbit|rabbits|rodent|rodents|monkey|monkeys|primate|veterinar\w*|animal|animals|beagle|beagles)\b|犬|猫|大鼠|小鼠|兔|猪|兽医|动物|实验', re.I)
PEDS = re.compile(r'child|pediatric|paediatric|infant|neonat|newborn|toddler|\bboy\b|\bgirl\b|adolescen|儿童|小儿|患儿|婴|幼儿|新生儿|少儿|\b(?:[0-9]|1[0-7])[- ]?(?:year|yr|month|week|day)s?[- ]?old|\b(?:[0-9]|1[0-7])岁|(?:[0-9]|1[0-7])个月', re.I)
WSRE = re.compile(r'wander|floating spleen|ptosic|ptotic|splenoptosis|ectopic spleen|pelvic spleen|migrat|torsion|twist|volvulus|游走脾|游动脾|漂浮脾|脾下垂|脾蒂|扭转|异位脾', re.I)
ACCESS = re.compile(r'accessory|supernumerary|splenosis|splenule|ectopic pregnan|pregnan|transplant|副脾|脾种植|妊娠|移植', re.I)
ADULTWORD = re.compile(r'\badults?\b|elderly|\bolder\b|middle[- ]aged|geriatric|postpartum|menopaus|成人|成年|老年|中年|产后|产妇', re.I)
AGE_RE = re.compile(r'\b(\d{1,3})[- ]?(?:year|yr)s?[- ]?old|\baged?\s+(\d{1,3})\b|\b(\d{1,3})岁')


def text(i):
    return title[i] + ' ' + abstract[i]


def ages(t):
    out = []
    for m in AGE_RE.finditer(t):
        for g in m.groups():
            if g:
                out.append(int(g))
    return out


def adult_support(i):
    """True if the text states an adult age or adult word and no child age/word."""
    t = text(i)
    a = ages(t)
    adult = any(x >= 18 for x in a) or bool(ADULTWORD.search(t))
    child = any(x <= 17 for x in a) or bool(PEDS.search(t))
    return adult and not child


def reasons(s):
    return [x.strip() for x in s.split(';') if x.strip()]


flags = []   # (ws, reviewer, issue, decision, reason, title)
out = []


def P(*a):
    out.append(' '.join(str(x) for x in a))


def flag(r, who, issue, d, rs):
    flags.append((r['ws_id'], who, issue, d, rs, title[r['ws_id']][:160]))


def wilson(k, n, z=1.96):
    if n == 0:
        return (float('nan'),) * 2
    p = k / n; d = 1 + z * z / n; c = p + z * z / (2 * n); h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (c - h) / d, (c + h) / d


def pct(k, n):
    return f'{k}/{n} = {100 * k / n:.1f}%' if n else f'{k}/0'


REV = (('R1', 'Jun Shu', 'R1_JunShu_decision', 'R1_JunShu_reason'), ('R2', 'Fei Peng', 'R2_FeiPeng_decision', 'R2_FeiPeng_reason'))

# ------------------------------------------------------------------ A. guide breaches, both reviewers
P('=' * 100)
P('A. GUIDE BREACHES (mechanical)')
for tag, name, dk, rk in REV:
    P(f'\n--- {tag} {name} ---')
    c = collections.Counter(r[dk] for r in res)
    P('decisions:', dict(c), f'(advance rate {100 * (c["Include"] + c["Maybe"]) / len(res):.1f}%)')
    exc = [r for r in res if r[dk] == 'Exclude']
    noreason = [r for r in exc if not r[rk]]
    P('Exclude without any reason (guide: choose Maybe instead):', len(noreason), 'of', len(exc))
    for r in noreason:
        flag(r, tag, 'A1 Exclude without reason', r[dk], '')
    dflt = [r for r in res if any(x not in DEFAULTS_OK for x in reasons(r[rk]))]
    P('Rayyan default reasons used (guide: never):', len(dflt), [(r['ws_id'], r[rk]) for r in dflt])
    for r in dflt:
        flag(r, tag, 'A2 default reason', r[dk], r[rk])
    left = [r for r in res if r[dk] != 'Exclude' and r[rk]]
    P('Include/Maybe records still carrying an exclusion reason (leftover from a changed decision):', len(left))
    for r in left:
        flag(r, tag, 'A3 leftover reason', r[dk], r[rk])
    multi = [r for r in exc if len(reasons(r[rk])) > 1]
    P('Exclude with 2 or more reasons:', len(multi), '(guide section 5 allows any ONE applicable reason; several is harmless for who advances but muddles PRISMA counts)')
    inc_noabs = [r for r in res if r[dk] == 'Include' and not abstract[r['ws_id']]]
    P('Include on a record WITHOUT abstract (guide: Maybe or Exclude only):', len(inc_noabs))
    for r in inc_noabs:
        flag(r, tag, 'A5 Include without abstract', r[dk], r[rk])
    exc_noabs = [r for r in exc if not abstract[r['ws_id']]]
    P('Exclude on a record without abstract:', len(exc_noabs), 'of which without reason', sum(1 for r in exc_noabs if not r[rk]))

# ------------------------------------------------------------------ B. reason plausibility (PROXY)
P('\n' + '=' * 100)
P('B. REASON PLAUSIBILITY (keyword proxies - pointers, not ground truth)')
for tag, name, dk, rk in REV:
    P(f'\n--- {tag} {name} ---')
    e1 = [r for r in res if 'E1' in reasons(r[rk])[0:9] or any(x.startswith('E1') for x in reasons(r[rk]))]
    e1_noanimal = [r for r in e1 if not ANIMAL.search(text(r['ws_id']))]
    P('E1 non-human used:', len(e1), '| text has NO animal/experimental word:', len(e1_noanimal), '|', pct(len(e1_noanimal), len(e1)))
    P('   of those, the other reviewer advanced:', sum(1 for r in e1_noanimal if r['R2_FeiPeng_decision' if tag == 'R1' else 'R1_JunShu_decision'] in ADV))
    for r in e1_noanimal:
        flag(r, tag, 'B1 E1 but no animal word in text', r[dk], r[rk])
    e3 = [r for r in res if any(x.startswith('E3') for x in reasons(r[rk]))]
    e3_sup = [r for r in e3 if adult_support(r['ws_id'])]
    e3_child = [r for r in e3 if PEDS.search(text(r['ws_id'])) or any(a <= 17 for a in ages(text(r['ws_id'])))]
    e3_noabs = [r for r in e3 if not abstract[r['ws_id']]]
    P('E3 adults only used:', len(e3), '| text states an adult age/word and no child cue:', len(e3_sup), '|', pct(len(e3_sup), len(e3)))
    P('   text contains a CHILD cue (age <=17 or child word):', len(e3_child), '| no abstract (title only):', len(e3_noabs))
    P('   no adult evidence and no abstract-based support (E3 on thin evidence):', len([r for r in e3 if not adult_support(r['ws_id'])]))
    for r in e3_child:
        flag(r, tag, 'B2 E3 but text has child cue', r[dk], r[rk])
    for r in e3:
        if not adult_support(r['ws_id']) and r not in e3_child:
            flag(r, tag, 'B3 E3 without adult evidence in text', r[dk], r[rk])
    e5 = [r for r in res if any(x.startswith('E5') for x in reasons(r[rk]))]
    e5_bad = [r for r in e5 if rtype[r['ws_id']] not in ('PAT', 'NEWS', 'CONF', 'GEN')]
    P('E5 not a formal article used:', len(e5), '| record type not PAT/NEWS/CONF/GEN:', len(e5_bad), collections.Counter(rtype[r['ws_id']] for r in e5_bad))
    for r in e5_bad:
        flag(r, tag, 'B4 E5 on a journal article/chapter', r[dk], r[rk])
    e2 = [r for r in res if any(x.startswith('E2') for x in reasons(r[rk]))]
    e2_ws = [r for r in e2 if re.search(r'wandering spleen|floating spleen|游走脾|漂浮脾|游动脾', title[r['ws_id']], re.I) and not ACCESS.search(text(r['ws_id']))]
    P('E2 not wandering spleen used:', len(e2), '| title says wandering/floating spleen and no accessory/splenosis/pregnancy/transplant word:', len(e2_ws))
    for r in e2_ws:
        flag(r, tag, 'B5 E2 but title says wandering spleen', r[dk], r[rk])
    e4 = [r for r in res if any(x.startswith('E4') for x in reasons(r[rk]))]
    e4_cr = [r for r in e4 if re.search(r'case report|case series|report of|例', text(r['ws_id']), re.I) and not re.search(r'review|综述|literature', text(r['ws_id']), re.I)]
    P('E4 no original patient data used:', len(e4), '| text looks like a case report/series and not a review:', len(e4_cr))
    for r in e4_cr:
        flag(r, tag, 'B6 E4 but text looks like a case report', r[dk], r[rk])

# ------------------------------------------------------------------ C. relevance proxy
P('\n' + '=' * 100)
P('C. RELEVANCE PROXY: wandering/torsion word AND child cue present in title/abstract')


def proxy_rel(i):
    t = text(i)
    return bool(WSRE.search(t)) and bool(PEDS.search(t)) and not (ANIMAL.search(t) and not re.search(r'patient|child|infant|human|患儿|患者', t, re.I))


for tag, name, dk, rk in REV:
    exc = [r for r in res if r[dk] == 'Exclude']
    adv = [r for r in res if r[dk] in ADV]
    ex_rel = [r for r in exc if proxy_rel(r['ws_id'])]
    ad_irr = [r for r in adv if not WSRE.search(text(r['ws_id']))]
    ad_animal = [r for r in adv if ANIMAL.search(text(r['ws_id'])) and not PEDS.search(text(r['ws_id']))]
    P(f'\n--- {tag} {name} ---')
    P('Excluded although proxy-relevant:', pct(len(ex_rel), len(exc)), '| of these the other reviewer advanced:', sum(1 for r in ex_rel if r['R2_FeiPeng_decision' if tag == 'R1' else 'R1_JunShu_decision'] in ADV))
    P('   by reason:', dict(collections.Counter(r[rk] or '(none)' for r in ex_rel)))
    P('Advanced although NO wandering/torsion word in text:', pct(len(ad_irr), len(adv)))
    P('Advanced although text has an animal word and no child cue:', len(ad_animal))
    for r in ex_rel:
        flag(r, tag, 'C1 Excluded but proxy-relevant', r[dk], r[rk])
    for r in ad_animal:
        flag(r, tag, 'C2 Advanced but animal word and no child cue', r[dk], r[rk])

# ------------------------------------------------------------------ D. conflicts: what are they?
P('\n' + '=' * 100)
P('D. THE 642 ADVANCE-VS-EXCLUDE CONFLICTS')
conf1 = [r for r in res if r['R1_JunShu_decision'] == 'Exclude' and r['R2_FeiPeng_decision'] in ADV]
conf2 = [r for r in res if r['R2_FeiPeng_decision'] == 'Exclude' and r['R1_JunShu_decision'] in ADV]
for name, grp in (('R1 Exclude / R2 advance', conf1), ('R2 Exclude / R1 advance', conf2)):
    rel = [r for r in grp if proxy_rel(r['ws_id'])]
    noabs = [r for r in grp if not abstract[r['ws_id']]]
    P(f'\n{name}: {len(grp)} | proxy-relevant {pct(len(rel), len(grp))} | no abstract {len(noabs)} | no wandering/torsion word {sum(1 for r in grp if not WSRE.search(text(r["ws_id"])))}')
    P('   Exclude-side reasons:', dict(collections.Counter((r['R1_JunShu_reason'] if name.startswith('R1') else r['R2_FeiPeng_reason']) or '(none)' for r in grp).most_common(8)))
    P('   type:', dict(collections.Counter(rtype[r['ws_id']] for r in grp)))
    P('   language:', dict(collections.Counter(r['language'] for r in grp).most_common(5)))
    if name.startswith('R1'):
        e3 = [r for r in grp if 'E3' in r['R1_JunShu_reason']]
        P('   R1 E3 in this group:', len(e3), '| adult support in text:', sum(1 for r in e3 if adult_support(r['ws_id'])))
        P('   R1 reason-less Excludes in this group:', sum(1 for r in grp if not r['R1_JunShu_reason']))

# ------------------------------------------------------------------ E. pilot reference set
P('\n' + '=' * 100)
P('E. PILOT REFERENCE SET (45 eligible paediatric wandering-spleen reports with IPD; all must advance)')
pil = list(csv.DictReader(open(F + 'pilot_reference_set_decisions.csv', encoding='utf-8-sig')))
P('file columns:', list(pil[0].keys()))
for tag, name, dk, rk in REV:
    pass

# ------------------------------------------------------------------ F. R1 specifics from the log
P('\n' + '=' * 100)
P('F. R1 (Jun Shu) FROM THE EVENT LOG')


def ts(s):
    return dt.datetime.strptime(s[:19], '%Y-%m-%dT%H:%M:%S')


byrev = collections.defaultdict(lambda: collections.defaultdict(list))
for e in log:
    if e['key'] == 'included':
        byrev[e['reviewer']][e['ws_id']].append((e['created_at_utc'], e['value']))
rs = {(e['reviewer'], e['ws_id'], e['created_at_utc'][:19]) for e in log if e['key'].startswith('__EXR__')}
r1_nr = [r for r in res if r['R1_JunShu_decision'] == 'Exclude' and not r['R1_JunShu_reason']]
h = collections.Counter()
htot = collections.Counter()
for r in res:
    if r['R1_JunShu_decision'] != 'Exclude':
        continue
    seq = sorted(byrev['R1'][r['ws_id']])
    last = seq[-1][0] if seq else None
    if last:
        k = last[:13]
        htot[k] += 1
        if not r['R1_JunShu_reason']:
            h[k] += 1
P('R1 Excludes without reason: first', min(h) if h else None, 'last', max(h) if h else None, '(UTC hour of the final Exclude event)')
P('share of R1 Excludes without reason by UTC hour (only hours with at least one):')
for k in sorted(h):
    P(f'   {k}  {h[k]:3d} of {htot[k]:3d}  ({100 * h[k] / htot[k]:.0f}%)')
rng = [int(r['ws_id'][2:]) for r in r1_nr]
P('WS range of R1 reason-less Excludes:', min(rng), max(rng))
chg = collections.Counter()
nchg = 0
for w, seq in byrev['R1'].items():
    vals = [v for t, v in sorted(seq) if v != 'deleted']
    if len(set(vals)) > 1:
        nchg += 1
        chg[(vals[0], vals[-1])] += 1
P('R1 records whose decision changed at least once:', nchg, dict(chg))

# ------------------------------------------------------------------ G. R2 specifics from the log
P('\n' + '=' * 100)
P('G. R2 (Fei Peng) FROM THE EVENT LOG')
chg2 = collections.Counter()
n2 = 0
first_ts = {}
final_val = {}
for w, seq in byrev['R2'].items():
    seq = sorted(seq)
    first_ts[w] = seq[0][0]
    vals = [v for t, v in seq if v != 'deleted']
    final_val[w] = vals[-1] if vals else None
    if len(set(vals)) > 1:
        n2 += 1
        chg2[(vals[0], vals[-1])] += 1
P('R2 records whose decision changed at least once:', n2, dict(chg2))
CUT = '2026-10-10T10:00:00'
pa = [r for r in res if first_ts[r['ws_id']] < CUT]
pb = [r for r in res if first_ts[r['ws_id']] >= CUT]


def kappa3(rows):
    cats = ('Include', 'Maybe', 'Exclude')
    n = len(rows)
    if not n:
        return float('nan')
    po = sum(1 for r in rows if r['R1_JunShu_decision'] == r['R2_FeiPeng_decision']) / n
    pe = sum((sum(1 for r in rows if r['R1_JunShu_decision'] == c) / n) * (sum(1 for r in rows if r['R2_FeiPeng_decision'] == c) / n) for c in cats)
    return (po - pe) / (1 - pe) if pe < 1 else float('nan')


for name, grp in (('R2 first decision before 10 Oct 10:00 UTC (human pace, ~15 s per record)', pa), ('R2 first decision after that (about 2 s per record)', pb)):
    n = len(grp)
    a2 = sum(1 for r in grp if r['R2_FeiPeng_decision'] in ADV)
    a1 = sum(1 for r in grp if r['R1_JunShu_decision'] in ADV)
    agree = sum(1 for r in grp if r['R1_JunShu_decision'] == r['R2_FeiPeng_decision'])
    P(f'\n{name}: n={n}')
    P(f'   R2 advance {pct(a2, n)} | R1 advance on the same records {pct(a1, n)} | 3-category agreement {pct(agree, n)} | kappa {kappa3(grp):.2f}')
    c2 = collections.Counter(r['R2_FeiPeng_decision'] for r in grp)
    P('   R2 decisions:', dict(c2), '| R1 decisions:', dict(collections.Counter(r['R1_JunShu_decision'] for r in grp)))
bulk = []
sec = collections.defaultdict(list)
for e in log:
    if e['reviewer'] == 'R2' and e['key'] == 'included':
        sec[e['created_at_utc'][:19]].append(e)
bulk_ws = set()
for s, evs in sec.items():
    if len(evs) >= 5:
        for e in evs:
            if e['value'] == '-1':
                bulk_ws.add(e['ws_id'])
bulk_rows = [r for r in res if r['ws_id'] in bulk_ws and r['R2_FeiPeng_decision'] == 'Exclude']
P('\nR2 final Excludes set in bulk seconds (>=5 decisions in one second):', len(bulk_rows))
P('   R1 decision on them:', dict(collections.Counter(r['R1_JunShu_decision'] for r in bulk_rows)))
P('   R2 reasons on them:', dict(collections.Counter(r['R2_FeiPeng_reason'] for r in bulk_rows)))
b_e3 = [r for r in bulk_rows if 'E3' in r['R2_FeiPeng_reason']]
P('   bulk E3 adults only:', len(b_e3), '| adult age/word in text and no child cue:', sum(1 for r in b_e3 if adult_support(r['ws_id'])), '| child cue in text:', sum(1 for r in b_e3 if PEDS.search(text(r['ws_id'])) or any(a <= 17 for a in ages(text(r['ws_id'])))), '| no abstract:', sum(1 for r in b_e3 if not abstract[r['ws_id']]))
b_rel = [r for r in bulk_rows if proxy_rel(r['ws_id'])]
P('   bulk Excludes that are proxy-relevant (wandering/torsion word + child cue):', len(b_rel), '| R1 advanced', sum(1 for r in b_rel if r['R1_JunShu_decision'] in ADV))
for r in b_rel:
    flag(r, 'R2', 'G1 bulk Exclude but proxy-relevant', r['R2_FeiPeng_decision'], r['R2_FeiPeng_reason'])
for r in b_e3:
    if not adult_support(r['ws_id']):
        flag(r, 'R2', 'G2 bulk E3 without adult evidence', r['R2_FeiPeng_decision'], r['R2_FeiPeng_reason'])
mb = [r for r in res if r['R2_FeiPeng_decision'] == 'Maybe']
P('\nR2 Maybe:', len(mb), '| with no wandering/torsion word in text', sum(1 for r in mb if not WSRE.search(text(r['ws_id']))), '| animal word and no child cue', sum(1 for r in mb if ANIMAL.search(text(r['ws_id'])) and not PEDS.search(text(r['ws_id']))), '| record type PAT', sum(1 for r in mb if rtype[r['ws_id']] == 'PAT'))
mb1 = [r for r in res if r['R1_JunShu_decision'] == 'Maybe']
P('R1 Maybe:', len(mb1), '| with no wandering/torsion word in text', sum(1 for r in mb1 if not WSRE.search(text(r['ws_id']))), '| animal word and no child cue', sum(1 for r in mb1 if ANIMAL.search(text(r['ws_id'])) and not PEDS.search(text(r['ws_id']))))

with open(F + 'reviewer_issue_records.csv', 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f)
    w.writerow(['ws_id', 'reviewer', 'issue', 'decision', 'reason', 'title'])
    for x in flags:
        w.writerow(x)
P('\nflag rows written:', len(flags), dict(collections.Counter((x[1], x[2]) for x in flags)))
open(F + 'reviewer_issue_check.txt', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print('\n'.join(out))
