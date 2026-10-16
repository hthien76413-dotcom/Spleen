"""Check each reviewer's formal title/abstract decisions against the 53 hand-collected pilot papers.

The pilot papers (literature-pilot-extraction-53-papers.csv) are known paediatric wandering-spleen reports. The 45 papers with
at least one 'IPD-included' row are eligible by construction and must advance to full text (Include or Maybe); an Exclude on
one of them is a false exclusion. The paper -> WS id mapping below was made by first author, year and title (checked by reading
the titles, 12 Oct 2026) and is not an independent gold standard: the pilot papers were found by hand and are probably easier
to recognise than the average eligible record, so miss rates here are likely optimistic.

Usage: python3 -I tools/pilot_reference_check.py   (run from the repo root; needs search/screening/formal/screening_results_all.csv)
Writes search/screening/formal/pilot_reference_set_decisions.csv and prints the counts.
"""
import csv, collections, math
M = {'01':'WS0814','02':'WS0826','03':'WS2145','04':'WS0741','05':'WS0719','06':'WS0681','07':'WS0678','08':'WS0664','09':'WS0683','10':'WS0645','11':'WS0653','12':'WS0616','13':'WS0624','14':'WS0623','15':'WS0619','16':'WS0630','17':'WS0601','18':'WS0580','19':'WS0585','20':'WS0552','21':'WS0553','22':'WS0550','23':'WS0537','24':'WS0541','25':'WS2011','26':'WS0482','27':'WS0474','28':'WS0489','29':'WS0432','30':'WS0411','31':'WS0449','32':'WS0399','33':'WS0359','34':'WS0342','35':'WS0321','36':'WS1925','37':'WS0324','38':'WS0237','39':'WS1902','40':'WS0212','41':'WS0228','42':'WS0229','43':'WS1890','44':'WS0168','45':'WS0173','46':'WS0186','47':'WS0160','48':'WS0143','49':'WS0141','50':'WS0151','51':'WS1868','52':'WS0093','53':'WS0044'}
assert len(M) == 53 and len(set(M.values())) == 53
pil = list(csv.DictReader(open('literature-pilot-extraction-53-papers.csv', encoding='utf-8-sig')))
status = collections.defaultdict(set); study = {}
for r in pil:
    status[r['paper_no']].add(r['status']); study.setdefault(r['paper_no'], r['study'])
res = {r['ws_id']: r for r in csv.DictReader(open('search/screening/formal/screening_results_all.csv', encoding='utf-8-sig'))}
out = []
for n in sorted(M):
    r = res[M[n]]
    out.append([n, study[n], M[n], 'IPD-included' if 'IPD-included' in status[n] else 'other (review/aggregate/duplicate)',
                r['R1_JunShu_decision'], r['R1_JunShu_reason'], r['R2_FeiPeng_decision'], r['R2_FeiPeng_reason']])
with open('search/screening/formal/pilot_reference_set_decisions.csv', 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f); w.writerow(['pilot_paper_no', 'study', 'ws_id', 'pilot_status', 'R1_decision', 'R1_reason', 'R2_decision', 'R2_reason']); w.writerows(out)
ref = [o for o in out if o[3] == 'IPD-included']
def wilson(k, n, z=1.96):
    p = k / n; d = 1 + z * z / n; c = p + z * z / (2 * n); h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (c - h) / d, (c + h) / d
for lab, i in (('R1 Jun Shu', 4), ('R2 Fei Peng', 6)):
    k = sum(1 for o in ref if o[i] == 'Exclude'); lo, hi = wilson(k, len(ref))
    print(f'{lab}: false exclusions {k}/{len(ref)} = {k/len(ref):.1%} (Wilson 95% CI {lo:.1%}-{hi:.1%})')
both = sum(1 for o in ref if o[4] == 'Exclude' and o[6] == 'Exclude'); either = sum(1 for o in ref if o[4] == 'Exclude' or o[6] == 'Exclude')
print('excluded by both:', both, '; excluded by at least one:', either, '; missed if "advance if either advances":', both)
try:
    from scipy.stats import fisher_exact
    k1 = sum(1 for o in ref if o[4] == 'Exclude'); k2 = sum(1 for o in ref if o[6] == 'Exclude')
    print('Fisher exact two-sided p =', round(fisher_exact([[k1, len(ref) - k1], [k2, len(ref) - k2]])[1], 3))
except Exception as e:
    print('scipy not available:', e)
