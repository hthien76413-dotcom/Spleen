# Registered analysis plan, protocol v1.8 (Sections 16-18). R version for the statistician (Ji Wang).
#
# Original-author provenance (before this review): R is not installed in the environment where it was written. The logic was tested only in the
# Python twin analysis_crosscheck.py on simulated data. Run both on the same workbook and compare the numbers before trusting either.
#
# Usage (from the repository root):
#   Rscript analysis/analysis_main.R CONSENSUS.xlsx OUT_DIR [rob.csv]
# Packages: readxl, sandwich, lmtest, lme4. Print sessionInfo() into the Methods (the protocol asks for the R version).
#
# Data rules (same as the Python twin): Reports and Patients sheets of the consensus workbook, header codes in row 1, data from row 4;
# patients with same_patient_as filled are dropped; outcome: Non-viable = 1, Viable = 0, Partially non-viable counts as non-viable if
# a total or partial splenectomy was done, Review / NR / Not applicable = missing; exposure log2(idx_dur_days); complete cases;
# period 2000-2014 vs 2015 onward from Reports.year, own series (OWN) = 2015 onward; cluster = report_id.
# Choices the protocol does not fix (change here if the statistician decides otherwise):
#   trend test = Cochran-Armitage with scores 1-4; bounding of missing durations = smallest / largest observed duration;
#   spline = restricted cubic spline, 3 knots at the 10th, 50th, 90th percentiles of log2 days, only if events per df >= 10;
#   analysis A(d): of two linked reports the report carrying the overlap declaration is omitted.

suppressPackageStartupMessages({library(readxl); library(sandwich); library(lmtest)})
args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 2) stop("Usage: Rscript analysis_main.R CONSENSUS.xlsx OUT_DIR [rob.csv]")
wbfile <- args[1]; outdir <- args[2]; robfile <- if (length(args) >= 3) args[3] else NA
dir.create(outdir, showWarnings = FALSE, recursive = TRUE)
SP_FLAG <- "Torsion only, position not stated"; EVENTS_PER_DF <- 10

read_sheet <- function(sheet) {
  raw <- suppressMessages(read_excel(wbfile, sheet = sheet, col_names = FALSE, col_types = "text"))
  codes <- as.character(unlist(raw[1, ])); d <- as.data.frame(raw[-(1:3), ], stringsAsFactors = FALSE)
  names(d) <- ifelse(is.na(codes), paste0("V", seq_along(codes)), codes)
  d[!is.na(d[[1]]) & trimws(d[[1]]) != "", , drop = FALSE]
}
txt <- function(x) ifelse(is.na(x), "", trimws(x))
numv <- function(x) suppressWarnings(as.numeric(gsub(",", ".", txt(x))))

rep <- read_sheet("Reports"); pat <- read_sheet("Patients")
pat <- pat[txt(pat$patient_id) != "", ]
pat <- pat[txt(pat$same_patient_as) == "", ]              # duplicates of a patient in a more complete report
ri <- match(txt(pat$report_id), txt(rep$report_id))
D <- data.frame(patient_id = pat$patient_id, report_id = txt(pat$report_id), stringsAsFactors = FALSE)
D$own <- D$report_id == "OWN"
D$year <- ifelse(D$own, 2026, numv(rep$year[ri]))
D$consecutive <- txt(rep$consecutive[ri]); D$language <- txt(rep$language[ri]); D$design <- txt(rep$design[ri]); D$linked <- txt(rep$linked_duplicates[ri])
D$age <- numv(pat$age_years); D$days <- numv(pat$idx_dur_days); D$days_alt <- numv(pat$idx_dur_alt_days)
D$lower_bound <- txt(pat$idx_dur_lower_bound) == "Yes"; D$total_hist <- numv(pat$total_hist_days)
D$missed <- c(Yes = 1, No = 0)[txt(pat$missed_dx)]; D$defer <- c(Yes = 1, No = 0)[txt(pat$known_dx_deferred)]
D$thr <- ifelse(is.na(numv(pat$platelets)), NA, as.numeric(numv(pat$platelets) > 450))
D$torsion_at_op <- txt(pat$torsion_at_op); D$ws_basis <- txt(pat$ws_basis); D$aetiology <- txt(pat$aetiology)
D$gv <- txt(pat$cond_gv); D$goo <- txt(pat$cond_goo); D$dh <- txt(pat$cond_dh)
D$torsion_awaiting <- txt(pat$torsion_awaiting); D$deferred <- txt(pat$known_dx_deferred)
v <- txt(pat$viability); pr <- txt(pat$procedure)
removal <- pr %in% c("Total splenectomy", "Partial splenectomy +/- splenopexy")
D$y <- ifelse(v == "Non-viable", 1, ifelse(v == "Viable", 0, ifelse(v == "Partially non-viable" & removal, 1, NA)))
D$y_sa3 <- ifelse(v == "Partially non-viable" & removal, 0, D$y)
D$nr_removed <- v == "NR" & removal
D$period2015 <- as.numeric(D$year >= 2015); D$l2 <- ifelse(!is.na(D$days) & D$days > 0, log2(D$days), NA)

