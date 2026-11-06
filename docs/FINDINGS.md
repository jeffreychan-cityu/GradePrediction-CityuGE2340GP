# GE2340 Technical Findings

Use these results to support the [English analysis report v5](../GE2340_Data_Analysis_EN_v5.md) and prepare model comparisons. File paths are relative to the package root. Model inputs and shared settings are in [HANDOFF.md](HANDOFF.md).

Source: Charlotte Bennett1234, Kaggle dataset version 3. See [DATA_LICENSE.md](../DATA_LICENSE.md) for attribution and license references.

## Data audit

- 2,000 rows, 9 original columns; zero missing cells, duplicate full rows or duplicate Student_ID values.
- All observations were retained without imputation. `Grades` remains in its original units, with an observed range of 5.60–10.00. The theoretical grading scale is undocumented.
- Predictors: Study, Extracurricular, Sleep, Social and Physical Activity hours per day. Gender, Stress_Level and IDs excluded from model inputs.
- The five durations sum to 24 (floating-point tolerance). Centered training feature rank is 4, so coefficients for all five features plus an intercept would not be uniquely identifiable.

## Training-only EDA (n=1,200)

- Pearson correlation of Study hours with Grades: 0.7391.
- Physical Activity with Grades: −0.3614; Social: −0.1009; Extracurricular: 0.0024; Sleep: −0.0015.
- Study and Physical Activity correlate −0.5115. The fixed total links the activity durations, so these correlations describe associations within a constrained time allocation.
- Small pairwise correlations describe weak marginal linear associations with Grades. Nonlinear or conditional relationships would require separate evaluation.
- See `outputs/train_correlations.csv`, descriptive statistics and IQR flags. The pipeline retains observations flagged by the training IQR rule.

## Fixed baseline evaluation

Both baselines were fitted on training rows only and specified without test-based tuning. OLS uses a squared-error objective and the first four time features, with physical activity as the reference. The target retains its original units, and predictions are not clipped.

| Split | Model | MAE | RMSE | R² |
|---|---|---:|---:|---:|
| Validation (400) | Mean baseline |0.604939|0.744219|−0.000525|
| Validation (400) | Linear regression |0.410385|0.518293|0.514737|
| Test (400) | Mean baseline |0.565948|0.699383|−0.004431|
| Test (400) | Linear regression |0.372452|0.473131|0.540324|

MAE and RMSE use the original Grades units; R² is unitless. Page 1 of the submitted Phase 1 proposal specifies MSE, matching this OLS implementation. OLS meets its minimum value-prediction criterion, MAE(model) < MAE(mean baseline), on the fixed test split. These results describe this split; uncertainty across populations has not been estimated. The Softmax comparison awaits its experimental results. The neural-network comparison is an optional extension.

## Figure guide

Each figure is available as PNG and PDF in `outputs/figures/`. Page numbers below refer to the original report PDF; figure numbers also apply to the editable Markdown report.

| Report position | File stem | Contents |
|---|---|---|
| Figure 1, page 2 | `01_distributions_train` | Five predictors and Grades, training rows only |
| Figure 2, page 3 | `02_correlations_train` | Training Pearson correlations |
| Supplement referenced in Section 3 | `03_relationships_train` | Each time predictor against Grades, training rows only |
| Figure 3, page 5 | `04_validation_diagnostics` | Observed versus predicted Grades and validation residuals |
| Additional package figure | `05_class_distribution_train` | Training relative-grade distribution |

## Project-defined classification groups

These outputs were introduced in v2 and are included in the current v3 package.

The selected training-only quintile boundaries are fixed: F<7.10; D[7.10,7.55); C[7.55,8.00); B[8.00,8.45); A>=8.45. These project-defined groups express relative standing; F denotes the lowest group rather than an official failure category. Scores on a boundary enter the higher group, and equal scores share a label. Grades remains in its original units.

| Group | Train | Validation | Test |
|---|---:|---:|---:|
| F |238|69|59|
| D |236|79|78|
| C |234|99|104|
| B |249|62|75|
| A |243|91|84|

B is the most frequent training class, so the majority baseline predicts B for every observation in each split. Validation accuracy is 0.155, macro-F1 is 0.05367965 and balanced accuracy is 0.20. Test accuracy is 0.1875, macro-F1 is 0.06315789 and balanced accuracy is 0.20. Macro-F1 averages all five classes, with undefined precision/F1 set to zero. The fixed split retains the observed differences in class counts.

Test labels, class counts and fixed baseline metrics were examined in v2. These results were not used to change boundaries, splits or model settings. Softmax results are pending; the NN experiment is optional. V3 records verification that MSE/OLS matches the submitted Phase 1 PDF uploaded by the user; the existing OLS method is retained.
