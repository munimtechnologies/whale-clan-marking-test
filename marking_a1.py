# Copyright 2026 MV2, Munim, Inc. Licensed under the Apache License, Version 2.0 (Apache-2.0).
# Made with AI agents working in MV2's name.
"""whale-clan-marking-test AMENDMENT-1 (post hoc, exploratory; plan in AMENDMENT-1.md).

Written AFTER the registered results of clan_marking.py were seen. Four checks:
  A1  T6 with leave-one-cell-out identity types: a clan's identity types are recomputed without
      the clan-region cell being scored, so a cell cannot help define the types it is scored on.
  A2  placebo: typicality (Pearson r between the cell's coda-type profile and its clan's
      leave-one-cell-out profile), tested with the same sympatry statistic and null.
  A3  A1 with each eligible clan dropped in turn.
  A4  T4 and T5 rerun with the authors' Figure 4 matrices after mapping the clan name 'pal' to
      'palindrome' (in the registered run the names did not match, so T5 was skipped and T4 used
      the CSV-rebuild similarity).
  A5  exact size of the published Mantel test and of the published 'identity significant,
      non-identity not' declaration over all 5,040 relabelings of the 7 clans.
Imports the registered clan_marking.py unchanged. Only derived statistics are written out.
"""
import argparse
import json
import math
import os
import sys

import numpy as np

import clan_marking as cm

PRIORS_A1 = {"Q1": 0.55, "Q2": 0.50, "Q3": 0.60, "Q4": 0.50, "Q5": 0.60}


def loco_cells(counts, rep_clan, rep_loc, n_clans, sym):
    """One record per clan x region cell whose clan has repertoires outside the cell.
    share = mean over the cell's repertoires of the share of codas that are identity types of the
    own clan, the clan's usage computed WITHOUT the cell; typ = Pearson r of the cell's mean type
    profile with that leave-one-cell-out clan usage."""
    counts = np.asarray(counts, float)
    props = counts / counts.sum(axis=1, keepdims=True)
    rep_clan = np.asarray(rep_clan)
    rep_loc = np.asarray(list(rep_loc), dtype=object)
    sym = np.asarray(sym, bool)
    U = cm.usage_table(counts, rep_clan, n_clans)
    out = []
    for c, loc in sorted(set(zip(rep_clan.tolist(), rep_loc.tolist()))):
        in_cell = (rep_clan == c) & (rep_loc == loc)
        rest = (rep_clan == c) & ~in_cell
        if not rest.any():
            continue
        Ul = U.copy()
        Ul[c] = props[rest].mean(axis=0)
        idc = cm.id_types(Ul)[c]
        idx = np.where(in_cell)[0]
        shares = [float(counts[r, idc].sum() / counts[r].sum()) for r in idx]
        typ = cm.pearson(props[idx].mean(axis=0), Ul[c])
        fy = float(sym[idx].mean())
        out.append({"clan": int(c), "loc": str(loc), "n": int(len(idx)), "share": float(np.mean(shares)),
                    "typ": float(typ), "n_id": int(len(idc)), "sym_frac": fy, "sym": 1 if fy >= 0.5 else 0})
    return out


def exact_size(S_id, S_non, G, alpha=cm.ALPHA):
    """Every relabeling of G is a world with no link between overlap and similarity. Because the
    relabelings form a group, each world's exact permutation null is the same multiset of values,
    so each world's lower-tailed p is its rank in that multiset."""
    G = np.asarray(G, float)
    s1, s2 = cm.upper(S_id), cm.upper(S_non)
    plist, exact = cm.perm_list(G.shape[0])
    ups = [cm.upper(G[np.ix_(p, p)]) for p in plist]
    v1 = np.array([cm.pearson(s1, u) for u in ups])
    v2 = np.array([cm.pearson(s2, u) for u in ups])
    n = len(plist)
    p1 = np.searchsorted(np.sort(v1), v1 + cm.EPS, side="right") / float(n)
    p2 = np.searchsorted(np.sort(v2), v2 + cm.EPS, side="right") / float(n)
    hid = int((p1 <= alpha).sum())
    hdec = int(((p1 <= alpha) & (p2 > alpha)).sum())
    return {"worlds": n, "exact": exact, "hits_id": hid, "rate_id": hid / float(n),
            "hits_declaration": hdec, "rate_declaration": hdec / float(n),
            "p_obs_id": float(p1[0]), "p_obs_non": float(p2[0])}


