"""Helpers for loading per-game tuning parameters from JSON files."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_tuning_file(path: Path | None) -> dict[str, Any]:
    """
    Loads a JSON tuning file into a dictionary.

    :param path: Location of the JSON file, or None when a game has no tuning file.
    :return: The parsed top-level JSON object, or an empty dictionary if the file does not exist.
    :raises ValueError: If the file exists but its top-level value is not a JSON object.
    """
    if path is None or not path.is_file():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Tuning file must contain a JSON object: {path}")
    return data


def get_section(data: dict[str, Any], name: str) -> dict[str, Any]:
    """
    Returns a named sub-object of a tuning dictionary.

    :param data: The loaded tuning dictionary.
    :param name: Key of the sub-object.
    :return: The sub-object, or an empty dictionary if it is missing or not an object.
    """
    section = data.get(name, {})
    return section if isinstance(section, dict) else {}


def get_number(section: dict[str, Any], key: str, default: float) -> float:
    """
    Reads a numeric tuning value, falling back to a default when the key is missing.

    :param section: The tuning object holding the value.
    :param key: Name of the value.
    :param default: Value used when the key is absent.
    :return: The value converted to float.
    """
    return float(section.get(key, default))
