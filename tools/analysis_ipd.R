#!/usr/bin/env Rscript
# Analysis script for the wandering-spleen IPD systematic review (PROSPERO CRD420261520329), protocol v1.4,
# Sections 12 and 16-18. DRAFT: not approved by the review team, never run on real data.
#
# Usage:
#   Rscript tools/analysis_ipd.R --extraction extraction_consensus.xlsx --out results_dir [--rob rob_consensus.xlsx]
#                                [--zero-as VALUE] [--min-epv 10]
#
# Input : the consensus extraction workbook built from tools/build_extraction_workbook.py (sheets Patients and Reports;
#         rows 1-3 are the header block, data from row 4) and, for sensitivity analysis 5, the consensus risk-of-bias
#         workbook built from tools/build_rob_workbook.py (rows with reviewer = Consensus).
# Output: CSV tables in --out, plus run_log.txt with R and package versions, SHA-256 of this script and of the inputs
#         (so the protocol's "script frozen before the final dataset is analysed" can be shown), warnings, and every
#         value that was not in the allowed list. Keep the input workbooks and the output folder OUTSIDE the repository.
#
# Everything marked ASSUMPTION is Claude's reading of the protocol where the protocol is silent; the review team has to
# confirm each one before the script is frozen. Nothing here replaces the statistician's judgement (Ji Wang).
#
# Grey (derived) columns of the workbooks are formulas without cached values until Excel/WPS saves the file, so they are
# recomputed here with the same rules as tools/compare_extractions.py (tests check both against the workbook formulas).

suppressPackageStartupMessages({
  library(readxl); library(sandwich); library(lmtest); library(lme4); library(digest)
})

# ------------------------------------------------------------------------------------------------ arguments
args <- commandArgs(trailingOnly = TRUE)
get_arg <- function(flag, default = NULL) {
  i <- match(flag, args)
  if (is.na(i) || i == length(args)) default else args[i + 1]
}
f_extraction <- get_arg("--extraction")
out_dir      <- get_arg("--out")
f_rob        <- get_arg("--rob")
zero_as      <- get_arg("--zero-as")
min_epv      <- as.numeric(get_arg("--min-epv", "10"))   # protocol Section 16: at least 10 events per model df for the spline
if (is.null(f_extraction) || is.null(out_dir)) {
  stop("usage: Rscript analysis_ipd.R --extraction FILE.xlsx --out DIR [--rob FILE.xlsx] [--zero-as VALUE] [--min-epv 10]")
}
dir.create(out_dir, showWarnings = FALSE, recursive = TRUE)

log_lines <- character(0)
logmsg <- function(...) { s <- paste0(...); log_lines <<- c(log_lines, s); message(s) }
write_out <- function(x, name) {
  write.csv(x, file.path(out_dir, name), row.names = FALSE, na = "")
  logmsg("wrote ", name, " (", nrow(x), " rows)")
}

# ------------------------------------------------------------------------------------------------ reading
read_sheet <- function(path, sheet) {
  raw <- suppressMessages(read_excel(path, sheet = sheet, col_names = FALSE, col_types = "text", .name_repair = "minimal"))
  codes <- as.character(unlist(raw[1, ]))
  keep <- !is.na(codes) & nzchar(codes)
  d <- as.data.frame(raw[-(1:3), keep, drop = FALSE], stringsAsFactors = FALSE)
  names(d) <- codes[keep]
  for (nm in names(d)) {
    v <- trimws(as.character(d[[nm]]))
    v[!nzchar(v)] <- NA
    d[[nm]] <- v
  }
  d
}
num <- function(x) suppressWarnings(as.numeric(x))

# allowed values (mirror the Lists sheet); anything else is reported in the log, not silently recoded
ALLOWED <- list(
  sex = c("M", "F", "NR"), yn_nr = c("Yes", "No", "NR"),
  aetiology = c("Congenital", "Acquired", "NR"),
  viability = c("Viable", "Partially non-viable", "Non-viable", "NR", "Not applicable"),
  procedure = c("Detorsion only", "Splenopexy", "Partial splenectomy +/- splenopexy", "Total splenectomy",
                "Autotransplantation", "No operation", "NR"),
  torsion_awaiting = c("Yes", "No", "Not applicable"),
  dur_category = c("<=2 d", "3-7 d", "8-30 d", ">30 d")
)
canon_to <- function(x, allowed, field) {
  # case-insensitive match to the canonical spelling; unknown values are kept and logged
  out <- x
  low <- tolower(allowed)
  hit <- match(tolower(x), low)
  out[!is.na(hit)] <- allowed[hit[!is.na(hit)]]
  bad <- unique(x[is.na(hit) & !is.na(x)])
  if (length(bad)) logmsg("WARNING: values not in the allowed list for ", field, ": ", paste(bad, collapse = " | "))
  out
}

