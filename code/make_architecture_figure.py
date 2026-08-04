"""
============================================================================
FIGURE 11 — ANALYTICAL ARCHITECTURE DIAGRAM
Fiscal Discipline & FDI in Indian States
============================================================================
Regenerates the full-page architecture diagram used as Figure 11.

The original existed only as a PDF with no source, so it could not be kept in
step with the manuscript and had drifted: it described the LASSO penalty as
leave-one-out cross-validated (the row-wise scheme the panel-aware correction
replaced), omitted the specification-testing work of Sections 5.4 and 6.7
entirely, and opened Stage 9 by calling the five methods independent, which
Section 5.3 now explicitly disowns.

Canvas is 6.47 x 9.25 in, the LaTeX text-block width by the usable page
height, so `\\includegraphics[width=\\textwidth]` places it at 1:1 and the point
sizes below are the point sizes on the page. If the geometry margins in
paper/latex/main.tex change, change PAGE_W here to match or the type will
scale with the image.

Stage numbering stays at 0-10 deliberately. Section 5.3 refers to "Stage 9"
and "the tenth stage" by name, so the specification-testing work is folded into
Stages 4 and 5 rather than inserted as a twelfth box.

Boxes size themselves from their line count and are laid out by a cursor
running down the page, so editing the text below cannot silently push text
outside its box.

Run:  python code/make_architecture_figure.py
============================================================================
"""
import os
import shutil

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

PAGE_W, PAGE_H = 6.47, 9.25
OUT_PDF = "paper/figures/fig_architecture.pdf"
OUT_PNG = "paper/figures/fig_architecture.png"
LATEX_COPY = "paper/latex/figures/fig_architecture.pdf"

INK = "#1c2b46"
ASSEMBLY = ("#e8ecf5", "#8c9bb8")
CLASSICAL = ("#dce8f7", "#2f5f9e")
ML = ("#e9e2f5", "#5b4a9e")
CONVERGE = ("#dff0dc", "#2e7d32")
RESIDUAL = ("#fdf2dc", "#b9821f")

TITLE_PT, SUB_PT, HEAD_PT, BODY_PT, REF_PT, BRANCH_PT = 15, 10, 10.5, 7.5, 7.2, 9.5
LINESP = 1.30

# one y-unit is PAGE_H/100 inches; convert point heights into y-units
PT_PER_Y = PAGE_H * 72.0 / 100.0
LINE_H = BODY_PT * LINESP / PT_PER_Y
HEAD_H = HEAD_PT * 1.35 / PT_PER_Y
PAD_T, PAD_B = 0.7, 0.8

fig = plt.figure(figsize=(PAGE_W, PAGE_H), facecolor="white")
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis("off")


def box_height(lines, head_pt=HEAD_PT):
    return PAD_T + head_pt * 1.35 / PT_PER_Y + 0.5 + len(lines) * LINE_H + PAD_B


def draw_box(x0, x1, y_top, lines, fill, edge, stage, title, ref,
             head_pt=HEAD_PT, lw=1.4, body_pt=BODY_PT):
    h = box_height(lines, head_pt)
    y0 = y_top - h
    ax.add_patch(FancyBboxPatch((x0, y0), x1 - x0, h,
                                boxstyle="round,pad=0,rounding_size=1.1",
                                facecolor=fill, edgecolor=edge, linewidth=lw, zorder=2))
    label = ("%s    %s" % (stage, title)) if stage else title
    ax.text(x0 + 1.7, y_top - PAD_T, label, fontsize=head_pt, fontweight="bold",
            color=INK, va="top", ha="left", zorder=3)
    if ref:
        ax.text(x1 - 1.7, y_top - PAD_T - 0.1, ref, fontsize=REF_PT, style="italic",
                color=edge, va="top", ha="right", zorder=3)
    ax.text(x0 + 1.7, y_top - PAD_T - head_pt * 1.35 / PT_PER_Y - 0.5,
            "\n".join(lines), fontsize=body_pt, color=INK,
            va="top", ha="left", linespacing=LINESP, zorder=3)
    return y0


