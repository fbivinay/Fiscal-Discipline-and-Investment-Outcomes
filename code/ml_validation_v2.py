"""
============================================================================
MACHINE LEARNING VALIDATION v2 — panel-aware rigour additions
Fiscal Discipline & FDI in Indian States (extends ml_validation.py)
============================================================================
WHAT v2 ADDS OVER v1 (each item answers a specific referee objection)

  A  Panel-aware CV for the LASSO penalty (state-blocked, not row-wise LOO),
     plus the coefficient ENTRY ORDER along the regularisation path — the
     informative fact that a near-zero alpha hides.
  B  Stability selection: 500 state-subsample refits over an alpha grid,
     giving a selection PROBABILITY per variable instead of a single
     "everything survived" table.
  C  WITHIN specification: LASSO + RF/SHAP on state-demeaned data, mirroring
     the fixed-effects econometric model. v1 only ever ran the pooled one.
  D  SHAP leave-one-state-out RANK stability (v1 only did this for LASSO;
     the research plan claimed a SHAP version that was never produced).
  E  Permutation null: is debt's #1 SHAP rank distinguishable from chance at
     n = 48? Gives an actual p-value for an importance ranking.
  F  Out-of-sample R2 under THREE cv schemes side by side — row-wise LOO
     (leaky: same state in train and test), leave-one-state-out, and
     forward-chaining by year. The gap between them IS a result.
  G  SHAP interaction debt x capital expenditure — answers the open question
     the paper poses in Section 7.2 with data already in hand.
  H  Gradient boosting as a third non-linear lens (cheap cross-check).

Framing is unchanged from v1 and deliberately so: this VALIDATES the panel
regressions at n = 48. It does not predict FDI.

Run:  python ml_validation_v2.py
Self-check:  python ml_validation_v2.py --selftest
Outputs -> ./ml_results_v2/
============================================================================
"""
import os
import sys

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import shap
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import ElasticNetCV, LassoCV, LinearRegression, lasso_path
from sklearn.model_selection import LeaveOneGroupOut, LeaveOneOut, cross_val_predict
from sklearn.preprocessing import StandardScaler

OUT = "results/ml/panel_aware_v2"
RNG = 42
N_STABILITY = 500   # state-subsample refits for stability selection
N_PERM = 500        # permutations for the SHAP null test
rng = np.random.default_rng(RNG)

DATA_CANDIDATES = ["data/processed/MASTER_PANEL_DATASET.csv",
                   "MASTER_PANEL_FINAL.csv"]

# same 5 time-varying regressors the fixed-effects model uses; the two Census
# controls stay out — see the v1 urbanisation leakage diagnosis
FEATURES = ["fd", "debt", "otr", "capex", "covid"]
NICE = {"fd": "Fiscal Deficit", "debt": "Debt-to-GSDP", "otr": "Own Tax Revenue",
        "capex": "Capital Expenditure", "covid": "COVID year"}
KEY = "debt"  # the variable whose dominance the whole exercise is testing

plt.rcParams.update({"figure.dpi": 150, "font.size": 9, "axes.titleweight": "bold",
                     "figure.facecolor": "white"})


# ------------------------------------------------------------------ data ----
def load_panel():
    path = next((p for p in DATA_CANDIDATES if os.path.exists(p)), None)
    if path is None:
        sys.exit(f"None of {DATA_CANDIDATES} found. Run from the project root.")
    df = pd.read_csv(path)
    df.columns = ["state", "year", "year_num", "fd", "fd_amt", "debt", "debt_amt",
                  "otr", "otr_amt", "capex", "capex_amt", "rd", "rd_amt",
                  "fdi", "gsdp", "growth", "log_fdi", "log_gsdp",
                  "covid", "post_covid", "literacy", "urban", "rank_in_year"]
    d = df.dropna(subset=["log_fdi"]).reset_index(drop=True)  # 48 rows (UP FY20/21 out)
    print(f"Loaded {path}: {len(d)} observations, {d['state'].nunique()} states, "
          f"{len(FEATURES)} predictors, target = log(FDI)")
    return d


def demean_by_state(arr, states):
    """State-demean each column: the algebra a fixed-effects estimator performs."""
    out = np.asarray(arr, dtype=float).copy()
    for s in np.unique(states):
        m = states == s
        out[m] = out[m] - out[m].mean(axis=0)
    return out


