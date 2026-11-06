# GE2340 Application

This directory contains the browser interface and desktop wrapper.

| Folder | Purpose | Entry point |
|---|---|---|
| [demo/](demo/README.md) | Shared interface, prediction adapters and model data | [Open the browser demo](demo/index.html) |
| [desktop/](desktop/README.md) | Electron window controls, icon and Windows packaging | Run `npm start` from `app/desktop/` |

For presentations, run the [portable Windows executable](../GE2340-Model-Explorer-1.0.0-Windows.exe) in the package root.

Edit the interface or add a trained classifier in `app/demo/`. Edit window behavior and packaging in `app/desktop/`. Both runtimes use the same interface. Existing model outputs remain in the package root's `outputs/` folder.

From the package root, refresh the embedded model and verify predictions:

```powershell
python app/demo/export_model.py
node app/demo/test-models.cjs
```

From the package root, set up and run the desktop app:

```powershell
cd app/desktop
npm ci
npm start
```

Install dependencies with `npm ci` on a fresh checkout. From `app/desktop/`, run `npm run test:desktop` to check the app or `npm run dist` to package it. Rebuild after editing the interface or adding a classifier.

The Windows build writes to the package root. The existing portable executable is self-contained and continues to work after source folders are reorganized.