lines <- character(); P <- function(...) lines <<- c(lines, sprintf(...))
res <- data.frame(analysis = character(), n = integer(), events = integer(), clusters = integer(), OR = numeric(), lo = numeric(), hi = numeric(), note = character(), stringsAsFactors = FALSE)
add <- function(a, n = NA, e = NA, k = NA, OR = NA, lo = NA, hi = NA, note = "") res[nrow(res) + 1, ] <<- list(a, n, e, k, OR, lo, hi, note)

fit_or <- function(label, d, y = "y", x = c("l2", "age", "period2015"), term = x[1]) {
  d <- d[stats::complete.cases(d[, c(y, x)]), ]
  if (nrow(d) < 5 || length(unique(d[[y]])) < 2) { add(label, nrow(d), sum(d[[y]] == 1), length(unique(d$report_id)), note = "not estimable (too few patients or one outcome class)"); return(invisible(NULL)) }
  m <- tryCatch(glm(reformulate(x, y), data = d, family = binomial, control = glm.control(epsilon=1e-12, maxit=200)), error = function(e) NULL, warning = function(w) NULL)
  if (is.null(m) || !m$converged) { add(label, nrow(d), sum(d[[y]]), length(unique(d$report_id)), note = "failed: no convergence or separation"); return(invisible(NULL)) }
  vc <- tryCatch(vcovCL(m, cluster = d$report_id, type = "HC1", cadjust = TRUE), error = function(e) NULL)
  if (is.null(vc) || any(!is.finite(diag(vc)))) { add(label, nrow(d), sum(d[[y]]), length(unique(d$report_id)), note = "failed: robust variance"); return(invisible(NULL)) }
  b <- coef(m)[term]; se <- sqrt(diag(vc))[term]
  if (label == "Primary") write.csv(data.frame(beta=b, se=se, OR=exp(b), lo=exp(b-1.96*se), hi=exp(b+1.96*se)), file.path(outdir,"primary_precision.csv"), row.names=FALSE)
  add(label, nrow(d), sum(d[[y]]), length(unique(d$report_id)), round(exp(b), 3), round(exp(b - 1.96 * se), 3), round(exp(b + 1.96 * se), 3))
  invisible(list(m = m, vc = vc, d = d))
}
# Explicit HC1 and cadjust=TRUE match statsmodels use_correction=True.
# glm default is HC0, not HC1; correction = G/(G-1) * (N-1)/(N-K).

