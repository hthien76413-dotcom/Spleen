#!/usr/bin/env python3
"""Python reference implementation of the registered analysis plan (protocol v1.8, Sections 16-18).

PURPOSE. The protocol names R. R is not installed in the cloud container, so this script exists to (1) test the analysis logic on
simulated data with a known answer and (2) give Ji Wang a second, independent implementation to compare with analysis_main.R.
Run it on the consensus extraction workbook only when the analysis is meant to be run: it prints results.

    python3 -I analysis/analysis_crosscheck.py CONSENSUS.xlsx --out DIR [--rob rob.csv] [--seed 1]
(needs openpyxl, numpy, scipy, pandas, statsmodels; `-I` hides user-site packages, so drop it if they are installed there.)

Data rules (all derived from the raw columns, as in tools/compare_extraction.py)
  * One consensus workbook: Reports and Patients sheets. extractor must be Consensus (not enforced).
  * Patients with same_patient_as filled are duplicates of a patient in a more complete report and are dropped.
  * Outcome (Rules D3): Non-viable = 1, Viable = 0; Partially non-viable counts as non-viable if a total/partial splenectomy was done;
    Review, NR, Not applicable = missing. 'NR - removed, check reason' = splenectomy with viability not reported (bounding analyses).
  * Exposure: log2(idx_dur_days). Complete cases: duration, outcome, age_years and period must be present.
  * Period of publication: 2000-2014 vs 2015 onward from Reports.year; the own series (report_id OWN) is 2015 onward. Reports
    before 2000 should not exist; they are counted and reported, not silently dropped.
  * Cluster = report_id (the own series is one cluster).
Original proposed choices; decisions and changes are documented in the accompanying review record
  * Trend test over the four duration categories: Cochran-Armitage with scores 1-4.
  * Bounding of missing durations: missing days are set to the smallest (then the largest) observed duration.
  * Spline: restricted cubic spline, 3 knots at the 10th, 50th and 90th percentiles of log2 days (Harrell), nonlinearity tested by a Wald
    test of the nonlinear term; fitted only if events / model degrees of freedom >= 10 (degrees of freedom counted with the spline).
  * Duplicate-report analysis (d): of two reports linked by Reports.linked_duplicates, the report carrying linked_duplicates is omitted, regardless of year (protocol v1.8).
  * Mixed-effects model (sensitivity analysis 8) is not implemented here; use analysis_main.R (lme4::glmer).
Output: results.txt and results.csv in --out.
"""
import argparse, collections, csv, math, os, sys
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np, pandas as pd
import statsmodels.api as sm
from scipy import stats

SP_FLAG = "Torsion only, position not stated"
EVENTS_PER_DF = 10


def num(v):
    s = "" if v is None else str(v).strip()
    try:
        return float(s.replace(",", "."))
    except ValueError:
        return np.nan


