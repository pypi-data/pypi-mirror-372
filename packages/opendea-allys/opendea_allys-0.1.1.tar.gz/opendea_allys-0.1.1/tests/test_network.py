import pandas as pd

from opendea import dea_network_two_stage

TOL = 1e-6


def test_two_stage_basic_vrs():
    # 3 DMUs, 1 input, 1 intermed, 1 output
    df = pd.DataFrame(
        {
            "DMU": ["A", "B", "C"],
            "x": [4, 2, 3],
            "z": [3, 2, 2.5],
            "y": [5, 4, 6],
        }
    ).set_index("DMU")

    res = dea_network_two_stage(
        X=df, Z=df, Y=df, inputs=["x"], intermeds=["z"], outputs=["y"], vrs=True
    )

    assert all((res["efficiency"] > 0 - TOL) & (res["efficiency"] <= 1 + TOL))
    # DMU B costuma ser eficiente nesse toy
    assert abs(res.loc["B", "efficiency"] - 1.0) <= 1e-4