def a1_reading(p_share, p_typ):
    """Reading rule fixed in AMENDMENT-1.md before the amendment ran."""
    if not (isinstance(p_share, float) and math.isfinite(p_share)):
        return "UNTESTABLE"
    if p_share > cm.ALPHA:
        return "EMPHASIS_LOST_UNDER_LOCO"
    if isinstance(p_typ, float) and math.isfinite(p_typ) and p_typ <= cm.ALPHA:
        return "EMPHASIS_NOT_SEPARABLE_FROM_TYPICALITY"
    return "EMPHASIS_SURVIVES_LOCO"


def run(data_dir, out_dir):
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(out_dir, exist_ok=True)
    notes = []
    res = {"study": "whale-clan-marking-test", "plan": "AMENDMENT-1.md (post hoc, exploratory)",
           "priors": PRIORS_A1, "notes": notes}
    csvp = cm.fetch(cm.CSV_URL, os.path.join(data_dir, "pacific_coda_data.csv"), cm.CSV_SIZE)
    rdap = cm.fetch(cm.RDA_URL, os.path.join(data_dir, "HershEtAl2022_Figure4_Data.RData"), cm.RDA_SIZE)
    res["inputs"] = {"csv_sha256": cm.sha256(csvp), "rdata_sha256": cm.sha256(rdap)}
    csv, info = cm.load_csv(csvp, notes)
    if csv is None:
        raise RuntimeError("CSV schema unresolved: %r" % (info,))
    cl = csv["clans"]
    n_c = len(cl)
    geo = np.isfinite(csv["lat"]) & np.isfinite(csv["lon"])
    if not geo.all():
        raise RuntimeError("repertoires without coordinates: %d" % int((~geo).sum()))
    Dg = cm.dist_matrix(csv["lat"], csv["lon"])
    sym = cm.sympatry_flags(Dg, csv["rep_clan"], cm.MAIN_RADIUS)

    # A1, A2, A3
    cells = loco_cells(csv["counts"], csv["rep_clan"], csv["loc"], n_c, sym)
    share_cells = [(cl[x["clan"]], x["share"], x["sym"]) for x in cells]
    typ_cells = [(cl[x["clan"]], x["typ"], x["sym"]) for x in cells]
    a1 = cm.sympatry_test(share_cells)
    a1["verdict"] = cm.sympatry_verdict(a1)
    a2 = cm.sympatry_test(typ_cells)
    a2["verdict"] = cm.sympatry_verdict(a2)
    a3 = []
    for drop in a1["eligible"]:
        sub = cm.sympatry_test([t for t in share_cells if t[0] != drop])
        a3.append({"dropped": drop, "n_eligible": sub["n_eligible"], "obs": sub["obs"],
                   "p_up": sub["p_up"], "verdict": cm.sympatry_verdict(sub)})
    res["A1"], res["A2"], res["A3"] = a1, a2, a3
    res["A1A2_reading"] = a1_reading(a1["p_up"], a2["p_up"])

    # A4, A5 on the authors' Figure 4 matrices
    cm.ALIASES["pal"] = "palindrome"
    objs = cm.read_fig4(rdap)
    cl_f, m_id = cm.pair_matrices(objs["IDmean"], ["acsim", "geov"])
    cl_f2, m_non = cm.pair_matrices(objs["nonIDmean"], ["acsim", "geov"])
    if cl_f != cl_f2 or sorted(cl_f) != sorted(cl):
        raise RuntimeError("clan names still differ: fig %r csv %r" % (cl_f, cl))
    S_id = cm.reorder(m_id["acsim"], cl_f, cl)
    S_non = cm.reorder(m_non["acsim"], cl_f, cl)
    G = cm.reorder(m_id["geov"], cl_f, cl)
    r_check = cm.pearson(cm.upper(S_id), cm.upper(G))
    if abs(r_check - cm.REPORTED["r_id"]) > cm.REPRO_TOL_FIG:
        raise RuntimeError("Figure 4 identity r %.4f does not reproduce" % r_check)
    U = cm.usage_table(csv["counts"], csv["rep_clan"], n_c)
    ids = cm.id_types(U)
    t4 = {}
    for rad in cm.RADII:
        for kind, M in cm.sym_kinds(cm.overlap_matrix(Dg, csv["rep_clan"], n_c, rad)).items():
            key = "%d_%s" % (int(rad), kind)
            if np.isnan(M).any():
                t4[key] = {"obs": float("nan"), "p": float("nan"), "valid": False}
                continue
            m = cm.mantel(S_id, M, True)
            m["valid"] = True
            t4[key] = m
    valid = [v for v in t4.values() if v["valid"]]
    G1000 = cm.sym_kinds(cm.overlap_matrix(Dg, csv["rep_clan"], n_c, cm.MAIN_RADIUS))["mean"]
    n_rep = np.array([int((csv["rep_clan"] == c).sum()) for c in range(n_c)], float)
    E = np.log(np.outer(n_rep, n_rep))
    nid = np.array([max(1, len(ids[c])) for c in range(n_c)], float)
    Eid = np.log(np.outer(nid, nid))
    res["A4"] = {"T4_variants": t4, "T4_n_valid": len(valid),
                 "T4_n_sig": sum(1 for v in valid if v["p"] <= cm.ALPHA),
                 "r_fig_geov_vs_csv_1000_mean": cm.pearson(cm.upper(G), cm.upper(G1000)),
                 "T5": {"r_overlap_effort": cm.pearson(cm.upper(G), cm.upper(E)),
                        "r_simid_effort": cm.pearson(cm.upper(S_id), cm.upper(E)),
                        "partial_effort": cm.partial_mantel(S_id, G, E, True),
                        "r_overlap_nid": cm.pearson(cm.upper(G), cm.upper(Eid)),
                        "partial_nid": cm.partial_mantel(S_id, G, Eid, True)}}
    a5 = exact_size(S_id, S_non, G)
    res["A5"] = a5
    t1_p = cm.mantel(S_id, G, True)["p"]
    res["A5"]["matches_registered_T1"] = bool(abs(a5["p_obs_id"] - t1_p) < 1e-9)

    t5 = res["A4"]["T5"]
    p_drop = [x["p_up"] for x in a3 if x["dropped"] == "short"]
    outcomes = {
        "Q1": bool(a1["p_up"] > cm.ALPHA),
        "Q2": bool(a2["p_up"] <= cm.ALPHA),
        "Q3": (bool(p_drop[0] > cm.ALPHA) if p_drop and math.isfinite(p_drop[0]) else None),
        "Q4": bool(t5["r_overlap_effort"] >= 0.30),
        "Q5": bool(t5["partial_effort"]["p"] > cm.ALPHA),
    }
    b, nb = cm.brier(PRIORS_A1, outcomes)
    res["predictions"] = {"outcomes": outcomes, "brier": b, "n_graded": nb,
                          "n_true": sum(1 for v in outcomes.values() if v)}
    write_outputs(res, cells, cl, out_dir)
    return res


