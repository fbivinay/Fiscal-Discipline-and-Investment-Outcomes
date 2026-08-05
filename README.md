# Fiscal Discipline and Investment Outcomes

Panel evidence and machine-learning validation from India's ten largest FDI-recipient states, FY 2019-20 to FY 2023-24.

**R Vinay Kumar** — author
Department of Advanced Computing, St. Joseph's University, Bengaluru, Karnataka, India
rvinaykumar6924@gmail.com

**S. Dutta** — research guide
Department of Advanced Computing, St. Joseph's University, Bengaluru, Karnataka, India
duttasanjay098@gmail.com

**📄 [Download the paper](https://github.com/fbivinay/Fiscal-Discipline-and-Investment-Outcomes/raw/main/paper/Fiscal_Discipline_and_Investment_Outcomes.docx)** (.docx — GitHub cannot preview it in the browser)

---

## What this study asks

Do Indian states that manage their public finances well attract more foreign direct investment? Ten states receive roughly 97 per cent of India's recorded FDI equity inflows, and fiscal discipline is widely assumed to be part of the reason — but the link has not been tested directly at the state level.

The panel is small on purpose: it uses only audited, single-vintage data. Ten states over five fiscal years is 50 state-year cells, 48 of them with a usable FDI observation. Everything in the design follows from that constraint.

## Findings

**Debt predicts FDI between states.** States carrying persistently lower debt-to-GSDP receive more FDI than their peers — roughly 19 per cent more per percentage point of lower debt. At ten clusters the wild cluster bootstrap the paper defers to puts that coefficient at p = 0.057, significant at ten per cent rather than five, so the claim rests on convergence across methods rather than on that one p-value. The relationship holds *across* states, not *within* a state from year to year; Section 7.1 of the paper argues fiscal discipline is a structural signal investors price, not a lever a finance department can pull in one budget.

That convergence:

| Evidence | Result |
|---|---|
| Pooled panel regression | −0.176 (cluster-robust p = 0.007; wild cluster bootstrap p = 0.057) |
| Specification curve | Negative in **88 of 88** pooled specifications |
| LASSO / Elastic Net | Debt is the largest standardised coefficient, and enters the regularisation path first |
| SHAP (random forest) | Debt ranks first in **10 of 10** leave-one-state-out refits |
| Mundlak within/between split | Coefficients differ in sign, and differ from each other at a bootstrapped p = 0.017 |
| Permutation null | Importance margin reproduced by chance in 3.8 per cent of draws, permuting whole states |

**The growth hypothesis is not supported.** Earlier versions of this work reported first a deficit-growth effect and then a debt-and-own-tax-revenue one. Neither survived. The deficit effect (p = 0.031 under Driscoll-Kraay) fails a wild cluster bootstrap appropriate to ten clusters (p = 0.448). Debt and own tax revenue clear that bootstrap but only while the pandemic is controlled for by a single dummy: replace it with a full set of year fixed effects and own tax revenue goes to zero while the debt coefficient reverses sign, from +1.097 to −0.689. The association was tracking the common shape of the post-pandemic recovery, in which every state's growth rebounded while debt stayed above its pre-pandemic level. H2 is therefore reported as unsupported. Ninety-eight per cent of the variation in growth here is within states and almost all of it is common to them, which is the honest reason a ten-state, five-year panel cannot answer the question; that is a limit of this design rather than a contradiction of the longer panels in Trivedi and Rajmal (2011) and Panda and Sahay (2022), which also model real rather than nominal growth.

**Two states depart from the pattern for identifiable reasons.** Jharkhand is fiscally mid-table with near-zero realised FDI — discipline appears necessary but not sufficient. Uttar Pradesh ranks first on discipline and near-last on realised investment. Part of that is an artefact of DPIIT beginning its series in FY 2021-22, but only part: scaling its three observed years to a five-year equivalent still leaves it ninth of ten, and the rank correlation stays insignificant under every censoring-consistent treatment we tried. It is a genuine counterexample as well as a censored series, and the significant rank correlation reported in Section 6.2 depends on excluding it.

## Repository layout

```
data/
  raw/                        Source series as collected
    fiscal_data_source_tables/   Fiscal ratios from the Sixteenth Finance Commission
    FDI_top_states_*.csv         DPIIT state-wise FDI equity inflows
    GSDP_statewise_*.csv         MoSPI GSDP, 2011-12 series
    Control_Variables.xlsx       Census 2011 literacy and urbanisation
  processed/
    MASTER_PANEL_DATASET.csv     The 23-column analysis panel (50 rows)
    MASTER_PANEL_PLAN.csv        Column-by-column construction notes

code/
  analysis.py                 Descriptives, rankings, panel regressions, robustness
  ml_validation.py            Original ML run — 7 variables, superseded (see note below)
  ml_validation_corrected.py  Corrected 5-variable run, reproduces the paper's Section 6.6
  ml_validation_v2.py         Panel-aware extensions: state-blocked CV, within
                              specification, permutation null, stability selection
  specification_tests.py      Estimator choice, error structure, functional form,
                              specification curve, wild cluster bootstrap
  reconstruct_from_paper.py   Rebuilds the panel from the manuscript's own
                              published tables and re-derives the results
  verify_against_fc16.py      Checks every fiscal figure in Section 4 against
                              the FC-16 annexures, the stated source
  verify_against_dpiit.py     Checks the sample selection and Table 11's
                              cumulative totals against the DPIIT factsheet

results/
  econometrics/               Tables 1-6, Figures 1-10, full regression output
  ml/
    lasso_shap_original_7var/    The flawed run, kept deliberately (see below)
    lasso_shap_corrected_5var/   The corrected run reported in the paper
    panel_aware_v2/              Stability, within, permutation, out-of-sample
  diagnostics/                Specification tests, specification curve, bootstrap

paper/                        Manuscript, LaTeX source, figures
docs/                         Research plan
```

## Reproducing

```bash
pip install numpy pandas scipy matplotlib scikit-learn shap statsmodels linearmodels
```

Run from the repository root, in this order:

```bash
python code/analysis.py                  # econometrics
python code/ml_validation_corrected.py   # ML validation as reported
python code/ml_validation_v2.py          # panel-aware extensions
python code/specification_tests.py       # diagnostics + specification curve
python code/reconstruct_from_paper.py    # reproducibility check, see below
```

## Checking the paper against its source

`reconstruct_from_paper.py` shows the paper is internally consistent. It cannot
show the numbers were transcribed correctly in the first place, which is a
different question and the one an auditor would ask first.

`verify_against_fc16.py` answers it. It reads the Sixteenth Finance Commission's
Volume II annexures directly and compares all 200 fiscal figures in Section 4
against them:

| Annexure | Table | Indicator | Result |
|---|---|---|---|
| 5.1 | Table 2 | Fiscal deficit, % GSDP | 50/50 |
| 5.2 | Table 10 | Revenue deficit, % GSDP | 50/50 |
| 5.3 | Table 4 | Outstanding liabilities, % GSDP | 50/50 |
| 5.5 | Table 6 | Own tax revenue, % GSDP | 50/50 |

**200 of 200 match exactly, with no discrepancies.** That includes Jharkhand's
FY 2021-22 fiscal deficit of 0.0 per cent, the one cell in the panel that looks
wrong: it reads 0.0 in Annexure 5.1, so the transcription is right and the
oddity is in the source. Section 4.2 discusses what can and cannot be concluded
from it.

`verify_against_dpiit.py` covers the FDI side. DPIIT reports state-wise inflow
as a single cumulative figure rather than year by year, so it cannot confirm
Table 11 cell by cell, but it settles two things. The sample is the ten largest
recipients **among states FC-16 reports on**, not off DPIIT's table outright:
Delhi ranks fourth on FDI and is excluded because it appears nowhere in the
FC-16 annexures, so no fiscal indicator exists for it, and West Bengal enters in
its place. And every state's cumulative total in Table 11 is at least as large in
a later factsheet, as it must be. Jharkhand's is larger by 86 crore over fifteen
months against Maharashtra's 210,796 crore, which corroborates Section 7.3 from
data published after the paper's window.

### What is not checked against a source

Two of the eight input tables have not been verified against the documents they
cite, and the record should say so rather than imply otherwise.

| Table | Input | Status |
|---|---|---|
| Table 12 | GSDP levels, MoSPI | not checked |
| Table 14 | Literacy and urbanisation, Census 2011 | not checked |
| Table 8 (cross-check columns) | Capital outlay, state budget documents | not checked |

Neither gap is load-bearing. The four fiscal regressors are published by FC-16
*already expressed as a share of GSDP*, so they are verified without reference
to Table 12: the Commission performed its own division and this repository
checked its output. GSDP enters the paper only through the rupee-amount tables,
which are presentational and used in no estimate, through GSDP growth, which is
the dependent variable of a hypothesis the paper reports as unsupported, and
through the log-GSDP market-size control of Table 23c, which is a robustness
check rather than a headline. Literacy and urbanisation enter the pooled
specification alone, and Section 6.5 shows both lose significance once scale is
controlled for.

An error in either table could therefore not disturb the debt-FDI result. They
are listed here because a verification claim is worth only as much as its
statement of what it does not cover.

The script needs `Vol2-Annexures.pdf` in the project root, which is not
redistributed here — download it from the URL in the reference list — and
`pdftotext` on the path (poppler; it ships with Git for Windows).

One implementation note, because it is a trap. The annexure headings cannot be
used to locate the tables: pdftotext's reading order places a table's rows
either side of the next heading, and Annexure 5.4 reports Special Assistance in
rupees rather than as a share of GSDP, so it emits no percentage rows and shifts
every later heading by one relative to its data. Anchoring on headings produces
confident, wrong answers — it reports own tax revenue as 10-19 per cent of GSDP,
which is Annexure 5.6's revenue receipts. The script therefore indexes the
percentage tables by document order, and checks the assignment independently by
confirming own tax revenue falls below revenue receipts in all 31 rows, which it
must, being a component of it.

## Reproducing the paper without trusting this repository

`reconstruct_from_paper.py` answers a sharper question than "do the scripts
run?". It opens only `paper/Fiscal_Discipline_and_Investment_Outcomes.docx`,
parses the eight input tables printed in Section 4, rebuilds the fifty-row
panel from them, re-estimates the models and compares the output against the
figures printed in Sections 6 and 7. It never reads
`data/processed/MASTER_PANEL_DATASET.csv`.

It passes: the descriptive statistics of Table 17, every coefficient in
Tables 19 and 20, the variance inflation factors of Table 21, and the Mundlak
and between-estimator coefficients of Table 35 are all recovered to the
precision at which they are published. A reader with the manuscript alone can
therefore reproduce every headline estimate, and no intermediate file in this
repository has to be taken on trust.

One detail is worth stating because it is a real limit rather than a rounding
convenience. GSDP growth is read from Table 13 rather than recomputed from the
GSDP levels in Table 12. The published growth series is rounded to two decimals
and Model 2 is estimated on those rounded values, so recomputing at full
precision shifts the Model 2 coefficients in the fourth decimal. The script
performs that recomputation anyway as a cross-check and reports the divergence
between the two published series, which is 0.005 percentage points.

The two scripts with non-trivial logic carry a self-check:

```bash
python code/ml_validation_v2.py --selftest
python code/specification_tests.py --selftest
```

`specification_tests.py` takes several minutes — the wild cluster bootstrap refits the panel 1,999 times per coefficient. All scripts are seeded (`RNG = 42`) and reproduce the reported numbers exactly.

## Two methodological notes worth reading

**A leakage failure is kept in the repository rather than deleted.** The first SHAP run included the two Census controls and ranked urbanisation as the dominant predictor by a factor of five. Urbanisation is constant within a state across all five years, so the random forest was using it as a state identifier and re-learning the fixed effect through the back door. `lasso_shap_original_7var/` preserves that output; the paper discloses it. Anyone applying tree-based importance to a short panel with few entities should expect this.

**Inference is reported three ways because no single estimator is trustworthy here.** Driscoll-Kraay is asymptotic in the number of periods (five); the cluster-robust *t* is asymptotic in the number of clusters (ten). Where they disagree the wild cluster bootstrap adjudicates, and `results/diagnostics/TableS4_wild_cluster_bootstrap.csv` reports every coefficient the paper relies on under all three. Two results changed verdict as a result, and both are stated in the paper rather than dropped.

## Data sources

| Series | Source |
|---|---|
| Fiscal ratios (deficit, debt, own tax revenue, capital expenditure) | Report of the Sixteenth Finance Commission, Volume II, Chapter 5 annexures, computed from CAG-audited State Finance Accounts |
| FDI equity inflows, state-wise | Department for Promotion of Industry and Internal Trade (DPIIT) |
| GSDP and growth | Ministry of Statistics and Programme Implementation (MoSPI), 2011-12 series, current prices — growth is therefore nominal |
| Literacy, urbanisation | Census of India 2011 |

Capital expenditure is derived as gross fiscal deficit minus revenue deficit, so it includes net lending — a limitation the paper discusses in Section 7.2. DPIIT began publishing state-wise FDI in October 2019, making FY 2019-20 a six-month flow; Uttar Pradesh's series begins FY 2021-22 and those two cells are missing, not zero.

## Limitations

Fifty state-year cells. Association, not causation — reverse causality cannot be excluded at T = 5. The debt measure is the on-budget figure and excludes off-budget borrowings and guarantees, which for Telangana have been estimated at 14-15 per cent of GSDP. The sample is the ten states that already receive almost all of India's FDI, so the result describes how investment sorts among states already in contention, not how a state enters that group.

## License

Research output. Underlying data is from public government sources; please cite the originating agencies listed above.
