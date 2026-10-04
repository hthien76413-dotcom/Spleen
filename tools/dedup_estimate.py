"""Estimate the number of duplicates across the six database exports in ../search.

This is an ESTIMATE to cross-check the formal EndNote deduplication; it does not replace it.
Usage:  python3 dedup_estimate.py            (run from tools/; writes ../search/dedup_estimate/)

Tiers, applied in this order (each merge removes one record from the unique count):
  T1  identical DOI
  T2  identical normalised title + same first author + year within +/-1
      (or, when an author is missing, a long title (>=40 characters) and the same year)
  T2b identical normalised English title (CBM's parallel English title) vs an English record,
      year within +/-1, title >= 25 characters (cross-script duplicates)
  T3  similar title (difflib ratio >= 0.90) + same first author + year within +/-1
Pairs with an identical title but a different author or year are NOT merged; they are listed
as ambiguous for manual review.
"""
import csv
import difflib
import os
import re
import unicodedata
from collections import Counter, defaultdict

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "search")
OUT = os.path.join(BASE, "dedup_estimate")
os.makedirs(OUT, exist_ok=True)


def strip_acc(s):
    s = unicodedata.normalize("NFKD", s)
    return "".join(c for c in s if not unicodedata.combining(c))


def norm_title(s):
    s = re.sub(r"<[^>]+>", "", s or "")
    s = unicodedata.normalize("NFKC", strip_acc(s)).lower()
    return re.sub(r"[\W_]+", "", s)


def norm_doi(d):
    d = (d or "").strip().lower()
    d = re.sub(r"^(https?://(dx\.)?doi\.org/|doi:\s*)", "", d)
    return d.rstrip(".")


def surname(a, chinese=False):
    a = (a or "").strip()
    if not a:
        return ""
    if chinese or re.search(r"[一-鿿]", a):
        return re.sub(r"\s+", "", a)
    a = strip_acc(a).lower()
    return re.split(r"[,\s]", a)[0]


def year_of(s):
    m = re.search(r"(1[89]\d\d|20\d\d)", s or "")
    return int(m.group(1)) if m else None


recs = []


def add(source, rid, title, author, year, doi, journal, alt=""):
    zh = bool(re.search(r"[一-鿿]", author or "")) or bool(re.search(r"[一-鿿]", title or ""))
    recs.append(dict(source=source, rid=rid, title=(title or "").strip(), nt=norm_title(title),
                     author=surname(author, zh), year=year_of(str(year or "")), doi=norm_doi(doi),
                     journal=(journal or "").strip(), alt=norm_title(alt), zh=zh))


# ---------------------------------------------------------------- PubMed (.nbib)
def parse_nbib(path):
    t = open(path, encoding="utf-8-sig").read()
    for blk in re.split(r"\n(?=PMID- )", t):
        if not blk.strip():
            continue
        f = defaultdict(list)
        last = None
        for ln in blk.split("\n"):
            m = re.match(r"^([A-Z]{2,4})\s*- (.*)$", ln)
            if m:
                last = m.group(1)
                f[last].append(m.group(2))
            elif ln.startswith("      ") and last:
                f[last][-1] += " " + ln.strip()
        doi = next((re.sub(r" \[doi\]$", "", a) for a in f["AID"] if a.endswith("[doi]")), "")
        au = (f["FAU"] or f["AU"] or [""])[0]
        add("PubMed", (f["PMID"] or [""])[0], " ".join(f["TI"]), au,
            (f["DP"] or [""])[0], doi, (f["TA"] or f["JT"] or [""])[0])


# ---------------------------------------------------------------- RIS (WoS, Scopus)
def parse_ris(path, source):
    t = open(path, encoding="utf-8-sig").read().replace("\r", "")
    for i, blk in enumerate(r for r in re.split(r"\nER  - *\n?", t) if r.strip()):
        f = defaultdict(list)
        for m in re.finditer(r"^([A-Z0-9]{2})  - (.*)$", blk, re.M):
            f[m.group(1)].append(m.group(2))
        rid = (f["AN"] or [""])[0]
        if not rid:
            m = re.search(r"publications/(\d+)", (f["UR"] or [""])[0])
            rid = m.group(1) if m else str(i)
        add(source, rid, (f["TI"] or [""])[0], (f["AU"] or [""])[0], (f["PY"] or f["Y1"] or [""])[0],
            (f["DO"] or [""])[0], (f["T2"] or f["JO"] or [""])[0])


