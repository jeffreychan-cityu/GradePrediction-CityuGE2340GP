(function () {
  'use strict';
  const api = window.desktopWindow;
  if (!api) return;
  document.documentElement.classList.add('desktop-app');
  const bar = document.createElement('header');
  bar.className = 'desktop-titlebar';
  bar.innerHTML = '<div class="desktop-identity"><span class="desktop-logo" aria-hidden="true">g.</span><span>GE2340 <span class="desktop-divider">/</span> <span class="desktop-subtitle">Model Explorer</span></span></div><span class="desktop-local">OFFLINE WORKSPACE</span><div class="desktop-controls"><button id="window-minimize" aria-label="Minimize window" title="Minimize"><svg viewBox="0 0 12 12" aria-hidden="true"><path d="M1 6h10"/></svg></button><button id="window-maximize" aria-label="Maximize window" title="Maximize"><svg viewBox="0 0 12 12" aria-hidden="true"><rect x="1.5" y="1.5" width="9" height="9"/></svg></button><button id="window-close" aria-label="Close window" title="Close"><svg viewBox="0 0 12 12" aria-hidden="true"><path d="m2 2 8 8M10 2l-8 8"/></svg></button></div>';
  document.body.prepend(bar);
  const maximize = document.getElementById('window-maximize');
  function update(state) {
    const label = state.maximized ? 'Restore window' : 'Maximize window';
    maximize.setAttribute('aria-label', label);
    maximize.title = label;
    maximize.innerHTML = state.maximized ? '<svg viewBox="0 0 12 12" aria-hidden="true"><path d="M4 3V1h7v7H9"/><rect x="1" y="4" width="7" height="7"/></svg>' : '<svg viewBox="0 0 12 12" aria-hidden="true"><rect x="1.5" y="1.5" width="9" height="9"/></svg>';
  }
  document.getElementById('window-minimize').addEventListener('click', () => api.minimize());
  maximize.addEventListener('click', () => api.toggleMaximize().then(update));
  document.getElementById('window-close').addEventListener('click', () => api.close());
  api.onState(update);
  api.getState().then(update);
})();
