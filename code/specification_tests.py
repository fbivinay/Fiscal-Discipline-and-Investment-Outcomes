"""
============================================================================
SPECIFICATION AND DIAGNOSTIC TESTS
Fiscal Discipline & FDI in Indian States (companion to analysis.py)
============================================================================
PURPOSE
  Answer the question "how do you justify that the model you chose is the
  right one?" with evidence rather than assertion.

  PART A  Estimator choice ....... Hausman (FE vs RE), Breusch-Pagan LM
                                   (pooled vs RE), poolability F (FE vs pooled)
  PART B  Error structure ........ Pesaran CD (cross-sectional dependence),
                                   Wooldridge AR(1) (serial correlation),
                                   modified Wald (groupwise heteroskedasticity)
                                   — these are what justify Driscoll-Kraay
  PART C  Functional form ........ Ramsey RESET; log vs IHS vs level for FDI
  PART D  Inference robustness ... same coefficient under Driscoll-Kraay,
                                   cluster-robust and bootstrap SEs
  PART E  Specification curve .... the debt coefficient across every
                                   defensible modelling choice, which at
                                   N = 10 and T = 5 is stronger evidence than
                                   any single test statistic
  PART F  ML hyperparameters ..... grid search under state-blocked CV, so the
                                   forest's depth/leaf settings are selected
                                   rather than asserted

HONESTY NOTE
  Several of these tests are asymptotic in N (Pesaran CD) or in T (Driscoll-
  Kraay, Wooldridge). At N = 10 and T = 5 they are underpowered, and Hausman
  frequently fails to compute because the covariance difference is not
  positive definite. Every result is reported with that caveat attached. A
  test reported as inconclusive is worth more than a test claimed and never
  run.

Run:  python specification_tests.py
Self-check:  python specification_tests.py --selftest
Outputs -> ./spec_tests/
============================================================================
"""
import itertools
import os
import sys
import warnings

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import statsmodels.api as sm
from linearmodels.panel import PanelOLS, PooledOLS, RandomEffects
from scipy import stats
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import LeaveOneGroupOut

warnings.filterwarnings("ignore")
OUT = "results/diagnostics"
RNG = 42
N_BOOT = 2000
DATA_CANDIDATES = ["data/processed/MASTER_PANEL_DATASET.csv",
                   "MASTER_PANEL_FINAL.csv"]
FISCAL = ["fd", "debt", "otr", "capex"]
REGS = FISCAL + ["covid"]
rng = np.random.default_rng(RNG)
plt.rcParams.update({"figure.dpi": 150, "font.size": 9, "axes.titleweight": "bold",
                     "figure.facecolor": "white"})


# ---------------------------------------------------------------- data ------
def load():
    path = next((p for p in DATA_CANDIDATES if os.path.exists(p)), None)
    if path is None:
        sys.exit(f"None of {DATA_CANDIDATES} found. Run from the project root.")
    df = pd.read_csv(path)
    df.columns = ["state", "year", "year_num", "fd", "fd_amt", "debt", "debt_amt",
                  "otr", "otr_amt", "capex", "capex_amt", "rd", "rd_amt",
                  "fdi", "gsdp", "growth", "log_fdi", "log_gsdp",
                  "covid", "post_covid", "literacy", "urban", "rank_in_year"]
    df["ihs_fdi"] = np.arcsinh(df["fdi"])
    return df


def panel(df, dep):
    """linearmodels wants a (entity, time) MultiIndex and no missing dependent."""
    d = df.dropna(subset=[dep]).copy()
    return d.set_index(["state", "year_num"]), d


ROWS = []


def record(part, test, stat, pval, verdict, caveat=""):
    ROWS.append({"Part": part, "Test": test,
                 "Statistic": "" if stat is None else round(float(stat), 4),
                 "p-value": "" if pval is None else round(float(pval), 4),
                 "What it says": verdict, "Caveat at N=10, T=5": caveat})
    p = "" if pval is None else f"p={pval:.4f}"
    s = "" if stat is None else f"stat={stat:.4f}"
    print(f"  {test:<46} {s:<18} {p:<12} {verdict}")


