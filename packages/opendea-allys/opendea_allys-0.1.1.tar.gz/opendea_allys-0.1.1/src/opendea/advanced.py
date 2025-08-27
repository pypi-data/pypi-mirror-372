# ==========================================================
# advanced.py — NDEA (two-stage) e Dynamic DEA (carryover)
# ==========================================================
from typing import Optional

import numpy as np
import pandas as pd
from scipy.optimize import linprog

__all__ = [
    "dea_network_two_stage",
    "dea_dynamic_carryover",
]


# -------------------------
# Helpers
# -------------------------
def _to_np(df_or_np) -> np.ndarray:
    if isinstance(df_or_np, pd.DataFrame):
        return df_or_np.to_numpy(dtype=float, copy=True)
    if isinstance(df_or_np, np.ndarray):
        return df_or_np.astype(float, copy=False)
    raise TypeError("Esperado pandas.DataFrame ou numpy.ndarray")


def _clean(arr: np.ndarray, tol: float = 1e-9) -> np.ndarray:
    a = arr.copy()
    a[np.abs(a) < tol] = 0.0
    return np.clip(a, 0.0, None)


# ==========================================================
# NDEA two-stage (serial), input-oriented
# ----------------------------------------------------------
# Estágio 1: X -> Z (λ1)
# Estágio 2: Z -> Y (λ2)
# Link consistente: Z λ1 = z_link = Z λ2
# VRS opcional: sum λ1 = 1, sum λ2 = 1
# Objetivo: min θ
# ==========================================================
def dea_network_two_stage(
    X: pd.DataFrame,
    Z: pd.DataFrame,
    Y: pd.DataFrame,
    inputs: list[str],
    intermeds: list[str],
    outputs: list[str],
    vrs: bool = True,
    index: Optional[pd.Index] = None,
) -> pd.DataFrame:
    """
    NDEA two-stage (serial), input-oriented (θ), VRS opcional.

    Variáveis:
      λ1 ∈ R^n_+ (estágio 1), λ2 ∈ R^n_+, θ ≥ 0, z_link ∈ R^{|Z|}

    Restrições:
      (1) X λ1 ≤ θ x0      (inputs)
      (2) Y λ2 ≥ y0        (outputs)  ->  -Y λ2 ≤ -y0
      (3) Z λ1 = z_link
      (4) Z λ2 = z_link
      (5) (VRS) sum λ1 = 1, sum λ2 = 1

    Retorna:
      DataFrame com 'efficiency' (=θ) e lambdas por estágio (lambda1_*, lambda2_*).
    """
    X = X[inputs].copy()
    Z = Z[intermeds].copy()
    Y = Y[outputs].copy()

    if index is None:
        index = X.index
    # Garante mesma ordem de DMUs
    X = X.loc[index]
    Z = Z.loc[index]
    Y = Y.loc[index]

    Xn = _to_np(X)
    Zn = _to_np(Z)
    Yn = _to_np(Y)

    dmus = index.astype(str)
    n, m_in = Xn.shape
    m_mid = Zn.shape[1]
    m_out = Yn.shape[1]

    rows: list[tuple[str, dict]] = []

    for k in range(n):
        x0 = Xn[k]  # (m_in,)
        y0 = Yn[k]  # (m_out,)

        # Vars: [λ1 (n), λ2 (n), θ (1), z_link (m_mid)]
        num_vars = n + n + 1 + m_mid
        lam1_s = slice(0, n)
        lam2_s = slice(n, n + n)
        theta_i = n + n
        z_s = slice(n + n + 1, n + n + 1 + m_mid)

        c = np.zeros(num_vars)
        c[theta_i] = 1.0  # min θ

        A_ub = []
        b_ub = []
        A_eq = []
        b_eq = []

        # (1) X λ1 - θ x0 ≤ 0
        A1 = np.zeros((m_in, num_vars))
        A1[:, lam1_s] = Xn.T
        A1[:, theta_i] = -x0
        A_ub.append(A1)
        b_ub.append(np.zeros(m_in))

        # (2) -Y λ2 ≤ -y0
        A2 = np.zeros((m_out, num_vars))
        A2[:, lam2_s] = -Yn.T
        A_ub.append(A2)
        b_ub.append(-y0)

        # (3) Z λ1 - z_link = 0
        E1 = np.zeros((m_mid, num_vars))
        E1[:, lam1_s] = Zn.T
        E1[:, z_s] = -np.eye(m_mid)
        A_eq.append(E1)
        b_eq.append(np.zeros(m_mid))

        # (4) Z λ2 - z_link = 0
        E2 = np.zeros((m_mid, num_vars))
        E2[:, lam2_s] = Zn.T
        E2[:, z_s] = -np.eye(m_mid)
        A_eq.append(E2)
        b_eq.append(np.zeros(m_mid))

        if vrs:
            # sum λ1 = 1
            E3 = np.zeros((1, num_vars))
            E3[0, lam1_s] = 1.0
            A_eq.append(E3)
            b_eq.append(np.array([1.0]))
            # sum λ2 = 1
            E4 = np.zeros((1, num_vars))
            E4[0, lam2_s] = 1.0
            A_eq.append(E4)
            b_eq.append(np.array([1.0]))

        A_ub = np.vstack(A_ub) if len(A_ub) else None
        b_ub = np.concatenate(b_ub) if len(b_ub) else None
        A_eq = np.vstack(A_eq) if len(A_eq) else None
        b_eq = np.concatenate(b_eq) if len(b_eq) else None

        bounds = [(0, None)] * num_vars

        res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method="highs")
        if not res.success:
            raise RuntimeError(f"NDEA two-stage falhou para {dmus[k]}: {res.message}")

        lam1 = _clean(res.x[lam1_s])
        lam2 = _clean(res.x[lam2_s])
        theta = float(res.x[theta_i])

        row = {"efficiency": theta}
        for j in range(n):
            row[f"lambda1_{dmus[j]}"] = float(lam1[j])
        for j in range(n):
            row[f"lambda2_{dmus[j]}"] = float(lam2[j])

        rows.append((dmus[k], row))

    return pd.DataFrame.from_dict(dict(rows), orient="index")


