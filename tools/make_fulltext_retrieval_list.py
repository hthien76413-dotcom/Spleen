"""Build the full-text retrieval list (17 Oct 2026).

List = records advanced after the two blind adjudication sheets (fulltext_list_final.csv)
     + the 27 conflict records that the third reviewer excluded as E4 while the second reviewer advanced
       (e4_safety_net_candidates.csv; added by the author's decision of 17 Oct 2026, a documented deviation).
Usage (from the repo root): python3 -I tools/make_fulltext_retrieval_list.py [FOLDER]   (default search/screening/rescreen/)
Reads  FOLDER/fulltext_list_final.csv, FOLDER/e4_safety_net_candidates.csv, search/dedup/records_deduplicated.ris
Writes FOLDER/fulltext_retrieval_list.csv with language group, abstract flag, source and retrieval class, and
       FOLDER/fulltext_retrieval_summary.txt with the counts needed for the PRISMA flow.
Retrieval class, applied in this order (18 Oct 2026 version; the date rule was decided by the author on 17 Oct 2026, before any
full text was retrieved or any data were extracted, and is a documented deviation from the registered eligibility criteria):
  'Y published before 2000' - publication year in the database record is earlier than 2000: not sought, not judged;
  'L other language'        - language is neither English nor Chinese (listed and counted, not extracted, protocol Section 10);
  'retrieve'                - everything else (English or Chinese, published in 2000 or later).
A record without a publication year would be retrieved (none occurs in the current list).
"""
import csv, re, sys, collections
CUTOFF_YEAR = 2000  # records published before this year are not sought
F = sys.argv[1].rstrip('/') + '/' if len(sys.argv) > 1 else 'search/screening/rescreen/'
base = list(csv.DictReader(open(F + 'fulltext_list_final.csv', encoding='utf-8-sig')))
e4 = list(csv.DictReader(open(F + 'e4_safety_net_candidates.csv', encoding='utf-8-sig')))
info = {}
for blk in open('search/dedup/records_deduplicated.ris', encoding='utf-8-sig').read().split('\nER  -'):
    m = re.search(r'^ID  - (.*)$', blk, re.M)
    if not m:
        continue
    la = re.search(r'^LA  - (.*)$', blk, re.M)
    l = la.group(1).strip().lower() if la else 'none'
    grp = 'English' if l in ('eng', 'english') else 'Chinese' if l in ('chinese', 'chi') else 'Other'
    ab = ' '.join(re.findall(r'^AB  - (.*)$', blk, re.M)).strip()
    ty = re.search(r'^TY  - (.*)$', blk, re.M)
    info[m.group(1)] = (grp, 'yes' if ab else 'no', ty.group(1) if ty else '', ' '.join(re.findall(r'^TI  - (.*)$', blk, re.M)), re.search(r'^PY  - (\d{4})', blk, re.M))
rows = [(r['ws_id'], r['source']) for r in base]
have = {w for w, _ in rows}
added = [(r['ws_id'], 'E4 safety net: third reviewer excluded as E4, second reviewer advanced (author decision 17 Oct 2026)') for r in e4 if r['ws_id'] not in have]
rows += added
def klass(g, yr):
    if yr and int(yr.group(1)) < CUTOFF_YEAR:
        return 'Y published before %d' % CUTOFF_YEAR
    return 'retrieve' if g in ('English', 'Chinese') else 'L other language'
out = []
with open(F + 'fulltext_retrieval_list.csv', 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f)
    w.writerow(['ws_id', 'year', 'title', 'language_group', 'has_abstract', 'record_type', 'source', 'retrieval_class'])
    for k, src in rows:
        g, ab, ty, ti, yr = info[k]
        c = klass(g, yr)
        out.append((k, g, ab, c, src))
        w.writerow([k, yr.group(1) if yr else '', ti, g, ab, ty, src, c])
cls = collections.Counter(c for _, _, _, c, _ in out)
lines = ['Full-text retrieval list summary (date rule: published before %d is not sought)' % CUTOFF_YEAR,
         'Records on the list: %d (from the blind adjudication: %d; E4 safety net added: %d)' % (len(out), len(base), len(added)),
         'By retrieval class: ' + ', '.join('%s %d' % kv for kv in sorted(cls.items()))]
for c in sorted(cls):
    s = [o for o in out if o[3] == c]
    lines.append('  %s: %d | English %d, Chinese %d, other %d | with abstract %d, without %d' % (
        c, len(s), sum(1 for o in s if o[1] == 'English'), sum(1 for o in s if o[1] == 'Chinese'), sum(1 for o in s if o[1] == 'Other'),
        sum(1 for o in s if o[2] == 'yes'), sum(1 for o in s if o[2] == 'no')))
e4set = [o for o in out if o[4].startswith('E4 safety net')]
lines.append('E4 safety-net records: %d, of which to retrieve %d, not sought because of the date rule %d, other language %d' % (
    len(e4set), sum(1 for o in e4set if o[3] == 'retrieve'), sum(1 for o in e4set if o[3].startswith('Y')), sum(1 for o in e4set if o[3].startswith('L'))))
open(F + 'fulltext_retrieval_summary.txt', 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
print('\n'.join(lines))
