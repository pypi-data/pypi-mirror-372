import pandas as pd

from opendea import dea_dynamic_carryover

TOL = 1e-6


def test_dynamic_2periods_vrs():
    # 3 DMUs, T=2, 1 input, 1 output, 1 carryover
    d0 = pd.DataFrame(
        {
            "DMU": ["A", "B", "C"],
            "x": [4, 2, 3],
            "y": [5, 4, 6],
            "g": [2, 1, 1.5],
        }
    ).set_index("DMU")

    d1 = pd.DataFrame(
        {
            "DMU": ["A", "B", "C"],
            "x": [3, 2, 3],
            "y": [6, 4, 6],
            "g": [2.2, 1.2, 1.7],
        }
    ).set_index("DMU")

    X_ts = {0: d0, 1: d1}
    Y_ts = {0: d0, 1: d1}
    G_ts = {0: d0, 1: d1}

    res = dea_dynamic_carryover(
        X_ts, Y_ts, G_ts, inputs=["x"], outputs=["y"], carryovers=["g"], vrs=True
    )

    # eficiências entre 0 e 1; B tipicamente eficiente nesse toy
    assert all((res["efficiency"] > -TOL) & (res["efficiency"] <= 1 + TOL))
    assert abs(res.loc["B", "efficiency"] - 1.0) <= 1e-4
