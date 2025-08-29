"""Verify matching reference for FaSt_Fig."""

# %%
from __future__ import annotations

import hashlib
import os
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from fast_fig import FFig

if os.getenv("CI") == "true":  # Skip in GitHub actions
    pytest.skip("Skipping references tests in CI", allow_module_level=True)

# %%

SHOW = False  # True requires manual closing of windows
REFERENCE_PATH = Path("tests/references")


# %%
def calc_checksum(file_path: str | Path) -> str:
    """Calculate the checksum of a file."""
    hasher = hashlib.sha256()
    image = Image.open(file_path)
    image_bytes = np.array(image).tobytes()
    hasher.update(image_bytes)
    return hasher.hexdigest()


# %%
def test_subplot2(tmpdir: str, test_name: str = "test_subplot2.png") -> None:
    """Test subplot with 2 plots."""
    test_file = Path(tmpdir) / test_name
    fig = FFig(nrows=2, show=SHOW)  # create figure
    fig.plot([1, 2, 3, 1, 2, 3, 4, 1, 1])  # plot first data set
    fig.set_title("First data set")  # set title for subplot
    fig.subplot()  # set focus to next subplot/axis
    assert fig.subplot_index == 1, "Current axe number should be 1"
    fig.plot([0, 1, 2, 3, 4], [0, 1, 1, 2, 3], label="random")  # plot second data set
    fig.legend()  # generate legend
    fig.grid()  # show translucent grid to highlight major ticks
    fig.set_xlabel("Data")  # create xlabel for second axis
    fig.save(test_file)
    fig.close()
    assert test_file.is_file(), "File not created!"
    checksum = calc_checksum(test_file)

    ref_file = REFERENCE_PATH / test_name
    assert ref_file.is_file(), "Reference file missing!"
    ref_checksum = calc_checksum(ref_file)
    assert checksum == ref_checksum, "Checksums do not match!"


# %%
def test_subplot6(tmpdir: str, test_name: str = "test_subplot6.png") -> None:
    """Test subplot with 6 plots."""
    test_file = Path(tmpdir) / test_name
    fig = FFig("l", nrows=2, ncols=3, isubplot=1, show=SHOW)
    assert fig.subplot_index == 1, "Current axe number should be 1"
    fig.plot([1, 2, 3, 1, 2, 3, 4, 1, 1])
    fig.set_title("Plot 2")
    fig.next_axis()
    assert fig.subplot_index == 2, "Current axe number should be 2"
    fig.plot([1, 2, 3, 1, 2, 3, 4])
    fig.set_title("Plot 3")
    fig.set_current_axis(5)
    assert fig.subplot_index == 5, "Current axe number should be 5"
    fig.plot([2, 3, 4, 1, 1])
    fig.set_title("Plot 6")
    fig.save(test_file)
    fig.close()
    assert test_file.is_file(), "File not created!"
    checksum = calc_checksum(test_file)

    ref_file = REFERENCE_PATH / test_name
    assert ref_file.is_file(), "Reference file missing!"
    ref_checksum = calc_checksum(ref_file)
    assert checksum == ref_checksum, "Checksums do not match!"


# %%
def test_subplot2x2(tmpdir: str, test_name: str = "test_subplot2x2.png") -> None:
    """Test subplot with 4 plots."""
    test_file = Path(tmpdir) / test_name
    test_data = np.array(
        [
            [
                -0.83722053,
                -0.51003761,
                0.4682258,
                -0.23955723,
                -0.86086072,
                -1.66734963,
                -1.57778298,
                1.17874921,
                2.0594913,
                -0.45492548,
            ],
            [
                0.84123257,
                1.08339579,
                -1.56462187,
                0.55017709,
                -0.00619132,
                0.24243796,
                0.76902829,
                0.18287101,
                -2.0649845,
                1.58538508,
            ],
        ]
    )

    fig = FFig("l", show=SHOW)
    fig.subplot(2, 2, sharex=True)
    fig.pcolor(test_data)

    fig.next_axis()
    assert fig.subplot_index == 1, "Current axe number should be 1"
    fig.scatter(test_data, test_data)
    fig.set_current_axis(3)  # jump to last subplot
    assert fig.subplot_index == 3, "Current axe number should be 3"
    fig.plot(test_data)
    fig.save(test_file)
    fig.close()
    assert test_file.is_file(), "File not created!"
    checksum = calc_checksum(test_file)

    ref_file = REFERENCE_PATH / test_name
    assert ref_file.is_file(), "Reference file missing!"
    ref_checksum = calc_checksum(ref_file)
    assert checksum == ref_checksum, "Checksums do not match!"


# %%
def test_pcolor(tmpdir: str, test_name: str = "test_pcolor.png") -> None:
    """Test pcolor with Gaussian."""
    test_file = Path(tmpdir) / test_name
    xvec = np.arange(-50e-6, 50e-6, 0.1e-6)
    xmesh, ymesh = np.meshgrid(xvec, xvec)
    r_gauss = 15e-6 / 2
    e_gauss = np.exp(-(xmesh**2 + ymesh**2) / r_gauss**2)

    fig = FFig(show=SHOW)
    fig.pcolor(e_gauss)
    fig.contour(e_gauss, [0.1], colors="white")
    fig.save(test_file)
    fig.close()
    assert test_file.is_file(), "File not created!"
    checksum = calc_checksum(test_file)

    ref_file = REFERENCE_PATH / test_name
    assert ref_file.is_file(), "Reference file missing!"
    ref_checksum = calc_checksum(ref_file)
    assert checksum == ref_checksum, "Checksums do not match!"


# %%
def test_pcolor_log(tmpdir: str, test_name: str = "test_pcolor_log.png") -> None:
    """Test pcolor with logarithmic scaling."""
    test_file = Path(tmpdir) / test_name

    xvec = np.arange(-50e-6, 50e-6, 0.1e-6)
    xmesh, ymesh = np.meshgrid(xvec, xvec)
    r_gauss = 15e-6 / 2
    e_gauss = np.exp(-(xmesh**2 + ymesh**2) / r_gauss**2)

    fig = FFig(show=SHOW)
    fig.pcolor_log(e_gauss, vmin=1e-10, vmax=1)
    fig.colorbar()
    fig.save(test_file)
    fig.close()
    assert test_file.is_file(), "File not created!"
    checksum = calc_checksum(test_file)

    ref_file = REFERENCE_PATH / test_name
    assert ref_file.is_file(), "Reference file missing!"
    ref_checksum = calc_checksum(ref_file)
    assert checksum == ref_checksum, "Checksums do not match!"


# %%
def test_legend(tmpdir: str, test_name: str = "test_legend.png") -> None:
    """Test lengend function."""
    test_file = Path(tmpdir) / test_name
    fig = FFig("OL", show=SHOW)
    fig.set_ylim(-10, 2)
    fig.plot([1, 2, 3, 4, 5, 6], [0.2, 0.4, 0.5, 0.3, 0.1, 0], label="Test")
    fig.plot([1, 2, 3, 4, 5, 6], [0.1, 0.2, 0.4, 0.5, 0.2, 0.1], label="Test")
    fig.legend()
    fig.grid()
    assert fig.legend_count() == 2, "Legend count should be 2"
    fig.save(test_file)
    fig.close()
    assert test_file.is_file(), "File not created!"
    checksum = calc_checksum(test_file)

    ref_file = REFERENCE_PATH / test_name
    assert ref_file.is_file(), "Reference file missing!"
    ref_checksum = calc_checksum(ref_file)
    assert checksum == ref_checksum, "Checksums do not match!"
