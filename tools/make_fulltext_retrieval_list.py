"""Build the full-text retrieval list (17 Oct 2026).

List = records advanced after the two blind adjudication sheets (fulltext_list_final.csv)
     + the 27 conflict records that the third reviewer excluded as E4 while the second reviewer advanced
       (e4_safety_net_candidates.csv; added by the author's decision of 17 Oct 2026, a documented deviation).
Usage (from the repo root): python3 -I tools/make_fulltext_retrieval_list.py [FOLDER]   (default search/screening/rescreen/)
Reads  FOLDER/fulltext_list_final.csv, FOLDER/e4_safety_net_candidates.csv, search/dedup/records_deduplicated.ris
Writes FOLDER/fulltext_retrieval_list.csv with language group, abstract flag, source and retrieval class
  (retrieval class: 'retrieve' for English or Chinese; 'L other language' for the rest, which the protocol lists and counts but does not extract).
"""
import csv, re, sys, collections
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
with open(F + 'fulltext_retrieval_list.csv', 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f)
    w.writerow(['ws_id', 'year', 'title', 'language_group', 'has_abstract', 'record_type', 'source', 'retrieval_class'])
    for k, src in rows:
        g, ab, ty, ti, yr = info[k]
        w.writerow([k, yr.group(1) if yr else '', ti, g, ab, ty, src, 'retrieve' if g in ('English', 'Chinese') else 'L other language'])
c = collections.Counter(info[k][0] for k, _ in rows)
print(len(rows), 'records;', 'added from the E4 safety net:', len(added), '| languages', dict(c), '| to retrieve:', c['English'] + c['Chinese'])
