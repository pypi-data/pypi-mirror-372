import pandas as pd

from opendea import super_eff_bcc_output, super_eff_ccr_input


def _toy():
    return pd.DataFrame(
        {
            "x1": [10, 12, 15, 20, 18, 25, 40, 35],
            "x2": [5, 6, 6, 7, 8, 12, 18, 16],
            "y1": [80, 75, 60, 55, 50, 45, 38, 40],
            "y2": [50, 48, 40, 38, 36, 30, 22, 25],
        },
        index=list("ABCDEFGH"),
    )


def test_super_eff_bounds():
    df = _toy()
    res_in = super_eff_ccr_input(df, ["x1", "x2"], ["y1", "y2"])
    res_out = super_eff_bcc_output(df, ["x1", "x2"], ["y1", "y2"])
    assert (res_in["super_eff"].to_numpy(float) >= 1 - 1e-9).all()
    assert (res_out["super_eff"].to_numpy(float) >= 1 - 1e-9).all()
