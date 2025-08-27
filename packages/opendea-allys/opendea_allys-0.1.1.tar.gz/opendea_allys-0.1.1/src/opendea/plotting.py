from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from .plot_theme import apply_theme

__all__ = [
    "plot_efficiency",
    "plot_efficiency_hist",
    "plot_lambdas_heatmap",
    "compute_frontier_1in1out",
    "plot_frontier_1in_1out",
    "plot_quadrants_like_cnj",
    "plot_sbm_efficiency_bars",
    "plot_slacks_heatmap",
    "plot_corr_heatmap",
    "plot_corr_triangle",
]


# --------------------------
# Helpers
# --------------------------
def _require_cols(df: pd.DataFrame, cols: list[str]):
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise KeyError(f"Missing columns in results DataFrame: {missing}")


apply_theme()


# --------------------------
# Basic DEA plots
# --------------------------
def plot_efficiency(
    res: pd.DataFrame, *, title: str = "Efficiency (0–1)", ax=None, sort: bool = True
):
    """
    Plot efficiency bars.

    Parameters
    ----------
    res : DataFrame
        Must contain column 'efficiency' (0–1).
    title : str
    ax : matplotlib.axes.Axes | None
    sort : bool
        Sort descending by efficiency.

    Returns
    -------
    matplotlib.axes.Axes
    """
    _require_cols(res, ["efficiency"])
    data = res["efficiency"].sort_values(ascending=False) if sort else res["efficiency"]
    if ax is None:
        _, ax = plt.subplots(figsize=(7, 4))
    data.plot(kind="bar", rot=0, ax=ax)
    ax.set_ylim(0, 1.05)
    ax.axhline(1.0, linestyle="--", color="tab:red")
    ax.set_ylabel("Efficiency")
    ax.set_title(title)
    return ax


def plot_efficiency_hist(
    res: pd.DataFrame, *, bins: int = 10, title: str = "Efficiency distribution", ax=None
):
    """Histogram of efficiency scores."""
    _require_cols(res, ["efficiency"])
    if ax is None:
        _, ax = plt.subplots(figsize=(6, 4))
    res["efficiency"].plot(kind="hist", bins=bins, edgecolor="black", ax=ax)
    ax.axvline(1.0, linestyle="--", color="tab:red")
    ax.set_xlabel("Efficiency (0–1)")
    ax.set_title(title)
    return ax


def plot_lambdas_heatmap(
    res: pd.DataFrame, *, title: str = "Peer weights (lambdas)", ax=None, cmap: str = "Blues"
):
    """Heatmap for λ (peer weights)."""
    lam_cols = [c for c in res.columns if c.startswith("lambda_")]
    if not lam_cols:
        raise KeyError("No lambda_ columns found in results DataFrame.")
    M = res[lam_cols].to_numpy(dtype=float)
    xt = [c.replace("lambda_", "") for c in lam_cols]
    yt = list(res.index.astype(str))
    if ax is None:
        _, ax = plt.subplots(figsize=(max(6, len(xt) * 0.6), max(4, len(yt) * 0.4)))
    im = ax.imshow(M, aspect="auto", cmap=cmap)
    ax.set_xticks(range(len(xt)))
    ax.set_xticklabels(xt, rotation=90)
    ax.set_yticks(range(len(yt)))
    ax.set_yticklabels(yt)
    ax.set_title(title)
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label("λ weight", rotation=90)
    return ax


def compute_frontier_1in1out(df: pd.DataFrame, input_col: str, output_col: str) -> pd.DataFrame:
    """Compute efficient upper envelope for 1 input / 1 output."""
    pts = df[[input_col, output_col]].dropna().sort_values(input_col)
    frontier = [pts.iloc[0]]
    for _, row in pts.iloc[1:].iterrows():
        if row[output_col] >= frontier[-1][output_col]:
            frontier.append(row)
    return pd.DataFrame(frontier)


