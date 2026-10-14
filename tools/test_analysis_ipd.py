#!/usr/bin/env python3
"""Tests for tools/analysis_ipd.R on INVENTED data (nothing here is real patient data).

Run from the repository root:   python3 tools/test_analysis_ipd.py
Needs: Rscript with readxl, sandwich, lmtest, lme4, Hmisc, digest; and for the cross-checks the Python packages
openpyxl, statsmodels and scipy (the tests are skipped when something is missing).

What is checked (the R script is compared with independent Python code, not with itself)
  1. The population flow (duplicates, not operated, outcome unknown, missing duration/age) equals a Python recount.
  2. The derived variables the R script computes (duration category, primary outcome) equal the Python rules of
     tools/compare_extractions.py, which are in turn tested against the workbook formulas.
  3. The primary model: log odds ratio per doubling and its cluster-robust standard error equal statsmodels'
     logistic regression with cluster-robust covariance (same small-sample correction), to 1e-6.
  4. Category counts, Clopper-Pearson intervals (scipy beta quantiles) and the Cochran-Armitage trend statistic
     (hand formula).
  5. Sensitivity analyses 1, 5, 6 and 7: patient and event counts, and the odds ratio of SA1.
  6. A duration of 0 days stops the script unless --zero-as is given; the run log carries SHA-256 hashes.
The synthetic data are generated with a fixed seed; the true effect is an odds ratio of 1.3 per doubling, which the
estimate should be near, but that is a sanity check only, not a test.
"""
import csv
import hashlib
import math
import os
import random
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import compare_extractions as ce  # noqa: E402
from openpyxl import load_workbook  # noqa: E402

try:
    import numpy as np
    import statsmodels.api as sm
    from scipy.stats import beta as beta_dist
    HAVE_PY = True
except Exception:  # pragma: no cover
    HAVE_PY = False

HAVE_R = shutil.which("Rscript") is not None
R_SCRIPT = os.path.join(HERE, "analysis_ipd.R")
BUILD_EXTRACTION = os.path.join(HERE, "build_extraction_workbook.py")
BUILD_ROB = os.path.join(HERE, "build_rob_workbook.py")
TRUE_LOG_OR_PER_DOUBLING = math.log(1.3)


