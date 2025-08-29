"""Tests for save function of FaSt Fig."""

# %%
from pathlib import Path

import pytest

from fast_fig import FFig

# %%

SHOW = False  # True requires manual closing of windows


def test_save_png(tmpdir: str) -> None:
    """Save a PNG figure."""
    test_file = Path(tmpdir) / "test_save.png"
    fig = FFig(show=SHOW)
    fig.plot()
    fig.save(test_file)
    fig.close()
    assert test_file.is_file(), "PNG file not created!"


def test_save_pdf(tmpdir: str) -> None:
    """Save a PDF figure."""
    test_file = Path(tmpdir) / "test_save.pdf"
    fig = FFig(show=SHOW)
    fig.plot()
    fig.save(test_file)
    fig.close()
    assert test_file.is_file(), "PDF file not created!"


def test_save_no_suffix(tmpdir: str) -> None:
    """Save a figure without suffix."""
    test_file = Path(tmpdir) / "test_save"
    if test_file.is_file():
        test_file.unlink()
    fig = FFig(show=SHOW)
    fig.plot()

    # with pytest.warns(UserWarning):
    fig.save(test_file)

    fig.close()
    assert test_file.with_suffix(".png").is_file(), "PNG file not created!"


def test_save_multi(tmpdir: str) -> None:
    """Save multiple figures at once."""
    test_file = Path(tmpdir) / "test_save.pdf"

    fig = FFig(show=SHOW)
    fig.plot()
    fig.save(test_file, ".png", "jpg")
    fig.close()
    assert test_file.is_file(), "PDF file not created!"
    assert test_file.with_suffix(".png").is_file(), "PNG file not created!"
    assert test_file.with_suffix(".jpg").is_file(), "JPG file not created!"
