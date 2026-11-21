# Copyright 2026 MV2, Munim, Inc. Licensed under the Apache License, Version 2.0 (Apache-2.0).
# Made with AI agents working in MV2's name.
"""whale-clan-marking-test: a pre-registered re-test of the 'symbolic marking' result of
Hersh et al. 2022 (PNAS 119:e2201692119): between-clan similarity in IDENTITY coda usage falls as
clans' spatial overlap rises (Mantel r = -0.499, P = 0.041, 7 clans), NON-identity codas do not
(r = -0.076, P = 0.411). See MARKING-PREREG.md for the plan, tests, decision rules and priors.

The authors' OSF files (osf.io/ae6pd; no licence attached) are downloaded at run time, checked by
size, read in the container and never redistributed. Only derived statistics are written out.
numpy only at import; pandas and rdata are imported inside the loaders.
"""
import argparse
import hashlib
import itertools
import json
import math
import os
import sys
import time
import urllib.request

import numpy as np

CSV_URL = "https://osf.io/download/9hwmj/"      # RawCodaInterClickIntervals/pacific_coda_data.csv
CSV_SIZE = 3872453
RDA_URL = "https://osf.io/download/z879f/"      # MainTextFigures_RScriptsAndData/HershEtAl2022_Figure4_Data.RData
RDA_SIZE = 3571
REPORTED = {"r_id": -0.499, "p_id": 0.041, "r_non": -0.076, "p_non": 0.411}
REPRO_TOL_FIG = 0.01
REPRO_TOL_CSV = 0.05
CRITFACT = 5.0
MIN_USE = 0.01
MIN_CODAS = 25
RADII = [500.0, 1000.0, 2000.0]
MAIN_RADIUS = 1000.0
ALPHA = 0.05
EPS = 1e-12
PRIORS = {"P1": 0.80, "P2": 0.70, "P3": 0.65, "P4": 0.80, "P5": 0.50, "P6": 0.50, "P7": 0.65}
ALIASES = {"fp": "fourplus", "pali": "palindrome", "po": "plusone", "reg": "regular",
           "ri": "rapidincreasing", "sh": "short", "si": "slowincreasing"}


# ----------------------------------------------------------------- pure functions (numpy only)
def canon(name):
    s = "".join(ch for ch in str(name).lower() if ch.isalpha())
    return ALIASES.get(s, s)


def upper(m):
    m = np.asarray(m, float)
    return m[np.triu_indices(m.shape[0], 1)]


def pearson(x, y):
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    x = x - x.mean()
    y = y - y.mean()
    d = math.sqrt(float((x * x).sum()) * float((y * y).sum()))
    return float((x * y).sum() / d) if d > 0 else float("nan")


def avg_rank(x):
    x = np.asarray(x, float)
    order = np.argsort(x, kind="mergesort")
    sx = x[order]
    r = np.empty(len(x))
    i = 0
    while i < len(x):
        j = i
        while j + 1 < len(x) and sx[j + 1] == sx[i]:
            j += 1
        r[order[i:j + 1]] = (i + j) / 2.0 + 1.0
        i = j + 1
    return r


def rank_matrix(m):
    """Symmetric matrix whose off-diagonal entries are the average ranks of the upper triangle."""
    m = np.asarray(m, float)
    n = m.shape[0]
    out = np.zeros((n, n))
    iu = np.triu_indices(n, 1)
    out[iu] = avg_rank(m[iu])
    return out + out.T


def partial_r(s, g, c):
    rsg, rsc, rgc = pearson(s, g), pearson(s, c), pearson(g, c)
    d = math.sqrt(max(0.0, (1 - rsc ** 2) * (1 - rgc ** 2)))
    return (rsg - rsc * rgc) / d if d > 0 else float("nan")


def perm_list(n, max_exact=40320, n_random=19999, seed=1):
    """All label permutations (identity first) when n! <= max_exact, else identity + random ones."""
    if math.factorial(n) <= max_exact:
        return [list(p) for p in itertools.permutations(range(n))], True
    rng = np.random.default_rng(seed)
    return [list(range(n))] + [list(rng.permutation(n)) for _ in range(n_random)], False


def perm_test(G, stat, lower_tail=True):
    """Permute the clan labels of G (rows and columns together); stat(Gp) -> float.
    p = share of permutations, identity included, at least as extreme as the observed value."""
    G = np.asarray(G, float)
    plist, exact = perm_list(G.shape[0])
    vals = np.array([stat(G[np.ix_(p, p)]) for p in plist])
    obs = float(vals[0])
    if not math.isfinite(obs):
        return {"obs": obs, "p": float("nan"), "n_perm": len(plist), "exact": exact}
    if lower_tail:
        p = float((vals <= obs + EPS).mean())
    else:
        p = float((vals >= obs - EPS).mean())
    return {"obs": obs, "p": p, "n_perm": len(plist), "exact": exact}