# ==========================================================
# Dynamic DEA (input-oriented) com good carryover
# ----------------------------------------------------------
# θ_k comum a todos os períodos para cada DMU k.
# VRS: sum_i λ_{t,i} = 1 para cada período t.
# Good carryover:
#     G_t λ_t ≤ G_{t+1} λ_{t+1}
# Objetivo: min θ
# ==========================================================
def dea_dynamic_carryover(
    X_ts: dict[int, pd.DataFrame],
    Y_ts: dict[int, pd.DataFrame],
    G_ts: dict[int, pd.DataFrame],
    inputs: list[str],
    outputs: list[str],
    carryovers: list[str],
    vrs: bool = True,
    index: Optional[pd.Index] = None,
) -> pd.DataFrame:
    """
    DEA dinâmico (input-oriented) com good carryover:
      Para cada DMU avaliada k:
        min θ
        s.t. X_t λ_t ≤ θ x_{t,k},   -Y_t λ_t ≤ -y_{t,k}
             (VRS) 1'λ_t = 1,  ∀t
             G_t λ_t ≤ G_{t+1} λ_{t+1},  ∀t=1..T-1
        λ_t ≥ 0, θ ≥ 0

    Retorno:
      DataFrame indexado por DMU contendo 'efficiency' (= θ_k).
      (θ_k é único por DMU e comum a todos os períodos.)
    """
    Ts = sorted(X_ts.keys())
    if (set(Ts) != set(Y_ts.keys())) or (set(Ts) != set(G_ts.keys())):
        raise ValueError("Períodos inconsistentes entre X_ts, Y_ts e G_ts.")

    # Reindexa e seleciona colunas
    if index is None:
        index = X_ts[Ts[0]].index
    dmus = index.astype(str)

    Xn: dict[int, np.ndarray] = {}
    Yn: dict[int, np.ndarray] = {}
    Gn: dict[int, np.ndarray] = {}
    for t in Ts:
        Xt = X_ts[t].loc[index, inputs].copy()
        Yt = Y_ts[t].loc[index, outputs].copy()
        Gt = G_ts[t].loc[index, carryovers].copy()
        Xn[t] = _to_np(Xt)
        Yn[t] = _to_np(Yt)
        Gn[t] = _to_np(Gt)

    n, m_in = Xn[Ts[0]].shape
    m_out = Yn[Ts[0]].shape[1]
    m_car = Gn[Ts[0]].shape[1]
    T = len(Ts)

    rows: list[tuple[str, dict]] = []

    for k in range(n):
        num_vars = n * T + 1
        theta_i = n * T

        c = np.zeros(num_vars)
        c[theta_i] = 1.0

        A_ub_list = []
        b_ub_list = []
        A_eq_list = []
        b_eq_list = []

        # Inputs e outputs por período
        for ti, t in enumerate(Ts):
            x0 = Xn[t][k]  # (m_in,)
            y0 = Yn[t][k]  # (m_out,)

            # X_t λ_t - θ x0 ≤ 0
            Ai = np.zeros((m_in, num_vars))
            Ai[:, ti * n : (ti + 1) * n] = Xn[t].T
            Ai[:, theta_i] = -x0
            A_ub_list.append(Ai)
            b_ub_list.append(np.zeros(m_in))

            # -Y_t λ_t ≤ -y0
            Ao = np.zeros((m_out, num_vars))
            Ao[:, ti * n : (ti + 1) * n] = -Yn[t].T
            A_ub_list.append(Ao)
            b_ub_list.append(-y0)

            if vrs:
                Ev = np.zeros((1, num_vars))
                Ev[0, ti * n : (ti + 1) * n] = 1.0
                A_eq_list.append(Ev)
                b_eq_list.append(np.array([1.0]))

        # Good carryover: G_t λ_t - G_{t+1} λ_{t+1} ≤ 0
        for ti in range(T - 1):
            t = Ts[ti]
            t1 = Ts[ti + 1]
            Ag = np.zeros((m_car, num_vars))
            Ag[:, ti * n : (ti + 1) * n] = Gn[t].T
            Ag[:, (ti + 1) * n : (ti + 2) * n] = -Gn[t1].T
            A_ub_list.append(Ag)
            b_ub_list.append(np.zeros(m_car))

        A_ub = np.vstack(A_ub_list) if len(A_ub_list) else None
        b_ub = np.concatenate(b_ub_list) if len(b_ub_list) else None
        A_eq = np.vstack(A_eq_list) if len(A_eq_list) else None
        b_eq = np.concatenate(b_eq_list) if len(b_eq_list) else None
        bounds = [(0, None)] * num_vars  # λ, θ ≥ 0

        res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method="highs")
        if not res.success:
            raise RuntimeError(f"DEA dinâmico falhou para {dmus[k]}: {res.message}")

        theta = float(res.x[theta_i])
        rows.append((dmus[k], {"efficiency": theta}))

    # retorna DataFrame por DMU (coluna 'efficiency')
    return pd.DataFrame.from_dict(dict(rows), orient="index")