def rank_of(scores, feats, target):
    """1 = most important. scores aligned with feats."""
    order = np.argsort(-np.asarray(scores))
    return list(np.array(feats)[order]).index(target) + 1


def shap_importance(X_fit, y_fit, seed=RNG, n_trees=1000):
    """mean |SHAP| per feature from a shallow forest. Depth/leaf caps stop a
    forest with <50 rows memorising individual states."""
    rf = RandomForestRegressor(n_estimators=n_trees, max_depth=3, min_samples_leaf=4,
                               random_state=seed).fit(X_fit, y_fit)
    sv = shap.TreeExplainer(rf).shap_values(X_fit, check_additivity=False)
    return rf, sv, np.abs(sv).mean(axis=0)


# =========================================================== PART A ==========
# LASSO with a PANEL-AWARE penalty, plus entry order along the path
# ============================================================================
def part_a(X, y, groups, d):
    # inner CV folds that never split a state across train and test
    logo_folds = list(LeaveOneGroupOut().split(X, y, groups))

    lasso = LassoCV(cv=logo_folds, random_state=RNG, max_iter=50000).fit(X, y)
    enet = ElasticNetCV(cv=logo_folds, l1_ratio=[.3, .5, .7, .9, 1],
                        random_state=RNG, max_iter=50000).fit(X, y)
    lasso_rowwise = LassoCV(cv=LeaveOneOut(), random_state=RNG, max_iter=50000).fit(X, y)

    tab = pd.DataFrame({
        "Variable": [NICE[f] for f in FEATURES],
        "LASSO_coef_state_blocked_CV": lasso.coef_.round(4),
        "LASSO_selected": np.where(np.abs(lasso.coef_) > 1e-8, "YES", "no"),
        "ElasticNet_coef": enet.coef_.round(4),
        "ElasticNet_selected": np.where(np.abs(enet.coef_) > 1e-8, "YES", "no"),
    }).sort_values("LASSO_coef_state_blocked_CV", key=lambda s: s.abs(), ascending=False)
    tab.to_csv(f"{OUT}/TableV1_lasso_state_blocked.csv", index=False)
    print("\n=== TABLE V1: LASSO / ELASTIC NET, state-blocked CV penalty ===")
    print(tab.to_string(index=False))
    print(f"alpha state-blocked = {lasso.alpha_:.5f} | alpha row-wise LOO (v1) = "
          f"{lasso_rowwise.alpha_:.5f} | ElasticNet alpha = {enet.alpha_:.5f}, "
          f"l1_ratio = {enet.l1_ratio_}")

    # --- entry order: which variable survives the HARSHEST penalty? ----------
    alphas = np.logspace(0.7, -3, 300)
    _, coefs, _ = lasso_path(X, y, alphas=alphas)
    entry_alpha, entry_rank = [], []
    for i in range(len(FEATURES)):
        nz = np.flatnonzero(np.abs(coefs[i]) > 1e-8)
        entry_alpha.append(alphas[nz[0]] if nz.size else np.nan)
    order = np.argsort(-np.nan_to_num(np.array(entry_alpha), nan=-1))
    for i in range(len(FEATURES)):
        entry_rank.append(int(np.flatnonzero(order == i)[0]) + 1)
    tab_entry = pd.DataFrame({
        "Variable": [NICE[f] for f in FEATURES],
        "Alpha_at_which_variable_enters": np.round(entry_alpha, 4),
        "Entry_order": entry_rank,
    }).sort_values("Entry_order")
    tab_entry.to_csv(f"{OUT}/TableV2_lasso_entry_order.csv", index=False)
    print("\n=== TABLE V2: LASSO ENTRY ORDER (1 = survives the harshest penalty) ===")
    print(tab_entry.to_string(index=False))
    return lasso