pat <- read_sheet(f_extraction, "Patients")
reps <- read_sheet(f_extraction, "Reports")
pat <- pat[!is.na(pat$patient_id), , drop = FALSE]
reps <- reps[!is.na(reps$report_id), , drop = FALSE]
logmsg("Patients rows with a patient_id: ", nrow(pat), "; Reports rows with a report_id: ", nrow(reps))
if (anyDuplicated(pat$patient_id)) stop("duplicate patient_id in Patients: ", paste(pat$patient_id[duplicated(pat$patient_id)], collapse = ", "))
if (anyDuplicated(reps$report_id)) stop("duplicate report_id in Reports: ", paste(reps$report_id[duplicated(reps$report_id)], collapse = ", "))
missing_rep <- setdiff(unique(pat$report_id), reps$report_id)
if (length(missing_rep)) stop("report_id in Patients but not in Reports: ", paste(missing_rep, collapse = ", "))

for (f in c("sex")) pat[[f]] <- canon_to(pat[[f]], ALLOWED$sex, f)
for (f in c("cond_gv", "cond_goo", "cond_dh", "missed_dx", "known_dx_deferred", "recurrence", "further_surgery",
            "idx_dur_intermittent")) pat[[f]] <- canon_to(pat[[f]], ALLOWED$yn_nr, f)
pat$aetiology        <- canon_to(pat$aetiology, ALLOWED$aetiology, "aetiology")
pat$viability        <- canon_to(pat$viability, ALLOWED$viability, "viability")
pat$procedure        <- canon_to(pat$procedure, ALLOWED$procedure, "procedure")
pat$torsion_awaiting <- canon_to(pat$torsion_awaiting, ALLOWED$torsion_awaiting, "torsion_awaiting")
pat$torsion_at_op    <- canon_to(pat$torsion_at_op, ALLOWED$yn_nr, "torsion_at_op")
pat$idx_dur_cat_imprecise <- canon_to(pat$idx_dur_cat_imprecise, ALLOWED$dur_category, "idx_dur_cat_imprecise")

for (f in c("age_years", "idx_dur_days", "idx_dur_alt_days", "total_hist_days", "platelets", "spleen_size_cm", "followup_months"))
  pat[[paste0(f, "_num")]] <- num(pat[[f]])
reps$year_num <- num(reps$year)

# ------------------------------------------------------------------------------------------------ derived variables
derive_category <- function(days, imprecise) {
  d <- num(days)
  out <- rep(NA_character_, length(d))
  out[!is.na(d) & d <= 2] <- "<=2 d"
  out[!is.na(d) & d > 2 & d <= 7] <- "3-7 d"
  out[!is.na(d) & d > 7 & d <= 30] <- "8-30 d"
  out[!is.na(d) & d > 30] <- ">30 d"
  fill <- is.na(d) & !is.na(imprecise)
  out[fill] <- imprecise[fill]
  out[is.na(d) & is.na(imprecise) & !is.na(days) & toupper(days) == "NR"] <- "NR"
  out
}
derive_outcome <- function(viability, procedure) {
  removal <- procedure %in% c("Total splenectomy", "Partial splenectomy +/- splenopexy")
  out <- rep(NA_character_, length(viability))
  out[viability %in% "Non-viable"] <- "Non-viable"
  out[viability %in% "Viable"] <- "Viable"
  out[viability %in% "Partially non-viable" & removal] <- "Non-viable"
  out[viability %in% "Partially non-viable" & !removal] <- "Review"
  out[viability %in% "NR" & removal] <- "NR - removed, check reason"
  out[viability %in% "NR" & !removal] <- "NR"
  out[viability %in% "Not applicable"] <- "Not applicable"
  out
}

pat$idx_dur_category <- derive_category(pat$idx_dur_days, pat$idx_dur_cat_imprecise)
pat$primary_outcome  <- derive_outcome(pat$viability, pat$procedure)
pat$thrombocytosis   <- ifelse(!is.na(pat$platelets_num), ifelse(pat$platelets_num > 450, "Yes", "No"),
                               ifelse(!is.na(pat$platelets) & toupper(pat$platelets) == "NR", "NR", NA))
pat$own_patient      <- ifelse(pat$report_id == "OWN", "Yes", "No")

pat <- merge(pat, reps[, c("report_id", "year", "year_num", "language", "design", "consecutive")],
             by = "report_id", all.x = TRUE, sort = FALSE, suffixes = c("", "_rep"))
pat$pub_period <- ifelse(is.na(pat$year_num), NA,
                         ifelse(pat$year_num < 2000, "before 2000", ifelse(pat$year_num <= 2014, "2000-2014", "2015 onward")))
pat$pub_period <- factor(pat$pub_period, levels = c("before 2000", "2000-2014", "2015 onward"))
pat$n_in_report <- ave(rep(1, nrow(pat)), pat$report_id, FUN = sum)   # patients of the report in the Patients sheet

