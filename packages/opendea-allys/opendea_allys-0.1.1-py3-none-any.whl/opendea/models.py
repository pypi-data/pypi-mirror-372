from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.optimize import linprog

from .core import (
    _solve_input_oriented,
    _solve_output_oriented,
    _solve_super_input,
    _solve_super_output,
)


# ---------------------------------------------------------------------
# Helper: validate and extract X, Y and DMU labels
# ---------------------------------------------------------------------
def _prep(df: pd.DataFrame, inputs: list[str], outputs: list[str]):
    if not isinstance(df, pd.DataFrame):
        raise TypeError("`df` must be a pandas.DataFrame.")
    missing = [c for c in (inputs + outputs) if c not in df.columns]
    if missing:
        raise ValueError(f"Columns not found in DataFrame: {missing}")

    X = df[inputs].to_numpy(dtype=float)
    Y = df[outputs].to_numpy(dtype=float)
    dmus = df.index.astype(str)
    return X, Y, dmus, inputs, outputs


# ===========================
# CCR/BCC Input-oriented
# ===========================
def dea_ccr_input(df: pd.DataFrame, inputs: list[str], outputs: list[str]) -> pd.DataFrame:
    """
    Modelo DEA CCR input-oriented (CRS).
    Minimiza θ sujeito a:
        Σ λ x_i ≤ θ x0
        Σ λ y_i ≥ y0
        λ ≥ 0
    """
    X, Y, dmus, in_names, out_names = _prep(df, inputs, outputs)
    n = X.shape[0]
    rows = []

    for k in range(n):
        theta_k, lam = _solve_input_oriented(X, Y, X[k], Y[k], vrs=False)
        lam = _clean(lam)

        # slacks
        sminus = theta_k * X[k] - X.T @ lam
        splus = Y.T @ lam - Y[k]

        row = {"efficiency": float(theta_k)}
        for j, col in enumerate(in_names):
            row[f"s_minus_{col}"] = float(max(0.0, sminus[j]))
        for t, col in enumerate(out_names):
            row[f"s_plus_{col}"] = float(max(0.0, splus[t]))
        row.update({f"lambda_{dmus[j]}": float(lam[j]) for j in range(n)})
        rows.append((dmus[k], row))

    return pd.DataFrame.from_dict(dict(rows), orient="index")


def dea_bcc_input(df: pd.DataFrame, inputs: list[str], outputs: list[str]) -> pd.DataFrame:
    """
    Modelo DEA BCC input-oriented (VRS).
    Minimiza θ sujeito a:
        Σ λ x_i ≤ θ x0
        Σ λ y_i ≥ y0
        Σ λ = 1
        λ ≥ 0
    """
    X, Y, dmus, in_names, out_names = _prep(df, inputs, outputs)
    n = X.shape[0]
    rows = []

    for k in range(n):
        theta_k, lam = _solve_input_oriented(X, Y, X[k], Y[k], vrs=True)
        lam = _clean(lam)

        # slacks
        sminus = theta_k * X[k] - X.T @ lam
        splus = Y.T @ lam - Y[k]

        row = {"efficiency": float(theta_k)}
        for j, col in enumerate(in_names):
            row[f"s_minus_{col}"] = float(max(0.0, sminus[j]))
        for t, col in enumerate(out_names):
            row[f"s_plus_{col}"] = float(max(0.0, splus[t]))
        row.update({f"lambda_{dmus[j]}": float(lam[j]) for j in range(n)})
        rows.append((dmus[k], row))

    return pd.DataFrame.from_dict(dict(rows), orient="index")


# ===========================
# CCR/BCC Output-oriented
# ===========================
def dea_ccr_output(df: pd.DataFrame, inputs: list[str], outputs: list[str]) -> pd.DataFrame:
    """
    Modelo DEA CCR output-oriented (CRS).
    Maximiza φ sujeito a:
        Σ λ x_i ≤ x0
        Σ λ y_i ≥ φ y0
        λ ≥ 0
    Retorna também efficiency = 1/φ.
    """
    X, Y, dmus, in_names, out_names = _prep(df, inputs, outputs)
    n = X.shape[0]
    rows = []
    eps = 1e-12

    for k in range(n):
        phi_k, lam = _solve_output_oriented(X, Y, X[k], Y[k], vrs=False)
        lam = _clean(lam)

        # slacks
        sminus = X[k] - X.T @ lam
        splus = (Y.T @ lam) - phi_k * Y[k]

        row = {
            "phi": float(phi_k),
            "efficiency": float(1.0 / max(phi_k, eps)),
        }
        for j, col in enumerate(in_names):
            row[f"s_minus_{col}"] = float(max(0.0, sminus[j]))
        for t, col in enumerate(out_names):
            row[f"s_plus_{col}"] = float(max(0.0, splus[t]))
        row.update({f"lambda_{dmus[j]}": float(lam[j]) for j in range(n)})
        rows.append((dmus[k], row))

    return pd.DataFrame.from_dict(dict(rows), orient="index")


