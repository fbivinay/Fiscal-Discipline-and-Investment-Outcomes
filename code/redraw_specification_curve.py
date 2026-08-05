# -*- coding: utf-8 -*-
"""
Redraw Figure 24 so its lower panel shows both inference methods.

The published figure plotted cluster-robust p-values against a 5 per cent line
and said only "the p-value" in the caption. Section 6.7 now reports that those
rates overstate the evidence, and gives the wild cluster bootstrap rates
instead, so a figure showing only the cluster-robust series contradicts the text
that introduces it. Both are plotted here, on the same sorted ordering, which is
the honest picture: the coefficients are unchanged and the significance is not.

Requires bootstrap_specification_curve.py to have been run.

Run:  python redraw_specification_curve.py
      python redraw_specification_curve.py --selftest
"""
import hashlib
import os
import re
import shutil
import sys

import matplotlib
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt

DOCX = "paper/Fiscal_Discipline_and_Investment_Outcomes.docx"
DIAG = "results/diagnostics"
TEX = "paper/latex/figures"
CURVE = f"{DIAG}/TableS2_specification_curve.csv"
BOOT = f"{DIAG}/TableS2b_specification_curve_bootstrap.csv"
KEY = ["estimator", "covid", "controls", "dep", "dropped_state"]


def merged():
    if not os.path.exists(BOOT):
        sys.exit("run bootstrap_specification_curve.py first")
    old, new = pd.read_csv(CURVE), pd.read_csv(BOOT)
    m = old.merge(new[KEY + ["debt_p_bootstrap"]], on=KEY, how="left")
    if m.debt_p_bootstrap.isna().any():
        sys.exit("bootstrap file does not cover every specification")
    return m


def build():
    sc = merged().sort_values("debt_coef").reset_index(drop=True)
    fig, ax = plt.subplots(2, 1, figsize=(10, 7.4), sharex=True,
                           gridspec_kw={"height_ratios": [3, 2]})
    for est, c in [("Pooled", "steelblue"), ("FE", "darkorange")]:
        s = sc[sc.estimator == est].reset_index(drop=True)
        ax[0].scatter(range(len(s)), s.debt_coef, s=14, c=c, label=f"{est} ({len(s)} specs)")
        ax[1].scatter(range(len(s)), s.debt_p, s=12, c=c, marker="o",
                      alpha=.45, edgecolors="none")
        ax[1].scatter(range(len(s)), s.debt_p_bootstrap, s=16, c=c, marker="^",
                      edgecolors="none")
    ax[0].axhline(0, c="k", lw=1)
    ax[0].set_ylabel("Debt-to-GSDP coefficient")
    ax[0].legend(fontsize=8)
    ax[0].grid(alpha=.3)
    ax[0].set_title("Specification curve: debt coefficient across every defensible "
                    "modelling choice\n(estimator, COVID year, controls, transform, "
                    "leave-one-state-out)", fontsize=10)
    ax[1].axhline(.05, ls=":", c="firebrick", lw=1)
    ax[1].set_ylabel("p-value")
    ax[1].set_xlabel("Specification, sorted by coefficient")
    ax[1].grid(alpha=.3)
    h = [plt.Line2D([], [], marker="o", ls="", c="grey", alpha=.5, label="cluster-robust"),
         plt.Line2D([], [], marker="^", ls="", c="grey", label="wild cluster bootstrap")]
    ax[1].legend(handles=h, fontsize=8, loc="upper left")
    fig.tight_layout()
    fig.savefig(f"{DIAG}/FigS1_specification_curve.png", bbox_inches="tight")
    plt.close(fig)
    shutil.copyfile(f"{DIAG}/FigS1_specification_curve.png", f"{TEX}/fig24.png")

    for est in ["Pooled", "FE"]:
        s = sc[sc.estimator == est]
        sign = s.debt_coef < 0 if est == "Pooled" else s.debt_coef > 0
        print(f"  {est:<7} {len(s):>3} specs   cluster p<.05 "
              f"{100*(sign & (s.debt_p < .05)).mean():.0f}%   bootstrap p<.05 "
              f"{100*(sign & (s.debt_p_bootstrap < .05)).mean():.0f}%")


def embed():
    import docx
    from docx.oxml.ns import qn
    from docx.text.paragraph import Paragraph
    doc = docx.Document(DOCX)
    prev = None
    for ch in doc.element.body.iterchildren():
        if ch.tag != qn("w:p"):
            continue
        for rid in re.findall(r'r:embed="(rId\d+)"', ch.xml):
            prev = rid
        if Paragraph(ch, doc).text.strip().startswith("Figure 24.") and prev:
            doc.part.related_parts[prev]._blob = open(
                f"{DIAG}/FigS1_specification_curve.png", "rb").read()
            doc.save(DOCX)
            print(f"  Figure 24 -> {prev} replaced")
            return
    sys.exit("Figure 24 not found")


def selftest():
    """The redraw must not touch the coefficients, only add a second p-value series."""
    m = merged()
    assert len(m) == 132, f"expected 132 specifications, got {len(m)}"
    assert m.debt_p_bootstrap.between(0, 1).all()
    pooled = m[m.estimator == "Pooled"]
    assert (pooled.debt_coef < 0).all(), "pooled coefficients should all be negative"
    # the bootstrap is the more conservative of the two, spec by spec, on average
    share_c = (pooled.debt_p < .05).mean()
    share_b = (pooled.debt_p_bootstrap < .05).mean()
    print(f"  pooled significant: cluster {share_c:.0%}, bootstrap {share_b:.0%}")
    assert share_b < share_c, "bootstrap should not be less conservative here"
    print("  self-test passed")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    else:
        build()
        embed()
