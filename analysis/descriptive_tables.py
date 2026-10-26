#!/usr/bin/env python3
"""Descriptive tables for the IPD review (protocol v1.8, Sections 14-16). No inference, no model.

Usage:  python descriptive_tables.py CONSENSUS.xlsx --out DIR
Writes (CSV, numbers unrounded as counts; percentages to 1 decimal):
  table2_reports.csv            reports by language, period, design, source of individual data
  table3_children.csv           characteristics of the children (own series included)
  with_without_duration.csv     children with vs without a reported index-episode duration (protocol Section 16)
  failure_by_operation.csv      outcome and later loss of spleen by index operation
  descriptive_notes.txt         counts, exclusions and columns that were absent
Rules: patients with same_patient_as filled are dropped (as in the main analysis); a column that is
absent from the workbook gives rows marked 'column not in workbook'; blank and NR are counted as
'not reported', never as No. Own series (OWN) is counted among the children, not among the reports.
"""
import argparse, os, sys, csv
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import compare_extraction as ce


def pct(n, d):
    return "%d (%.1f%%)" % (n, 100.0 * n / d) if d else "%d" % n


def med(s):
    s = s.dropna()
    if s.empty:
        return "not reported"
    return "%.2f (%.2f to %.2f)" % (s.median(), s.min(), s.max())


def load(path):
    _, reports, patients = ce.load(path)
    rep = pd.DataFrame(reports)
    pat = pd.DataFrame(patients)
    for c in ["patient_id", "report_id", "same_patient_as"]:
        if c in pat:
            pat[c] = pat[c].map(ce.txt)
    dup = pat[pat.get("same_patient_as", "") != ""] if "same_patient_as" in pat else pat.iloc[0:0]
    pat = pat[pat.patient_id != ""]
    if "same_patient_as" in pat:
        pat = pat[pat.same_patient_as == ""]
    pat = pat.copy()
    pat["outcome_raw"] = [ce.outcome(r) for r in pat.to_dict("records")]
    pat["y"] = pat.outcome_raw.map({"Non-viable": 1.0, "Viable": 0.0})
    for c in ["age_years", "idx_dur_days", "platelets", "followup_months"]:
        if c in pat:
            pat[c] = pd.to_numeric(pat[c].map(lambda v: ce.txt(v).replace(",", ".")), errors="coerce")
    return rep, pat, len(dup)


def val(pat, col):
    return pat[col].map(ce.txt) if col in pat else None


def count_rows(pat, label, col, value, rows, notes, n):
    v = val(pat, col)
    if v is None:
        rows.append((label, "column not in workbook")); notes.append("absent column: " + col)
        return
    rows.append((label, pct(int((v == value).sum()), n)))


def table2(rep, pat, notes):
    r = rep[rep.report_id.map(ce.txt).ne("OWN") & rep.report_id.map(ce.txt).ne("")].copy()
    ids = set(pat.report_id)
    r = r[r.report_id.map(ce.txt).isin(ids)] if len(ids) else r
    n = len(r)
    rows = [("Reports with extracted children", str(n))]
    r["year"] = pd.to_numeric(r.get("year"), errors="coerce")
    lang = r.language.map(ce.txt)
    for k in ["English", "Chinese"]:
        rows.append(("Language: " + k, pct(int((lang == k).sum()), n)))
    rows.append(("Year of publication: 2000 to 2014", pct(int(((r.year >= 2000) & (r.year <= 2014)).sum()), n)))
    rows.append(("Year of publication: 2015 onward", pct(int((r.year >= 2015).sum()), n)))
    rows.append(("Year of publication: not reported", pct(int(r.year.isna().sum()), n)))
    design = r.design.map(ce.txt)
    for k in ["Case report", "Case series", "Cohort", "Letter", "Review with new patients"]:
        rows.append(("Design: " + k, pct(int((design == k).sum()), n)))
    rows.append(("Design: other or not reported", pct(int((~design.isin(["Case report", "Case series", "Cohort", "Letter", "Review with new patients"])).sum()), n)))
    rows.append(("Individual data supplied by the authors", "not in the consensus workbook (see IPD_requests)"))
    notes.append("Table 2: 'Individual data: supplied by the authors' cannot be taken from Reports/Patients; fill from IPD_requests.")
    return rows


def table3(pat, notes):
    n = len(pat)
    rows = [("Children (duplicates by same_patient_as removed)", str(n)),
            ("Age at operation, years, median (min to max)", med(pat["age_years"]) if "age_years" in pat else "column not in workbook")]
    if "sex" in pat:
        s = val(pat, "sex")
        rows += [("Girls", pct(int((s == "F").sum()), n)), ("Boys", pct(int((s == "M").sum()), n)), ("Sex not reported", pct(int((~s.isin(["F", "M"])).sum()), n))]
    else:
        rows.append(("Sex", "column not in workbook")); notes.append("absent column: sex")
    for v, lab in [("Acute", "acute"), ("Chronic or intermittent", "chronic or intermittent"), ("Acute on chronic", "acute on chronic"), ("Asymptomatic", "asymptomatic"), ("Mass only", "abdominal mass only")]:
        count_rows(pat, "Presentation: " + lab, "presentation", v, rows, notes, n)
    for col, lab in [("cond_gv", "Gastric volvulus"), ("cond_goo", "Gastric outlet obstruction"), ("cond_panc_tail", "Pancreatic tail involved"), ("cond_dh", "Diaphragmatic anomaly")]:
        count_rows(pat, lab + " (Yes)", col, "Yes", rows, notes, n)
    if "aetiology" in pat:
        a = val(pat, "aetiology")
        rows.append(("Aetiology: acquired", pct(int(a.str.startswith("Acquired").sum()), n)))
        rows.append(("Aetiology: congenital", pct(int(a.str.startswith("Congenital").sum()), n)))
        rows.append(("Aetiology: not reported or unclear", pct(int((~a.str.startswith(("Acquired", "Congenital"))).sum()), n)))
        notes.append("Table 3 aetiology rows match the first word of the list value ('Acquired...', 'Congenital...'); check Lists sheet if values differ.")
    for v, lab in [("Yes", "Yes"), ("No", "No")]:
        count_rows(pat, "Pedicle torsion at operation: " + lab, "torsion_at_op", v, rows, notes, n)
    for v in ["Viable", "Partially non-viable", "Non-viable", "NR"]:
        count_rows(pat, "Spleen at operation: " + v, "viability", v, rows, notes, n)
    for v in ["Total splenectomy", "Partial splenectomy +/- splenopexy", "Splenopexy", "Detorsion only", "Autotransplantation", "No operation", "NR"]:
        count_rows(pat, "Operation: " + v, "procedure", v, rows, notes, n)
    if "followup_months" in pat:
        rows.append(("Follow-up, months, median (min to max)", med(pat["followup_months"])))
    else:
        rows.append(("Follow-up, months", "column not in workbook"))
    return rows


