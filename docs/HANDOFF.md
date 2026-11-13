# GE2340 Technical Handoff

This handoff separates Alex's completed data and baseline work from Jeffrey's model tasks. It accompanies the v3 data and code and the [English analysis report v6](../GE2340_Data_Analysis_EN_v6.md). Paths are relative to the package root.

**Jeffrey: start with Part B for your tasks, input files and deliverables.** Part A records Alex's completed work; Part C defines the shared inputs and labels.

## Part A — Alex: completed work and supplied materials

### Completed data preparation and baselines

- Data quality checks on the five daily time-use predictors, missing values, duplicate records and student IDs. All 2,000 records are retained, with no imputation.
- A fixed split of 1,200 training, 400 validation and 400 test records using seed 2340, with stable row IDs.
- Standardization fitted on training predictors and applied unchanged to validation and test data.
- Training-set distributions, correlations, scatter plots and outlier flags; validation-set prediction and residual diagnostics.
- OLS regression and a training-mean baseline, with predictions and MAE, RMSE and R² for each split.
- Fixed relative grade labels and a training-majority baseline, with class counts, predictions, confusion matrices and classification metrics.

### Existing regression method

OLS uses an intercept and four unstandardized time predictors, with physical activity as the reference. The five durations sum to 24 hours. Including all five with an intercept would therefore make individual coefficients non-unique. The fixed-total constraint retains information about physical activity. Each coefficient describes time reallocation from physical activity to the corresponding activity, holding the other included activities fixed.

The submitted Phase 1 proposal specifies MSE, which matches the OLS squared-error objective. Both the grade-band thresholds and regression objective are fixed. The source verification is recorded in [PHASE1_VERIFICATION.md](PHASE1_VERIFICATION.md).

### Existing classification baseline

The majority baseline always predicts B, selected from training counts: 249 of 1,200 records. Its validation Accuracy is 15.50% and Macro-F1 is 0.05368; test Accuracy is 18.75% and Macro-F1 is 0.06316. Full-precision results are saved in the CSVs.

### Materials supplied for the report and slides

Report and slides writers should start with the [English v5 report](../GE2340_Data_Analysis_EN_v5.md), use [FINDINGS.md](FINDINGS.md) for supporting detail, and take original images from `outputs/figures/`. Figure 3 in the report corresponds to `04_validation_diagnostics`, while `03_relationships_train` is the supplementary scatter-plot figure.

The v5 report and existing outputs cover data analysis and baseline results. Interpret activity-grade relationships as associations. The reported performance applies to this dataset and fixed split; performance across schools remains untested.

### Reproducing Alex's results

