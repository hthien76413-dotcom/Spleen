#!/usr/bin/env python3
"""Draw the 10-report calibration set for the EXTRACTION stage (extraction guide section 10; protocol Section 14).

WHY THE DRAW CANNOT BE DONE YET. The 10 reports must be reports that are actually in the extraction set, i.e. reports that both
full-text screeners (and, where they differ, the adjudicator) have marked Include. That list does not exist until the full-text
stage is finished and tools/finalize_fulltext.py has written fulltext_included.csv. What is fixed NOW, before any full-text decision
exists, is the procedure and the seed, so the draw cannot be steered by the outcome. Run this script when the list exists.

Population: rows of fulltext_included.csv with decision = Include and no ipd_outcome (reports whose individual data are published;
reports whose individual data arrive by e-mail come later and are not used for calibration). Reports of the 53-paper pilot set are
left out by default (Jun Shu extracted them before the protocol, so he would not be calibrating on an unseen report); --keep-pilot
puts them back. Both rules (pilot papers left out; only reports with published individual data, none that depend on data sent by e-mail)
were Claude's choices and were agreed by both extractors, Jun Shu (E1) and Hongqiang Bian (E2), as reported by the author on 19 Oct 2026.

Strata (the extraction guide asks for at least: Chinese 3, series 3, durations written in different ways - hours, weeks, a range,
a vague phrase - at least 1 each, 'torsion only' 1, a child who was not operated on or whose spleen was not removed 1). They are
KEYWORD PROXIES, not judgements, and the duration and not-operated ones read the database abstract only (reports without an abstract
cannot match them). Chinese, series and 'torsion only' use the full-text log where the reviewers' entries allow it:
  chinese   language group Chinese
  series    n_children_individual >= 3 in the full-text log (R1/R2 value if the agreed one is blank); title keyword proxy as fall-back
  d1        ws_basis 'Torsion only, position not stated' (agreed value, or either reviewer's)
  hours     abstract mentions a number of hours / 小时
  weeks     abstract mentions weeks / 周
  range     abstract gives a duration range such as 2-3 days, 3 to 5 weeks, 2~3天 (not in years: '2-3 years' is mostly an age range)
  vague     abstract uses a vague phrase (several days, a few weeks, for a long time, 数日, 十余天, 多年 ...)
  nonop     abstract says conservative / non-operative / not operated / without surgery / 保守 / 未手术
Drawing order is fixed (scarcest first): nonop, d1, vague, range, hours, weeks, series, chinese. A report already drawn counts toward
every stratum it belongs to. Within a stratum the reports are ranked by sha256(SEED | stratum | ws_id). The remaining places up to N
are filled at random the same way. If a stratum has too few candidates, or the minimum cannot all fit into N places, the design file
says which minimum was not met; nothing is invented.

Usage (from the repository root; needs only the standard library):
  python3 -I tools/draw_extraction_calibration.py FULLTEXT_INCLUDED_CSV [--n 10] [--keep-pilot] [--out DIR]
Writes into DIR (default search/extraction/calibration/):
  calibration_10_list.csv    for both extractors: position, ws_id, year, language, has_abstract, title, doi, url (no strata, no decisions)
  calibration_10_key.csv     strata flags per record: NOT for the extractors, keep it closed until both have finished
  calibration_10_design.txt  seed, rules, pool sizes, what was drawn, minimums not met, rough patient count
"""
import argparse
import ast
import csv
import importlib.util
import os
import re

SEED = "20261019"   # fixed on 19 Oct 2026, before any full-text decision exists
N_DEFAULT = 10
LIST = "search/screening/rescreen/fulltext_retrieval_list.csv"
PILOT = "tools/pilot_reference_check.py"
ORDER = [("nonop", 1), ("d1", 1), ("vague", 1), ("range", 1), ("hours", 1), ("weeks", 1), ("series", 3), ("chinese", 3)]

NUM_UNIT = r"(?:hours?|hrs?|days?|weeks?|wks?|months?|years?)"
HOURS = re.compile(r"\b\d+(?:\.\d+)?\s*(?:hours?|hrs?|h)\b|\bhours?\b|小时", re.I)
WEEKS = re.compile(r"\bweeks?\b|\bwks?\b|周", re.I)
RANGE_UNIT = r"(?:hours?|hrs?|days?|weeks?|wks?|months?)"   # no years: '2-3 years' is mostly an age range
RANGE = re.compile(r"\b\d+(?:\.\d+)?\s*(?:-|–|—|to)\s*\d+(?:\.\d+)?\s*%s\b|\d+\s*[-~—至到]\s*\d+\s*(?:小时|天|日|周|个月|月)" % RANGE_UNIT, re.I)
VAGUE = re.compile(r"\b(?:several|a few|few|some|a couple of|many)\s+%s\b|\bfor (?:a )?(?:long|some|considerable) (?:time|period)\b|"
                   r"\blong[- ]standing\b|数(?:小时|日|天|周|月|年)|[十二三四五六七八九]余(?:天|日|周|个月|月|年)|多年|多日|长期" % NUM_UNIT, re.I)
