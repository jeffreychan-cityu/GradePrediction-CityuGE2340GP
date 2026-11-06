# GE2340 Model Explorer

Open [index.html](index.html) in a browser to demonstrate the existing linear regression model. The page runs locally, without installation, a server or an internet connection. Keep the files in this directory together when copying the demo.

A Windows portable build with a custom GE2340 title bar and icon is also available. See the [desktop app guide](../desktop/README.md) for running and rebuilding it.

## Using the demo

1. Enter daily hours for the five activities using the sliders or number fields.
2. Physical activity receives the remaining hours by default. Clear the checkbox to enter all five durations manually.
3. The total must be 24 hours. Empty, negative, non-finite or over-budget inputs block prediction.
4. Select **Run prediction**. The main result shows a relative group name with its letter, such as **Middle group (C)**, and a whole-number top percentage labelled **Estimated position in training set**. Expand **View numeric estimate & baseline** to inspect the continuous prediction and mean baseline. Held-out regression metrics remain below the result.
5. **Reset example** restores the demonstration schedule. After an input change, the previous result is marked until prediction runs again.

The page uses English for team presentations. On small screens, inputs and results stack vertically.

## Current model

The fitted intercept, coefficients and mean baseline come from [regression_model.json](../../outputs/regression_model.json). Test metrics come from [metrics.csv](../../outputs/metrics.csv). Training ranges come from [train_descriptive_statistics.csv](../../outputs/train_descriptive_statistics.csv).

Linear regression consumes **raw hours** in the fitted feature order. It uses four coefficients plus an intercept; physical activity is the reference under the 24-hour constraint. The underlying regression estimate stays in its original units, without standardization or clipping. The display maps it to the established relative grade bands. The training-mean value in the numeric details is a comparator, not a confidence interval. The error metrics describe the test set, not an individual prediction.

The initial schedule is a demonstration input, not a student record. Source data attribution and terms are recorded in [DATA_LICENSE.md](../../DATA_LICENSE.md).

## Relative group and top percentage

Display names are Upper group (A), Upper-middle group (B), Middle group (C), Lower-middle group (D) and Lower group (F).

The display uses the exact boundaries from [grade_bands.json](../../config/grade_bands.json): F below 7.10; D from 7.10 to below 7.55; C from 7.55 to below 8.00; B from 8.00 to below 8.45; A from 8.45 upward. A score on a boundary enters the higher band. Mapping uses the full-precision prediction before rounding.

The top percentage compares the prediction with the **observed Grades of the 1,200 training records**, not validation/test records or fitted predictions:

```text
top percentage = 100 × (number above the estimate + 0.5 × number equal to it) / 1,200
```

For example, “Top ≈ 40%” places the estimate around the top 40% of that reference distribution. Values round to the nearest whole percentage point; a value that would round to zero displays as “Top <1%”. The underlying calculation retains its full precision. This is a descriptive position in the training dataset, not a percentile calibrated to another school or a probability of classification correctness. F denotes the lowest relative group, not official failure.

These are presentation mappings of the regression estimate. The existing regression metrics remain unchanged; classification performance for the mapped output has not been evaluated. A future Softmax model supplies its own predicted class and probabilities, without inferring a precise percentile from a class label alone.

## Files and extension points

| File | Purpose |
|---|---|
| `index.html` / `styles.css` | Shared page layout and styling |
| `app.js` | Input controls, time validation feedback, model selection and result rendering |
| `model-registry.js` | Shared input validation, adapter registration and output validation |
| `model-data.js` | Exported fitted model, metrics, training ranges, fixed bands and observed training Grades |
| `linear-adapter.js` | Current regression adapter |
| `export_model.py` | Refresh browser data from existing outputs without fitting a model |
| `test-models.cjs` | Compare browser inference with all saved predictions and test the adapter contract |

## Adding Jeffrey's Softmax classifier

The shared UI already supports classification results: predicted class and a probability bar for each class. Softmax is shown as unavailable until a trained adapter is registered.

Create a separate `softmax-adapter.js` and load its trained assets and adapter **after** `model-registry.js` and **before** `app.js` in `index.html`. Register it with `GE2340.register` using this contract:

| Property | Requirement |
|---|---|
| `id` | Unique model ID, for example `softmax` |
| `label` | Name displayed in the model selector |
| `task` | `classification` |
| `description` | Brief description shown below the selector |
| `classLabels` | Labels in the exact order of the model's probability outputs; use the established F, D, C, B, A order when training |
| `predict(input)` | Accept the five **raw-hour** values by their original field names; return `{ probabilities: [...] }` or a Promise of that object |
| `metrics` | Optional array of `{ label, value, note }` entries from the actual fixed test evaluation, such as Accuracy and Macro-F1 |

The input keys, in shared feature order, are:

```text
Study_Hours_Per_Day
Extracurricular_Hours_Per_Day
Sleep_Hours_Per_Day
Social_Hours_Per_Day
Physical_Activity_Hours_Per_Day
```

Apply the classifier's training-time preprocessing **inside its adapter**. If trained on the supplied scaled data, load and use the exact parameters in [preprocessor.json](../../outputs/processed/preprocessor.json); the regression adapter must continue to receive raw hours. Load any inference dependency before the adapter. To retain double-click offline use, bundle model weights and preprocessing parameters as local JavaScript assets, as the regression adapter does.

Return one finite probability per class, each between zero and one and summing to one within 1e-6. The registry derives the label from the largest probability; a tie selects the first class in output order. `predict` may be synchronous or asynchronous. Invalid outputs produce an error message, and a result from an old input is discarded if the user changes inputs during inference.

Registering a classifier automatically enables its selector entry and probability display. Class labels remain the project-defined relative bands from [grade_bands.json](../../config/grade_bands.json). Softmax probabilities must come from the trained classifier. The regression page's grade mapping is a separate presentation of its continuous estimate.

## Refreshing and checking

From the package root:

```bash
python app/demo/export_model.py
node app/demo/test-models.cjs
```

The check compares all 2,000 saved train, validation and test predictions with the JavaScript implementation. It also checks invalid inputs, the total-time constraint, unclipped predictions and the classification adapter contract. Synthetic classifier fixtures exist only inside the test process; the demo does not load them.

For an optional local HTTP preview, run from the package root:

```bash
python -m http.server 8765 --bind 127.0.0.1 --directory app/demo
```

Open `http://127.0.0.1:8765`. Stop the preview with Ctrl+C when finished.