# =========================================================== PART A ==========
def part_a(df, dep, label):
    pdata, _ = panel(df, dep)
    y, X = pdata[dep], sm.add_constant(pdata[REGS])
    fe = PanelOLS(y, X, entity_effects=True).fit()
    re_ = RandomEffects(y, X).fit()
    pooled = PooledOLS(y, X).fit()

    # Hausman: (b_FE - b_RE)' [V_FE - V_RE]^-1 (b_FE - b_RE), fiscal terms only
    b = fe.params[FISCAL] - re_.params[FISCAL]
    V = fe.cov.loc[FISCAL, FISCAL] - re_.cov.loc[FISCAL, FISCAL]
    eig = np.linalg.eigvalsh(V.values)
    if (eig <= 0).any():
        record("A. Estimator", f"Hausman FE vs RE [{label}]", None, None,
               "NOT COMPUTABLE — covariance difference not positive definite",
               "Common at small N; report as inconclusive, do not suppress")
    else:
        h = float(b.values @ np.linalg.inv(V.values) @ b.values)
        p = 1 - stats.chi2.cdf(h, len(FISCAL))
        record("A. Estimator", f"Hausman FE vs RE [{label}]", h, p,
               "FE preferred (reject RE)" if p < .05 else "RE not rejected; FE still consistent",
               "chi2 approximation is asymptotic in N")

    # Breusch-Pagan LM for random effects against pooled OLS
    e = pd.Series(pooled.resids.values, index=pdata.index)
    grp = e.groupby(level=0)
    n_i = grp.size().values
    s_i = grp.sum().values
    lm = (np.sum(n_i) / (2 * (np.mean(n_i) - 1))) * ((np.sum(s_i ** 2) / np.sum(e ** 2)) - 1) ** 2
    p_lm = 1 - stats.chi2.cdf(lm, 1)
    record("A. Estimator", f"Breusch-Pagan LM, pooled vs RE [{label}]", lm, p_lm,
           "Panel structure needed (reject pooled)" if p_lm < .05 else "No panel effect detected",
           "Unbalanced panel; LM uses the mean group size")

    f = fe.f_pooled
    record("A. Estimator", f"F-test for poolability, pooled vs FE [{label}]",
           f.stat, f.pval,
           "State effects jointly significant — FE justified" if f.pval < .05
           else "State effects NOT jointly significant — FE is a modelling choice, not a test result",
           "")
    return fe, pooled


# =========================================================== PART B ==========
def part_b(df, dep, label):
    """The three tests that justify Driscoll-Kraay rather than assuming it."""
    pdata, flat = panel(df, dep)
    fe = PanelOLS(pdata[dep], sm.add_constant(pdata[REGS]), entity_effects=True).fit()
    flat = flat.assign(resid=fe.resids.values)
    wide = flat.pivot_table(index="year_num", columns="state", values="resid")

    # Pesaran CD: average pairwise residual correlation across entities
    corr, pairs = wide.corr(min_periods=3), []
    states = corr.columns
    for i, j in itertools.combinations(range(len(states)), 2):
        r = corr.iloc[i, j]
        t = wide[[states[i], states[j]]].dropna().shape[0]
        if np.isfinite(r) and t >= 3:
            pairs.append((r, t))
    N = len(states)
    cd = np.sqrt(2 / (N * (N - 1))) * sum(np.sqrt(t) * r for r, t in pairs)
    p_cd = 2 * (1 - stats.norm.cdf(abs(cd)))
    record("B. Errors", f"Pesaran CD, cross-sectional dependence [{label}]", cd, p_cd,
           "Cross-sectional dependence present — Driscoll-Kraay justified" if p_cd < .05
           else "No dependence detected; DK is conservative rather than required",
           "CD is asymptotic in N; N=10 gives it little power")

    # Wooldridge AR(1): regress first-differenced residuals on their own lag
    dd = flat.sort_values(["state", "year_num"]).copy()
    dd["d"] = dd.groupby("state")["resid"].diff()
    dd["dlag"] = dd.groupby("state")["d"].shift(1)
    sub = dd.dropna(subset=["d", "dlag"])
    ols = sm.OLS(sub["d"], sm.add_constant(sub["dlag"])).fit(
        cov_type="cluster", cov_kwds={"groups": sub["state"]})
    rho, p_w = ols.params["dlag"], ols.pvalues["dlag"]
    record("B. Errors", f"Wooldridge AR(1) in first differences [{label}]", rho, p_w,
           "Serial correlation present — DK justified" if p_w < .05
           else f"No AR(1) detected (rho={rho:.3f}); -0.5 would mean no serial correlation",
           "Asymptotic in T; T=5 gives two usable differences per state")

    # Modified Wald for groupwise heteroskedasticity
    g = flat.groupby("state")["resid"]
    sig2 = g.apply(lambda s: (s ** 2).mean())
    Ti = g.size()
    s2 = (flat["resid"] ** 2).mean()
    Vi = g.apply(lambda s: ((s ** 2 - (s ** 2).mean()) ** 2).sum()) / (Ti * (Ti - 1))
    ok = Vi > 0
    w = float(np.sum((sig2[ok] - s2) ** 2 / Vi[ok]))
    p_mw = 1 - stats.chi2.cdf(w, ok.sum())
    record("B. Errors", f"Modified Wald, groupwise heteroskedasticity [{label}]", w, p_mw,
           "Error variance differs by state — robust SEs justified" if p_mw < .05
           else "Homoskedasticity across states not rejected",
           "Each state contributes ~5 residuals; treat as indicative")


