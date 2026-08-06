# Preprint submission kit

Everything below is copy-paste ready for MPRA and SSRN. Upload `paper/latex/main.pdf`.

Do MPRA first — it takes 1–5 working days and feeds RePEc/IDEAS, which is where
economists actually find sub-national India work. SSRN in parallel, same day.
Posting to both is normal practice in economics and does not compromise a later
journal submission.

---

## Title

Fiscal Discipline and Foreign Direct Investment across Indian States: What a
Ten-State Panel Can and Cannot Identify, FY 2019–20 to FY 2023–24

## Authors

| | |
|---|---|
| R Vinay Kumar | Department of Advanced Computing, St. Joseph's University, Bengaluru, Karnataka, India — rvinaykumar6924@gmail.com |
| S. Dutta | Department of Advanced Computing, St. Joseph's University, Bengaluru, Karnataka, India — duttasanjay098@gmail.com |

Set the corresponding author before you submit. MPRA attaches the deposit to
whoever holds the account, so if the account is yours, you are corresponding.

## Keywords

fiscal discipline; foreign direct investment; sub-national public finance; panel
data; India; LASSO; SHAP

## JEL codes

| Code | Field | Why it applies |
|---|---|---|
| **H72** | State and Local Budget and Expenditures | The four fiscal indicators are state budget aggregates — this is the primary code |
| **F21** | International Investment; Long-term Capital Movements | FDI equity inflows are the dependent variable of Model 1 |
| **H74** | State and Local Borrowing | Debt-to-GSDP is the paper's headline regressor |
| **O53** | Economywide Country Studies: Asia including Middle East | India-specific empirical study |
| **C33** | Panel Data Models; Spatio-temporal Models | Fixed effects, Driscoll-Kraay, wild cluster bootstrap |
| **C55** | Modelling with Large Data Sets | LASSO, Elastic Net, SHAP validation stage |

Lead with H72 and F21. Six codes is normal; do not submit fewer than three.

## Abstract — short form (≈150 words)

Use this for MPRA, and anywhere a length cap applies.

> Foreign direct investment in India concentrates in a handful of states, and
> fiscal discipline is widely assumed, though rarely tested, to be part of the
> reason. Using a balanced panel of India's ten largest FDI-recipient states over
> FY 2019–20 to FY 2023–24, built from audited state finance accounts in the
> Sixteenth Finance Commission report, we estimate fixed-effects and pooled
> regressions of FDI and GSDP growth on four fiscal indicators, cross-checked
> against rank correlation, LASSO and SHAP-based random forest importance. States
> carrying persistently lower public debt receive more FDI. The association is
> large, holds between states rather than within them, and every method recovers
> the same sign — but it clears five per cent under cluster-robust inference and
> falls just short under the wild cluster bootstrap we treat as arbiter. Because
> low-debt states here are western and southern, regional indicators absorb the
> effect entirely. Ten states across four regions cannot separate a fiscal signal
> from a regional one, and we report that as the finding.

## Abstract — full form

SSRN allows long abstracts. Paste the paper's own abstract verbatim from
`main.tex` (the `\section*{Abstract}` block) — it is already written for this and
does not need trimming.

---

## MPRA deposit fields

| Field | Value |
|---|---|
| Type | Preprint / MPRA Paper |
| Language | English |
| Institution | St. Joseph's University, Bengaluru |
| Keywords | as above, semicolon-separated |
| JEL | as above |
| File | `paper/latex/main.pdf` |

MPRA asks for a "Notes" field. Put the reproducibility statement there — it is
the strongest thing this paper has and it belongs where a reader sees it early:

> Complete dataset, analysis code, results and manuscript at
> https://github.com/fbivinay/Fiscal-Discipline-and-Investment-Outcomes — the
> audited source series, the 50-row analysis panel behind every estimate, every
> analysis script, and the full set of tables and figures.

## SSRN fields

Same title, authors, keywords, JEL. SSRN additionally wants:

- **Classification**: Economics Research Network → Public Economics; add
  Development Economics as secondary.
- **Date written**: the date you finalise, not the data window.

---

## Before you upload — three checks

1. **Get your co-author's and supervisor's written sign-off.** A preprint is
   public and permanent. MPRA deposits can be updated but not withdrawn cleanly,
   and SSRN removal takes weeks. This is the only irreversible step in the plan.
2. **Confirm the GitHub repository is public** and that the link in Section 9
   resolves. The reproducibility claim is checkable, so someone will check it.
3. **Rebuild the PDF** after any further edit — `pdflatex main.tex` twice, from
   `paper/latex`. The current `main.pdf` is 71 pages and already reflects the
   Appendix A restructure.

---

## What comes next: Economics Bulletin

Free, EconLit and RePEc indexed, peer-reviewed, and genuinely fast. Their
constraint, from the author instructions:

> Be **seven** printed pages or less **excluding tables, figures, appendices and
> references**.

That exclusion is the whole game. Concretely, for this paper:

- **Seven pages of prose is the budget.** 12pt Times Roman, single spaced, 1-inch
  margins. The current body prose is far over — Sections 2, 4 and 7 carry most of
  the excess.
- **Tables and figures cost nothing** and stay inline where they belong.
- **Appendix A rides free**, and there is a separate appendix-PDF upload slot on
  top of that.
- **A ZIP of code and data can be uploaded and is published.** This repository is
  already in the right shape for it.
- Submit as a **Note** or **Preliminary Results** — both are peer-reviewed. Given
  the paper's own conclusion (a design and an audit trail, not an identified
  effect), Preliminary Results is the honest category and the easier sell.

Formatting quirks that will otherwise cost you a revision round:

- No title page — the first page starts at "1. Introduction". Metadata is entered
  through their interface.
- No page numbers anywhere in the final PDF.
- Section headings centred, bold, 12pt, numbered in Arabic.
- **Tables numbered in Roman numerals** — Table I, Table II, and so on. That is a
  global renumber from the current Arabic scheme.
- Accepted papers publish immediately, with no typesetting queue.

Say the word and I will build the seven-page version as a separate file, leaving
the full manuscript untouched.