See the commands in [README.md](../README.md#run-the-existing-pipeline). The original source archive and CSV are bundled. Existing results can be reviewed directly without executing the pipeline.

## Part B — Jeffrey: model tasks and deliverables

### Required and optional models

| Task | Target and method | Evaluation and comparison |
|---|---|---|
| Softmax classifier (required) | Predict A/B/C/D/F using SGD and cross-entropy loss | Report Accuracy and Macro-F1; compare with the supplied majority-class baseline |
| Small neural network (optional) | Predict continuous `Grades` in its original units | Report MAE, RMSE and R²; compare with the supplied OLS and training-mean baselines |

Softmax is Jeffrey's required model task. The small neural network is an optional extension. Neither model's results are included in this package yet. Start from the prepared inputs below and reuse Alex's completed data analysis and baseline results.

### Input files to use

Paths below are relative to the package root.

| File | Use |
|---|---|
| `outputs/processed/train_scaled.csv` | Five scaled predictors, original Grades and row_id for training |
| `outputs/processed/validation_scaled.csv` | Validation inputs and targets |
| `outputs/processed/test_scaled.csv` | Test inputs and targets |
| `outputs/processed/split_manifest.csv` | Fixed sample membership shared by all models |
| `outputs/processed/preprocessor.json` | Training-fitted scaling parameters |
| `outputs/processed/grade_labels.csv` | Relative grade labels, joined one-to-one by row_id |
| `config/grade_bands.json` | Fixed thresholds, class order and boundary rule |
| `src/load_data.py` | Load a requested split and return row IDs, five predictors and continuous Grades |
| `outputs/metrics.csv` | OLS and mean-baseline regression metrics |
| `outputs/classification_metrics.csv` | Majority-baseline classification metrics |

### Experiment settings to follow

Softmax predicts the fixed grade classes. If the optional neural network is implemented, it predicts continuous `Grades` in its original units. Keep continuous `Grades` alongside the class labels. Join labels by `row_id`, preserving the order of feature rows.

Use the existing split and preprocessing. Select hyperparameters and stopping points with training and validation data. Test regression results, classification counts and baseline metrics have already been examined. Keep the test split and grade boundaries fixed during subsequent experiments.

The current baselines fit the 1,200 training records. Any final refit using training plus validation requires a shared protocol across the compared models.

### Materials to hand back

Provide the following for Softmax. If the optional neural network is completed, provide the same materials for that model.

- **Code:** a runnable implementation, with instructions for reproducing the experiments. Code integration can be completed jointly with Alex.
- **Methods and settings:** describe the completed model, its training procedure, chosen hyperparameters and how validation data guided those choices.
- **Results:** supply the evaluation metrics and comparison tables for the completed model, using the corresponding baselines listed above. Identify the data split for each result.
- **Figures and interpretation:** provide the experiment figures and explain the main findings, model differences and limitations for use in the report and slides.

Give these materials to Writer A for the English report and Writer B for model comparisons and slides. Writer B uses the supplied results, figures and explanations to prepare the presentation.

Regression comparisons use MAE, RMSE and R² for the mean baseline and OLS, adding the neural network if the optional experiment is completed. Classification comparisons use Accuracy and Macro-F1 for the majority baseline and Softmax. The existing classification outputs also contain balanced accuracy.

Update (Nov 13) - The classification model is complete, and can be seen in `src/run_pipeline.py`. Since it is an append to the regression model, the classification model is created after the regression model and its figures have completed. To run the code on the local computer, make sure to have installed `numpy`, `pandas`, `scikit-learn` and `matplotlib`. Construct the folder structure the same as described in the repository, and include `data/raw/student_lifestyle..csv` file, as well as the specified files above. Afterwards, simply execute the pipeline and all the figures, csv files will be generated automatically. 

The other sections are all included in the [English analysis report v6](../GE2340_Data_Analysis_EN_v6.md), appended at section 7. Some of the text within the report is also modified to inform that the classifier has been implemented, but the neural network will not be worked on for now. (Do note that vibe coding was used to complete the linear classifier, though the analysis report was completly written by me.)

I have also attempted to update the links that direct to the report/PDF, and any instances of mentions that the linear classifier/neural network model was incomplete, through this may not be incomplete. Additionally, Alex will need to generate the PDF file again, since the VSCode's extension `Markdown PDF` generates a completely different PDF format. The links to the PDF file is updated, so Alex only needs to modify the updated PDF's name to `GE2340_Data_Analysis_EN_v6.pdf`. Furthermore, no Chinese MD or PDF file is provided (if you want to update it, translate it on your own accord). Lastly, Alex will need to connect the classifier to the webpage/the executable file, as I do not have the access to the source build and that I do not know the underlying logic of the webpage well.

If there's any question, feel free to contact me in WhatsApp so that I can correct it, although I will be busy for the next week to finish an individual report, individual presentation and preparing for a test. Hopefully, I wouldn't be interfered much before the presentation of our finished project. - Jeffrey (Nov 13)

## Part C — Shared reference: data, features and labels

The bundled Kaggle version 3 file, `data/raw/student_lifestyle_dataset..csv`, contains 2,000 rows and 9 columns. Its target is `Grades`, observed from 5.60 to 10.00 and retained in its original units. Source and license details are in [DATA_LICENSE.md](../DATA_LICENSE.md).

Use these five predictors in the shared feature order:

1. `Study_Hours_Per_Day`
2. `Extracurricular_Hours_Per_Day`
3. `Sleep_Hours_Per_Day`
4. `Social_Hours_Per_Day`
5. `Physical_Activity_Hours_Per_Day`

`Student_ID` identifies records; `Gender` and `Stress_Level` are excluded from the model inputs. The original collection method, population representativeness and whether the data are real or synthetic remain unverified.

The grade bands use fixed boundaries calculated from training quintiles:

| Label | Grades interval |
|---|---|
| F | Grades < 7.10 |
| D | 7.10 ≤ Grades < 7.55 |
| C | 7.55 ≤ Grades < 8.00 |
| B | 8.00 ≤ Grades < 8.45 |
| A | Grades ≥ 8.45 |

Boundary values enter the higher group. F is the lowest relative group, not an official failure category. Class order is F, D, C, B, A, which can be encoded as 0, 1, 2, 3, 4. Tied scores explain why class counts are not exactly equal.

## Appendix — Demonstration app and website

A [local model explorer](../app/demo/index.html) already demonstrates Alex's linear regression. Its shared input and classification display can be reused when connecting the trained Softmax model; see the [adapter contract](../app/demo/README.md#adding-jeffreys-softmax-classifier).

For presentation use, see the [application guide](../app/README.md) for the Windows executable, browser version and development instructions. Connecting Softmax to the interface is an optional demonstration step after the model experiment.
