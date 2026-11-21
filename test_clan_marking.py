# Copyright 2026 MV2, Munim, Inc. Licensed under the Apache License, Version 2.0 (Apache-2.0).
# Made with AI agents working in MV2's name.
"""Unit tests for clan_marking.py (numpy only; no data, no network)."""
import unittest

import numpy as np

import clan_marking as cm


def toy4():
    S = np.zeros((4, 4))
    S[np.triu_indices(4, 1)] = [1, 2, 3, 4, 5, 6]
    return S + S.T


class TestClanMarking(unittest.TestCase):
    def test_canon(self):
        self.assertEqual(cm.canon("Four-Plus"), "fourplus")
        self.assertEqual(cm.canon("FP"), "fourplus")
        self.assertEqual(cm.canon("Rapid Increasing"), "rapidincreasing")
        self.assertEqual(cm.canon("SI"), "slowincreasing")

    def test_pearson_and_ranks(self):
        self.assertAlmostEqual(cm.pearson([1, 2, 3], [2, 4, 6]), 1.0)
        self.assertAlmostEqual(cm.pearson([1, 2, 3], [3, 2, 1]), -1.0)
        self.assertEqual(list(cm.avg_rank([10, 20, 20, 30])), [1.0, 2.5, 2.5, 4.0])
        M = np.zeros((3, 3))
        M[np.triu_indices(3, 1)] = [3, 1, 2]
        R = cm.rank_matrix(M + M.T)
        self.assertEqual(R[0, 1], 3.0)
        self.assertEqual(R[1, 0], 3.0)
        self.assertEqual(R[0, 2], 1.0)

    def test_mantel_exact(self):
        S = toy4()
        up = cm.mantel(S, S, lower_tail=False)
        self.assertAlmostEqual(up["obs"], 1.0)
        self.assertEqual(up["n_perm"], 24)
        self.assertTrue(up["exact"])
        self.assertAlmostEqual(up["p"], 1 / 24)
        low = cm.mantel(S, -S, lower_tail=True)
        self.assertAlmostEqual(low["obs"], -1.0)
        self.assertAlmostEqual(low["p"], 1 / 24)

    def test_contrast_and_partial(self):
        S = toy4()
        d = cm.contrast_test(-S, S, S)
        self.assertAlmostEqual(d["obs"], -2.0)
        self.assertAlmostEqual(d["p"], 1 / 24)
        self.assertAlmostEqual(cm.partial_r([1, 2, 3, 5], [1, 2, 3, 5], [1, 0, 1, 0]), 1.0)

    def test_perm_list_sizes(self):
        p7, ex7 = cm.perm_list(7)
        self.assertEqual(len(p7), 5040)
        self.assertTrue(ex7)
        self.assertEqual(p7[0], list(range(7)))
        self.assertLessEqual(1.0 / len(p7), cm.ALPHA)
        p6, _ = cm.perm_list(6)
        self.assertLessEqual(1.0 / len(p6), cm.ALPHA)
        p9, ex9 = cm.perm_list(9)
        self.assertFalse(ex9)
        self.assertEqual(len(p9), 20000)
        self.assertEqual(p9[0], list(range(9)))

    def test_distance_overlap_sympatry(self):
        D2 = cm.dist_matrix([0, 0], [0, 1])
        self.assertAlmostEqual(D2[0, 1], 111.19, delta=0.1)
        D = cm.dist_matrix([0, 0, 0], [0, 20, 1])
        rc = [0, 0, 1]
        O = cm.overlap_matrix(D, rc, 2, 500.0)
        self.assertAlmostEqual(O[0, 1], 0.5)
        self.assertAlmostEqual(O[1, 0], 1.0)
        k = cm.sym_kinds(O)
        self.assertAlmostEqual(k["mean"][0, 1], 0.75)
        self.assertAlmostEqual(k["min"][0, 1], 0.5)
        self.assertAlmostEqual(k["max"][1, 0], 1.0)
        self.assertEqual(list(cm.sympatry_flags(D, rc, 500.0)), [True, False, True])

    def test_usage_ids_similarity(self):
        counts = np.array([[5, 0, 5], [4, 1, 5], [0, 10, 0]], float)
        U = cm.usage_table(counts, [0, 0, 1], 2)
        np.testing.assert_allclose(U, [[0.45, 0.05, 0.5], [0.0, 1.0, 0.0]])
        self.assertEqual([list(a) for a in cm.id_types(U)], [[0, 2], [1]])
        S = cm.similarity(np.array([[1, 2, 3], [2, 4, 6], [3, 2, 1]], float), [0, 1, 2])
        self.assertAlmostEqual(S[0, 1], 1.0)
        self.assertAlmostEqual(S[0, 2], -1.0)
        R = cm.reorder(np.array([[0, 1], [2, 3]]), ["a", "b"], ["b", "a"])
        self.assertEqual(R.tolist(), [[3, 2], [1, 0]])

    def test_sympatry_test_and_verdict(self):
        r = cm.sympatry_test([("A", 1.0, 1), ("A", 0.0, 0)])
        self.assertEqual(r["n_arrangements"], 2)
        self.assertAlmostEqual(r["obs"], 1.0)
        self.assertAlmostEqual(r["p_up"], 0.5)
        self.assertAlmostEqual(r["p_low"], 1.0)
        self.assertEqual(cm.sympatry_verdict(r), "UNTESTABLE")
        base = {"n_eligible": 3, "n_arrangements": 200}
        self.assertEqual(cm.sympatry_verdict(dict(base, p_up=0.01, p_low=0.99)), "MARKING_IN_SYMPATRY")
        self.assertEqual(cm.sympatry_verdict(dict(base, p_up=0.5, p_low=0.02)), "REVERSED")
        self.assertEqual(cm.sympatry_verdict(dict(base, p_up=0.5, p_low=0.5)), "NOT_DETECTED")
        none = cm.sympatry_test([("A", 1.0, 1), ("A", 0.5, 1)])
        self.assertEqual(none["n_eligible"], 0)

    def test_headline_and_brier(self):
        self.assertEqual(cm.loco_needed(7), 5)
        self.assertEqual(cm.headline(False, 0.01, 0.01, 7), "REPRO_FAILED")
        self.assertEqual(cm.headline(True, 0.01, 0.01, 6), "MARKING_CONTRAST_HOLDS")
        self.assertEqual(cm.headline(True, 0.01, 0.01, 4), "CONTRAST_FRAGILE")
        self.assertEqual(cm.headline(True, 0.04, 0.30, 3), "ID_TREND_WITHOUT_CONTRAST")
        self.assertEqual(cm.headline(True, 0.20, 0.01, 7), "ID_TREND_NOT_SIGNIFICANT")
        b, n = cm.brier({"P1": 0.8, "P2": 0.5}, {"P1": True, "P2": None})
        self.assertAlmostEqual(b, 0.04)
        self.assertEqual(n, 1)


if __name__ == "__main__":
    unittest.main()