def with_without(pat, notes):
    has = pat.idx_dur_days.notna()
    a, b = pat[has], pat[~has]
    rows = []
    def add(lab, f):
        rows.append((lab, f(a), f(b)))
    add("Children", lambda d: str(len(d)))
    add("Age, years, median (min to max)", lambda d: med(d["age_years"]) if "age_years" in d else "column not in workbook")
    if "sex" in pat:
        add("Girls", lambda d: pct(int((d["sex"].map(ce.txt) == "F").sum()), len(d)))
    add("Year of publication 2015 onward or own series", lambda d: pct(int(((d.get("year_rep", pd.Series(dtype=float)) >= 2015) | (d.report_id == "OWN")).sum()), len(d)) if "year_rep" in d else "n/a")
    for v in ["Viable", "Partially non-viable", "Non-viable", "NR"]:
        add("Spleen at operation: " + v, lambda d, v=v: pct(int((d["viability"].map(ce.txt) == v).sum()), len(d)) if "viability" in d else "column not in workbook")
    add("Primary outcome known (viable or non-viable)", lambda d: pct(int(d.y.notna().sum()), len(d)))
    add("Non-viable among those with a known outcome", lambda d: pct(int((d.y == 1).sum()), int(d.y.notna().sum())))
    add("Total or partial splenectomy", lambda d: pct(int(d["procedure"].map(ce.txt).isin(["Total splenectomy", "Partial splenectomy +/- splenopexy"]).sum()), len(d)) if "procedure" in d else "column not in workbook")
    add("Gastric volvulus or outlet obstruction (Yes)", lambda d: pct(int(((d["cond_gv"].map(ce.txt) == "Yes") | (d["cond_goo"].map(ce.txt) == "Yes")).sum()), len(d)) if "cond_gv" in d and "cond_goo" in d else "column not in workbook")
    notes.append("With/without duration: %d children with idx_dur_days, %d without. Comparison is descriptive; no test was specified in the protocol." % (len(a), len(b)))
    return rows


def failure_by_op(pat, notes):
    if "procedure" not in pat:
        notes.append("absent column: procedure"); return [("procedure column not in workbook",)]
    d = pat.copy()
    d["proc"] = d["procedure"].map(ce.txt).replace("", "NR")
    rows = []
    def later(col):
        return d[col].map(ce.txt) if col in d else pd.Series([""] * len(d), index=d.index)
    d["rec"] = later("recurrence"); d["fs"] = later("further_surgery")
    for k, g in d.groupby("proc"):
        ok = g.y.notna()
        rows.append((k, len(g), int((g.outcome_raw == "Non-viable").sum()), int((g.outcome_raw == "Viable").sum()),
                     int(g.outcome_raw.str.startswith("NR").sum()), int((g.rec == "Yes").sum()), int((g.fs == "Yes").sum())))
    if "recurrence" not in d or "further_surgery" not in d:
        notes.append("recurrence/further_surgery columns absent: later-failure counts are 0 by default and must not be read as 'none'.")
    return rows


def write(path, header, rows):
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f); w.writerow(header); w.writerows(rows)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("workbook"); ap.add_argument("--out", default="descriptive_output")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    rep, pat, ndup = load(a.workbook)
    ymap = {ce.txt(r["report_id"]): r.get("year") for r in rep.to_dict("records")}
    pat["year_rep"] = pat.report_id.map(lambda r: pd.to_numeric(ymap.get(r), errors="coerce"))
    notes = ["Children after removing same_patient_as duplicates: %d (removed: %d)" % (len(pat), ndup)]
    write(os.path.join(a.out, "table2_reports.csv"), ["Characteristic", "Reports, n (%)"], table2(rep, pat, notes))
    write(os.path.join(a.out, "table3_children.csv"), ["Characteristic", "Children, n (%) or median (min to max)"], table3(pat, notes))
    write(os.path.join(a.out, "with_without_duration.csv"), ["Characteristic", "Duration reported", "Duration not reported"], with_without(pat, notes))
    write(os.path.join(a.out, "failure_by_operation.csv"), ["Index operation", "Children", "Non-viable", "Viable", "Outcome NR (incl. removed, reason unknown)", "Recurrence Yes", "Further surgery Yes"], failure_by_op(pat, notes))
    with open(os.path.join(a.out, "descriptive_notes.txt"), "w", encoding="utf-8") as f:
        notes = list(dict.fromkeys(notes)); f.write("\n".join(notes) + "\n")
    print("\n".join(notes))


if __name__ == "__main__":
    main()
