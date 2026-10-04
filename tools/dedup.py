"""Deduplicate the six database exports in ../search and write a Rayyan-ready RIS file plus an audit trail.

Usage:  python3 dedup.py            (run from tools/; writes ../search/dedup/)

Tiers, applied in this order (each merge removes one record from the unique count):
  T1  identical DOI
  T2  identical normalised title + same first author + year within +/-1
      (or, when an author is missing, a long title (>=40 characters) and the same year)
  T2b identical normalised English title (CBM's parallel English title) vs an English record,
      year within +/-1, title >= 25 characters (cross-script duplicates)
  T3  similar title (difflib ratio >= 0.90) + same first author + year within +/-1
  T4  same first author + same year + same volume + same first page (all present)
  T5  identical normalised title + year within +/-1 + same volume + compatible pages (a single page inside the
      other record's range counts as compatible); different journal/volume/pages are kept apart
  T6  Chinese records: identical title + same year + same journal + compatible pages
  MANUAL  decisions in DECISIONS below, taken after reading the residual pairs (listed in the audit files)
Identical-title pairs that match none of these are NOT merged and are listed for review.

The master record of each cluster is the one with an abstract, then a DOI, then the source priority
PubMed > Scopus > WoS > Wanfang > CNKI > CBM; missing fields are filled from the other members.
"""
import csv
import difflib
import os
import re
import unicodedata
from collections import Counter, defaultdict

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "search")
OUT = os.path.join(BASE, "dedup")
os.makedirs(OUT, exist_ok=True)

# Manual merges decided on 4 Oct 2026 after reading the residual pairs: (source_a, title_a, source_b, title_b, reason).
# Records are matched by source and normalised title prefix. Every other residual pair was reviewed and kept apart.
DECISIONS = [
    ("CNKI", "超声检查腹部脏器的适应证有哪些", "Wanfang", "超声检查腹部脏器的适应证有哪些",
     "same journal (护士进修杂志), year and page 1160; Wanfang has no volume and a non-author in the author field"),
    ("CNKI", "耐受性树突状细胞诱导移植脾免疫耐受的实验研究", "Wanfang", "耐受性树突状细胞诱导移植脾免疫耐受的实验研究",
     "same title and author, year missing in CNKI (animal experiment, irrelevant to the review)"),
    ("CNKI", "游走脾并脾蒂扭转二例", "Wanfang", "游走脾并脾蒂扭转二例",
     "same title, journal (中华放射学杂志) and year; CNKI first page differs from Wanfang (CNKI pagination unreliable)"),
]


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
    if re.search(r"[一-鿿]", a):
        return re.sub(r"\s+", "", a)
    a = strip_acc(a).lower()
    return re.split(r"[,\s]", a)[0]


def year_of(s):
    m = re.search(r"(1[89]\d\d|20\d\d)", s or "")
    return int(m.group(1)) if m else None


def first_page(p):
    m = re.search(r"\d+", (p or "").split("-")[0])
    return m.group(0) if m else ""


def page_range(p):
    nums = [int(x) for x in re.findall(r"\d+", p or "")]
    if not nums:
        return None
    return (nums[0], nums[1] if len(nums) > 1 and nums[1] >= nums[0] else nums[0])


def norm_vol(v):
    return re.sub(r"^0+(?=\d)", "", (v or "").strip())


def hard_blocked(a, b):
    """True when two records are certainly different items:
    - both volumes present and different, with first pages more than 10 apart; or
    - two records of the SAME database whose pages are incompatible, or whose first authors differ
      (a database lists one article once; distinct items on the same page, e.g. a letter and a reply, stay apart)."""
    if a["source"] == b["source"]:
        if a["pages"] and b["pages"] and not pages_compatible(a["pages"], b["pages"]):
            return True
        if a["author"] and b["author"] and a["author"] != b["author"]:
            return True
    ra, rb = page_range(a["pages"]), page_range(b["pages"])
    if ra and rb and not pages_compatible(a["pages"], b["pages"]) and abs(ra[0] - rb[0]) > 10:
        if a["vol"] and b["vol"] and a["vol"] != b["vol"]:
            return True
    return False


