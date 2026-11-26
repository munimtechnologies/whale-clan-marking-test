# RESULTS-A1

whale-clan-marking-test AMENDMENT-1 (post hoc, exploratory), written by marking_a1.py. Made with AI agents working in MV2's name; not yet checked by a human expert.

**Reading of A1 and A2: EMPHASIS_LOST_UNDER_LOCO**

| check | statistic | p_up | p_low | eligible clans | verdict |
|---|---|---|---|---|---|
| A1 identity share, leave-one-cell-out types | 0.0559 | 0.1099 | 0.8902 | 4 | NOT_DETECTED |
| A2 placebo: typicality | 0.1329 | 0.0356 | 0.9645 | 4 | MARKING_IN_SYMPATRY |

## A3 A1 with one clan dropped

| dropped | eligible | statistic | p_up | verdict |
|---|---|---|---|---|
| fourplus | 3 | 0.0365 | 0.1863 | NOT_DETECTED |
| palindrome | 3 | 0.0663 | 0.0807 | NOT_DETECTED |
| rapidincreasing | 3 | 0.0720 | 0.0803 | NOT_DETECTED |
| short | 3 | 0.0423 | 0.3185 | NOT_DETECTED |

## A4 T4 and T5 with the authors' similarity (clan names mapped)

| overlap variant | r_id | p |
|---|---|---|
| 500_mean | -0.6588 | 0.0062 |
| 500_min | -0.4831 | 0.0187 |
| 500_max | -0.5676 | 0.0188 |
| 1000_mean | -0.4985 | 0.0413 |
| 1000_min | -0.3617 | 0.0750 |
| 1000_max | -0.5130 | 0.0431 |
| 2000_mean | -0.4089 | 0.0817 |
| 2000_min | -0.3093 | 0.1264 |
| 2000_max | -0.4616 | 0.0718 |

Significant variants: 5 of 9 valid. r(authors' overlap, CSV 1000 km mean overlap) = 1.0000.

T5: r(overlap, log repertoire-count product) 0.1066; r(identity similarity, effort) 0.3464; partial Mantel identity given effort r -0.5742, p 0.0165; r(overlap, log identity-type product) 0.1051; partial given identity-type counts r -0.4908, p 0.0484.

## A5 exact size over all relabelings

Published identity Mantel test fires (p <= 0.05) in 252 of 5040 relabeled worlds (0.0500); the published declaration 'identity p <= 0.05 and non-identity p > 0.05' holds in 230 (0.0456). Observed p_id 0.0409 (matches registered T1: True), p_non 0.4081.

## Amendment predictions

| prediction | prior | came true |
|---|---|---|
| Q1 | 0.55 | True |
| Q2 | 0.50 | True |
| Q3 | 0.60 | True |
| Q4 | 0.50 | False |
| Q5 | 0.60 | False |

3 of 5 graded predictions true; Brier 0.245.

Notes: CSV: 24237 rows; 22829 typed codas of assigned clans in 191 repertoires with >= 25 typed codas
