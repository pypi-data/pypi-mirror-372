from __future__ import annotations

import pandas as pd

from .models import dea_sbm_input  # usa a versão revisada que aceita leave_one_out
from .types import DEAResult


def sbm_input(
    df: pd.DataFrame,
    inputs: list[str],
    outputs: list[str],
    *,
    vrs: bool = True,
    leave_one_out: bool = True,
) -> DEAResult:
    res = dea_sbm_input(df, inputs, outputs, vrs=vrs, leave_one_out=leave_one_out)

    eff = res["rho"].rename("efficiency")
    lambdas = res[[c for c in res.columns if c.startswith("lambda_")]]
    s_minus = res[[c for c in res.columns if c.startswith("s_minus_")]]
    s_plus = res[[c for c in res.columns if c.startswith("s_plus_")]]

    return DEAResult(
        efficiency=eff,
        lambdas=lambdas,
        slacks_input=s_minus,
        slacks_output=s_plus,
        meta={"model": "SBM-input", "vrs": vrs, "leave_one_out": leave_one_out},
    )
