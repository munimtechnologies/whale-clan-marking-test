# whale-clan-marking-test

An open, pre-registered re-test of the "symbolic marking" result for Pacific sperm whale clans
(Hersh et al. 2022, PNAS 119:e2201692119). The paper reports that clans' identity codas get less
alike as clans share more ocean (Mantel r = -0.499, P = 0.041, 7 clans), while other codas do not
(r = -0.076, P = 0.411).

## Result (registered test graded 2026-11-22; post hoc amendment graded 2026-11-26)

**Registered verdict: ID_TREND_WITHOUT_CONTRAST.** **Amendment reading: EMPHASIS_LOST_UNDER_LOCO.**
See [READING-MARKING.md](READING-MARKING.md), [READING-A1.md](READING-A1.md),
[results/RESULTS-MARKING.md](results/RESULTS-MARKING.md) and
[results/a1/RESULTS-A1.md](results/a1/RESULTS-A1.md).

- The authors' Figure 4 values reproduce exactly (identity r -0.4986, exact p 0.0409 over all
  5,040 relabelings of the 7 clans), and the published test is exactly sized: it fires in 252 of
  5,040 relabeled worlds (0.0500).
- The identity trend survives a control for sampling effort (partial Mantel r -0.5742, exact
  p 0.0165) and holds at p <= 0.05 in 5 of 9 overlap definitions with the authors' similarity.
- The difference between identity and non-identity codas, which symbolic marking predicts and the
  paper never tested, is not significant: D = -0.422, exact p = 0.091. Dropping any one clan, the
  identity trend keeps p <= 0.05 in only 2 of 7 sets.
- A within-clan test first seemed to support marking (clans use more of their identity codas where
  they meet other clans, p 0.040). The post hoc amendment shows it was circular: with identity
  codas re-derived without the region being scored, p_up 0.1099; a placebo (overall typicality)
  fires the same test (p_up 0.0356).

In short: consistent with symbolic marking, but the public data cannot yet show that the effect is
specific to identity codas.

## What the study asks

1. Is the **difference** between identity and non-identity codas itself significant? (primary)
2. Does the result survive dropping any one of the seven clans, other overlap radii and summaries,
   and a control for sampling effort? (exact permutation tests: 5,040 relabelings of 7 clans)
3. Do clans use **more** of their own identity codas in regions where they meet other clans than
   where they do not? This is a sharper, repertoire-level prediction of symbolic marking.
4. Do the authors' own Figure 4 values reproduce the published statistics?

The plan, tests, decision rules and priors are in [MARKING-PREREG.md](MARKING-PREREG.md), fixed
before the data were opened; the post hoc checks are in [AMENDMENT-1.md](AMENDMENT-1.md), fixed
before they ran. `clan_marking.py` and `marking_a1.py` download the authors' public OSF files at run
time (osf.io/ae6pd; no licence is attached, so the files are read in the job and not redistributed;
only derived statistics are published).

```
python -m unittest -v test_clan_marking test_marking_a1
python clan_marking.py --data-dir data --out-dir out
python marking_a1.py --data-dir data --out-dir out
```

Requires Python 3.11+, numpy, pandas and rdata 1.0.0 (for the authors' Figure 4 file).

Made with AI agents working in MV2's name; not yet checked by a human expert.
MV2, Munim, Inc., mv2@munimtech.com. Licence: Apache-2.0.
