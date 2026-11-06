# GE2340 Desktop App

The Windows app wraps the existing [model explorer](../demo/README.md) with a custom GE2340 title bar and icon. It has no default application menu. The title bar supports dragging; the three buttons minimize, maximize/restore and close the window. Alt+F4 also closes it.

## Run the packaged app

Download [GE2340-Model-Explorer-1.0.0-Windows.exe](https://github.com/wdffdw07/GradePrediction-CityuGE2340GP/releases/download/v1.0.0/GE2340-Model-Explorer-1.0.0-Windows.exe) from [Release v1.0.0](https://github.com/wdffdw07/GradePrediction-CityuGE2340GP/releases/tag/v1.0.0), or use the local copy in the main `ge2340_data_package_v3` folder. It is a Windows x64 portable app; no Node.js, Python, browser or separate model installation is needed. Its initial launch extracts the bundled runtime into a temporary directory.

The app includes the same fitted model, preprocessing reference and grade display as the browser demo. Predictions work offline. The source attribution link opens in the default browser when clicked.

The executable is not code-signed. A Windows reputation prompt may identify the publisher as unknown.

## Develop and package

From `app/desktop/`, with Node.js installed:

```powershell
npm ci
npm start
npm run test:desktop
npm run dist
```

Dependencies are pinned in `package-lock.json`. The desktop wrapper uses Electron 44.4.5 and electron-builder 26.18.0. Build output goes to the main `ge2340_data_package_v3` folder for this checkout. Once Electron is installed locally, packaging can also use the installed runtime:

```powershell
npm run dist -- --config.electronDist=node_modules/electron/dist
```

`main.cjs` owns the window and the restricted window-control IPC. `preload.cjs` exposes only window controls to the isolated renderer. The shared `app/demo/desktop-bar.js` and `app/demo/desktop.css` enable the custom title bar only inside the app; the HTML page continues to work in a browser.

The app loads local content with renderer sandboxing and context isolation. External navigation is limited to the existing dataset/license links. Application assets and the fitted model are packaged locally.

## Update the model or classifier

Edit the shared files in `../demo/`, following its adapter contract, then rebuild the executable. Classifier scripts and local model assets must be included by the `extraResources` filter in `package.json`. The current filter includes HTML, CSS and JavaScript; add another extension only if the new adapter needs it. The packaged executable does not automatically read changes from the source folder.

## Verification

`npm run test:desktop` checks the custom title bar, menu removal, isolated renderer, prediction updates and all window buttons. Its default output is `smoke-results/`; pass `-- --smoke-output=<absolute-path>` to choose another directory. The same `--smoke-test` and `--smoke-output` arguments work on the packaged executable.

Numerical checks remain available from the package root with `node app/demo/test-models.cjs`.

Implementation references: [Electron custom title bars](https://www.electronjs.org/docs/latest/tutorial/custom-title-bar) and [Electron security guidance](https://www.electronjs.org/docs/latest/tutorial/security).
