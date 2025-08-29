"""Basic tests for fast_fig."""

from __future__ import annotations

# %%
import matplotlib.pyplot as plt
import numpy as np
import pytest

from fast_fig import FFig

try:
    import pandas as pd

    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

# %%
SHOW = True  # True requires manual closing of windows
RNG = np.random.default_rng(42)  # Create a random number generator with fixed seed


# %%
def test_ffig() -> None:
    """Test basic plot."""
    fig = FFig(show=SHOW)
    fig.plot()
    assert len(fig.current_axis._children) == 2, "Simple plot should generate two lines!"  # noqa: SLF001
    fig.close()


def test_ffig_args() -> None:
    """Test basic plot."""
    fig = FFig("l", 2, 1, show=SHOW)
    fig.plot()
    assert len(fig.current_axis._children) == 2, "Simple plot should generate two lines!"  # noqa: SLF001
    fig.close()


def test_plot_1d() -> None:
    """Test plot of vector."""
    fig = FFig(show=SHOW)
    fig.plot(RNG.standard_normal(5))
    assert len(fig.current_axis._children) == 1, "Plot with one vector should generate one line!"  # noqa: SLF001
    fig.close()


def test_plot_mat() -> None:
    """Test plot of matrix."""
    mat = np.array(
        [
            [1, 2, 3, 4, 5],
            RNG.standard_normal(5),
            2 * RNG.standard_normal(5),
            1.5 * RNG.standard_normal(5),
        ],
    )
    with FFig(show=SHOW) as fig:
        fig.plot(mat)
        assert len(fig.current_axis._children) == 3, (  # noqa: SLF001
            "Plot with matrix shape (4, 8) should generate three lines!"
        )


def test_plot_list() -> None:
    """Test plot of a list."""
    with FFig("l", 2, 1, show=SHOW) as fig:
        fig.plot([1, 2, 3], [1, 1, 3])
        assert len(fig.current_axis._children) == 1, (
            "Simple plot with list should generate one line!"
        )  # noqa: SLF001


def test_plot_lol() -> None:
    """Test plot of a list of lists."""
    with FFig("l", 2, 1, show=SHOW) as fig:
        fig.plot([1, 2, 3], [[1, 1, 3], [1, 2, 1]])
        assert len(fig.current_axis._children) == 2, (
            "Simple plot with list should generate two lines!"
        )  # noqa: SLF001


def test_plot_lol_arg() -> None:
    """Test plot of a list of lists with additional argument."""
    with FFig("l", 2, 1, show=SHOW) as fig:
        fig.plot([1, 2, 3], [[1, 1, 3], [1, 2, 1]], "--")
        assert len(fig.current_axis._children) == 2, (
            "Simple plot with list should generate two lines!"
        )  # noqa: SLF001


def test_semilogx() -> None:
    """Test plot with logarithmic x-axis."""
    fig = FFig(show=SHOW)
    fig.semilogx(RNG.standard_normal(5))
    assert len(fig.current_axis._children) == 1, "Plot with one vector should generate one line!"  # noqa: SLF001
    fig.close()


def test_semilogx() -> None:
    """Test plot with logarithmic y-axis."""
    fig = FFig(show=SHOW)
    fig.semilogx(RNG.standard_normal(5))
    assert len(fig.current_axis._children) == 1, "Plot with one vector should generate one line!"  # noqa: SLF001
    fig.close()


def test_label() -> None:
    """Test xlabel and ylabel."""
    fig = FFig(show=SHOW)
    fig.plot()
    fig.set_xlabel("xlab")
    fig.set_ylabel("ylab")
    fig.set_title("Title")
    assert fig.current_axis.get_xlabel() == "xlab", "xlabel should be set to xlab!"
    assert fig.current_axis.get_ylabel() == "ylab", "ylabel should be set to ylab!"
    assert fig.current_axis.get_title() == "Title", "title should be set to Title!"
    fig.close()
    fig.close()


