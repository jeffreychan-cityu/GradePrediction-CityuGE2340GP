(function (root) {
  'use strict';
  const fields = [
    { key: 'Study_Hours_Per_Day', label: 'Study', color: '#315cce' },
    { key: 'Extracurricular_Hours_Per_Day', label: 'Extracurricular', color: '#a37420' },
    { key: 'Sleep_Hours_Per_Day', label: 'Sleep', color: '#7960b8' },
    { key: 'Social_Hours_Per_Day', label: 'Social', color: '#ba626e' },
    { key: 'Physical_Activity_Hours_Per_Day', label: 'Physical activity', color: '#318578' }
  ];
  const models = new Map();
  function validateInput(input) {
    for (const field of fields) {
      const value = input[field.key];
      if (typeof value !== 'number' || !Number.isFinite(value) || value < 0 || value > 24) {
        return { valid: false, message: 'Enter a number from 0 to 24 for every activity.' };
      }
    }
    const total = fields.reduce((sum, field) => sum + input[field.key], 0);
    if (Math.abs(total - 24) > 1e-8) {
      return { valid: false, total, message: total > 24 ? 'Your day exceeds 24 hours. Reduce an activity to continue.' : 'Allocate the remaining ' + (24 - total).toFixed(2) + ' hours to continue.' };
    }
    return { valid: true, total, message: 'Your full day is allocated.' };
  }
  function relativeStanding(value, reference, bands) {
    if (!Number.isFinite(value) || !Array.isArray(reference) || !reference.length || reference.some(x => !Number.isFinite(x))) throw new Error('Invalid percentile reference.');
    const index = bands.cutpoints.filter(cutpoint => value >= cutpoint).length;
    const greater = reference.filter(score => score > value).length;
    const equal = reference.filter(score => score === value).length;
    const topPercent = 100 * (greater + equal / 2) / reference.length;
    return { label: bands.labels_low_to_high[index], topPercent, referenceSize: reference.length };
  }
  function register(model) {
    if (!model || !model.id || !model.label || typeof model.predict !== 'function' || !['regression', 'classification'].includes(model.task)) throw new Error('Invalid model adapter.');
    if (models.has(model.id)) throw new Error('Duplicate model ID.');
    if (model.task === 'classification' && (!Array.isArray(model.classLabels) || model.classLabels.length < 2 || new Set(model.classLabels).size !== model.classLabels.length)) throw new Error('Classification requires unique classLabels in model output order.');
    models.set(model.id, model);
  }
  async function predict(id, input) {
    const validation = validateInput(input);
    if (!validation.valid) throw new Error(validation.message);
    const model = models.get(id);
    if (!model) throw new Error('Model is not available.');
    const result = await model.predict({ ...input });
    if (model.task === 'regression') {
      if (!result || !Number.isFinite(result.value)) throw new Error('The model returned an invalid prediction.');
      return { value: result.value };
    }
    const probs = result && result.probabilities;
    if (!Array.isArray(probs) || probs.length !== model.classLabels.length || probs.some(x => !Number.isFinite(x) || x < 0 || x > 1) || Math.abs(probs.reduce((a, b) => a + b, 0) - 1) > 1e-6) throw new Error('The classifier returned invalid probabilities.');
    const best = probs.indexOf(Math.max(...probs));
    return { label: model.classLabels[best], probabilities: probs };
  }
  root.GE2340 = { fields, models, register, validateInput, predict, relativeStanding };
  if (typeof module !== 'undefined') module.exports = root.GE2340;
})(globalThis);