# zero or negative durations cannot be log-transformed; the protocol says nothing about them -> a decision is required
bad0 <- which(!is.na(pat$idx_dur_days_num) & pat$idx_dur_days_num <= 0)
if (length(bad0)) {
  if (is.null(zero_as)) {
    stop("idx_dur_days <= 0 for ", length(bad0), " patient(s) (", paste(head(pat$patient_id[bad0], 5), collapse = ", "),
         "): the protocol does not say how to log-transform a duration of 0 days. Decide (e.g. 0.5 d as in rule 4), then run again with --zero-as VALUE.")
  }
  logmsg("ASSUMPTION in force: ", length(bad0), " duration(s) <= 0 replaced by ", zero_as, " d (--zero-as)")
  pat$idx_dur_days_num[bad0] <- as.numeric(zero_as)
}
bad0t <- which(!is.na(pat$total_hist_days_num) & pat$total_hist_days_num <= 0)
if (length(bad0t)) {
  if (is.null(zero_as)) stop("total_hist_days <= 0 for ", length(bad0t), " patient(s); use --zero-as VALUE")
  pat$total_hist_days_num[bad0t] <- as.numeric(zero_as)
}
pat$log2dur  <- ifelse(!is.na(pat$idx_dur_days_num), log2(pat$idx_dur_days_num), NA)
pat$log2hist <- ifelse(!is.na(pat$total_hist_days_num), log2(pat$total_hist_days_num), NA)
pat$nonviable <- ifelse(pat$primary_outcome %in% "Non-viable", 1L, ifelse(pat$primary_outcome %in% "Viable", 0L, NA))

# extraction still incomplete? (blank = not yet extracted)
for (f in c("viability", "procedure", "idx_dur_days", "age_years")) {
  nb <- sum(is.na(pat[[f]]))
  if (nb) logmsg("WARNING: ", nb, " patient(s) with a BLANK ", f, " (blank = not yet extracted; NR = not reported)")
}

# ------------------------------------------------------------------------------------------------ population
flow <- data.frame(step = character(), n = integer(), stringsAsFactors = FALSE)
add_flow <- function(step, n) flow[nrow(flow) + 1, ] <<- list(step, as.integer(n))
add_flow("Patients with a patient_id", nrow(pat))
dup <- !is.na(pat$same_patient_as)
add_flow("  minus duplicates of a patient in another report (same_patient_as filled)", sum(dup))
pop <- pat[!dup, , drop = FALSE]
add_flow("Unique children", nrow(pop))
adult <- !is.na(pop$age_years_num) & pop$age_years_num >= 18
add_flow("  minus age 18 or older (should not be in the sheet)", sum(adult))
pop <- pop[!adult, , drop = FALSE]
not_operated <- pop$procedure %in% "No operation" | pop$viability %in% "Not applicable"
add_flow("  of whom managed without operation (descriptive only)", sum(not_operated))
op <- pop[!not_operated, , drop = FALSE]
add_flow("Operated children", nrow(op))
add_flow("  minus primary outcome not Viable/Non-viable (Review, NR, blank)", sum(is.na(op$nonviable)))
oc <- op[!is.na(op$nonviable), , drop = FALSE]
add_flow("Outcome population (primary outcome known)", nrow(oc))
add_flow("  minus index-episode duration missing (no number)", sum(is.na(oc$log2dur)))
add_flow("  minus age missing (NR or blank)", sum(!is.na(oc$log2dur) & is.na(oc$age_years_num)))
cc <- oc[!is.na(oc$log2dur) & !is.na(oc$age_years_num) & !is.na(oc$pub_period), , drop = FALSE]
add_flow("Primary analysis population (complete cases: duration, age, period)", nrow(cc))
add_flow("  of which non-viable spleen (events)", sum(cc$nonviable))
add_flow("  reports (clusters)", length(unique(cc$report_id)))
write_out(flow, "01_population_flow.csv")
write_out(pop[, c("patient_id", "report_id", "own_patient", "age_years_num", "sex", "idx_dur_days_num", "idx_dur_category",
                  "total_hist_days_num", "viability", "procedure", "primary_outcome", "thrombocytosis", "pub_period",
                  "language", "design")], "00_analysis_dataset.csv")

