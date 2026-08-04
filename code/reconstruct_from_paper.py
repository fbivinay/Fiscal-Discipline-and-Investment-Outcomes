"""
============================================================================
RECONSTRUCTION FROM THE PUBLISHED TABLES
Fiscal Discipline & FDI in Indian States
============================================================================
PURPOSE
  Rebuild the 50-row analysis panel using nothing but the tables printed in
  Section 4 of the manuscript, then re-estimate the paper's headline results
  and check them against the numbers printed in Sections 6 and 7.

  This is a stronger reproducibility claim than "the code and data are in the
  repository". It says a reader who has only the PDF can recover every
  estimate. If this script passes, no intermediate file has to be taken on
  trust: the published inputs determine the published outputs.

WHAT IT READS
  Only paper/Fiscal_Discipline_and_Investment_Outcomes.docx, and only these
  tables from it:
      Table 2   fiscal deficit, per cent of GSDP
      Table 4   outstanding liabilities (debt), per cent of GSDP
      Table 6   own tax revenue, per cent of GSDP
      Table 8   capital expenditure (derived), per cent of GSDP
      Table 11  FDI equity inflows, Rupees crore
      Table 12  GSDP, Rupees crore
      Table 13  GSDP growth, per cent per annum
      Table 14  literacy and urbanisation, Census 2011

  It never opens data/processed/MASTER_PANEL_DATASET.csv. That is the point.

WHAT IT CHECKS
  Table 17  descriptive statistics
  Table 19  Model 1, fixed effects and pooled OLS
  Table 20  Model 2, fixed effects and pooled OLS
  Table 21  variance inflation factors
  Table 35  Mundlak within/between split and the between estimator

Run:  python code/reconstruct_from_paper.py
Exit code 0 if every published figure is recovered, 1 otherwise.
============================================================================
"""
import re
import sys
import warnings

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
import docx
import statsmodels.api as sm
from docx.oxml.ns import qn
from docx.table import Table
from docx.text.paragraph import Paragraph
from linearmodels.panel import BetweenOLS, PanelOLS

DOCX = "paper/Fiscal_Discipline_and_Investment_Outcomes.docx"
YEARS = ["FY2019-20", "FY2020-21", "FY2021-22", "FY2022-23", "FY2023-24"]
TOL = 0.0006          # published figures are rounded to 4 dp
failures = []


# ------------------------------------------------------------------ reading --
def published_tables(path):
    """Return {'Table 2': [[cell, ...], ...]} keyed by the caption above each table."""
    d = docx.Document(path)
    out, caption = {}, None
    for child in d.element.body.iterchildren():
        if child.tag == qn("w:p"):
            m = re.match(r"(Table \d+[a-z]?)\.", Paragraph(child, d).text.strip())
            if m:
                caption = m.group(1)
        elif child.tag == qn("w:tbl"):
            if caption is not None:
                out[caption] = [[c.text.strip() for c in r.cells]
                                for r in Table(child, d).rows]
                caption = None
    return out


def num(x):
    """Cell -> float, or NaN for the Uttar Pradesh 'NA (combined ...)' entries."""
    x = x.replace(",", "").replace("−", "-").strip()
    try:
        return float(x)
    except ValueError:
        return np.nan


def wide_to_long(rows, value_name, year_cols=5):
    """First column is the state; the next `year_cols` are the fiscal years."""
    recs = []
    for r in rows[1:]:
        for j, yr in enumerate(YEARS[:year_cols], start=1):
            recs.append({"state": r[0], "year": yr, value_name: num(r[j])})
    return pd.DataFrame(recs)


# ------------------------------------------------------- build the panel -----
T = published_tables(DOCX)
missing = [k for k in ("Table 2", "Table 4", "Table 6", "Table 8", "Table 11",
                       "Table 12", "Table 13", "Table 14") if k not in T]
if missing:
    sys.exit("could not locate published tables: %s" % missing)

panel = wide_to_long(T["Table 2"], "fd")
for cap, name in [("Table 4", "debt"), ("Table 6", "otr"),
                  ("Table 8", "capex"), ("Table 11", "fdi")]:
    panel = panel.merge(wide_to_long(T[cap], name), on=["state", "year"])

# GSDP: Table 12 carries six columns, 2018-19 first, so year-on-year growth is
# available for FY2019-20 as well.
g = {r[0]: [num(v) for v in r[1:7]] for r in T["Table 12"][1:]}
panel["gsdp"] = [g[s][YEARS.index(y) + 1] for s, y in zip(panel.state, panel.year)]

# Growth is taken from Table 13 rather than recomputed from Table 12. The paper
# publishes it to two decimals and estimates Model 2 on those rounded values, so
# recomputing at full precision from the GSDP levels moves the Model 2
# coefficients in the fourth decimal. Table 13 is itself one of the Section 4
# tables, so this stays within the rules of the exercise; the recomputation is
# kept below as a cross-check that the two published series agree.
panel = panel.merge(wide_to_long(T["Table 13"], "growth"), on=["state", "year"])
recomputed = np.array([100 * (g[s][YEARS.index(y) + 1] / g[s][YEARS.index(y)] - 1)
                       for s, y in zip(panel.state, panel.year)])
drift = np.abs(recomputed - panel.growth.values).max()
print("Table 13 growth vs recomputed from Table 12 GSDP: max divergence %.4f pp"
      % drift)
if drift > 0.02:
    failures.append("published growth series disagrees with the published GSDP levels")

cen = {r[0]: (num(r[1]), num(r[2])) for r in T["Table 14"][1:]}
panel["literacy"] = [cen[s][0] for s in panel.state]
panel["urban"] = [cen[s][1] for s in panel.state]

