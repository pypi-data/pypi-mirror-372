# randomstatsmodels
Check out medium story here: [Medium Story](https://medium.com/@jacoblouiswright/univarient-forecasting-models-2025-c483d04f04d8)
Lightweight utilities for benchmarking, forecasting, and statistical modeling — with simple `Auto*` model wrappers that tune hyperparameters for you.

## Installation

```bash
pip install randomstatsmodels
```

Requires: Python 3.9+ and NumPy.

---

## Quick Start

```python
from randomstatsmodels import AutoNEO, AutoFourier, AutoKNN, AutoPolymath, AutoThetaAR
import numpy as np

# Toy data: sine wave + noise
rng = np.random.default_rng(42)
t = np.arange(200)
y = np.sin(2*np.pi*t/24) + 0.1*rng.normal(size=t.size)

h = 12  # forecast horizon

model = AutoNEO().fit(y)
yhat = model.predict(h)
print("Forecast:", yhat[:5])
```

---

## Models

Each `Auto*` class:
- accepts a **parameter grid** (or uses sensible defaults),
- fits/evaluates candidates using a chosen metric,
- exposes a unified API: `.fit(y[, X])` and `.predict(h)`.

### AutoNEO

```python
from randomstatsmodels import AutoNEO

neo = AutoNEO(
    param_grid={"n_components": [8, 16, 32]},
    metric="mae",
)
neo.fit(y)
print("Best params:", neo.best_params_)
print("Prediction:", neo.predict(h))
```

### AutoFourier

```python
from randomstatsmodels import AutoFourier

fourier = AutoFourier(
    param_grid={"season_length": [12, 24], "n_terms": [3, 5]},
    metric="smape",
)
fourier.fit(y)
print("Prediction:", fourier.predict(h))
```

### AutoKNN

```python
from randomstatsmodels import AutoKNN

knn = AutoKNN(
    param_grid={"k": [3, 5, 7], "window": [12, 24]},
    metric="rmse",
)
knn.fit(y)
print("Prediction:", knn.predict(h))
```

### AutoPolymath

```python
from randomstatsmodels import AutoPolymath

poly = AutoPolymath(
    param_grid={"degree": [2, 3], "ridge": [0.0, 0.1]},
    metric="mae",
)
poly.fit(y)
print("Prediction:", poly.predict(h))
```

### AutoThetaAR

```python
from randomstatsmodels import AutoThetaAR

theta = AutoThetaAR(
    param_grid={"theta": [0.5, 1.0, 2.0]},
    metric="mape",
)
theta.fit(y)
print("Prediction:", theta.predict(h))
```

---

## Metrics

Available out of the box:

```python
from randomstatsmodels.metrics import mae, rmse, mape, smape
```

---

## License

MIT © 2025 Jacob Wright
