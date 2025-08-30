import numpy as np
from ..metrics import mse


# ================== HybridForecastNet =================
class HybridForecastNet:
    """
    Hybrid Dynamical Fourier + Trend/AR + GRU-residual forecaster.

    The model linearly combines:
      • Seasonal harmonics (Fourier pairs at multiples of 2π / seasonal_period)
      • Polynomial trend up to `trend_degree`
      • Autoregressive (AR) lags up to `ar_order`
    and then learns a nonlinear **residual** mapping with a lightweight GRU.

    Equation (ASCII)
    ----------------
        y[t] ≈  Linear_{Fourier, Trend, AR}(t, y[t-1..])  +  GRU( residual window )

    Deterministic point forecasts by default (can be extended to probabilistic).

    Parameters
    ----------
    seasonal_period : int, default=24
        Fundamental seasonal period used by the Fourier block.
    fourier_order : int, default=3
        Number of Fourier harmonics. Uses k = 1..fourier_order with both cos/sin.
    trend_degree : int, default=1
        Polynomial trend degree (0 = intercept only).
    ar_order : int, default=3
        Number of AR lags in the linear part.
    hidden_size : int, default=16
        GRU hidden width.
    rnn_layers : int, default=1
        (Reserved) Number of stacked GRU layers. Current implementation trains a single GRU cell;
        this value is stored for API compatibility.
    epochs : int, default=100
        Training epochs for the residual GRU (full-batch).
    lr : float, default=0.01
        Learning rate for the GRU parameters.
    seed : int, default=123
        Random seed for initialization.

    Attributes
    ----------
    _fourier_coefs : ndarray of shape (2*fourier_order,)
        Learned Fourier coefficients [cos terms | sin terms] (on normalized y).
    _trend_coefs : ndarray of shape (trend_degree + 1,)
        Polynomial trend coefficients (on normalized y).
    _ar_coefs : ndarray of shape (ar_order,)
        AR coefficients (on normalized y).
    _rnn : dict
        Container of GRU parameters (weights, biases, hidden size).
    _y_mean : float
        Training mean of the series (for de/normalization).
    _y_std : float
        Training std of the series (for de/normalization).
    _y_train_norm : ndarray
        Normalized training series.
    _residual_norm : ndarray
        Residuals (normalized) after fitting the linear block on training data.
    _linear_fitted : ndarray
        Linear block in-sample fit on normalized data.
    _seq_len : int
        Residual window length used to train the GRU (ties to `ar_order`).
    _res_window_init : ndarray of shape (_seq_len,)
        Last residual window from training (seed for forecasting).
    _ar_buffer_init : ndarray of shape (max(1, ar_order),)
        Last normalized lags from training (seed for AR recursion).
    train_loss_history : list of float
        Per-epoch average training loss for the GRU residual model.
    """

    def __init__(
        self,
        seasonal_period=24,
        fourier_order=3,
        trend_degree=1,
        ar_order=3,
        hidden_size=16,
        rnn_layers=1,
        epochs=100,
        lr=0.01,
        seed=123,
    ):
        self.seasonal_period = int(seasonal_period)
        self.fourier_order = int(max(0, fourier_order))
        self.trend_degree = int(max(0, trend_degree))
        self.ar_order = int(max(0, ar_order))
        self.hidden_size = int(max(1, hidden_size))
        self.rnn_layers = int(max(1, rnn_layers))
        self.epochs = int(max(1, epochs))
        self.lr = float(lr)
        self.seed = int(seed)

        # learned linear parts
        self._fourier_coefs = None  # (2*fourier_order,)
        self._trend_coefs = None  # (trend_degree+1,)
        self._ar_coefs = None  # (ar_order,)

        # learned GRU params (single-layer GRU + linear head)
        self._rnn = None

        # training artifacts
        self._y_mean = 0.0
        self._y_std = 1.0
        self._y_train_norm = None  # (n,)
        self._residual_norm = None  # (n,)
        self._linear_fitted = None  # (n,)
        self._seq_len = None  # residual window length used to train GRU
        self._res_window_init = None  # (seq_len,) last residual window from training
        self._ar_buffer_init = None  # (max(1, ar_order),) last y_norm lags from training

        self.train_loss_history = []

    # ---------- feature builders ----------

    def _fourier_feats(self, t_idx):
        """Return stacked cos/sin features for k=1..fourier_order at time index `t_idx`."""
        if self.fourier_order == 0:
            return np.empty(0, dtype=float)
        k = np.arange(1, self.fourier_order + 1, dtype=float)
        ang = 2.0 * np.pi * (t_idx / self.seasonal_period) * k
        return np.concatenate([np.cos(ang), np.sin(ang)], axis=0)  # length 2*order

    def _trend_val(self, t_idx):
        """Evaluate the polynomial trend at integer time index `t_idx`."""
        if self.trend_degree < 0:
            return 0.0
        return sum(self._trend_coefs[d] * (t_idx**d) for d in range(self.trend_degree + 1))

    def _prepare_design_matrix(self, y_norm):
        """Build the linear-block design matrix [Fourier | Trend | AR] on normalized series."""
        n = len(y_norm)
        t = np.arange(n, dtype=float)

        # Fourier block
        if self.fourier_order > 0:
            k = np.arange(1, self.fourier_order + 1, dtype=float)[None, :]
            ang = 2.0 * np.pi * (t[:, None] / self.seasonal_period) * k
            cos_terms = np.cos(ang)
            sin_terms = np.sin(ang)
            S = np.concatenate([cos_terms, sin_terms], axis=1)  # (n, 2*order)
        else:
            S = np.empty((n, 0), dtype=float)

        # Trend block
        if self.trend_degree >= 0:
            T = np.vstack([t**d for d in range(self.trend_degree + 1)]).T  # (n, deg+1)
        else:
            T = np.empty((n, 0), dtype=float)

        # AR block
        if self.ar_order > 0:
            A = np.zeros((n, self.ar_order), dtype=float)
            A[:] = np.nan
            for lag in range(1, self.ar_order + 1):
                A[lag:, lag - 1] = y_norm[:-lag]
            # fill NaNs with first value to avoid dropping rows
            A[np.isnan(A)] = y_norm[0]
        else:
            A = np.empty((n, 0), dtype=float)

        X = np.concatenate([S, T, A], axis=1)
        return X

    # ---------- GRU helpers ----------

    def _init_gru(self):
        """Initialize GRU parameters (single-cell) with small random weights."""
        rs = np.random.RandomState(self.seed)
        H = self.hidden_size
        # Single input scalar per step (residual)
        W_z = rs.randn(H, 1) * 0.1
        U_z = rs.randn(H, H) * 0.1
        b_z = np.zeros(H)
        W_r = rs.randn(H, 1) * 0.1
        U_r = rs.randn(H, H) * 0.1
        b_r = np.zeros(H)
        W_h = rs.randn(H, 1) * 0.1
        U_h = rs.randn(H, H) * 0.1
        b_h = np.zeros(H)
        V_o = rs.randn(H) * 0.1
        c_o = 0.0
        return {
            "W_z": W_z,
            "U_z": U_z,
            "b_z": b_z,
            "W_r": W_r,
            "U_r": U_r,
            "b_r": b_r,
            "W_h": W_h,
            "U_h": U_h,
            "b_h": b_h,
            "V_o": V_o,
            "c_o": c_o,
            "H": H,
        }

    @staticmethod
    def _sigmoid(x):
        return 1.0 / (1.0 + np.exp(-x))

    @staticmethod
    def _tanh(x):
        return np.tanh(x)

    def _gru_forward_once(self, rnn, seq):
        """
        Run a GRU over a residual window.

        Parameters
        ----------
        rnn : dict
            GRU parameter dictionary.
        seq : ndarray of shape (L,)
            Residual window sequence.

        Returns
        -------
        h_final : ndarray of shape (H,)
            Final hidden state.
        y_pred : float
            Predicted next residual.
        """
        W_z, U_z, b_z = rnn["W_z"], rnn["U_z"], rnn["b_z"]
        W_r, U_r, b_r = rnn["W_r"], rnn["U_r"], rnn["b_r"]
        W_h, U_h, b_h = rnn["W_h"], rnn["U_h"], rnn["b_h"]
        V_o, c_o = rnn["V_o"], rnn["c_o"]
        H = rnn["H"]

        h = np.zeros(H, dtype=float)
        for x in seq:
            x1 = np.array([x], dtype=float)  # (1,)
            z = self._sigmoid(W_z @ x1 + U_z @ h + b_z)  # (H,)
            r = self._sigmoid(W_r @ x1 + U_r @ h + b_r)  # (H,)
            h_tilde = self._tanh(W_h @ x1 + U_h @ (r * h) + b_h)  # (H,)
            h = z * h + (1.0 - z) * h_tilde
        y_pred = V_o.dot(h) + c_o
        return h, float(y_pred)

    # ---------- fit / predict ----------

    def fit(self, y):
        """
        Fit the hybrid model.

        Steps:
          1) Normalize y.
          2) Fit the linear block (Fourier + Trend + AR) via least squares.
          3) Compute residuals and train a small GRU to predict next residual.

        Parameters
        ----------
        y : ndarray of shape (n_samples,)
            Univariate time series.

        Returns
        -------
        self : HybridForecastNet
            Fitted model instance.

        Raises
        ------
        ValueError
            If the series is too short for the configured `ar_order`.
        """
        y = np.asarray(y, dtype=float)
        n = len(y)
        if n < max(3, self.ar_order + 1):
            raise ValueError("Series too short for configuration.")

        # normalize
        self._y_mean = y.mean()
        self._y_std = y.std() if y.std() > 1e-8 else 1.0
        y_norm = (y - self._y_mean) / self._y_std
        self._y_train_norm = y_norm.copy()

        # linear fit
        X = self._prepare_design_matrix(y_norm)
        beta, *_ = np.linalg.lstsq(X, y_norm, rcond=None)
        p = 2 * self.fourier_order
        q = self.trend_degree + 1
        r = self.ar_order
        self._fourier_coefs = beta[:p] if p > 0 else np.zeros(0)
        self._trend_coefs = beta[p : p + q] if q > 0 else np.zeros(0)
        self._ar_coefs = beta[p + q : p + q + r] if r > 0 else np.zeros(0)

        linear_fitted = X @ beta
        self._linear_fitted = linear_fitted
        residual = y_norm - linear_fitted
        self._residual_norm = residual

        # residual windows for GRU
        seq_len = max(1, self.ar_order)  # tie window to AR depth
        self._seq_len = seq_len
        X_res = []
        Y_res = []
        for t in range(seq_len - 1, n - 1):
            X_res.append(residual[t - seq_len + 1 : t + 1])
            Y_res.append(residual[t + 1])
        X_res = np.array(X_res, dtype=float)  # (N_s, L)
        Y_res = np.array(Y_res, dtype=float)  # (N_s,)

        # initialize GRU
        rnn = self._init_gru()

        # simple full-batch gradient descent through time (coarse but OK)
        lr = self.lr
        H = rnn["H"]
        for epoch in range(self.epochs):
            d = {k: np.zeros_like(v) if isinstance(v, np.ndarray) else 0.0 for k, v in rnn.items()}
            total_loss = 0.0

            for i in range(X_res.shape[0]):
                seq = X_res[i]
                target = Y_res[i]

                # forward + store for BPTT
                W_z, U_z, b_z = rnn["W_z"], rnn["U_z"], rnn["b_z"]
                W_r, U_r, b_r = rnn["W_r"], rnn["U_r"], rnn["b_r"]
                W_h, U_h, b_h = rnn["W_h"], rnn["U_h"], rnn["b_h"]
                V_o, c_o = rnn["V_o"], rnn["c_o"]

                hs = [np.zeros(H, dtype=float)]
                zs, rs, hts, xs = [], [], [], []
                h = hs[0]
                for x in seq:
                    x1 = np.array([x], dtype=float)
                    z = self._sigmoid(W_z @ x1 + U_z @ h + b_z)
                    r = self._sigmoid(W_r @ x1 + U_r @ h + b_r)
                    h_tilde = self._tanh(W_h @ x1 + U_h @ (r * h) + b_h)
                    h = z * h + (1.0 - z) * h_tilde

                    xs.append(x1)
                    zs.append(z)
                    rs.append(r)
                    hts.append(h_tilde)
                    hs.append(h)

                y_pred = V_o.dot(h) + c_o
                err = y_pred - target
                total_loss += 0.5 * err * err

                # backprop output
                d["V_o"] += err * h
                d["c_o"] += err
                dh_next = err * V_o

                # BPTT
                for t in reversed(range(len(seq))):
                    h_prev = hs[t]
                    h_curr = hs[t + 1]
                    z = zs[t]
                    r = rs[t]
                    h_tilde = hts[t]
                    x1 = xs[t]

                    # h = z * h_prev + (1 - z) * h_tilde
                    dh = dh_next.copy()
                    dh_prev = z * dh
                    dh_tilde = (1.0 - z) * dh
                    dz = (h_prev - h_tilde) * dh

                    # activations
                    dz_net = dz * z * (1.0 - z)
                    dh_tilde_net = dh_tilde * (1.0 - h_tilde**2)

                    # r gate grad via candidate path
                    dr_from_ht = (rnn["U_h"].T @ dh_tilde_net) * h_prev
                    dr_net = dr_from_ht * r * (1.0 - r)

                    # params grads
                    d["W_z"] += dz_net[:, None] * x1[None, :]
                    d["U_z"] += dz_net[:, None] * h_prev[None, :]
                    d["b_z"] += dz_net

                    d["W_r"] += dr_net[:, None] * x1[None, :]
                    d["U_r"] += dr_net[:, None] * h_prev[None, :]
                    d["b_r"] += dr_net

                    d["W_h"] += dh_tilde_net[:, None] * x1[None, :]
                    d["U_h"] += dh_tilde_net[:, None] * (r * h_prev)[None, :]
                    d["b_h"] += dh_tilde_net

                    # to previous h
                    dh_prev += rnn["U_z"].T @ dz_net
                    dh_prev += rnn["U_r"].T @ dr_net
                    dh_prev += r * (rnn["U_h"].T @ dh_tilde_net)
                    dh_next = dh_prev

            # update step (average)
            N = X_res.shape[0]
            for k in [
                "W_z",
                "U_z",
                "b_z",
                "W_r",
                "U_r",
                "b_r",
                "W_h",
                "U_h",
                "b_h",
                "V_o",
                "c_o",
            ]:
                rnn[k] -= (lr / max(1, N)) * d[k]
            self.train_loss_history.append(float(total_loss) / max(1, N))

        self._rnn = rnn

        # buffers for inference
        # last residual window (length seq_len)
        self._res_window_init = residual[-self._seq_len :].copy()
        # last AR buffer: last max(1, ar_order) normalized values
        L = max(1, self.ar_order)
        self._ar_buffer_init = y_norm[-L:].copy()
        return self

    def _linear_forecast_norm(self, current_index, ar_buffer):
        """Compute linear part (normalized space) at future index, using AR buffer."""
        # Fourier
        fourier = 0.0
        if self.fourier_order > 0 and self._fourier_coefs.size > 0:
            k = np.arange(1, self.fourier_order + 1, dtype=float)
            ang = 2.0 * np.pi * (current_index / self.seasonal_period) * k
            cos_vals = np.cos(ang)
            sin_vals = np.sin(ang)
            fourier = float(
                cos_vals.dot(self._fourier_coefs[: self.fourier_order])
                + sin_vals.dot(self._fourier_coefs[self.fourier_order : 2 * self.fourier_order])
            )

        # Trend
        trend = 0.0
        if self._trend_coefs is not None and self._trend_coefs.size > 0:
            trend = sum(self._trend_coefs[d] * (current_index**d) for d in range(self.trend_degree + 1))

        # AR
        ar_part = 0.0
        if self.ar_order > 0 and self._ar_coefs.size > 0:
            # ar_buffer[-1] is most recent actual y_norm
            for lag in range(1, self.ar_order + 1):
                ar_part += self._ar_coefs[lag - 1] * ar_buffer[-lag]

        return fourier + trend + ar_part

    def predict(self, h):
        """
        Forecast future values.

        Parameters
        ----------
        h : int
            Forecast horizon (number of steps ahead).

        Returns
        -------
        preds : ndarray of shape (h,)
            Point forecasts.

        Raises
        ------
        RuntimeError
            If called before `fit()`.
        """
        if self._y_train_norm is None or self._rnn is None:
            raise RuntimeError("Call fit() before predict().")
        h = int(h)
        if h <= 0:
            return np.array([], dtype=float)

        n_train = len(self._y_train_norm)
        ar_buffer = self._ar_buffer_init.copy()
        res_window = self._res_window_init.copy()

        preds_norm = []
        for step in range(h):
            t_idx = n_train + step
            lin = self._linear_forecast_norm(t_idx, ar_buffer)
            # GRU over residual window -> next residual prediction
            _, res_pred = self._gru_forward_once(self._rnn, res_window)
            y_pred_norm = lin + res_pred

            preds_norm.append(y_pred_norm)

            # roll buffers
            if self.ar_order > 0:
                ar_buffer = np.append(ar_buffer, y_pred_norm)[-max(1, self.ar_order) :]
            res_window = np.append(res_window, res_pred)[-self._seq_len :]

        preds_norm = np.array(preds_norm, dtype=float)
        return preds_norm * self._y_std + self._y_mean


