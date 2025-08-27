import numpy as np
import pandas as pd
from scipy.optimize import linprog


def _prep(df: pd.DataFrame, inputs, outputs):
    X = df[inputs].to_numpy(float)  # (n, m)
    Y = df[outputs].to_numpy(float)  # (n, s)
    return X, Y, df.index.astype(str)


# ========================= DUAL (INPUT-ORIENTED) =========================
def dea_ccr_input_dual(df: pd.DataFrame, inputs, outputs) -> pd.DataFrame:
    """
    CCR dual (input): max u^T y0
    s.a. v^T x0 = 1;  u^T Y - v^T X <= 0;  u,v >= 0
    θ* = u^T y0
    """
    X, Y, dmus = _prep(df, inputs, outputs)
    n, m = X.shape
    s = Y.shape[1]
    rows = []

    for k in range(n):
        x0 = X[k]
        y0 = Y[k]
        c = np.zeros(s + m)
        c[:s] = -y0  # max -> min(-)
        A_eq = np.zeros((1, s + m))
        A_eq[0, s:] = x0
        b_eq = np.array([1.0])
        A_ub = np.hstack([Y, -X])
        b_ub = np.zeros(n)
        bounds = [(0, None)] * (s + m)

        res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method="highs")
        if not res.success:
            raise RuntimeError(f"Dual CCR input falhou p/ {dmus[k]}: {res.message}")

        u = res.x[:s]
        v = res.x[s:]
        theta = float(y0 @ u)
        row = {"efficiency": theta}
        row.update({f"u_{c}": u[i] for i, c in enumerate(outputs)})
        row.update({f"v_{c}": v[i] for i, c in enumerate(inputs)})
        rows.append(row)

    return pd.DataFrame(rows, index=dmus)


def dea_bcc_input_dual(df: pd.DataFrame, inputs, outputs) -> pd.DataFrame:
    """
    BCC dual (input): max u^T y0 + u0
    s.a. v^T x0 = 1;  u^T Y - v^T X + u0*1 <= 0;  u,v >= 0; u0 livre
    θ* = u^T y0 + u0
    """
    X, Y, dmus = _prep(df, inputs, outputs)
    n, m = X.shape
    s = Y.shape[1]
    rows = []

    for k in range(n):
        x0 = X[k]
        y0 = Y[k]

        # vars = [u (s), v (m), u0+, u0-]  with u0 = u0+ - u0-
        c = np.zeros(s + m + 2)
        c[:s] = -y0
        c[-2] = -1.0
        c[-1] = +1.0

        A_eq = np.zeros((1, s + m + 2))
        A_eq[0, s : s + m] = x0
        b_eq = np.array([1.0])

        A_ub = np.zeros((n, s + m + 2))
        A_ub[:, :s] = Y
        A_ub[:, s : s + m] = -X
        A_ub[:, -2] = 1.0
        A_ub[:, -1] = -1.0
        b_ub = np.zeros(n)

        bounds = [(0, None)] * (s + m + 2)
        res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method="highs")
        if not res.success:
            raise RuntimeError(f"Dual BCC input falhou p/ {dmus[k]}: {res.message}")

        u = res.x[:s]
        v = res.x[s : s + m]
        u0 = float(res.x[-2] - res.x[-1])
        theta = float(y0 @ u + u0)
        row = {"efficiency": theta, "u0": u0}
        row.update({f"u_{c}": u[i] for i, c in enumerate(outputs)})
        row.update({f"v_{c}": v[i] for i, c in enumerate(inputs)})
        rows.append(row)

    return pd.DataFrame(rows, index=dmus)