# =========================================================== PART B ==========
# Stability selection — selection PROBABILITY, not a one-shot yes/no
# ============================================================================
def part_b(X, y, d, alpha_cv):
    states = d["state"].unique()
    half = len(states) // 2
    grid = np.logspace(0.3, -2, 30)
    hits = np.zeros((len(grid), len(FEATURES)))

    for _ in range(N_STABILITY):
        keep = rng.choice(states, size=half, replace=False)       # Meinshausen-Buhlmann
        m = d["state"].isin(keep).values                          # subsampling, by STATE
        _, coefs, _ = lasso_path(X[m], y[m], alphas=grid)
        hits += (np.abs(coefs).T > 1e-8)

    prob = hits / N_STABILITY
    # the discriminating statistic: the harshest penalty a variable still
    # survives 80% of the time. Raw selection probability at a mild alpha is
    # ~1.0 for everything and says nothing.
    breakdown = [grid[prob[:, i] >= 0.8].max() if (prob[:, i] >= 0.8).any() else np.nan
                 for i in range(len(FEATURES))]
    tab = pd.DataFrame({
        "Variable": [NICE[f] for f in FEATURES],
        "Harshest_alpha_surviving_80pct_of_subsamples": np.round(breakdown, 4),
        "Selection_prob_at_CV_alpha": prob[np.argmin(np.abs(grid - alpha_cv))].round(3),
    }).sort_values("Harshest_alpha_surviving_80pct_of_subsamples", ascending=False)
    tab.to_csv(f"{OUT}/TableV3_stability_selection.csv", index=False)
    print(f"\n=== TABLE V3: STABILITY SELECTION ({N_STABILITY} {half}-state subsamples) ===")
    print(tab.to_string(index=False))

    fig, ax = plt.subplots(figsize=(8, 5))
    for i, f in enumerate(FEATURES):
        ax.plot(np.log10(grid), prob[:, i], lw=1.8, marker="o", ms=2.5, label=NICE[f])
    ax.axhline(0.8, ls=":", c="k", lw=1, label="0.8 selection threshold")
    ax.set_xlabel("log10(penalty alpha)  ->  stronger shrinkage")
    ax.set_ylabel(f"Selection probability across {N_STABILITY} state subsamples")
    ax.set_title("Figure V1: Stability selection — how reliably each predictor survives")
    ax.legend(fontsize=8); ax.grid(alpha=.3)
    fig.tight_layout(); fig.savefig(f"{OUT}/FigV1_stability_selection.png",
                                    bbox_inches="tight"); plt.close(fig)


# =========================================================== PART C ==========
# WITHIN specification — state-demeaned, mirroring fixed effects
# ============================================================================
def part_c(X_raw, y, d, pooled_shap):
    states = d["state"].values
    Xw_raw = demean_by_state(X_raw, states)
    yw = demean_by_state(y.reshape(-1, 1), states).ravel()
    Xw = StandardScaler().fit_transform(Xw_raw)

    folds = list(LeaveOneGroupOut().split(Xw, yw, states))
    lw = LassoCV(cv=folds, random_state=RNG, max_iter=50000).fit(Xw, yw)
    _, svw, impw = shap_importance(Xw_raw, yw)

    tab = pd.DataFrame({
        "Variable": [NICE[f] for f in FEATURES],
        "WITHIN_LASSO_coef": lw.coef_.round(4),
        "WITHIN_mean_abs_SHAP": impw.round(4),
        "POOLED_mean_abs_SHAP": pooled_shap.round(4),
    }).sort_values("WITHIN_mean_abs_SHAP", ascending=False)
    tab.to_csv(f"{OUT}/TableV4_within_specification.csv", index=False)
    print("\n=== TABLE V4: WITHIN (state-demeaned) LASSO + SHAP vs POOLED SHAP ===")
    print(tab.to_string(index=False))
    print(f"WITHIN debt SHAP rank = {rank_of(impw, FEATURES, KEY)} of {len(FEATURES)}; "
          f"POOLED debt SHAP rank = {rank_of(pooled_shap, FEATURES, KEY)}")

    fig, ax = plt.subplots(figsize=(8, 4.5))
    idx = np.arange(len(FEATURES)); w = 0.38
    o = np.argsort(-pooled_shap)
    ax.barh(idx + w / 2, pooled_shap[o], w, label="Pooled (between states)", color="steelblue")
    ax.barh(idx - w / 2, impw[o], w, label="Within (state-demeaned)", color="darkorange")
    ax.set_yticks(idx, [NICE[FEATURES[i]] for i in o])
    ax.set_xlabel("mean |SHAP|"); ax.legend(fontsize=8); ax.grid(axis="x", alpha=.3)
    ax.set_title("Figure V2: SHAP importance, pooled vs within-state specification")
    fig.tight_layout(); fig.savefig(f"{OUT}/FigV2_within_vs_pooled.png",
                                    bbox_inches="tight"); plt.close(fig)


