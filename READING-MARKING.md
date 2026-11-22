# READING-MARKING: what the registered re-test found

whale-clan-marking-test, graded 2026-11-22 from job clan-marking-v1 (run 2026-11-22 19:25-19:32 UTC;
plan `MARKING-PREREG.md`, code and tests checked identical to the public copies before computing).
All numbers are from `results/marking_results.json` and `results/RESULTS-MARKING.md`. Made with AI
agents working in MV2's name; not yet checked by a human expert.

**Registered headline verdict: ID_TREND_WITHOUT_CONTRAST.**

## 1. The authors' numbers reproduce exactly

The authors' Figure 4 file gives identity Mantel r = -0.4986 and non-identity r = -0.0764
(published -0.499 and -0.076). Enumerating all 5,040 relabelings of the 7 clans gives exact
one-tailed p = 0.0409 for identity (published 0.041) and 0.4081 for non-identity (published 0.411).
The published analysis is computed as described. (Our own rebuild from the raw coda file, with an
approximate identity-coda rule, did not reproduce it: identity r -0.338, non-identity r -0.276.)

## 2. The contrast that symbolic marking predicts is not established

Symbolic marking predicts that identity codas respond to overlap **more** than non-identity codas
do. The paper showed one significant and one non-significant correlation but never tested their
difference. The registered primary test of the difference, D = r_id - r_non = -0.4223, has exact
p = 0.0911 (5,040 relabelings). The direction is the one the paper predicts; the difference is not
significant at the registered 0.05 level.

## 3. The identity trend itself is fragile

- **Leave one clan out (T3).** Dropping any one of the 7 clans, the identity test keeps p <= 0.10
  in 6 sets (the registered robustness bar was 5) but keeps p <= 0.05 in only 2 of 7. The contrast
  D is not significant in any of the 7 six-clan sets (smallest p_D 0.0625, dropping Regular).
- **Overlap definitions (T4).** With overlap rebuilt from the coda positions at 500, 1,000 and
  2,000 km (mean, minimum, maximum of the two directions), 2 of 9 variants give p <= 0.05
  (500 km mean 0.0101; 500 km max 0.0034); the 1,000 km mean gives r -0.338, p 0.0978. Because the
  Figure 4 file names the Palindrome clan "pal", these runs used our CSV-rebuild similarity, not
  the authors'. AMENDMENT-1 reruns them with the authors' similarity.
- **Sampling effort (T5)** was skipped for the same naming reason (prediction P5 ungraded); it is
  part of AMENDMENT-1.

## 4. A new, sharper test leans the authors' way, with a caveat

T6 asks a question the paper did not: inside each clan, do region cells where the clan meets
other clans use a larger share of that clan's identity codas than cells where it does not? Over the
4 clans with both kinds of cells, sympatric cells use more: weighted difference 0.117, p_up 0.0401
(9,999 random rearrangements of sympatry labels within clan). Registered verdict
MARKING_IN_SYMPATRY. Our prediction P7 (that this would not be found, prior 0.65) failed.

Caveat, found while grading and not anticipated in the plan: identity types are defined from each
clan's average usage, and most of each clan's repertoires come from sympatric regions (Short:
38 of 50). Allopatric repertoires may share fewer identity types simply because they are less like
the average they did not help define. The Short clan also carries about 60% of the statistic's
weight. AMENDMENT-1 tests this with leave-one-cell-out identity types and a typicality placebo.

## 5. Predictions

5 of 6 graded predictions came true (P5 ungraded); Brier 0.161. P1 (reproduction), P2 (identity
p <= 0.05), P3 (contrast p > 0.05), P4 (at least 2 leave-one-out sets lose p <= 0.05) and P6 (fewer
than half of overlap variants significant) came true; P7 failed.

## What this means

The headline numbers of Hersh et al. (2022) are real, but the step from them to "identity codas
are symbolic markers made more distinct where clans meet" rests on a difference the paper never
tested, which is not significant (p 0.091) on 7 clans, and on a trend that keeps p <= 0.05 in only
2 of 7 leave-one-clan-out sets. The new within-clan test points the same way as the paper
(p 0.040) and is the strongest support we found, pending the circularity check. With 7 clans,
none of this is evidence against marking; it says the public data cannot yet establish it.