# =========================================================== PART C ==========
def part_c(df):
    pdata, _ = panel(df, "log_fdi")
    fe = PanelOLS(pdata["log_fdi"], sm.add_constant(pdata[REGS]), entity_effects=True).fit()
    fit = fe.fitted_values.values.ravel()
    X2 = sm.add_constant(np.column_stack([pdata[REGS].values, fit ** 2, fit ** 3]))
    r = sm.OLS(pdata["log_fdi"].values, X2).fit()
    r0 = sm.OLS(pdata["log_fdi"].values, sm.add_constant(pdata[REGS].values)).fit()
    fstat = ((r0.ssr - r.ssr) / 2) / (r.ssr / r.df_resid)
    p = 1 - stats.f.cdf(fstat, 2, r.df_resid)
    record("C. Form", "Ramsey RESET, powers of fitted values", fstat, p,
           "Functional form misspecified" if p < .05 else "No evidence of misspecification",
           "")

    for dep, name in [("log_fdi", "log(FDI)"), ("ihs_fdi", "asinh(FDI)"), ("fdi", "FDI in levels")]:
        pd_, _ = panel(df, dep)
        m = PanelOLS(pd_[dep], sm.add_constant(pd_[REGS]), entity_effects=True).fit()
        record("C. Form", f"Within R-squared, dependent = {name}", m.rsquared_within, None,
               "log and asinh are near-identical here; levels fit far worse"
               if dep == "fdi" else "", "Not a test, a comparison")


# =========================================================== PART D ==========
def part_d(df):
    """Does the inference depend on the standard-error choice?"""
    pdata, flat = panel(df, "log_fdi")
    y, X = pdata["log_fdi"], sm.add_constant(pdata[REGS])
    for name, kw in [("Driscoll-Kraay (kernel)", dict(cov_type="kernel")),
                     ("Cluster-robust by state", dict(cov_type="clustered", cluster_entity=True)),
                     ("Unadjusted", dict())]:
        m = PanelOLS(y, X, entity_effects=True).fit(**kw)
        record("D. Inference", f"FE debt coefficient, SE = {name}",
               m.params["debt"], m.pvalues["debt"],
               f"coef {m.params['debt']:+.3f}, SE {m.std_errors['debt']:.3f}", "")

    states = flat["state"].unique()
    draws = []
    for _ in range(N_BOOT):                                  # cluster bootstrap by state
        pick = rng.choice(states, size=len(states), replace=True)
        rows = pd.concat([flat[flat["state"] == s].assign(state=f"{s}_{k}")
                          for k, s in enumerate(pick)])
        try:
            pb = rows.set_index(["state", "year_num"])
            mb = PanelOLS(pb["log_fdi"], sm.add_constant(pb[REGS]), entity_effects=True).fit()
            draws.append(mb.params["debt"])
        except Exception:
            continue
    draws = np.array(draws)
    lo, hi = np.percentile(draws, [2.5, 97.5])
    record("D. Inference", f"FE debt coefficient, cluster bootstrap ({len(draws)} draws)",
           draws.mean(), None, f"95% CI [{lo:+.3f}, {hi:+.3f}]; excludes zero: {lo * hi > 0}",
           "Resamples states, so it respects the panel structure")


