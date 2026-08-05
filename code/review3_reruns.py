# -*- coding: utf-8 -*-
"""Reruns the third review requires: Mundlak time control, the leaking bootstrap,
Model 2's lag, and the capital-outlay refit."""
import io, warnings, itertools
warnings.filterwarnings("ignore")
import numpy as np, pandas as pd, statsmodels.api as sm
from sklearn.linear_model import LassoCV, LinearRegression, Lasso
from sklearn.ensemble import RandomForestRegressor, HistGradientBoostingRegressor
from sklearn.model_selection import LeaveOneGroupOut, GroupKFold, cross_val_predict
from sklearn.preprocessing import StandardScaler
from linearmodels.panel import PanelOLS

RNG = 42
d = pd.read_csv('data/processed/MASTER_PANEL_DATASET.csv')
d.columns = ["state","year","year_num","fd","fd_amt","debt","debt_amt","otr","otr_amt","capex",
             "capex_amt","rd","rd_amt","fdi","gsdp","growth","log_fdi","log_gsdp","covid",
             "post_covid","literacy","urban","rank_in_year"]
o = io.open("reruns3_out.txt", "w", encoding="utf-8")
def w(s=""):
    o.write(s + "\n"); o.flush(); print(s, flush=True)

dd = d.dropna(subset=["log_fdi"]).copy()
for v in ["fd","debt","otr","capex"]:
    dd[v+"_m"] = dd.groupby("state")[v].transform("mean")
    dd[v+"_d"] = dd[v] - dd[v+"_m"]
COLS = [v+"_d" for v in ["fd","debt","otr","capex"]] + [v+"_m" for v in ["fd","debt","otr","capex"]]
YD = pd.get_dummies(dd.year, prefix="y", drop_first=True).astype(float)
dd = pd.concat([dd, YD], axis=1)
YC = list(YD.columns)

w("=" * 74)
w("ITEM 1: WHAT TIME CONTROL DOES THE MUNDLAK SPECIFICATION USE?")
w("=" * 74)
for lbl, regs in [("COVID dummy (as published)", COLS + ["covid"]),
                  ("full year fixed effects", COLS + YC)]:
    m = sm.OLS(dd.log_fdi, sm.add_constant(dd[regs])).fit(
        cov_type="cluster", cov_kwds={"groups": dd.state})
    t = m.t_test("debt_d - debt_m = 0")
    w("   %-30s within %+.3f  between %+.3f  equality p %.6f"
      % (lbl, m.params.debt_d, m.params.debt_m, float(np.ravel(t.pvalue)[0])))
w("   (the published Table 35 matches the first line, so it uses the COVID dummy)")

w("")
w("=" * 74)
w("ITEM 3: TABLE 31a's BOOTSTRAP LEAKS DUPLICATED STATES ACROSS FOLDS")
w("=" * 74)
F = ["fd","debt","otr","capex","covid"]
X, y, groups = dd[F].values, dd.log_fdi.values, dd.state.values
Xs = StandardScaler().fit_transform(X)
alpha = LassoCV(cv=list(GroupKFold(n_splits=10).split(Xs, y, groups)),
                random_state=RNG, max_iter=100000).fit(Xs, y).alpha_
def r2(a, b): return 1 - np.sum((a-b)**2)/np.sum((a-a.mean())**2)
MODELS = {"OLS": (LinearRegression(), X),
          "LASSO": (Lasso(alpha=alpha, max_iter=100000), Xs),
          "RandomForest": (RandomForestRegressor(n_estimators=500, max_depth=3,
                                                 min_samples_leaf=4, random_state=RNG), X),
          "GradBoost": (HistGradientBoostingRegressor(max_depth=3, max_iter=200,
                                                      min_samples_leaf=4, random_state=RNG), X)}
point = {k: r2(y, cross_val_predict(m, Xm, y, cv=LeaveOneGroupOut(), groups=groups))
         for k, (m, Xm) in MODELS.items()}
uniq = np.unique(groups)
rng = np.random.default_rng(RNG)
# jackknife: leave one state out entirely, no duplication, no leakage
jack = {k: [] for k in MODELS}
for s in uniq:
    keep = groups != s
    g2 = groups[keep]
    for k, (m, Xm) in MODELS.items():
        Xk = (Xm[keep])
        pred = cross_val_predict(m, Xk, y[keep], cv=LeaveOneGroupOut(), groups=g2)
        jack[k].append(r2(y[keep], pred))
w("   %-14s %10s %26s" % ("model", "point", "jackknife over the ten states"))
for k in MODELS:
    a = np.array(jack[k])
    w("   %-14s %10.3f   min %6.3f  median %6.3f  max %6.3f"
      % (k, point[k], a.min(), np.median(a), a.max()))
w("   a jackknife holds each state out once and never duplicates one,")
w("   so no state can appear in both the training and the test fold")

w("")
w("=" * 74)
w("ITEM 2: A LAG FOR MODEL 2, WHICH WAS ONLY EVER APPLIED TO MODEL 1")
w("=" * 74)
z = d.sort_values(["state","year_num"]).copy()
z["debt_l1"] = z.groupby("state")["debt"].shift(1)
zz = z.dropna(subset=["growth","debt_l1"])
p = zz.set_index(["state","year_num"])
for lbl, regs in [("contemporaneous debt", ["fd","debt","otr","capex","covid"]),
                  ("debt lagged one year", ["fd","debt_l1","otr","capex","covid"])]:
    m = PanelOLS(p["growth"], sm.add_constant(p[regs]), entity_effects=True).fit(
        cov_type="clustered", cluster_entity=True)
    k = "debt" if "debt" in m.params else "debt_l1"
    w("   FE, %-24s coef %+.3f  p %.4f  n %d" % (lbl, m.params[k], m.pvalues[k], m.nobs))

w("")
w("=" * 74)
w("ITEM 10: REFIT ON THE TWO YEARS WITH EXACT CAPITAL OUTLAY")
w("=" * 74)
exact = {"Maharashtra":(1.69,2.12),"Uttar Pradesh":(4.12,6.19),"Telangana":(1.37,3.02),
         "Gujarat":(1.59,2.38),"Karnataka":(2.63,2.00),"Jharkhand":(3.56,5.06),
         "Tamil Nadu":(1.67,1.56),"Haryana":(1.19,1.32),"Rajasthan":(1.46,2.28),
         "West Bengal":(1.44,1.80)}
sub = d[d.year.isin(["FY2022-23","FY2023-24"])].dropna(subset=["log_fdi"]).copy()
sub["capex_exact"] = [exact[s][0 if y == "FY2022-23" else 1] for s, y in zip(sub.state, sub.year)]
w("   subsample: %d state-years (FY2022-23 actuals and FY2023-24 revised estimates)" % len(sub))
for lbl, cx in [("derived capex", "capex"), ("exact capital outlay", "capex_exact")]:
    m = sm.OLS(sub.log_fdi, sm.add_constant(sub[["fd","debt","otr",cx,"literacy","urban"]])).fit(
        cov_type="cluster", cov_kwds={"groups": sub.state})
    w("   %-24s debt %+.3f p %.4f   capex term %+.3f p %.4f"
      % (lbl, m.params.debt, m.pvalues.debt, m.params[cx], m.pvalues[cx]))
w("   note: the FY2023-24 exact column is revised estimates, not audited actuals,")
w("   so this subsample mixes vintages and is reported as indicative only")
o.close()
print("DONE")
