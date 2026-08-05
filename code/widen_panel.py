"""
============================================================================
WIDENING THE SAMPLE BELOW THE TOP TEN
Fiscal Discipline & FDI in Indian States
============================================================================
PURPOSE
  Section 7.4 reports that ten states across four regions cannot separate a
  fiscal signal from a regional one, and Section 8 names a wider panel as the
  most valuable extension. This script asks how far the available data can
  take that, and answers two different questions.

  1. THE DESIGN QUESTION. With ten states, 71 per cent of the cross-state
     variance in debt lies between regions, which is why region absorbs the
     coefficient. Does that improve with 28 states? This needs only FC-16 and
     settles whether a wider study is worth running.

  2. AN EXPLORATORY CROSS-SECTION. FC-16 covers 28 states; DPIIT reports
     cumulative FDI for all of them. That supports a 28-state cross-section,
     which is not the paper's design and is not a replacement for it.

WHAT CANNOT BE DONE
  The annual panel cannot be widened. DPIIT publishes state-wise FDI below the
  top ten only as a cumulative total since October 2019, with no year-by-year
  breakdown, so there is no annual outcome for the other eighteen states.

  Nor is there a market-size control. FC-16 reports every fiscal series as a
  share of GSDP and never the level, and no GSDP series for the wider set is
  in this repository. FDI in levels is strongly size-driven, so the
  cross-sectional coefficients below are not comparable with the paper's,
  which do carry that control (Table 23c). They are reported as indicative of
  whether the design question is worth pursuing, not as estimates.

Run:  python code/widen_panel.py
============================================================================
"""
import re
import subprocess
import sys
import warnings

warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats

FC16 = "Vol2-Annexures.pdf"
DPIIT = "4128971a6c7fd4a7653ca9e648a5f34b.pdf"
WINDOW = ["2019-20", "2020-21", "2021-22", "2022-23", "2023-24"]

ROWS = ["All States", "Non-NEH States", "NEH States", "Andhra Pradesh", "Arunachal Pradesh",
        "Assam", "Bihar", "Chhattisgarh", "Goa", "Gujarat", "Haryana", "Himachal Pradesh",
        "Jharkhand", "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur",
        "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim",
        "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal"]
AGG = {"All States", "Non-NEH States", "NEH States"}

REGION = {
    "Maharashtra": "West", "Gujarat": "West", "Goa": "West", "Rajasthan": "North",
    "Madhya Pradesh": "Central", "Chhattisgarh": "Central",
    "Karnataka": "South", "Tamil Nadu": "South", "Telangana": "South",
    "Andhra Pradesh": "South", "Kerala": "South",
    "Haryana": "North", "Punjab": "North", "Himachal Pradesh": "North",
    "Uttarakhand": "North", "Uttar Pradesh": "North",
    "Bihar": "East", "Jharkhand": "East", "Odisha": "East", "West Bengal": "East",
    "Assam": "Northeast", "Arunachal Pradesh": "Northeast", "Manipur": "Northeast",
    "Meghalaya": "Northeast", "Mizoram": "Northeast", "Nagaland": "Northeast",
    "Sikkim": "Northeast", "Tripura": "Northeast",
}

PAPER_TEN = ["Maharashtra", "Uttar Pradesh", "Telangana", "Gujarat", "Karnataka",
             "Jharkhand", "Tamil Nadu", "Haryana", "Rajasthan", "West Bengal"]


def text_of(path):
    return subprocess.run(["pdftotext", "-q", path, "-"],
                          capture_output=True).stdout.decode("utf-8", "replace")


def fc16_blocks(text):
    rows = []
    for m in re.finditer(r"((?:19|20)\d\d-\d\d)\s+((?:-?\d+\.?\d*\s+){20,})", text):
        v = m.group(2).split()
        if len(v) == len(ROWS):
            rows.append((m.group(1), v))
    blocks, cur, seen = [], {}, set()
    for yr, v in rows:
        if yr in seen:
            blocks.append(cur); cur, seen = {}, set()
        cur[yr] = v; seen.add(yr)
    if cur:
        blocks.append(cur)
    return blocks


def series(block, name):
    """Mean over the paper's window, per state."""
    out = {}
    for s in ROWS:
        if s in AGG:
            continue
        i = ROWS.index(s)
        vals = [float(block[y][i]) for y in WINDOW if y in block]
        if vals:
            out[s] = np.mean(vals)
    return pd.Series(out, name=name)


