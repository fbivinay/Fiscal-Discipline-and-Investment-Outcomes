# LaTeX build — Fiscal Discipline and Investment Outcomes

## How to compile

Locally, with any TeX distribution on the path:

```bash
cd paper/latex
pdflatex main.tex && pdflatex main.tex     # twice, for the cross-references
```

Or on Overleaf: **New Project → Upload Project**, zip this whole `latex` folder
(keep `figures/` inside it), and let it pick `main.tex` as the root with
**pdfLaTeX** as the compiler.

No `.bib` file and no bibtex run is needed. The reference list is typeset directly
as hanging-indent paragraphs, matching the APA formatting of the original document.

### Last verified build

Compiled with MiKTeX 25.12 (pdfTeX 4.23): **71 pages, no errors, no undefined
references.** All 41 tables number correctly, including the lettered 16a, 16b,
23a, 23b, 23c and 31a, and all 25 figures place where their captions sit. The
main text runs to page 66 and Appendix A holds pages 67-71.

The architecture diagram is included at `0.99\textwidth` rather than the full
width. It is drawn at exactly the text-block width, so at `\textwidth` the float
plus its caption exceeded the page by 0.13 pt and LaTeX warned; the one per cent
reduction clears that and is far too small to see.

## How the table and spacing problems are fixed

**Tables drifting to the next page.** Every table and every chart is now set
`[H]` (from the `float` package), which pins it exactly where it appears in the
source — immediately after the sentence that introduces it. `[H]` is not a
float, so nothing can drift past its discussion. Where a table genuinely will
not fit in the space left on a page, LaTeX starts a new page and the text that
follows the table moves with it, so the table and its discussion stay together.

**Large gaps around images.** Three causes, three fixes:

- `\raggedbottom` collects leftover vertical slack at the foot of the page
  instead of stretching it between paragraphs. This is what produced most of
  the visible gaps.
- `\intextsep`, `\floatsep` and `\textfloatsep` cut from 16/14/18 pt to
  10/10/12 pt, and caption skips from 6 pt to 4 pt.
- Each chart's width is set individually so its **printed height never exceeds
  3.7 in** — computed per file from the image's own aspect ratio. Two figures
  can therefore share a page rather than each claiming most of one.

**Small tables blown up to full width.** Tables use
`\begin{adjustbox}{max width=\textwidth}`, which shrinks a table only if it is
too wide and leaves it alone otherwise. The earlier `\resizebox{\textwidth}{!}`
scaled *every* table to the full width, which made the two-column tables (VIF,
SHAP importance, LOO-CV R²) render in enormous type. `\footnotesize` is applied
first, so wide tables need less shrinking and stay legible.

Margins are 0.9 in rather than 1 in, which widens the text block to 6.47 in and
reduces how much the wide regression tables have to shrink.

## Figure 11 (the architecture diagram)

Drawn on a canvas of exactly 6.47 × 9.25 in, which is the text block width by
the usable page height. It is placed with `width=\textwidth` on a `[p]` float,
so it renders at **1:1 with no scaling** — the point sizes in the diagram are
the point sizes on the page (body text 8.5 pt, box titles 9.8–11 pt, main title
16 pt). It fills its own page.

If you change the geometry margins, regenerate the diagram to match, or it will
be scaled and the type will shrink with it.

## Files

| Path | What it is |
|---|---|
| `main.tex` | The whole paper: 8 sections plus a data-availability section and Appendix A, 22 subsections, 41 tables, 25 figures, 42 references |
| `figures/fig01–fig10, fig12–fig25 .png` | The charts, extracted from the DOCX |
| `figures/fig_architecture.pdf` | Figure 11, the full-page architecture diagram (vector) |

## main.tex is generated, not hand-edited

`main.tex` is regenerated from `paper/Fiscal_Discipline_and_Investment_Outcomes.docx`,
which is the authoritative copy of the manuscript. The preamble above the
`\begin{document}` line — geometry, float control, per-figure widths, caption
skips — is preserved across regenerations; everything below it is rebuilt from
the DOCX. **Edit the DOCX and regenerate**, or your changes will be overwritten
the next time the two are synchronised.

The figure widths are not arbitrary: each is `min(1.00, 3.7in / (6.47in * h/w))`
so that no chart prints taller than 3.7 in, which is what lets two figures share
a page.

## Appendix A and the table counter

Tables 1-14 — the year-wise source data — live in **Appendix A at the end of the
document**, not in Section 4. Section 4 keeps its prose, its figures and the
ranking tables (15, 16, 16a, 16b), and points at the appendix by table number.

Their numbers are unchanged, and two `\setcounter` calls are what hold that:

- `\setcounter{table}{14}` immediately before Table 15, so the body picks up at
  15 even though Tables 1-14 no longer precede it;
- `\setcounter{table}{0}` at the top of Appendix A, so the appendix runs 1-14.

Every in-text reference is the literal string "Table N", not `\ref`, so the two
counters are the only thing keeping the numbering honest. **Do not remove them**,
and if tables are added or moved again, check both.

## Sub-lettered tables

Four tables carry letters rather than plain numbers — 16a, 23a, 23b and 31a —
because they were inserted after the surrounding tables were already numbered and
cross-referenced in the text. LaTeX cannot produce that from its own counter, so
each is wrapped in:

```latex
\addtocounter{table}{-1}\renewcommand{\thetable}{\arabic{table}a}
\caption{...}
\label{tab:16a}
\renewcommand{\thetable}{\arabic{table}}
```

The counter is rolled back one, `\caption` advances it again and prints the
lettered form, then the normal numbering is restored so the next table continues
the sequence. Do not renumber these to close the gap: the DOCX and every in-text
reference use the lettered form.

## Other conversion notes

- Models 1 and 2 are real `equation` environments rather than plain text.
- The two regression tables (19 and 20) have proper two-level headers via
  `\multicolumn` + `\cmidrule`, replacing the repeated
  `FE + Driscoll-Kraay (coef)` / `(std_err)` / `(t)` / `(p)` column labels.
- Table 8's cross-check columns are grouped under their own spanning header.
- URLs in the reference list are wrapped in `\url{}` with `xurl`, so they break
  across lines instead of running into the margin.
- Section and subsection numbers are generated by LaTeX and line up with the
  in-text cross-references ("Section 4.7", "Section 6.6", and so on).