# %%
def test_subplot_nrows() -> None:
    """Test subplot with nrows."""
    fig = FFig(show=SHOW)
    fig.subplot(nrows=3)
    fig.plot()
    assert len(fig.handle_axis) == 3, "Subplot(nrows=3) should give 3 axis."
    fig.close()


def test_subplot_ncols() -> None:
    """Test subplot with ncols."""
    fig = FFig(show=SHOW)
    fig.subplot(nrows=4)
    fig.plot()
    assert len(fig.handle_axis) == 4, "Subplot(ncols=4) should give 4 axis."
    fig.close()


def test_subplot_nrows_cols() -> None:
    """Test subplot with nrows, ncols and index."""
    fig = FFig(show=SHOW)
    fig.subplot(nrows=4, ncols=3, index=4)
    fig.plot()
    assert fig.handle_axis.shape == (
        4,
        3,
    ), "Subplot(nrows=4, ncols=3) should give 4x3 plots."
    assert fig.subplot_index == 4, "subplot(index=4) should set current axe number to 4"
    fig.close()


def test_subplot_index() -> None:
    """Test subplot with index."""
    fig = FFig(show=SHOW, nrows=4, ncols=3)
    fig.subplot(index=4)
    fig.plot()
    assert fig.subplot_index == 4, "subplot(index=4) should set current axe number to 4"
    fig.close()


def test_subplot_arg() -> None:
    """Test subplot with index."""
    fig = FFig(show=SHOW, nrows=4, ncols=3)
    fig.subplot(3)
    fig.plot()
    assert fig.subplot_index == 3, "subplot(index=4) should set current axe number to 4"
    fig.close()


@pytest.mark.skipif(not PANDAS_AVAILABLE, reason="pandas not installed")
def test_plot_dataframe() -> None:
    """Test plot of pandas DataFrame with two columns and index."""
    fig = FFig(show=SHOW)

    # Create a test DataFrame
    index = pd.date_range("2024-01-01", periods=5, freq="D")
    df = pd.DataFrame(  # noqa: PD901
        {
            "A": [1, 2, 3, 4, 5],
            "B": [2, 4, 6, 8, 10],
        },
        index=index,
    )

    fig.plot(df)
    assert len(fig.current_axis._children) == 2, (  # noqa: SLF001
        "Plot with DataFrame of two columns should generate two lines!"
    )
    assert fig.current_axis.get_xlabel() == "Date", (
        "xlabel should default to index name for DataFrame!"
    )
    fig.close()


def test_context_manager() -> None:
    """Test using FFig as a context manager."""
    with FFig(show=SHOW) as fig:
        fig.plot([1, 2, 3])
        assert len(fig.current_axis._children) == 1, "Plot should generate one line"  # noqa: SLF001

    # After context exit, figure should be closed
    assert plt.fignum_exists(fig.handle_fig.number) is False, (
        "Figure should be closed after context exit"
    )


def test_clear() -> None:
    """Test clearing figure content."""
    fig = FFig(show=SHOW)
    fig.plot([1, 2, 3])
    assert len(fig.current_axis._children) == 1, "Plot should generate one line"  # noqa: SLF001

    # Test successful clear
    success = fig.clear()
    assert success is True, "Clear should return True on success"
    assert len(fig.current_axis._children) == 0, "Clear should remove all plot elements"  # noqa: SLF001

    # Test reuse after clear
    fig.plot([4, 5, 6])
    assert len(fig.current_axis._children) == 1, "Should be able to plot after clear"  # noqa: SLF001
    fig.close()


def test_close() -> None:
    """Test closing figure."""
    fig = FFig(show=SHOW)
    fig.plot([1, 2, 3])

    # Test successful close
    success = fig.close()
    assert success is True, "Close should return True on success"
    assert plt.fignum_exists(fig.handle_fig.number) is False, "Figure should be closed"

    # Test double close
    success = fig.close()
    assert success is True, "Close should return True when figure already closed"


def test_clear_after_close() -> None:
    """Test clearing after closing."""
    fig = FFig(show=SHOW)
    fig.plot([1, 2, 3])
    fig.close()

    # Try to clear after close
    success = fig.clear()
    assert success is True, "Clear should return True after figure is closed"