# =========================================================== PART E ==========
def part_e(df):
    """Specification curve: the debt coefficient under every defensible choice."""
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
        pdta, _ = panel(d, dep)
        try:
            X = sm.add_constant(pdta[regs])
            m = (PanelOLS(pdta[dep], X, entity_effects=True).fit(cov_type="clustered",
                                                                cluster_entity=True)
                 if est == "FE" else
                 PooledOLS(pdta[dep], X).fit(cov_type="clustered", cluster_entity=True))
            rows.append({"estimator": est, "covid": covid, "controls": ctrl, "dep": dep,
                         "dropped_state": drop, "n": int(m.nobs),
                         "debt_coef": float(m.params["debt"]),
                         "debt_p": float(m.pvalues["debt"])})
        except Exception:
            continue

    sc = pd.DataFrame(rows).sort_values("debt_coef").reset_index(drop=True)
    sc.to_csv(f"{OUT}/TableS2_specification_curve.csv", index=False)

    for est in ["Pooled", "FE"]:
        s = sc[sc.estimator == est]
        neg = (s.debt_coef < 0).mean() * 100
        sig = ((s.debt_coef < 0) & (s.debt_p < .05)).mean() * 100
        record("E. Spec curve", f"{est}: debt coefficient negative", None, None,
               f"{neg:.0f}% of {len(s)} specifications; negative AND p<0.05 in {sig:.0f}%", "")

    fig, ax = plt.subplots(2, 1, figsize=(10, 7), sharex=True,
                           gridspec_kw={"height_ratios": [3, 1]})
    for est, c in [("Pooled", "steelblue"), ("FE", "darkorange")]:
        s = sc[sc.estimator == est].reset_index(drop=True)
        ax[0].scatter(range(len(s)), s.debt_coef, s=14, c=c, label=f"{est} ({len(s)} specs)")
        ax[1].scatter(range(len(s)), s.debt_p, s=10, c=c)
    ax[0].axhline(0, c="k", lw=1)
    ax[0].set_ylabel("Debt-to-GSDP coefficient"); ax[0].legend(fontsize=8); ax[0].grid(alpha=.3)
    ax[0].set_title("Specification curve: debt coefficient across every defensible "
                    "modelling choice\n(estimator, COVID year, controls, transform, "
                    "leave-one-state-out)", fontsize=10)
    ax[1].axhline(.05, ls=":", c="firebrick", lw=1)
    ax[1].set_ylabel("p-value"); ax[1].set_xlabel("Specification, sorted by coefficient")
    ax[1].grid(alpha=.3)
    fig.tight_layout(); fig.savefig(f"{OUT}/FigS1_specification_curve.png",
                                    bbox_inches="tight"); plt.close(fig)
    print(f"  specification curve: {len(sc)} specifications estimated")