# ------------------------------------------------------------------------------------------------ helpers
exact_ci <- function(x, n) {
  if (is.na(n) || n == 0) return(c(NA_real_, NA_real_))
  as.numeric(binom.test(x, n)$conf.int)
}
count_row <- function(label, x, n) {
  ci <- exact_ci(x, n)
  data.frame(group = label, n = n, events = x, proportion = ifelse(n > 0, x / n, NA), ci_low = ci[1], ci_high = ci[2])
}
fit_logit <- function(formula, data, term, label, note = "") {
  warns <- character(0)
  fit <- withCallingHandlers(
    tryCatch(glm(formula, data = data, family = binomial()), error = function(e) e),
    warning = function(w) { warns <<- c(warns, conditionMessage(w)); invokeRestart("muffleWarning") })
  ev <- sum(data$nonviable)
  base <- data.frame(analysis = label, term = term, n = nrow(data), events = ev, clusters = length(unique(data$report_id)),
                     logOR = NA_real_, se = NA_real_, OR = NA_real_, ci_low = NA_real_, ci_high = NA_real_, p = NA_real_,
                     ci_low_t = NA_real_, ci_high_t = NA_real_, model_df = NA_integer_, events_per_df = NA_real_, note = note,
                     stringsAsFactors = FALSE)
  if (inherits(fit, "error")) { base$note <- paste(note, "MODEL FAILED:", conditionMessage(fit)); return(base) }
  if (!(term %in% names(coef(fit))) || is.na(coef(fit)[term])) { base$note <- paste(note, "term not estimable"); return(base) }
  V <- tryCatch(sandwich::vcovCL(fit, cluster = data$report_id, type = "HC1"), error = function(e) NULL)
  if (is.null(V)) { base$note <- paste(note, "robust variance failed"); return(base) }
  b <- unname(coef(fit)[term]); se <- sqrt(V[term, term])
  G <- base$clusters
  tcrit <- if (G > 1) qt(0.975, G - 1) else NA_real_
  df_model <- length(coef(fit)) - 1
  base[1, c("logOR", "se", "OR", "ci_low", "ci_high", "p", "ci_low_t", "ci_high_t", "model_df", "events_per_df")] <-
    list(b, se, exp(b), exp(b - 1.96 * se), exp(b + 1.96 * se), 2 * pnorm(-abs(b / se)),
         exp(b - tcrit * se), exp(b + tcrit * se), df_model, min(ev, nrow(data) - ev) / df_model)
  notes <- note
  if (length(warns)) notes <- paste(notes, "WARNINGS:", paste(unique(warns), collapse = "; "))
  if (base$events_per_df < min_epv) notes <- paste(notes, sprintf("events per df %.1f < %g", base$events_per_df, min_epv))
  base$note <- trimws(notes)
  base
}
primary_formula <- nonviable ~ log2dur + age_years_num + pub_period

# ------------------------------------------------------------------------------------------------ descriptive
describe <- function(d, label) {
  rows <- list()
  add <- function(var, level, n, pct) rows[[length(rows) + 1]] <<- data.frame(population = label, variable = var, level = level, n = n, pct = pct, stringsAsFactors = FALSE)
  N <- nrow(d)
  add("children", "", N, NA)
  for (v in c("sex", "aetiology", "presentation", "cond_gv", "cond_goo", "cond_dh", "missed_dx", "known_dx_deferred",
              "torsion_at_op", "approach", "procedure", "viability", "primary_outcome", "thrombocytosis", "status_last_fu",
              "pub_period", "language", "design")) {
    if (!(v %in% names(d))) next
    x <- as.character(d[[v]]); x[is.na(x)] <- "(blank)"
    tb <- table(x)
    for (lv in names(tb)) add(v, lv, as.integer(tb[[lv]]), 100 * as.integer(tb[[lv]]) / N)
  }
  for (v in c("age_years_num", "idx_dur_days_num", "total_hist_days_num", "platelets_num", "spleen_size_cm_num", "followup_months_num")) {
    x <- d[[v]]; x <- x[!is.na(x)]
    if (length(x)) {
      q <- quantile(x, c(0.25, 0.5, 0.75), names = FALSE)
      add(v, sprintf("median %.2f (IQR %.2f-%.2f; range %.2f-%.2f)", q[2], q[1], q[3], min(x), max(x)), length(x), 100 * length(x) / N)
    } else add(v, "no values", 0L, 0)
  }
  # additional outcomes (protocol Section 13)
  removed_viable <- d$primary_outcome %in% "Viable" & d$procedure %in% c("Total splenectomy", "Partial splenectomy +/- splenopexy")
  add("additional: viable spleen removed", "", sum(removed_viable), 100 * sum(removed_viable) / N)
  if (any(removed_viable)) {
    tb <- table(ifelse(is.na(d$reason_viable_removed[removed_viable]), "(blank)", d$reason_viable_removed[removed_viable]))
    for (lv in names(tb)) add("additional: reason for removing a viable spleen", lv, as.integer(tb[[lv]]), 100 * as.integer(tb[[lv]]) / sum(removed_viable))
  }
  do.call(rbind, rows)
}
write_out(rbind(describe(pop, "all unique children"), describe(oc, "outcome population"), describe(cc, "primary analysis population")),
          "02_descriptives.csv")

