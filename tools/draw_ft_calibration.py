#!/usr/bin/env python3
"""Draw the 20-report calibration set for the full-text stage (guide section 12, decision D5).

Population: the 540 records of search/screening/rescreen/fulltext_retrieval_list.csv with retrieval_class = 'retrieve'
(English or Chinese, published in 2000 or later).
Required in the 20 (guide D5): at least 3 Chinese, at least 2 reviews, at least 3 series reports, plus 3 'D1-type' reports
(paediatric torsion without any wandering/ectopic/floating word in the title or abstract). The rest is drawn at random.

The draw is reproducible and does not depend on the Python version: within each stratum the records are ranked by
sha256(SEED | stratum | ws_id) and the first ones are taken. The final order is ranked by sha256(SEED | order | ws_id), so the
order in the list says nothing about the strata. The strata are KEYWORD PROXIES made by a script, not judgements about any
record; the reviewers decide each report on its full text.

Usage (from the repo root): python3 -I tools/draw_ft_calibration.py
Writes into search/screening/fulltext/:
  calibration_20_list.csv     for both reviewers: position, ws_id, year, language, has_abstract, title, doi, url (no strata, no source)
  calibration_20_key.csv      strata flags per record: NOT for the reviewers (keep it closed until both have finished)
  calibration_20_design.txt   seed, rules, pool sizes, what was drawn
"""
import ast
import csv
import hashlib
import os
import re
import collections

SEED = "20261018"
OUT = "search/screening/fulltext/"
LIST = "search/screening/rescreen/fulltext_retrieval_list.csv"
RIS = "search/dedup/records_deduplicated.ris"
PILOT = "tools/pilot_reference_check.py"
MIN = [("d1", 3), ("review", 2), ("chinese", 3), ("series", 3)]  # order of drawing
N = 20

WS_WORD = re.compile(r"wander|ectopic spleen|floating|migrat|movable|mobile|pelvic spleen|splenoptosis|ptosis|dystop|"
                     r"游走|游动|漂浮|下垂|异位脾|脾异位|活动脾|可动", re.I)
TORSION = re.compile(r"torsion|torted|twist|volvulus|扭转|蒂扭", re.I)
CHILD = re.compile(r"child|pediatric|paediatric|infant|neonat|newborn|toddler|boy|girl|adolescen|year-old|years old|"
                   r"儿童|小儿|患儿|婴|幼|新生儿|男孩|女孩", re.I)
REVIEW_TITLE = re.compile(r"review|综述|进展|overview", re.I)
NOT_REVIEW_TITLE = re.compile(r"case|report|series|例", re.I)
SERIES_EN = re.compile(r"\b(series|cohort|retrospective|multicent\w*|experience|cases)\b", re.I)
SERIES_ZH = re.compile(r"(\d{2,}|[三四五六七八九十]+)\s*例|回顾|病例分析")


def h(*parts):
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()


def read_ris():
    out = {}
    for blk in open(RIS, encoding="utf-8-sig").read().split("\nER  -"):
        m = re.search(r"^ID  - (.*)$", blk, re.M)
        if not m:
            continue

        def one(tag):
            x = re.search(r"^%s  - (.*)$" % tag, blk, re.M)
            return x.group(1).strip() if x else ""
        out[m.group(1)] = dict(title=" ".join(re.findall(r"^TI  - (.*)$", blk, re.M)).strip(),
                               abstract=" ".join(re.findall(r"^AB  - (.*)$", blk, re.M)).strip(),
                               doi=one("DO"), url=one("UR"))
    return out