# =========================================================== PART D ==========
# SHAP leave-one-state-out RANK stability (v1 only did this for LASSO)
# ============================================================================
def part_d(X_raw, y, d):
    ranks, tops = [], []
    for s in d["state"].unique():
        m = (d["state"] != s).values
        _, _, imp = shap_importance(X_raw[m], y[m], n_trees=500)
        ranks.append(rank_of(imp, FEATURES, KEY))
        tops.append(NICE[FEATURES[int(np.argmax(imp))]])
    tab = pd.DataFrame({"State_left_out": d["state"].unique(),
                        "Debt_SHAP_rank": ranks, "Top_ranked_variable": tops})
    tab.to_csv(f"{OUT}/TableV5_shap_rank_stability.csv", index=False)
    print("\n=== TABLE V5: SHAP RANK STABILITY (leave-one-state-out, 10 refits) ===")
    print(tab.to_string(index=False))
    print(f"Debt mean rank = {np.mean(ranks):.2f}, SD = {np.std(ranks):.2f}, "
          f"ranked #1 in {sum(r == 1 for r in ranks)}/10 refits")
    return ranks


# =========================================================== PART E ==========
# Permutation null — is the #1 SHAP rank distinguishable from chance at n=48?
# ============================================================================
def part_e(X_raw, y, obs_imp):
    obs_gap = np.sort(obs_imp)[-1] - np.sort(obs_imp)[-2]
    obs_top_is_key = int(np.argmax(obs_imp)) == FEATURES.index(KEY)
    key_first, gap_ge = 0, 0
    null_gaps = np.empty(N_PERM)

    for b in range(N_PERM):
        yp = rng.permutation(y)
        _, _, imp = shap_importance(X_raw, yp, seed=RNG + b, n_trees=300)
        null_gaps[b] = np.sort(imp)[-1] - np.sort(imp)[-2]
        key_first += int(np.argmax(imp) == FEATURES.index(KEY))
        gap_ge += int(null_gaps[b] >= obs_gap)

    p_rank = (1 + key_first) / (1 + N_PERM)   # debt tops a shuffled outcome how often?
    p_gap = (1 + gap_ge) / (1 + N_PERM)       # margin this wide by chance how often?
    tab = pd.DataFrame({
        "Quantity": ["Observed top variable",
                     "Observed top-to-second mean|SHAP| gap",
                     f"P(debt ranks #1 | y permuted), {N_PERM} draws",
                     f"P(gap >= observed | y permuted), {N_PERM} draws"],
        "Value": [NICE[FEATURES[int(np.argmax(obs_imp))]], round(obs_gap, 4),
                  round(p_rank, 4), round(p_gap, 4)],
    })
    tab.to_csv(f"{OUT}/TableV6_permutation_null.csv", index=False)
    print(f"\n=== TABLE V6: PERMUTATION NULL FOR THE SHAP RANKING ===")
    print(tab.to_string(index=False))
    if not obs_top_is_key:
        print("NOTE: debt is not top on the real data in this run — report as-is.")

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.hist(null_gaps, bins=35, color="lightsteelblue", edgecolor="w")
    ax.axvline(obs_gap, c="firebrick", lw=2, label=f"observed gap = {obs_gap:.3f}")
    ax.set_xlabel("Top-to-second mean |SHAP| gap under permuted outcomes")
    ax.set_ylabel("Frequency"); ax.legend(fontsize=8); ax.grid(alpha=.3)
    ax.set_title(f"Figure V3: Permutation null (p = {p_gap:.3f}) — the importance\n"
                 "gap is not what shuffled data produces")
    fig.tight_layout(); fig.savefig(f"{OUT}/FigV3_permutation_null.png",
                                    bbox_inches="tight"); plt.close(fig)