panel["covid"] = (panel.year == "FY2020-21").astype(float)
panel["year_num"] = [2019 + YEARS.index(y) for y in panel.year]
panel["log_fdi"] = np.log(panel.fdi)
panel = panel.sort_values(["state", "year_num"]).reset_index(drop=True)

print("reconstructed panel: %d rows, %d states, %d with a usable FDI observation"
      % (len(panel), panel.state.nunique(), panel.log_fdi.notna().sum()))

REGS = ["fd", "debt", "otr", "capex", "covid"]
POOLED = REGS + ["literacy", "urban"]


def check(label, got, want, tol=TOL):
    ok = (got is not None) and abs(got - want) <= tol
    print("   %-46s %10.4f  vs published %10.4f  %s"
          % (label, got if got is not None else float("nan"), want,
             "ok" if ok else "MISMATCH"))
    if not ok:
        failures.append(label)


def fe_fit(dep, cov="kernel", **kw):
    s = panel.dropna(subset=[dep])
    p = s.set_index(["state", "year_num"])
    return PanelOLS(p[dep], sm.add_constant(p[REGS]), entity_effects=True).fit(
        cov_type=cov, **kw)


def pooled_fit(dep):
    s = panel.dropna(subset=[dep])
    return sm.OLS(s[dep], sm.add_constant(s[POOLED])).fit(
        cov_type="cluster", cov_kwds={"groups": s.state})


# ---------------------------------------------------------- Table 17 --------
print("\nTable 17  descriptive statistics")
labels = {"Fiscal Deficit (% GSDP)": "fd", "Debt (% GSDP)": "debt",
          "Own Tax Revenue (% GSDP)": "otr", "Capital Expenditure (% GSDP)": "capex",
          "FDI (Rs crore)": "fdi", "GSDP Growth (%)": "growth"}
for row in T["Table 17"][1:]:
    if row[0] not in labels:
        continue
    col = panel[labels[row[0]]].dropna()
    check("%s mean" % row[0], round(col.mean(), 2), num(row[2]), 0.006)
    check("%s std dev" % row[0], round(col.std(), 2), num(row[3]), 0.006)

# ---------------------------------------------------------- Table 19 --------
print("\nTable 19  Model 1, log(FDI)")
fe1, po1 = fe_fit("log_fdi"), pooled_fit("log_fdi")
pub19 = {r[0]: r for r in T["Table 19"][1:]}
for v in REGS:
    check("FE %s coefficient" % v, round(float(fe1.params[v]), 4), num(pub19[v][1]))
    check("FE %s p-value" % v, round(float(fe1.pvalues[v]), 4), num(pub19[v][4]))
for v in POOLED:
    check("pooled %s coefficient" % v, round(float(po1.params[v]), 4), num(pub19[v][5]))
check("FE within R-squared", round(float(fe1.rsquared_within), 4), 0.4292)
check("poolability F", round(float(fe1.f_pooled.stat), 3), 6.741, 0.002)

# ---------------------------------------------------------- Table 20 --------
print("\nTable 20  Model 2, GSDP growth")
fe2, po2 = fe_fit("growth"), pooled_fit("growth")
pub20 = {r[0]: r for r in T["Table 20"][1:]}
for v in REGS:
    check("FE %s coefficient" % v, round(float(fe2.params[v]), 4), num(pub20[v][1]))
for v in POOLED:
    check("pooled %s coefficient" % v, round(float(po2.params[v]), 4), num(pub20[v][5]))

# ---------------------------------------------------------- Table 21 --------
print("\nTable 21  variance inflation factors")
from statsmodels.stats.outliers_influence import variance_inflation_factor
X = sm.add_constant(panel[["fd", "debt", "otr", "capex"]])
pub21 = {r[0]: num(r[1]) for r in T["Table 21"][1:]}
for i, c in enumerate(X.columns):
    if c in pub21:
        check("VIF %s" % c, round(variance_inflation_factor(X.values, i), 2),
              pub21[c], 0.006)

# ---------------------------------------------------------- Table 35 --------
print("\nTable 35  Mundlak split and the between estimator")
z = panel.dropna(subset=["log_fdi"]).copy()
for v in ["fd", "debt", "otr", "capex"]:
    z[v + "_m"] = z.groupby("state")[v].transform("mean")
    z[v + "_d"] = z[v] - z[v + "_m"]
cols = ([v + "_d" for v in ["fd", "debt", "otr", "capex"]]
        + [v + "_m" for v in ["fd", "debt", "otr", "capex"]] + ["covid"])
mk = sm.OLS(z.log_fdi, sm.add_constant(z[cols])).fit(
    cov_type="cluster", cov_kwds={"groups": z.state})
pub35 = {r[0]: r for r in T["Table 35"][1:]}
check("Mundlak within-state debt", round(float(mk.params.debt_d), 3),
      num(pub35["Mundlak: within-state deviation"][1]), 0.0006)
check("Mundlak state-mean debt", round(float(mk.params.debt_m), 3),
      num(pub35["Mundlak: state-mean term"][1]), 0.0006)
p = z.set_index(["state", "year_num"])
be = BetweenOLS(p.log_fdi, sm.add_constant(p[["fd", "debt", "otr", "capex"]])).fit()
check("between estimator debt", round(float(be.params.debt), 3),
      num(pub35["Between estimator, ten state means"][1]), 0.0006)

# ------------------------------------------------------------------ verdict --
print("\n" + "=" * 70)
if failures:
    print("FAILED to recover %d published figure(s):" % len(failures))
    for f in failures:
        print("   " + f)
    sys.exit(1)
print("PASS - every published figure checked was recovered from the paper's own "
      "tables alone.")
print("=" * 70)
