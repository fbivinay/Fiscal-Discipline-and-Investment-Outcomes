"""
============================================================================
MACHINE LEARNING VALIDATION (CORRECTED SPECIFICATION) — LASSO + SHAP
Fiscal Discipline & FDI in Indian States (companion to analysis.py)
============================================================================
This is ml_validation.py with the correction described in Section 5.2 of the
paper applied. The original run carried the two time-invariant Census
controls (literacy, urbanisation) into the machine-learning stage and SHAP
ranked urbanisation first, at mean |SHAP| = 1.30 against 0.25 for debt.
Urbanisation is constant within a state across all five years, so the forest
was using it as a near-unique fingerprint for state identity and re-learning
the fixed effect through the back door rather than any fiscal relationship.

The corrected specification below restricts every ML method to the same FIVE
time-varying regressors the fixed-effects econometric model uses. Both runs
are kept in the repository: ml_validation.py reproduces the flawed 7-variable
outputs in results/ml/lasso_shap_original_7var/, this file reproduces the
5-variable outputs in results/ml/lasso_shap_corrected_5var/ that Section 6.6
reports.

  PART A  LASSO / Elastic Net  — regularized LINEAR variable selection
  PART B  Random Forest + SHAP — NON-LINEAR explainable-AI importance
  PART C  Honest out-of-sample comparison (leave-one-out CV)

Framed as VALIDATION of the panel regressions, not replacement — the
statistically correct posture at n = 48. See ml_validation_v2.py for the
panel-aware extensions (state-blocked CV, within specification,
permutation null).

Run:  python ml_validation_corrected.py
Outputs -> ./results/ml/lasso_shap_corrected_5var/
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
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import ElasticNetCV, LassoCV, LinearRegression, lasso_path
from sklearn.model_selection import LeaveOneOut, cross_val_predict
from sklearn.preprocessing import StandardScaler

OUT = os.environ.get("OUT_DIR", "results/ml/lasso_shap_corrected_5var")
os.makedirs(OUT, exist_ok=True)
plt.rcParams.update({"figure.dpi": 150, "font.size": 9, "axes.titleweight": "bold",
                     "figure.facecolor": "white"})
RNG = 42  # reproducibility

DATA_CANDIDATES = ["data/processed/MASTER_PANEL_DATASET.csv",
                   "MASTER_PANEL_FINAL.csv"]

# ---------------------------------------------------------------- data ----
path = next((p for p in DATA_CANDIDATES if os.path.exists(p)), None)
if path is None:
    sys.exit(f"None of {DATA_CANDIDATES} found. Run from the project root.")
df = pd.read_csv(path)
df.columns = ["state", "year", "year_num", "fd", "fd_amt", "debt", "debt_amt",
              "otr", "otr_amt", "capex", "capex_amt", "rd", "rd_amt",
              "fdi", "gsdp", "growth", "log_fdi", "log_gsdp",
              "covid", "post_covid", "literacy", "urban", "rank_in_year"]
d = df.dropna(subset=["log_fdi"]).reset_index(drop=True)   # 48 rows (UP FY20/21 out)

# THE CORRECTION: literacy and urbanization are excluded. Both are Census 2011
# values, constant within a state across all five years, and a tree model can
# read either as a state identifier. Same regressor set as the FE model.
FEATURES = ["fd", "debt", "otr", "capex", "covid"]
NICE = {"fd": "Fiscal Deficit", "debt": "Debt-to-GSDP", "otr": "Own Tax Revenue",
        "capex": "Capital Expenditure", "covid": "COVID year"}
X_raw = d[FEATURES].values
y = d["log_fdi"].values
scaler = StandardScaler().fit(X_raw)
X = scaler.transform(X_raw)                                # standardized for LASSO
print(f"Data: {len(d)} observations, {len(FEATURES)} predictors, target = log(FDI)")

# ============================================================== PART A =====
# LASSO & ELASTIC NET — which variables SURVIVE selection?
# ============================================================================
loo = LeaveOneOut()
lasso = LassoCV(cv=loo, random_state=RNG, max_iter=50000).fit(X, y)
enet = ElasticNetCV(cv=loo, l1_ratio=[.3, .5, .7, .9, 1], random_state=RNG,
                    max_iter=50000).fit(X, y)

tabA = pd.DataFrame({
    "Variable": [NICE[f] for f in FEATURES],
    "LASSO_coef (standardized)": lasso.coef_.round(4),
    "LASSO_selected": np.where(np.abs(lasso.coef_) > 1e-8, "YES", "no"),
    "ElasticNet_coef": enet.coef_.round(4),
    "ElasticNet_selected": np.where(np.abs(enet.coef_) > 1e-8, "YES", "no"),
}).sort_values("LASSO_coef (standardized)", key=lambda s: s.abs(), ascending=False)
tabA.to_csv(f"{OUT}/TableM1_lasso_selection_corrected.csv", index=False)
print("\n=== TABLE M1: LASSO / ELASTIC NET SELECTION (corrected, 5 regressors) ===")
print(tabA.to_string(index=False))
print(f"LASSO alpha (LOO-CV): {lasso.alpha_:.4f} | ElasticNet alpha: {enet.alpha_:.4f}, "
      f"l1_ratio: {enet.l1_ratio_}")

# --- stability: refit LASSO leaving each STATE out (10 refits) --------------
sel_count = {f: 0 for f in FEATURES}
for s in d["state"].unique():
    mask = (d["state"] != s).values
    li = LassoCV(cv=LeaveOneOut(), random_state=RNG, max_iter=50000).fit(X[mask], y[mask])
    for f, c in zip(FEATURES, li.coef_):
        if abs(c) > 1e-8:
            sel_count[f] += 1
COL = "Times_selected_out_of_10_state-leave-out_refits"
stab = pd.DataFrame({"Variable": [NICE[f] for f in FEATURES],
                     COL: [sel_count[f] for f in FEATURES]}
                    ).sort_values(COL, ascending=False)
stab.to_csv(f"{OUT}/TableM2_lasso_stability_corrected.csv", index=False)
print("\n=== TABLE M2: LASSO SELECTION STABILITY (leave-one-state-out) ===")
print(stab.to_string(index=False))

# --- Figure M1: LASSO coefficient path --------------------------------------
alphas, coefs, _ = lasso_path(X, y, alphas=np.logspace(-3, 0.5, 100))
fig, ax = plt.subplots(figsize=(9, 5.5))
for i, f in enumerate(FEATURES):
    ax.plot(np.log10(alphas), coefs[i], lw=1.8, label=NICE[f])
ax.axvline(np.log10(lasso.alpha_), ls="--", c="k", lw=1, label="Chosen alpha (LOO-CV)")
ax.set_xlabel("log10(regularization strength alpha)  ->  stronger shrinkage")
ax.set_ylabel("Standardized coefficient")
ax.set_title("LASSO Coefficient Paths — which predictors survive shrinkage?")
ax.legend(fontsize=8); ax.grid(alpha=.3)
fig.tight_layout(); fig.savefig(f"{OUT}/FigM1_lasso_path_corrected.png",
                                bbox_inches="tight"); plt.close(fig)

# --- Figure M2: selected coefficients bar -----------------------------------
fig, ax = plt.subplots(figsize=(8, 4.5))
order = np.argsort(np.abs(lasso.coef_))
cols = ["seagreen" if c > 0 else "firebrick" for c in lasso.coef_[order]]
ax.barh([NICE[FEATURES[i]] for i in order], lasso.coef_[order], color=cols)
ax.axvline(0, c="k", lw=.8)
ax.set_xlabel("LASSO coefficient (standardized; 0 = eliminated)")
ax.set_title("LASSO — surviving predictors of log(FDI)")
ax.grid(axis="x", alpha=.3)
fig.tight_layout(); fig.savefig(f"{OUT}/FigM2_lasso_coefs_corrected.png",
                                bbox_inches="tight"); plt.close(fig)

# ============================================================== PART B =====
# RANDOM FOREST + SHAP — non-linear explainable-AI importance
# ============================================================================
# depth 3 / leaf 4 are deliberate: a deeper forest with 48 training rows can
# memorise individual states rather than learn a fiscal relationship.
rf = RandomForestRegressor(n_estimators=1000, max_depth=3, min_samples_leaf=4,
                           oob_score=True, random_state=RNG).fit(X_raw, y)
with open(f"{OUT}/oob_r2.txt", "w", encoding="utf-8") as f:
    f.write(f"RF OOB R2 (5-var restricted model): {rf.oob_score_:.4f}\n")
print(f"\nRF out-of-bag R2 (5-var restricted model): {rf.oob_score_:.4f}")

explainer = shap.TreeExplainer(rf)
sv = explainer.shap_values(X_raw, check_additivity=False)

meanabs = pd.DataFrame({"Variable": [NICE[f] for f in FEATURES],
                        "Mean_|SHAP|": np.abs(sv).mean(axis=0).round(4)}
                       ).sort_values("Mean_|SHAP|", ascending=False)
meanabs.to_csv(f"{OUT}/TableM3_shap_importance_corrected.csv", index=False)
print("\n=== TABLE M3: SHAP IMPORTANCE (mean |SHAP|, Random Forest) ===")
print(meanabs.to_string(index=False))

Xdf = pd.DataFrame(X_raw, columns=[NICE[f] for f in FEATURES])

# --- Figure M3: SHAP beeswarm summary ---------------------------------------
plt.figure(figsize=(8, 5))
shap.summary_plot(sv, Xdf, show=False, plot_size=None)
plt.title("SHAP Summary — direction & strength of each predictor",
          fontweight="bold", fontsize=10)
plt.tight_layout(); plt.savefig(f"{OUT}/FigM3_shap_beeswarm_corrected.png",
                                bbox_inches="tight", dpi=150); plt.close()

# --- Figure M4: SHAP bar -----------------------------------------------------
plt.figure(figsize=(7.5, 4.5))
shap.summary_plot(sv, Xdf, plot_type="bar", show=False, plot_size=None)
plt.title("SHAP Importance Ranking (mean |SHAP value|)",
          fontweight="bold", fontsize=10)
plt.tight_layout(); plt.savefig(f"{OUT}/FigM4_shap_bar_corrected.png",
                                bbox_inches="tight", dpi=150); plt.close()

# --- Figure M5: SHAP dependence for the top fiscal variable (debt) ----------
plt.figure(figsize=(7.5, 5))
shap.dependence_plot("Debt-to-GSDP", sv, Xdf, interaction_index=None, show=False)
plt.title("SHAP Dependence — Debt-to-GSDP vs its effect on predicted log(FDI)",
          fontweight="bold", fontsize=10)
plt.tight_layout(); plt.savefig(f"{OUT}/FigM5_shap_dependence_debt_corrected.png",
                                bbox_inches="tight", dpi=150); plt.close()

# ============================================================== PART C =====
# HONEST OUT-OF-SAMPLE COMPARISON (leave-one-out CV)
# ============================================================================
# NOTE: row-wise LOO leaves the held-out state's other four years in the
# training sample, so these figures are optimistic. ml_validation_v2.py
# reports the state-blocked and forward-chaining alternatives alongside them.
def loo_r2(model, Xm):
    pred = cross_val_predict(model, Xm, y, cv=LeaveOneOut())
    return 1 - np.sum((y - pred) ** 2) / np.sum((y - y.mean()) ** 2)


r2_ols = loo_r2(LinearRegression(), X)
r2_lasso = loo_r2(LassoCV(cv=5, random_state=RNG, max_iter=50000), X)
r2_rf = loo_r2(RandomForestRegressor(n_estimators=500, max_depth=3,
                                     min_samples_leaf=4, random_state=RNG), X_raw)
tabC = pd.DataFrame({"Model": ["OLS (5 predictors)", "LASSO (selected subset)",
                               "Random Forest"],
                     "LOO-CV out-of-sample R2": [round(r2_ols, 3), round(r2_lasso, 3),
                                                 round(r2_rf, 3)]})
tabC.to_csv(f"{OUT}/TableM4_out_of_sample_corrected.csv", index=False)
print("\n=== TABLE M4: OUT-OF-SAMPLE (LOO-CV) R-SQUARED ===")
print(tabC.to_string(index=False))

print(f"\nAll corrected ML outputs saved in ./{OUT}/")
print(sorted(os.listdir(OUT)))