# ------------------------------------------------------------------------------------------------ primary analysis (Section 16)
prim <- fit_logit(primary_formula, cc, "log2dur", "PRIMARY: non-viable spleen ~ log2(index-episode days) + age + period; OR per doubling",
                  note = "cluster-robust SE by report (sandwich::vcovCL, HC1); normal-based CI; t(G-1) CI in the *_t columns")
# non-linearity: restricted cubic spline with 3 knots, only if events allow >= min_epv events per model df
spline_note <- "not done"
n_ev <- sum(cc$nonviable)
spline_df <- 2 + 1 + 2      # spline (linear + 1 nonlinear term) + age + two period indicators
if (nrow(cc) > 0 && n_ev / spline_df >= min_epv && min(n_ev, nrow(cc) - n_ev) / spline_df >= min_epv) {
  sp <- Hmisc::rcspline.eval(cc$log2dur, nk = 3, inclx = TRUE)
  cs <- cbind(cc, rcs1 = sp[, 1], rcs2 = sp[, 2])
  f_sp <- fit_logit(nonviable ~ rcs1 + rcs2 + age_years_num + pub_period, cs, "rcs2",
                    "NON-LINEARITY: restricted cubic spline (3 knots); robust Wald test of the non-linear term",
                    note = "the OR columns are not interpretable for the non-linear term; p is the test of non-linearity")
  spline_note <- sprintf("done: non-linear term p = %.4f", f_sp$p)
  prim <- rbind(prim, f_sp)
} else {
  spline_note <- sprintf("not done: %d events (minority class %d) allow %.1f events per df of the spline model (df = %d); the protocol needs at least %g",
                         n_ev, min(n_ev, nrow(cc) - n_ev), min(n_ev, nrow(cc) - n_ev) / spline_df, spline_df, min_epv)
}
logmsg("spline: ", spline_note)
prim$note[1] <- trimws(paste(prim$note[1], "| spline", spline_note))
write_out(prim, "03_primary_model.csv")

# ------------------------------------------------------------------------------------------------ categories and trend
cat_table <- function(d, label) {
  d <- d[!is.na(d$idx_dur_category) & d$idx_dur_category != "NR", , drop = FALSE]
  rows <- do.call(rbind, lapply(ALLOWED$dur_category, function(cn) {
    sub <- d[d$idx_dur_category == cn, ]
    r <- count_row(cn, sum(sub$nonviable), nrow(sub)); r$population <- label; r
  }))
  keep <- rows$n > 0
  trend_p <- NA_real_; trend_stat <- NA_real_
  if (sum(keep) >= 2 && sum(rows$events[keep]) > 0 && sum(rows$events[keep]) < sum(rows$n[keep])) {
    tt <- prop.trend.test(rows$events[keep], rows$n[keep], score = which(keep))
    trend_p <- tt$p.value; trend_stat <- unname(tt$statistic)
  }
  rows$trend_chisq <- trend_stat; rows$trend_p <- trend_p
  rows[, c("population", "group", "n", "events", "proportion", "ci_low", "ci_high", "trend_chisq", "trend_p")]
}
cat_out <- cat_table(oc, "outcome population (category from a number or from an imprecise term, rule 5)")
cat_out$note <- "exact (Clopper-Pearson) CIs; ASSUMPTION: trend test = Cochran-Armitage chi-square (stats::prop.trend.test), scores 1-4; the protocol only says 'a test for trend'"
write_out(cat_out, "04_categories_and_trend.csv")

# ------------------------------------------------------------------------------------------------ secondary exposures
sec <- list()
hist_d <- oc[!is.na(oc$log2hist) & !is.na(oc$age_years_num) & !is.na(oc$pub_period), , drop = FALSE]
sec[[1]] <- fit_logit(nonviable ~ log2hist + age_years_num + pub_period, hist_d, "log2hist",
                      "SECONDARY: total symptom history, OR per doubling (same model as primary)")
for (ex in c("missed_dx", "known_dx_deferred")) {
  d <- oc[oc[[ex]] %in% c("Yes", "No") & !is.na(oc$age_years_num) & !is.na(oc$pub_period), , drop = FALSE]
  d$expo <- factor(d[[ex]], levels = c("No", "Yes"))
  sec[[length(sec) + 1]] <- fit_logit(nonviable ~ expo + age_years_num + pub_period, d, "expoYes",
                                      paste0("SECONDARY: ", ex, " (Yes vs No), same covariates"))
}
write_out(do.call(rbind, sec), "05_secondary_exposures.csv")

# torsion while awaiting surgery; failures after splenopexy by technique
kd <- pop[pop$known_dx_deferred %in% "Yes", , drop = FALSE]
ta <- count_row("known diagnosis with surgery deferred: torsion while awaiting surgery", sum(kd$torsion_awaiting %in% "Yes"), nrow(kd))
ta$note <- "denominator: all unique children with known_dx_deferred = Yes (operated or not); exact 95% CI"
write_out(ta, "06_torsion_while_awaiting.csv")

