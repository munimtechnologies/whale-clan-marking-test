# READING-A1: the post hoc amendment, graded

whale-clan-marking-test, amendment 1 (post hoc, exploratory), graded 2026-11-26 from job
clan-marking-a1-v1 (run 2026-11-26 06:05-06:46 UTC). Before computing, the job checked that
`AMENDMENT-1.md`, `marking_a1.py` and `test_marking_a1.py` were identical to the public copies and
that the registered `clan_marking.py` had its registered md5. All numbers are from
`results/a1/a1_results.json` and `results/a1/RESULTS-A1.md` (per-cell values in
`results/a1/a1_cells.csv`). Made with AI agents working in MV2's name; not yet checked by a human
expert. Nothing here changes the registered verdict in READING-MARKING.md
(ID_TREND_WITHOUT_CONTRAST).

**Amendment reading: EMPHASIS_LOST_UNDER_LOCO.**

## 1. The within-clan "emphasis where clans meet" was circular

The registered T6 found that clans use a larger share of their identity codas in regions where they
meet other clans (0.117, p_up 0.0401). Its identity codas were defined from each clan's average
usage over all its repertoires, most of which were recorded where clans meet.

- **A1, leave-one-cell-out identity types.** Re-deriving each clan's identity types without the
  region cell being scored, the same test gives 0.0559, p_up 0.1099 (4 eligible clans, 10,000
  arrangements): NOT_DETECTED. The statistic falls by more than half.
- **A2, typicality placebo.** Cells where a clan meets other clans are simply more typical of the
  clan's overall coda use: the same test on typicality (correlation of a cell's coda profile with
  its clan's leave-one-cell-out profile) gives 0.1329, p_up 0.0356. A shift that is not specific to
  identity codas fires the test.
- **A3.** Dropping any one clan, A1 stays NOT_DETECTED in all 4 sets (p_up 0.0803 to 0.3185).

So the strongest support for marking we had found (T6) is explained by how the identity codas were
defined (from averages dominated by repertoires recorded where clans meet), and sympatric cells
are more typical of their clan in general, not only in identity codas. Predictions Q1, Q2 and Q3 came true.

## 2. The between-clan identity trend is sturdier than the registered run showed

The registered T4 and T5 used our rebuilt similarity because the authors' file names the Palindrome
clan "pal". With the name mapped and the authors' own similarity matrices:

- **Overlap definitions (A4, T4).** 5 of 9 overlap definitions give p <= 0.05 (exact, 5,040
  relabelings): 500 km mean r -0.6588 (p 0.0062), min -0.4831 (0.0187), max -0.5676 (0.0188);
  1,000 km mean -0.4985 (0.0413) and max -0.5130 (0.0431); the other four have p 0.0718 to 0.1264.
  Our 1,000 km mean overlap correlates with the authors' at r = 1.0000.
- **Sampling effort (A4, T5).** Overlap barely tracks sampling effort (r 0.1066 with the log product
  of repertoire counts; Q4 failed), and the identity trend survives controlling for it: partial
  Mantel r -0.5742, exact p 0.0165 (Q5 failed); controlling for identity-type counts instead,
  r -0.4908, p 0.0484.

## 3. The published test is exactly sized

Over all 5,040 relabelings of the 7 clans (worlds with no link between overlap and coda
similarity), the published identity Mantel test gives p <= 0.05 in 252 (0.0500), and the published
declaration "identity p <= 0.05 and non-identity p > 0.05" holds in 230 (0.0456). The observed
identity p 0.0409 matches the registered T1. The published test is not a false-alarm machine; the
weakness is that 7 clans give little power and the contrast was never tested.

## 4. Predictions

3 of 5 amendment predictions came true (Q1, Q2, Q3; Q4 and Q5 failed); Brier 0.245.

## What this means

Taken with READING-MARKING.md: the authors' numbers reproduce exactly, their test is correctly
sized, and the identity trend holds up against sampling effort and in most overlap definitions near
the published one. What does not hold up is the evidence that the trend is **specific to identity
codas** (the identity minus non-identity difference has p 0.091 on 7 clans) and the within-clan
emphasis we found, which was circular. The public data are consistent with symbolic marking but
cannot yet distinguish it from a general divergence of sympatric clans. Ledger verdict: UNDECIDED.

Limits: post hoc and exploratory; 7 clans and 4 eligible clans; typicality is a crude placebo;
leave-one-cell-out removes one source of circularity but not geographic drift itself.