def write_outputs(res, cells, cl, out_dir):
    def conv(o):
        if hasattr(o, "item"):
            return o.item()
        if hasattr(o, "tolist"):
            return o.tolist()
        return str(o)
    with open(os.path.join(out_dir, "a1_results.json"), "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=1, default=conv)
    with open(os.path.join(out_dir, "a1_cells.csv"), "w", encoding="utf-8") as fh:
        fh.write("clan,region,n_repertoires,loco_id_share,typicality,n_loco_id_types,share_sympatric,sympatric\n")
        for x in cells:
            fh.write("%s,%s,%d,%.4f,%.4f,%d,%.3f,%d\n" % (cl[x["clan"]], x["loc"], x["n"], x["share"],
                                                        x["typ"], x["n_id"], x["sym_frac"], x["sym"]))
    f = cm.fmt
    a1, a2, a4, a5 = res["A1"], res["A2"], res["A4"], res["A5"]
    L = ["# RESULTS-A1", "",
         "whale-clan-marking-test AMENDMENT-1 (post hoc, exploratory), written by marking_a1.py. "
         "Made with AI agents working in MV2's name; not yet checked by a human expert.", "",
         "**Reading of A1 and A2: %s**" % res["A1A2_reading"], "",
         "| check | statistic | p_up | p_low | eligible clans | verdict |", "|---|---|---|---|---|---|",
         "| A1 identity share, leave-one-cell-out types | %s | %s | %s | %d | %s |" % (
             f(a1["obs"]), f(a1["p_up"]), f(a1["p_low"]), a1["n_eligible"], a1["verdict"]),
         "| A2 placebo: typicality | %s | %s | %s | %d | %s |" % (
             f(a2["obs"]), f(a2["p_up"]), f(a2["p_low"]), a2["n_eligible"], a2["verdict"]), "",
         "## A3 A1 with one clan dropped", "", "| dropped | eligible | statistic | p_up | verdict |",
         "|---|---|---|---|---|"]
    for x in res["A3"]:
        L.append("| %s | %d | %s | %s | %s |" % (x["dropped"], x["n_eligible"], f(x["obs"]), f(x["p_up"]), x["verdict"]))
    L += ["", "## A4 T4 and T5 with the authors' similarity (clan names mapped)", "",
          "| overlap variant | r_id | p |", "|---|---|---|"]
    for k, v in a4["T4_variants"].items():
        L.append("| %s | %s | %s |" % (k, f(v["obs"]), f(v["p"])))
    t5 = a4["T5"]
    L += ["", "Significant variants: %d of %d valid. r(authors' overlap, CSV 1000 km mean overlap) = %s." % (
              a4["T4_n_sig"], a4["T4_n_valid"], f(a4["r_fig_geov_vs_csv_1000_mean"])), "",
          "T5: r(overlap, log repertoire-count product) %s; r(identity similarity, effort) %s; "
          "partial Mantel identity given effort r %s, p %s; r(overlap, log identity-type product) %s; "
          "partial given identity-type counts r %s, p %s." % (
              f(t5["r_overlap_effort"]), f(t5["r_simid_effort"]), f(t5["partial_effort"]["obs"]),
              f(t5["partial_effort"]["p"]), f(t5["r_overlap_nid"]), f(t5["partial_nid"]["obs"]),
              f(t5["partial_nid"]["p"])), "",
          "## A5 exact size over all relabelings", "",
          "Published identity Mantel test fires (p <= 0.05) in %d of %d relabeled worlds (%s); the published "
          "declaration 'identity p <= 0.05 and non-identity p > 0.05' holds in %d (%s). Observed p_id %s "
          "(matches registered T1: %s), p_non %s." % (
              a5["hits_id"], a5["worlds"], f(a5["rate_id"]), a5["hits_declaration"], f(a5["rate_declaration"]),
              f(a5["p_obs_id"]), a5["matches_registered_T1"], f(a5["p_obs_non"])), "",
          "## Amendment predictions", "", "| prediction | prior | came true |", "|---|---|---|"]
    pr = res["predictions"]
    for k in sorted(PRIORS_A1):
        L.append("| %s | %.2f | %s |" % (k, PRIORS_A1[k], f(pr["outcomes"].get(k))))
    L += ["", "%d of %d graded predictions true; Brier %s." % (pr["n_true"], pr["n_graded"], f(pr["brier"], 3))]
    if res["notes"]:
        L += ["", "Notes: " + "; ".join(res["notes"])]
    with open(os.path.join(out_dir, "RESULTS-A1.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", default="data")
    ap.add_argument("--out-dir", default="out")
    a = ap.parse_args(argv)
    res = run(a.data_dir, a.out_dir)
    print("A1/A2 reading:", res["A1A2_reading"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
