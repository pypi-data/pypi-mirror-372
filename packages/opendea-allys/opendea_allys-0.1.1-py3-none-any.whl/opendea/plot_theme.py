import matplotlib as mpl


def apply_theme():
    mpl.rcParams.update(
        {
            "figure.dpi": 120,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.titleweight": "semibold",
            "axes.grid": True,
            "grid.linestyle": ":",
            "grid.alpha": 0.3,
            "legend.frameon": False,
            "font.size": 10,
        }
    )
