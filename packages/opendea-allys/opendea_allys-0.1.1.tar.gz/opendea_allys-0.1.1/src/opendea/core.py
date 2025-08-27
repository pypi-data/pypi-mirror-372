# ============================================================================
# core.py – Core linear programming solvers for DEA models
# ============================================================================

from __future__ import annotations

import numpy as np
from scipy.optimize import linprog


# ============================================================================
# CCR/BCC Input-Oriented
# ============================================================================
def _solve_input_oriented(
    X: np.ndarray,
    Y: np.ndarray,
    x0: np.ndarray,
    y0: np.ndarray,
    vrs: bool,
    exclude_idx: int | None = None,
):
    """
    CCR/BCC input-oriented (envelopment).
    Minimize θ
    s.t.   X λ ≤ θ x0
           Y λ ≥ y0
           λ ≥ 0
           (VRS) 1'λ = 1
    """
    n, m_in = X.shape
    m_out = Y.shape[1]

    # leave-one-out (optional)
    mask = np.ones(n, dtype=bool)
    if exclude_idx is not None:
        mask[exclude_idx] = False
    Xr, Yr = X[mask], Y[mask]
    nref = Xr.shape[0]

    # objective: minimize θ
    c = np.zeros(nref + 1)
    c[-1] = 1.0

    # X λ - θ x0 ≤ 0
    A_ub_in = np.hstack([Xr.T, -x0.reshape(-1, 1)])
    b_ub_in = np.zeros(m_in)

    # -Y λ ≤ -y0   (=> Y λ ≥ y0)
    A_ub_out = np.hstack([-Yr.T, np.zeros((m_out, 1))])
    b_ub_out = -y0

    A_ub = np.vstack([A_ub_in, A_ub_out])
    b_ub = np.concatenate([b_ub_in, b_ub_out])

    A_eq, b_eq = None, None
    if vrs:
        A_eq = np.hstack([np.ones((1, nref)), np.zeros((1, 1))])
        b_eq = np.array([1.0])

    bounds = [(0, None)] * nref + [(0, None)]

    res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method="highs")
    if not res.success:
        raise RuntimeError(f"LP (input-oriented) did not converge: {res.message}")

    lambdas = res.x[:nref]
    theta = float(res.x[-1])

    lam_full = np.zeros(n)
    lam_full[mask] = lambdas

    return theta, lam_full


# ============================================================================
# CCR/BCC Output-Oriented
# ============================================================================
def _solve_output_oriented(
    X: np.ndarray,
    Y: np.ndarray,
    x0: np.ndarray,
    y0: np.ndarray,
    vrs: bool,
    exclude_idx: int | None = None,
):
    """
    CCR/BCC output-oriented (envelopment).
    Maximize φ   <=> minimize -φ
    s.t.   X λ ≤ x0
           Y λ ≥ φ y0
           λ ≥ 0
           (VRS) 1'λ = 1
    """
    n, m_in = X.shape
    m_out = Y.shape[1]

    mask = np.ones(n, dtype=bool)
    if exclude_idx is not None:
        mask[exclude_idx] = False
    Xr, Yr = X[mask], Y[mask]
    nref = Xr.shape[0]

    c = np.zeros(nref + 1)
    c[-1] = -1.0  # maximize φ

    # X λ ≤ x0
    A_ub_in = np.hstack([Xr.T, np.zeros((m_in, 1))])
    b_ub_in = x0

    # -Y λ + φ y0 ≤ 0
    A_ub_out = np.hstack([-Yr.T, y0.reshape(-1, 1)])
    b_ub_out = np.zeros(m_out)

    A_ub = np.vstack([A_ub_in, A_ub_out])
    b_ub = np.concatenate([b_ub_in, b_ub_out])

    A_eq, b_eq = None, None
    if vrs:
        A_eq = np.hstack([np.ones((1, nref)), np.zeros((1, 1))])
        b_eq = np.array([1.0])

    bounds = [(0, None)] * nref + [(0, None)]

    res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method="highs")
    if not res.success:
        raise RuntimeError(f"LP (output-oriented) did not converge: {res.message}")

    lambdas = res.x[:nref]
    phi = float(res.x[-1])

    lam_full = np.zeros(n)
    lam_full[mask] = lambdas

    return phi, lam_full


