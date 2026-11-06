'use strict';
const { app, BrowserWindow, Menu, ipcMain, shell, session } = require('electron');
const path = require('node:path');
const { pathToFileURL } = require('node:url');
const isSmoke = process.argv.includes('--smoke-test');
app.setName('GE2340 Model Explorer');
app.setAppUserModelId('edu.ge2340.modelexplorer');
let window;
const state = () => ({ maximized: Boolean(window && !window.isDestroyed() && window.isMaximized()) });
function createWindow() {
  const html = path.join(app.isPackaged ? process.resourcesPath : path.resolve(__dirname, '..'), 'demo', 'index.html');
  const entry = pathToFileURL(html).href;
  Menu.setApplicationMenu(null);
  window = new BrowserWindow({
    width: 1320, height: 960, minWidth: 800, minHeight: 640,
    frame: false, show: false, backgroundColor: '#fafafa',
    title: 'GE2340 Model Explorer', icon: path.join(__dirname, 'assets', 'icon.ico'),
    autoHideMenuBar: true,
    webPreferences: {
      preload: path.join(__dirname, 'preload.cjs'),
      contextIsolation: true, nodeIntegration: false, sandbox: true,
      spellcheck: false, devTools: !app.isPackaged
    }
  });
  window.setMenu(null);
  const trusted = event => event.sender === window.webContents && event.senderFrame === window.webContents.mainFrame;
  const handle = (channel, callback) => ipcMain.handle(channel, event => { if (trusted(event)) return callback(); });
  handle('window:minimize', () => window.minimize());
  handle('window:toggle-maximize', () => { window.isMaximized() ? window.unmaximize() : window.maximize(); return state(); });
  handle('window:close', () => { setImmediate(() => window.close()); });
  handle('window:state', state);
  for (const name of ['maximize', 'unmaximize']) window.on(name, () => window.webContents.send('window:state-changed', state()));
  window.on('page-title-updated', event => event.preventDefault());
  window.webContents.on('will-navigate', (event, url) => { if (url !== entry) event.preventDefault(); });
  window.webContents.setWindowOpenHandler(({ url }) => {
    try {
      const parsed = new URL(url);
      if (parsed.protocol === 'https:' && ['www.kaggle.com', 'opendatacommons.org'].includes(parsed.hostname)) shell.openExternal(url);
    } catch { /* Ignore invalid external URLs. */ }
    return { action: 'deny' };
  });
  session.defaultSession.setPermissionRequestHandler((_contents, _permission, callback) => callback(false));
  session.defaultSession.setPermissionCheckHandler(() => false);
  window.once('ready-to-show', () => { if (!isSmoke) window.show(); });
  return window.loadFile(html).then(() => { window.setTitle('GE2340 Model Explorer'); return window; });
}
app.whenReady().then(async () => {
  const win = await createWindow();
  if (isSmoke) await require('./smoke.cjs')(win);
}).catch(error => { console.error(error); app.exit(1); });
app.on('window-all-closed', () => app.quit());

