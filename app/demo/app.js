(function () {
  'use strict';
  const $ = id => document.getElementById(id);
  const { fields, models } = GE2340;
  const initial = [8, 2, 8, 3, 3];
  const groupNames = { A: 'Upper group', B: 'Upper-middle group', C: 'Middle group', D: 'Lower-middle group', F: 'Lower group' };
  const groupLabel = label => groupNames[label] ? groupNames[label] + ' (' + label + ')' : label;
  let revision = 0;
  let busy = false;
  const numericInputs = [];
  const sliders = [];
  function element(tag, className, text) {
    const el = document.createElement(tag);
    if (className) el.className = className;
    if (text !== undefined) el.textContent = text;
    return el;
  }
  fields.forEach((field, i) => {
    const row = element('div', 'field');
    row.style.setProperty('--field-color', field.color);
    const top = element('div', 'field-top');
    const label = element('label', 'field-name');
    label.htmlFor = 'hours-' + i;
    const dot = element('span', 'field-dot');
    dot.style.background = field.color;
    label.append(dot, document.createTextNode(field.label));
    const wrap = element('div', 'number-wrap');
    const input = element('input');
    Object.assign(input, { id: 'hours-' + i, type: 'number', min: '0', max: '24', step: 'any', value: String(initial[i]), required: true });
    input.setAttribute('aria-label', field.label + ' hours per day');
    const slider = element('input');
    Object.assign(slider, { type: 'range', min: '0', max: '24', step: '0.1', value: String(initial[i]) });
    slider.setAttribute('aria-label', field.label + ' hours slider');
    wrap.append(input, element('span', '', 'h'));
    top.append(label, wrap);
    row.append(top, slider);
    $('fields').append(row);
    numericInputs.push(input);
    sliders.push(slider);
    input.addEventListener('input', () => { slider.value = input.value; changed(); });
    slider.addEventListener('input', () => { input.value = slider.value; changed(); });
  });
  for (const model of models.values()) {
    const option = element('option', '', model.label);
    option.value = model.id;
    $('model').append(option);
  }
  if (![...models.values()].some(model => model.task === 'classification')) {
    const option = element('option', '', 'Softmax classifier · not connected');
    option.disabled = true;
    $('model').append(option);
  }
  function inputs() {
    return Object.fromEntries(fields.map((field, i) => [field.key, numericInputs[i].value === '' ? NaN : Number(numericInputs[i].value)]));
  }
  function updateBudget() {
    const auto = $('auto-balance').checked;
    numericInputs[4].readOnly = auto;
    sliders[4].disabled = auto;
    if (auto) {
      const first = numericInputs.slice(0, 4).map(input => input.value === '' ? NaN : Number(input.value));
      const remainder = 24 - first.reduce((a, b) => a + b, 0);
      numericInputs[4].value = Number.isFinite(remainder) ? String(Math.max(0, Math.round(remainder * 1e10) / 1e10)) : '';
      sliders[4].value = numericInputs[4].value;
    }
    const input = inputs();
    const validation = GE2340.validateInput(input);
    const total = Object.values(input).reduce((a, b) => a + b, 0);
    $('total').textContent = Number.isFinite(total) ? total.toFixed(1) : '—';
    $('total').classList.toggle('invalid', !validation.valid);
    $('budget-message').textContent = validation.message;
    $('budget-message').classList.toggle('invalid', !validation.valid);
    $('predict').disabled = !validation.valid || busy;
    $('time-bar').replaceChildren();
    fields.forEach((field, i) => {
      sliders[i].style.setProperty('--progress', (Number(sliders[i].value) / 24 * 100) + '%');
      const piece = element('span');
      piece.style.background = field.color;
      piece.style.width = (Math.max(0, Number.isFinite(input[field.key]) ? input[field.key] : 0) / Math.max(24, Number.isFinite(total) ? total : 24) * 100) + '%';
      $('time-bar').append(piece);
    });
    const outside = fields.filter(field => {
      const range = GE2340_DATA.trainingRanges[field.key];
      return Number.isFinite(input[field.key]) && (input[field.key] < range[0] || input[field.key] > range[1]);
    });
    $('range-note').hidden = !validation.valid || outside.length === 0;
    $('range-note').textContent = 'Outside the training range: ' + outside.map(field => field.label + ' (' + GE2340_DATA.trainingRanges[field.key].join('–') + ' h)').join(', ') + '. This prediction extrapolates beyond the observed inputs.';
    return validation;
  }
  function changed() {
    revision++;
    updateBudget();
    document.querySelector('.prediction-card').classList.add('stale');
    $('result-state').textContent = 'INPUTS CHANGED';
    $('result-message').textContent = 'Previous prediction shown. Run again for the edited schedule.';
  }
  function setModel() {
    const model = models.get($('model').value);
    $('model-description').textContent = model.description || model.label;
    $('output-title').textContent = 'Estimated relative group';
    $('regression-result').hidden = model.task !== 'regression';
    $('classification-result').hidden = model.task !== 'classification';
    $('baseline-comparison').hidden = !Number.isFinite(model.baseline);
    $('metrics').replaceChildren();
    for (const metric of model.metrics || []) {
      const card = element('div', 'metric');
      card.append(element('span', 'metric-label', metric.label), element('strong', 'metric-value', metric.value), element('span', 'metric-note', metric.note));
      $('metrics').append(card);
    }
    document.querySelector('.performance-heading').hidden = !model.metrics?.length;
    document.querySelector('.performance-footnote').hidden = !model.metrics?.length;
    $('comparison-note').hidden = model.id !== 'linear-regression';
    const improvement = (1 - GE2340_DATA.metrics.linear_regression.MAE / GE2340_DATA.metrics.mean_baseline.MAE) * 100;
    $('mae-improvement').textContent = improvement.toFixed(1) + '% lower test MAE';
    $('prediction-value').textContent = '—';
    $('relative-grade').textContent = '—';
    $('top-percent').textContent = '—';
    $('band-scale').replaceChildren();
    $('class-value').textContent = '—';
    $('baseline-value').textContent = Number.isFinite(model.baseline) ? model.baseline.toFixed(3) : '—';
    $('baseline-delta').textContent = '—';
    $('probabilities').replaceChildren();
    $('snapshot').textContent = '';
    $('result-state').textContent = 'READY';
    $('result-message').textContent = 'Run prediction for the current schedule.';
    revision++;
  }
  async function run(isExample = false) {
    const validation = updateBudget();
    if (!validation.valid || busy) return;
    const input = inputs();
    const id = $('model').value;
    const model = models.get(id);
    const currentRevision = revision;
    busy = true;
    $('predict').disabled = true;
    $('result-state').textContent = 'CALCULATING';
    try {
      const result = await GE2340.predict(id, input);
      if (currentRevision !== revision) return;
      if (model.task === 'regression') {
        $('prediction-value').textContent = result.value.toFixed(3);
        const standing = GE2340.relativeStanding(result.value, GE2340_DATA.trainingGrades, GE2340_DATA.gradeBands);
        $('relative-grade').textContent = groupLabel(standing.label);
        $('top-percent').textContent = standing.topPercent < 0.5 ? 'Top <1%' : 'Top ≈ ' + Math.round(standing.topPercent) + '%';
        $('reference-size').textContent = standing.referenceSize.toLocaleString('en-US');
        $('band-scale').replaceChildren();
        for (const label of GE2340_DATA.gradeBands.labels_low_to_high) {
          const band = element('span', 'band' + (label === standing.label ? ' active' : ''), label);
          band.title = groupLabel(label);
          if (label === standing.label) band.setAttribute('aria-current', 'true');
          $('band-scale').append(band);
        }
        const delta = result.value - model.baseline;
        $('baseline-delta').textContent = (delta >= 0 ? '+' : '−') + Math.abs(delta).toFixed(3);
      } else {
        $('class-value').textContent = groupLabel(result.label);
        $('probabilities').replaceChildren();
        model.classLabels.forEach((label, i) => {
          const row = element('div', 'prob-row');
          const track = element('div', 'prob-track');
          const fill = element('div', 'prob-fill');
          fill.style.width = result.probabilities[i] * 100 + '%';
          track.append(fill);
          row.append(element('span', '', label), track, element('span', '', (result.probabilities[i] * 100).toFixed(1) + '%'));
          $('probabilities').append(row);
        });
      }
      document.querySelector('.prediction-card').classList.remove('stale');
      $('result-state').textContent = isExample ? 'EXAMPLE DAY' : 'PREDICTION UPDATED';
      $('result-message').textContent = model.task === 'regression' ? 'Relative band mapped from the linear regression estimate.' : 'Relative grade prediction and model probabilities.';
      $('snapshot').textContent = fields.map(field => field.label + ' ' + Number(input[field.key].toFixed(2)) + ' h').join(' · ');
    } catch (error) {
      if (currentRevision !== revision) return;
      document.querySelector('.prediction-card').classList.add('stale');
      $('result-state').textContent = 'UNAVAILABLE';
      $('result-message').textContent = error.message;
    } finally {
      busy = false;
      updateBudget();
    }
  }
  $('prediction-form').addEventListener('submit', event => { event.preventDefault(); run(); });
  $('auto-balance').addEventListener('change', changed);
  $('model').addEventListener('change', () => { setModel(); updateBudget(); });
  $('reset').addEventListener('click', () => {
    numericInputs.forEach((input, i) => { input.value = String(initial[i]); sliders[i].value = String(initial[i]); });
    $('auto-balance').checked = true;
    changed();
    if (!busy) run(true);
  });
  setModel();
  run(true);
})();