def mantel(S, G, lower_tail=True):
    s = upper(S)
    return perm_test(G, lambda Gp: pearson(s, upper(Gp)), lower_tail)


def contrast_test(S_id, S_non, G):
    """D = r(S_id, G) - r(S_non, G); lower tail (identity more negative than non-identity)."""
    a, b = upper(S_id), upper(S_non)
    return perm_test(G, lambda Gp: pearson(a, upper(Gp)) - pearson(b, upper(Gp)), True)


def partial_mantel(S, G, C, lower_tail=True):
    s, c = upper(S), upper(C)
    return perm_test(G, lambda Gp: partial_r(s, upper(Gp), c), lower_tail)


def dist_matrix(lat, lon):
    la = np.radians(np.asarray(lat, float))
    lo = np.radians(np.asarray(lon, float))
    dla = la[:, None] - la[None, :]
    dlo = lo[:, None] - lo[None, :]
    a = np.sin(dla / 2) ** 2 + np.cos(la)[:, None] * np.cos(la)[None, :] * np.sin(dlo / 2) ** 2
    return 2 * 6371.0 * np.arcsin(np.sqrt(np.clip(a, 0, 1)))


def overlap_matrix(D, rep_clan, n_clans, radius):
    """O[a, b] = share of clan a's repertoires within `radius` km of at least one of clan b's."""
    rep_clan = np.asarray(rep_clan)
    O = np.full((n_clans, n_clans), np.nan)
    for a in range(n_clans):
        ia = np.where(rep_clan == a)[0]
        for b in range(n_clans):
            if a == b:
                O[a, b] = 1.0
                continue
            ib = np.where(rep_clan == b)[0]
            if len(ia) and len(ib):
                O[a, b] = float((D[np.ix_(ia, ib)].min(axis=1) <= radius).mean())
    return O


def sym_kinds(O):
    return {"mean": (O + O.T) / 2, "min": np.minimum(O, O.T), "max": np.maximum(O, O.T)}


def sympatry_flags(D, rep_clan, radius):
    rep_clan = np.asarray(rep_clan)
    return np.array([bool((D[i, rep_clan != rep_clan[i]] <= radius).any()) for i in range(len(rep_clan))])


def usage_table(counts, rep_clan, n_clans):
    counts = np.asarray(counts, float)
    props = counts / counts.sum(axis=1, keepdims=True)
    rep_clan = np.asarray(rep_clan)
    return np.array([props[rep_clan == c].mean(axis=0) for c in range(n_clans)])


def id_types(U, critfact=CRITFACT, min_use=MIN_USE):
    """Identity types of clan c: mean usage >= min_use and >= critfact x its usage in EVERY other clan."""
    U = np.asarray(U, float)
    out = []
    for c in range(U.shape[0]):
        other = np.delete(U, c, axis=0).max(axis=0)
        out.append(np.where((U[c] >= min_use) & (U[c] >= critfact * other))[0])
    return out


def similarity(U, cols):
    n = U.shape[0]
    S = np.eye(n)
    for a in range(n):
        for b in range(a + 1, n):
            S[a, b] = S[b, a] = pearson(U[a, cols], U[b, cols])
    return S