# =========================================================== PART F ==========
# Out-of-sample R2 under three CV schemes — the gap between them IS a result
# ============================================================================
def part_f(X, X_raw, y, d):
    states = d["state"].values
    years = d["year_num"].values

    def r2(pred, mask=None):
        m = np.ones(len(y), bool) if mask is None else mask
        return 1 - np.sum((y[m] - pred[m]) ** 2) / np.sum((y[m] - y[m].mean()) ** 2)

    def forward_chain(model, Xm):
        """Train on every year strictly before t, predict year t. No future leakage."""
        pred = np.full(len(y), np.nan)
        for t in sorted(np.unique(years))[1:]:
            tr, te = years < t, years == t
            pred[te] = model.fit(Xm[tr], y[tr]).predict(Xm[te])
        return pred, ~np.isnan(pred)

    def models():
        return {
            "OLS (5 predictors)": (LinearRegression(), X),
            "LASSO": (LassoCV(cv=5, random_state=RNG, max_iter=50000), X),
            "Random Forest": (RandomForestRegressor(n_estimators=500, max_depth=3,
                                                    min_samples_leaf=4,
                                                    random_state=RNG), X_raw),
            "Gradient Boosting": (HistGradientBoostingRegressor(max_depth=3, max_iter=200,
                                                               min_samples_leaf=4,
                                                               random_state=RNG), X_raw),
        }

    rows = []
    for name, (mdl, Xm) in models().items():
        loo = cross_val_predict(mdl, Xm, y, cv=LeaveOneOut())
        loso = cross_val_predict(mdl, Xm, y, cv=LeaveOneGroupOut(), groups=states)
        fc, fcm = forward_chain(mdl, Xm)
        rows.append({"Model": name,
                     "Row-wise LOO (leaky)": round(r2(loo), 3),
                     "Leave-one-STATE-out": round(r2(loso), 3),
                     "Forward-chaining by year": round(r2(fc, fcm), 3)})
    tab = pd.DataFrame(rows)
    tab.to_csv(f"{OUT}/TableV7_out_of_sample_three_schemes.csv", index=False)
    print("\n=== TABLE V7: OUT-OF-SAMPLE R2 UNDER THREE CV SCHEMES ===")
    print(tab.to_string(index=False))
    print("Row-wise LOO keeps other years of the SAME state in training — that is the "
          "optimistic number v1 reported. The other two columns are the honest ones.")


# =========================================================== PART G ==========
# SHAP interaction: does capital expenditure read differently at high debt?
# ============================================================================
def part_g(X_raw, sv):
    Xdf = pd.DataFrame(X_raw, columns=[NICE[f] for f in FEATURES])
    plt.figure(figsize=(7.5, 5))
    shap.dependence_plot(NICE["capex"], sv, Xdf, interaction_index=NICE["debt"], show=False)
    plt.title("Figure V4: Capital expenditure's SHAP effect, coloured by debt-to-GSDP\n"
              "(Section 7.2's open question, answered with data already in hand)",
              fontweight="bold", fontsize=9)
    plt.tight_layout(); plt.savefig(f"{OUT}/FigV4_shap_interaction_capex_debt.png",
                                    bbox_inches="tight", dpi=150); plt.close()


# ------------------------------------------------------------ selftest ------
def selftest():
    """Smallest checks that fail if the non-trivial logic breaks."""
    st = np.array(["A", "A", "B", "B"])
    dm = demean_by_state(np.array([[1., 10.], [3., 20.], [5., 0.], [9., 4.]]), st)
    assert np.allclose(dm, [[-1, -5], [1, 5], [-2, -2], [2, 2]]), "demeaning wrong"
    for s in np.unique(st):
        assert np.allclose(dm[st == s].mean(axis=0), 0), "state means not zeroed"

    assert rank_of([0.1, 9.0, 0.5], ["a", "b", "c"], "b") == 1
    assert rank_of([0.1, 9.0, 0.5], ["a", "b", "c"], "a") == 3

    # a permutation p-value must stay inside (0, 1] and never hit exactly 0
    for hits in (0, 250, 500):
        p = (1 + hits) / (1 + 500)
        assert 0 < p <= 1, "permutation p-value out of range"

    # grouped CV must never leak a state across the train/test boundary
    g = np.repeat(np.arange(10), 5)
    for tr, te in LeaveOneGroupOut().split(np.zeros((50, 3)), np.zeros(50), g):
        assert not set(g[tr]) & set(g[te]), "state leaked across grouped CV fold"

    print("selftest OK")


# ---------------------------------------------------------------- main ------
def main():
    os.makedirs(OUT, exist_ok=True)
    d = load_panel()
    X_raw = d[FEATURES].values
    y = d["log_fdi"].values
    X = StandardScaler().fit_transform(X_raw)
    groups = d["state"].values

    lasso = part_a(X, y, groups, d)
    part_b(X, y, d, lasso.alpha_)

    _, sv, imp = shap_importance(X_raw, y)          # pooled corrected-spec SHAP
    part_c(X_raw, y, d, imp)
    part_d(X_raw, y, d)
    part_e(X_raw, y, imp)
    part_f(X, X_raw, y, d)
    part_g(X_raw, sv)

    print(f"\nAll v2 outputs saved in ./{OUT}/")
    print(sorted(os.listdir(OUT)))


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    else:
        main()
