(function () {
  'use strict';
  const data = GE2340_DATA;
  const fitted = data.model;
  GE2340.register({
    id: 'linear-regression',
    label: 'Linear regression',
    task: 'regression',
    description: 'Ordinary least squares · fixed 24-hour day',
    metrics: [
      { label: 'Test MAE', value: data.metrics.linear_regression.MAE.toFixed(4), note: 'Mean absolute error' },
      { label: 'Test RMSE', value: data.metrics.linear_regression.RMSE.toFixed(4), note: 'Root mean squared error' },
      { label: 'Test R²', value: data.metrics.linear_regression.R2.toFixed(4), note: 'Coefficient of determination' }
    ],
    baseline: fitted.mean_baseline,
    predict(input) {
      return { value: fitted.features.reduce((value, feature, i) => value + fitted.coefficients[i] * input[feature], fitted.intercept) };
    }
  });
})();