# ========================= DUAL (OUTPUT-ORIENTED) =========================
def dea_ccr_output_dual(df: pd.DataFrame, inputs, outputs) -> pd.DataFrame:
    """
    CCR dual (output): min v^T x0
    s.a. u^T y0 = 1;  u^T Y - v^T X <= 0;  u,v >= 0
    Aqui reportamos φ = v^T x0 (alinhado ao retorno do primal).
    """
    X, Y, dmus = _prep(df, inputs, outputs)
    n, m = X.shape
    s = Y.shape[1]
    rows = []

    for k in range(n):
        x0 = X[k]
        y0 = Y[k]

        # vars = [u (s), v (m)]
        c = np.zeros(s + m)
        c[s:] = x0  # min v^T x0

        # u^T y0 = 1
        A_eq = np.zeros((1, s + m))
        A_eq[0, :s] = y0
        b_eq = np.array([1.0])

        # u^T Y - v^T X <= 0
        A_ub = np.hstack([Y, -X])
        b_ub = np.zeros(n)

        bounds = [(0, None)] * (s + m)
        res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method="highs")
        if not res.success:
            raise RuntimeError(f"Dual CCR output falhou p/ {dmus[k]}: {res.message}")

        u = res.x[:s]
        v = res.x[s:]
        phi = float(x0 @ v)  # reportar φ igual ao primal
        row = {"phi": phi}
        row.update({f"u_{c}": u[i] for i, c in enumerate(outputs)})
        row.update({f"v_{c}": v[i] for i, c in enumerate(inputs)})
        rows.append(row)

    return pd.DataFrame(rows, index=dmus)


def dea_bcc_output_dual(df: pd.DataFrame, inputs, outputs) -> pd.DataFrame:
    """
    BCC dual (output): min v^T x0 - u0
    s.a. u^T y0 = 1;  u^T Y - v^T X + u0*1 <= 0;  u,v >= 0; u0 livre
    Reportamos φ = v^T x0 - u0 (alinhado ao primal).
    """
    X, Y, dmus = _prep(df, inputs, outputs)
    n, m = X.shape
    s = Y.shape[1]
    rows = []

    for k in range(n):
        x0 = X[k]
        y0 = Y[k]

        # vars = [u (s), v (m), u0+, u0-]  (u0 = u0+ - u0-)
        c = np.zeros(s + m + 2)
        c[s : s + m] = x0  # parte v^T x0
        c[-2] = -1.0  # - u0  =>  -(u0+ - u0-) = -u0+ + u0-
        c[-1] = +1.0

        # u^T y0 = 1
        A_eq = np.zeros((1, s + m + 2))
        A_eq[0, :s] = y0
        b_eq = np.array([1.0])

        # u^T Y - v^T X + (u0+ - u0-) <= 0
        A_ub = np.zeros((n, s + m + 2))
        A_ub[:, :s] = Y
        A_ub[:, s : s + m] = -X
        A_ub[:, -2] = 1.0
        A_ub[:, -1] = -1.0
        b_ub = np.zeros(n)

        bounds = [(0, None)] * (s + m + 2)
        res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method="highs")
        if not res.success:
            raise RuntimeError(f"Dual BCC output falhou p/ {dmus[k]}: {res.message}")

        u = res.x[:s]
        v = res.x[s : s + m]
        u0 = float(res.x[-2] - res.x[-1])
        phi = float(x0 @ v - u0)  # φ alinhado ao primal
        row = {"phi": phi, "u0": u0}
        row.update({f"u_{c}": u[i] for i, c in enumerate(outputs)})
        row.update({f"v_{c}": v[i] for i, c in enumerate(inputs)})
        rows.append(row)

    return pd.DataFrame(rows, index=dmus)


# -------------------------------
# Post-processing: targets + rótulos amigáveis
# -------------------------------


def _pick_cols(df: pd.DataFrame, prefix: str) -> list[str]:
    """Return all columns starting with a given prefix."""
    return [c for c in df.columns if c.startswith(prefix)]


