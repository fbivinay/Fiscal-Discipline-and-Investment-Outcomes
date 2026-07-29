"""
============================================================================
FISCAL DISCIPLINE & FDI IN INDIAN STATES — COMPLETE DISSERTATION ANALYSIS
============================================================================
Runs the entire analysis from MASTER_PANEL_FINAL.csv:
  PART 1  Descriptive statistics (Table 1)
  PART 2  Charts & figures (Figures 1-7)
  PART 3  Ranking analysis (Table 2)
  PART 4  Panel regressions — Model 1 (FDI) & Model 2 (GSDP growth) (Tables 3-4)
  PART 5  Diagnostics (VIF, correlation matrix) (Table 5)
  PART 6  Robustness checks (Table 6)
All outputs saved to ./analysis_results/
Author: [Your name] | PG Dissertation
============================================================================
"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from linearmodels.panel import PanelOLS, PooledOLS
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor

# ---------------------------------------------------------------- setup ----
OUT = "results/econometrics"
os.makedirs(OUT, exist_ok=True)
plt.rcParams.update({"figure.dpi": 150, "font.size": 9, "axes.titlesize": 10,
                     "axes.titleweight": "bold", "figure.facecolor": "white"})
sns.set_palette("tab10")

# 1. LOAD DATA — rename long labelled headers to short analysis names
df = pd.read_csv("data/processed/MASTER_PANEL_DATASET.csv")
df.columns = ["state","year","year_num","fd","fd_amt","debt","debt_amt",
              "otr","otr_amt","capex","capex_amt","rd","rd_amt",
              "fdi","gsdp","growth","log_fdi","log_gsdp",
              "covid","post_covid","literacy","urban","rank_in_year"]
print(f"Loaded: {df.shape[0]} rows x {df.shape[1]} cols")
print(f"Missing FDI cells (UP FY20/21, correct): {df['fdi'].isna().sum()}")

STATES = df["state"].unique().tolist()
YEARS  = sorted(df["year"].unique().tolist())

# ================================================================ PART 1 ===
# DESCRIPTIVE STATISTICS  (Table 1)
# ============================================================================
desc_vars = {"fd":"Fiscal Deficit (% GSDP)","debt":"Debt (% GSDP)",
             "otr":"Own Tax Revenue (% GSDP)","capex":"Capital Expenditure (% GSDP)",
             "rd":"Revenue Deficit (% GSDP)","fdi":"FDI (Rs crore)",
             "growth":"GSDP Growth (%)"}
t1 = df[list(desc_vars)].describe().T[["count","mean","std","min","50%","max"]]
t1.columns = ["N","Mean","Std Dev","Min","Median","Max"]
t1.index = [desc_vars[v] for v in t1.index]
t1 = t1.round(2)
t1.to_csv(f"{OUT}/Table1_descriptive_statistics.csv")
print("\n=== TABLE 1: DESCRIPTIVE STATISTICS ===")
print(t1.to_string())

# ================================================================ PART 2 ===
# FIGURES 1-7
# ============================================================================
# --- Figure 1: fiscal variable trends (4 small multiples) -------------------
fig, axes = plt.subplots(2, 2, figsize=(12, 8))
specs = [("fd","Fiscal Deficit (% of GSDP) — lower is better"),
         ("debt","Debt (% of GSDP) — lower is better"),
         ("otr","Own Tax Revenue (% of GSDP) — higher is better"),
         ("capex","Capital Expenditure (% of GSDP) — higher is better")]
for ax,(v,title) in zip(axes.flat, specs):
    for s in STATES:
        d = df[df.state==s]
        ax.plot(d.year, d[v], marker="o", ms=3, lw=1.2, label=s)
    ax.set_title(title); ax.tick_params(axis="x", rotation=30); ax.grid(alpha=.3)
axes[0,0].legend(fontsize=6.5, ncol=2, loc="upper right")
fig.suptitle("Figure 1: Fiscal Discipline Indicators, Top-10 FDI States (FY2019-20 to FY2023-24)",
             fontsize=12, fontweight="bold")
fig.tight_layout(); fig.savefig(f"{OUT}/Fig1_fiscal_trends.png", bbox_inches="tight"); plt.close(fig)

# --- Figure 2: FDI 5-year totals bar --------------------------------------
tot = df.groupby("state")["fdi"].sum().sort_values(ascending=True)
fig, ax = plt.subplots(figsize=(9, 5))
bars = ax.barh(tot.index, tot.values/1000, color=sns.color_palette("viridis", 10))
ax.set_xlabel("Total FDI FY2019-20 to FY2023-24 (Rs '000 crore)")
ax.set_title("Figure 2: Five-Year FDI Equity Inflows by State\n(UP total understated — recorded only from FY2021-22)")
for b, v in zip(bars, tot.values):
    ax.text(b.get_width()+3, b.get_y()+b.get_height()/2, f"{v/1000:,.0f}", va="center", fontsize=8)
ax.grid(axis="x", alpha=.3)
fig.tight_layout(); fig.savefig(f"{OUT}/Fig2_fdi_totals.png", bbox_inches="tight"); plt.close(fig)

# --- Figure 3: scatter — avg deficit vs avg log FDI ------------------------
avg = df.groupby("state").agg(fd=("fd","mean"), debt=("debt","mean"),
                              logf=("log_fdi","mean")).reset_index()
fig, ax = plt.subplots(figsize=(8, 6))
ax.scatter(avg.fd, avg.logf, s=90, c=avg.debt, cmap="RdYlGn_r", edgecolor="k", zorder=3)
for _, r in avg.iterrows():
    ax.annotate(r.state, (r.fd, r.logf), textcoords="offset points", xytext=(6, 4), fontsize=8)
m, b = np.polyfit(avg.fd, avg.logf, 1)
xs = np.linspace(avg.fd.min(), avg.fd.max(), 50)
ax.plot(xs, m*xs+b, "--", color="gray", lw=1.5, label=f"Fitted line (slope = {m:.2f})")
cb = plt.colorbar(ax.collections[0], ax=ax); cb.set_label("Avg Debt (% GSDP)")
ax.set_xlabel("Average Fiscal Deficit (% of GSDP)"); ax.set_ylabel("Average log(FDI)")
ax.set_title("Figure 3: Fiscal Deficit vs FDI (5-year averages)\nColour = debt level; note Jharkhand as outlier")
ax.legend(); ax.grid(alpha=.3)
fig.tight_layout(); fig.savefig(f"{OUT}/Fig3_deficit_vs_fdi_scatter.png", bbox_inches="tight"); plt.close(fig)

# --- Figure 4: discipline rank evolution heatmap ---------------------------
piv = df.pivot(index="state", columns="year", values="rank_in_year")
piv = piv.loc[piv.mean(axis=1).sort_values().index]
fig, ax = plt.subplots(figsize=(8, 5.5))
sns.heatmap(piv, annot=True, fmt=".0f", cmap="RdYlGn_r", cbar_kws={"label":"Rank (1 = best)"},
            linewidths=.5, ax=ax, vmin=1, vmax=10)
ax.set_title("Figure 4: Fiscal Discipline Rank by Year (1 = most disciplined)")
ax.set_xlabel(""); ax.set_ylabel("")
fig.tight_layout(); fig.savefig(f"{OUT}/Fig4_rank_heatmap.png", bbox_inches="tight"); plt.close(fig)

# --- Figure 5: COVID impact on deficits -------------------------------------
fig, ax = plt.subplots(figsize=(9, 5))
means = df.groupby("year")[["fd","debt"]].mean()
ax.plot(means.index, means.fd, marker="o", lw=2, label="Avg Fiscal Deficit (% GSDP)")
ax2 = ax.twinx()
ax2.plot(means.index, means.debt, marker="s", lw=2, color="firebrick", label="Avg Debt (% GSDP)")
ax.axvspan(0.5, 1.5, color="orange", alpha=.15)
ax.text(1, ax.get_ylim()[1]*0.97, "COVID year", ha="center", fontsize=9, color="darkorange")
ax.set_ylabel("Fiscal Deficit (% GSDP)"); ax2.set_ylabel("Debt (% GSDP)", color="firebrick")
ax.set_title("Figure 5: The COVID Fiscal Shock — 10-State Averages")
ax.tick_params(axis="x", rotation=20); ax.grid(alpha=.3)
h1,l1 = ax.get_legend_handles_labels(); h2,l2 = ax2.get_legend_handles_labels()
ax.legend(h1+h2, l1+l2, loc="center right")
fig.tight_layout(); fig.savefig(f"{OUT}/Fig5_covid_shock.png", bbox_inches="tight"); plt.close(fig)

# --- Figure 6: FDI year-wise lines (log scale) ------------------------------
fig, ax = plt.subplots(figsize=(9.5, 5.5))
for s in STATES:
    d = df[df.state==s].dropna(subset=["fdi"])
    ax.plot(d.year, d.fdi, marker="o", ms=4, lw=1.4, label=s)
ax.set_yscale("log")
ax.set_ylabel("FDI (Rs crore, log scale)")
ax.set_title("Figure 6: Year-wise FDI Inflows (log scale)\nNote Jharkhand's collapse after FY2020-21")
ax.tick_params(axis="x", rotation=20); ax.grid(alpha=.3, which="both")
ax.legend(fontsize=7, ncol=2)
fig.tight_layout(); fig.savefig(f"{OUT}/Fig6_fdi_yearwise.png", bbox_inches="tight"); plt.close(fig)

# --- Figure 7: GSDP growth by state -----------------------------------------
fig, ax = plt.subplots(figsize=(9.5, 5.5))
for s in STATES:
    d = df[df.state==s]
    ax.plot(d.year, d.growth, marker="o", ms=4, lw=1.4, label=s)
ax.axhline(0, color="k", lw=.8)
ax.set_ylabel("Nominal GSDP growth (% per year)")
ax.set_title("Figure 7: GSDP Growth — COVID Dip and Recovery")
ax.tick_params(axis="x", rotation=20); ax.grid(alpha=.3); ax.legend(fontsize=7, ncol=2)
fig.tight_layout(); fig.savefig(f"{OUT}/Fig7_gsdp_growth.png", bbox_inches="tight"); plt.close(fig)
print("\nFigures 1-7 saved.")

# ================================================================ PART 3 ===
# RANKING TABLE  (Table 2)
# ============================================================================
t2 = piv.copy()
t2["5yr Avg Rank"] = t2.mean(axis=1).round(2)
t2.to_csv(f"{OUT}/Table2_discipline_ranks_by_year.csv")
print("\n=== TABLE 2: DISCIPLINE RANK BY YEAR ===")
print(t2.to_string())

# ================================================================ PART 4 ===
# PANEL REGRESSIONS  (Tables 3-4)
# ============================================================================
pdf = df.set_index(["state","year_num"])
def run_models(data, label, dv):
    """FE + Driscoll-Kraay, and Pooled OLS with Census controls."""
    d = data.dropna(subset=[dv])
    # Fixed effects, Driscoll-Kraay (kernel) SEs
    fe = PanelOLS.from_formula(
        f"{dv} ~ 1 + fd + debt + otr + capex + covid + EntityEffects",
        data=d).fit(cov_type="kernel")
    # Pooled OLS with time-invariant controls, clustered by state
    po = PooledOLS.from_formula(
        f"{dv} ~ 1 + fd + debt + otr + capex + covid + literacy + urban",
        data=d).fit(cov_type="clustered", cluster_entity=True)
    return fe, po, len(d)

fe1, po1, n1 = run_models(pdf, "Model 1", "log_fdi")
fe2, po2, n2 = run_models(pdf, "Model 2", "growth")

def tidy(res, name):
    out = pd.DataFrame({"coef":res.params, "std_err":res.std_errors,
                        "t":res.tstats, "p":res.pvalues}).round(4)
    out.columns = pd.MultiIndex.from_product([[name], out.columns])
    return out

t3 = pd.concat([tidy(fe1,"FE + Driscoll-Kraay"), tidy(po1,"Pooled OLS + controls")], axis=1)
t3.to_csv(f"{OUT}/Table3_Model1_FDI_regressions.csv")
t4 = pd.concat([tidy(fe2,"FE + Driscoll-Kraay"), tidy(po2,"Pooled OLS + controls")], axis=1)
t4.to_csv(f"{OUT}/Table4_Model2_growth_regressions.csv")

with open(f"{OUT}/regression_full_output.txt","w") as f:
    f.write("="*70+"\nMODEL 1: log(FDI) — FIXED EFFECTS, DRISCOLL-KRAAY SEs"
            f"  (n={n1})\n"+"="*70+"\n"+str(fe1)+"\n\n")
    f.write("="*70+"\nMODEL 1: log(FDI) — POOLED OLS + CENSUS CONTROLS\n"+"="*70+"\n"+str(po1)+"\n\n")
    f.write("="*70+"\nMODEL 2: GSDP GROWTH — FIXED EFFECTS, DRISCOLL-KRAAY SEs"
            f"  (n={n2})\n"+"="*70+"\n"+str(fe2)+"\n\n")
    f.write("="*70+"\nMODEL 2: GSDP GROWTH — POOLED OLS + CENSUS CONTROLS\n"+"="*70+"\n"+str(po2)+"\n")

print("\n=== TABLE 3: MODEL 1 (log FDI) — FE + Driscoll-Kraay ===")
print(tidy(fe1,"FE").to_string())
print(f"Within R-squared: {fe1.rsquared_within:.3f} | n = {n1}")
print("\n=== TABLE 4: MODEL 2 (GSDP growth) — FE + Driscoll-Kraay ===")
print(tidy(fe2,"FE").to_string())
print(f"Within R-squared: {fe2.rsquared_within:.3f} | n = {n2}")

# ================================================================ PART 5 ===
# DIAGNOSTICS  (Table 5): VIF + correlation matrix
# ============================================================================
X = df[["fd","debt","otr","capex"]].dropna()
Xc = sm.add_constant(X)
vif = pd.DataFrame({"Variable":["const"]+list(X.columns),
                    "VIF":[variance_inflation_factor(Xc.values,i) for i in range(Xc.shape[1])]}).round(2)
vif.to_csv(f"{OUT}/Table5_VIF.csv", index=False)
corr = df[["fd","debt","otr","capex","log_fdi","growth"]].corr().round(3)
corr.to_csv(f"{OUT}/Table5b_correlation_matrix.csv")
fig, ax = plt.subplots(figsize=(6.5, 5))
sns.heatmap(corr, annot=True, cmap="coolwarm", center=0, ax=ax, fmt=".2f")
ax.set_title("Correlation Matrix (pooled, n=48-50)")
fig.tight_layout(); fig.savefig(f"{OUT}/Fig8_correlation_heatmap.png", bbox_inches="tight"); plt.close(fig)
print("\n=== TABLE 5: VIF (multicollinearity check; <10 acceptable) ===")
print(vif.to_string(index=False))

# ================================================================ PART 6 ===
# ROBUSTNESS CHECKS  (Table 6): coefficient stability across subsamples
# ============================================================================
checks = {
    "Baseline (all data)":            pdf,
    "Excl. COVID year (FY2020-21)":   pdf[pdf.covid==0],
    "Excl. Jharkhand":                pdf.drop("Jharkhand", level="state"),
    "Excl. Uttar Pradesh":            pdf.drop("Uttar Pradesh", level="state"),
}
rows = []
for name, d in checks.items():
    dd = d.dropna(subset=["log_fdi"])
    # drop covid dummy if the subsample has no variation in it (e.g. COVID year excluded)
    covid_term = " + covid" if dd["covid"].nunique() > 1 else ""
    r = PanelOLS.from_formula(f"log_fdi ~ 1 + fd + debt + otr + capex{covid_term} + EntityEffects",
                              data=dd).fit(cov_type="kernel")
    rows.append({"Specification":name, "n":dd.shape[0],
                 "fd_coef":round(r.params["fd"],3),   "fd_p":round(r.pvalues["fd"],3),
                 "debt_coef":round(r.params["debt"],3),"debt_p":round(r.pvalues["debt"],3),
                 "otr_coef":round(r.params["otr"],3), "otr_p":round(r.pvalues["otr"],3),
                 "capex_coef":round(r.params["capex"],3),"capex_p":round(r.pvalues["capex"],3)})
t6 = pd.DataFrame(rows)
t6.to_csv(f"{OUT}/Table6_robustness_Model1.csv", index=False)
print("\n=== TABLE 6: ROBUSTNESS — MODEL 1 COEFFICIENTS ACROSS SUBSAMPLES ===")
print(t6.to_string(index=False))

print(f"\nAll outputs saved in ./{OUT}/")
print("Files:", sorted(os.listdir(OUT)))
