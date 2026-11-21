# MARKING-PREREG: do sperm whale clans really mark their identity where they meet?

Pre-registration for whale-clan-marking-test, version 1, fixed 2026-11-21 before any data were
opened. Plan, code (`clan_marking.py`) and tests (`test_clan_marking.py`) are public before the job
computes anything (`gate.py` checks that the job's copies equal the public ones). Made with AI agents
working in MV2's name (MV2, Munim, Inc., mv2@munimtech.com); not yet checked by a human expert.
Licence of this repository: Apache-2.0.

## The claim

Hersh T. A. et al. (2022; senior author H. Whitehead; Figure 4 script by T. A. Hersh and
M. Cantor), "Evidence from sperm whale clans of symbolic marking in non-human cultures", PNAS
119(37):e2201692119, doi 10.1073/pnas.2201692119.

From 23,429 codas in 191 day-repertoires recorded across the Pacific (1978-2017) the authors find
seven vocal clans. Their central result: between clans, similarity in the usage of **identity**
codas (types frequent in one clan, rare in others) decreases as the clans' spatial overlap
increases, while similarity in **non-identity** codas does not. Their Figure 4 script gives
identity Mantel r = -0.499, P = 0.041 and non-identity r = -0.076, P = 0.411 (one-tailed, 10,000
permutations, 7 clans = 21 clan pairs). They read this as evidence that identity codas are symbolic
markers, made more distinct where clans meet. It was widely reported as evidence of symbolic
marking in a non-human culture.

## Why re-test it

1. **The contrast was never tested.** "Identity significant, non-identity not" is not a test of
   whether the two differ (Gelman & Stern 2006). Symbolic marking predicts the *difference*.
2. **Seven units.** The test has 21 pairs but only 7 exchangeable clans; one clan can carry it.
   With 7 clans the exact permutation distribution has 5,040 members and can be enumerated.
3. **Choices.** The overlap radius (1,000 km), the overlap summary (mean of the two directions)
   and the identity-coda rule are each one of several reasonable options.
4. **Sampling.** Overlap and identity-coda counts may both track sampling effort (the heavily
   sampled Galapagos holds all seven clans).
5. **A sharper, untested prediction.** If clans emphasise identity codas where they meet, a clan's
   own repertoires recorded near other clans should use a larger share of its identity codas than
   its repertoires recorded far from other clans. The paper's within-clan analysis (similarity vs
   distance, beta = -0.019, P = 0.267) did not test this.

No published statistical re-analysis of this result was found (searched 2026-11-21: PNAS letters,
Google Scholar-indexed comments, the eLife review of Leitao et al., arXiv). Leitao et al.
(eLife reviewed preprint 96362, arXiv 2307.05304) build on the result with a different measure
(rhythmic "vocal style") and report convergence of *non-identity* style with overlap; they do not
re-test the Hersh Mantel result.

## Data (downloaded at run time, never redistributed)

OSF project ae6pd (no licence attached; read inside the job only):
- `RawCodaInterClickIntervals/pacific_coda_data.csv`, 3,872,453 bytes, https://osf.io/download/9hwmj/
  (columns per the authors' README: clan_name, within_clan_correlation, coda_type, grpvar, loc,
  year, date, latitude, longitude, coda_num, nclicks, duration, ICI1-ICI30).
- `MainTextFigures_RScriptsAndData/HershEtAl2022_Figure4_Data.RData`, 3,571 bytes,
  https://osf.io/download/z879f/ (data frames IDmean and nonIDmean: Var1, Var2, acsim = between-clan
  similarity, geov = mean spatial overlap, per clan pair).
A size mismatch stops the job. SHA-256 of both files is recorded in the results.

## Source of the confirmatory tests (fixed rule)

1. Read the Figure 4 data (python `rdata` 1.0.0). If Pearson r of acsim vs geov over the clan
   pairs is within 0.01 of -0.499 (identity) AND of -0.076 (non-identity), the confirmatory tests
   use these matrices with Pearson. Else, if Spearman matches within 0.01, they use Spearman.
2. Otherwise, the CSV rebuild (below) is used if its Pearson (then Spearman) r values are within
   0.05 of both published values.
3. Otherwise the verdict is **REPRO_FAILED**; all statistics are still reported for the record.