# ============================================================================
# Additive Model (non-radial)
# ============================================================================
def _solve_additive(
    X: np.ndarray,
    Y: np.ndarray,
    x0: np.ndarray,
    y0: np.ndarray,
    *,
    vrs: bool,
    exclude_idx: int | None = None,
):
    """
    Additive model (non-radial).
    Minimize sum(s−) + sum(s+)
    s.t.   X λ + s− = x0
           Y λ - s+ = y0
           λ ≥ 0, s− ≥ 0, s+ ≥ 0
           (VRS) 1'λ = 1
    """
    n, m_in = X.shape
    m_out = Y.shape[1]

    mask = np.ones(n, dtype=bool)
    if exclude_idx is not None:
        mask[exclude_idx] = False
    Xr, Yr = X[mask], Y[mask]
    nref = Xr.shape[0]

    num_vars = nref + m_in + m_out
    L = slice(0, nref)
    SM = slice(nref, nref + m_in)
    SP = slice(nref + m_in, nref + m_in + m_out)

    c = np.zeros(num_vars)
    c[SM] = 1.0
    c[SP] = 1.0

    A_eq1 = np.hstack([Xr.T, np.eye(m_in), np.zeros((m_in, m_out))])
    b_eq1 = x0

    A_eq2 = np.hstack([Yr.T, np.zeros((m_out, m_in)), -np.eye(m_out)])
    b_eq2 = y0

    A_eq = np.vstack([A_eq1, A_eq2])
    b_eq = np.concatenate([b_eq1, b_eq2])

    if vrs:
        A_eq = np.vstack([A_eq, np.hstack([np.ones(nref), np.zeros(m_in + m_out)])])
        b_eq = np.concatenate([b_eq, np.array([1.0])])

    bounds = [(0, None)] * num_vars

    res = linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method="highs")
    if not res.success:
        raise RuntimeError(f"LP (additive) did not converge: {res.message}")

    lam_ref = res.x[L]
    s_minus = res.x[SM]
    s_plus = res.x[SP]
    return lam_ref, s_minus, s_plus


# ============================================================================
# SBM Input-Oriented (Tone, 2001)
# ⚠️ Mantido no arquivo, mas DESATIVADO em v0.1.0 (não exportar)
# ============================================================================
def _solve_sbm_input_oriented(
    X: np.ndarray,
    Y: np.ndarray,
    x0: np.ndarray,
    y0: np.ndarray,
    vrs: bool,
    exclude_idx: int | None = None,
):
    """
    SBM input-oriented (Tone, 2001).
    Mantido aqui para versões futuras.
    """
    pass


# ============================================================================
# Super-Efficiency (Andersen & Petersen, 1993)
# ============================================================================
def _solve_super_input(
    X: np.ndarray,
    Y: np.ndarray,
    x0: np.ndarray,
    y0: np.ndarray,
    *,
    vrs: bool,
    exclude_idx: int,
):
    """
    Super-efficiency input-oriented (Andersen–Petersen 1993).
    Excludes DMU k.
    """
    n, m_in = X.shape
    m_out = Y.shape[1]

    ref_idx = [i for i in range(n) if i != exclude_idx]
    nref = len(ref_idx)

    num_vars = nref + 1
    L = slice(0, nref)
    theta_idx = nref

    c = np.zeros(num_vars)
    c[theta_idx] = 1.0

    A_ub = []
    b_ub = []

    for j in range(m_in):
        row = np.zeros(num_vars)
        row[L] = X[ref_idx, j]
        row[theta_idx] = -x0[j]
        A_ub.append(row)
        b_ub.append(0.0)

    for t in range(m_out):
        row = np.zeros(num_vars)
        row[L] = -Y[ref_idx, t]
        A_ub.append(row)
        b_ub.append(-y0[t])

    A_eq, b_eq = None, None
    if vrs:
        row = np.zeros(num_vars)
        row[L] = 1.0
        A_eq = np.array([row])
        b_eq = np.array([1.0])

    bounds = [(0, None)] * nref + [(0, None)]

    res = linprog(
        c,
        A_ub=np.array(A_ub),
        b_ub=np.array(b_ub),
        A_eq=A_eq,
        b_eq=b_eq,
        bounds=bounds,
        method="highs",
    )
    if not res.success:
        raise RuntimeError(f"LP (Super-input) did not converge: {res.message}")

    theta = res.x[theta_idx]
    lam = res.x[L]
    return float(theta), lam


def _solve_super_output(
    X: np.ndarray,
    Y: np.ndarray,
    x0: np.ndarray,
    y0: np.ndarray,
    *,
    vrs: bool,
    exclude_idx: int,
):
    """
    Super-efficiency output-oriented (Andersen–Petersen 1993).
    Excludes DMU k.
    """
    n, m_in = X.shape
    m_out = Y.shape[1]

    ref_idx = [i for i in range(n) if i != exclude_idx]
    nref = len(ref_idx)

    num_vars = nref + 1
    L = slice(0, nref)
    phi_idx = nref

    c = np.zeros(num_vars)
    c[phi_idx] = -1.0

    A_ub = []
    b_ub = []

    for j in range(m_in):
        row = np.zeros(num_vars)
        row[L] = X[ref_idx, j]
        A_ub.append(row)
        b_ub.append(x0[j])

    for t in range(m_out):
        row = np.zeros(num_vars)
        row[L] = -Y[ref_idx, t]
        row[phi_idx] = y0[t]
        A_ub.append(row)
        b_ub.append(0.0)

    # forma estável: VRS usa Σλ ≤ 1
    if vrs:
        row = np.zeros(num_vars)
        row[L] = 1.0
        A_ub.append(row)
        b_ub.append(1.0)

    bounds = [(0, None)] * nref + [(0, None)]

    res = linprog(c, A_ub=np.array(A_ub), b_ub=np.array(b_ub), bounds=bounds, method="highs")
    if not res.success:
        raise RuntimeError(f"LP (Super-output) did not converge: {res.message}")

    phi = res.x[phi_idx]
    lam = res.x[L]
    return float(phi), lam