# ------------------------------------------------------------------------------------------------ synthetic data
def make_synthetic(seed=20261014):
    rnd = random.Random(seed)
    reports, patients = [], []

    def new_patient(pid, rid):
        age = round(rnd.uniform(0.1, 17.5), 2)
        dur = max(0.5, round(math.exp(rnd.gauss(math.log(5), 1.3)), 1))
        logit = -1.2 + TRUE_LOG_OR_PER_DOUBLING * math.log2(dur) + 0.02 * age
        nonviable = rnd.random() < 1 / (1 + math.exp(-logit))
        p = dict(patient_id=pid, report_id=rid, age_years=age, sex=rnd.choice(["M", "F"]))
        # duration: mostly numbers, some NR, some imprecise-only
        u = rnd.random()
        if u < 0.10:
            p["idx_dur_days"] = "NR"
        elif u < 0.14:
            p["idx_dur_days"] = "NR"
            p["idx_dur_cat_imprecise"] = rnd.choice(["3-7 d", ">30 d"])
        else:
            p["idx_dur_days"] = dur
            if rnd.random() < 0.15:
                p["idx_dur_intermittent"] = "Yes"
                p["idx_dur_alt_days"] = max(0.5, round(dur / 2, 1))
        p["total_hist_days"] = round(dur + rnd.expovariate(1 / 20), 1) if rnd.random() < 0.7 else "NR"
        if rnd.random() < 0.03:
            p["age_years"] = "NR"
        if rnd.random() < 0.05:   # managed without operation
            p.update(viability="Not applicable", procedure="No operation", approach="Not applicable")
        elif rnd.random() < 0.03:  # viability not reported, spleen removed
            p.update(viability="NR", procedure="Total splenectomy", approach="Open")
        elif nonviable:
            if rnd.random() < 0.2:
                p.update(viability="Partially non-viable", procedure="Partial splenectomy +/- splenopexy")
            else:
                p.update(viability="Non-viable", procedure="Total splenectomy")
            p["approach"] = rnd.choice(["Open", "Laparoscopic"])
        else:
            u2 = rnd.random()
            if u2 < 0.05:
                p.update(viability="Partially non-viable", procedure="Splenopexy")       # -> Review, outside the analysis
            elif u2 < 0.15:
                p.update(viability="Viable", procedure="Total splenectomy", reason_viable_removed="Surgeon's preference")
            elif u2 < 0.30:
                p.update(viability="Viable", procedure="Detorsion only")
            else:
                p.update(viability="Viable", procedure="Splenopexy",
                         fixation=rnd.choice(["Mesh", "Direct suture", "Omental wrap", "Retroperitoneal or extraperitoneal pouch"]))
            p["approach"] = rnd.choice(["Open", "Laparoscopic"])
        if p.get("procedure") in ("Splenopexy", "Partial splenectomy +/- splenopexy"):
            p.setdefault("fixation", rnd.choice(["Mesh", "Direct suture"]))
            p["recurrence"] = "Yes" if rnd.random() < 0.12 else rnd.choice(["No", "No", "NR"])
            p["further_surgery"] = "Yes" if p["recurrence"] == "Yes" else rnd.choice(["No", "NR"])
        p["torsion_at_op"] = "Yes" if rnd.random() < 0.7 else rnd.choice(["No", "NR"])
        p["cond_gv"] = "Yes" if rnd.random() < 0.12 else "No"
        p["cond_goo"] = "Yes" if rnd.random() < 0.05 else "No"
        p["cond_dh"] = "Yes" if rnd.random() < 0.05 else "No"
        p["aetiology"] = "Acquired" if rnd.random() < 0.1 else "Congenital"
        p["missed_dx"] = rnd.choice(["Yes", "No", "No", "NR"])
        p["known_dx_deferred"] = "Yes" if rnd.random() < 0.15 else "No"
        p["torsion_awaiting"] = ("Yes" if rnd.random() < 0.3 else "No") if p["known_dx_deferred"] == "Yes" else "Not applicable"
        p["platelets"] = rnd.choice([250, 320, 480, 560, "NR"])
        p["presentation"] = rnd.choice(["Acute", "Chronic or intermittent", "Acute on chronic"])
        return p

    for i in range(1, 71):
        rid = f"WS{i:04d}"
        kind = rnd.random()
        if kind < 0.65:
            design, cons, k = "Case report", "Unclear", 1
        elif kind < 0.9:
            design, cons, k = "Case series", rnd.choice(["Yes", "No"]), rnd.randint(2, 8)
        else:
            design, cons, k = "Cohort", "Yes", rnd.randint(5, 12)
        reports.append(dict(report_id=rid, first_author=f"Author{i}", year=rnd.randint(1985, 2025), journal="J",
                            country="X", language="Chinese" if rnd.random() < 0.25 else "English", design=design,
                            consecutive=cons, n_children_individual=k, n_children_aggregate=0))
        for j in range(1, k + 1):
            patients.append(new_patient(f"{rid}_P{j}", rid))
    reports.append(dict(report_id="OWN", first_author="Own", year=2026, journal="-", country="China", language="English",
                        design="Case series", consecutive="Yes", n_children_individual=5, n_children_aggregate=0))
    for j in range(1, 6):
        patients.append(new_patient(f"OWN_P{j}", "OWN"))
    # three duplicates of patients in other reports (the duplicate row is the one carrying same_patient_as)
    for n, src in enumerate(rnd.sample([p for p in patients if p["report_id"] != "OWN"], 3), start=1):
        d = dict(src)
        d.update(patient_id=f"WS9{n:03d}_P1", report_id=reports[n]["report_id"], same_patient_as=src["patient_id"])
        patients.append(d)
    return reports, patients


def fill_workbook(template, path, reports, patients):
    wb = load_workbook(template)
    for sheet, rows in (("Reports", reports), ("Patients", patients)):
        ws = wb[sheet]
        idx = {str(ws.cell(row=1, column=c).value): c for c in range(1, ws.max_column + 1) if ws.cell(row=1, column=c).value}
        for i, row in enumerate(rows):
            for code, v in row.items():
                ws.cell(row=ce.FIRST_DATA_ROW + i, column=idx[code]).value = v
    wb.save(path)


