# Economics Bulletin submission

Short version of the full manuscript, cut to the journal's limit. The full paper
in `paper/` is untouched — this is a separate, self-contained note.

Build: `pdflatex main.tex` twice, from this directory. Check the prose budget
with `python tools/pagecount.py` after any edit.

**Current state: 9 pages total, 6 prose pages, 1 to spare** against the
seven-page limit — 8 tables, none of which count. Compiles with no overfull boxes
and no undefined references. No figures: the regional scatter drafted at
`e7638b4` was cut, since the numbers in Section 5 carry the point without it.

## Compliance against the author instructions

Every rule in `Economics Bulletin author guildlines-2012.pdf`, and where it is met.

| Rule (journal's wording) | Status |
|---|---|
| "Be seven printed pages or fewer excluding tables, figures, and references" | 6 prose pages. `tools/pagecount.py` measures it the way the rule is written, by stripping floats and back matter and recounting. Note the live submission page drops **appendices** from the exclusion list the 2012 PDF gave — an appendix bound into the manuscript may now count, so this note has none |
| "Be written in English" | Yes |
| "Use 12pt Times Roman, CM … or other similar font" | `mathptmx` (Times), `12pt` class option |
| "Pages should be single spaced with one-inch margins" | `geometry margin=1in`, no line-spacing package |
| "Sections and subsections … numbered consecutively in Arabic numerals (as in section 1. and subsection 1.2)" | `\titleformat` gives `1.` for sections and `4.1` for subsections — matching the period convention in their own example |
| "Section headings should be centered and in bold **14pt** type" | Sections centred and bold at exactly 14pt via `\fontsize{14}{17}`; subsections centred and bold at 12pt. The 2012 PDF said 12pt — the live page says 14, and the live page wins. At final-draft stage the requirement changes again, to **16pt** |
| "Figures, and tables should be included **within** the manuscript in the correct place… do not substitute text such as 'figure 1 about here'" | All six tables set `[H]` at the point of discussion. No placeholders |
| "**Do not include a title page with any submission** … the first page of the PDF you submit should begin with the title of the first section" | Page 1 opens at `1. Introduction` |
| "Do not include page numbers anywhere in your final PDF" | `\pagestyle{empty}` |
| "Numbers for displayed equations should be placed in parentheses at the right margin" | Equation (1), amsmath default |
| "Footnotes should be used sparingly" | None used |
| "Number tables consecutively with **Roman numerals** in order of appearance" | Tables I–VI, in text order |
| "A short descriptive caption should be typed directly above each table" | Captions above and kept to one line; qualifying detail moved to notes below each table |
| "Cite references in the text by author's surname and date" — their examples show **no comma** before the year | `(DPIIT 2024)`, `(Cameron, Gelbach and Miller 2008)`, `(Roodman 2009, and Mullainathan and Spiess 2017)` |
| "References should be listed in alphabetical order and in descending order of date" | Checked: Blonigen → Zou |
| "Style and punctuate references according to the following examples" | Restyled to their format: `Surname, A.B. (Year) "Title" *Journal* **Vol**, pages.` Volume bold, journal italic, no DOIs — their own examples carry none |
| "hyperlinks be underlined but appear in black" | The one URL uses `\uline` with `hidelinks` |
| Every listed reference is cited in the text | Checked programmatically; Blonigen (2005) was uncited and is now cited in the introduction |

## Why this venue

Free, no article processing charge, peer-reviewed, and publishes immediately on
acceptance. Indexed in **Scopus** (SJR 0.152, Q4, h-index 42), **ESCI**, **ABDC**,
**EconLit** and **RePEc**. Publisher is AccessEcon LLC.

Q4 is the bottom quartile, so this is a low-prestige Scopus journal — the trade
being made deliberately in exchange for speed and zero cost. Metrics above come
from aggregator sites and should be re-checked against Elsevier's own Scopus
source list before being quoted to anyone.

Note that UGC discontinued the CARE list on 3 October 2024 and stopped
maintaining it in February 2025, replacing it with 36 parameters each institution
applies itself. Any journal still advertising "UGC CARE listed" is citing a dead
list. Confirm what St. Joseph's now accepts.

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

**JEL:** H72, F21, H74, H63, R11

C33 (Panel Data Models) was dropped. The submission page warns that C1 "and the
other 'C' methodology JELs should only be used for papers that make a
contribution to econometric theory, not for empirical papers in general.
Misclassified submissions may be declined without further review." This paper
uses panel methods, it does not contribute to them. H63 (debt) and R11 (regional
economic activity) replace it, and R11 in particular matches the headline claim
better than a methods code ever did — the journal says it routes referees by
these codes.

## What was cut, and why

The full paper is 71 pages. What survives here is the spine: debt predicts FDI
between states, every method agrees on the sign, and region absorbs it.

Because tables, figures, appendices and references are all excluded from the page
limit, the budget binds only on prose. Anything that can be carried by a table is
therefore free, and the note uses that: the diagnostics and the subsample
robustness both earn their place without costing a line of the seven pages.

What is *not* done is padding the submission with every table from the full paper
because they happen to be free. Economics Bulletin exists to publish short notes;
a submission with six pages of prose and twenty-five of tables reads as someone
gaming the rule, and every extra exhibit is another thing a referee can object to.
The tables kept are the ones that answer a question a referee would otherwise
ask.

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
   a different headline claim from the full paper. The journal's terms require
   that "all of the authors as well as the institutions at which the work was
   carried out approve of its submission".
2. **Send the cover letter** in `COVER_LETTER.md`. Optional by the instructions,
   but the General Publication Terms make it the authors' responsibility to keep
   editors informed about related research in other outlets, and a longer version
   of this work is public on GitHub. The letter discloses it.
3. **Upload the code/data ZIP.** Zip `code/` and `data/`. The instructions allow
   a ZIP "containing programming code, data, or other relevant details" and ask
   for a short text description of it.
4. **Optionally upload the full paper as the appendix PDF.** The instructions
   allow an appendix "which will be sent to the editors and referees, but which
   may not be intended for publication". It costs nothing against the page limit.
5. **At final-draft stage, re-check the author metadata.** The instructions warn:
   "Check and correct the metadata especially for number and order or coauthors …
   We will not be able to make corrections after the proofs are published."
6. **Know what becomes public.** "The supplemental data and appendix will be made
   publicly available. If you do not wish this to happen do not upload anything in
   these slots with your final draft."
7. **Do not chase the editors.** "Please do not request updates on the status of
   submitted papers for at least four months." Plan around that, not around the
   3–6 week figure aggregator sites quote.
8. **Fix the author list now.** Coauthors may be added to a submission or a
   revision, but "once a paper is accepted, the set of authors is fixed.
   Coauthors cannot be added with a final draft."
9. **Three submissions per year, maximum**, coauthored papers included.
   "Submissions in excess of this will be declined without further review."

## What compliance does and does not buy

Everything above removes the avoidable reasons for rejection — formatting, style,
length, disclosure. It does not make acceptance certain, and nothing can: the
paper still goes to referees who will judge whether a fifty-observation panel
reporting its own identification failure is worth publishing. The honest case for
it is that the negative result is clearly established and the remedy is specified.
That is a real argument, and it is the one the cover letter makes.