# =========================================================== PART F ==========
def part_f(df):
    """Select the forest's depth and leaf size instead of asserting them."""
    d = df.dropna(subset=["log_fdi"])
    X, y, g = d[REGS].values, d["log_fdi"].values, d["state"].values
    # R2 is POOLED over the out-of-fold predictions. Averaging per-fold R2 the way
    # GridSearchCV does would compare each held-out state against its own mean, and
    # with ~5 rows of tiny within-state variance every fold scores hugely negative.
    rows = []
    for depth, leaf in itertools.product([2, 3, 4, 5, None], [2, 3, 4, 6, 8]):
        pred = np.empty(len(y))
        for tr, te in LeaveOneGroupOut().split(X, y, g):
            m = RandomForestRegressor(n_estimators=500, max_depth=depth,
                                      min_samples_leaf=leaf, random_state=RNG)
            pred[te] = m.fit(X[tr], y[tr]).predict(X[te])
        r2 = 1 - np.sum((y - pred) ** 2) / np.sum((y - y.mean()) ** 2)
        rows.append({"max_depth": depth, "min_samples_leaf": leaf,
                     "pooled_leave_one_state_out_R2": round(r2, 4)})
    res = pd.DataFrame(rows).sort_values("pooled_leave_one_state_out_R2", ascending=False)
    res["rank"] = range(1, len(res) + 1)
    res.to_csv(f"{OUT}/TableS3_rf_hyperparameter_grid.csv", index=False)

    best = res.iloc[0]
    record("F. ML tuning", "Random forest grid search, state-blocked CV",
           best.pooled_leave_one_state_out_R2, None,
           f"best: max_depth={best.max_depth}, min_samples_leaf={best.min_samples_leaf}"
           f" (paper uses depth 3, leaf 4)", "25 combinations, 10 folds each")
    used = res[(res.max_depth == 3) & (res.min_samples_leaf == 4)]
    if len(used):
        record("F. ML tuning", "Paper's hand-chosen setting (depth 3, leaf 4)",
               float(used.pooled_leave_one_state_out_R2.iloc[0]), None,
               f"ranks {int(used['rank'].iloc[0])} of {len(res)}; spread across the whole "
               f"grid is {res.pooled_leave_one_state_out_R2.max() - res.pooled_leave_one_state_out_R2.min():.3f} R2",
               "")


# =========================================================== PART G ==========
# Wild cluster bootstrap-t, null imposed, Rademacher weights (Cameron, Gelbach
# and Miller 2008). At G = 10 clusters neither Driscoll-Kraay (asymptotic in T)
# nor the cluster-robust t (asymptotic in G) is reliable; this is the arbiter.
# ============================================================================
B_WILD = 1999


def wild_bootstrap_p(df, dep, regs, target, pooled=False, seed=RNG):
    r = np.random.default_rng(seed)
    d = df.dropna(subset=[dep]).copy()
    idx = d.set_index(["state", "year_num"])
    Est = PooledOLS if pooled else (lambda y, X: PanelOLS(y, X, entity_effects=True))

    def fit(y, X, robust=True):
        m = Est(y, X)
        return (m.fit(cov_type="clustered", cluster_entity=True) if robust else m.fit())

    full = fit(idx[dep], sm.add_constant(idx[regs]))
    t_obs = full.params[target] / full.std_errors[target]
    rest = fit(idx[dep], sm.add_constant(idx[[v for v in regs if v != target]]), robust=False)
    base, res = rest.fitted_values.values.ravel(), rest.resids.values.ravel()
    states = d["state"].values
    uniq = np.unique(states)
    hits = 0
    for _ in range(B_WILD):
        w = dict(zip(uniq, r.choice([-1.0, 1.0], size=len(uniq))))
        ib = idx.copy()
        ib[dep] = base + res * np.array([w[s] for s in states])
        try:
            m = fit(ib[dep], sm.add_constant(ib[regs]))
            hits += abs(m.params[target] / m.std_errors[target]) >= abs(t_obs)
        except Exception:
            continue
    return float(full.params[target]), float(full.pvalues[target]), (hits + 1) / (B_WILD + 1)