def dpiit_totals(text):
    i = text.find("STATE-WISE FDI EQUITY INFLOW FROM OCTOBER 2019")
    blk = text[i:i + 3000]
    nm = re.search(r"1 MAHARASHTRA.*?State Not Indicated", blk, re.S).group(0).replace("\n", " ")
    names = [s.strip().title() for _, s in re.findall(
        r"(\d{1,2})\s+([A-Za-z][A-Za-z \-\.]+?)(?=\s+\d{1,2}\s+[A-Za-z]|\s*\Z)", nm)]
    inr = re.search(r"\(In USD Million\)(.*?)% age out of total", blk, re.S).group(1)
    vals = [float(v.replace(",", "")) for v in re.findall(r"[\d,]+\.\d+", inr)]
    return dict(zip(names, vals))


def main():
    fc = fc16_blocks(text_of(FC16))
    debt = series(fc[2], "debt")
    fd = series(fc[0], "fd")
    otr = series(fc[3], "otr")
    dp = dpiit_totals(text_of(DPIIT))

    df = pd.concat([fd, debt, otr], axis=1)
    df["region"] = df.index.map(REGION)
    df["fdi"] = [dp.get(s, np.nan) for s in df.index]
    df = df.dropna(subset=["fdi", "region"])
    df["log_fdi"] = np.log(df.fdi.clip(lower=0.01))
    df["in_paper"] = df.index.isin(PAPER_TEN)

    print("=" * 76)
    print("SAMPLE")
    print("=" * 76)
    print("   states with both FC-16 fiscal data and a DPIIT total: %d" % len(df))
    print("   of which in the paper's sample: %d" % df.in_paper.sum())
    print(df.groupby("region").size().to_string())

    print()
    print("=" * 76)
    print("1. THE DESIGN QUESTION: CAN DEBT BE SEPARATED FROM REGION?")
    print("=" * 76)
    for lbl, sub in [("paper's ten states", df[df.in_paper]), ("all %d states" % len(df), df)]:
        tot = sub.debt.var(ddof=0)
        wth = sub.groupby("region").debt.transform(lambda s: s - s.mean()).var(ddof=0)
        print("   %-22s between-region share of debt variance: %4.0f%%   (within %4.0f%%)"
              % (lbl, 100 * (1 - wth / tot), 100 * wth / tot))
        print("   %-22s regions represented: %d, states per region: %.1f"
              % ("", sub.region.nunique(), len(sub) / sub.region.nunique()))

    print()
    print("=" * 76)
    print("2. EXPLORATORY CROSS-SECTION (no market-size control; see the header)")
    print("=" * 76)
    rd = pd.get_dummies(df, columns=["region"], drop_first=True, dtype=float)
    rc = [c for c in rd.columns if c.startswith("region_")]
    for lbl, regs in [("debt only", ["debt"]),
                      ("debt + fiscal deficit + own tax revenue", ["debt", "fd", "otr"]),
                      ("debt + region", ["debt"] + rc),
                      ("debt + fiscals + region", ["debt", "fd", "otr"] + rc)]:
        m = sm.OLS(rd.log_fdi, sm.add_constant(rd[regs])).fit()
        print("   %-42s debt %+7.4f  p %.4f  R2 %.3f"
              % (lbl, m.params.debt, m.pvalues.debt, m.rsquared))
    r, p = stats.spearmanr(df.debt, df.fdi)
    print("   %-42s rho  %+7.3f  p %.4f" % ("rank correlation, debt vs FDI", r, p))

    print()
    print("=" * 76)
    print("3. WITHIN-REGION VARIATION, THE THING THE TEN-STATE PANEL LACKS")
    print("=" * 76)
    print("   %-12s %6s %8s %8s" % ("region", "states", "debt sd", "debt range"))
    for reg, sub in df.groupby("region"):
        print("   %-12s %6d %8.2f %8.1f" % (reg, len(sub), sub.debt.std(),
                                            sub.debt.max() - sub.debt.min()))
    ten = df[df.in_paper]
    print()
    print("   mean within-region debt spread, paper's ten: %.1f points"
          % ten.groupby("region").debt.apply(lambda s: s.max() - s.min()).mean())
    print("   mean within-region debt spread, all states:  %.1f points"
          % df.groupby("region").debt.apply(lambda s: s.max() - s.min()).mean())


if __name__ == "__main__":
    main()
