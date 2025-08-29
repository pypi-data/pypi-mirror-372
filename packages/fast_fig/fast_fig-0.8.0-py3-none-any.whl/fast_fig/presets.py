"""Functions to define, validate and generate presets."""

from __future__ import annotations

import json
from pathlib import Path

try:
    import yaml

    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

DEFAULT_PRESETS = {
    "color_seq": ["blue", "red", "green", "orange"],
    "linestyle_seq": ["-", "--", ":", "-."],
    "m": {
        "width": 15,
        "height": 10,
        "fontfamily": "sans-serif",
        "fontsize": 12,
        "linewidth": 2,
    },
    "s": {
        "width": 10,
        "height": 8,
        "fontfamily": "sans-serif",
        "fontsize": 12,
        "linewidth": 2,
    },
    "l": {
        "width": 20,
        "height": 15,
        "fontfamily": "sans-serif",
        "fontsize": 12,
        "linewidth": 3,
    },
    "ol": {
        "width": 8,
        "height": 6,
        "fontfamily": "serif",
        "fontsize": 9,
        "linewidth": 1,
    },
    "oe": {
        "width": 12,
        "height": 8,
        "fontfamily": "serif",
        "fontsize": 10,
        "linewidth": 1,
    },
    "square": {
        "width": 10,
        "height": 10,
        "fontfamily": "serif",
        "fontsize": 10,
        "linewidth": 1,
    },
    "colors": {
        "blue": [33, 101, 146],
        "red": [218, 4, 19],
        "green": [70, 173, 52],
        "orange": [235, 149, 0],
        "yellow": [255, 242, 0],
        "grey": [64, 64, 64],
    },
}


def define_presets(presets: dict | str | Path | None = None) -> dict:
    """Define default presets for fast_fig.

    Parameters
    ----------
    presets : dict | str | Path | None, optional
        Custom presets to override defaults. Can be:
        - Dictionary of presets
        - Path to YAML file (.yaml or .yml)
        - Path to JSON file (.json)
        - None to use defaults

    Returns
    -------
    dict
        Complete presets dictionary

    Notes
    -----
    The function will look for configuration files in the following order:
    1. fast_fig_presets.yaml
    2. fast_fig_presets.yml
    3. fast_fig_presets.json

    """
    # define defaults in preset dictionary
    pdict = DEFAULT_PRESETS.copy()

    # First check for YAML files (preferred format)
    yaml_paths = [Path("fast_fig_presets.yaml"), Path("fast_fig_presets.yml")]
    yaml_found = False

    if YAML_AVAILABLE:
        for yaml_path in yaml_paths:
            if yaml_path.is_file():
                pdict.update(load_config(yaml_path))
                yaml_found = True
                break

    # Fall back to JSON if no YAML found
    if not yaml_found and Path("fast_fig_presets.json").is_file():
        pdict.update(load_config("fast_fig_presets.json"))

    # Overwrite defaults with presets from given file
    if isinstance(presets, (str, Path)) and Path(presets).is_file():
        pdict.update(load_config(presets))

    # Overwrite defaults with specific values
    if isinstance(presets, dict):
        pdict.update(presets)

    for key in pdict:
        if key not in ["colors", "color_seq", "linestyle_seq", "linewidth_seq"]:
            pdict[key] = fill_preset(pdict[key])

    return pdict


def fill_preset(preset: dict) -> dict:
    """Fill incomplete preset with defaults.

    Parameters
    ----------
    preset : dict
        Preset dictionary to fill with defaults

    Returns
    -------
    dict
        Complete preset dictionary with all required fields

    """
    preset.setdefault("width", 15)
    preset.setdefault("height", 10)
    preset.setdefault("fontfamily", "sans-serif")
    preset.setdefault("fontsize", 12)
    preset.setdefault("linewidth", 2)
    return preset


def load_config(filepath: str | Path) -> dict:
    """Load a preset from a JSON or YAML file.

    Parameters
    ----------
    filepath : str | Path
        Path to JSON or YAML file

    Returns
    -------
    dict
        Loaded configuration data

    Raises
    ------
    FileNotFoundError
        If the file is not found
    ValueError
        If the file format is not supported or content is invalid

    """
    filepath = Path(filepath)

    if not filepath.is_file():
        msg = f"File not found: '{filepath}'"
        raise FileNotFoundError(msg)

    # First check file extension
    file_ext = filepath.suffix.lower()
    if file_ext not in [".yaml", ".yml", ".json"]:
        msg = f"Unsupported file format: {file_ext}. Use .json, .yaml, or .yml"
        raise ValueError(msg)

    try:
        with filepath.open(mode="r", encoding="utf-8") as file:
            if file_ext in [".yaml", ".yml"]:
                if not YAML_AVAILABLE:
                    msg = "YAML support requires PyYAML package. Install with: pip install pyyaml"
                    raise ValueError(msg)
                data = yaml.safe_load(file)
            else:  # .json
                data = json.load(file)
    except (json.JSONDecodeError, yaml.YAMLError) as e:
        msg = f"Invalid file format in '{filepath}': {e!s}"
        raise ValueError(msg) from e
    except OSError as e:
        msg = f"Error reading file '{filepath}': {e!s}"
        raise OSError(msg) from e

    return data


def generate_file(filepath: str = "fast_fig_presets_example") -> None:
    """Generate a preset example that can be modified for custom presets.

    Parameters
    ----------
    filepath : str, optional
        Base path for generated files, by default "fast_fig_presets_example"
        Will generate both YAML (preferred) and JSON versions if YAML is available

    Notes
    -----
    If the provided filepath includes an extension (.yaml, .yml, or .json),
    only that format will be generated. Otherwise, both YAML (if available)
    and JSON versions will be generated.

    """
    example_dict = define_presets()
    filepath = Path(filepath)

    # Check if specific format was requested
    if filepath.suffix.lower() in [".yaml", ".yml"]:
        if not YAML_AVAILABLE:
            msg = "YAML support requires PyYAML package. Install with: pip install pyyaml"
            raise ValueError(msg)
        with filepath.open("w", encoding="utf-8") as file:
            yaml.dump(example_dict, file, sort_keys=False, indent=2)
    elif filepath.suffix.lower() == ".json":
        with filepath.open("w", encoding="utf-8") as file:
            json.dump(example_dict, file, indent=2)
    else:
        # No specific format requested, generate both if possible
        if YAML_AVAILABLE:
            yaml_path = filepath.with_suffix(".yaml")
            with yaml_path.open("w", encoding="utf-8") as file:
                yaml.dump(example_dict, file, sort_keys=False, indent=2)

        # Always generate JSON as fallback
        json_path = filepath.with_suffix(".json")
        with json_path.open("w", encoding="utf-8") as file:
            json.dump(example_dict, file, indent=2)