P("Patients after dropping duplicates: %d in %d reports; own series %d", nrow(D), length(unique(D$report_id)), sum(D$own))
if (any(D$year < 2000, na.rm = TRUE)) P("WARNING: %d patients in reports dated before 2000", sum(D$year < 2000, na.rm = TRUE))
P("Outcome: non-viable %d, viable %d, missing %d (splenectomy with viability not reported: %d)", sum(D$y == 1, na.rm = TRUE), sum(D$y == 0, na.rm = TRUE), sum(is.na(D$y)), sum(D$nr_removed))
prim <- fit_or("Primary", D)
if (!is.null(prim)) {
  ev <- sum(prim$d$y)
  if (ev / 4 >= EVENTS_PER_DF) {
    kn <- quantile(prim$d$l2, c(.1, .5, .9)); if(length(unique(kn)) < 3) stop("Spline knots coincide; review synthetic/input distribution before inference"); pos <- function(z) pmax(z, 0)^3
    sp <- (pos(prim$d$l2 - kn[1]) - pos(prim$d$l2 - kn[2]) * (kn[3] - kn[1]) / (kn[3] - kn[2]) + pos(prim$d$l2 - kn[3]) * (kn[2] - kn[1]) / (kn[3] - kn[2])) / (kn[3] - kn[1])^2
    d2 <- cbind(prim$d, sp = sp); m2 <- glm(y ~ l2 + age + period2015 + sp, data = d2, family = binomial, control = glm.control(epsilon=1e-12, maxit=200))
    write.csv(data.frame(p=coeftest(m2, vcovCL(m2, cluster=d2$report_id, type="HC1", cadjust=TRUE), df=Inf)["sp",4]), file.path(outdir,"spline_precision.csv"), row.names=FALSE)
    P("Spline: Wald p for the nonlinear term = %.3f", coeftest(m2, vcovCL(m2, cluster = d2$report_id, type = "HC1", cadjust = TRUE), df = Inf)["sp", 4])
  } else P("Spline not examined: %d events, fewer than %d per degree of freedom.", ev, EVENTS_PER_DF)
}
cc <- D[!is.na(D$y) & !is.na(D$days), ]
P("Duration reported for %d of %d patients with an outcome", nrow(cc), sum(!is.na(D$y)))
cc$cat <- cut(cc$days, c(-Inf, 2, 7, 30, Inf), labels = c("<=2 d", ">2-7 d", ">7-30 d", ">30 d"))
kk <- tapply(cc$y == 1, cc$cat, sum); nn <- table(cc$cat)
for (l in levels(cc$cat)) {
  ci <- if (nn[l] > 0) binom.test(kk[l], nn[l])$conf.int else c(NA, NA)
  P("  %-8s %3d %3d  (%.2f to %.2f)", l, nn[l], kk[l], ci[1], ci[2])
  add(paste("Category", l), nn[l], kk[l], length(unique(cc$report_id[cc$cat == l])), lo = round(ci[1], 3), hi = round(ci[2], 3), note = "proportion")
}
kk[is.na(kk)] <- 0
tr <- tryCatch(prop.trend.test(kk[nn > 0], nn[nn > 0], score = (1:4)[nn > 0])$p.value, error = function(e) NA)   # Cochran-Armitage
P("  Trend p (scores 1-4) = %s", ifelse(is.na(tr), "NA", ifelse(tr < 0.001, "<0.001", sprintf("%.3f", tr))))
write.csv(data.frame(p=tr), file.path(outdir,"trend_precision.csv"), row.names=FALSE)
# bounding of missing durations
if (any(!is.na(D$days))) for (b in list(c("shortest", min(D$days[D$days > 0], na.rm = TRUE)), c("longest", max(D$days, na.rm = TRUE)))) {
  d <- D; d$days[is.na(d$days)] <- as.numeric(b[2]); d$l2 <- ifelse(d$days > 0, log2(d$days), NA)
  fit_or(paste("Missing durations set to the", b[1], "observed"), d)
}
for (side in c("shortest", "longest")) {
  z <- D[!is.na(D$y), ]; z$cat <- cut(z$days, c(-Inf,2,7,30,Inf), labels=1:4)
  z$cat <- as.integer(z$cat); z$cat[is.na(z$days)] <- if(side=="shortest") 1 else 4
  for (j in 1:4) { yy <- z$y[z$cat==j]; ci <- if(length(yy)) binom.test(sum(yy),length(yy))$conf.int else c(NA,NA)
    add(paste("Category bound",side,j),length(yy),sum(yy),lo=round(ci[1],3),hi=round(ci[2],3),note="proportion") }
}
# secondary exposures
d <- D; d$l2th <- ifelse(!is.na(d$total_hist) & d$total_hist > 0, log2(d$total_hist), NA)
fit_or("Secondary: log2 total history", d, x = c("l2th", "age", "period2015"))
fit_or("Secondary: missed diagnosis", D, x = c("missed", "age", "period2015"))
fit_or("Secondary: known diagnosis, surgery deferred", D, x = c("defer", "age", "period2015"))
fit_or("Secondary: thrombocytosis", D, x = c("thr", "age", "period2015"))
w_all <- D[D$deferred == "Yes", ]; w <- w_all[w_all$torsion_awaiting %in% c("Yes","No"), ]
P("Torsion while awaiting: unknown outcomes %d of %d deferred patients", nrow(w_all)-nrow(w), nrow(w_all))
if (nrow(w) > 0) { ci <- binom.test(sum(w$torsion_awaiting == "Yes"), nrow(w))$conf.int; P("Torsion while awaiting surgery: %d of %d (exact 95%% CI %.2f to %.2f)", sum(w$torsion_awaiting == "Yes"), nrow(w), ci[1], ci[2]) }
# subgroups
fit_or("Subgroup: gastric volvulus or outlet obstruction", D[D$gv == "Yes" | D$goo == "Yes", ])
fit_or("Subgroup: no gastric volvulus or outlet obstruction", D[D$gv != "Yes" & D$goo != "Yes", ])
fit_or("Subgroup: congenital", D[D$aetiology == "Congenital", ]); fit_or("Subgroup: acquired", D[D$aetiology == "Acquired", ])
fit_or("Subgroup: diaphragmatic anomaly", D[D$dh == "Yes", ]); fit_or("Subgroup: no diaphragmatic anomaly", D[D$dh != "Yes", ])
# sensitivity analyses
fit_or("SA1 without own series", D[!D$own, ])
fit_or("SA2 pedicle torsion confirmed at operation", D[D$torsion_at_op == "Yes", ])
fit_or("SA3 partial splenectomy for partial infarction as salvage", D, y = "y_sa3")
d <- D; alt <- !is.na(d$days_alt); d$days[alt] <- d$days_alt[alt]; d$l2 <- ifelse(!is.na(d$days) & d$days > 0, log2(d$days), NA)
fit_or("SA4 alternative coding of intermittent or worsening episodes", d)
if (!is.na(robfile) && file.exists(robfile)) {
  rob <- read.csv(robfile, stringsAsFactors = FALSE); ok <- rob$report_id[tolower(trimws(rob$adequate)) == "yes"]
  fit_or("SA5 reports judged adequate", D[D$report_id %in% ok, ])
} else add("SA5 reports judged adequate", note = "not run: no rob file (report_id, adequate)")
fit_or("SA6 without Chinese-language reports", D[D$language != "Chinese", ])
add("SA7 without reports before 2000", note = "not applicable (v1.5)")
if (requireNamespace("lme4", quietly = TRUE)) {
  d <- D[stats::complete.cases(D[, c("y", "l2", "age", "period2015")]), ]
  m <- tryCatch(lme4::glmer(y ~ l2 + age + period2015 + (1 | report_id), data = d, family = binomial), error = function(e) NULL)
  if (is.null(m)) add("SA8 mixed-effects model", nrow(d), note = "failed")
  else { s <- summary(m)$coefficients["l2", ]; add("SA8 mixed-effects model", nrow(d), sum(d$y), length(unique(d$report_id)), round(exp(s[1]), 3), round(exp(s[1] - 1.96 * s[2]), 3), round(exp(s[1] + 1.96 * s[2]), 3)) }
  if (!is.null(m)) {
    diag_note <- c(if(lme4::isSingular(m)) "singular fit: random-intercept variance at boundary" else NULL, unlist(m@optinfo$conv$lme4$messages))
    if(length(diag_note)) res$note[nrow(res)] <- paste(unique(diag_note),collapse="; ")
  }
} else add("SA8 mixed-effects model", note = "lme4 not installed")
fit_or("A(a) without torsion-only inclusions", D[D$ws_basis != SP_FLAG, ])
for (b in list(c("non-viable (assumption)", 1), c("viable", 0))) { d <- D; d$yb <- d$y; d$yb[d$nr_removed] <- as.numeric(b[2]); fit_or(paste("A(b) splenectomy with viability NR assigned", b[1]), d, y = "yb") }
fit_or("A(c) without lower-bound durations", D[!D$lower_bound, ])
yr <- tapply(D$year, D$report_id, function(z) z[1]); lk <- tapply(D$linked, D$report_id, function(z) z[1]); omit <- character()
for (r in names(lk)) for (o in trimws(strsplit(gsub(",", ";", lk[[r]]), ";")[[1]])) if (nzchar(o) && o %in% names(yr)) omit <- c(omit, r)
P("Reports omitted in analysis A(d): %s", ifelse(length(omit), paste(sort(unique(omit)), collapse = ", "), "none"))
fit_or("A(d) without the report that states an overlap", D[!D$report_id %in% omit, ])
sizes <- table(D$report_id)
D$report_group <- ifelse(D$design == "Case report", "single case reports", ifelse(sizes[D$report_id]>=3 & D$consecutive=="Yes", "consecutive series >=3", "other or consecutiveness NR"))
for(g in unique(D$report_group)) { z <- D[D$report_group==g & !is.na(D$y), ]; P("Non-viable by %s: %d of %d",g,sum(z$y),nrow(z)) }
write.csv(res, file.path(outdir, "results.csv"), row.names = FALSE, na = "")
writeLines(c(lines, "", capture.output(print(res, row.names = FALSE)), "", capture.output(sessionInfo())), file.path(outdir, "results.txt"))
cat(paste(lines, collapse = "\n"), "\n")