NONOP = re.compile(r"\bconservative(?:ly)?\b|\bnon-?operative(?:ly)?\b|\bnot (?:been )?(?:operated|undergo|treated surgically)\b|"
                   r"\bwithout (?:surgery|operation|surgical)\b|\bdeclined (?:surgery|operation)\b|保守|未手术|未行手术|拒绝手术", re.I)
SERIES_EN = re.compile(r"\b(series|cohort|retrospective|multicent\w*|experience|cases)\b", re.I)
SERIES_ZH = re.compile(r"(\d{2,}|[三四五六七八九十]+)\s*例|回顾|病例分析")


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def num(x):
    x = (x or "").strip()
    return int(float(x)) if re.fullmatch(r"\d+(?:\.0+)?", x) else None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("included", help="fulltext_included.csv written by tools/finalize_fulltext.py")
    ap.add_argument("--n", type=int, default=N_DEFAULT)
    ap.add_argument("--keep-pilot", action="store_true", help="do not leave the 53 pilot papers out")
    ap.add_argument("--out", default="search/extraction/calibration")
    args = ap.parse_args()

    dfc = load_module(os.path.join(os.path.dirname(os.path.abspath(__file__)), "draw_ft_calibration.py"), "dfc")
    ris = dfc.read_ris()
    h = dfc.h
    retr = {r["ws_id"]: r for r in csv.DictReader(open(LIST, encoding="utf-8-sig"))}
    inc_rows = list(csv.DictReader(open(args.included, encoding="utf-8-sig")))
    if not inc_rows:
        raise SystemExit("The included list is empty; nothing to draw from.")

    pilot = set()
    if os.path.exists(PILOT):
        m = re.search(r"^M = (\{.*\})\s*$", open(PILOT, encoding="utf-8").read(), re.M)
        if m:
            pilot = set(ast.literal_eval(m.group(1)).values())

    pool, skipped = {}, {"not Include": 0, "individual data by e-mail": 0, "pilot paper": 0, "not on retrieval list": 0}
    for r in inc_rows:
        w = (r.get("ws_id") or "").strip().upper()
        if (r.get("decision") or "").strip() != "Include":
            skipped["not Include"] += 1
            continue
        if (r.get("ipd_outcome") or "").strip():
            skipped["individual data by e-mail"] += 1
            continue
        if w not in retr or w not in ris:
            skipped["not on retrieval list"] += 1
            continue
        if w in pilot and not args.keep_pilot:
            skipped["pilot paper"] += 1
            continue
        pool[w] = r

    flags, n_kids = {}, {}
    for w, r in pool.items():
        t, a = ris[w]["title"], ris[w]["abstract"]
        zh = retr[w]["language_group"] == "Chinese"
        kids = [num(r.get(c)) for c in ("n_children_individual", "R1_n_children_individual", "R2_n_children_individual")]
        kids = [k for k in kids if k is not None]
        n_kids[w] = kids[0] if kids and num(r.get("n_children_individual")) is not None else (max(kids) if kids else None)
        basis = {(r.get(c) or "").strip() for c in ("ws_basis", "R1_ws_basis", "R2_ws_basis")}
        flags[w] = dict(
            chinese=zh,
            series=(n_kids[w] >= 3) if n_kids[w] is not None else bool(SERIES_ZH.search(t) if zh else SERIES_EN.search(t)),
            d1="Torsion only, position not stated" in basis,
            hours=bool(HOURS.search(a)), weeks=bool(WEEKS.search(a)), range=bool(RANGE.search(a)), vague=bool(VAGUE.search(a)),
            nonop=bool(NONOP.search(a)),
        )
    pools = {k: sorted(w for w in flags if flags[w][k]) for k, _ in ORDER}

    drawn, how, unmet = [], {}, []
    for k, need in ORDER:
        have = sum(1 for w in drawn if flags[w][k])
        cands = sorted((w for w in pools[k] if w not in drawn), key=lambda w: h(SEED, k, w))
        for w in cands[:max(0, need - have)]:
            if len(drawn) >= args.n:
                break
            drawn.append(w)
            how[w] = "stratum " + k
        have = sum(1 for w in drawn if flags[w][k])
        if have < need:
            unmet.append("%s: %d of %d (%s)" % (k, have, need, "pool has %d" % len(pools[k]) if len(pools[k]) < need else "no places left within N"))
    rest = sorted((w for w in flags if w not in drawn), key=lambda w: h(SEED, "fill", w))
    for w in rest[:max(0, args.n - len(drawn))]:
        drawn.append(w)
        how[w] = "random"
    drawn.sort(key=lambda w: h(SEED, "order", w))

    os.makedirs(args.out, exist_ok=True)
    with open(os.path.join(args.out, "calibration_10_list.csv"), "w", encoding="utf-8-sig", newline="") as f:
        wr = csv.writer(f)
        wr.writerow(["position", "ws_id", "year", "language", "has_abstract", "title", "doi", "url"])
        for i, w in enumerate(drawn, 1):
            wr.writerow([i, w, retr[w]["year"], retr[w]["language_group"], retr[w]["has_abstract"], ris[w]["title"], ris[w]["doi"], ris[w]["url"]])
    cols = [k for k, _ in ORDER]
    with open(os.path.join(args.out, "calibration_10_key.csv"), "w", encoding="utf-8-sig", newline="") as f:
        wr = csv.writer(f)
        wr.writerow(["NOT FOR THE EXTRACTORS - keyword proxies and full-text-log values, not judgements"])
        wr.writerow(["position", "ws_id", "drawn_as"] + cols + ["n_children_individual_in_log", "in_pilot_set"])
        for i, w in enumerate(drawn, 1):
            wr.writerow([i, w, how[w]] + [int(flags[w][c]) for c in cols] + [n_kids[w] if n_kids[w] is not None else "", int(w in pilot)])

    kids_known = [n_kids[w] for w in drawn if n_kids[w] is not None]
    lines = [
        "Extraction calibration set: %d reports (extraction guide section 10; protocol Section 14)" % len(drawn),
        "Seed: %s (fixed on 19 Oct 2026, before any full-text decision). Ranking: sha256(SEED|stratum|ws_id); final order: sha256(SEED|order|ws_id)." % SEED,
        "Rerun: python3 -I tools/draw_extraction_calibration.py %s%s" % (args.included, " --keep-pilot" if args.keep_pilot else ""),
        "",
        "Input: %d rows in the included list. Left out: %s." % (len(inc_rows), "; ".join("%s %d" % (k, v) for k, v in skipped.items())),
        "Population after that: %d reports (Include, individual data in the published report%s)." % (len(pool), "" if args.keep_pilot else ", pilot papers left out"),
        "Pool sizes by stratum (keyword proxies / full-text-log values): " + ", ".join("%s %d" % (k, len(v)) for k, v in pools.items()),
        "Fixed drawing order and minimum: " + ", ".join("%s %d" % kn for kn in ORDER) + ". A report already drawn counts toward every stratum it belongs to; the rest is random up to N = %d." % args.n,
        "Drawn: %d by stratum, %d random." % (sum(1 for w in drawn if how[w] != "random"), sum(1 for w in drawn if how[w] == "random")),
        "In the set (a report can belong to several strata): " + ", ".join("%s %d" % (c, sum(1 for w in drawn if flags[w][c])) for c in cols),
        "Minimums not met: " + ("; ".join(unmet) if unmet else "none"),
        "Reports with an abstract in the database record: %d of %d; English %d, Chinese %d." % (
            sum(1 for w in drawn if retr[w]["has_abstract"] == "yes"), len(drawn),
            sum(1 for w in drawn if retr[w]["language_group"] == "English"), sum(1 for w in drawn if retr[w]["language_group"] == "Chinese")),
        "Children with individual data in the set (from the full-text log, %d of %d reports have a number): %s" % (
            len(kids_known), len(drawn), "about %d" % sum(kids_known) if kids_known else "unknown"),
        "",
        "Give the extractors only calibration_10_list.csv. The key holds the strata flags and stays closed until both have finished.",
        "The strata for duration wording and 'not operated' read only the database abstract and are rough; the extractors judge from the full text.",
        "The five own children (report OWN) are extracted separately and are not part of this set.",
    ]
    open(os.path.join(args.out, "calibration_10_design.txt"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
