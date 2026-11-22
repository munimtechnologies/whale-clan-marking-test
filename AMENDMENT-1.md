# AMENDMENT-1 (post hoc, exploratory): is the sympatry emphasis real, or circular?

whale-clan-marking-test, amendment 1, fixed 2026-11-22 **after** the registered results
(`results/RESULTS-MARKING.md`, job clan-marking-v1) were seen. Nothing here changes the registered
verdict (ID_TREND_WITHOUT_CONTRAST) or the registered grading of T6 (MARKING_IN_SYMPATRY,
p_up 0.0401). Everything below is exploratory and is labelled so wherever it is reported.
Code: `marking_a1.py` (imports the registered `clan_marking.py` unchanged; the job checks its md5),
tests `test_marking_a1.py`. Made with AI agents working in MV2's name (MV2, Munim, Inc.,
mv2@munimtech.com); not yet checked by a human expert. Licence: Apache-2.0.

## Why

1. **T6 may be circular.** A clan's identity types are defined from its mean coda usage over all
   its repertoires, and most repertoires of every eligible clan were recorded in sympatry (for
   the Short clan, 38 of 50). Any geographic drift inside a clan makes the few allopatric
   repertoires look less like the clan average, so they share fewer of the clan's identity types
   even with no marking at all. The registered T6 cannot tell these apart.
2. **T6 rests mostly on one clan.** With the registered weights, Short carries about 60% of the
   statistic (weight 4.28 of 7.17); Four-plus contributes through a single allopatric repertoire
   (Palmyra).
3. **Two registered steps did not run as intended.** The authors' Figure 4 file calls the
   Palindrome clan "pal", which the registered name rule did not map, so T5 (sampling effort) was
   skipped and T4 used the CSV-rebuild similarity instead of the authors' similarity.

## Checks

- **A1 (leave-one-cell-out identity types).** For each clan x region cell, the clan's usage is
  recomputed without that cell's repertoires (other clans unchanged), identity types are
  re-derived with the registered rule (usage >= 0.01 and >= 5 x every other clan), and the cell
  is scored on those types. Same statistic, weights, null (sympatry labels permuted within clan;
  9,999 random arrangements plus the observed one, seed 7) and verdict rule as T6. Cells whose
  clan has no repertoire outside the cell are dropped.
- **A2 (placebo: typicality).** Each cell's typicality = Pearson r between its mean coda-type
  profile and its clan's leave-one-cell-out usage over all types. Same test. If sympatric cells
  are simply more typical, an identity-share difference cannot be read as marking.
- **A3.** A1 with each eligible clan dropped in turn.
- **A4.** T4 (9 overlap definitions) and T5 (sampling effort: r of overlap with the log product
  of repertoire counts; partial Mantel of identity similarity on overlap given effort; same with
  identity-type counts) rerun with the authors' Figure 4 matrices after mapping "pal" to
  "palindrome". The job stops if the identity r no longer reproduces -0.499 within 0.01.
- **A5 (exact size).** Over all 5,040 relabelings of the 7 clans (worlds with no link between
  overlap and coda similarity), the share in which the published identity Mantel test gives
  p <= 0.05, and the share in which the published declaration "identity p <= 0.05 and
  non-identity p > 0.05" holds. Because the relabelings form a group, each world's exact p is its
  rank among the same 5,040 values.

## Reading rule (fixed now, before the amendment runs)

- EMPHASIS_LOST_UNDER_LOCO: A1 p_up > 0.05.
- EMPHASIS_NOT_SEPARABLE_FROM_TYPICALITY: A1 p_up <= 0.05 and A2 p_up <= 0.05.
- EMPHASIS_SURVIVES_LOCO: A1 p_up <= 0.05 and A2 p_up > 0.05.
- UNTESTABLE: A1 has no eligible clan.

## Predictions (priors; graded by the job, Brier score)

- Q1 (0.55): A1 p_up > 0.05.
- Q2 (0.50): A2 p_up <= 0.05.
- Q3 (0.60): A1 without the Short clan has p_up > 0.05.
- Q4 (0.50): r(overlap, log repertoire-count product) >= 0.30 (registered P5, now computable).
- Q5 (0.60): partial Mantel of identity similarity on overlap given effort has p > 0.05.

## Limits

Post hoc: the choice of these checks was informed by the registered results. Leave-one-cell-out
removes one source of circularity but not geographic drift itself; typicality is a crude
placebo. Seven clans and four eligible clans give little power either way.