def sympatry_test(cells, n_random=9999, seed=7, max_exact=20000):
    """cells: (clan, share, sym 0/1). Statistic: weighted mean over clans with both kinds of
    cells of mean(share | sym) - mean(share | allo), weight ns*na/(ns+na). Null: sym labels
    permuted among each clan's own cells (exact when the arrangements are few)."""
    by = {}
    for c, s, y in cells:
        by.setdefault(c, []).append((float(s), int(y)))
    elig = [c for c in sorted(by) if 0 < sum(y for _, y in by[c]) < len(by[c])]
    out = {"n_eligible": len(elig), "eligible": elig, "n_arrangements": 0, "obs": float("nan"),
           "p_up": float("nan"), "p_low": float("nan"), "exact": None}
    if not elig:
        return out
    shares = [np.array([s for s, _ in by[c]]) for c in elig]
    labels = [np.array([y for _, y in by[c]]) for c in elig]
    n_arr = 1
    for lab in labels:
        n_arr *= math.comb(len(lab), int(lab.sum()))

    def stat(lbls):
        num = den = 0.0
        for s, lab in zip(shares, lbls):
            ns = float(lab.sum())
            na = float(len(lab) - ns)
            w = ns * na / (ns + na)
            num += w * (s[lab == 1].mean() - s[lab == 0].mean())
            den += w
        return num / den

    obs = stat(labels)
    if n_arr <= max_exact:
        options = []
        for lab in labels:
            n, k = len(lab), int(lab.sum())
            opts = []
            for comb in itertools.combinations(range(n), k):
                v = np.zeros(n, int)
                v[list(comb)] = 1
                opts.append(v)
            options.append(opts)
        vals = np.array([stat(list(combo)) for combo in itertools.product(*options)])
        exact = True
    else:
        rng = np.random.default_rng(seed)
        vals = np.array([obs] + [stat([rng.permutation(lab) for lab in labels]) for _ in range(n_random)])
        exact = False
    out.update({"n_arrangements": n_arr, "obs": float(obs), "exact": exact, "n_null": len(vals),
                "p_up": float((vals >= obs - EPS).mean()), "p_low": float((vals <= obs + EPS).mean())})
    return out


def sympatry_verdict(res, min_clans=3, min_arr=100):
    if res["n_eligible"] < min_clans or res["n_arrangements"] < min_arr:
        return "UNTESTABLE"
    if res["p_up"] <= ALPHA:
        return "MARKING_IN_SYMPATRY"
    if res["p_low"] <= ALPHA:
        return "REVERSED"
    return "NOT_DETECTED"


def loco_needed(n_clans):
    return int(math.ceil(0.7 * n_clans - 1e-9))


def headline(repro_ok, p_id, p_d, loco_keep, n_clans=7):
    if not repro_ok:
        return "REPRO_FAILED"
    if p_id <= ALPHA and p_d <= ALPHA:
        return "MARKING_CONTRAST_HOLDS" if loco_keep >= loco_needed(n_clans) else "CONTRAST_FRAGILE"
    if p_id <= ALPHA:
        return "ID_TREND_WITHOUT_CONTRAST"
    return "ID_TREND_NOT_SIGNIFICANT"


def brier(priors, outcomes):
    keys = [k for k in sorted(priors) if outcomes.get(k) is not None]
    if not keys:
        return float("nan"), 0
    return float(np.mean([(priors[k] - float(bool(outcomes[k]))) ** 2 for k in keys])), len(keys)


# ----------------------------------------------------------------- data loading (pandas/rdata)
def fetch(url, path, size):
    if os.path.exists(path) and os.path.getsize(path) == size:
        return path
    last = "no attempt"
    for _ in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (research replication)"})
            with urllib.request.urlopen(req, timeout=180) as r:
                blob = r.read()
            if len(blob) == size:
                with open(path + ".part", "wb") as fh:
                    fh.write(blob)
                os.replace(path + ".part", path)
                return path
            last = "size %d, expected %d" % (len(blob), size)
        except Exception as exc:  # noqa: BLE001
            last = repr(exc)
        time.sleep(20)
    raise RuntimeError("download failed for %s: %s" % (url, last))