**CSV rebuild.** Keep codas with an assigned clan, a coda type and a repertoire id; type key =
(nclicks, coda_type); keep repertoires (grpvar) with >= 25 such codas; a repertoire's clan is its
codas' modal clan; its position is the mean latitude and circular-mean longitude of its codas.
Clan usage = mean over the clan's repertoires of each repertoire's type proportions. A type is an
identity type of clan c if its usage in c is >= 0.01 and >= 5 x its usage in EVERY other clan
(critfact = 5, as in the paper's final tree). Between-clan similarity = Pearson correlation of the
two clans' usage over all identity types of all clans (identity) or over all other used types
(non-identity). Overlap O(a, b) = share of a's repertoires within R km (great circle) of at least
one of b's repertoires; mean = (O(a,b)+O(b,a))/2, min, max.

## Tests (all permutation tests permute clan labels of the overlap matrix; exact enumeration when
n! <= 40,320, else 19,999 random permutations plus the identity; p counts the identity)

- **T1 (reproduction, exact).** Mantel r and exact one-tailed (lower) p for identity and
  non-identity similarity vs overlap.
- **T2 (PRIMARY, the contrast).** D = r_id - r_non. Lower-tailed exact permutation p. This is a
  Mantel test of overlap against the difference of the standardised similarity matrices.
- **T3 (leave one clan out).** T1 identity test and T2 on each set of n-1 clans (720 exact
  permutations for 6 clans).
- **T4 (overlap definitions).** Identity Mantel test with the confirmatory similarity matrix and
  CSV overlap at R = 500, 1,000, 2,000 km x {mean, min, max} (9 variants). If clan names cannot be
  matched between sources, the CSV-rebuild similarity is used (recorded).
- **T5 (sampling effort).** r(overlap, log of the product of the two clans' repertoire counts);
  partial Mantel of identity similarity on overlap given that effort matrix; same with the log
  product of identity-type counts.
- **T6 (new: identity emphasis in sympatry).** Each repertoire's identity share = share of its
  codas that are identity types of its own clan (CSV rule). A repertoire is sympatric if any
  repertoire of another clan lies within 1,000 km. Units = clan x region (loc) cells: mean identity
  share; cell sympatric if >= half its repertoires are. Statistic = weighted mean over clans with
  both kinds of cells of mean(share | sympatric) - mean(share | allopatric), weight
  ns*na/(ns+na). Null: sympatry labels permuted among each clan's own cells (exact if <= 20,000
  arrangements, else 9,999 random + observed). Verdict: UNTESTABLE if < 3 eligible clans or
  < 100 arrangements; MARKING_IN_SYMPATRY if p_up <= 0.05; REVERSED if p_low <= 0.05; else
  NOT_DETECTED. An unblocked repertoire-level version is reported as exploratory only.

## Headline verdict (fixed)

- REPRO_FAILED: no source reproduces the published r values.
- MARKING_CONTRAST_HOLDS: T1 identity p <= 0.05 AND T2 p <= 0.05 AND at least ceil(0.7 n) of the n
  leave-one-out sets keep identity p <= 0.10.
- CONTRAST_FRAGILE: T1 and T2 p <= 0.05 but the leave-one-out condition fails.
- ID_TREND_WITHOUT_CONTRAST: T1 identity p <= 0.05, T2 p > 0.05.
- ID_TREND_NOT_SIGNIFICANT: T1 identity p > 0.05.

## Predictions and priors (graded by the job; Brier score over graded predictions)

- P1 (0.80): the Figure 4 data reproduce the published r values (source = authors_fig4).
- P2 (0.70): exact T1 identity p <= 0.05.
- P3 (0.65): T2 contrast p > 0.05 (the identity vs non-identity difference is not established).
- P4 (0.80): at least 2 leave-one-clan-out sets have identity p > 0.05.
- P5 (0.50): r(overlap, log repertoire-count product) >= 0.30.
- P6 (0.50): fewer than half of the valid T4 variants have identity p <= 0.05.
- P7 (0.65): T6 verdict is not MARKING_IN_SYMPATRY.

## What would be remarkable

Either outcome matters. If the contrast and the sympatry emphasis both hold, the first evidence of
symbolic marking in a non-human culture gains a calibrated, pre-registered confirmation and a
second, independent line of support. If the contrast is not established, the headline rests on a
difference that was never tested, on 7 clans.

## Limits fixed in advance

Seven clans give little power to any clan-level test; a non-significant contrast is not evidence of
no contrast. Overlap has no time component (as in the paper). Repertoire positions are day means
of varying precision. The identity-type rule of the CSV route approximates the IDcall method and
is validated only by how well it reproduces the published values. Nothing here asks how whales
perceive codas; only playback experiments can show that.