sp_pop <- pop[pop$procedure %in% c("Splenopexy", "Partial splenectomy +/- splenopexy"), , drop = FALSE]
sp_pop$fail_known <- !(is.na(sp_pop$recurrence) | sp_pop$recurrence == "NR") | !(is.na(sp_pop$further_surgery) | sp_pop$further_surgery == "NR")
sp_pop$failure <- sp_pop$recurrence %in% "Yes" | sp_pop$further_surgery %in% "Yes"
sp_pop$tech <- ifelse(is.na(sp_pop$fixation), "(blank)", sp_pop$fixation)
fail_tab <- do.call(rbind, lapply(sort(unique(sp_pop$tech)), function(t) {
  s <- sp_pop[sp_pop$tech == t, ]
  known <- s[s$fail_known | s$failure, ]
  r <- count_row(t, sum(known$failure), nrow(known))
  r$unknown_outcome <- nrow(s) - nrow(known)
  r
}))
if (!is.null(fail_tab)) fail_tab$note <- "ASSUMPTION: failure = recurrence or re-torsion = Yes, or further surgery = Yes; children with both NR are counted as unknown, not as successes"
write_out(if (is.null(fail_tab)) data.frame(note = "no splenopexy patients") else fail_tab, "07_failures_after_splenopexy.csv")

# ------------------------------------------------------------------------------------------------ missing data and bounding
oc$dur_reported <- !is.na(oc$log2dur)
md <- list()
add_md <- function(var, with_v, without_v, test, p) md[[length(md) + 1]] <<- data.frame(variable = var, with_duration = with_v, without_duration = without_v, test = test, p = p, stringsAsFactors = FALSE)
add_md("n", sum(oc$dur_reported), sum(!oc$dur_reported), "", NA)
if (sum(!oc$dur_reported) > 0 && sum(oc$dur_reported) > 0) {
  w <- oc[oc$dur_reported, ]; wo <- oc[!oc$dur_reported, ]
  add_md("non-viable spleen n (%)", sprintf("%d (%.0f%%)", sum(w$nonviable), 100 * mean(w$nonviable)),
         sprintf("%d (%.0f%%)", sum(wo$nonviable), 100 * mean(wo$nonviable)), "Fisher exact",
         tryCatch(fisher.test(table(oc$dur_reported, oc$nonviable))$p.value, error = function(e) NA))
  if (sum(!is.na(w$age_years_num)) > 1 && sum(!is.na(wo$age_years_num)) > 1)
    add_md("age, median years", sprintf("%.2f", median(w$age_years_num, na.rm = TRUE)), sprintf("%.2f", median(wo$age_years_num, na.rm = TRUE)),
           "Wilcoxon rank-sum", tryCatch(suppressWarnings(wilcox.test(age_years_num ~ dur_reported, data = oc)$p.value), error = function(e) NA))
  for (v in c("pub_period", "language", "sex")) {
    tb <- table(oc$dur_reported, as.character(oc[[v]]))
    add_md(paste0(v, " (distribution)"), paste(paste0(colnames(tb), ":", tb["TRUE", ]), collapse = "; "),
           if ("FALSE" %in% rownames(tb)) paste(paste0(colnames(tb), ":", tb["FALSE", ]), collapse = "; ") else "",
           "Fisher exact", tryCatch(fisher.test(tb, simulate.p.value = TRUE, B = 10000)$p.value, error = function(e) NA))
  }
}
write_out(do.call(rbind, md), "08_missing_duration_comparison.csv")

bnd <- list()
for (scn in c("shortest", "longest")) {
  d <- oc
  miss <- is.na(d$idx_dur_category) | d$idx_dur_category == "NR"
  d$idx_dur_category[miss] <- if (scn == "shortest") "<=2 d" else ">30 d"
  r <- cat_table(d, paste0("bounding: all missing durations assigned to the ", scn, " category"))
  r$note <- paste0(sum(miss), " children with a missing duration assigned to the ", scn, " category (protocol Section 16)")
  bnd[[length(bnd) + 1]] <- r
}
write_out(do.call(rbind, bnd), "09_bounding_categories.csv")
# ASSUMPTION: the protocol assigns missing durations to a CATEGORY; for the continuous model the smallest / largest observed duration is used
bm <- list()
for (scn in c("shortest", "longest")) {
  d <- oc[!is.na(oc$age_years_num) & !is.na(oc$pub_period), , drop = FALSE]
  v <- if (scn == "shortest") min(d$log2dur, na.rm = TRUE) else max(d$log2dur, na.rm = TRUE)
  nmiss <- sum(is.na(d$log2dur)); d$log2dur[is.na(d$log2dur)] <- v
  bm[[length(bm) + 1]] <- fit_logit(primary_formula, d, "log2dur", paste0("BOUNDING (continuous): missing durations set to the ", scn, " observed value"),
                                   note = paste0("ASSUMPTION (the protocol names categories): ", nmiss, " missing durations set to ", round(2^v, 2), " d"))
}
write_out(do.call(rbind, bm), "10_bounding_continuous.csv")