# ---------------------------------------------------------------- EndNote-tagged text (CNKI, Wanfang, CBM)
def parse_tagged(path, source):
    t = open(path, encoding="utf-8-sig").read().replace("\r", "")
    for i, blk in enumerate(b for b in re.split(r"\n(?=%0 )", t) if b.strip()):
        f = defaultdict(list)
        for ln in blk.split("\n"):
            m = re.match(r"^%(.) (.*)$", ln)
            if m:
                f[m.group(1)].append(m.group(2).strip())
        authors = f["A"]
        if len(authors) == 1 and ";" in authors[0]:
            authors = [a.strip() for a in authors[0].split(";")]
        rid = (f["]"] or f["U"] or [str(i)])[0]
        add(source, rid, (f["T"] or [""])[0], (authors or [""])[0], (f["D"] or [""])[0],
            (f["R"] or [""])[0], (f["J"] or [""])[0], alt=(f["Q"] or [""])[0])


parse_nbib(os.path.join(BASE, "pubmed", "wandering_spleen_pubmed_1263.nbib"))
parse_ris(os.path.join(BASE, "wos", "wandering_spleen_wos_750.ris"), "WoS")
parse_ris(os.path.join(BASE, "scopus", "wandering_spleen_scopus_1563.ris"), "Scopus")
parse_tagged(os.path.join(BASE, "cnki", "wandering_spleen_cnki_486.enw"), "CNKI")
parse_tagged(os.path.join(BASE, "wanfang", "wandering_spleen_wanfang_423.txt"), "Wanfang")
parse_tagged(os.path.join(BASE, "cbm", "wandering_spleen_cbm.txt"), "CBM")

EXPECT = {"PubMed": 1263, "WoS": 750, "Scopus": 1563, "CNKI": 486, "Wanfang": 423, "CBM": 421}
got = Counter(r["source"] for r in recs)
for k, v in EXPECT.items():
    assert got[k] == v, (k, got[k], v)

# ---------------------------------------------------------------- union-find
parent = list(range(len(recs)))


def find(x):
    while parent[x] != x:
        parent[x] = parent[parent[x]]
        x = parent[x]
    return x


tier_of = {}      # record index -> tier at which it was merged into an earlier cluster
merges = Counter()


def union(a, b, tier):
    ra, rb = find(a), find(b)
    if ra == rb:
        return False
    parent[rb] = ra
    merges[tier] += 1
    tier_of[b] = tier_of.get(b, tier)
    return True


def ydiff_ok(a, b, tol=1):
    return a["year"] is not None and b["year"] is not None and abs(a["year"] - b["year"]) <= tol


# T1 DOI
by_doi = defaultdict(list)
for i, r in enumerate(recs):
    if r["doi"]:
        by_doi[r["doi"]].append(i)
for ids in by_doi.values():
    for j in ids[1:]:
        union(ids[0], j, "T1 DOI")

# T2 exact title
ambiguous = []
by_title = defaultdict(list)
for i, r in enumerate(recs):
    if len(r["nt"]) >= 6:
        by_title[r["nt"]].append(i)
for nt, ids in by_title.items():
    for x in range(len(ids)):
        for y in range(x + 1, len(ids)):
            a, b = recs[ids[x]], recs[ids[y]]
            if find(ids[x]) == find(ids[y]):
                continue
            if a["author"] and b["author"]:
                same_au = a["author"] == b["author"]
                if same_au and ydiff_ok(a, b):
                    union(ids[x], ids[y], "T2 title+author+year")
                else:
                    ambiguous.append((ids[x], ids[y], "same title, different author" if not same_au else "same title and author, year differs >1"))
            else:
                if len(nt) >= 40 and a["year"] is not None and a["year"] == b["year"]:
                    union(ids[x], ids[y], "T2 title+author+year")
                else:
                    ambiguous.append((ids[x], ids[y], "same title, author missing"))

# T2b cross-script: CBM English title vs English record titles
en_by_title = defaultdict(list)
for i, r in enumerate(recs):
    if not r["zh"] and len(r["nt"]) >= 25:
        en_by_title[r["nt"]].append(i)
for i, r in enumerate(recs):
    if r["alt"] and len(r["alt"]) >= 25:
        for j in en_by_title.get(r["alt"], []):
            if ydiff_ok(r, recs[j]):
                union(j, i, "T2b English title (cross-script)")

# T3 fuzzy title with same author and year +/-1
by_au = defaultdict(list)
for i, r in enumerate(recs):
    if r["author"] and r["nt"]:
        by_au[r["author"]].append(i)
for au, ids in by_au.items():
    for x in range(len(ids)):
        for y in range(x + 1, len(ids)):
            a, b = recs[ids[x]], recs[ids[y]]
            if find(ids[x]) == find(ids[y]) or not ydiff_ok(a, b):
                continue
            if abs(len(a["nt"]) - len(b["nt"])) > 0.25 * max(len(a["nt"]), len(b["nt"])):
                continue
            if difflib.SequenceMatcher(None, a["nt"], b["nt"]).ratio() >= 0.90:
                union(ids[x], ids[y], "T3 similar title+author+year")