def build(path):
    import compare_extraction as ce
    _, reports, patients = ce.load(path)
    rep = {ce.txt(r["report_id"]): r for r in reports}
    rows = []
    for p in patients:
        pid = ce.txt(p["patient_id"])
        if not pid:
            continue
        rid = ce.txt(p["report_id"])
        r = rep.get(rid, {})
        year = num(r.get("year")) if rid != "OWN" else 2026.0
        o = ce.outcome(p)
        dur_alt = num(p["idx_dur_alt_days"])
        rows.append(dict(
            patient_id=pid, report_id=rid, duplicate=bool(ce.txt(p["same_patient_as"])),
            own=(rid == "OWN"), year=year, language=ce.txt(r.get("language")), design=ce.txt(r.get("design")),
            consecutive=ce.txt(r.get("consecutive")), linked=ce.txt(r.get("linked_duplicates")),
            outcome_raw=o, age=num(p["age_years"]), days=num(p["idx_dur_days"]), days_alt=dur_alt,
            lower_bound=ce.txt(p["idx_dur_lower_bound"]) == "Yes", total_hist=num(p["total_hist_days"]),
            missed_dx=ce.txt(p["missed_dx"]), deferred=ce.txt(p["known_dx_deferred"]), platelets=num(p["platelets"]),
            torsion_at_op=ce.txt(p["torsion_at_op"]), ws_basis=ce.txt(p["ws_basis"]), viability=ce.txt(p["viability"]),
            procedure=ce.txt(p["procedure"]), gv=ce.txt(p["cond_gv"]), goo=ce.txt(p["cond_goo"]), dh=ce.txt(p["cond_dh"]),
            aetiology=ce.txt(p["aetiology"]), torsion_awaiting=ce.txt(p["torsion_awaiting"]), fixation=ce.txt(p["fixation"]),
            status=ce.txt(p["status_last_fu"])))
    df = pd.DataFrame(rows)
    df = df[~df.duplicate].copy()
    df["period2015"] = np.where(df.year.notna(), (df.year >= 2015).astype(float), np.nan)
    df.loc[df.own, "period2015"] = 1.0
    df["removal"] = df.procedure.isin(["Total splenectomy", "Partial splenectomy +/- splenopexy"])
    df["y"] = df.outcome_raw.map({"Non-viable": 1.0, "Viable": 0.0})
    # sensitivity 3: partial infarction with partial/total splenectomy coded as salvage (viable)
    df["y_sa3"] = df.y
    df.loc[(df.viability == "Partially non-viable") & df.removal, "y_sa3"] = 0.0
    df["nr_removed"] = df.outcome_raw == "NR - removed, check reason"
    return df


def omit_overlap_reports(df):
    """Reports to omit in analysis (d). Returns a set of report ids."""
    yr = df.groupby("report_id").year.first().to_dict()
    linked = df.groupby("report_id").linked.first().to_dict()
    omit = set()
    for rid, l in linked.items():
        for other in [x.strip() for x in l.replace(",", ";").split(";") if x.strip()]:
            if other not in yr:
                continue
            omit.add(rid)  # Protocol v1.8: omit the report stating overlap
    return omit


def rcs(x, knots):
    """Harrell restricted cubic spline, 3 knots: returns the one nonlinear basis column."""
    k1, k2, k3 = knots
    pos = lambda v: np.maximum(v, 0) ** 3
    return (pos(x - k1) - pos(x - k2) * (k3 - k1) / (k3 - k2) + pos(x - k3) * (k2 - k1) / (k3 - k2)) / (k3 - k1) ** 2


def fit(df, ycol, xcols, cluster="report_id"):
    d = df.dropna(subset=[ycol] + xcols).copy()
    if len(d) < 5 or d[ycol].nunique() < 2:
        return None, d
    X = sm.add_constant(d[xcols].astype(float))
    try:
        m = sm.Logit(d[ycol].astype(float), X).fit(disp=0, cov_type="cluster", cov_kwds={"groups": pd.factorize(d[cluster])[0], "use_correction": True}, use_t=False, maxiter=200)
    except Exception as e:  # separation, singular matrix
        return ("failed: %s" % e), d
    if not np.all(np.isfinite(m.bse)) or m.mle_retvals.get("converged") is False:
        return "failed: no convergence or separation", d
    return m, d


def or_row(label, m, d, term, ycol):
    if m is None or isinstance(m, str):
        return dict(analysis=label, n=len(d), events=int(d[ycol].sum()) if len(d) else 0, clusters=d.report_id.nunique() if len(d) else 0,
                    OR="", lo="", hi="", note=m or "not estimable (too few patients or one outcome class)")
    b, se = m.params[term], m.bse[term]
    return dict(analysis=label, n=len(d), events=int(d[ycol].sum()), clusters=d.report_id.nunique(),
                OR=round(math.exp(b), 3), lo=round(math.exp(b - 1.96 * se), 3), hi=round(math.exp(b + 1.96 * se), 3), note="")


