"""From-scratch multiple linear regression with L2 regularisation (Question 1).
Generated from the code shown in Q1/02_Q1_Implementation.ipynb."""
import numpy as np
import pandas as pd
from pathlib import Path


def fit_scaler(X, method="standard"):
    """Learn the scaling parameters from the TRAINING data only (avoids data leakage)."""
    X = np.asarray(X, dtype=float)
    if method == "standard":            # z-score: (x - mean) / std
        center, scale = X.mean(axis=0), X.std(axis=0)
    elif method == "minmax":            # (x - min) / (max - min)
        center, scale = X.min(axis=0), X.max(axis=0) - X.min(axis=0)
    elif method == "none":              # no scaling (used only for the experiment)
        center, scale = np.zeros(X.shape[1]), np.ones(X.shape[1])
    else:
        raise ValueError("method must be 'standard', 'minmax' or 'none'")
    scale = np.where(scale == 0, 1.0, scale)   # protect against constant columns
    return {"method": method, "center": center, "scale": scale}


def apply_scaler(X, scaler):
    """Apply already-learned scaling parameters (works for train AND test data)."""
    return (np.asarray(X, dtype=float) - scaler["center"]) / scaler["scale"]


def add_bias(X):
    """Prepend the column x0 = 1 so that theta_0 is handled like every other theta_j."""
    return np.hstack([np.ones((X.shape[0], 1)), X])


def hypothesis(X_b, theta):
    """h_theta(x) = theta_0 + theta_1 x_1 + ... + theta_n x_n   (vectorised: X_b @ theta)."""
    return X_b @ theta


def cost_function(X_b, y, theta, lam=0.0):
    """J(theta) = 1/(2m) * [ sum (h - y)^2 + lambda * sum_{j>=1} theta_j^2 ]  (theta_0 NOT regularised)."""
    m = len(y)
    errors = hypothesis(X_b, theta) - y
    reg_term = lam * np.sum(theta[1:] ** 2)
    return (np.sum(errors ** 2) + reg_term) / (2 * m)


def gradient(X_b, y, theta, lam=0.0):
    """Vector form of dJ/dtheta:  (1/m) * [ X^T (X theta - y) + lambda * theta_tilde ],  theta_tilde = [0, theta_1..theta_n]."""
    m = len(y)
    errors = hypothesis(X_b, theta) - y
    grad = (X_b.T @ errors) / m          # j = 0 and the data part of j >= 1
    grad[1:] += (lam / m) * theta[1:]    # regularisation part (only for j >= 1)
    return grad


def gradient_descent(X_b, y, alpha=0.1, lam=0.0, n_iters=2000, theta0=None, tol=0.0):
    """Batch gradient descent. Returns (theta, cost_history)."""
    m, n_plus_1 = X_b.shape
    theta = np.zeros(n_plus_1) if theta0 is None else np.array(theta0, dtype=float)
    history = []
    with np.errstate(all="ignore"):
        for it in range(n_iters):
            cost = cost_function(X_b, y, theta, lam)
            history.append(cost)
            if not np.isfinite(cost) or cost > 1e30:        # diverged -> stop early
                break
            if tol and it > 0 and abs(history[-2] - cost) < tol:   # converged
                break
            theta = theta - alpha * gradient(X_b, y, theta, lam)   # simultaneous update of all theta_j
    return theta, np.array(history)


def mse(y_true, y_pred):
    """Mean Squared Error = mean((y - y_hat)^2)   (this is NOT the same as J(theta))."""
    y_true, y_pred = np.asarray(y_true, float), np.asarray(y_pred, float)
    return float(np.mean((y_true - y_pred) ** 2))


def r2_score_manual(y_true, y_pred):
    y_true, y_pred = np.asarray(y_true, float), np.asarray(y_pred, float)
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - y_true.mean()) ** 2)
    return float(1 - ss_res / ss_tot)


def normal_equation(X_b, y, lam=0.0):
    """Closed-form solution theta = (X^T X + lambda * L)^-1 X^T y, L = identity with L[0,0] = 0.
    Used only to VERIFY that gradient descent reached the true minimum."""
    n_plus_1 = X_b.shape[1]
    L = np.eye(n_plus_1)
    L[0, 0] = 0.0
    return np.linalg.solve(X_b.T @ X_b + lam * L, X_b.T @ y)


def theta_to_original_units(theta, scaler):
    """Convert theta learned on scaled features back to the original feature units
    (so it can be compared directly with scikit-learn's intercept_ and coef_)."""
    coefs = theta[1:] / scaler["scale"]
    intercept = theta[0] - np.sum(theta[1:] * scaler["center"] / scaler["scale"])
    return np.concatenate([[intercept], coefs])


def load_regression_data(data_dir, filename=None, target=None, drop_cols=()):
    """Load the multiple-linear-regression dataset (csv/xlsx) from data_dir.
    - target=None  -> the LAST column is used as the target y
    - text columns are one-hot encoded, missing numeric values are filled with the median.
    Returns X (DataFrame), y (Series), the path of the file, and the raw DataFrame."""
    data_dir = Path(data_dir)
    if filename:
        path = data_dir / filename
    else:
        files = sorted(p for p in data_dir.glob("*") if p.suffix.lower() in (".csv", ".xlsx", ".xls"))
        if not files:
            raise FileNotFoundError(
                f"No dataset found in {data_dir}. Download the 'multiple linear regression dataset' "
                "(link inside the exam paper) and put the CSV file in that folder.")
        path = files[0]
    df = pd.read_excel(path) if path.suffix.lower() in (".xlsx", ".xls") else pd.read_csv(path)
    df = df.loc[:, ~df.columns.astype(str).str.contains("^Unnamed")]
    df = df.drop(columns=[c for c in drop_cols if c in df.columns])
    target = target or df.columns[-1]
    df = df.dropna(subset=[target])
    y = pd.to_numeric(df[target], errors="coerce")
    X = df.drop(columns=[target])
    X = pd.get_dummies(X, drop_first=True, dtype=float)
    X = X.fillna(X.median())
    ok = y.notna()
    return X[ok].reset_index(drop=True), y[ok].reset_index(drop=True), path, df
