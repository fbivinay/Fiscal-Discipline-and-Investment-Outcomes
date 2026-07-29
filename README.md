# Fiscal Discipline and Investment Outcomes

Panel evidence and machine-learning validation from India's ten largest FDI-recipient states, FY 2019-20 to FY 2023-24.

**R Vinay Kumar** — author
Department of Advanced Computing, St. Joseph's University, Bengaluru, Karnataka, India
rvinaykumar6924@gmail.com

**S. Dutta** — research guide
Department of Advanced Computing, St. Joseph's University, Bengaluru, Karnataka, India
duttasanjay098@gmail.com

---

## What this study asks

Do Indian states that manage their public finances well attract more foreign direct investment? Ten states receive roughly 97 per cent of India's recorded FDI equity inflows, and fiscal discipline is widely assumed to be part of the reason — but the link has not been tested directly at the state level.

The panel is small on purpose: it uses only audited, single-vintage data. Ten states over five fiscal years is 50 state-year cells, 48 of them with a usable FDI observation. Everything in the design follows from that constraint.

## Findings

**Debt predicts FDI between states.** States carrying persistently lower debt-to-GSDP attract significantly more FDI than their peers — roughly 17.6 per cent more per percentage point of lower debt. The relationship holds *across* states, not *within* a state from year to year; Section 7.1 of the paper argues fiscal discipline is a structural signal investors price, not a lever a finance department can pull in one budget.

The claim does not rest on one p-value. It rests on convergence:

| Evidence | Result |
|---|---|
| Pooled panel regression | −0.176 (cluster-robust p = 0.007; wild cluster bootstrap p = 0.057) |
| Specification curve | Negative in **88 of 88** pooled specifications |
| LASSO / Elastic Net | Debt is the largest standardised coefficient, and enters the regularisation path first |
| SHAP (random forest) | Debt ranks first in **10 of 10** leave-one-state-out refits |
| Permutation null | Importance margin reproduced by chance in 0.4 per cent of draws |

**Growth is associated with debt and own tax revenue, not with the deficit.** An earlier version of this work reported a significant deficit-growth effect (p = 0.031) under Driscoll-Kraay standard errors. That result does not survive a wild cluster bootstrap appropriate to ten clusters (p = 0.448) and is no longer claimed. Debt (p = 0.020) and own tax revenue (p = 0.028) do survive. This is a departure from Trivedi and Rajmal (2011) and Panda and Sahay (2022), and is read as a limit of a short panel rather than a contradiction of their longer ones.

**Two states depart from the pattern for identifiable reasons.** Jharkhand is fiscally mid-table with near-zero realised FDI — discipline appears necessary but not sufficient. Uttar Pradesh's apparent weakness is an artefact of DPIIT beginning its series in FY 2021-22.

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
```

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
| GSDP and growth | Ministry of Statistics and Programme Implementation (MoSPI), 2011-12 series |
| Literacy, urbanisation | Census of India 2011 |

Capital expenditure is derived as gross fiscal deficit minus revenue deficit, so it includes net lending — a limitation the paper discusses in Section 7.2. DPIIT began publishing state-wise FDI in October 2019, making FY 2019-20 a six-month flow; Uttar Pradesh's series begins FY 2021-22 and those two cells are missing, not zero.

## Limitations

Fifty state-year cells. Association, not causation — reverse causality cannot be excluded at T = 5. The debt measure is the on-budget figure and excludes off-budget borrowings and guarantees, which for Telangana have been estimated at 14-15 per cent of GSDP. The sample is the ten states that already receive almost all of India's FDI, so the result describes how investment sorts among states already in contention, not how a state enters that group.

## License

Research output. Underlying data is from public government sources; please cite the originating agencies listed above.
