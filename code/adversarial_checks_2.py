"""
============================================================================
ADVERSARIAL CHECKS, SECOND PASS
Fiscal Discipline & FDI in Indian States
============================================================================
Follow-ups to the regional confound found by adversarial_checks.py. If region
absorbs the pooled debt coefficient, the question is how far that reaches into
the rest of the paper. It reaches most of it.

  6  The machine-learning branch was never shown a regional indicator. Given
     one, LASSO promotes a western-region term above debt (+0.699 against
     -0.679). SHAP is unmoved, debt staying first at 1.006 against 1.029.
  7  The Mundlak between-state coefficient reverses from -0.256 to +0.151
     with region in the equation, though the two dimensions stay
     distinguishable at p = 0.026.
  8  The rank correlation falls from -0.842 (p = 0.002) to -0.285 (p = 0.425)
     once regional means are removed from both series.

Region is time-invariant within a state, which is the property that made
urbanisation unusable in Section 5.2. That defends the machine-learning
results and does not defend the pooled regression or the rank correlation.
Section 7.4 reports all of it.

Run:  python code/adversarial_checks_2.py
============================================================================
"""

import sys, warnings
warnings.filterwarnings("ignore")
import numpy as np, pandas as pd, statsmodels.api as sm
from sklearn.linear_model import LassoCV
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GroupKFold
from sklearn.preprocessing import StandardScaler
from scipy import stats
import shap
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

RNG = 42
d = pd.read_csv('data/processed/MASTER_PANEL_DATASET.csv')
d.columns = ["state","year","year_num","fd","fd_amt","debt","debt_amt","otr","otr_amt","capex",
             "capex_amt","rd","rd_amt","fdi","gsdp","growth","log_fdi","log_gsdp","covid",
             "post_covid","literacy","urban","rank_in_year"]
d = d.dropna(subset=["log_fdi"]).reset_index(drop=True)
REGION = {"Maharashtra":"West","Gujarat":"West","Karnataka":"South","Tamil Nadu":"South",
          "Telangana":"South","Haryana":"North","Rajasthan":"North","Uttar Pradesh":"North",
          "Jharkhand":"East","West Bengal":"East"}
d["region"] = d.state.map(REGION)
rdum = pd.get_dummies(d.region, prefix="reg", drop_first=True).astype(float)
d = pd.concat([d, rdum], axis=1)
RC = list(rdum.columns)

F5 = ["fd","debt","otr","capex","covid"]
N5 = ["Fiscal Deficit","Debt-to-GSDP","Own Tax Revenue","Capital Expenditure","COVID year"]
y = d.log_fdi.values
groups = d.state.values

print("=" * 76)
print("ATTACK 6: GIVE THE MACHINE-LEARNING BRANCH REGION AND SEE WHAT IT PREFERS")
print("=" * 76)
print("   Section 6.6 rests on LASSO, Elastic Net and SHAP all ranking debt first.")
print("   None of them was ever shown a regional indicator.")
print()
for lbl, feats, names in [
    ("five fiscal regressors (as published)", F5, N5),
    ("fiscal regressors + region", F5 + RC, N5 + [c.replace("reg_", "") for c in RC]),
]:
    X = d[feats].values
    Xs = StandardScaler().fit_transform(X)
    cv = list(GroupKFold(n_splits=10).split(Xs, y, groups))
    la = LassoCV(cv=cv, random_state=RNG, max_iter=100000).fit(Xs, y)
    rf = RandomForestRegressor(n_estimators=1000, max_depth=3, min_samples_leaf=4,
                               random_state=RNG, oob_score=True).fit(X, y)
    imp = np.abs(shap.TreeExplainer(rf).shap_values(X)).mean(0)
    print("   --- %s ---" % lbl)
    print("      LASSO, by absolute standardised coefficient:")
    for n, c in sorted(zip(names, la.coef_), key=lambda t: -abs(t[1]))[:4]:
        print("         %-22s %+.4f" % (n, c))
    print("      SHAP, by mean |SHAP|   (forest out-of-bag R2 = %.3f):" % rf.oob_score_)
    for n, v in sorted(zip(names, imp), key=lambda t: -t[1])[:4]:
        print("         %-22s %.4f" % (n, v))
    print()

print("=" * 76)
print("ATTACK 7: DOES THE MUNDLAK SPLIT SURVIVE REGION?")
print("=" * 76)
z = d.copy()
for v in ["fd","debt","otr","capex"]:
    z[v+"_m"] = z.groupby("state")[v].transform("mean")
    z[v+"_d"] = z[v] - z[v+"_m"]
cols = [v+"_d" for v in ["fd","debt","otr","capex"]] + [v+"_m" for v in ["fd","debt","otr","capex"]] + ["covid"]
for lbl, regs in [("as published", cols), ("+ region", cols + RC)]:
    m = sm.OLS(z.log_fdi, sm.add_constant(z[regs])).fit(cov_type="cluster", cov_kwds={"groups": z.state})
    t = m.t_test("debt_d - debt_m = 0")
    print("   %-14s within %+.3f  between %+.3f  equality p %.6f"
          % (lbl, m.params.debt_d, m.params.debt_m, float(np.ravel(t.pvalue)[0])))

print()
print("=" * 76)
print("ATTACK 8: IS THE RANK CORRELATION A REGIONAL ORDERING TOO?")
print("=" * 76)
g = d.groupby("state").agg(debt=("debt","mean"), fdi=("fdi","sum"))
g["region"] = g.index.map(REGION)
r, p = stats.spearmanr(g.debt, g.fdi)
print("   debt vs FDI across the ten states:            rho %+.3f  p %.4f" % (r, p))
gd = g.assign(debt_w=g.debt - g.groupby("region").debt.transform("mean"),
              fdi_w=np.log(g.fdi) - g.groupby("region").fdi.transform(lambda s: np.log(s).mean()))
r2, p2 = stats.spearmanr(gd.debt_w, gd.fdi_w)
print("   after removing regional means from both:      rho %+.3f  p %.4f" % (r2, p2))
print("   (this is the rank version of the Section 7.4 regression)")