# ------------------------------------------------------------------------------------------------ reporting bias
rb <- oc
rb$source_type <- ifelse(rb$design %in% "Case report", "single case report",
                   ifelse(rb$design %in% c("Case series", "Cohort") & rb$consecutive %in% "Yes" & rb$n_in_report >= 3,
                          "series of >=3 consecutive patients", NA))
rb <- rb[!is.na(rb$source_type), ]
rbt <- do.call(rbind, lapply(sort(unique(rb$source_type)), function(g) count_row(g, sum(rb$nonviable[rb$source_type == g]), sum(rb$source_type == g))))
if (!is.null(rbt) && nrow(rbt) == 2) rbt$fisher_p <- tryCatch(fisher.test(table(rb$source_type, rb$nonviable))$p.value, error = function(e) NA)
rbt$note <- "ASSUMPTION: 'series' = design Case series/Cohort, consecutive = Yes and >= 3 patients of the report in the Patients sheet"
write_out(if (is.null(rbt)) data.frame(note = "no eligible reports") else rbt, "11_reporting_bias.csv")

# ------------------------------------------------------------------------------------------------ subgroups (Section 17)
sub_out <- list()
run_sub <- function(label, flag) {
  for (lv in c(TRUE, FALSE)) {
    d <- cc[!is.na(flag[match(cc$patient_id, oc$patient_id)]) & (flag[match(cc$patient_id, oc$patient_id)] == lv), , drop = FALSE]
    nm <- paste0(label, ": ", if (lv) "yes" else "no")
    ev <- sum(d$nonviable)
    if (nrow(d) > 0 && min(ev, nrow(d) - ev) / 4 >= min_epv) {
      r <- fit_logit(primary_formula, d, "log2dur", paste0("SUBGROUP ", nm))
    } else {
      r <- data.frame(analysis = paste0("SUBGROUP ", nm), term = "log2dur", n = nrow(d), events = ev, clusters = length(unique(d$report_id)),
                      logOR = NA, se = NA, OR = NA, ci_low = NA, ci_high = NA, p = NA, ci_low_t = NA, ci_high_t = NA,
                      model_df = NA, events_per_df = ifelse(nrow(d) > 0, min(ev, nrow(d) - ev) / 4, NA),
                      note = sprintf("descriptive only: fewer than %g events per model df (4)", min_epv), stringsAsFactors = FALSE)
    }
    sub_out[[length(sub_out) + 1]] <<- r
  }
}
run_sub("gastric volvulus or gastric outlet obstruction", ifelse(is.na(oc$cond_gv) & is.na(oc$cond_goo), NA, (oc$cond_gv %in% "Yes") | (oc$cond_goo %in% "Yes")))
run_sub("acquired (vs congenital) wandering spleen", ifelse(oc$aetiology %in% c("Acquired", "Congenital"), oc$aetiology == "Acquired", NA))
run_sub("diaphragmatic hernia or eventration", ifelse(oc$cond_dh %in% c("Yes", "No"), oc$cond_dh == "Yes", NA))
write_out(do.call(rbind, sub_out), "12_subgroups.csv")

# ------------------------------------------------------------------------------------------------ sensitivity analyses (Section 18)
sens <- list()
add_sens <- function(r) sens[[length(sens) + 1]] <<- r
ccb <- function(d) d[!is.na(d$log2dur) & !is.na(d$age_years_num) & !is.na(d$pub_period) & !is.na(d$nonviable), , drop = FALSE]
add_sens(fit_logit(primary_formula, cc, "log2dur", "SA0 primary (for reference)"))
add_sens(fit_logit(primary_formula, cc[cc$own_patient != "Yes", ], "log2dur", "SA1 excluding our own patients"))
add_sens(fit_logit(primary_formula, cc[cc$torsion_at_op %in% "Yes", ], "log2dur", "SA2 restricted to torsion confirmed at operation"))
# SA3: partial splenectomy for partial infarction coded as salvage
oc3 <- oc
sal <- oc3$viability %in% "Partially non-viable" & oc3$procedure %in% "Partial splenectomy +/- splenopexy"
oc3$nonviable[sal] <- 0L
add_sens(fit_logit(primary_formula, ccb(oc3), "log2dur", "SA3 partial splenectomy for partial infarction coded as salvage",
                   note = paste0(sum(sal), " patient(s) recoded to viable")))
# SA4: alternative coding of intermittent or worsening episodes (duration of the worsening period)
oc4 <- oc
alt <- oc4$idx_dur_intermittent %in% "Yes" & !is.na(oc4$idx_dur_alt_days_num) & oc4$idx_dur_alt_days_num > 0
oc4$log2dur[alt] <- log2(oc4$idx_dur_alt_days_num[alt])
add_sens(fit_logit(primary_formula, ccb(oc4), "log2dur", "SA4 alternative coding of intermittent or worsening episodes (rule 6)",
                   note = paste0(sum(alt), " patient(s) with the alternative duration")))