def main():
    rows = [r for r in csv.DictReader(open(LIST, encoding="utf-8-sig")) if r["retrieval_class"] == "retrieve"]
    ris = read_ris()
    flags = {}
    for r in rows:
        w = r["ws_id"]
        t, s = ris[w]["title"], ris[w]["title"] + " " + ris[w]["abstract"]
        zh = r["language_group"] == "Chinese"
        flags[w] = dict(
            chinese=zh,
            review=bool(REVIEW_TITLE.search(t) and not NOT_REVIEW_TITLE.search(t)),
            series=bool(SERIES_ZH.search(t) if zh else SERIES_EN.search(t)),
            d1=bool(TORSION.search(s) and not WS_WORD.search(s) and CHILD.search(s)),
        )
    pools = {k: sorted(w for w in flags if flags[w][k]) for k, _ in MIN}
    drawn, how = [], {}
    for k, need in MIN:
        have = sum(1 for w in drawn if flags[w][k])
        cands = sorted((w for w in pools[k] if w not in drawn), key=lambda w: h(SEED, k, w))
        for w in cands[:max(0, need - have)]:
            drawn.append(w)
            how[w] = "stratum " + k
    rest = sorted((w for w in flags if w not in drawn), key=lambda w: h(SEED, "fill", w))
    for w in rest[:N - len(drawn)]:
        drawn.append(w)
        how[w] = "random"
    drawn.sort(key=lambda w: h(SEED, "order", w))
    pilot = set()
    if os.path.exists(PILOT):
        m = re.search(r"^M = (\{.*\})\s*$", open(PILOT, encoding="utf-8").read(), re.M)
        if m:
            pilot = set(ast.literal_eval(m.group(1)).values())
    info = {r["ws_id"]: r for r in rows}
    os.makedirs(OUT, exist_ok=True)
    with open(OUT + "calibration_20_list.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["position", "ws_id", "year", "language", "has_abstract", "title", "doi", "url"])
        for i, k in enumerate(drawn, 1):
            w.writerow([i, k, info[k]["year"], info[k]["language_group"], info[k]["has_abstract"], ris[k]["title"], ris[k]["doi"], ris[k]["url"]])
    with open(OUT + "calibration_20_key.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["NOT FOR THE REVIEWERS - keyword proxies, not judgements"])
        w.writerow(["position", "ws_id", "drawn_as", "chinese", "review_proxy", "series_proxy", "d1_proxy", "in_pilot_set"])
        for i, k in enumerate(drawn, 1):
            w.writerow([i, k, how[k]] + [int(flags[k][c]) for c in ("chinese", "review", "series", "d1")] + [int(k in pilot)])
    n_have = {c: sum(1 for k in drawn if flags[k][c]) for c in ("chinese", "review", "series", "d1")}
    lines = [
        "Full-text calibration set: 20 reports (guide section 12, decision D5)",
        "Seed: %s | population: %d records (retrieval_class = retrieve) of %s" % (SEED, len(rows), LIST),
        "Ranking within each stratum: sha256(SEED|stratum|ws_id); final order: sha256(SEED|order|ws_id). Rerun: python3 -I tools/draw_ft_calibration.py",
        "",
        "Strata (keyword proxies made by the script; the reviewers judge every report on its full text):",
        "  chinese: language group Chinese",
        "  review:  title contains review / 综述 / 进展 / overview and none of case / report / series / 例 (a report of a case plus a literature review is NOT in this stratum)",
        "  series:  English title with series / cohort / retrospective / multicentre / experience / cases; Chinese title with N例 (N >= 10 or 三 to 十) / 回顾 / 病例分析",
        "  d1:      title or abstract has a torsion or volvulus word, a child cue, and no wandering / ectopic / floating / migrating / mobile / movable / pelvic-spleen / ptosis word (the guide's D1 situation)",
        "",
        "Pool sizes: " + ", ".join("%s %d" % (k, len(v)) for k, v in pools.items()),
        "Minimum required: d1 3, review 2, chinese 3, series 3 (drawn in this order; a record already drawn counts toward every stratum it belongs to); the remaining places are random.",
        "Drawn (%d): %d by stratum, %d random" % (len(drawn), sum(1 for k in drawn if how[k] != "random"), sum(1 for k in drawn if how[k] == "random")),
        "In the 20 (a record can belong to several strata): " + ", ".join("%s %d" % (c, n_have[c]) for c in n_have),
        "With an abstract in the database record: %d of %d; English %d, Chinese %d" % (
            sum(1 for k in drawn if info[k]["has_abstract"] == "yes"), len(drawn),
            sum(1 for k in drawn if info[k]["language_group"] == "English"), sum(1 for k in drawn if info[k]["language_group"] == "Chinese")),
        "Records of the 53-paper pilot set among the 20: %d" % sum(1 for k in drawn if k in pilot),
        "",
        "Give the reviewers only calibration_20_list.csv. The key file holds the strata flags; keep it closed until both have finished.",
        "The retrieval list's 'source' column (how a record reached the full-text stage) is deliberately left out of the list.",
    ]
    open(OUT + "calibration_20_design.txt", "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
