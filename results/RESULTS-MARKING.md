# RESULTS-MARKING

whale-clan-marking-test, written by clan_marking.py (plan: MARKING-PREREG.md). Made with AI agents working in MV2's name; not yet checked by a human expert.

**Headline verdict: ID_TREND_WITHOUT_CONTRAST**

Source of confirmatory tests: authors_fig4 (method pearson)

Figure 4 data reproduction: Pearson r_id -0.4986, r_non -0.0764 (ok True); Spearman r_id -0.5610, r_non 0.0325 (ok False); published r_id -0.499, r_non -0.076.
CSV rebuild: Pearson r_id -0.3380, r_non -0.2761; identity types per clan {'fourplus': 9, 'palindrome': 8, 'plusone': 5, 'rapidincreasing': 4, 'regular': 11, 'short': 5, 'slowincreasing': 3}.

| test | statistic | p | permutations |
|---|---|---|---|
| T1 identity codas, Mantel r | -0.4986 | 0.0409 | 5040 |
| T1 non-identity codas, Mantel r | -0.0764 | 0.4081 | 5040 |
| T2 PRIMARY contrast D = r_id - r_non | -0.4223 | 0.0911 | 5040 |

## T3 leave one clan out

| dropped | r_id | p_id | D | p_D |
|---|---|---|---|---|
| fourplus | -0.3787 | 0.1764 | -0.2771 | 0.2319 |
| pal | -0.4400 | 0.0819 | -0.4407 | 0.1194 |
| plusone | -0.4356 | 0.0889 | -0.3254 | 0.1986 |
| rapidincreasing | -0.4919 | 0.0486 | -0.3695 | 0.1611 |
| regular | -0.5412 | 0.0611 | -0.6088 | 0.0625 |
| short | -0.6991 | 0.0097 | -0.6012 | 0.1111 |
| slowincreasing | -0.4784 | 0.0722 | -0.2259 | 0.2222 |

Drops keeping p_id <= 0.10: 6 (needed 5); drops with p_id > 0.05: 5.

## T4 overlap definitions (CSV positions)

| radius_kind | r_id | p |
|---|---|---|
| 500_mean | -0.5633 | 0.0101 |
| 500_min | -0.3021 | 0.1042 |
| 500_max | -0.6322 | 0.0034 |
| 1000_mean | -0.3380 | 0.0978 |
| 1000_min | -0.1816 | 0.2502 |
| 1000_max | -0.4618 | 0.0629 |
| 2000_mean | -0.2642 | 0.1712 |
| 2000_min | -0.1573 | 0.2796 |
| 2000_max | -0.4117 | 0.0790 |

Significant variants: 2 of 9 valid.

## T6 repertoire-level sympatry test

Verdict MARKING_IN_SYMPATRY: statistic 0.1170 (identity-coda share, sympatric minus allopatric region cells), p_up 0.0401, p_low 0.9600, 4 eligible clans, 12888720 arrangements (exact False).
Unblocked repertoire-level reading (exploratory): statistic 0.0725, p_up 0.0418, p_low 0.9583.

## Registered predictions

| prediction | prior | came true |
|---|---|---|
| P1 | 0.80 | True |
| P2 | 0.70 | True |
| P3 | 0.65 | True |
| P4 | 0.80 | True |
| P5 | 0.50 | NA |
| P6 | 0.50 | True |
| P7 | 0.65 | False |

5 of 6 graded predictions true; Brier 0.161.

Notes: CSV: 24237 rows; 22829 typed codas of assigned clans in 191 repertoires with >= 25 typed codas; clan names differ between sources; T4/T5 use the CSV rebuild similarity
