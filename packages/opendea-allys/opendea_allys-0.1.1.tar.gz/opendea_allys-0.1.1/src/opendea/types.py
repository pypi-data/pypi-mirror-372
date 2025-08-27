from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass
class DEAResult:
    """Container for DEA results (model-agnostic)."""

    efficiency: pd.Series | None = None  # (n,) θ or 1/φ or ρ
    lambdas: pd.DataFrame | None = None  # (n, n) λ_{k,j}
    slacks_input: pd.DataFrame | None = None  # (n, m) s^- (inputs)
    slacks_output: pd.DataFrame | None = None  # (n, s) s^+ (outputs)
    targets_input: pd.DataFrame | None = None  # (n, m) projected inputs
    targets_output: pd.DataFrame | None = None  # (n, s) projected outputs
    meta: dict[str, object] = None  # model metadata

    def to_dataframe(self) -> pd.DataFrame:
        """Return a wide table merging key fields (good for CSV/preview)."""
        frames: list[pd.DataFrame] = []
        if self.efficiency is not None:
            frames.append(self.efficiency.rename("efficiency").to_frame())
        if self.lambdas is not None:
            frames.append(self.lambdas.add_prefix("lambda_"))
        if self.slacks_input is not None:
            frames.append(self.slacks_input.add_prefix("s_minus_"))
        if self.slacks_output is not None:
            frames.append(self.slacks_output.add_prefix("s_plus_"))
        if not frames:
            return pd.DataFrame()
        out = pd.concat(frames, axis=1)
        return out

    def copy(self) -> DEAResult:
        return DEAResult(
            efficiency=None if self.efficiency is None else self.efficiency.copy(),
            lambdas=None if self.lambdas is None else self.lambdas.copy(),
            slacks_input=None if self.slacks_input is None else self.slacks_input.copy(),
            slacks_output=None if self.slacks_output is None else self.slacks_output.copy(),
            targets_input=None if self.targets_input is None else self.targets_input.copy(),
            targets_output=None if self.targets_output is None else self.targets_output.copy(),
            meta=dict(self.meta or {}),
        )
