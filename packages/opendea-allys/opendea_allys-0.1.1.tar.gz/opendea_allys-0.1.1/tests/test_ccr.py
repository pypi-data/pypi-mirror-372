import pandas as pd

from opendea import dea_bcc_input


def test_bcc_input_orientation():
    df = pd.DataFrame({"DMU": ["A", "B", "C"], "x1": [4, 2, 3], "y1": [5, 4, 6]}).set_index("DMU")

    res = dea_bcc_input(df, ["x1"], ["y1"])

    # Checa se resultado retorna todas as DMUs
    assert all(dmu in res.index for dmu in ["A", "B", "C"])

    # θ ∈ (0, 1]
    assert (res["efficiency"] <= 1 + 1e-9).all()
    assert (res["efficiency"] > 0 - 1e-12).all()