def plot_frontier_1in_1out(
    df: pd.DataFrame,
    input_col: str,
    output_col: str,
    res_input_oriented: pd.DataFrame,
    *,
    title: str = "DEA CCR Frontier (1 input, 1 output)",
    show_targets: bool = True,
    ax=None,
):
    """Scatter and efficient frontier projection for 1 input and 1 output."""
    for c in [input_col, output_col]:
        if c not in df.columns:
            raise KeyError(f"Column '{c}' not in df.")
    x = df[input_col].to_numpy(dtype=float)
    y = df[output_col].to_numpy(dtype=float)
    names = df.index.astype(str).tolist()
    if ax is None:
        _, ax = plt.subplots(figsize=(6.5, 4.5))
    ax.scatter(x, y, label="DMUs")
    for i, name in enumerate(names):
        ax.annotate(name, (x[i], y[i]), xytext=(5, 5), textcoords="offset points")
    theta = (
        res_input_oriented["efficiency"].to_numpy(dtype=float)
        if "efficiency" in res_input_oriented.columns
        else None
    )
    s_plus_cols = [c for c in res_input_oriented.columns if c.startswith("s_plus_")]
    y_slack = (
        res_input_oriented[s_plus_cols[0]].to_numpy(dtype=float)
        if s_plus_cols
        else np.zeros_like(x)
    )
    if show_targets and theta is not None:
        x_star = theta * x
        y_star = y + y_slack
        ax.scatter(x_star, y_star, marker="x", label="Targets (frontier)")
        for i in range(len(x)):
            ax.plot([x[i], x_star[i]], [y[i], y_star[i]], linestyle=":", linewidth=1)
    ax.set_xlabel(input_col)
    ax.set_ylabel(output_col)
    ax.set_title(title)
    ax.legend()
    return ax


def plot_quadrants_like_cnj(
    df: pd.DataFrame,
    xcol: str,
    ycol: str,
    label_col=None,
    *,
    x_ref=None,
    y_ref=None,
    size_col=None,
    size_map=None,
    legend_title: str = "Group",
    frontier_points=None,
    frontier_x=None,
    frontier_y=None,
    annotate: bool = True,
    x_pct: bool = False,
    y_pct: bool = False,
    title: str = "CNJ-style Quadrant Plot",
    ax=None,
):
    """Scatter with quadrants and optional frontier line (CNJ style)."""
    if ax is None:
        _, ax = plt.subplots(figsize=(8, 5))
    x = df[xcol].to_numpy(dtype=float)
    y = df[ycol].to_numpy(dtype=float)

    ax.scatter(x, y, s=60, edgecolors="black", linewidths=0.5)

    xr_ref = x_ref if x_ref is not None else float((np.min(x) + np.max(x)) / 2.0)
    yr_ref = y_ref if y_ref is not None else float((np.min(y) + np.max(y)) / 2.0)
    ax.axvline(xr_ref, linestyle="--", linewidth=1)
    ax.axhline(yr_ref, linestyle="--", linewidth=1)

    if annotate:
        labs = df[label_col].astype(str).tolist() if label_col else df.index.astype(str).tolist()
        for xi, yi, lab in zip(x, y, labs):
            ax.annotate(lab, (xi, yi), xytext=(3, 3), textcoords="offset points", fontsize=9)

    if frontier_points is not None and frontier_x and frontier_y:
        fp = frontier_points[[frontier_x, frontier_y]].dropna().sort_values(frontier_x)
        ax.plot(
            fp[frontier_x].to_numpy(),
            fp[frontier_y].to_numpy(),
            linewidth=1.2,
            color="tab:red",
            label="Frontier",
        )
        ax.legend()

    ax.set_xlabel(xcol)
    ax.set_ylabel(ycol)
    ax.set_title(title)
    return ax


