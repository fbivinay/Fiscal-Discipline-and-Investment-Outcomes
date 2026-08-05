# -*- coding: utf-8 -*-
"""
Wild cluster bootstrap-t for every specification in the curve of Part E.

The curve as published reports cluster-robust p-values. Section 6.7 names the
wild cluster bootstrap as the paper's arbiter at ten clusters, so the curve
should be read on the same footing as everything else. Running 132
specifications through linearmodels at 1,999 draws apiece is a quarter of a
million model fits and was skipped on cost grounds; done directly it is cheap,
because only the dependent variable changes across draws.

For a fixed design matrix the OLS coefficients are a linear map of y, so
A = (X'X)^-1 X' is computed once per specification and reused for every draw.
The cluster-robust variance of a single coefficient collapses further: with
a = (X'X)^-1 e_debt and h = X a, the CR1 variance of the debt coefficient is
c * sum_g (sum_{i in g} h_i u_i)^2, which is a grouped sum over residuals and
needs no k-by-k matrix per draw. All 1,999 draws are carried as columns of one
array.

Bootstrap-t with the null imposed, Rademacher weights drawn per state:
  1. unrestricted fit -> t = beta_debt / se_debt
  2. restricted fit with debt excluded -> fitted values and residuals
  3. y* = fitted + w_state * residual, refit unrestricted, t* = beta* / se*
  4. p = share of draws with |t*| >= |t|

Run:  python bootstrap_specification_curve.py
      python bootstrap_specification_curve.py --selftest
Outputs -> results/diagnostics/TableS2b_specification_curve_bootstrap.csv
"""
import itertools
import os
import sys
import warnings

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

OUT = "results/diagnostics"
RNG = 42
N_BOOT = 1999
DATA_CANDIDATES = ["data/processed/MASTER_PANEL_DATASET.csv", "MASTER_PANEL_FINAL.csv"]
REGS = ["fd", "debt", "otr", "capex", "covid"]
COLUMNS = ["state", "year", "year_num", "fd", "fd_amt", "debt", "debt_amt", "otr",
           "otr_amt", "capex", "capex_amt", "rd", "rd_amt", "fdi", "gsdp", "growth",
           "log_fdi", "log_gsdp", "covid", "post_covid", "literacy", "urban",
           "rank_in_year"]


def load():
    path = next((p for p in DATA_CANDIDATES if os.path.exists(p)), None)
    if path is None:
        sys.exit(f"None of {DATA_CANDIDATES} found. Run from the project root.")
    df = pd.read_csv(path)
    df.columns = COLUMNS
    df["ihs_fdi"] = np.arcsinh(df["fdi"])
    return df


def cluster_var(h, resid, codes, n_clust, n, k):
    """CR1 variance of one coefficient. resid is n-by-B; returns length-B."""
    resid = np.atleast_2d(resid.T).T
    sums = np.zeros((n_clust, resid.shape[1]))
    np.add.at(sums, codes, h[:, None] * resid)
    c = (n_clust / (n_clust - 1)) * ((n - 1) / (n - k))
    return c * (sums ** 2).sum(axis=0)


def wild_cluster_p(y, X, j, codes, n_clust, rng, n_boot=N_BOOT):
    """Bootstrap-t p-value for coefficient j, null imposed, Rademacher weights."""
    n, k = X.shape
    XtX_inv = np.linalg.pinv(X.T @ X)
    A = XtX_inv @ X.T
    a = XtX_inv[:, j]
    h = X @ a

    beta = A @ y
    resid = y - X @ beta
    se = np.sqrt(cluster_var(h, resid, codes, n_clust, n, k)[0])
    if not np.isfinite(se) or se <= 0:
        return np.nan, np.nan, np.nan
    t_obs = beta[j] / se

    # restricted fit: debt excluded, so the null beta_debt = 0 holds by construction
    keep = [c for c in range(k) if c != j]
    Xr = X[:, keep]
    beta_r = np.linalg.pinv(Xr.T @ Xr) @ Xr.T @ y
    fitted_r = Xr @ beta_r
    resid_r = y - fitted_r

    w = rng.choice(np.array([-1.0, 1.0]), size=(n_clust, n_boot))[codes]
    Y = fitted_r[:, None] + resid_r[:, None] * w
    B = A @ Y
    U = Y - X @ B
    se_b = np.sqrt(cluster_var(h, U, codes, n_clust, n, k))
    ok = np.isfinite(se_b) & (se_b > 0)
    if ok.sum() < n_boot // 2:
        return beta[j], t_obs, np.nan
    t_star = B[j, ok] / se_b[ok]
    p = (np.abs(t_star) >= np.abs(t_obs)).mean()
    return beta[j], t_obs, p


def design(d, dep, regs, entity_effects):
    """Return y, X, cluster codes. Entity effects enter as dummies, not demeaning,
    so the residual degrees of freedom used by CR1 count them."""
    d = d.dropna(subset=[dep] + regs)
    y = d[dep].to_numpy(float)
    parts = [np.ones((len(d), 1)), d[regs].to_numpy(float)]
    names = ["const"] + regs
    if entity_effects:
        dum = pd.get_dummies(d["state"], drop_first=True).to_numpy(float)
        parts.append(dum)
        names += [f"state_{i}" for i in range(dum.shape[1])]
    X = np.hstack(parts)
    codes, uniq = pd.factorize(d["state"])
    return y, X, names, codes, len(uniq)


