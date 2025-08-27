# opendea

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/)

**Data Envelopment Analysis (DEA)** in Python — simple, robust, and extensible, built on **SciPy**.  
Includes **CCR (CRS)** and **BCC (VRS)** models, **super-efficiency**, **additive model**,  
as well as modules for **NDEA (two-stage networks)** and **Dynamic DEA with carry-overs**.  

⚠️ **Note**: The **SBM (Slack-Based Measure, Tone 2001)** is **included in the code but inactive** in version `0.1.0`.  
It will be available in a future release (`0.2.0`).

---

## 📦 Installation

### User (pip)
```bash
pip install opendea          # core only
pip install opendea[viz]     # core + plotting (matplotlib, seaborn)
pip install opendea[full]    # everything: plotting + notebooks + dev tools

```

### Development
```bash
git clone https://github.com/yourusername/opendea.git
cd opendea
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev,viz]"

```

---

## ⚡ Quickstart

```python
import pandas as pd
from opendea import dea_ccr_input, dea_bcc_output
from opendea.plotting import plot_efficiency

df = pd.DataFrame({
    "x1": [4, 2, 3, 5],
    "x2": [2, 1, 1, 3],
    "y1": [1, 1, 1, 2],
}, index=["A","B","C","D"])

# CCR (CRS) input-oriented
res_ccr_in = dea_ccr_input(df, inputs=["x1","x2"], outputs=["y1"])
print(res_ccr_in[["efficiency"]])

# BCC (VRS) output-oriented
res_bcc_out = dea_bcc_output(df, inputs=["x1","x2"], outputs=["y1"])
print(res_bcc_out[["phi"]])

# Plot efficiencies
plot_efficiency(res_ccr_in, title="CCR Efficiency")
```

---

## 🧰 Main API

### Classical models
- `dea_ccr_input(df, inputs, outputs)`
- `dea_bcc_input(df, inputs, outputs)`
- `dea_ccr_output(df, inputs, outputs)`
- `dea_bcc_output(df, inputs, outputs)`

### Extensions
- `super_eff_ccr_input(df, inputs, outputs)`
- `super_eff_ccr_output(df, inputs, outputs)`
- `dea_additive_ccr(df, inputs, outputs)`
- `dea_additive_bcc(df, inputs, outputs)`
- ~~`dea_sbm_input(df, inputs, outputs, vrs=True)`~~ 🚫 *inactive in v0.1.0*

### Advanced
- `ndea_two_stage_input(df, inputs_stage1, link_m, outputs_stage2, vrs=True)`
- `dynamic_dea_input(panels, inputs, outputs, carryovers, vrs=True)`

### Utilities
- `projections(df, inputs, outputs, result, orientation="input"|"output")`
- `peers_from_lambdas(result)`

---

## 🧠 Conventions (summary)

- **Input-oriented**: minimize θ  
  Projections: `x* = θ·x0 − s−` ; `y* = y0 + s+`
- **Output-oriented**: maximize φ  
  Projections: `x* = x0 − s−` ; `y* = φ·y0 + s+`
- **SBM (ρ)**: 0–1, average proportional reduction in inputs.
- **Results** return a `DataFrame` (or `DEAResult` in typed API) with columns:
  - `efficiency` (θ) or `phi` (φ) or `rho` (SBM)  
  - `lambda_*` (intensities)  
  - `s_minus_*`, `s_plus_*` (slacks)

---

## 🔬 Advanced examples

### NDEA (two-stage in series)
```python
from opendea import ndea_two_stage_input
df_net = pd.DataFrame({
  "x1":[4,2,3,5], "x2":[2,1,1,3],
  "m1":[3,2,2,4],              # link Stage1->Stage2
  "y1":[1,1,1,2],
}, index=list("ABCD"))
res_net = ndea_two_stage_input(df_net, ["x1","x2"], ["m1"], ["y1"], vrs=True)
print(res_net[["efficiency"]])
```

### Dynamic DEA with carry-overs
```python
from opendea import dynamic_dea_input
panels = {
  1: pd.DataFrame({"x1":[5,3,4], "y1":[1,1,2], "k1":[2,1,1]}, index=["A","B","C"]),
  2: pd.DataFrame({"x1":[4,3,3], "y1":[2,1,2], "k1":[2,1,1]}, index=["A","B","C"]),
}
dyn = dynamic_dea_input(panels, inputs=["x1"], outputs=["y1"], carryovers=["k1"], vrs=True)
for t, df_t in dyn.items():
    print(t, df_t[["efficiency"]])
```

---

## 🗺️ Roadmap

- Cross-efficiency (benevolent/aggressive)  
- Window analysis (sliding windows)  
- Malmquist TFP  
- Multiplier (dual) models and Assurance Region I/II  
- Extended NDEA / Dynamic (network-SBM, dynamic-SBM)  
- Directional distance functions (DDF), robust/stochastic DEA, sensitivity analysis

---

## 🧪 Tests

```bash
pytest -q
```

---

## 🤝 Contributing

- PRs are welcome!  
- Run `ruff` + `black` before submitting.  
- Always add tests.

---

## 📄 License

MIT — see `LICENSE`.