def compute_targets_from_dual(
    res: pd.DataFrame,
    df_data: pd.DataFrame,
    inputs: list[str],
    outputs: list[str],
    *,
    orientation: str = "output",  # "output" (phi) or "input" (theta)
    add_friendly_labels: bool = True,
) -> pd.DataFrame:
    """
    Add frontier targets and friendly labels to a dual DEA result.

    For OUTPUT orientation (uses φ):
        x* = x - s_minus
        y* = φ · y + s_plus

    For INPUT orientation (uses θ):
        x* = θ · x - s_minus
        y* = y + s_plus

    Parameters
    ----------
    res : DataFrame
        Result returned by dual routines (must contain 'phi' for output
        or 'theta' for input, plus slacks/lambdas if available).
        Index must match df_data.
    df_data : DataFrame
        Original data with input/output columns.
    inputs, outputs : list[str]
        Column names for inputs/outputs in df_data.
    orientation : {"output","input"}
        Which orientation formula to apply for targets.
    add_friendly_labels : bool
        If True, add human-friendly aliases for the technical columns.

    Returns
    -------
    DataFrame
        Copy of `res` with columns:
          - target_x_<input>, target_y_<output>
          - (aliases) target_input:<input>, target_output:<output>
          - (aliases) slack_input:<input>, slack_output:<output>
          - (aliases) peer_weight:<DMU>  (from lambda_*)
          - efficiency(0-1)  (alias for 'efficiency', if present)
    """
    # reindex to ensure alignment
    if not res.index.equals(df_data.index):
        res = res.copy().reindex(df_data.index)

    out = res.copy()

    # collect slacks (fallback to zeros if not present)
    s_minus_cols = _pick_cols(out, "s_minus_")
    s_plus_cols = _pick_cols(out, "s_plus_")
    Sminus = (
        out[s_minus_cols].to_numpy(dtype=float)
        if s_minus_cols
        else np.zeros((len(out), len(inputs)))
    )
    Splus = (
        out[s_plus_cols].to_numpy(dtype=float)
        if s_plus_cols
        else np.zeros((len(out), len(outputs)))
    )

    X = df_data[inputs].to_numpy(dtype=float)
    Y = df_data[outputs].to_numpy(dtype=float)

    if orientation.lower() == "output":
        if "phi" not in out.columns:
            raise KeyError("Column 'phi' is required for output-oriented targets.")
        phi = out["phi"].to_numpy(dtype=float).reshape(-1, 1)
        X_star = X - Sminus
        Y_star = phi * Y + Splus
    elif orientation.lower() == "input":
        if "theta" not in out.columns:
            raise KeyError("Column 'theta' is required for input-oriented targets.")
        theta = out["theta"].to_numpy(dtype=float).reshape(-1, 1)
        X_star = theta * X - Sminus
        Y_star = Y + Splus
    else:
        raise ValueError("orientation must be 'output' or 'input'.")

    # add target columns (technical + friendly aliases)
    for j, name in enumerate(inputs):
        out[f"target_x_{name}"] = X_star[:, j]
        if add_friendly_labels:
            out[f"target_input:{name}"] = out[f"target_x_{name}"]

    for r, name in enumerate(outputs):
        out[f"target_y_{name}"] = Y_star[:, r]
        if add_friendly_labels:
            out[f"target_output:{name}"] = out[f"target_y_{name}"]

    if add_friendly_labels:
        # slacks (friendly aliases)
        for name in inputs:
            col = f"s_minus_{name}"
            if col in out.columns:
                out[f"slack_input:{name}"] = out[col]
        for name in outputs:
            col = f"s_plus_{name}"
            if col in out.columns:
                out[f"slack_output:{name}"] = out[col]
        # peers (lambdas)
        for c in _pick_cols(out, "lambda_"):
            dmu_name = c.replace("lambda_", "")
            out[f"peer_weight:{dmu_name}"] = out[c]
        # efficiency friendly alias
        if "efficiency" in out.columns:
            out["efficiency(0-1)"] = out["efficiency"]

    return out
