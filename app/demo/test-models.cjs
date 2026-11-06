'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '..', '..');
require('./model-data.js');
const api = require('./model-registry.js');
require('./linear-adapter.js');
function rows(file) {
  const [head, ...lines] = fs.readFileSync(file, 'utf8').trim().split(/\r?\n/);
  const keys = head.replace(/^\uFEFF/, '').split(',');
  return lines.map(line => Object.fromEntries(line.split(',').map((value, i) => [keys[i], value])));
}
(async () => {
  const original = JSON.parse(fs.readFileSync(path.join(root, 'outputs/regression_model.json'), 'utf8'));
  assert.deepEqual(GE2340_DATA.model, original, 'Exported parameters must match the fitted model');
  let count = 0, maxError = 0;
  for (const split of ['train', 'validation', 'test']) {
    const expected = new Map(rows(path.join(root, 'outputs', `predictions_${split}.csv`)).map(row => [row.row_id, Number(row.linear_regression)]));
    for (const row of rows(path.join(root, 'outputs/processed', `${split}_raw.csv`))) {
      const input = Object.fromEntries(api.fields.map(field => [field.key, Number(row[field.key])]));
      const result = await api.predict('linear-regression', input);
      const error = Math.abs(result.value - expected.get(row.row_id));
      assert.ok(error < 1e-11, `${split}/${row.row_id}: ${error}`);
      maxError = Math.max(maxError, error);
      count++;
    }
  }
  const input = Object.fromEntries(api.fields.map((field, i) => [field.key, [8, 2, 8, 3, 3][i]]));
  for (const value of [NaN, Infinity, -1, 25, '8']) {
    await assert.rejects(api.predict('linear-regression', { ...input, Study_Hours_Per_Day: value }));
  }
  await assert.rejects(api.predict('linear-regression', { ...input, Study_Hours_Per_Day: 7 }), /remaining/);
  await assert.rejects(api.predict('missing', input), /not available/);
  const edge = Object.fromEntries(api.fields.map((field, i) => [field.key, i === 0 ? 24 : 0]));
  assert.ok((await api.predict('linear-regression', edge)).value > 10, 'Predictions must not be clipped');
  const bands = JSON.parse(fs.readFileSync(path.join(root, 'config/grade_bands.json'), 'utf8'));
  assert.deepEqual(GE2340_DATA.gradeBands, bands);
  const grades = rows(path.join(root, 'outputs/processed/train_raw.csv')).map(row => Number(row.Grades)).sort((a, b) => a - b);
  assert.deepEqual(GE2340_DATA.trainingGrades, grades, 'Percentiles use observed training Grades only');
  for (const row of rows(path.join(root, 'outputs/processed/grade_labels.csv'))) {
    assert.equal(api.relativeStanding(Number(row.Grades), grades, bands).label, row.grade_class);
  }
  for (let i = 0; i < bands.cutpoints.length; i++) {
    assert.equal(api.relativeStanding(bands.cutpoints[i], grades, bands).label, bands.labels_low_to_high[i + 1]);
    assert.equal(api.relativeStanding(bands.cutpoints[i] - 1e-8, grades, bands).label, bands.labels_low_to_high[i]);
  }
  assert.equal(api.relativeStanding(7, [6, 7, 7, 8], bands).topPercent, 50, 'Half of ties count toward the upper-tail rank');
  assert.equal(api.relativeStanding(9, [6, 7, 7, 8], bands).topPercent, 0);
  assert.equal(api.relativeStanding(5, [6, 7, 7, 8], bands).topPercent, 100);
  assert.throws(() => api.relativeStanding(NaN, grades, bands));
  console.log('PASS: existing 2,000 grade labels, exact boundaries, training-only reference, ties and percentile extremes.');
  // Synthetic fixtures exercise the extension contract only; they are never loaded by the demo.
  api.register({ id: 'test-classifier', label: 'Contract fixture', task: 'classification', classLabels: ['A', 'C', 'F', 'B', 'D'], async predict() { return { probabilities: [.1, .05, .1, .7, .05] }; } });
  assert.deepEqual(await api.predict('test-classifier', input), { label: 'B', probabilities: [.1, .05, .1, .7, .05] });
  api.register({ id: 'invalid-classifier', label: 'Invalid fixture', task: 'classification', classLabels: ['A', 'B'], predict() { return { probabilities: [.6, .6] }; } });
  await assert.rejects(api.predict('invalid-classifier', input), /invalid probabilities/);
  assert.throws(() => api.register({ id: 'linear-regression', label: 'duplicate', task: 'regression', predict() {} }), /Duplicate/);
  console.log(`PASS: ${count} saved predictions match (maximum absolute error ${maxError}).`);
  console.log('PASS: invalid inputs, fixed total, unclipped predictions, async classification, class order, probability validation and duplicate IDs.');
})();
