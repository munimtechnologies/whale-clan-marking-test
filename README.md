# whale-clan-marking-test

An open, pre-registered re-test of the "symbolic marking" result for Pacific sperm whale clans
(Hersh et al. 2022, PNAS 119:e2201692119). The paper reports that clans' identity codas get less
alike as clans share more ocean (Mantel r = -0.499, P = 0.041, 7 clans), while other codas do not
(r = -0.076, P = 0.411).

This study asks four things the paper did not:

1. Is the **difference** between identity and non-identity codas itself significant? (primary)
2. Does the result survive dropping any one of the seven clans, other overlap radii and summaries,
   and a control for sampling effort? (exact permutation tests: 5,040 relabelings of 7 clans)
3. Do clans use **more** of their own identity codas in regions where they meet other clans than
   where they do not? This is a sharper, repertoire-level prediction of symbolic marking.
4. Do the authors' own Figure 4 values reproduce the published statistics?

The plan, tests, decision rules and priors are in [MARKING-PREREG.md](MARKING-PREREG.md), fixed
before the data were opened. `clan_marking.py` downloads the authors' public OSF files at run time
(osf.io/ae6pd; no licence is attached, so the files are read in the job and not redistributed;
only derived statistics are published) and writes `RESULTS-MARKING.md`, `marking_results.json`,
`pairs.csv` and `cells.csv`.

```
python -m unittest -v test_clan_marking
python clan_marking.py --data-dir data --out-dir out
```

Requires Python 3.11+, numpy, pandas and (optional, for the authors' Figure 4 file) rdata 1.0.0.

Made with AI agents working in MV2's name; not yet checked by a human expert.
MV2, Munim, Inc., mv2@munimtech.com. Licence: Apache-2.0.
