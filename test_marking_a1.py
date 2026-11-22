# Copyright 2026 MV2, Munim, Inc. Licensed under the Apache License, Version 2.0 (Apache-2.0).
# Made with AI agents working in MV2's name.
"""Unit tests for marking_a1.py (numpy only; no data, no network)."""
import unittest

import numpy as np

import clan_marking as cm
import marking_a1 as a1


class TestMarkingA1(unittest.TestCase):
    def test_loco_cells_toy(self):
        # r0 clan0 region A, r1 clan0 region B, r2 clan1 region A
        counts = np.array([[10, 0, 0], [5, 5, 0], [0, 0, 10]], float)
        cells = a1.loco_cells(counts, [0, 0, 1], ["A", "B", "A"], 2, [True, False, True])
        self.assertEqual(len(cells), 2)  # clan 1 has no repertoire outside its only cell
        c0a, c0b = cells
        self.assertEqual((c0a["clan"], c0a["loc"], c0a["sym"]), (0, "A", 1))
        self.assertEqual((c0b["clan"], c0b["loc"], c0b["sym"]), (0, "B", 0))
        # without r0, clan 0 usage is [.5, .5, 0]: identity types {0, 1}; r0 share 10/10
        self.assertAlmostEqual(c0a["share"], 1.0)
        self.assertEqual(c0a["n_id"], 2)
        self.assertAlmostEqual(c0a["typ"], 0.5)
        # without r1, clan 0 usage is [1, 0, 0]: identity type {0}; r1 share 5/10
        self.assertAlmostEqual(c0b["share"], 0.5)
        self.assertEqual(c0b["n_id"], 1)

    def test_exact_size_matches_mantel(self):
        S = np.zeros((4, 4))
        S[np.triu_indices(4, 1)] = [1, 2, 3, 4, 5, 6]
        S = S + S.T
        G = np.zeros((4, 4))
        G[np.triu_indices(4, 1)] = [6, 1, 5, 2, 4, 3]
        G = G + G.T
        N = np.zeros((4, 4))
        N[np.triu_indices(4, 1)] = [2, 2, 1, 3, 1, 3]
        N = N + N.T
        r = a1.exact_size(S, N, G)
        self.assertEqual(r["worlds"], 24)
        self.assertAlmostEqual(r["p_obs_id"], cm.mantel(S, G, True)["p"])
        self.assertAlmostEqual(r["p_obs_non"], cm.mantel(N, G, True)["p"])
        # with 24 worlds only a strict minimum (p = 1/24) can reach p <= 0.05
        self.assertLessEqual(r["hits_id"], 1)
        self.assertLessEqual(r["hits_declaration"], r["hits_id"])
        self.assertAlmostEqual(r["rate_id"], r["hits_id"] / 24.0)
        # perfectly anti-aligned similarity: the identity world is the unique minimum (p = 1/24),
        # and there the 'non-identity' matrix (= overlap) is at its maximum, p_non = 1
        r2 = a1.exact_size(-S, S, S)
        self.assertAlmostEqual(r2["p_obs_id"], 1 / 24)
        self.assertAlmostEqual(r2["p_obs_non"], 1.0)
        self.assertEqual(r2["hits_id"], 1)
        self.assertEqual(r2["hits_declaration"], 1)

    def test_reading_rule(self):
        self.assertEqual(a1.a1_reading(float("nan"), 0.5), "UNTESTABLE")
        self.assertEqual(a1.a1_reading(0.20, 0.01), "EMPHASIS_LOST_UNDER_LOCO")
        self.assertEqual(a1.a1_reading(0.03, 0.01), "EMPHASIS_NOT_SEPARABLE_FROM_TYPICALITY")
        self.assertEqual(a1.a1_reading(0.03, 0.40), "EMPHASIS_SURVIVES_LOCO")
        self.assertEqual(a1.a1_reading(0.05, float("nan")), "EMPHASIS_SURVIVES_LOCO")

    def test_alias_mapping(self):
        old = dict(cm.ALIASES)
        try:
            cm.ALIASES["pal"] = "palindrome"
            self.assertEqual(cm.canon("Pal"), "palindrome")
        finally:
            cm.ALIASES.clear()
            cm.ALIASES.update(old)


if __name__ == "__main__":
    unittest.main()