def pages_compatible(a, b):
    ra, rb = page_range(a), page_range(b)
    if not ra or not rb:
        return False
    return ra[0] == rb[0] or (ra[0] == ra[1] and rb[0] <= ra[0] <= rb[1]) or (rb[0] == rb[1] and ra[0] <= rb[0] <= ra[1])


TYPE_MAP = {"journal article": "JOUR", "patent": "PAT", "thesis": "THES", "conference proceedings": "CONF",
            "newspaper article": "NEWS", "book section": "CHAP", "book": "BOOK", "generic": "GEN"}
recs = []


def add(source, rid, title, authors, year, doi, journal, vol="", issue="", pages="", abstract="", kws=None,
        lang="", url="", rtype="JOUR", alt=""):
    authors = [a.strip() for a in authors if a and a.strip()]
    zh = bool(re.search(r"[一-鿿]", (authors[0] if authors else "") + (title or "")))
    recs.append(dict(source=source, rid=rid, title=(title or "").strip(), nt=norm_title(title), authors=authors,
                     author=surname(authors[0] if authors else "", zh), year=year_of(str(year or "")),
                     doi=norm_doi(doi), journal=(journal or "").strip(), vol=norm_vol(vol),
                     issue=(issue or "").strip(), pages=(pages or "").strip(), fp=first_page(pages),
                     abstract=(abstract or "").strip(), kws=kws or [], lang=lang, url=url, rtype=rtype,
                     alt=norm_title(alt), zh=zh))


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
        pmid = (f["PMID"] or [""])[0]
        add("PubMed", pmid, " ".join(f["TI"]), f["FAU"] or f["AU"], (f["DP"] or [""])[0], doi,
            (f["JT"] or f["TA"] or [""])[0], (f["VI"] or [""])[0], (f["IP"] or [""])[0], (f["PG"] or [""])[0],
            " ".join(f["AB"]), f["OT"], (f["LA"] or [""])[0], f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/")


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
        pages = (f["SP"] or [""])[0] + (("-" + f["EP"][0]) if f["EP"] else "")
        ty = (f["TY"] or ["JOUR"])[0]
        ty = ty if re.fullmatch(r"[A-Z]{3,4}", ty) else ("CHAP" if "BOOK_CHAPTER" in ty else "JOUR")
        add(source, rid, (f["TI"] or [""])[0], f["AU"], (f["PY"] or f["Y1"] or [""])[0], (f["DO"] or [""])[0],
            (f["T2"] or f["JO"] or [""])[0], (f["VL"] or [""])[0], (f["IS"] or [""])[0], pages,
            " ".join(f["AB"]), f["KW"], (f["LA"] or [""])[0], (f["UR"] or [""])[0], ty)


def parse_tagged(path, source):
    t = open(path, encoding="utf-8-sig").read().replace("\r", "")
    for i, blk in enumerate(b for b in re.split(r"\n(?=%0 )", t) if b.strip()):
        f = defaultdict(list)
        for ln in blk.split("\n"):
            m = re.match(r"^%(.) (.*)$", ln)
            if m:
                f[m.group(1)].append(m.group(2).strip())
        authors = f["A"]
        if len(authors) == 1 and re.search(r"[\u4e00-\u9fff]", authors[0]) and re.search(r"[;；,，、]", authors[0]):
            authors = [a.strip() for a in re.split(r"[;；,，、]", authors[0]) if a.strip()]
        elif len(authors) == 1 and ";" in authors[0]:
            authors = [a.strip() for a in authors[0].split(";")]
        kws = [k.strip() for x in f["K"] for k in re.split(r"[;；]", x) if k.strip()]
        rid = (f["]"] or f["U"] or [str(i)])[0]
        pages = (f["P"] or f["&"] or [""])[0]
        rtype = TYPE_MAP.get((f["0"] or ["generic"])[0].lower(), "GEN")
        lang = {"chi": "Chinese", "eng": "English"}.get((f["G"] or [""])[0], "Chinese")
        add(source, rid, (f["T"] or [""])[0], authors, (f["D"] or [""])[0], (f["R"] or [""])[0],
            (f["J"] or [""])[0], (f["V"] or [""])[0], (f["N"] or [""])[0], pages, " ".join(f["X"]), kws, lang,
            (f["U"] or [""])[0], rtype, alt=(f["Q"] or [""])[0])


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
key_of = {(r["source"], r["rid"]): i for i, r in enumerate(recs)}
assert len(key_of) == len(recs), "source ids are not unique"

parent = list(range(len(recs)))


def find(x):
    while parent[x] != x:
        parent[x] = parent[parent[x]]
        x = parent[x]
    return x


tier_of, merges = {}, Counter()


members = {}


def cluster_blocked(a, b):
    ma = members.get(find(a), [find(a)])
    mb = members.get(find(b), [find(b)])
    return any(hard_blocked(recs[p], recs[q]) for p in ma for q in mb)


def union(a, b, tier):
    ra, rb = find(a), find(b)
    if ra == rb:
        return False
    parent[rb] = ra
    members[ra] = members.get(ra, [ra]) + members.pop(rb, [rb])
    merges[tier] += 1
    tier_of[b] = tier_of.get(b, tier)
    return True


def ydiff_ok(a, b, tol=1):
    return a["year"] is not None and b["year"] is not None and abs(a["year"] - b["year"]) <= tol


by_doi = defaultdict(list)
for i, r in enumerate(recs):
    if r["doi"]:
        by_doi[r["doi"]].append(i)
for ids in by_doi.values():
    for j in ids[1:]:
        union(ids[0], j, "T1 DOI")

pairs_title = []
by_title = defaultdict(list)
for i, r in enumerate(recs):
    if len(r["nt"]) >= 6:
        by_title[r["nt"]].append(i)
cands = []
for nt, ids in by_title.items():
    for x in range(len(ids)):
        for y in range(x + 1, len(ids)):
            a, b = recs[ids[x]], recs[ids[y]]
            if a["author"] and b["author"]:
                if a["author"] == b["author"] and ydiff_ok(a, b):
                    cands.append((ids[x], ids[y]))
                else:
                    pairs_title.append((ids[x], ids[y], "same title, different author" if a["author"] != b["author"] else "same title and author, year differs >1"))
            elif len(nt) >= 40 and a["year"] is not None and a["year"] == b["year"]:
                cands.append((ids[x], ids[y]))
            else:
                pairs_title.append((ids[x], ids[y], "same title, author missing"))
# pairs with positive citation evidence (compatible pages) first, then the rest
cands.sort(key=lambda p: 0 if pages_compatible(recs[p[0]]["pages"], recs[p[1]]["pages"]) else 1)
for a_i, b_i in cands:
    if find(a_i) == find(b_i):
        continue
    if cluster_blocked(a_i, b_i):
        pairs_title.append((a_i, b_i, "same title, author and year but conflicting volume/pages"))
    else:
        union(a_i, b_i, "T2 title+author+year")

en_by_title = defaultdict(list)
for i, r in enumerate(recs):
    if not r["zh"] and len(r["nt"]) >= 25:
        en_by_title[r["nt"]].append(i)
for i, r in enumerate(recs):
    if r["alt"] and len(r["alt"]) >= 25:
        for j in en_by_title.get(r["alt"], []):
            if ydiff_ok(r, recs[j]):
                union(j, i, "T2b English title (cross-script)")

by_au = defaultdict(list)
for i, r in enumerate(recs):
    if r["author"] and r["nt"]:
        by_au[r["author"]].append(i)
for au, ids in by_au.items():
    for x in range(len(ids)):
        for y in range(x + 1, len(ids)):
            a, b = recs[ids[x]], recs[ids[y]]
            if find(ids[x]) == find(ids[y]) or not ydiff_ok(a, b) or cluster_blocked(ids[x], ids[y]):
                continue
            if abs(len(a["nt"]) - len(b["nt"])) > 0.25 * max(len(a["nt"]), len(b["nt"])):
                continue
            if difflib.SequenceMatcher(None, a["nt"], b["nt"]).ratio() >= 0.90:
                union(ids[x], ids[y], "T3 similar title+author+year")

# T4: same first author + year + volume + first page
by_bib = defaultdict(list)
for i, r in enumerate(recs):
    if r["author"] and r["year"] and r["vol"] and r["fp"]:
        by_bib[(r["author"], r["year"], r["vol"], r["fp"])].append(i)
for ids in by_bib.values():
    for j in ids[1:]:
        if not cluster_blocked(ids[0], j):
            union(ids[0], j, "T4 author+year+volume+first page")

# T5: identical title, year within +/-1 (or missing), same volume and compatible pages
# (titles shorter than 6 characters, e.g. "游走脾", need the same year)
by_title_all = defaultdict(list)
for i, r in enumerate(recs):
    if len(r["nt"]) >= 2:
        by_title_all[r["nt"]].append(i)
for nt, ids in by_title_all.items():
    for x in range(len(ids)):
        for y in range(x + 1, len(ids)):
            a, b = recs[ids[x]], recs[ids[y]]
            if find(ids[x]) == find(ids[y]):
                continue
            if len(nt) < 6:
                year_ok = a["year"] is not None and a["year"] == b["year"]
            else:
                year_ok = ydiff_ok(a, b) or a["year"] is None or b["year"] is None
            if year_ok and a["vol"] and a["vol"] == b["vol"] and pages_compatible(a["pages"], b["pages"]) \
                    and not cluster_blocked(ids[x], ids[y]):
                union(ids[x], ids[y], "T5 title+volume+pages")

# T6: Chinese records, identical title, same year, same journal (normalised) and compatible pages
by_title_zh = defaultdict(list)
for i, r in enumerate(recs):
    if r["zh"] and len(r["nt"]) >= 2 and r["journal"] and r["pages"] and r["year"]:
        by_title_zh[(r["nt"], r["year"], norm_title(r["journal"]))].append(i)
for ids in by_title_zh.values():
    for x in range(len(ids)):
        for y in range(x + 1, len(ids)):
            if find(ids[x]) != find(ids[y]) and pages_compatible(recs[ids[x]]["pages"], recs[ids[y]]["pages"]) \
                    and not cluster_blocked(ids[x], ids[y]):
                union(ids[x], ids[y], "T6 Chinese title+year+journal+pages")

# manual decisions
for sa, ta, sb, tb, why in DECISIONS:
    ia = [i for i, r in enumerate(recs) if r["source"] == sa and r["nt"].startswith(norm_title(ta))]
    ib = [i for i, r in enumerate(recs) if r["source"] == sb and r["nt"].startswith(norm_title(tb))]
    assert ia and ib, (sa, ta, sb, tb)
    for a in ia:
        for b in ib:
            union(a, b, "MANUAL merge")

residual = [(a, b, why) for a, b, why in pairs_title if find(a) != find(b) and why != "same title, different author"]  # still apart after manual decisions
residual_diff_author = sum(1 for a, b, why in pairs_title if find(a) != find(b) and why == "same title, different author")

clusters = defaultdict(list)
for i in range(len(recs)):
    clusters[find(i)].append(i)
n_rec, n_uni = len(recs), len(clusters)

# conflicts inside merged clusters (non-DOI merges): different DOIs or different volume/first page
conflicts = []
for c, ids in clusters.items():
    if len(ids) < 2:
        continue
    dois = {recs[i]["doi"] for i in ids if recs[i]["doi"]}
    bib = {(recs[i]["vol"], recs[i]["fp"]) for i in ids if recs[i]["vol"] and recs[i]["fp"]}
    if len(dois) > 1:
        conflicts.append((c, "different DOIs in one cluster"))
    elif len(bib) > 1:
        conflicts.append((c, "different volume/first page in one cluster"))

SRC_PRIORITY = {"PubMed": 0, "Scopus": 1, "WoS": 2, "Wanfang": 3, "CNKI": 4, "CBM": 5}


def master_order(ids):
    return sorted(ids, key=lambda i: (0 if recs[i]["abstract"] else 1, 0 if recs[i]["doi"] else 1,
                                      SRC_PRIORITY[recs[i]["source"]], i))


cid_of = {}
ordered_clusters = sorted(clusters, key=lambda c: min(clusters[c]))
for n, c in enumerate(ordered_clusters, 1):
    cid_of[c] = f"WS{n:04d}"

# ---------------------------------------------------------------- RIS output (one record per cluster)
def ris_clean(s):
    return re.sub(r"\s+", " ", s or "").strip()


with open(os.path.join(OUT, "records_deduplicated.ris"), "w", encoding="utf-8", newline="\n") as fh:
    for c in ordered_clusters:
        ids = master_order(clusters[c])
        m = recs[ids[0]]

        def pick(field):
            for i in ids:
                if recs[i][field]:
                    return recs[i][field]
            return "" if field not in ("authors", "kws") else []

        title = m["title"] or pick("title")
        authors = pick("authors")
        doi = pick("doi")
        abstract = pick("abstract")
        kws = pick("kws")
        srcs = "; ".join(f"{recs[i]['source']} {recs[i]['rid']}" for i in sorted(clusters[c], key=lambda i: (SRC_PRIORITY[recs[i]['source']], i)))
        alt_titles = [recs[i]["title"] for i in ids if recs[i]["title"] and norm_title(recs[i]["title"]) != norm_title(title)]
        w = fh.write
        w(f"TY  - {m['rtype'] if m['rtype'] != 'JOUR' or True else 'JOUR'}\n")
        w(f"ID  - {cid_of[c]}\n")
        w(f"TI  - {ris_clean(title)}\n")
        for a in authors:
            w(f"AU  - {ris_clean(a)}\n")
        yr = pick("year")
        if yr:
            w(f"PY  - {yr}\n")
        j = pick("journal")
        if j:
            w(f"T2  - {ris_clean(j)}\n")
        for tag, field in (("VL", "vol"), ("IS", "issue")):
            v = pick(field)
            if v:
                w(f"{tag}  - {ris_clean(v)}\n")
        pg = pick("pages")
        if pg:
            sp, _, ep = pg.partition("-")
            w(f"SP  - {ris_clean(sp)}\n")
            if ep:
                w(f"EP  - {ris_clean(ep)}\n")
        if doi:
            w(f"DO  - {doi}\n")
        if abstract:
            w(f"AB  - {ris_clean(abstract)}\n")
        for k in kws:
            w(f"KW  - {ris_clean(k)}\n")
        lg = pick("lang")
        if lg:
            w(f"LA  - {lg}\n")
        u = pick("url")
        if u:
            w(f"UR  - {u}\n")
        note = f"Found in: {srcs}"
        if alt_titles:
            note += " | Other titles: " + " / ".join(ris_clean(t) for t in alt_titles[:3])
        w(f"N1  - {note}\n")
        w("ER  - \n\n")

# ---------------------------------------------------------------- audit files
with open(os.path.join(OUT, "dedup_map_all_records.csv"), "w", newline="", encoding="utf-8-sig") as fh:
    w = csv.writer(fh)
    w.writerow(["final_id", "source", "source_id", "role", "merged_by_tier", "year", "first_author", "doi", "volume", "first_page", "journal", "title"])
    for c in ordered_clusters:
        ids = master_order(clusters[c])
        for k, i in enumerate(ids):
            r = recs[i]
            w.writerow([cid_of[c], r["source"], r["rid"], "kept" if k == 0 else "duplicate", tier_of.get(i, ""), r["year"] or "", r["author"], r["doi"], r["vol"], r["fp"], r["journal"], r["title"]])

def pair_row(a, b, why):
    ra, rb = recs[a], recs[b]
    return [why, ra["source"], ra["rid"], ra["year"] or "", ra["author"], ra["journal"], ra["vol"], ra["pages"], ra["doi"],
            rb["source"], rb["rid"], rb["year"] or "", rb["author"], rb["journal"], rb["vol"], rb["pages"], rb["doi"], ra["title"], rb["title"]]


with open(os.path.join(OUT, "residual_pairs_for_review.csv"), "w", newline="", encoding="utf-8-sig") as fh:
    w = csv.writer(fh)
    w.writerow(["decision", "reason", "src_a", "id_a", "year_a", "author_a", "journal_a", "vol_a", "pages_a", "doi_a",
                "src_b", "id_b", "year_b", "author_b", "journal_b", "vol_b", "pages_b", "doi_b", "title_a", "title_b"])
    for a, b, why in pairs_title:
        if why == "same title, different author":
            continue
        dec = "merged (manual decision)" if find(a) == find(b) else "kept apart: different journal/volume/pages/year, or irrelevant (patent, animal study); reviewed 4 Oct 2026"
        w.writerow([dec] + pair_row(a, b, why))

with open(os.path.join(OUT, "cluster_conflicts_for_review.csv"), "w", newline="", encoding="utf-8-sig") as fh:
    w = csv.writer(fh)
    w.writerow(["final_id", "reason", "source", "source_id", "year", "first_author", "doi", "volume", "pages", "tier", "title"])
    for c, why in conflicts:
        for i in clusters[c]:
            r = recs[i]
            w.writerow([cid_of[c], why, r["source"], r["rid"], r["year"] or "", r["author"], r["doi"], r["vol"], r["pages"], tier_of.get(i, ""), r["title"]])

# ---------------------------------------------------------------- summary
lines = []
P = lines.append
P("# Deduplication result (script; to be verified in EndNote)")
P("")
P(f"Records before deduplication: {n_rec}  |  unique records after deduplication: {n_uni}  |  duplicates removed: {n_rec - n_uni}")
P("")
P("## Duplicates removed by tier (in the order applied)")
cum = n_rec
for tname in ["T1 DOI", "T2 title+author+year", "T2b English title (cross-script)", "T3 similar title+author+year",
              "T4 author+year+volume+first page", "T5 title+volume+pages", "T6 Chinese title+year+journal+pages", "MANUAL merge"]:
    cum -= merges[tname]
    P(f"- {tname}: {merges[tname]} (records left after this step: {cum})")
P(f"- identical-title pairs with a different author, correctly kept apart: {residual_diff_author}")
P(f"- manual merges: {merges['MANUAL merge']}; identical-title pairs reviewed and kept apart (different journal/volume/pages/year, patents, animal studies): {len(residual)} (all listed in residual_pairs_for_review.csv)")
P(f"- clusters with conflicting DOI or volume/page, listed for review: {len(conflicts)}")
P("")
P("## By source")
P("| source | records identified | duplicates within the source | unique records (clusters) that include this source | of which found only in this source |")
P("|---|---|---|---|---|")
cl_sources = {c: {recs[i]["source"] for i in ids} for c, ids in clusters.items()}
for s in ["PubMed", "WoS", "Scopus", "CNKI", "Wanfang", "CBM"]:
    ids_s = [i for i in range(n_rec) if recs[i]["source"] == s]
    cl_s = {find(i) for i in ids_s}
    only = sum(1 for c in cl_s if cl_sources[c] == {s})
    P(f"| {s} | {len(ids_s)} | {len(ids_s) - len(cl_s)} | {len(cl_s)} | {only} |")
P("")
P("## PRISMA numbers")
P(f"Records identified from six databases: {n_rec}. Duplicates removed: {n_rec - n_uni}. Records to screen: {n_uni}.")
P("")
P("## Fields in the final file")
fin = {c: master_order(ids) for c, ids in clusters.items()}
P(f"- with abstract (own or filled from a duplicate): {sum(1 for c, ids in fin.items() if any(recs[i]['abstract'] for i in ids))} of {n_uni}")
P(f"- with DOI: {sum(1 for c, ids in fin.items() if any(recs[i]['doi'] for i in ids))} of {n_uni}")
P(f"- Chinese-language records (by title/author script): {sum(1 for c, ids in fin.items() if recs[ids[0]]['zh'])}")
open(os.path.join(OUT, "dedup_summary.md"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
print("\n".join(lines))