def build(builder, out):
    subprocess.run([sys.executable, "-I", builder, out], check=True, capture_output=True)


def run_r(extraction, outdir, *extra):
    return subprocess.run(["Rscript", R_SCRIPT, "--extraction", extraction, "--out", outdir, *extra],
                          capture_output=True, text=True)


def read_csv(path):
    with open(path, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def fnum(x):
    return float(x) if x not in ("", None) else float("nan")


# ------------------------------------------------------------------------------------------------ Python reference
def period(year):
    return "before 2000" if year < 2000 else ("2000-2014" if year <= 2014 else "2015 onward")


def reference_population(reports, patients):
    year = {r["report_id"]: r["year"] for r in reports}
    lang = {r["report_id"]: r["language"] for r in reports}
    flow = {}
    dup = [p for p in patients if p.get("same_patient_as")]
    uniq = [p for p in patients if not p.get("same_patient_as")]
    flow["patients"], flow["dup"], flow["unique"] = len(patients), len(dup), len(uniq)
    notop = [p for p in uniq if p.get("procedure") == "No operation" or p.get("viability") == "Not applicable"]
    op = [p for p in uniq if p not in notop]
    flow["notop"], flow["op"] = len(notop), len(op)
    for p in op:
        p["_outcome"] = ce.derive_outcome(p.get("viability"), p.get("procedure"))
    oc = [p for p in op if p["_outcome"] in ("Non-viable", "Viable")]
    flow["oc"] = len(oc)
    for p in oc:
        d = p.get("idx_dur_days")
        p["_log2"] = math.log2(d) if isinstance(d, (int, float)) else None
        p["_y"] = 1 if p["_outcome"] == "Non-viable" else 0
        p["_year"], p["_lang"] = year[p["report_id"]], lang[p["report_id"]]
    flow["no_dur"] = sum(p["_log2"] is None for p in oc)
    flow["no_age"] = sum(p["_log2"] is not None and not isinstance(p["age_years"], (int, float)) for p in oc)
    cc = [p for p in oc if p["_log2"] is not None and isinstance(p["age_years"], (int, float))]
    flow["cc"], flow["events"], flow["clusters"] = len(cc), sum(p["_y"] for p in cc), len({p["report_id"] for p in cc})
    return flow, oc, cc


def sm_fit(rows):
    """statsmodels logistic regression with cluster-robust covariance by report; returns (logOR, SE) for log2dur."""
    X = np.array([[1.0, p["_log2"], p["age_years"], 1.0 if period(p["_year"]) == "2000-2014" else 0.0,
                   1.0 if period(p["_year"]) == "2015 onward" else 0.0] for p in rows])
    y = np.array([p["_y"] for p in rows], dtype=float)
    groups = np.array([p["report_id"] for p in rows])
    res = sm.Logit(y, X).fit(disp=0, cov_type="cluster", cov_kwds={"groups": groups, "use_correction": True})
    return res.params[1], res.bse[1]


def cp_ci(x, n):
    lo = 0.0 if x == 0 else beta_dist.ppf(0.025, x, n - x + 1)
    hi = 1.0 if x == n else beta_dist.ppf(0.975, x + 1, n - x)
    return lo, hi


# ------------------------------------------------------------------------------------------------ tests
@unittest.skipUnless(HAVE_R and HAVE_PY, "Rscript or the Python packages (statsmodels, scipy) are missing")
class AnalysisScriptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp()
        tpl = os.path.join(cls.tmp, "tpl.xlsx")
        build(BUILD_EXTRACTION, tpl)
        cls.reports, cls.patients = make_synthetic()
        cls.xlsx = os.path.join(cls.tmp, "syn.xlsx")
        fill_workbook(tpl, cls.xlsx, cls.reports, cls.patients)
        # a consensus RoB workbook: every second report adequate, the others not
        rob_tpl = os.path.join(cls.tmp, "rob_tpl.xlsx")
        build(BUILD_ROB, rob_tpl)
        wb = load_workbook(rob_tpl)
        ws = wb["RoB"]
        idx = {str(ws.cell(row=1, column=c).value): c for c in range(1, ws.max_column + 1) if ws.cell(row=1, column=c).value}
        cls.rob_ok = set()
        for i, r in enumerate(cls.reports):
            good = i % 2 == 0
            if good:
                cls.rob_ok.add(r["report_id"])
            for code, v in (("report_id", r["report_id"]), ("reviewer", "Consensus"), ("q_exposure", "Yes"),
                            ("q_outcome", "Yes" if good else "Unclear"), ("q_reporting", "Yes")):
                ws.cell(row=ce.FIRST_DATA_ROW + i, column=idx[code]).value = v
        cls.rob = os.path.join(cls.tmp, "rob.xlsx")
        wb.save(cls.rob)
        cls.out = os.path.join(cls.tmp, "out")
        cls.proc = run_r(cls.xlsx, cls.out, "--rob", cls.rob)
        cls.flow, cls.oc, cls.cc = reference_population(cls.reports, cls.patients)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def table(self, name):
        return read_csv(os.path.join(self.out, name))

    def test_script_runs(self):
        self.assertEqual(self.proc.returncode, 0, self.proc.stderr[-2000:])
        for name in ("01_population_flow.csv", "03_primary_model.csv", "04_categories_and_trend.csv",
                     "13_sensitivity_analyses.csv", "run_log.txt"):
            self.assertTrue(os.path.exists(os.path.join(self.out, name)), name)

    def test_population_flow(self):
        rows = {r["step"].strip(): int(r["n"]) for r in self.table("01_population_flow.csv")}
        f = self.flow
        self.assertEqual(rows["Patients with a patient_id"], f["patients"])
        self.assertEqual(rows["minus duplicates of a patient in another report (same_patient_as filled)"], f["dup"])
        self.assertEqual(rows["Unique children"], f["unique"])
        self.assertEqual(rows["of whom managed without operation (descriptive only)"], f["notop"])
        self.assertEqual(rows["Operated children"], f["op"])
        self.assertEqual(rows["Outcome population (primary outcome known)"], f["oc"])
        self.assertEqual(rows["minus index-episode duration missing (no number)"], f["no_dur"])
        self.assertEqual(rows["minus age missing (NR or blank)"], f["no_age"])
        self.assertEqual(rows["Primary analysis population (complete cases: duration, age, period)"], f["cc"])
        self.assertEqual(rows["of which non-viable spleen (events)"], f["events"])
        self.assertEqual(rows["reports (clusters)"], f["clusters"])

    def test_derived_variables_equal_python_rules(self):
        by_id = {p["patient_id"]: p for p in self.patients}
        n = 0
        for r in self.table("00_analysis_dataset.csv"):
            p = by_id[r["patient_id"]]
            exp_cat = ce.derive_category(p.get("idx_dur_days"), p.get("idx_dur_cat_imprecise"))
            self.assertEqual(r["idx_dur_category"] or None, exp_cat, r["patient_id"])
            exp_out = ce.derive_outcome(p.get("viability"), p.get("procedure"))
            self.assertEqual(r["primary_outcome"] or None, exp_out, r["patient_id"])
            n += 1
        self.assertEqual(n, self.flow["unique"] - 0)

    def test_primary_model_equals_statsmodels(self):
        row = self.table("03_primary_model.csv")[0]
        b, se = sm_fit(self.cc)
        self.assertAlmostEqual(float(row["logOR"]), b, places=6)
        self.assertAlmostEqual(float(row["se"]), se, places=6)
        self.assertAlmostEqual(float(row["OR"]), math.exp(b), places=6)
        self.assertEqual(int(row["n"]), len(self.cc))
        # sanity only: the data were generated with OR 1.3 per doubling
        self.assertTrue(1.0 < float(row["OR"]) < 1.9, row["OR"])

    def test_spline_decision_follows_the_rule(self):
        ev, n = self.flow["events"], self.flow["cc"]
        minority = min(ev, n - ev)
        expected_done = ev / 5 >= 10 and minority / 5 >= 10
        rows = self.table("03_primary_model.csv")
        has_spline_row = any("NON-LINEARITY" in r["analysis"] for r in rows)
        self.assertEqual(has_spline_row, expected_done)

    def test_categories_clopper_pearson_and_trend(self):
        cats = ["<=2 d", "3-7 d", "8-30 d", ">30 d"]
        tab = {r["group"]: r for r in self.table("04_categories_and_trend.csv")}
        counts = {c: [0, 0] for c in cats}
        for p in self.oc:
            c = ce.derive_category(p.get("idx_dur_days"), p.get("idx_dur_cat_imprecise"))
            if c in counts:
                counts[c][0] += 1
                counts[c][1] += p["_y"]
        for c in cats:
            n, x = counts[c]
            self.assertEqual(int(tab[c]["n"]), n, c)
            self.assertEqual(int(tab[c]["events"]), x, c)
            if n:
                lo, hi = cp_ci(x, n)
                self.assertAlmostEqual(float(tab[c]["ci_low"]), lo, places=6)
                self.assertAlmostEqual(float(tab[c]["ci_high"]), hi, places=6)
        # Cochran-Armitage chi-square, scores 1..4 (hand formula)
        N = sum(counts[c][0] for c in cats)
        R = sum(counts[c][1] for c in cats)
        pbar = R / N
        scores = {c: i + 1 for i, c in enumerate(cats)}
        t_num = sum(scores[c] * (counts[c][1] - counts[c][0] * pbar) for c in cats) ** 2
        sx = sum(counts[c][0] * scores[c] for c in cats)
        sxx = sum(counts[c][0] * scores[c] ** 2 for c in cats)
        t_den = pbar * (1 - pbar) * (sxx - sx ** 2 / N)
        self.assertAlmostEqual(float(tab[cats[0]]["trend_chisq"]), t_num / t_den, places=6)

    def test_sensitivity_counts_and_sa1(self):
        sens = {r["analysis"][:3]: r for r in self.table("13_sensitivity_analyses.csv")}
        own = [p for p in self.cc if p["report_id"] != "OWN"]
        self.assertEqual(int(sens["SA1"]["n"]), len(own))
        self.assertEqual(int(sens["SA1"]["events"]), sum(p["_y"] for p in own))
        b, se = sm_fit(own)
        self.assertAlmostEqual(float(sens["SA1"]["logOR"]), b, places=6)
        self.assertAlmostEqual(float(sens["SA1"]["se"]), se, places=6)
        non_cn = [p for p in self.cc if p["_lang"] != "Chinese"]
        self.assertEqual(int(sens["SA6"]["n"]), len(non_cn))
        post = [p for p in self.cc if p["_year"] >= 2000]
        self.assertEqual(int(sens["SA7"]["n"]), len(post))
        adequate = [p for p in self.cc if p["report_id"] in self.rob_ok]
        self.assertEqual(int(sens["SA5"]["n"]), len(adequate))
        self.assertEqual(int(sens["SA5"]["events"]), sum(p["_y"] for p in adequate))
        self.assertTrue(sens["SA8"]["OR"] not in ("", None))

    def test_run_log_has_hashes(self):
        with open(os.path.join(self.out, "run_log.txt"), encoding="utf-8") as fh:
            log = fh.read()
        with open(R_SCRIPT, "rb") as fh:
            self.assertIn(hashlib.sha256(fh.read()).hexdigest(), log)
        with open(self.xlsx, "rb") as fh:
            self.assertIn(hashlib.sha256(fh.read()).hexdigest(), log)

    def test_zero_duration_needs_a_decision(self):
        wb = load_workbook(self.xlsx)
        ws = wb["Patients"]
        idx = {str(ws.cell(row=1, column=c).value): c for c in range(1, ws.max_column + 1) if ws.cell(row=1, column=c).value}
        for r in range(ce.FIRST_DATA_ROW, ws.max_row + 1):
            if isinstance(ws.cell(row=r, column=idx["idx_dur_days"]).value, (int, float)):
                ws.cell(row=r, column=idx["idx_dur_days"]).value = 0
                break
        zero = os.path.join(self.tmp, "zero.xlsx")
        wb.save(zero)
        bad = run_r(zero, os.path.join(self.tmp, "out_zero"))
        self.assertNotEqual(bad.returncode, 0)
        self.assertIn("--zero-as", bad.stderr)
        good = run_r(zero, os.path.join(self.tmp, "out_zero2"), "--zero-as", "0.5")
        self.assertEqual(good.returncode, 0, good.stderr[-1500:])


if __name__ == "__main__":
    unittest.main(verbosity=2)