def arrow(x, y_from, y_to, color):
    ax.add_patch(FancyArrowPatch((x, y_from), (x, y_to), arrowstyle="-|>",
                                 mutation_scale=10, color=color, linewidth=1.2, zorder=1))


def pill(cx, y_top, w, text, colour, pt=BRANCH_PT):
    h = 3.0
    ax.add_patch(FancyBboxPatch((cx - w / 2, y_top - h), w, h,
                                boxstyle="round,pad=0,rounding_size=1.1",
                                facecolor="white", edgecolor=colour, lw=1.3, zorder=3))
    ax.text(cx, y_top - h / 2, text, fontsize=pt, fontweight="bold",
            color=colour, ha="center", va="center", zorder=4)
    return y_top - h


# ------------------------------------------------------------------- title --
ax.text(50, 99.0, "Analytical architecture of the study", fontsize=TITLE_PT,
        fontweight="bold", color=INK, ha="center", va="top")
ax.text(50, 96.2, "From raw source files to final validation", fontsize=SUB_PT,
        style="italic", color=INK, ha="center", va="top")
ax.plot([30, 70], [95.3, 95.3], color=INK, lw=0.7)
ax.text(50, 93.9, "DATA ASSEMBLY   ·   arithmetic, not inference", fontsize=9.0,
        fontweight="bold", color=INK, ha="center", va="top")
ax.plot([3, 24], [93.2, 93.2], color="#8c9bb8", lw=0.8)
ax.plot([76, 97], [93.2, 93.2], color="#8c9bb8", lw=0.8)

GAP = 1.5
y = 92.6
for stage, title, lines, ref in [
    ("Stage 0", "Source ingestion",
     ["FC-16 Vol. II Ch. 5 annexures  ·  DPIIT state-wise FDI  ·  MoSPI GSDP",
      "(2011-12 series, current prices)  ·  Census 2011 Primary Census Abstract"],
     "§ 4.2 – 4.6"),
    ("Stage 1", "Panel construction",
     ["Balanced 10 × 5 panel  ·  ratios as per cent of GSDP  ·  ln(FDI)  ·",
      "year-on-year GSDP growth  ·  COVID dummy  ·  48 usable FDI cells of 50"],
     "§ 4.1, 4.3 – 4.5"),
    ("Stage 2", "Composite discipline ranking",
     ["Four fiscal ratios ranked across the ten states, then averaged into a",
      "composite  ·  weighting sensitivity checked against realised FDI"],
     "§ 4.7, 6.2"),
]:
    y = draw_box(6, 94, y, lines, *ASSEMBLY, stage=stage, title=title, ref=ref)
    if stage != "Stage 2":
        arrow(50, y, y - GAP, "#8c9bb8")
        y -= GAP

# split into branches
ax.plot([50, 50], [y, y - 1.6], color="#8c9bb8", lw=1.2, zorder=1)
ax.plot([25, 75], [y - 1.6, y - 1.6], color="#8c9bb8", lw=1.2, zorder=1)
arrow(25, y - 1.6, y - 3.2, CLASSICAL[1])
arrow(75, y - 1.6, y - 3.2, ML[1])
y -= 3.2

y_lbl = min(pill(25, y, 31, "BRANCH A  ·  classical", CLASSICAL[1]),
            pill(75, y, 41, "BRANCH B  ·  machine learning", ML[1]))
y = y_lbl - 1.4

