# -*- coding: utf-8 -*-
"""
Figures 12 and 13: the composite discipline rank against each outcome.

Two reasons this script exists.

The first is a sign error. Both figures plot the discipline rank against an
outcome in levels, and on that pairing a better rank is a lower number, so a
state that is both disciplined and successful sits top-left and the scatter
slopes down. The published versions printed the rank-against-rank correlation
in the title instead, which carries the opposite sign, so each figure showed a
visibly downward slope over a caption reporting rho = +0.255 and +0.728. The
values here are computed from what is actually plotted.

The second is that no script produced these figures. analysis.py stops at
Figure 8, and Figures 12 and 13 existed only as PNG files, which is a gap in a
paper that claims every result is reproducible from its published tables. The
per-capita column is read out of Table 18 of the manuscript rather than
recomputed, so the figure cannot drift from the table it illustrates.

Writes to results/econometrics/ and to paper/latex/figures/.

Run:  python make_outcome_figures.py
      python make_outcome_figures.py --selftest
"""
import os
import re
import shutil
import sys

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats

DOCX = "paper/Fiscal_Discipline_and_Investment_Outcomes.docx"
OUT = "results/econometrics"
TEX = "paper/latex/figures"
DATA = "data/processed/MASTER_PANEL_DATASET.csv"
COLUMNS = ["state", "year", "year_num", "fd", "fd_amt", "debt", "debt_amt", "otr",
           "otr_amt", "capex", "capex_amt", "rd", "rd_amt", "fdi", "gsdp", "growth",
           "log_fdi", "log_gsdp", "covid", "post_covid", "literacy", "urban",
           "rank_in_year"]


def composite_rank():
    d = pd.read_csv(DATA)
    d.columns = COLUMNS
    g = d.groupby("state").agg(fd=("fd", "mean"), debt=("debt", "mean"),
                               otr=("otr", "mean"), capex=("capex", "mean"),
                               fdi=("fdi", "sum"))
    rank = ((g.fd.rank() + g.debt.rank() + g.otr.rank(ascending=False)
             + g.capex.rank(ascending=False)) / 4).rank()
    return rank, g.fdi


def per_capita_from_table18():
    """Read the per-capita column out of the manuscript so the figure and the
    table cannot disagree."""
    import docx
    from docx.oxml.ns import qn
    from docx.table import Table
    from docx.text.paragraph import Paragraph
    doc = docx.Document(DOCX)
    cap = None
    for ch in doc.element.body.iterchildren():
        if ch.tag == qn("w:p"):
            m = re.match(r"(Table \d+[a-z]?)\.", Paragraph(ch, doc).text.strip())
            if m:
                cap = m.group(1)
        elif ch.tag == qn("w:tbl"):
            if cap == "Table 18":
                rows = [[c.text.strip() for c in r.cells] for r in Table(ch, doc).rows]
                return pd.Series({r[0]: float(r[4].replace(",", "")) for r in rows[1:]})
            cap = None
    sys.exit("Table 18 not found in the manuscript")


def scatter(ax, x, y, labels, colours, ylabel, xlabel):
    ax.scatter(x, y, s=190, c=colours, edgecolors="black", linewidths=1.4, zorder=3)
    # offset is in points, not data units; the two are not interchangeable here
    for xi, yi, lab in zip(x, y, labels):
        ax.annotate(lab, (xi, yi), xytext=(15, 8), textcoords="offset points",
                    fontsize=14, va="center")
    ax.set_xlabel(xlabel, fontsize=15)
    ax.set_ylabel(ylabel, fontsize=15)
    ax.tick_params(labelsize=14)
    ax.grid(alpha=0.3, zorder=0)
    ax.margins(x=0.16, y=0.11)


