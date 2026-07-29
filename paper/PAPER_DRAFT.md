Fiscal Discipline and Investment Outcomes: Panel Evidence and Machine-Learning Validation from India's Top Ten FDI-Recipient States, FY 2019-20 to FY 2023-24

[Author name], [Affiliation]
Corresponding author: [email]

ABSTRACT

Ten Indian states account for roughly 97 per cent of the country's recorded foreign direct investment (FDI) equity inflows, yet no published study has tested whether the fiscal discipline of these states — their deficits, debt, own-revenue effort and capital spending — helps explain the investment they attract. This paper builds a balanced panel of India's ten largest FDI-recipient states over five fiscal years (2019-20 to 2023-24) from Sixteenth Finance Commission and CAG-audited state finance accounts, and estimates two panel regressions: log FDI and GSDP growth on four fiscal indicators plus a COVID-19 dummy. A pooled specification with Census controls shows that a one-percentage-point-lower debt-to-GSDP ratio is associated with roughly 18 per cent higher FDI (coefficient -0.176, p = 0.007, between R² = 0.87). Within states over time, higher deficits are associated with significantly lower GSDP growth (coefficient -2.17, p = 0.031). Because the panel is short (T = 5) and dominated by a single pandemic shock, we cross-check the debt-FDI finding with LASSO, Elastic Net and SHAP-based random forest importance on the same five fiscal regressors; all three methods independently rank debt-to-GSDP as the dominant fiscal predictor, with a stability check confirming this ranking survives every leave-one-state-out refit. Jharkhand is the one state where fiscal discipline and FDI performance diverge sharply, and Uttar Pradesh's FDI series is left-censored before FY 2021-22; both cases are examined directly rather than dropped silently. The results support treating sub-national fiscal discipline as a structural, between-state signal to investors rather than a year-to-year lever, with direct implications for how state governments and the Finance Commission frame fiscal consolidation.

Keywords: fiscal discipline, foreign direct investment, sub-national public finance, panel data, India, LASSO, SHAP

1. INTRODUCTION

India's foreign direct investment is geographically lopsided. Since the Department for Promotion of Industry and Internal Trade (DPIIT) began publishing state-wise FDI equity figures in October 2019, ten states have absorbed close to 97 per cent of the total. Maharashtra, Karnataka and Gujarat alone routinely take half of it. This concentration invites an obvious question: what distinguishes the states that attract capital from those that do not, and does the answer include anything a state finance department actually controls?

Two strands of research bear on this question without meeting each other. The first studies the effect of state-level fiscal policy on growth. Trivedi and Rajmal (2011) find that fiscal deficits contract growth across fourteen Indian states using fixed-effects panel methods; Panda and Sahay (2022) extend this to seventeen states over 2004-05 to 2016-17 and reach the same conclusion using both fixed effects and two-stage least squares. Neither paper considers FDI. The second strand studies what draws FDI to Indian states, and it is dominated by infrastructure, market size and agglomeration variables (Mahatekar, 2025), with fiscal indicators appearing, if at all, as controls rather than the object of study. A parallel literature on state debt sustainability (Misra, Gupta and Trivedi, 2021; NIPFP, 2024) evaluates whether current borrowing paths are solvent, again without linking debt levels to the investment a state subsequently attracts. The NITI Aayog's Fiscal Health Index (2025, 2026) ranks states on fiscal metrics but is not validated against any downstream economic outcome — it assumes fiscal health matters without testing whether it correlates with anything investors actually do.

This paper closes that gap directly. Using a balanced panel of India's ten largest FDI-recipient states over five fiscal years — the most recent window for which audited, comparable state finance data exist, and one that happens to bracket the COVID-19 shock — we ask whether fiscal deficit, public debt, own tax revenue and capital expenditure, each measured as a share of state GSDP, predict (a) the FDI a state receives and (b) the GSDP growth it records. We estimate both relationships with two panel specifications — entity fixed effects with Driscoll-Kraay standard errors, and pooled OLS with time-invariant Census controls — so that the within-state and between-state dimensions of the relationship can be told apart, which turns out to matter a great deal for how the results should be read.

Because the panel is short and one of its five years is an extreme, common shock, we do not stop at the regression. We rerun the same prediction problem through LASSO, Elastic Net, and SHAP values from a shallow random forest, methods chosen specifically because they remain credible at n = 48 where instrument-heavy panel GMM estimators are not (Roodman, 2009). If a regularised linear selector, a non-linear tree-based explainer, and a fixed-effects panel regression converge on the same variable, that convergence is worth more than any one method's p-value. We also disclose a methodological pitfall we ran into and corrected: an initial SHAP specification that included the time-invariant Census literacy and urbanisation controls let the random forest use urbanisation as a disguised state identifier, artificially inflating its apparent importance. Excluding both controls and restricting the machine-learning stage to the same five time-varying regressors used in the fixed-effects model removes this leakage; we report both the leakage diagnosis and the corrected results, since the pitfall itself is informative for anyone applying tree-based methods to short state panels.