# --------------------------
# SBM plots
# --------------------------
def plot_sbm_efficiency_bars(res: pd.DataFrame, *, title: str = "SBM ρ (input-oriented)", ax=None):
    """Bar chart of ρ (SBM)."""
    if "rho" not in res.columns:
        raise KeyError("Resultado SBM requer coluna 'rho'.")
    if ax is None:
        _, ax = plt.subplots(figsize=(max(6, len(res) * 0.4), 4))
    y = res["rho"].to_numpy(dtype=float)
    ax.bar(range(len(res)), y)
    ax.axhline(1.0, linestyle="--")
    ax.set_xticks(range(len(res)))
    ax.set_xticklabels(res.index.astype(str), rotation=90)
    ax.set_ylabel("ρ")
    ax.set_title(title)
    return ax


def plot_slacks_heatmap(
    res: pd.DataFrame,
    *,
    normalize: bool = True,
    title: str = "Input slacks (normalized)",
    ax=None,
    cmap: str | None = None,
):
    """Heatmap for s_minus by DMU; optional per-column normalization."""
    cols = [c for c in res.columns if c.startswith("s_minus_")]
    if not cols:
        raise KeyError("Resultado não contém colunas s_minus_.")
    M = res[cols].to_numpy(dtype=float)
    xt = [c.replace("s_minus_", "") for c in cols]
    yt = list(res.index.astype(str))
    if normalize:
        denom = np.maximum(M.max(axis=0, keepdims=True), 1e-12)
        M = M / denom
    if ax is None:
        _, ax = plt.subplots(figsize=(max(6, len(xt) * 0.6), max(4, len(yt) * 0.4)))
    ax.imshow(M, aspect="auto", cmap=cmap)
    ax.set_xticks(range(len(xt)))
    ax.set_xticklabels(xt, rotation=90)
    ax.set_yticks(range(len(yt)))
    ax.set_yticklabels(yt)
    ax.set_title(title)
    return ax


# --------------------------
# Correlation plots
# --------------------------
def plot_corr_heatmap(df: pd.DataFrame, cols: list[str], title: str = "Correlation heatmap"):
    """Full correlation heatmap with annotations."""
    corr = df[cols].corr()
    fig, ax = plt.subplots(figsize=(12, 10))
    sns.heatmap(
        corr,
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        vmin=-1,
        vmax=1,
        square=True,
        cbar_kws={"shrink": 0.8},
        ax=ax,
    )
    ax.set_title(title)
    return ax.figure


def plot_corr_triangle(
    df: pd.DataFrame, cols: list[str], title: str = "Correlation triangular heatmap"
):
    """Lower-triangle correlation heatmap (PyDEA-like)."""
    corr = df[cols].corr()
    mask = np.triu(np.ones_like(corr, dtype=bool))
    fig, ax = plt.subplots(figsize=(12, 10))
    sns.heatmap(
        corr,
        mask=mask,
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        vmin=-1,
        vmax=1,
        square=True,
        cbar_kws={"shrink": 0.8},
        ax=ax,
    )
    ax.set_title(title)
    return ax.figure


def plot_super_efficiency_bars(
    res: pd.DataFrame, *, title: str = "Super-efficiency (≥1)", ax=None, sort: bool = True
):
    """
    Barras de super-eficiência. Espera coluna 'super_eff' (≥1).
    """
    if "super_eff" not in res.columns:
        raise KeyError("Resultado requer coluna 'super_eff'.")
    data = res["super_eff"].astype(float)
    if sort:
        data = data.sort_values(ascending=False)
    if ax is None:
        _, ax = plt.subplots(figsize=(max(6, len(data) * 0.4), 4))
    ax.bar(range(len(data)), data.values)
    ax.axhline(1.0, linestyle="--")  # linha da fronteira "clássica"
    ax.set_xticks(range(len(data)))
    ax.set_xticklabels(data.index.astype(str), rotation=90)
    ax.set_ylabel("super_eff")
    ax.set_title(title)
    return ax