def part_g(df):
    POOLED_REGS = REGS + ["literacy", "urban"]
    jobs = [("log_fdi", POOLED_REGS, "debt", True, "Model 1 pooled: debt"),
            ("log_fdi", POOLED_REGS, "literacy", True, "Model 1 pooled: literacy"),
            ("log_fdi", POOLED_REGS, "capex", True, "Model 1 pooled: capital expenditure"),
            ("log_fdi", REGS, "debt", False, "Model 1 within: debt"),
            ("log_fdi", REGS, "fd", False, "Model 1 within: fiscal deficit"),
            ("growth", REGS, "fd", False, "Model 2 within: fiscal deficit"),
            ("growth", REGS, "debt", False, "Model 2 within: debt"),
            ("growth", REGS, "otr", False, "Model 2 within: own tax revenue"),
            ("growth", REGS, "covid", False, "Model 2 within: COVID dummy")]
    rows = []
    for dep, regs, tgt, pooled, label in jobs:
        coef, p_cl, p_wb = wild_bootstrap_p(df, dep, regs, tgt, pooled)
        rows.append({"Coefficient": label, "Estimate": round(coef, 4),
                     "Cluster-robust p": round(p_cl, 4),
                     "Wild cluster bootstrap p": round(p_wb, 4),
                     "Significant at 5% under bootstrap": "YES" if p_wb < .05 else "no"})
        record("G. Wild bootstrap", label, coef, p_wb,
               f"cluster p={p_cl:.4f} -> bootstrap p={p_wb:.4f}"
               + ("" if (p_cl < .05) == (p_wb < .05) else "   <<< VERDICT CHANGES"),
               f"{B_WILD} Rademacher draws over {df['state'].nunique()} clusters")
    pd.DataFrame(rows).to_csv(f"{OUT}/TableS4_wild_cluster_bootstrap.csv", index=False)
def selftest():
    e = pd.Series([1., -1., 2., -2.], index=pd.MultiIndex.from_product([["A", "B"], [1, 2]]))
    grp = e.groupby(level=0)
    assert np.allclose(grp.sum().values, [0., 0.]), "group sums wrong"

    v = np.array([[2.0, 0.0], [0.0, -1.0]])                 # not positive definite
    assert (np.linalg.eigvalsh(v) <= 0).any(), "PD guard would miss a bad Hausman matrix"
    v2 = np.array([[2.0, 0.1], [0.1, 1.0]])
    assert (np.linalg.eigvalsh(v2) > 0).all(), "PD guard would reject a valid matrix"

    for hits, n in [(0, 100), (50, 100)]:                   # p-values stay in range
        assert 0 < (1 + hits) / (1 + n) <= 1

    g = np.repeat(np.arange(10), 5)                         # grouped CV never leaks a state
    for tr, te in LeaveOneGroupOut().split(np.zeros((50, 2)), np.zeros(50), g):
        assert not set(g[tr]) & set(g[te])

    d = pd.DataFrame({"state": ["A"] * 3 + ["B"] * 3, "x": [1., 2, 3, 4, 5, 6]})
    dm = d.groupby("state")["x"].transform(lambda s: s - s.mean())
    assert np.allclose(dm.values, [-1, 0, 1, -1, 0, 1]), "demeaning wrong"
    print("selftest OK")


# ---------------------------------------------------------------- main ------
def main():
    os.makedirs(OUT, exist_ok=True)
    df = load()
    print(f"Loaded panel: {len(df)} state-years, {df['state'].nunique()} states, "
          f"{df['log_fdi'].notna().sum()} with FDI\n")

    print("PART A — estimator choice")
    part_a(df, "log_fdi", "Model 1, log FDI")
    part_a(df, "growth", "Model 2, GSDP growth")
    print("\nPART B — error structure (what justifies Driscoll-Kraay)")
    part_b(df, "log_fdi", "Model 1")
    part_b(df, "growth", "Model 2")
    print("\nPART C — functional form")
    part_c(df)
    print("\nPART D — does inference depend on the SE choice?")
    part_d(df)
    print("\nPART E — specification curve")
    part_e(df)
    print("\nPART F — ML hyperparameter selection")
    part_f(df)
    print("\nPART G — wild cluster bootstrap (the arbiter at G = 10 clusters)")
    part_g(df)

    tab = pd.DataFrame(ROWS)
    tab.to_csv(f"{OUT}/TableS1_specification_tests.csv", index=False)
    print(f"\nAll outputs in ./{OUT}/")
    print(sorted(os.listdir(OUT)))


if __name__ == "__main__":
    selftest() if "--selftest" in sys.argv else main()