LX0, LX1, RX0, RX1 = 2, 48.5, 51.5, 98
BRANCH = [
    (("Stage 3", "Panel estimation",
      ["Models 1 and 2, each estimated twice:",
       "fixed effects with Driscoll-Kraay errors,",
       "and pooled OLS with Census controls"], "§ 6.3 – 6.4"),
     ("Stage 6", "Regularised fits",
      ["Five time-varying regressors only.",
       "LASSO at a state-blocked cross-validated",
       "penalty  ·  Elastic Net  ·  forest via SHAP"], "§ 5.2, 6.6")),
    (("Stage 4", "Diagnostics & inference",
      ["Variance inflation  ·  poolability F  ·  Hausman  ·",
       "Pesaran CD  ·  Wooldridge AR(1) against ρ = −0.5  ·",
       "wild cluster bootstrap, the arbiter at ten clusters"], "§ 6.7"),
     ("Stage 7", "Leakage audit",
      ["Urbanisation diagnosed as a disguised state",
       "identifier; branch refitted without time-invariant",
       "controls, then rerun with them for comparison"], "§ 6.6, 7.4")),
    (("Stage 5", "Perturbation",
      ["Refits dropping the COVID year, Uttar Pradesh",
       "and Jharkhand in turn  ·  year fixed effects against",
       "a single dummy  ·  132-specification curve  ·  Mundlak"], "§ 6.5, 7.1"),
     ("Stage 8", "Stability layer",
      ["Ten leave-one-state-out SHAP refits  ·  stability",
       "selection, 500 subsamples  ·  state-permuted null  ·",
       "within specification  ·  out-of-sample R² three ways"], "§ 6.6")),
]
for i, (L, R) in enumerate(BRANCH):
    lines = max(len(L[2]), len(R[2]))
    pad_l = L[2] + [""] * (lines - len(L[2]))
    pad_r = R[2] + [""] * (lines - len(R[2]))
    yl = draw_box(LX0, LX1, y, pad_l, *CLASSICAL, stage=L[0], title=L[1],
                  ref=L[3], head_pt=9.1)
    yr = draw_box(RX0, RX1, y, pad_r, *ML, stage=R[0], title=R[1],
                  ref=R[3], head_pt=9.1)
    y = min(yl, yr)
    if i < len(BRANCH) - 1:
        arrow(25, y, y - GAP, CLASSICAL[1])
        arrow(75, y, y - GAP, ML[1])
        y -= GAP

# ------------------------------------------------------------ convergence ---
ax.plot([25, 25], [y, y - 1.6], color=CLASSICAL[1], lw=1.2, zorder=1)
ax.plot([75, 75], [y, y - 1.6], color=ML[1], lw=1.2, zorder=1)
ax.plot([25, 75], [y - 1.6, y - 1.6], color="#8c9bb8", lw=1.2, zorder=1)
y = pill(50, y - 1.6, 26, "CONVERGENCE", CONVERGE[1])
arrow(50, y, y - GAP, CONVERGE[1])
y -= GAP

y = draw_box(3, 97, y,
             ["Five methods over the same 48 observations: pooled panel regression  ·  Spearman rank",
              "correlation  ·  LASSO  ·  Elastic Net  ·  SHAP importance. They are not five independent",
              "draws and are not treated as one — LASSO and Elastic Net differ only in the penalty, and",
              "the rank correlation is significant only with Uttar Pradesh excluded. What the design buys",
              "is agreement across three method families: a parametric panel estimator, a regularised",
              "linear selector, and a non-parametric tree ensemble. Disagreements are reported."],
             *CONVERGE, stage="Stage 9", title="Convergence test  —  FINAL VALIDATION",
             ref="§ 5.3, 6.6, 7.1", head_pt=11.5, lw=1.9)
arrow(50, y, y - GAP, RESIDUAL[1])
y -= GAP

y = draw_box(9, 91, y,
             ["Jharkhand and Uttar Pradesh examined by name as departures from the fitted",
              "pattern. Uttar Pradesh is a censored series and a genuine counterexample both:",
              "scaling its observed years still leaves it ninth of ten on realised investment."],
             *RESIDUAL, stage="Stage 10", title="Residual case analysis", ref="§ 7.3")

if y < 0.5:
    raise SystemExit("layout overflows the page: bottom edge at y = %.2f" % y)
print("layout ends at y = %.2f (0 is the page foot)" % y)

os.makedirs("paper/figures", exist_ok=True)
fig.savefig(OUT_PDF, format="pdf", facecolor="white")
fig.savefig(OUT_PNG, dpi=200, facecolor="white")
plt.close(fig)
shutil.copyfile(OUT_PDF, LATEX_COPY)
print("wrote %s (%.2f x %.2f in), %s, and copied to %s"
      % (OUT_PDF, PAGE_W, PAGE_H, OUT_PNG, LATEX_COPY))
