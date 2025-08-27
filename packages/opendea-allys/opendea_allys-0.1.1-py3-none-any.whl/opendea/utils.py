# src/opendea/utils.py
from __future__ import annotations

import re

import numpy as np
import pandas as pd


# -----------------------------------------------------------------------------
# 1) Padronização de saída do PRIMAL (multiplicador)
#    Converte colunas do tipo 'Peso_Output_*' / 'Peso_Input_*' para u_*/v_*
#    e 'Eficiência' -> 'phi', mantendo compatível com OpenDEA.
# -----------------------------------------------------------------------------
def standardize_primal_output(df: pd.DataFrame) -> pd.DataFrame:
    """
    Converte um DataFrame de resultados do CCR PRIMAL (output-oriented)
    para a nomenclatura padrão do OpenDEA.

    Mapeamentos:
      - 'Eficiência'                    -> 'phi'
      - 'Peso_Output_<nome>'            -> 'u_<nome>'
      - 'Peso_Input_<nome>'             -> 'v_<nome>'

    Outras colunas (ex.: 'DMU', 'Status') são preservadas.
    """
    df2 = df.copy()
    rename_map: dict[str, str] = {}

    for c in df2.columns:
        if c == "Eficiência":
            rename_map[c] = "phi"
        elif c.startswith("Peso_Output_"):
            var = c[len("Peso_Output_") :]
            var = re.sub(r"\s+", "_", var)
            rename_map[c] = f"u_{var}"
        elif c.startswith("Peso_Input_"):
            var = c[len("Peso_Input_") :]
            var = re.sub(r"\s+", "_", var)
            rename_map[c] = f"v_{var}"

    df2 = df2.rename(columns=rename_map)

    # Ordenação amigável
    lead = [c for c in ["DMU", "phi"] if c in df2.columns]
    u_cols = [c for c in df2.columns if c.startswith("u_")]
    v_cols = [c for c in df2.columns if c.startswith("v_")]
    rest = [c for c in df2.columns if c not in set(lead + u_cols + v_cols)]
    df2 = df2[lead + u_cols + v_cols + rest]
    return df2


# -----------------------------------------------------------------------------
# 2) Projeções canônicas (metas)
#    x* = θ·x0 − s− ; y* = y0 + s+          (input-oriented)
#    x* = x0 − s− ;  y* = φ·y0 + s+         (output-oriented)
# -----------------------------------------------------------------------------
def projections(
    df: pd.DataFrame,
    inputs: list[str],
    outputs: list[str],
    result: pd.DataFrame,
    orientation: str = "input",
) -> pd.DataFrame:
    """
    Retorna projeções canônicas para cada DMU, usando θ/φ e folgas.

    - Input-oriented:
        x* = θ·x0 − s−
        y* = y0 + s+
    - Output-oriented:
        x* = x0 − s−
        y* = φ·y0 + s+

    Parâmetros
    ----------
    df : DataFrame original (DMUs nas linhas)
    inputs, outputs : colunas
    result : DataFrame retornado por funções DEA (com colunas de folgas e θ ou φ)
    orientation : "input" ou "output"

    Retorno
    -------
    DataFrame com colunas xproj_<input> e yproj_<output>
    """
    # Alinha ordem/índice se necessário
    if not df.index.equals(result.index):
        result = result.reindex(df.index)

    X = df[inputs].to_numpy(float)
    Y = df[outputs].to_numpy(float)

    sminus_cols = [f"s_minus_{c}" for c in inputs]
    splus_cols = [f"s_plus_{c}" for c in outputs]

    # Se alguma coluna de slack não existir, assume zero (evita quebra em exemplos mínimos)
    Sminus = (
        result[sminus_cols].to_numpy(float)
        if all(c in result.columns for c in sminus_cols)
        else np.zeros_like(X)
    )
    Splus = (
        result[splus_cols].to_numpy(float)
        if all(c in result.columns for c in splus_cols)
        else np.zeros_like(Y)
    )

    if orientation.lower().startswith("out"):
        if "phi" not in result.columns:
            raise ValueError("Resultado não contém coluna 'phi' (modelo orientado a produto).")
        phi = result["phi"].to_numpy(float).reshape(-1, 1)
        x_star = X - Sminus
        y_star = phi * Y + Splus
    else:
        if "efficiency" not in result.columns:
            raise ValueError(
                "Resultado não contém coluna 'efficiency' (modelo orientado a insumo)."
            )
        theta = result["efficiency"].to_numpy(float).reshape(-1, 1)
        x_star = theta * X - Sminus
        y_star = Y + Splus

    proj = pd.DataFrame(
        np.hstack([x_star, y_star]),
        index=df.index,
        columns=[f"xproj_{c}" for c in inputs] + [f"yproj_{c}" for c in outputs],
    )
    return proj


# -----------------------------------------------------------------------------
# 3) Peers a partir das lambdas
# -----------------------------------------------------------------------------
def peers_from_lambdas(result, tol: float = 1e-6):
    """
    Retorna os peers (referências) de cada DMU a partir das colunas lambda_*.

    Parameters
    ----------
    result : pd.DataFrame
        Resultado de um modelo DEA com colunas lambda_*.
    tol : float
        Tolerância numérica para considerar valores > 0.

    Returns
    -------
    dict
        Dicionário {DMU: [lista de peers]}.
    """
    lam_cols = [c for c in result.columns if c.startswith("lambda_")]
    peers = {}
    for dmu, row in result[lam_cols].iterrows():
        nz = [c.replace("lambda_", "") for c, v in row.items() if abs(v) > tol]
        peers[dmu] = nz
    return peers
