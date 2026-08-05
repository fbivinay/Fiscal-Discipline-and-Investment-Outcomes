# -*- coding: utf-8 -*-
"""
Why does dropping Uttar Pradesh double the fiscal deficit coefficient in the
growth model?

Table 23a reports the leave-one-state-out sensitivity for Model 2. Dropping
Uttar Pradesh moves the fiscal deficit coefficient from -2.172 (p = 0.031) to
-5.078 (p = 0.001). No censoring story applies: Uttar Pradesh's growth series is
complete for all five years. The paper reported the sensitivity without an
explanation, which is the right thing to do in the absence of one, but the
decomposition below is available from the published data and gives one.

Method. By Frisch-Waugh-Lovell the fixed-effects slope on the fiscal deficit is

    beta = sum_i (x_i * y_i) / sum_i (x_i ^ 2)

where x and y are the fiscal deficit and growth after both have been residualised
on the entity dummies and the other regressors. Every state-year cell therefore
contributes one term to the numerator and one to the denominator, and the
contributions are additive, so each state's exact influence on beta can be read
off rather than inferred. A state with a large denominator share is a state the
slope is estimated from; a state whose numerator share has the opposite sign to
the whole is a state pulling the slope toward zero.

Run:  python diagnose_up_sensitivity.py
      python diagnose_up_sensitivity.py --selftest
"""
import os
import sys
import warnings

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

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
    return df


def fe_slope(d, target="fd", dep="growth", regs=REGS):
    """FWL residualisation. Returns beta and the per-cell numerator/denominator terms."""
    others = [r for r in regs if r != target]
    Z = np.hstack([pd.get_dummies(d["state"]).to_numpy(float),
                   d[others].to_numpy(float)])
    P = Z @ np.linalg.pinv(Z.T @ Z) @ Z.T
    M = np.eye(len(d)) - P
    x = M @ d[target].to_numpy(float)
    y = M @ d[dep].to_numpy(float)
    return (x * y).sum() / (x * x).sum(), x * y, x * x


def report(d, label, target="fd", dep="growth"):
    beta, num, den = fe_slope(d, target, dep)
    t = pd.DataFrame({"state": d["state"].to_numpy(), "num": num, "den": den})
    g = t.groupby("state").sum()
    g["den_share"] = 100 * g.den / g.den.sum()
    g["num_share"] = 100 * g.num / g.num.sum()
    g["own_slope"] = g.num / g.den
    g = g.sort_values("den_share", ascending=False)
    print(f"\n  {label}: beta = {beta:+.3f}")
    print(f"  {'state':<16}{'leverage %':>12}{'numerator %':>14}{'own slope':>12}")
    for s, r in g.iterrows():
        print(f"  {s:<16}{r.den_share:>11.1f}%{r.num_share:>13.1f}%{r.own_slope:>12.2f}")
    return beta, g


def main():
    df = load()
    d = df.dropna(subset=["growth"]).reset_index(drop=True)

    print("=" * 70)
    print("THE FISCAL DEFICIT SLOPE IN MODEL 2, DECOMPOSED BY STATE")
    print("=" * 70)
    beta_all, g = report(d, "all ten states")
    beta_no_up, _ = report(d[d.state != "Uttar Pradesh"].reset_index(drop=True),
                           "dropping Uttar Pradesh")
    print(f"\n  the published sensitivity: {beta_all:+.3f} -> {beta_no_up:+.3f}")

    up = g.loc["Uttar Pradesh"]
    print(f"\n  Uttar Pradesh carries {up.den_share:.1f} per cent of the leverage, "
          f"the largest of any state,")
    print(f"  and its own within-state slope is {up.own_slope:+.2f} against "
          f"{beta_all:+.2f} for the panel.")

    print()
    print("=" * 70)
    print("IS IT THE SURPLUS YEAR, OR THE WHOLE STATE?")
    print("=" * 70)
    print("  Uttar Pradesh is the only state recording a fiscal surplus in any year.")
    upd = df[df.state == "Uttar Pradesh"][["year", "fd", "growth"]]
    for _, r in upd.iterrows():
        print(f"    {r.year}   deficit {r.fd:>5.1f}   growth {r.growth:>6.2f}")
    for label, mask in [
        ("dropping only the FY2019-20 surplus cell",
         ~((d.state == "Uttar Pradesh") & (d.year == "FY2019-20"))),
        # keeping only the surplus cell leaves Uttar Pradesh one observation, which
        # its own entity dummy absorbs exactly, so this must equal dropping the state
        ("keeping only the surplus cell (= dropping the state)",
         ~((d.state == "Uttar Pradesh") & (d.year != "FY2019-20")))]:
        b = fe_slope(d[mask].reset_index(drop=True))[0]
        print(f"  {label:<44} beta = {b:+.3f}")

    print()
    print("=" * 70)
    print("HOW UNUSUAL IS THAT LEVERAGE?")
    print("=" * 70)
    spread = df.groupby("state").fd.agg(["min", "max", "std"])
    spread["range"] = spread["max"] - spread["min"]
    print(f"  {'state':<16}{'min':>7}{'max':>7}{'range':>8}{'leverage %':>13}")
    for s, r in spread.sort_values("range", ascending=False).iterrows():
        print(f"  {s:<16}{r['min']:>7.1f}{r['max']:>7.1f}{r['range']:>8.1f}"
              f"{g.loc[s, 'den_share']:>12.1f}%")

    print()
    print("=" * 70)
    print("DOES THE SAME STATE DOMINATE MODEL 1?")
    print("=" * 70)
    d1 = df.dropna(subset=["log_fdi"]).reset_index(drop=True)
    _, g1 = report(d1, "FDI model, all states with an observation", dep="log_fdi")


def selftest():
    """The decomposition must reproduce the fixed-effects coefficient exactly."""
    from linearmodels.panel import PanelOLS
    import statsmodels.api as sm
    df = load()
    d = df.dropna(subset=["growth"]).reset_index(drop=True)
    beta, num, den = fe_slope(d)
    ref = PanelOLS(d.set_index(["state", "year_num"])["growth"],
                   sm.add_constant(d.set_index(["state", "year_num"])[REGS]),
                   entity_effects=True).fit()
    print(f"  linearmodels {ref.params['fd']:+.9f}   decomposition {beta:+.9f}")
    assert abs(ref.params["fd"] - beta) < 1e-8, "FWL decomposition does not match PanelOLS"

    # the per-cell terms must sum back to the same slope
    assert abs(num.sum() / den.sum() - beta) < 1e-12, "per-cell terms do not sum to beta"

    # and dropping a state via the decomposition must match a refit on that subsample
    sub = d[d.state != "Uttar Pradesh"].reset_index(drop=True)
    b2, _, _ = fe_slope(sub)
    ref2 = PanelOLS(sub.set_index(["state", "year_num"])["growth"],
                    sm.add_constant(sub.set_index(["state", "year_num"])[REGS]),
                    entity_effects=True).fit()
    print(f"  dropping UP: linearmodels {ref2.params['fd']:+.9f}   here {b2:+.9f}")
    assert abs(ref2.params["fd"] - b2) < 1e-8, "leave-one-out refit does not match"
    print("  self-test passed")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    else:
        main()