The paper proceeds as follows. Section 2 reviews the relevant literature and states the two hypotheses. Section 3 describes the data and the four methodological stages. Section 4 reports the descriptive statistics, the panel regressions, the robustness checks, and the machine-learning validation. Section 5 discusses what the results mean, in particular the between-state versus within-state contrast and the Jharkhand and Uttar Pradesh cases. Section 6 concludes with policy implications and limitations.

2. LITERATURE REVIEW AND HYPOTHESES

2.1 Fiscal discipline and growth

The growth effects of state-level fiscal deficits in India are reasonably well established. Trivedi and Rajmal (2011) use a fixed-effects panel across fourteen major states and find that gross fiscal deficits reduce subsequent growth, working through crowding out of private investment and higher borrowing costs. Panda and Sahay (2022) revisit the question for seventeen states between 2004-05 and 2016-17 with both fixed effects and two-stage least squares to address possible reverse causality, and again find deficits detrimental to growth. Misra, Gupta and Trivedi (2021) shift the focus from deficits to debt stocks, examining the sustainability of state debt once off-budget guarantees are included, but stop short of linking debt sustainability to any investment outcome. The NIPFP's threshold-regression working paper (2024) estimates the debt level beyond which growth effects turn negative for major states, again without an FDI channel.

2.2 Fiscal discipline and FDI

The FDI-determinants literature, by contrast, is built almost entirely around agglomeration economics: existing industrial clusters, port and highway access, labour market depth, and the size of the state's own consumer market (Mahatekar, 2025). Cross-country work on fiscal federalism and FDI does exist — Feld et al. (2024) find that fiscally healthier sub-national and national governments attract more mobile capital in a panel of federal economies — but this evidence has not been tested within India, where states share a currency, a central bank, and most regulatory settings, and therefore compete on a narrower set of levers than countries do.

Three channels motivate why fiscal discipline might still matter for FDI even inside a currency union. A signalling channel: low deficits and sustainable debt tell an investor that a state government is unlikely to resort to distortionary taxation or expenditure compression in a crisis, reducing perceived policy risk (Misra, Gupta and Trivedi, 2021). A crowding-in channel: capital expenditure that is actually spent on infrastructure lowers the cost of doing business, and a state that can fund capex without borrowing heavily demonstrates administrative capacity as much as fiscal virtue. A competition channel: with a limited pool of mobile capital, states with fiscal headroom can credibly commit to honouring incentive packages, land arrangements and regulatory promises over a project's life, while a fiscally stressed state cannot (Feld et al., 2024). Against all three sits the agglomeration hypothesis, under which FDI simply goes where FDI already is, irrespective of the host government's balance sheet. We address this rival explanation with state fixed effects, which absorb any time-invariant structural advantage a state holds, and with the SHAP analysis, which can in principle let a location-fixed variable dominate if agglomeration is in fact doing all the work.

2.3 The gap

