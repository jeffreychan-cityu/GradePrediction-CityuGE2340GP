# GE2340 Data Analysis and Baseline Package

This package contains the shared data, completed baseline experiments and materials for the team report. The data and code are version 3; the analysis report is version 5. Documentation updated on 6 November 2026.

## Reading order

| Purpose | Read | Then use |
|---|---|---|
| Continue the model experiments | [Technical handoff](docs/HANDOFF.md) | `outputs/processed/`, `config/grade_bands.json`, `src/load_data.py` |
| Write the report | [English analysis report v5](GE2340_Data_Analysis_EN_v5.md) | [Technical findings](docs/FINDINGS.md), result CSVs and original figures |
| Prepare comparisons and slides | [English analysis report v5](GE2340_Data_Analysis_EN_v5.md) | [Figure mapping](docs/FINDINGS.md#figure-guide) and `outputs/figures/` |

Use the Markdown report for edits and team writing. The PDF preserves the original v5 report. Team documentation is in English; the corresponding Chinese report and personal reference materials are in [reference_zh/](reference_zh/).

## Current state

The package includes completed data quality checks, fixed splits, scaling fitted on training data, training-set EDA, OLS regression, the training-mean baseline, relative grade labels and the training-majority classification baseline.

Softmax is the next required model experiment. The small neural network is an optional extension. Use the [technical handoff](docs/HANDOFF.md) for inputs, targets, comparison rules and deliverables.

Use the existing 1,200/400/400 train/validation/test split and preprocessing parameters. Match records by `row_id`. The classifier predicts project-defined relative grade bands; the optional neural network predicts continuous `Grades`.

## Package contents

| Location | Contents |
|---|---|
| [Editable English report](GE2340_Data_Analysis_EN_v5.md) | Edited Markdown working copy based on v5 |
| [Original English PDF v5](GE2340_Data_Analysis_EN_v5.pdf) | Source PDF retained for reference |
| [docs/HANDOFF.md](docs/HANDOFF.md) | Inputs, fixed experiment settings and handoff files |
| [docs/FINDINGS.md](docs/FINDINGS.md) | Existing results, interpretation and figure mapping |
| [docs/PHASE1_VERIFICATION.md](docs/PHASE1_VERIFICATION.md) | Historical verification of the submitted Phase 1 method |
| `data/raw/` | Original CSV, archive and source metadata |
| `config/` | Fixed grade-band definition |
| `src/` | Pipeline and data-loading interface |
| [analysis.ipynb](analysis.ipynb) | Notebook entry point into the pipeline |
| `outputs/processed/` | Raw/scaled split data, labels and preprocessing parameters |
| `outputs/figures/` | Five figures, each in PNG and PDF formats |
| `outputs/` | Metrics, predictions, model parameters, quality checks and existing run records |
| `tests/` | Pipeline checks |
| [requirements.txt](requirements.txt) | Python dependency versions |
| [DATA_LICENSE.md](DATA_LICENSE.md) | Dataset attribution and license references |
| [MANIFEST_SHA256.json](MANIFEST_SHA256.json) | File checksums for project sources and supplied data, excluding this manifest, installed dependencies and desktop test output |
| `reference_zh/` | Chinese report, handoff reference and file index for the owner |

References to v2 classification outputs in report Section 6 identify when those results were introduced. Those outputs are included in the current v3 package. Metric CSVs retain full precision; the report presents rounded values.

## Run the existing pipeline

From this directory, using Python 3.12:

```bash
python -m pip install -r requirements.txt
python src/run_pipeline.py
python -m unittest discover -s tests -v
```

The pipeline reads the bundled raw data and writes results to `outputs/`. The notebook runs the same pipeline. To review the existing results, open the CSVs, PDFs and PNGs directly. Original execution records are in `outputs/environment.json`, `outputs/test_log.txt` and `outputs/reproduction_check.txt`.

Retain dataset attribution and [DATA_LICENSE.md](DATA_LICENSE.md) when using the data or figures. The original collection method and whether the records are real or synthetic remain unverified; the experiment describes prediction within this dataset and fixed split.

## Appendix — Demonstration app and website

The browser demo and Windows desktop app are complete for the existing linear regression model. This section covers presentation use and application development.

The application source is grouped under `app/`. The ready-to-run Windows executable is in the package root. The executable is stored with Git LFS; when cloning the repository, install Git LFS and run `git lfs pull` to download it.

```text
ge2340_data_package_v3/
├── GE2340-Model-Explorer-1.0.0-Windows.exe
├── app/
│   ├── README.md
│   ├── demo/       # Shared interface, model adapters and embedded model data
│   └── desktop/    # Electron window, app icon and packaging configuration
├── docs/           # Team handoff and technical findings
├── outputs/        # Existing experiment results and shared data exports
└── reference_zh/   # Chinese reference materials for the owner
```

**For presentations:** double-click the [Windows executable](GE2340-Model-Explorer-1.0.0-Windows.exe). It includes the runtime and model and works offline. Alternatively, open [app/demo/index.html](app/demo/index.html) in a browser. The previous root-level `demo/` path has moved to `app/demo/`.

**For interface or classifier work:** edit `app/demo/`. The current app runs linear regression and maps its prediction to a relative group and an estimated position within the training set. Softmax is not yet connected. Follow the [model adapter contract](app/demo/README.md#adding-jeffreys-softmax-classifier) to add the trained classifier.

**For window controls or packaging:** use `app/desktop/`. From the package root, run:

```powershell
cd app/desktop
npm ci
npm start
```

`npm ci` installs the development dependencies on a fresh checkout. From `app/desktop/`, use `npm run test:desktop` to check the window and prediction flow, or `npm run dist` to generate the Windows executable in the package root. Source edits appear when running the development app; rebuild to include them in the portable EXE.

After updating model outputs, run these commands from the package root before rebuilding:

```powershell
python app/demo/export_model.py
node app/demo/test-models.cjs
```

See [app/README.md](app/README.md) for the application overview and [app/desktop/README.md](app/desktop/README.md) for packaging details.