def exact_ci(k, n):
    if n == 0:
        return (np.nan, np.nan)
    lo = 0.0 if k == 0 else stats.beta.ppf(0.025, k, n - k + 1)
    hi = 1.0 if k == n else stats.beta.ppf(0.975, k + 1, n - k)
    return lo, hi


def trend_test(counts, totals):
    """Cochran-Armitage test for trend, scores 1..K; returns two-sided p."""
    t = np.array(totals, float); c = np.array(counts, float); s = np.arange(1, len(t) + 1, dtype=float)
    N, R = t.sum(), c.sum()
    if N == 0 or R in (0, N):
        return np.nan
    p = R / N
    T = (s * (c - t * p)).sum()
    var = p * (1 - p) * ((s ** 2 * t).sum() - (s * t).sum() ** 2 / N)
    return float(2 * (1 - stats.norm.cdf(abs(T) / math.sqrt(var)))) if var > 0 else np.nan


def category(d):
    return pd.cut(d, [-np.inf, 2, 7, 30, np.inf], labels=["<=2 d", ">2-7 d", ">7-30 d", ">30 d"])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("workbook"); ap.add_argument("--out", required=True); ap.add_argument("--rob", default=None)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    df = build(a.workbook)
    out, rows = [], []
    P = out.append
    P("Patients after dropping same_patient_as duplicates: %d in %d reports; own series %d" % (len(df), df.report_id.nunique(), df.own.sum()))
    if (df.year < 2000).any():
        P("WARNING: %d patients in reports dated before 2000 (should not be there)" % (df.year < 2000).sum())
    P("Outcome: non-viable %d, viable %d, missing %d (of which splenectomy with viability not reported: %d)" % (
        (df.y == 1).sum(), (df.y == 0).sum(), df.y.isna().sum(), df.nr_removed.sum()))
    df["l2"] = np.log2(df.days.where(df.days > 0))
    if (df.days <= 0).any():
        P("WARNING: %d patients with duration <= 0 days left out of the log model" % (df.days <= 0).sum())
    X = ["l2", "age", "period2015"]

    def primary(label, d, ycol="y", xcols=X, term="l2"):
        m, dd = fit(d, ycol, xcols)
        rows.append(or_row(label, m, dd, term, ycol)); return m, dd

    m, dd = primary("Primary", df)
    df_cc = dd
    if m is not None and not isinstance(m,str):
        b,se=float(m.params['l2']),float(m.bse['l2'])
        pd.DataFrame([dict(beta=b,se=se,OR=np.exp(b),lo=np.exp(b-1.96*se),hi=np.exp(b+1.96*se))]).to_csv(os.path.join(a.out,'primary_precision.csv'),index=False)
    # spline
    ev = int(dd.y.sum()) if len(dd) else 0
    if isinstance(m, type(None)) or isinstance(m, str) or len(dd) == 0:
        P("Primary model not estimable.")
    else:
        df_spl = 3  # l2 + spline term + age + period -> 4 coefficients; df counted with the spline
        if ev / (len(X) + 1) >= EVENTS_PER_DF:
            kn = np.percentile(dd.l2, [10, 50, 90])
            d2 = dd.copy(); d2["sp"] = rcs(d2.l2.values, kn)
            m2, _ = fit(d2, "y", X + ["sp"])
            if m2 is not None and not isinstance(m2, str):
                pd.DataFrame([dict(p=float(m2.pvalues["sp"]))]).to_csv(os.path.join(a.out,"spline_precision.csv"),index=False)
                P("Spline: Wald p for the nonlinear term = %.3f (knots at log2 days %s)" % (m2.pvalues["sp"], np.round(kn, 2)))
            else:
                P("Spline could not be fitted.")
        else:
            P("Spline not examined: %d events, fewer than %d per degree of freedom." % (ev, EVENTS_PER_DF))
    # missing vs reported duration
    P("Duration reported for %d of %d patients with an outcome; non-viable with duration %d/%d, without %d/%d" % (
        df[df.y.notna()].days.notna().sum(), df.y.notna().sum(),
        (df[df.days.notna()].y == 1).sum(), df.days.notna().sum() - df[df.days.notna()].y.isna().sum(),
        (df[df.days.isna()].y == 1).sum(), df.days.isna().sum() - df[df.days.isna()].y.isna().sum()))
    # categories
    cc = df[df.y.notna() & df.days.notna()].copy(); cc["cat"] = category(cc.days)
    k, t = [], []
    P("Duration category: n, non-viable, proportion, exact 95% CI")
    for lab in cc.cat.cat.categories:
        s = cc[cc.cat == lab]; kk, nn = int((s.y == 1).sum()), len(s); lo, hi = exact_ci(kk, nn); k.append(kk); t.append(nn)
        P("  %-8s %3d %3d  %s  (%s to %s)" % (lab, nn, kk, ("%.2f" % (kk / nn)) if nn else "NA", "%.2f" % lo if nn else "NA", "%.2f" % hi if nn else "NA"))
        rows.append(dict(analysis="Category " + lab, n=nn, events=kk, clusters=s.report_id.nunique(), OR="", lo=round(lo, 3) if nn else "", hi=round(hi, 3) if nn else "", note="proportion"))
    tp = trend_test(k, t)
    P("  Cochran-Armitage trend p (scores 1-4) = %s" % ("NA" if np.isnan(tp) else "<0.001" if tp < 0.001 else "%.3f" % tp))
    pd.DataFrame([dict(p=tp)]).to_csv(os.path.join(a.out,'trend_precision.csv'),index=False)
    # bounding of missing durations
    if df.days.notna().any():
        lo_d, hi_d = df.days[df.days > 0].min(), df.days.max()
        for lab, val in (("Missing durations set to the shortest observed", lo_d), ("Missing durations set to the longest observed", hi_d)):
            d = df.copy(); d.loc[d.days.isna(), "days"] = val; d["l2"] = np.log2(d.days.where(d.days > 0)); primary(lab, d)
    for side in ['shortest','longest']:
        z=df[df.y.notna()].copy(); z['boundcat']=category(z.days).cat.codes+1
        z.loc[z.days.isna(),'boundcat']=1 if side=='shortest' else 4
        for j in range(1,5):
            s=z[z.boundcat==j]; k,n=int(s.y.sum()),len(s); lo,hi=exact_ci(k,n)
            rows.append(dict(analysis=f'Category bound {side} {j}',n=n,events=k,clusters='',OR='',lo=round(lo,3),hi=round(hi,3),note='proportion'))
    # secondary exposures
    d = df.copy(); d["l2th"] = np.log2(d.total_hist.where(d.total_hist > 0)); primary("Secondary: log2 total history", d, xcols=["l2th", "age", "period2015"], term="l2th")
    d = df.copy(); d["missed"] = d.missed_dx.map({"Yes": 1.0, "No": 0.0}); primary("Secondary: missed diagnosis", d, xcols=["missed", "age", "period2015"], term="missed")
    d = df.copy(); d["defer"] = d.deferred.map({"Yes": 1.0, "No": 0.0}); primary("Secondary: known diagnosis, surgery deferred", d, xcols=["defer", "age", "period2015"], term="defer")
    d = df.copy(); d["thr"] = np.where(d.platelets.notna(), (d.platelets > 450).astype(float), np.nan); primary("Secondary: thrombocytosis", d, xcols=["thr", "age", "period2015"], term="thr")
    # torsion while awaiting
    w = df[df.deferred == "Yes"]; known = w[w.torsion_awaiting.isin(["Yes","No"])]; kk, nn = int((known.torsion_awaiting == "Yes").sum()), len(known); lo, hi = exact_ci(kk, nn)
    P("Torsion while awaiting: unknown outcomes %d of %d deferred patients" % (len(w)-nn,len(w)))
    P("Torsion while awaiting surgery: %d of %d known-diagnosis patients with deferral (exact 95%% CI %.2f to %.2f)" % (kk, nn, lo, hi) if nn else "Torsion while awaiting surgery: no patients with deferral")
    # subgroups
    for lab, mask in (("Subgroup: gastric volvulus or outlet obstruction", (df.gv == "Yes") | (df.goo == "Yes")),
                      ("Subgroup: no gastric volvulus or outlet obstruction", (df.gv != "Yes") & (df.goo != "Yes")),
                      ("Subgroup: congenital", df.aetiology == "Congenital"), ("Subgroup: acquired", df.aetiology == "Acquired"),
                      ("Subgroup: diaphragmatic anomaly", df.dh == "Yes"), ("Subgroup: no diaphragmatic anomaly", df.dh != "Yes")):
        primary(lab, df[mask])
    # sensitivity analyses
    primary("SA1 without own series", df[~df.own])
    primary("SA2 pedicle torsion confirmed at operation", df[df.torsion_at_op == "Yes"])
    primary("SA3 partial splenectomy for partial infarction as salvage", df, ycol="y_sa3")
    d = df.copy(); alt = d.days_alt.notna(); d.loc[alt, "days"] = d.loc[alt, "days_alt"]; d["l2"] = np.log2(d.days.where(d.days > 0)); primary("SA4 alternative coding of intermittent or worsening episodes", d)
    if a.rob and os.path.exists(a.rob):
        rob = {r["report_id"]: r["adequate"].strip().lower() for r in csv.DictReader(open(a.rob, encoding="utf-8-sig"))}
        primary("SA5 reports judged adequate", df[df.report_id.map(rob) == "yes"])
    else:
        rows.append(dict(analysis="SA5 reports judged adequate", n="", events="", clusters="", OR="", lo="", hi="", note="not run: no --rob file (report_id, adequate)"))
    primary("SA6 without Chinese-language reports", df[df.language != "Chinese"])
    rows.append(dict(analysis="SA7 without reports before 2000", n="", events="", clusters="", OR="", lo="", hi="", note="not applicable (v1.5)"))
    rows.append(dict(analysis="SA8 mixed-effects model", n="", events="", clusters="", OR="", lo="", hi="", note="not implemented here; see analysis_main.R"))
    primary("A(a) without torsion-only inclusions", df[df.ws_basis != SP_FLAG])
    for lab, val in (("A(b) splenectomy with viability NR assigned non-viable (assumption)", 1.0), ("A(b) splenectomy with viability NR assigned viable", 0.0)):
        d = df.copy(); d["yb"] = d.y; d.loc[d.nr_removed, "yb"] = val; primary(lab, d, ycol="yb")
    primary("A(c) without lower-bound durations", df[~df.lower_bound])
    om = omit_overlap_reports(df); P("Reports omitted in analysis A(d): %s" % (sorted(om) or "none"))
    primary("A(d) without the report that states an overlap", df[~df.report_id.isin(om)])
    # reporting bias
    ser = df[df.y.notna()].copy(); sizes=df.groupby('report_id').size()
    eligible=ser.report_id.map(sizes).ge(3) & ser.consecutive.eq('Yes')
    ser["grp"] = np.where(ser.design == "Case report", "single case reports", np.where(eligible,"consecutive series >=3","other or consecutiveness NR"))
    for g, s in ser.groupby("grp"):
        P("Non-viable by %s: %d of %d" % (g, int((s.y == 1).sum()), len(s)))
    pd.DataFrame(rows).to_csv(os.path.join(a.out, "results.csv"), index=False)
    P("")
    P(pd.DataFrame(rows).to_string(index=False))
    open(os.path.join(a.out, "results.txt"), "w", encoding="utf-8").write("\n".join(out) + "\n")
    print("\n".join(out))


if __name__ == "__main__":
    main()