# ---------------------------------------------------------------- summary
clusters = defaultdict(list)
for i in range(len(recs)):
    clusters[find(i)].append(i)
n_rec, n_uni = len(recs), len(clusters)
lines = []
P = lines.append
P("# Deduplication estimate (not the formal EndNote deduplication)")
P("")
P(f"Records before deduplication: {n_rec}  |  estimated unique records: {n_uni}  |  estimated duplicates: {n_rec - n_uni}")
P("")
P("## Merges by tier (in the order applied)")
for tname in ["T1 DOI", "T2 title+author+year", "T2b English title (cross-script)", "T3 similar title+author+year"]:
    P(f"- {tname}: {merges[tname]}")
why = Counter(w for _, _, w in ambiguous)
P(f"- identical-title pairs NOT merged (listed in dedup_estimate_ambiguous_pairs.csv): {len(ambiguous)}")
for k, v in why.most_common():
    P(f"    - {k}: {v}")
P("  (the large 'different author' count comes from generic titles such as 'Wandering spleen.' used by many different papers; only the 'author missing' and 'year differs' pairs need a manual look)")
P(f"- cumulative unique records: after T1 only {n_rec - merges['T1 DOI']}; after T1+T2 {n_rec - merges['T1 DOI'] - merges['T2 title+author+year']}; after all tiers {n_uni}")
P("")
P("## Per source")
P("| source | records | distinct records within source | within-source duplicates | records also found in another source | found only in this source |")
P("|---|---|---|---|---|---|")
srcs = ["PubMed", "WoS", "Scopus", "CNKI", "Wanfang", "CBM"]
cl_sources = {c: {recs[i]["source"] for i in ids} for c, ids in clusters.items()}
for s in srcs:
    ids_s = [i for i in range(n_rec) if recs[i]["source"] == s]
    cl_s = {find(i) for i in ids_s}
    only = sum(1 for c in cl_s if cl_sources[c] == {s})
    P(f"| {s} | {len(ids_s)} | {len(cl_s)} | {len(ids_s) - len(cl_s)} | {len(cl_s) - only} | {only} |")
P("")
P("## Unique records by number of sources that found them")
cnt = Counter(len(v) for v in cl_sources.values())
for k in sorted(cnt):
    P(f"- found by {k} source(s): {cnt[k]}")
P("")
EN, ZH = {"PubMed", "WoS", "Scopus"}, {"CNKI", "Wanfang", "CBM"}
en_only = sum(1 for v in cl_sources.values() if v <= EN)
zh_only = sum(1 for v in cl_sources.values() if v <= ZH)
both = n_uni - en_only - zh_only
P(f"- unique records found only by the three English-language sources: {en_only}")
P(f"- unique records found only by the three Chinese-language sources: {zh_only}")
P(f"- unique records found by both groups (cross-script matches): {both}")
P("")
P("## Pairwise overlap (unique records found by both sources)")
P("| | " + " | ".join(srcs) + " |")
P("|---|" + "---|" * len(srcs))
for a in srcs:
    P(f"| {a} | " + " | ".join(str(sum(1 for v in cl_sources.values() if a in v and b in v)) for b in srcs) + " |")
P("")
P("## Expected PRISMA numbers if EndNote agrees with this estimate")
P(f"identified from six databases: {n_rec}; duplicates removed: {n_rec - n_uni}; records to screen: {n_uni}")
open(os.path.join(OUT, "dedup_estimate_summary.md"), "w", encoding="utf-8").write("\n".join(lines) + "\n")

with open(os.path.join(OUT, "dedup_estimate_records.csv"), "w", newline="", encoding="utf-8-sig") as fh:
    w = csv.writer(fh)
    w.writerow(["cluster_id", "source", "source_id", "merged_by_tier", "year", "first_author", "doi", "journal", "title"])
    cid = {c: n for n, c in enumerate(sorted(clusters, key=lambda c: min(clusters[c])), 1)}
    for i, r in enumerate(recs):
        w.writerow([cid[find(i)], r["source"], r["rid"], tier_of.get(i, ""), r["year"] or "", r["author"], r["doi"], r["journal"], r["title"]])

with open(os.path.join(OUT, "dedup_estimate_ambiguous_pairs.csv"), "w", newline="", encoding="utf-8-sig") as fh:
    w = csv.writer(fh)
    w.writerow(["reason", "source_a", "id_a", "year_a", "author_a", "source_b", "id_b", "year_b", "author_b", "title"])
    for a, b, why in ambiguous:
        ra, rb = recs[a], recs[b]
        w.writerow([why, ra["source"], ra["rid"], ra["year"] or "", ra["author"], rb["source"], rb["rid"], rb["year"] or "", rb["author"], ra["title"]])

print("\n".join(lines))
