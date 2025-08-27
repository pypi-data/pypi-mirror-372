"""Visualization helpers for matplotlib styling."""

import matplotlib.pyplot as plt
import scienceplots  # noqa: F401  # register 'science' style


def style() -> None:
    """Set the style for matplotlib."""
    plt.style.use("science")
    plt.rcParams.update(
        {
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "font.family": "sans-serif",
            "figure.dpi": 600,
            "savefig.dpi": 600,
            "figure.figsize": (10, 7),
            "font.size": 13,
            "axes.labelsize": 17,
            "axes.titlesize": 17,
            "xtick.labelsize": 13,
            "ytick.labelsize": 13,
            "legend.fontsize": 13,
        }
    )


__all__ = ["style"]

# Backward compatibility alias
set_plt_style = style