Table 1 [narrative] summarises where the two literatures stop short of each other: growth studies that omit FDI, FDI studies that omit fiscal variables, debt-sustainability studies that omit any investment outcome, and a fiscal ranking (NITI Aayog's Fiscal Health Index) that is not validated against any outcome at all. No study, to our knowledge, uses Indian state fiscal indicators as direct predictors of state-wise FDI, and none corroborates a sub-national fiscal-investment relationship with machine-learning methods, an increasingly standard robustness step in applied economics (see, e.g., Athey and Imbens, 2019, on the broader case for ML as a complement to causal inference) but one not yet applied to Indian state finance research.

2.4 Hypotheses

H1: Fiscal discipline (lower deficit and debt, higher own tax revenue and capital expenditure) is significantly associated with higher state-wise FDI inflows.

H2: Fiscal discipline is significantly associated with state-wise GSDP growth.

The null in each case is no significant association. Both are tested twice — within states over time and between states — because, as the results below show, the two dimensions answer different questions and, in the case of H1, point in different directions for a substantive and explicable reason.

3. DATA AND METHODOLOGY

3.1 Sample

The sample is a balanced panel of ten states — Maharashtra, Karnataka, Gujarat, Tamil Nadu, Haryana, Telangana, Jharkhand, Rajasthan, West Bengal and Uttar Pradesh — chosen because they are the ten largest recipients of FDI equity inflows in DPIIT's state-wise series, over five fiscal years, FY 2019-20 to FY 2023-24 (50 state-year cells). Forty-eight of these fifty cells carry a usable FDI observation; Uttar Pradesh's two earliest years are missing rather than zero, because DPIIT's state-wise reporting for Uttar Pradesh only begins in FY 2021-22. We treat this as left-censoring, not as a true absence of investment, and test its influence directly in the robustness checks (Section 4.4).

3.2 Variables

All four fiscal indicators are computed as a percentage of state GSDP from the Sixteenth Finance Commission's Volume II annexures (Chapter 5), which in turn derive from CAG-audited State Finance Accounts: gross fiscal deficit, outstanding liabilities (debt), own tax revenue, and capital expenditure, the last derived as gross fiscal deficit minus revenue deficit and therefore inclusive of net lending as well as pure capital outlay. GSDP itself is MoSPI's comparable 2011-12-series figure. FDI equity inflows by state come from DPIIT and are converted to natural logs for the regression (log FDI); GSDP growth is computed year-on-year from the same MoSPI series. A COVID dummy equals one for FY 2020-21. Two Census 2011 controls — literacy and urbanisation — are included only in the pooled cross-state specification, where they proxy for time-invariant structural characteristics that the fixed-effects model already absorbs by construction. Table 1 reports descriptive statistics for the full panel.

TABLE 1. Descriptive statistics (N = 50, FDI/log FDI N = 48)
Variable | Mean | SD | Min | Median | Max
Fiscal deficit (% GSDP) | 2.82 | 1.26 | -0.70 | 3.10 | 5.40
Debt (% GSDP) | 28.82 | 6.55 | 17.60 | 29.55 | 42.50
Own tax revenue (% GSDP) | 6.47 | 0.80 | 5.20 | 6.30 | 8.20
Capital expenditure (% GSDP) | 2.27 | 1.01 | 0.10 | 1.90 | 4.60
Revenue deficit (% GSDP) | 0.54 | 1.77 | -4.00 | 0.60 | 3.90
FDI (Rs crore) | 31,194 | 43,933 | 44 | 12,884 | 163,795
GSDP growth (% p.a.) | 10.39 | 7.35 | -4.38 | 11.41 | 26.76

The debt-to-GSDP range (17.6 to 42.5 per cent) already hints at the cross-state story: a fourteen-point spread among just ten states over five years is large relative to the mean, and it is not evenly distributed — West Bengal and Rajasthan anchor the high end, Gujarat and Maharashtra the low end, a pattern that reappears in every result below.

3.3 Econometric specification

Two models are estimated:

Model 1: ln(FDI)_it = a_i + b1 FD_it + b2 DEBT_it + b3 OTR_it + b4 CAPEX_it + b5 COVID_t + e_it

Model 2: GROWTH_it = a_i + g1 FD_it + g2 DEBT_it + g3 OTR_it + g4 CAPEX_it + g5 COVID_t + v_it

where i indexes state and t indexes fiscal year. Each model is estimated twice: as an entity fixed-effects panel with Driscoll-Kraay standard errors, robust to cross-sectional dependence and serial correlation in a panel this short (Driscoll and Kraay, 1998), which identifies the within-state relationship; and as a pooled OLS with the two Census controls added and standard errors clustered by state, which identifies the between-state relationship. Variance inflation factors are computed for the four fiscal regressors to check for multicollinearity given that fiscal deficit and debt are mechanically related (a state's stock of debt is the accumulation of past deficits). Instrument-heavy dynamic panel estimators (difference or system GMM) are deliberately not used: with N = 10 and T = 5, the instrument count in a standard Arellano-Bond setup would approach or exceed the number of cross-sectional units, a configuration Roodman (2009) flags as unreliable.

3.4 Machine-learning validation

Panel regression on ten states and five years rests on thirty-three to forty residual degrees of freedom, and one of the five years is dominated by a single, extreme, common shock. A single specification's p-value is thin support for a policy claim in that setting. We therefore validate the debt-FDI finding with three additional, methodologically independent lenses, all chosen because they are appropriate — rather than merely fashionable — at this sample size:

(a) LASSO regression with leave-one-out cross-validated regularisation strength, which asks which regressors survive shrinkage rather than which cross a p < 0.05 threshold;

(b) Elastic Net as a cross-check on the LASSO selection, since the two penalise correlated regressors differently;

(c) A shallow random forest (1,000 trees, maximum depth 3, minimum leaf size 4 — depth and leaf constraints chosen specifically to prevent a forest with 48 training rows from memorising individual states) with SHAP (SHapley Additive exPlanations; Lundberg and Lee, 2017) values, which ranks predictors by their average marginal contribution to each individual prediction and can, unlike a linear model, in principle detect a non-linear or threshold effect.

All three are restricted to the same five time-varying regressors as the fixed-effects econometric model (fiscal deficit, debt, own tax revenue, capital expenditure, COVID dummy). This restriction was not the first choice: an initial SHAP run that also included the two time-invariant Census controls ranked urbanisation as the most important predictor by a wide margin (mean |SHAP| = 1.30, against 0.25 for debt, the next-highest variable). On inspection this reflected a known failure mode of tree-based models rather than a real urbanisation effect: because urbanisation is fixed within a state across all five years, the random forest could use it as a near-unique fingerprint for which state a given observation belonged to, effectively re-learning the state fixed effect through the back door rather than a genuine fiscal or structural relationship. We report this diagnosis rather than hide it, since it is a useful caution for any future application of tree-based importance methods to short, few-entity panels, and we rerun Part B with literacy and urbanisation excluded; the results in Section 4.5 are from that corrected specification. A leave-one-state-out stability check (ten refits, each excluding one state) is run on both the LASSO selection and, implicitly, the small sample underlying SHAP, to confirm that no single state is driving the ranking. Finally, leave-one-out cross-validated out-of-sample R² is computed for OLS, LASSO and the random forest, not to claim predictive power at n = 48 but to report honestly how much of that power exists.

4. RESULTS

4.1 Fiscal discipline ranking

Ranking the ten states each year on a composite of the four fiscal indicators produces a remarkably stable ordering (Table 2). Maharashtra and Uttar Pradesh share the best five-year average rank (2.2), followed by Telangana and Gujarat (3.4) and Karnataka (4.2). Jharkhand sits in the middle (5.8). Tamil Nadu, Haryana and Rajasthan cluster below (7.2 to 8.6), and West Bengal is last in every single year of the panel, the only state with a perfect run at rank 10.

TABLE 2. Fiscal discipline rank by year (1 = most disciplined)
State | FY20 | FY21 | FY22 | FY23 | FY24 | 5-yr avg
Maharashtra | 2 | 3 | 1 | 3 | 2 | 2.2
Uttar Pradesh | 1 | 1 | 2 | 4 | 3 | 2.2
Telangana | 4 | 4 | 3 | 2 | 4 | 3.4
Gujarat | 5 | 5 | 5 | 1 | 1 | 3.4
Karnataka | 3 | 2 | 4 | 6 | 6 | 4.2
Jharkhand | 6 | 7 | 6 | 5 | 5 | 5.8
Tamil Nadu | 7 | 6 | 8 | 7 | 8 | 7.2
Haryana | 8 | 8 | 9 | 8 | 7 | 8.0
Rajasthan | 9 | 9 | 7 | 9 | 9 | 8.6
West Bengal | 10 | 10 | 10 | 10 | 10 | 10.0

Gujarat's climb from rank 5 in FY 2019-20 to rank 1 in both FY 2022-23 and FY 2023-24, and Uttar Pradesh's slide from rank 1 to rank 3 over the same window, are the two largest year-on-year movements in the panel and both feature directly in the discussion below.

4.2 Panel regressions: FDI (Model 1)

The fixed-effects specification (n = 48, within R² = 0.429, F(5,33) = 4.96, p = 0.0017) explains within-state variation in log FDI. Fiscal deficit (coefficient 0.566, p < 0.001), debt (0.353, p < 0.001) and the COVID dummy (-1.406, p < 0.001) are all significant; own tax revenue and capital expenditure are not (Table 3). A poolability F-test strongly rejects the null of no entity effects (F(9,33) = 6.74, p < 0.001), confirming that state fixed effects are doing real work in this model and that pooling would be misspecified here.

The pooled specification with Census controls (n = 48, R² = 0.643, between R² = 0.874, F(7,40) = 10.29, p < 0.001) tells a different, and for the paper's central claim more important, story. Debt is significantly negative (coefficient -0.176, standard error 0.062, t = -2.84, p = 0.0071): a one-percentage-point-lower debt-to-GSDP ratio is associated with roughly 17.6 per cent higher FDI, holding the other regressors and the Census controls fixed. Literacy is also significant (0.101, p = 0.035); capital expenditure is negative and significant in this specification too (-0.366, p = 0.008), a result discussed below; fiscal deficit, own tax revenue, the COVID dummy, and urbanisation are not significant at conventional levels.

TABLE 3. Model 1 — log(FDI), fixed effects and pooled OLS
Variable | FE+DK coef | FE+DK p | Pooled coef | Pooled p
Fiscal deficit | 0.566 | 0.000 | 0.567 | 0.265
Debt-to-GSDP | 0.353 | 0.000 | -0.176 | 0.007
Own tax revenue | 0.107 | 0.684 | 0.325 | 0.268
Capital expenditure | -0.173 | 0.571 | -0.366 | 0.008
COVID dummy | -1.406 | 0.000 | 0.547 | 0.161
Literacy | — | — | 0.101 | 0.035
Urbanisation | — | — | 0.005 | 0.909
R² (within / overall) | 0.429 | | 0.643 | |
R² (between) | -4.49 | | 0.874 | |

The sign reversal on debt between the two specifications is the paper's central empirical fact and is addressed at length in Section 5.1; it is not a coding error or a contradiction, and both coefficients are individually well estimated.

4.3 Panel regressions: GSDP growth (Model 2)

For growth, the fixed-effects specification (n = 50, within R² = 0.689, F(5,35) = 15.53, p < 0.001) shows fiscal deficit significantly negative (coefficient -2.172, p = 0.031) and debt significantly positive (1.097, p = 0.028); the COVID dummy is large and negative (-13.783, p < 0.001), consistent with the roughly 14-percentage-point growth collapse the panel records in FY 2020-21. Unlike Model 1, the poolability test for the growth equation does not reject pooling (F(9,35) = 0.82, p = 0.603), meaning the state fixed effects contribute comparatively little explanatory power once the fiscal variables and the COVID dummy are already in the equation — growth, unlike the level of FDI a state attracts, is driven mostly by within-state shocks common to fiscal conditions and the pandemic rather than by fixed state characteristics.

TABLE 4. Model 2 — GSDP growth, fixed effects and pooled OLS
Variable | FE+DK coef | FE+DK p | Pooled coef | Pooled p
Fiscal deficit | -2.172 | 0.031 | -1.435 | 0.340
Debt-to-GSDP | 1.097 | 0.028 | 0.258 | 0.247
Own tax revenue | 4.083 | 0.101 | 1.627 | 0.071
Capital expenditure | -0.356 | 0.775 | -0.323 | 0.722
COVID dummy | -13.783 | 0.000 | -12.662 | 0.000
Literacy | — | — | -0.172 | 0.373
Urbanisation | — | — | 0.199 | 0.149
R² (within / overall) | 0.689 | | 0.641 | |

The pooled growth specification (n = 50, R² = 0.641, F(7,42) = 10.70, p < 0.001) is dominated by the COVID dummy (-12.662, p < 0.001); none of the four fiscal variables reach significance in this cross-state form, own tax revenue coming closest (1.627, p = 0.071). H2's support therefore comes specifically from the within-state, fixed-effects estimate, not from the cross-state comparison — the mirror image of the debt-FDI pattern in Model 1.

4.4 Diagnostics and robustness

Variance inflation factors for the four fiscal regressors range from 1.33 (capital expenditure) to 1.69 (debt), all comfortably below the conventional concern threshold of five, despite the mechanical link between deficits and debt (pairwise correlation 0.533; Table 5). Multicollinearity is not a threat to either model's coefficient estimates.

TABLE 5. Variance inflation factors
Variable | VIF
Fiscal deficit | 1.52
Debt-to-GSDP | 1.69
Own tax revenue | 1.51
Capital expenditure | 1.33

Table 6 reports the within-state deficit and debt coefficients from Model 1 under three perturbations of the sample. Dropping the COVID year (n = 39) leaves both coefficients stable in sign and significance (deficit 0.802, p = 0.017; debt 0.324, p = 0.002). Dropping Uttar Pradesh (n = 45) barely moves either estimate (deficit 0.532, p < 0.001; debt 0.366, p < 0.001), which matters because it shows the left-censoring in UP's FDI series discussed in Section 3.1 is not driving the within-state result. Dropping Jharkhand (n = 43), by contrast, flips the deficit coefficient's sign and removes its significance entirely (-0.310, p = 0.141), while the debt coefficient survives, smaller but still significant (0.182, p = 0.015). Jharkhand alone is therefore responsible for a meaningful share of the within-state deficit-FDI pattern; Section 5.3 examines why.

TABLE 6. Robustness of Model 1 within-state coefficients
Specification | n | Deficit coef | Deficit p | Debt coef | Debt p
Baseline | 48 | 0.566 | 0.000 | 0.353 | 0.000
Excl. COVID year | 39 | 0.802 | 0.017 | 0.324 | 0.002
Excl. Jharkhand | 43 | -0.310 | 0.141 | 0.182 | 0.015
Excl. Uttar Pradesh | 45 | 0.532 | 0.000 | 0.366 | 0.000

4.5 Machine-learning validation

The corrected specification (Section 3.4) restricts LASSO, Elastic Net and SHAP to the five time-varying fiscal regressors and re-estimates all three on the same 48 observations. LASSO, with its penalty strength chosen by leave-one-out cross-validation (alpha = 0.0011, a light penalty under which all five regressors survive), assigns debt-to-GSDP by far the largest standardised coefficient (-1.571), roughly twice the size of the next-largest, capital expenditure (-0.697); Elastic Net agrees closely (debt -1.478, capex -0.679; Table 7). The leave-one-state-out stability check selects debt in all ten refits, alongside capital expenditure and own tax revenue; only fiscal deficit is dropped in one of the ten refits.

TABLE 7. LASSO and Elastic Net, five fiscal predictors (standardised)
Variable | LASSO coef | Elastic Net coef | Selected in all 10 leave-one-state-out refits
Debt-to-GSDP | -1.571 | -1.478 | Yes
Fiscal deficit | 0.728 | 0.652 | 9 of 10
Capital expenditure | -0.697 | -0.679 | Yes
COVID dummy | 0.220 | 0.225 | Yes
Own tax revenue | 0.157 | 0.174 | Yes

SHAP values from the corrected random forest (out-of-bag R² = 0.402) rank debt-to-GSDP first among the five predictors by a wide margin: mean |SHAP| = 1.029, against 0.219 for fiscal deficit, 0.208 for own tax revenue, 0.136 for capital expenditure, and an effectively negligible 0.007 for the COVID dummy (Table 8). The SHAP beeswarm plot (Figure M3) shows the direction is consistent with the pooled regression: observations with high debt values sit on the negative side of the SHAP axis, meaning high debt pushes the model's predicted FDI down, and low-debt observations push it up.

TABLE 8. SHAP importance, five fiscal predictors (random forest)
Variable | Mean |SHAP|
Debt-to-GSDP | 1.029
Fiscal deficit | 0.219
Own tax revenue | 0.208
Capital expenditure | 0.136
COVID dummy | 0.007

Leave-one-out out-of-sample R² is modest for all three models, as expected at n = 48: 0.440 for OLS, 0.416 for LASSO, 0.395 for the random forest (Table 9). None of the three should be read as demonstrating predictive power; the exercise is a validation of the in-sample ranking, not a forecasting claim, and the similarity of the three numbers is itself informative — it indicates that the extra flexibility of the random forest is not buying additional out-of-sample accuracy at this sample size, consistent with a relationship that is close to linear once debt is accounted for.

TABLE 9. Leave-one-out out-of-sample R²
Model | LOO-CV R²
OLS | 0.440
LASSO | 0.416
Random forest | 0.395

Three methodologically independent approaches — a pooled panel regression, a regularised linear selector, and a non-linear tree-based explainer — therefore converge on debt-to-GSDP as the dominant fiscal predictor of cross-state FDI, always with the same negative sign. This convergence is the paper's strongest evidence for H1 in its cross-state form, because it does not depend on any single model's distributional assumptions or on treating a p = 0.007 result as sufficient on its own in a panel this short.

5. DISCUSSION

5.1 Why debt is negative between states and positive within them

The central empirical puzzle in Section 4.2 is that debt enters Model 1 with a negative, significant coefficient in the pooled cross-state specification and a positive, significant coefficient in the within-state fixed-effects specification. Both are correctly estimated; they are answering different questions. The pooled coefficient asks: does a state that persistently carries less debt than its peers attract more FDI than they do? The answer is yes, and the size of the effect — about 18 per cent more FDI per percentage point of lower debt-to-GSDP — lines up with the discipline ranking in Table 2, where the two lowest-debt states in the panel, Gujarat and Maharashtra, are also consistently ranked first or second overall, while the highest-debt state, West Bengal, is ranked last every year.

The fixed-effects coefficient asks a narrower question: within a given state, in the years when its own debt ratio rose relative to its own average, did its own FDI also rise? Here the answer is also yes, but for a reason that has nothing to do with fiscal virtue: the panel has only five years, and one of them, FY 2020-21, is a pandemic year in which every state's deficit and debt jumped simultaneously with a national FDI collapse, followed by a national FDI recovery in FY 2021-22 and FY 2022-23 that happened to coincide, in several states, with continued elevated debt from pandemic-era borrowing. Gujarat's FDI surge in FY 2020-21 and Karnataka's in FY 2021-22 both occurred in years when debt was still above pre-pandemic levels nationally. With only five time periods, a single common shock of this size can dominate the within-state covariance between any two variables that both moved sharply around it, and debt and the post-pandemic FDI recovery are exactly such a pair. This is a known limitation of short panels rather than a flaw specific to this dataset, and it is precisely why the paper reports both specifications rather than the more favourable one alone.

The practical reading we draw from this contrast is that fiscal discipline functions as a structural, between-state signal that investors use to compare states against each other, rather than a lever a single state can pull in a given budget year to move its own FDI inflows. A finance department that reduces its deficit by half a percentage point this year should not expect that action alone to move next year's FDI number; a state that has held debt below 25 per cent of GSDP for five consecutive years is operating in a different competitive tier than one that has not, and the market appears to price that difference.

5.2 Capital expenditure's negative sign

Capital expenditure is negative and significant in the pooled FDI specification (-0.366, p = 0.008), which runs against the crowding-in channel outlined in Section 2.2. Two features of the capex measure explain this without requiring us to reject the channel outright. First, capital expenditure here is derived (gross fiscal deficit minus revenue deficit) and therefore includes net lending; a state that lends heavily to public-sector undertakings shows high derived capex without necessarily building investment-relevant infrastructure. Second, and more directly, capex and debt are correlated in this sample in the wrong direction for the crowding-in story: several of the higher-debt, lower-FDI states in the panel also record higher derived capex, because capital spending financed by borrowing shows up as capex even when the borrowing itself is the more informative signal to an investor. The pooled coefficient on capex should therefore be read alongside debt rather than in isolation; a state that finances capex through low debt is a different signal from a state that finances the same nominal capex through high debt, and the current specification cannot separate the two within a single linear coefficient. This is a genuine limitation of the specification, flagged rather than smoothed over, and a natural extension for future work with a longer panel is to interact capex with the debt-financing share directly.

5.3 The Jharkhand and Uttar Pradesh cases

Jharkhand is the clearest case in the panel of fiscal discipline not translating into investment. It occupies the middle of the discipline ranking (5.8 of 10 on the five-year average, ahead of Tamil Nadu, Haryana, Rajasthan and West Bengal) while recording one of the sharpest FDI trajectories in the sample: a spike in FY 2019-20 followed by a near-total collapse from FY 2020-21 onward. Table 6 shows that removing Jharkhand from the sample flips the within-state deficit coefficient from significantly positive to statistically indistinguishable from zero, meaning Jharkhand's specific path — rising deficit alongside collapsing FDI, the opposite of the pattern in states like Gujarat and Karnataka discussed in Section 5.1 — is doing real work in the within-state estimate. Substantively, this is a useful negative case rather than a nuisance to be dropped: fiscal discipline appears to be a necessary condition investors screen for, but Jharkhand demonstrates it is not sufficient on its own, and factors this paper does not model directly — political transition, mining-sector-specific investment cycles, and infrastructure gaps relative to the western and southern states in the sample — plausibly explain the residual.

Uttar Pradesh presents a different kind of anomaly: its DPIIT-reported FDI series begins only in FY 2021-22, so its first two panel years are missing rather than genuinely zero. Because Uttar Pradesh's discipline rank is high throughout (2.2 on the five-year average, tied for best in the sample), a naive reading might worry that this censoring inflates the debt-FDI relationship by association. Table 6 rules this out directly: excluding Uttar Pradesh entirely leaves both the deficit and debt coefficients within a few hundredths of their baseline values and equally significant. The debt-FDI relationship in this panel is not an artefact of how Uttar Pradesh happens to be recorded.

5.4 What the agglomeration rival hypothesis survives

Section 2.2 raised agglomeration — FDI following existing industrial clusters regardless of a host government's fiscal position — as the main rival explanation for any debt-FDI correlation. The evidence here does not resolve that debate so much as locate fiscal discipline within it. The initial, uncorrected SHAP specification (Section 3.4), which included Census urbanisation as a predictor, ranked urbanisation far above every fiscal variable (mean |SHAP| = 1.30 against 0.25 for debt), and while part of that gap reflects the state-identity leakage problem diagnosed and corrected, part of it is plausibly a genuine agglomeration signal: urbanisation is, after all, a reasonable proxy for exactly the clustering and market-size effects the rival hypothesis describes. Once the machine-learning stage is restricted to the fiscal variables that vary within a state over time — the same set the fixed-effects econometric model uses — debt is unambiguously dominant among them. The honest synthesis is that agglomeration and fiscal discipline are not competing explanations so much as operating at different levels: structural, largely fixed advantages of geography and existing industrial base plausibly explain most of the variation in which states are in the top ten at all, while fiscal discipline operates as a second-order signal that helps sort investment among that already-favoured group, consistent with the between-state result in Section 4.2 and inconsistent with a story in which fiscal policy is irrelevant once agglomeration is accounted for.

6. CONCLUSION AND POLICY IMPLICATIONS

Sub-national fiscal discipline is associated with more FDI in India, but the relationship holds between states rather than within them over the five years examined here. States that have kept debt low relative to GSDP — Gujarat and Maharashtra foremost among the ten studied — attract significantly more FDI than states that have not, a finding replicated by a pooled panel regression, LASSO, Elastic Net, and SHAP-based random forest importance, four methods that share no common statistical assumption beyond the same 48 observations. Fiscal deficit is separately associated with lower GSDP growth within states over time, replicating Trivedi and Rajmal (2011) and Panda and Sahay (2022) on a newer, audited, post-pandemic panel.

For state finance departments, the direct implication is that fiscal consolidation should be evaluated as a multi-year credibility investment rather than a single-budget lever: the FDI market appears to reward a state's persistent position relative to its peers, not its year-on-year deficit arithmetic. For the Finance Commission and for national investment-promotion bodies, the results suggest that a fiscal discipline ranking is more informative when it is validated against an actual investment outcome, as done here, than when it is reported as an end in itself, which is the current practice of indices such as the NITI Aayog's Fiscal Health Index. The Jharkhand case is a caution against reading any such ranking mechanically: discipline appears necessary but is demonstrably not sufficient, and a state government that improves its fiscal position without addressing the sector- and region-specific frictions an investor also weighs should not expect FDI to follow automatically.

Three limitations bound these conclusions. The panel is short — fifty state-year cells, forty-eight with a usable FDI observation — which is why the paper leans on convergent machine-learning evidence rather than the panel regression's p-values alone, and why instrument-heavy dynamic panel GMM estimators were excluded by design as inappropriate at this N and T (Roodman, 2009). FDI recording itself is imperfect: DPIIT's state-wise series only begins in October 2019, making FY 2019-20 a six-month flow and Uttar Pradesh's series left-censored until FY 2021-22, a data limitation addressed but not eliminated by the robustness check in Table 6. And the debt measure used here, drawn from CAG-audited state finance accounts, is the official on-budget figure; it excludes off-budget borrowings and guarantees, which for at least one state in the sample — Telangana, where such liabilities have been estimated at roughly 14 to 15 per cent of GSDP — are large enough to matter for a true assessment of fiscal risk. Association, not causation, is what a five-year panel of ten states can support; reverse causality, in which anticipated FDI itself changes a state's fiscal behaviour, cannot be excluded with this design.

Future work with a longer panel, once more post-pandemic years are available, could test whether the within-state debt coefficient converges toward the between-state sign as the COVID shock recedes from the estimation window, which the discussion in Section 5.1 predicts it should. Extending the debt measure to include off-budget guarantees, and interacting capital expenditure with its financing source, are both natural next steps given the specification limits identified in Sections 5.2 and 6.

REFERENCES

Athey, S., & Imbens, G. W. (2019). Machine learning methods that economists should know about. Annual Review of Economics, 11, 685-725.

Driscoll, J. C., & Kraay, A. C. (1998). Consistent covariance matrix estimation with spatially dependent panel data. Review of Economics and Statistics, 80(4), 549-560.

Feld, L. P., et al. (2024). Fiscal federalism and foreign direct investment: An empirical analysis. The World Economy.

Government of India. (2025). Report of the Sixteenth Finance Commission, Volume II: Annexures. Ministry of Finance.

Lundberg, S. M., & Lee, S.-I. (2017). A unified approach to interpreting model predictions. Advances in Neural Information Processing Systems, 30.

Mahatekar, R. (2025). State-wise FDI flows and economic impacts in India (2019-2024). JETIR.

Misra, S., Gupta, K., & Trivedi, P. (2021). Sub-national government debt sustainability in India. Macroeconomics and Finance in Emerging Market Economies.

NIPFP. (2024). How much debt is optimal for the major Indian states? Working Paper No. 411. National Institute of Public Finance and Policy.

NITI Aayog. (2025). Fiscal Health Index 2025. Government of India.

Panda, D., & Sahay, A. (2022). Determinants of economic growth across states in India. Springer India Studies in Business and Economics.

Reserve Bank of India. (various years). State finances: A study of budgets. RBI, Mumbai.

Roodman, D. (2009). How to do xtabond2: An introduction to difference and system GMM in Stata. Stata Journal, 9(1), 86-136.

Tibshirani, R. (1996). Regression shrinkage and selection via the LASSO. Journal of the Royal Statistical Society, Series B, 58(1), 267-288.

Trivedi, P., & Rajmal. (2011). Growth effects of fiscal policy of Indian states. Margin: The Journal of Applied Economic Research, 5(2).