def sha256(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def read_fig4(path):
    import rdata  # noqa: PLC0415
    if hasattr(rdata, "read_rda"):
        objs = rdata.read_rda(path)
    else:
        objs = rdata.conversion.convert(rdata.parser.parse_file(path))
    return objs


def pair_matrices(df, value_cols):
    cols = {str(c).strip().lower(): c for c in df.columns}
    v1 = [canon(x) for x in df[cols["var1"]].astype(str)]
    v2 = [canon(x) for x in df[cols["var2"]].astype(str)]
    clans = sorted(set(v1) | set(v2))
    idx = {c: i for i, c in enumerate(clans)}
    n = len(clans)
    out = {}
    for vc in value_cols:
        vals = [float(x) for x in df[cols[vc]]]
        acc = {}
        for a, b, v in zip(v1, v2, vals):
            if a == b:
                continue
            key = tuple(sorted((idx[a], idx[b])))
            acc.setdefault(key, []).append(v)
        M = np.full((n, n), np.nan)
        np.fill_diagonal(M, 1.0)
        for (i, j), vs in acc.items():
            M[i, j] = M[j, i] = float(np.mean(vs))
        out[vc] = M
    return clans, out


def circ_mean_lon(lon):
    r = np.radians(np.asarray(lon, float))
    return float(np.degrees(math.atan2(np.sin(r).mean(), np.cos(r).mean())))


def load_csv(path, notes):
    import pandas as pd  # noqa: PLC0415
    df = pd.read_csv(path, low_memory=False)
    cols = {str(c).strip().lower(): c for c in df.columns}
    need = ["clan_name", "coda_type", "grpvar", "loc", "latitude", "longitude", "nclicks"]
    missing = [k for k in need if k not in cols]
    if missing:
        return None, {"columns": [str(c) for c in df.columns], "missing": missing, "rows": int(len(df))}
    d = pd.DataFrame({k: df[cols[k]] for k in need})
    d["clan"] = [canon(x) if isinstance(x, str) and x.strip() and x.strip().upper() not in ("#N/A", "NA", "N/A")
                 else None for x in d["clan_name"]]
    for k in ("coda_type", "nclicks", "latitude", "longitude"):
        d[k] = pd.to_numeric(d[k], errors="coerce")
    n_rows = len(d)
    t = d[d["clan"].notna() & d["coda_type"].notna() & d["nclicks"].notna() & d["grpvar"].notna()].copy()
    t["key"] = ["%d_%g" % (int(a), float(b)) for a, b in zip(t["nclicks"], t["coda_type"])]
    t["grp"] = t["grpvar"].astype(str)
    sizes = t.groupby("grp").size()
    keep = sizes[sizes >= MIN_CODAS].index
    t = t[t["grp"].isin(keep)]
    reps = sorted(t["grp"].unique())
    rep_clan_name, rep_lat, rep_lon, rep_loc, mixed = [], [], [], [], 0
    groups = dict(tuple(t.groupby("grp")))
    for g in reps:
        sub = groups[g]
        vc = sub["clan"].value_counts()
        if len(vc) > 1:
            mixed += 1
        rep_clan_name.append(str(vc.index[0]))
        ll = sub[sub["latitude"].notna() & sub["longitude"].notna()]
        rep_lat.append(float(ll["latitude"].mean()) if len(ll) else float("nan"))
        rep_lon.append(circ_mean_lon(ll["longitude"]) if len(ll) else float("nan"))
        rep_loc.append(str(sub["loc"].mode().iloc[0]) if sub["loc"].notna().any() else "NA")
    types = sorted(t["key"].unique())
    tix = {k: i for i, k in enumerate(types)}
    rix = {g: i for i, g in enumerate(reps)}
    counts = np.zeros((len(reps), len(types)))
    np.add.at(counts, ([rix[g] for g in t["grp"]], [tix[k] for k in t["key"]]), 1.0)
    clans = sorted(set(rep_clan_name))
    cix = {c: i for i, c in enumerate(clans)}
    info = {"rows": int(n_rows), "typed_clan_codas_kept": int(len(t)), "repertoires": len(reps),
            "repertoires_mixed_clan": mixed, "types": len(types), "clans": clans,
            "repertoires_without_coords": int(np.isnan(np.array(rep_lat)).sum())}
    notes.append("CSV: %d rows; %d typed codas of assigned clans in %d repertoires with >= %d typed codas"
                 % (n_rows, len(t), len(reps), MIN_CODAS))
    return {"counts": counts, "rep_clan": np.array([cix[c] for c in rep_clan_name]), "clans": clans,
            "lat": np.array(rep_lat), "lon": np.array(rep_lon), "loc": rep_loc, "types": types}, info


# ----------------------------------------------------------------- analysis
def reorder(M, from_clans, to_clans):
    ix = [from_clans.index(c) for c in to_clans]
    return np.asarray(M)[np.ix_(ix, ix)]


def repro_check(S_id, S_non, G, tol):
    out = {}
    for method in ("pearson", "spearman"):
        a, b, g = (S_id, S_non, G) if method == "pearson" else (rank_matrix(S_id), rank_matrix(S_non), rank_matrix(G))
        r_id, r_non = pearson(upper(a), upper(g)), pearson(upper(b), upper(g))
        ok = bool(abs(r_id - REPORTED["r_id"]) <= tol and abs(r_non - REPORTED["r_non"]) <= tol)
        out[method] = {"r_id": r_id, "r_non": r_non, "ok": ok}
    return out


def prep(M, method):
    return rank_matrix(M) if method == "spearman" else np.asarray(M, float)


def run(data_dir, out_dir):
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(out_dir, exist_ok=True)
    notes = []
    res = {"study": "whale-clan-marking-test", "plan": "MARKING-PREREG.md", "reported": REPORTED,
           "priors": PRIORS, "notes": notes}
    csvp = fetch(CSV_URL, os.path.join(data_dir, "pacific_coda_data.csv"), CSV_SIZE)
    rdap = fetch(RDA_URL, os.path.join(data_dir, "HershEtAl2022_Figure4_Data.RData"), RDA_SIZE)
    res["inputs"] = {"csv_sha256": sha256(csvp), "csv_bytes": CSV_SIZE,
                     "rdata_sha256": sha256(rdap), "rdata_bytes": RDA_SIZE}

    csv, info = load_csv(csvp, notes)
    res["csv"] = info
    if csv is None:
        with open(os.path.join(out_dir, "SCHEMA.md"), "w", encoding="utf-8") as fh:
            fh.write("# SCHEMA (unresolved)\n\nColumns: %s\n\nMissing: %s\n" % (info["columns"], info["missing"]))
        res["verdict"] = "SCHEMA_UNRESOLVED"
        write_outputs(res, out_dir, [], [])
        return res

    # CSV rebuild
    cl = csv["clans"]
    n_c = len(cl)
    U = usage_table(csv["counts"], csv["rep_clan"], n_c)
    ids = id_types(U)
    idset = sorted(set(int(i) for arr in ids for i in arr))
    used = np.where(U.max(axis=0) > 0)[0]
    nonset = [int(i) for i in used if int(i) not in set(idset)]
    S_id_csv, S_non_csv = similarity(U, idset), similarity(U, nonset)
    geo = np.isfinite(csv["lat"]) & np.isfinite(csv["lon"])
    Dg = dist_matrix(csv["lat"][geo], csv["lon"][geo])
    rc_geo = csv["rep_clan"][geo]
    G_csv = {}
    for rad in RADII:
        for kind, M in sym_kinds(overlap_matrix(Dg, rc_geo, n_c, rad)).items():
            G_csv["%d_%s" % (int(rad), kind)] = M
    n_rep = np.array([int((csv["rep_clan"] == c).sum()) for c in range(n_c)])
    res["csv_rebuild"] = {"clans": cl, "n_repertoires": n_rep.tolist(),
                          "id_types_per_clan": {cl[c]: [csv["types"][i] for i in ids[c]] for c in range(n_c)},
                          "n_id_types": {cl[c]: int(len(ids[c])) for c in range(n_c)},
                          "n_id_union": len(idset), "n_non_id": len(nonset)}
    rep_csv = repro_check(S_id_csv, S_non_csv, G_csv["1000_mean"], REPRO_TOL_CSV)
    res["csv_rebuild"]["repro"] = rep_csv

    # authors' Figure 4 values
    fig = None
    try:
        objs = read_fig4(rdap)
        res["rdata_objects"] = sorted(str(k) for k in objs.keys())
        cl_f, m_id = pair_matrices(objs["IDmean"], ["acsim", "geov"])
        cl_f2, m_non = pair_matrices(objs["nonIDmean"], ["acsim", "geov"])
        if cl_f != cl_f2:
            raise ValueError("clan lists differ between IDmean and nonIDmean")
        fig = {"clans": cl_f, "S_id": m_id["acsim"], "S_non": m_non["acsim"], "G": m_id["geov"],
               "G_non": m_non["geov"]}
        if np.isnan(fig["S_id"]).any() or np.isnan(fig["S_non"]).any() or np.isnan(fig["G"]).any():
            raise ValueError("missing clan pairs in Figure 4 data")
        res["fig4"] = {"clans": cl_f, "n_rows_id": int(len(objs["IDmean"])),
                       "geov_same_in_both": bool(np.allclose(fig["G"], fig["G_non"], equal_nan=True)),
                       "repro": repro_check(fig["S_id"], fig["S_non"], fig["G"], REPRO_TOL_FIG)}
    except Exception as exc:  # noqa: BLE001
        notes.append("Figure 4 RData not usable: %r" % (exc,))
        fig = None

    # source of the confirmatory tests (rule fixed in MARKING-PREREG.md)
    src = method = None
    if fig is not None:
        for m in ("pearson", "spearman"):
            if res["fig4"]["repro"][m]["ok"]:
                src, method = "authors_fig4", m
                break
    if src is None:
        for m in ("pearson", "spearman"):
            if rep_csv[m]["ok"]:
                src, method = "csv_rebuild", m
                break
    res["source"], res["method"] = src, method
    if src == "authors_fig4":
        clans, S_id, S_non, G = fig["clans"], fig["S_id"], fig["S_non"], fig["G"]
    elif src == "csv_rebuild":
        clans, S_id, S_non, G = cl, S_id_csv, S_non_csv, G_csv["1000_mean"]
    elif fig is not None:
        clans, S_id, S_non, G, method = fig["clans"], fig["S_id"], fig["S_non"], fig["G"], "pearson"
        notes.append("no source reproduced the published r values; tests run on the Figure 4 data for the record")
    else:
        clans, S_id, S_non, G, method = cl, S_id_csv, S_non_csv, G_csv["1000_mean"], "pearson"
        notes.append("no source reproduced the published r values; tests run on the CSV rebuild for the record")
    n = len(clans)
    a_id, a_non, a_g = prep(S_id, method), prep(S_non, method), prep(G, method)

    # T1 exact Mantel tests, T2 contrast, T3 leave one clan out
    t1_id, t1_non = mantel(a_id, a_g, True), mantel(a_non, a_g, True)
    t2 = contrast_test(a_id, a_non, a_g)
    loco = []
    for k in range(n):
        keep = [i for i in range(n) if i != k]
        sub = lambda M: prep(np.asarray(M)[np.ix_(keep, keep)], method)  # noqa: E731
        m_id = mantel(sub(S_id), sub(G), True)
        m_d = contrast_test(sub(S_id), sub(S_non), sub(G))
        loco.append({"dropped": clans[k], "r_id": m_id["obs"], "p_id": m_id["p"], "D": m_d["obs"],
                     "p_D": m_d["p"], "n_perm": m_id["n_perm"]})
    loco_keep = sum(1 for x in loco if x["p_id"] <= 0.10)
    res["T1"] = {"id": t1_id, "non": t1_non, "min_p": 1.0 / t1_id["n_perm"]}
    res["T2"] = t2
    res["T3"] = {"loco": loco, "keep_p_le_0.10": loco_keep, "needed": loco_needed(n),
                 "lose_p_gt_0.05": sum(1 for x in loco if x["p_id"] > ALPHA)}

    # T4 overlap variants (CSV overlap, confirmatory similarity), T5 sampling effort
    same_set = sorted(clans) == sorted(cl)
    res["clan_sets_match"] = same_set
    S_for_csv = reorder(S_id, clans, cl) if same_set else S_id_csv
    if not same_set:
        notes.append("clan names differ between sources; T4/T5 use the CSV rebuild similarity")
    t4 = {}
    for key, Gv in G_csv.items():
        if np.isnan(Gv).any():
            t4[key] = {"obs": float("nan"), "p": float("nan"), "valid": False}
            continue
        m = mantel(prep(S_for_csv, method), prep(Gv, method), True)
        m["valid"] = True
        t4[key] = m
    valid = [v for v in t4.values() if v["valid"]]
    res["T4"] = {"variants": t4, "n_valid": len(valid), "n_sig": sum(1 for v in valid if v["p"] <= ALPHA)}
    if fig is not None and sorted(fig["clans"]) == sorted(cl):
        res["T4"]["r_fig_geov_vs_csv_1000_mean"] = pearson(
            upper(fig["G"]), upper(reorder(G_csv["1000_mean"], cl, fig["clans"])))
        res["T4"]["r_fig_simid_vs_csv_simid"] = pearson(
            upper(fig["S_id"]), upper(reorder(S_id_csv, cl, fig["clans"])))
        res["T4"]["r_fig_simnon_vs_csv_simnon"] = pearson(
            upper(fig["S_non"]), upper(reorder(S_non_csv, cl, fig["clans"])))
    if same_set:
        E =np.log(np.outer(n_rep, n_rep).astype(float))
        E = reorder(E, cl, clans)
        nid = np.array([max(1, len(ids[c])) for c in range(n_c)], float)
        Eid = reorder(np.log(np.outer(nid, nid)), cl, clans)
        res["T5"] = {"r_overlap_effort": pearson(upper(a_g), upper(prep(E, method))),
                     "r_simid_effort": pearson(upper(a_id), upper(prep(E, method))),
                     "partial_effort": partial_mantel(a_id, a_g, prep(E, method), True),
                     "r_overlap_nid": pearson(upper(a_g), upper(prep(Eid, method))),
                     "partial_nid": partial_mantel(a_id, a_g, prep(Eid, method), True)}
    else:
        res["T5"] = None

    # T6 repertoire-level sympatry test (CSV only)
    share = np.array([csv["counts"][r, ids[csv["rep_clan"][r]]].sum() / csv["counts"][r].sum()
                      for r in range(len(csv["rep_clan"]))])
    sym = np.zeros(len(share), dtype=bool)
    sym[np.where(geo)[0]] = sympatry_flags(Dg, rc_geo, MAIN_RADIUS)
    cells_d = {}
    for r in np.where(geo)[0]:
        cells_d.setdefault((cl[csv["rep_clan"][r]], csv["loc"][r]), []).append((share[r], sym[r]))
    cells, cell_rows = [], []
    for (c, loc), v in sorted(cells_d.items()):
        sh = float(np.mean([x for x, _ in v]))
        fy = float(np.mean([y for _, y in v]))
        y = 1 if fy >= 0.5 else 0
        cells.append((c, sh, y))
        cell_rows.append([c, loc, len(v), round(sh, 4), round(fy, 3), y])
    t6 = sympatry_test(cells)
    t6["verdict"] = sympatry_verdict(t6)
    rep_cells = [(cl[csv["rep_clan"][r]], share[r], int(sym[r])) for r in np.where(geo)[0]]
    t6["unblocked_exploratory"] = sympatry_test(rep_cells, max_exact=0)
    res["T6"] = t6

    repro_ok = src is not None
    res["verdict"] = headline(repro_ok, t1_id["p"], t2["p"], loco_keep, n)
    t5 = res["T5"]
    outcomes = {
        "P1": bool(fig is not None and src == "authors_fig4"),
        "P2": bool(t1_id["p"] <= ALPHA),
        "P3": bool(t2["p"] > ALPHA),
        "P4": bool(res["T3"]["lose_p_gt_0.05"] >= 2),
        "P5": (bool(t5["r_overlap_effort"] >= 0.30) if t5 else None),
        "P6": (bool(res["T4"]["n_sig"] < res["T4"]["n_valid"] / 2.0) if res["T4"]["n_valid"] else None),
        "P7": bool(t6["verdict"] != "MARKING_IN_SYMPATRY"),
    }
    b, nb = brier(PRIORS, outcomes)
    res["predictions"] = {"outcomes": outcomes, "brier": b, "n_graded": nb,
                          "n_true": sum(1 for v in outcomes.values() if v)}
    pair_rows = []
    for i in range(n):
        for j in range(i + 1, n):
            pair_rows.append([clans[i], clans[j], round(float(S_id[i, j]), 6), round(float(S_non[i, j]), 6),
                              round(float(G[i, j]), 6)])
    write_outputs(res, out_dir, pair_rows, cell_rows)
    return res


def fmt(x, nd=4):
    if x is None:
        return "NA"
    if isinstance(x, (bool, np.bool_)):
        return str(bool(x))
    if isinstance(x, (int, np.integer)):
        return str(int(x))
    try:
        if math.isnan(float(x)):
            return "NA"
    except (TypeError, ValueError):
        return str(x)
    return ("%." + str(nd) + "f") % float(x)


def write_outputs(res, out_dir, pair_rows, cell_rows):
    def conv(o):
        if hasattr(o, "item"):
            return o.item()
        if hasattr(o, "tolist"):
            return o.tolist()
        return str(o)
    with open(os.path.join(out_dir, "marking_results.json"), "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=1, default=conv)
    with open(os.path.join(out_dir, "pairs.csv"), "w", encoding="utf-8") as fh:
        fh.write("clan_a,clan_b,sim_id,sim_non_id,overlap\n")
        for r in pair_rows:
            fh.write(",".join(str(x) for x in r) + "\n")
    with open(os.path.join(out_dir, "cells.csv"), "w", encoding="utf-8") as fh:
        fh.write("clan,region,n_repertoires,mean_id_share,share_sympatric,sympatric\n")
        for r in cell_rows:
            fh.write(",".join(str(x) for x in r) + "\n")
    L = ["# RESULTS-MARKING", "",
         "whale-clan-marking-test, written by clan_marking.py (plan: MARKING-PREREG.md). "
         "Made with AI agents working in MV2's name; not yet checked by a human expert.", "",
         "**Headline verdict: %s**" % res.get("verdict"), ""]
    if res.get("verdict") == "SCHEMA_UNRESOLVED":
        L.append("The CSV lacked required columns; see SCHEMA.md. No statistic was computed.")
    else:
        L += ["Source of confirmatory tests: %s (method %s)" % (res.get("source"), res.get("method")), ""]
        if "fig4" in res:
            rp = res["fig4"]["repro"]
            L.append("Figure 4 data reproduction: Pearson r_id %s, r_non %s (ok %s); Spearman r_id %s, r_non %s (ok %s); "
                     "published r_id -0.499, r_non -0.076." % (fmt(rp["pearson"]["r_id"]), fmt(rp["pearson"]["r_non"]),
                                                              rp["pearson"]["ok"], fmt(rp["spearman"]["r_id"]),
                                                              fmt(rp["spearman"]["r_non"]), rp["spearman"]["ok"]))
        rc = res["csv_rebuild"]["repro"]
        L.append("CSV rebuild: Pearson r_id %s, r_non %s; identity types per clan %s." % (
            fmt(rc["pearson"]["r_id"]), fmt(rc["pearson"]["r_non"]), res["csv_rebuild"]["n_id_types"]))
        L += ["", "| test | statistic | p | permutations |", "|---|---|---|---|",
              "| T1 identity codas, Mantel r | %s | %s | %d |" % (fmt(res["T1"]["id"]["obs"]), fmt(res["T1"]["id"]["p"]), res["T1"]["id"]["n_perm"]),
              "| T1 non-identity codas, Mantel r | %s | %s | %d |" % (fmt(res["T1"]["non"]["obs"]), fmt(res["T1"]["non"]["p"]), res["T1"]["non"]["n_perm"]),
              "| T2 PRIMARY contrast D = r_id - r_non | %s | %s | %d |" % (fmt(res["T2"]["obs"]), fmt(res["T2"]["p"]), res["T2"]["n_perm"])]
        if res.get("T5"):
            pe, pn = res["T5"]["partial_effort"], res["T5"]["partial_nid"]
            L.append("| T5 identity r given sampling effort (partial) | %s | %s | %d |" % (fmt(pe["obs"]), fmt(pe["p"]), pe["n_perm"]))
            L.append("| T5 identity r given identity-type counts (partial) | %s | %s | %d |" % (fmt(pn["obs"]), fmt(pn["p"]), pn["n_perm"]))
        L += ["", "## T3 leave one clan out", "", "| dropped | r_id | p_id | D | p_D |", "|---|---|---|---|---|"]
        for x in res["T3"]["loco"]:
            L.append("| %s | %s | %s | %s | %s |" % (x["dropped"], fmt(x["r_id"]), fmt(x["p_id"]), fmt(x["D"]), fmt(x["p_D"])))
        L += ["", "Drops keeping p_id <= 0.10: %d (needed %d); drops with p_id > 0.05: %d." % (
            res["T3"]["keep_p_le_0.10"], res["T3"]["needed"], res["T3"]["lose_p_gt_0.05"]),
              "", "## T4 overlap definitions (CSV positions)", "", "| radius_kind | r_id | p |", "|---|---|---|"]
        for k, v in res["T4"]["variants"].items():
            L.append("| %s | %s | %s |" % (k, fmt(v["obs"]), fmt(v["p"])))
        L += ["", "Significant variants: %d of %d valid." % (res["T4"]["n_sig"], res["T4"]["n_valid"])]
        if res.get("T5"):
            L.append("T5: r(overlap, log repertoire-count product) = %s; r(identity similarity, effort) = %s; "
                     "r(overlap, log identity-type product) = %s." % (fmt(res["T5"]["r_overlap_effort"]),
                                                                    fmt(res["T5"]["r_simid_effort"]),
                                                                    fmt(res["T5"]["r_overlap_nid"])))
        t6 = res["T6"]
        L += ["", "## T6 repertoire-level sympatry test", "",
              "Verdict %s: statistic %s (identity-coda share, sympatric minus allopatric region cells), "
              "p_up %s, p_low %s, %d eligible clans, %d arrangements (exact %s)." % (
                  t6["verdict"], fmt(t6["obs"]), fmt(t6["p_up"]), fmt(t6["p_low"]), t6["n_eligible"],
                  t6["n_arrangements"], t6["exact"]),
              "Unblocked repertoire-level reading (exploratory): statistic %s, p_up %s, p_low %s." % (
                  fmt(t6["unblocked_exploratory"]["obs"]), fmt(t6["unblocked_exploratory"]["p_up"]),
                  fmt(t6["unblocked_exploratory"]["p_low"]))]
        pr = res["predictions"]
        L += ["", "## Registered predictions", "", "| prediction | prior | came true |", "|---|---|---|"]
        for k in sorted(PRIORS):
            L.append("| %s | %.2f | %s |" % (k, PRIORS[k], fmt(pr["outcomes"].get(k))))
        L += ["", "%d of %d graded predictions true; Brier %s." % (pr["n_true"], pr["n_graded"], fmt(pr["brier"], 3))]
    L += ["", "Notes: " + "; ".join(res.get("notes", [])), ""]
    with open(os.path.join(out_dir, "RESULTS-MARKING.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(L))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", default="/data")
    ap.add_argument("--out-dir", default="/out")
    a = ap.parse_args(argv)
    res = run(a.data_dir, a.out_dir)
    print("verdict:", res.get("verdict"), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
