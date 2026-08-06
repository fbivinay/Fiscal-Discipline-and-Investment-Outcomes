# Economics Bulletin submission

Short version of the full manuscript, cut to the journal's limit. The full paper
in `paper/` is untouched — this is a separate, self-contained note.

Build: `pdflatex main.tex` twice, from this directory. Check the prose budget
with `python tools/pagecount.py` after any edit.

**Current state: 8 pages total, 5 prose pages, 2 to spare** against the seven-page
limit. Verified: no title page, no page numbers, Tables I–VI in Roman numerals,
centred bold Arabic section headings.

## Metadata for the submission interface

Do not put any of this in the PDF — the journal generates the title page from
what you enter online.

**Category:** Preliminary Results. (Notes and Comments are the alternatives; both
are peer-reviewed. Preliminary Results is the honest fit, because the paper's
conclusion is an identification problem rather than an identified effect, and it
is the easier sell for exactly that reason.)

**Title:**

> Fiscal Discipline and Foreign Direct Investment across Indian States: A
> Ten-State Panel Cannot Separate Debt from Region

**Authors:** R Vinay Kumar and S. Dutta, Department of Advanced Computing,
St. Joseph's University, Bengaluru, Karnataka, India.

**Abstract:**

> Indian states carrying persistently lower public debt receive more foreign
> direct investment. Using a balanced panel of the ten largest FDI-recipient
> states over FY 2019–20 to FY 2023–24, built from audited state finance accounts
> in the Sixteenth Finance Commission report, we recover that association from
> five estimators across three families — pooled and fixed-effects panel
> regression, a Mundlak decomposition, rank correlation, LASSO, and SHAP
> importance from a random forest. It holds between states rather than within
> them, and a Mundlak specification rejects equality of the two dimensions at
> p = 0.017. It nonetheless clears five per cent only under cluster-robust
> inference, falling to p = 0.057 under the wild cluster bootstrap we treat as
> arbiter. The association also cannot be attributed to fiscal policy: 72 per
> cent of the cross-state variance in debt lies between four regional groups, and
> adding regional indicators reverses the pooled coefficient's sign. Ten states
> across four regions cannot separate a fiscal signal from a regional one. We
> report the identification problem as the result, and show that a twenty-six
> state cross-section from the same source would resolve it.

**Keywords:** fiscal discipline; foreign direct investment; sub-national public
finance; panel data; India

**JEL:** H72, F21, H74, O53, C33

## What was cut, and why

The full paper is 71 pages. What survives here is the spine: debt predicts FDI
between states, every method agrees on the sign, and region absorbs it.

| Dropped | Reason |
|---|---|
| Literature review (Section 2) | Compressed to one paragraph in the introduction |
| Theoretical framework (Section 3) | The hypotheses are stated where they are tested |
| All 14 data tables | Cited to the source; available in the repository |
| Fiscal discipline ranking construction (4.7) | Not needed for the claim; noted only in the conclusion, where it is a caution to index builders |
| Analytical architecture diagram (5.3) | Presentational |
| Specification curve, VIF, correlation matrix, subsample robustness | Diagnostics that support the estimate rather than the argument |
| Jharkhand and Uttar Pradesh cases (7.3) | Interesting, not load-bearing |
| Capital expenditure discussion (7.2) | The coefficient does not survive the bootstrap, so the note declines to interpret it at all |
| 22 of 42 references | Kept only what is cited in the short text |

The regional confound, which sat in Section 7.4 of the full paper as one
subsection among four, is promoted to its own numbered section and given the
paper's headline claim. That is the main editorial judgement in this cut: the
negative result is the contribution, and it is what makes a short note coherent
rather than a truncated long one.

## Before submitting

1. **Co-author and supervisor sign-off** on this version specifically — it makes
   a different headline claim from the full paper.
2. **Upload the code/data ZIP.** The journal accepts one and publishes it. The
   repository is already in the right shape; zip `code/` and `data/`. Note that
   anything uploaded in the appendix and supplemental slots with the final draft
   is made public.
3. **Optionally upload the full paper as the appendix PDF** — it is the natural
   companion, and it costs nothing against the page limit.
4. Confirm the preprint is posted first if you want the timestamp to precede
   review.