def dea_bcc_output(df: pd.DataFrame, inputs: list[str], outputs: list[str]) -> pd.DataFrame:
    """
    Modelo DEA BCC output-oriented (VRS).
    Maximiza φ sujeito a:
        Σ λ x_i ≤ x0
        Σ λ y_i ≥ φ y0
        Σ λ = 1
        λ ≥ 0
    Retorna também efficiency = 1/φ.
    """
    X, Y, dmus, in_names, out_names = _prep(df, inputs, outputs)
    n = X.shape[0]
    rows = []
    eps = 1e-12

    for k in range(n):
        phi_k, lam = _solve_output_oriented(X, Y, X[k], Y[k], vrs=True)
        lam = _clean(lam)

        # slacks
        sminus = X[k] - X.T @ lam
        splus = (Y.T @ lam) - phi_k * Y[k]

        row = {
            "phi": float(phi_k),
            "efficiency": float(1.0 / max(phi_k, eps)),
        }
        for j, col in enumerate(in_names):
            row[f"s_minus_{col}"] = float(max(0.0, sminus[j]))
        for t, col in enumerate(out_names):
            row[f"s_plus_{col}"] = float(max(0.0, splus[t]))
        row.update({f"lambda_{dmus[j]}": float(lam[j]) for j in range(n)})
        rows.append((dmus[k], row))

    return pd.DataFrame.from_dict(dict(rows), orient="index")


# ===========================
# Additive model (non-radial)
# ===========================
def dea_additive(
    df: pd.DataFrame,
    inputs: list[str],
    outputs: list[str],
    vrs: bool = True,
    leave_one_out: bool = True,
) -> pd.DataFrame:
    """
    Modelo DEA Aditivo (não radial), com fallback automático:
      - Primeiro tenta com leave-one-out (se leave_one_out=True).
      - Se a LP ficar inviável para uma DMU, re-solve incluindo a própria DMU
      - no conjunto de referência (apenas para aquela DMU).
    Retorna:
      - 'efficiency'  = 1 / (1 + sum(slacks))
      - slacks        = s_minus_* , s_plus_*
      - lambdas       = lambda_<DMU>
    """
    # imports locais por segurança (caso esse bloco seja movido)

    X, Y, dmus, in_names, out_names = _prep(df, inputs, outputs)
    n, m, r = X.shape[0], X.shape[1], Y.shape[1]
    rows = []

    def _solve_one_k(k: int, ref_idx: list[int]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """resolve a LP aditiva para a DMU k com um conjunto de referência ref_idx"""
        nref = len(ref_idx)
        num_vars = nref + m + r
        L = slice(0, nref)
        SM = slice(nref, nref + m)
        SP = slice(nref + m, nref + m + r)

        # objetivo: minimizar s- + s+
        c = np.zeros(num_vars)
        c[SM] = 1.0
        c[SP] = 1.0

        # igualdade dos inputs: sum λ x + s- = x0
        A_eq1 = np.zeros((m, num_vars))
        A_eq1[:, L] = X[ref_idx].T
        A_eq1[:, SM] = np.eye(m)
        b_eq1 = X[k]

        # igualdade dos outputs: sum λ y - s+ = y0
        A_eq2 = np.zeros((r, num_vars))
        A_eq2[:, L] = Y[ref_idx].T
        A_eq2[:, SP] = -np.eye(r)
        b_eq2 = Y[k]

        A_eq = np.vstack([A_eq1, A_eq2])
        b_eq = np.concatenate([b_eq1, b_eq2])

        if vrs:
            row_vrs = np.zeros((1, num_vars))
            row_vrs[0, L] = 1.0
            A_eq = np.vstack([A_eq, row_vrs])
            b_eq = np.concatenate([b_eq, np.array([1.0])])

        bounds = [(0, None)] * num_vars

        res = linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method="highs")
        if res.status != 0:
            raise RuntimeError(res.message)

        lam_ref = res.x[L]
        s_minus = res.x[SM]
        s_plus = res.x[SP]
        return lam_ref, s_minus, s_plus

    for k in range(n):
        # 1) tenta com LOO (se solicitado)
        used_ref = [i for i in range(n) if not (leave_one_out and i == k)]
        try:
            lam_ref, s_minus, s_plus = _solve_one_k(k, used_ref)
        except RuntimeError:
            # 2) fallback: inclui a própria DMU no conjunto de referência (apenas para esse k)
            if leave_one_out:
                lam_ref, s_minus, s_plus = _solve_one_k(k, list(range(n)))
            else:
                raise

        # remonta lambda no tamanho n
        lam = np.zeros(n)
        # se usamos LOO, precisamos mapear lam_ref para as posições corretas
        if len(used_ref) == n:
            lam[:] = lam_ref
        else:
            for p, idx in enumerate(used_ref):
                lam[idx] = lam_ref[p]

        lam = _clean(lam)

        # eficiência "aditiva" simples (1 / (1 + soma das folgas))
        eff = 1.0 / (1.0 + float(s_minus.sum() + s_plus.sum()))

        row = {"efficiency": eff}
        for j, col in enumerate(in_names):
            row[f"s_minus_{col}"] = float(max(0.0, s_minus[j]))
        for t, col in enumerate(out_names):
            row[f"s_plus_{col}"] = float(max(0.0, s_plus[t]))
        row.update({f"lambda_{dmus[j]}": float(lam[j]) for j in range(n)})

        rows.append((dmus[k], row))

    return pd.DataFrame.from_dict(dict(rows), orient="index")