def build():
    rank, fdi = composite_rank()
    pcg = per_capita_from_table18()[rank.index]
    keep = rank.index != "Uttar Pradesh"

    r_all, p_all = stats.spearmanr(rank, fdi)
    r_ex, p_ex = stats.spearmanr(rank[keep], fdi[keep])
    r_pc, p_pc = stats.spearmanr(rank, pcg)

    # what is plotted must be what is reported: a downward scatter is a negative rho
    assert r_all < 0 and r_ex < 0, "rank-against-level correlation should be negative"

    os.makedirs(OUT, exist_ok=True)
    os.makedirs(TEX, exist_ok=True)

    fig, ax = plt.subplots(figsize=(10.3, 7.5), dpi=200)
    scatter(ax, rank.values, fdi.values / 1000.0, rank.index,
            ["#b22222" if s == "Uttar Pradesh" else "#2f6fa8" for s in rank.index],
            "Five-year total FDI, FY2019-20 to FY2023-24 (Rs '000 crore)",
            "Fiscal discipline composite rank (1 = most disciplined)")
    ax.set_title(f"Fiscal discipline rank vs total FDI\nSpearman rho = {r_all:.3f}, "
                 f"p = {p_all:.3f} (n=10); rho = {r_ex:.3f}, p = {p_ex:.3f} "
                 f"excluding Uttar Pradesh", fontsize=15, fontweight="bold", pad=14)
    fig.tight_layout()
    fig.savefig(f"{OUT}/Fig9a_discipline_vs_fdi.png", bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(10.3, 7.5), dpi=200)
    scatter(ax, rank.values, pcg.values, rank.index, ["#2e8b57"] * len(rank),
            "Per-capita GSDP, FY2023-24 (Rs)",
            "Fiscal discipline composite rank (1 = most disciplined)")
    ax.set_title(f"Fiscal discipline rank vs per-capita GSDP\nSpearman rho = "
                 f"{r_pc:.3f}, p = {p_pc:.3f} (n=10)", fontsize=15, fontweight="bold", pad=14)
    fig.tight_layout()
    fig.savefig(f"{OUT}/Fig9b_discipline_vs_pcgsdp.png", bbox_inches="tight")
    plt.close(fig)

    shutil.copyfile(f"{OUT}/Fig9a_discipline_vs_fdi.png", f"{TEX}/fig12.png")
    shutil.copyfile(f"{OUT}/Fig9b_discipline_vs_pcgsdp.png", f"{TEX}/fig13.png")
    print(f"  Figure 12  rho = {r_all:.3f} (p = {p_all:.3f}); "
          f"excluding UP {r_ex:.3f} (p = {p_ex:.3f})")
    print(f"  Figure 13  rho = {r_pc:.3f} (p = {p_pc:.3f})")
    return {"fdi_all": (r_all, p_all), "fdi_ex": (r_ex, p_ex), "pcg": (r_pc, p_pc)}


def embed():
    """Replace the two image parts inside the manuscript, matched by caption order."""
    import docx
    from docx.oxml.ns import qn
    from docx.text.paragraph import Paragraph
    doc = docx.Document(DOCX)
    order, prev = [], None
    for ch in doc.element.body.iterchildren():
        if ch.tag != qn("w:p"):
            continue
        for rid in re.findall(r'r:embed="(rId\d+)"', ch.xml):
            prev = rid
        m = re.match(r"(Figure \d+)\.", Paragraph(ch, doc).text.strip())
        if m and prev:
            order.append((m.group(1), prev))
    mapping = dict(order)
    for fig, src in [("Figure 12", f"{OUT}/Fig9a_discipline_vs_fdi.png"),
                     ("Figure 13", f"{OUT}/Fig9b_discipline_vs_pcgsdp.png")]:
        rid = mapping.get(fig)
        if rid is None:
            sys.exit(f"{fig} has no preceding image")
        doc.part.related_parts[rid]._blob = open(src, "rb").read()
        print(f"  {fig} -> {rid} replaced")
    doc.save(DOCX)


def selftest():
    rank, fdi = composite_rank()
    pcg = per_capita_from_table18()[rank.index]
    # the level and rank conventions must differ only in sign, which is the whole
    # point: reporting one on a plot of the other is what went wrong
    lvl = stats.spearmanr(rank, fdi)[0]
    rnk = stats.spearmanr(rank, fdi.rank(ascending=False))[0]
    print(f"  rank vs level {lvl:+.3f}   rank vs rank {rnk:+.3f}")
    assert abs(lvl + rnk) < 1e-12, "the two conventions should be exact negatives"
    assert round(lvl, 3) == -0.255 and round(rnk, 3) == 0.255

    # Maharashtra is rank 2 with the largest FDI; a downward slope is the only
    # reading consistent with that
    assert rank["Maharashtra"] == 2.0 and fdi.idxmax() == "Maharashtra"
    assert pcg["Telangana"] == pcg.max(), "Table 18 per-capita column misread"
    print("  self-test passed")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    else:
        build()
        embed()