# SA5: only reports judged adequate in the risk-of-bias assessment
if (!is.null(f_rob)) {
  rob <- read_sheet(f_rob, "RoB")
  rob <- rob[tolower(rob$reviewer) %in% "consensus" & !is.na(rob$report_id), , drop = FALSE]
  ade <- ifelse(is.na(rob$q_exposure) | is.na(rob$q_outcome) | is.na(rob$q_reporting), NA,
                ifelse(tolower(rob$q_exposure) == "yes" & tolower(rob$q_outcome) == "yes" & tolower(rob$q_reporting) == "yes", "Yes", "No"))
  ok_reports <- rob$report_id[ade %in% "Yes"]
  unrated <- setdiff(unique(cc$report_id), rob$report_id)
  add_sens(fit_logit(primary_formula, cc[cc$report_id %in% ok_reports, ], "log2dur", "SA5 reports judged adequate in the risk-of-bias assessment",
                     note = paste0(length(ok_reports), " adequate report(s); ", length(unrated), " report(s) of the analysis population without a consensus rating are excluded")))
} else {
  add_sens(data.frame(analysis = "SA5 reports judged adequate in the risk-of-bias assessment", note = "not run: no --rob file given"))
}
add_sens(fit_logit(primary_formula, cc[!(cc$language %in% "Chinese"), ], "log2dur", "SA6 excluding Chinese-language reports"))
add_sens(fit_logit(primary_formula, cc[!is.na(cc$year_num) & cc$year_num >= 2000, ], "log2dur", "SA7 excluding reports published before 2000"))
# SA8: mixed-effects logistic regression with a random intercept for each report
m_warn <- character(0)
glmm <- withCallingHandlers(
  tryCatch(glmer(nonviable ~ log2dur + age_years_num + pub_period + (1 | report_id), data = cc, family = binomial(),
                 control = glmerControl(optimizer = "bobyqa", optCtrl = list(maxfun = 2e5))), error = function(e) e),
  warning = function(w) { m_warn <<- c(m_warn, conditionMessage(w)); invokeRestart("muffleWarning") },
  message = function(m) { m_warn <<- c(m_warn, trimws(conditionMessage(m))); invokeRestart("muffleMessage") })
if (inherits(glmm, "error")) {
  add_sens(data.frame(analysis = "SA8 mixed-effects logistic regression, random intercept for report", note = paste("MODEL FAILED:", conditionMessage(glmm))))
} else {
  cf <- summary(glmm)$coefficients["log2dur", ]
  add_sens(data.frame(analysis = "SA8 mixed-effects logistic regression, random intercept for report", term = "log2dur", n = nrow(cc),
                      events = sum(cc$nonviable), clusters = length(unique(cc$report_id)), logOR = cf[1], se = cf[2], OR = exp(cf[1]),
                      ci_low = exp(cf[1] - 1.96 * cf[2]), ci_high = exp(cf[1] + 1.96 * cf[2]), p = cf[4],
                      note = trimws(paste("model-based Wald CI (lme4::glmer, bobyqa);", if (length(m_warn)) paste("MESSAGES:", paste(unique(m_warn), collapse = "; ")) else "")),
                      stringsAsFactors = FALSE))
}
all_cols <- unique(unlist(lapply(sens, names)))
sens <- lapply(sens, function(r) { for (cn in setdiff(all_cols, names(r))) r[[cn]] <- NA; r[, all_cols] })
write_out(do.call(rbind, sens), "13_sensitivity_analyses.csv")

# ------------------------------------------------------------------------------------------------ run log
pk <- sapply(c("readxl", "sandwich", "lmtest", "lme4", "digest", "Hmisc"), function(p) as.character(packageVersion(p)))
script_path <- sub("^--file=", "", grep("^--file=", commandArgs(FALSE), value = TRUE)[1])
logmsg("---- run log ----")
logmsg("date: ", format(Sys.time(), "%Y-%m-%d %H:%M:%S %Z"))
logmsg(R.version.string)
logmsg("packages: ", paste(names(pk), pk, sep = " ", collapse = "; "))
logmsg("script: ", script_path, " sha256 ", if (file.exists(script_path)) digest(script_path, algo = "sha256", file = TRUE) else "unknown")
logmsg("extraction file sha256 ", digest(f_extraction, algo = "sha256", file = TRUE))
if (!is.null(f_rob)) logmsg("risk-of-bias file sha256 ", digest(f_rob, algo = "sha256", file = TRUE))
logmsg("arguments: ", paste(args, collapse = " "))
writeLines(log_lines, file.path(out_dir, "run_log.txt"))
