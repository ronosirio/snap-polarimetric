"""
This module creates the requested capability and is used in snap_polarimetry
script.
"""
from typing import Any
from geojson import Feature


def set_capability(feature: Feature, capability: str, value: Any) -> Feature:
    """
    This methods create a new capability for the ouput json file.
    """
    feature["properties"][capability] = value
    return feature
