# src/opendea/_prep.py
from __future__ import annotations

import numpy as np
import pandas as pd


def _prep(
    df: pd.DataFrame,
    inputs: list[str],
    outputs: list[str],
) -> tuple[np.ndarray, np.ndarray, pd.Index, list[str], list[str]]:
    """
    Valida colunas e retorna:
      X (n x m_in), Y (n x m_out), dmus (Index), in_names, out_names
    Converte para float para uso no linprog.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")
    if not inputs or not outputs:
        raise ValueError("inputs and outputs must be non-empty lists of column names")

    missing = [c for c in inputs + outputs if c not in df.columns]
    if missing:
        raise KeyError(f"Missing columns in df: {missing}")

    # Índice dos DMUs
    dmus = df.index
    if dmus.duplicated().any():
        # Opcional: force unique names
        dmus = pd.Index([f"DMU_{i+1}" for i in range(len(df))], name=df.index.name)

    X = df[inputs].to_numpy(dtype=float)
    Y = df[outputs].to_numpy(dtype=float)

    if np.isnan(X).any() or np.isnan(Y).any():
        raise ValueError("NaNs found in inputs/outputs; please clean your data")

    return X, Y, dmus, list(inputs), list(outputs)