def curve(df, n_boot=N_BOOT, verbose=True):
    rng = np.random.default_rng(RNG)
    rows = []
    for est, covid, ctrl, dep, drop in itertools.product(
            ["FE", "Pooled"], ["keep COVID year", "drop COVID year"],
            ["no controls", "Census controls"], ["log_fdi", "ihs_fdi"],
            ["none"] + sorted(df["state"].unique())):
        d = df if drop == "none" else df[df["state"] != drop]
        if covid.startswith("drop"):
            d = d[d["covid"] == 0]
        regs = [r for r in REGS if not (covid.startswith("drop") and r == "covid")]
        if ctrl == "Census controls":
            if est == "FE":
                continue                       # collinear with entity effects
            regs = regs + ["literacy", "urban"]
        y, X, names, codes, n_clust = design(d, dep, regs, est == "FE")
        j = names.index("debt")
        coef, t_obs, p = wild_cluster_p(y, X, j, codes, n_clust, rng, n_boot)
        rows.append({"estimator": est, "covid": covid, "controls": ctrl, "dep": dep,
                     "dropped_state": drop, "n": len(y), "debt_coef": coef,
                     "t": t_obs, "debt_p_bootstrap": p})
        if verbose and len(rows) % 20 == 0:
            print(f"  {len(rows)} specifications done")
    return pd.DataFrame(rows)


def selftest():
    """The bootstrap machinery must reproduce a known cluster-robust SE, and the
    p-value must be stable across seeds."""
    import statsmodels.api as sm
    df = load()
    d = df.dropna(subset=["log_fdi"])
    y, X, names, codes, n_clust = design(d, "log_fdi", REGS, False)
    j = names.index("debt")

    ref = sm.OLS(y, X).fit(cov_type="cluster", cov_kwds={"groups": codes, "use_correction": True})
    XtX_inv = np.linalg.pinv(X.T @ X)
    h = X @ XtX_inv[:, j]
    resid = y - X @ (XtX_inv @ X.T @ y)
    mine = np.sqrt(cluster_var(h, resid, codes, n_clust, len(y), X.shape[1])[0])
    print(f"  cluster-robust SE  statsmodels {ref.bse[j]:.6f}   here {mine:.6f}")
    assert abs(ref.bse[j] - mine) < 1e-8, "CR1 variance does not match statsmodels"

    # the paper's headline pooled specification carries the Census controls and is
    # reported at bootstrap p = 0.057; reproduce it before trusting the other 131
    yc, Xc, nc_names, codes_c, n_clust_c = design(d, "log_fdi", REGS + ["literacy", "urban"], False)
    jc = nc_names.index("debt")
    ps = [wild_cluster_p(yc, Xc, jc, codes_c, n_clust_c, np.random.default_rng(s))[2]
          for s in (1, 2, 3)]
    print("  headline pooled spec, bootstrap p across three seeds: "
          + ", ".join(f"{p:.4f}" for p in ps) + "   (paper reports 0.057)")
    assert max(ps) - min(ps) < 0.02, "bootstrap p unstable across seeds"
    assert abs(np.mean(ps) - 0.057) < 0.015, "does not reproduce the published bootstrap p"

    # a coefficient the paper reports as clearly null must not come out significant
    jc = names.index("otr")
    _, _, p_otr = wild_cluster_p(y, X, jc, codes, n_clust, np.random.default_rng(RNG))
    print(f"  own tax revenue, a null the paper reports: p = {p_otr:.4f}")
    assert p_otr > 0.10, "own tax revenue should not be significant"
    print("  self-test passed")


def main():
    df = load()
    os.makedirs(OUT, exist_ok=True)
    print(f"Wild cluster bootstrap, {N_BOOT} draws per specification")
    sc = curve(df)
    sc.to_csv(f"{OUT}/TableS2b_specification_curve_bootstrap.csv", index=False)

    published = f"{OUT}/TableS2_specification_curve.csv"
    if os.path.exists(published):
        old = pd.read_csv(published)
        key = ["estimator", "covid", "controls", "dep", "dropped_state"]
        merged = sc.merge(old[key + ["debt_p"]], on=key, how="left")
        gap = (merged["debt_coef"] - merged.merge(
            old[key + ["debt_coef"]], on=key, suffixes=("", "_old"))["debt_coef_old"]).abs().max()
        print(f"\n  largest coefficient gap against the published curve: {gap:.2e}")
    else:
        merged = sc.assign(debt_p=np.nan)

    print(f"\n  {'':<8} {'specs':>6} {'negative':>10} {'p<0.05 cluster':>16} "
          f"{'p<0.05 bootstrap':>18}")
    for est in ["Pooled", "FE"]:
        s = merged[merged.estimator == est]
        neg = (s.debt_coef < 0).mean() * 100
        sig_c = ((s.debt_coef < 0) & (s.debt_p < .05)).mean() * 100
        sig_b = ((s.debt_coef < 0) & (s.debt_p_bootstrap < .05)).mean() * 100
        print(f"  {est:<8} {len(s):>6} {neg:>9.0f}% {sig_c:>15.0f}% {sig_b:>17.0f}%")
    print(f"\n  written to {OUT}/TableS2b_specification_curve_bootstrap.csv")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    else:
        main()
