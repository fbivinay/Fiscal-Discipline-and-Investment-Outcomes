"""
============================================================================
ADVERSARIAL CHECKS
Fiscal Discipline & FDI in Indian States
============================================================================
Attacks on the paper's central claim that the manuscript did not otherwise
test. Four of the five leave it standing; the first does not, and Section 7.4
reports what it found.

  1  Regional confounding. The low-debt states are western and southern, the
     high-debt ones northern and eastern. Region absorbs the debt coefficient
     entirely. Ten states across four regions cannot separate the two.
  2  Influence. Four of the 48 observations exceed the 4/n Cook's distance
     threshold, all of them Jharkhand's near-zero FDI years. Dropping them
     leaves the coefficient at -0.148, p < 0.0001.
  3  Functional form. A rank-rank specification, which assumes nothing about
     the shape, gives -0.586 (p = 0.011); Huber regression gives -0.156. The
     result is not an artefact of the log.
  4  Effective sample size. Dropping any one, two, three or four of the ten
     states leaves the between-state coefficient negative in all 385 subsets.
  5  Label permutation. Reassigning debt across states at random reproduces
     the observed rank correlation in 0.2 per cent of 20,000 draws.

Run:  python code/adversarial_checks.py
============================================================================
"""
# -*- coding: utf-8 -*-
"""Adversarial pass: attacks the paper has not tested, not consistency checks."""
import sys, warnings, itertools
warnings.filterwarnings("ignore")
import numpy as np, pandas as pd, statsmodels.api as sm
from scipy import stats
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

d = pd.read_csv('data/processed/MASTER_PANEL_DATASET.csv')
d.columns = ["state","year","year_num","fd","fd_amt","debt","debt_amt","otr","otr_amt","capex",
             "capex_amt","rd","rd_amt","fdi","gsdp","growth","log_fdi","log_gsdp","covid",
             "post_covid","literacy","urban","rank_in_year"]
d = d.dropna(subset=["log_fdi"]).copy()
BASE = ["fd","debt","otr","capex","covid","literacy","urban"]

REGION = {"Maharashtra":"West","Gujarat":"West",
          "Karnataka":"South","Tamil Nadu":"South","Telangana":"South",
          "Haryana":"North","Rajasthan":"North","Uttar Pradesh":"North",
          "Jharkhand":"East","West Bengal":"East"}
d["region"] = d.state.map(REGION)


def pooled(data, regs, dep="log_fdi", label=""):
    X = sm.add_constant(data[regs])
    m = sm.OLS(data[dep], X).fit(cov_type="cluster", cov_kwds={"groups": data.state})
    if label:
        print("   %-46s debt %+7.4f  p %.4f  R2 %.3f"
              % (label, m.params.get("debt", np.nan), m.pvalues.get("debt", np.nan), m.rsquared))
    return m


print("=" * 76)
print("ATTACK 1: IS 'LOW DEBT' JUST 'WESTERN AND SOUTHERN'?")
print("=" * 76)
g = d.groupby("state").agg(debt=("debt","mean"), fdi=("fdi","sum"))
g["region"] = g.index.map(REGION)
print(g.sort_values("debt").to_string())
print()
print("   mean debt by region:")
print(g.groupby("region").debt.mean().sort_values().to_string())
pooled(d, BASE, label="baseline")
rd_ = pd.get_dummies(d, columns=["region"], drop_first=True, dtype=float)
rcols = [c for c in rd_.columns if c.startswith("region_")]
pooled(rd_, BASE + rcols, label="+ region fixed effects (4 regions)")
south = d.assign(south=(d.region.isin(["South","West"])).astype(float))
pooled(south, BASE + ["south"], label="+ a single South/West indicator")

print()
print("=" * 76)
print("ATTACK 2: HOW MUCH DOES ONE OBSERVATION CARRY?")
print("=" * 76)
X = sm.add_constant(d[BASE])
ols = sm.OLS(d.log_fdi, X).fit()
infl = ols.get_influence()
cd = infl.cooks_distance[0]
lev = infl.hat_matrix_diag
d2 = d.assign(cooks=cd, leverage=lev)
print("   highest Cook's distance (4/n = %.3f is the usual flag):" % (4 / len(d)))
print(d2.nlargest(6, "cooks")[["state","year","fdi","debt","cooks","leverage"]].to_string(index=False))
print()
print("   observations above the 4/n threshold: %d of %d" % ((cd > 4 / len(d)).sum(), len(d)))
keep = d2[cd <= 4 / len(d)]
pooled(keep, BASE, label="dropping every high-influence observation")

print()
print("=" * 76)
print("ATTACK 3: IS IT THE LOG, OR THE DATA?")
print("=" * 76)
print("   FDI range: %.0f to %.0f crore, ratio %.0fx"
      % (d.fdi.min(), d.fdi.max(), d.fdi.max() / d.fdi.min()))
d3 = d.assign(rank_fdi=d.fdi.rank(), rank_debt=d.debt.rank())
pooled(d3, BASE, label="log FDI (as published)")
m = sm.OLS(d3.rank_fdi, sm.add_constant(d3[["fd","rank_debt","otr","capex","covid","literacy","urban"]])
           ).fit(cov_type="cluster", cov_kwds={"groups": d3.state})
print("   %-46s rank-debt %+7.4f p %.4f" % ("rank-rank (fully non-parametric)",
                                            m.params.rank_debt, m.pvalues.rank_debt))
from statsmodels.robust.robust_linear_model import RLM
rob = RLM(d.log_fdi, sm.add_constant(d[BASE])).fit()
print("   %-46s debt %+7.4f  (Huber, robust to outliers)" % ("robust regression", rob.params.debt))

print()
print("=" * 76)
print("ATTACK 4: THE EFFECTIVE SAMPLE IS TEN, NOT FORTY-EIGHT")
print("=" * 76)
gm = d.groupby("state").mean(numeric_only=True)
for k in range(1, 5):
    combos = list(itertools.combinations(gm.index, k))
    signs = []
    for c in combos:
        sub = gm.drop(list(c))
        if len(sub) - 3 < 1:
            continue
        m = sm.OLS(sub.log_fdi, sm.add_constant(sub[["debt"]])).fit()
        signs.append(m.params.debt)
    if signs:
        print("   dropping any %d of the ten states: debt stays negative in %d of %d subsets"
              % (k, sum(1 for s in signs if s < 0), len(signs)))

print()
print("=" * 76)
print("ATTACK 5: WOULD A RANDOM RANKING DO AS WELL?")
print("=" * 76)
fdi5 = d.groupby("state").fdi.sum()
obs = stats.spearmanr(gm.debt, fdi5).statistic
rng = np.random.default_rng(42)
draws = [stats.spearmanr(rng.permutation(gm.debt.values), fdi5.values).statistic for _ in range(20000)]
p = np.mean(np.array(draws) <= obs)
print("   observed rho(debt, FDI) = %+.3f" % obs)
print("   share of 20,000 random relabellings at least this negative: %.4f" % p)