# ============ AutoHybridForecaster ==============
class AutoHybridForecaster:
    """
    Validation tuner for :class:`HybridForecastNet`.

    Performs a grid search over Fourier order, trend degree, AR order, and GRU
    hidden size. Uses a holdout validation split, selects the configuration
    with the lowest MSE on the validation set, then refits the best model
    on the full series.

    ``season_length`` is accepted as an alias for ``seasonal_period``.

    Parameters
    ----------
    seasonal_period : int, default=24
        Fundamental seasonal period used by the Fourier block.
    season_length : int or None, default=None
        Alias for ``seasonal_period``. If provided, overrides ``seasonal_period``.
    candidate_fourier : iterable of int, default=(0, 3, 6)
        Candidate numbers of Fourier harmonics.
    candidate_trend : iterable of int, default=(0, 1)
        Candidate polynomial trend degrees.
    candidate_ar : iterable of int, default=(0, 3, 5)
        Candidate AR orders.
    candidate_hidden : iterable of int, default=(8, 16, 32)
        Candidate GRU hidden sizes.
    rnn_layers : int, default=1
        (Reserved) Number of GRU layers; current implementation trains one GRU cell.
    epochs : int, default=100
        Training epochs for the residual GRU in each candidate model.
    lr : float, default=0.01
        Learning rate for GRU training.
    val_ratio : float, default=0.2
        Fraction of the series reserved for validation (tail split).
    seed : int, default=123
        Random seed for reproducibility.

    Attributes
    ----------
    best_model : HybridForecastNet or None
        Best model refit on the full dataset.
    best_config : dict or None
        Dictionary with the best hyperparameters:
        ``{"fourier_order", "trend_degree", "ar_order", "hidden_size"}``.
    best_val_mse : float or None
        Best validation MSE achieved during tuning.
    """

    def __init__(
        self,
        seasonal_period=24,
        season_length=None,  # alias
        candidate_fourier=(0, 3, 6),
        candidate_trend=(0, 1),
        candidate_ar=(0, 3, 5),
        candidate_hidden=(8, 16, 32),
        rnn_layers=1,
        epochs=100,
        lr=0.01,
        val_ratio=0.2,
        seed=123,
    ):
        self.seasonal_period = int(seasonal_period if season_length is None else season_length)
        self.candidate_fourier = tuple(candidate_fourier)
        self.candidate_trend = tuple(candidate_trend)
        self.candidate_ar = tuple(candidate_ar)
        self.candidate_hidden = tuple(candidate_hidden)
        self.rnn_layers = int(rnn_layers)
        self.epochs = int(max(1, epochs))
        self.lr = float(lr)
        self.val_ratio = float(val_ratio)
        self.seed = int(seed)

        self.best_model = None
        self.best_config = None
        self.best_val_mse = None

    def fit(self, y):
        """
        Run grid search on a validation split and refit the best model.

        Parameters
        ----------
        y : ndarray of shape (n_samples,)
            Univariate time series.

        Returns
        -------
        self : AutoHybridForecaster
            Fitted tuner with `best_model`, `best_config`, and `best_val_mse` set.

        Raises
        ------
        ValueError
            If the series is too short to create a meaningful validation split.
        RuntimeError
            If no valid configuration can be fitted.
        """
        y = np.asarray(y, dtype=float)
        n = len(y)
        split = max(1, int(n * (1.0 - self.val_ratio)))
        if split < 5 or n - split < 5:
            raise ValueError("Series too short for validation split.")

        y_train = y[:split]
        y_val = y[split:]

        best_mse = np.inf
        best_model = None
        best_cfg = None

        for fo in self.candidate_fourier:
            for td in self.candidate_trend:
                for ar in self.candidate_ar:
                    for hs in self.candidate_hidden:
                        try:
                            model = HybridForecastNet(
                                seasonal_period=self.seasonal_period,
                                fourier_order=fo,
                                trend_degree=td,
                                ar_order=ar,
                                hidden_size=hs,
                                rnn_layers=self.rnn_layers,
                                epochs=self.epochs,
                                lr=self.lr,
                                seed=self.seed,
                            )
                            model.fit(y_train)
                            preds = model.predict(len(y_val))  # <- fixed: model now has needed state
                            mse_value = mse(y_val, preds)
                        except Exception:
                            continue
                        if mse_value < best_mse:
                            best_mse = mse_value
                            best_model = model
                            best_cfg = dict(
                                fourier_order=fo,
                                trend_degree=td,
                                ar_order=ar,
                                hidden_size=hs,
                            )

        if best_model is None:
            raise RuntimeError("AutoHybridForecaster failed to find a valid configuration.")

        # Refit best on full data to finalize
        final = HybridForecastNet(
            seasonal_period=self.seasonal_period,
            fourier_order=best_cfg["fourier_order"],
            trend_degree=best_cfg["trend_degree"],
            ar_order=best_cfg["ar_order"],
            hidden_size=best_cfg["hidden_size"],
            rnn_layers=self.rnn_layers,
            epochs=self.epochs,
            lr=self.lr,
            seed=self.seed,
        ).fit(y)

        self.best_model = final
        self.best_config = best_cfg
        self.best_val_mse = best_mse
        return self

    def predict(self, h):
        """
        Forecast using the best fitted :class:`HybridForecastNet`.

        Parameters
        ----------
        h : int
            Forecast horizon (number of steps ahead).

        Returns
        -------
        preds : ndarray of shape (h,)
            Forecasted values.

        Raises
        ------
        RuntimeError
            If called before :meth:`fit`.
        """
        if self.best_model is None:
            raise RuntimeError("Call fit() first.")
        return self.best_model.predict(h)