# ===========================
# Super-Efficiency (AP models)
# ===========================
def _lam_full_from_ref(lam_ref: np.ndarray, n: int, k: int) -> np.ndarray:
    lam_full = np.zeros(n, dtype=float)
    ref_idx = [i for i in range(n) if i != k]
    lam_full[ref_idx] = lam_ref
    return lam_full


def _clean(arr: np.ndarray, tol: float = 1e-9) -> np.ndarray:
    out = np.array(arr, dtype=float, copy=True)
    out[np.abs(out) < tol] = 0.0
    return np.clip(out, 0.0, None)


def super_eff_ccr_input(df: pd.DataFrame, inputs: list[str], outputs: list[str]) -> pd.DataFrame:
    X, Y, dmus, _, _ = _prep(df, inputs, outputs)
    n = X.shape[0]
    rows = []
    eps = 1e-12
    for k in range(n):
        theta_k, lam_ref = _solve_super_input(X, Y, X[k], Y[k], vrs=False, exclude_idx=k)
        # força resultado >= 1 (Shephard inverso)
        se = max(1.0, 1.0 / max(float(theta_k), eps))
        lam_full = _clean(_lam_full_from_ref(lam_ref, n, k))
        row = {"super_eff": float(se)}
        row.update({f"lambda_{dmus[j]}": float(lam_full[j]) for j in range(n)})
        rows.append((dmus[k], row))
    return pd.DataFrame.from_dict(dict(rows), orient="index")


def super_eff_bcc_input(df: pd.DataFrame, inputs: list[str], outputs: list[str]) -> pd.DataFrame:
    X, Y, dmus, _, _ = _prep(df, inputs, outputs)
    n = X.shape[0]
    rows = []
    eps = 1e-12
    for k in range(n):
        theta_k, lam_ref = _solve_super_input(X, Y, X[k], Y[k], vrs=True, exclude_idx=k)
        se = max(1.0, 1.0 / max(float(theta_k), eps))
        lam_full = _clean(_lam_full_from_ref(lam_ref, n, k))
        # normaliza se necessário
        s = lam_full.sum()
        if s > 0:
            lam_full = lam_full / s
        row = {"super_eff": float(se)}
        row.update({f"lambda_{dmus[j]}": float(lam_full[j]) for j in range(n)})
        rows.append((dmus[k], row))
    return pd.DataFrame.from_dict(dict(rows), orient="index")


def super_eff_ccr_output(df: pd.DataFrame, inputs: list[str], outputs: list[str]) -> pd.DataFrame:
    X, Y, dmus, _, _ = _prep(df, inputs, outputs)
    n = X.shape[0]
    rows = []
    for k in range(n):
        phi_k, lam_ref = _solve_super_output(X, Y, X[k], Y[k], vrs=False, exclude_idx=k)
        lam_full = _clean(_lam_full_from_ref(lam_ref, n, k))
        row = {"super_eff": float(max(1.0, phi_k))}
        row.update({f"lambda_{dmus[j]}": float(lam_full[j]) for j in range(n)})
        rows.append((dmus[k], row))
    return pd.DataFrame.from_dict(dict(rows), orient="index")


def super_eff_bcc_output(df: pd.DataFrame, inputs: list[str], outputs: list[str]) -> pd.DataFrame:
    X, Y, dmus, _, _ = _prep(df, inputs, outputs)
    n = X.shape[0]
    rows = []
    for k in range(n):
        phi_k, lam_ref = _solve_super_output(X, Y, X[k], Y[k], vrs=True, exclude_idx=k)
        se = max(1.0, float(phi_k))
        lam_full = _clean(_lam_full_from_ref(lam_ref, n, k))
        # forma estável: ∑λ ≤ 1, normaliza se passar
        s = lam_full.sum()
        if s > 1 + 1e-9:
            lam_full = lam_full / s
        row = {"super_eff": float(se)}
        row.update({f"lambda_{dmus[j]}": float(lam_full[j]) for j in range(n)})
        rows.append((dmus[k], row))
    return pd.DataFrame.from_dict(dict(rows), orient="index")
