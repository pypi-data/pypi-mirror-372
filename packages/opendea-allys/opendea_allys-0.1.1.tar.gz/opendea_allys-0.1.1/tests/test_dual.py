import numpy as np
import pandas as pd

from opendea import (
    dea_bcc_input,
    dea_bcc_input_dual,
    dea_bcc_output,
    dea_bcc_output_dual,
    dea_ccr_input,
    dea_ccr_input_dual,
    dea_ccr_output,
    dea_ccr_output_dual,
)

TOL = 1e-6


def _toy_df():
    return pd.DataFrame(
        {
            "x1": [4, 2, 3, 5],
            "x2": [2, 1, 1, 3],
            "y1": [1, 1, 1, 2],
        },
        index=["A", "B", "C", "D"],
    )


def test_ccr_input_primal_dual_equivalence():
    df = _toy_df()
    prim = dea_ccr_input(df, ["x1", "x2"], ["y1"])
    dual = dea_ccr_input_dual(df, ["x1", "x2"], ["y1"])
    np.testing.assert_allclose(prim["efficiency"], dual["efficiency"], atol=TOL)


def test_bcc_input_primal_dual_equivalence():
    df = _toy_df()
    prim = dea_bcc_input(df, ["x1", "x2"], ["y1"])
    dual = dea_bcc_input_dual(df, ["x1", "x2"], ["y1"])
    np.testing.assert_allclose(prim["efficiency"], dual["efficiency"], atol=TOL)


def test_ccr_output_primal_dual_equivalence():
    df = _toy_df()
    prim = dea_ccr_output(df, ["x1", "x2"], ["y1"])
    dual = dea_ccr_output_dual(df, ["x1", "x2"], ["y1"])
    np.testing.assert_allclose(prim["phi"], dual["phi"], atol=TOL)


def test_bcc_output_primal_dual_equivalence():
    df = _toy_df()
    prim = dea_bcc_output(df, ["x1", "x2"], ["y1"])
    dual = dea_bcc_output_dual(df, ["x1", "x2"], ["y1"])
    np.testing.assert_allclose(prim["phi"], dual["phi"], atol=TOL)
