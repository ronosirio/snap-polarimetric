"""
This module includes necessary helper functions that are used in the snap_polarimetry script.
"""
import json
import os
import pathlib
import logging
from geojson import FeatureCollection, Feature


LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
SENTINEL1_L1C_GRD = "up42.data.scene.sentinel1_l1c_grd"
SNAP_POLARIMETRIC = "up42.processing.snap_polarimetric"


def get_logger(name, level=logging.DEBUG):
    """
    This method creates logger object and sets the default log level to DEBUG.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    # create console handler and set level to debug
    c_h = logging.StreamHandler()
    c_h.setLevel(level)
    formatter = logging.Formatter(LOG_FORMAT)
    c_h.setFormatter(formatter)
    logger.addHandler(c_h)
    return logger


def ensure_data_directories_exist():
    """
    This method checks input and output directories for data flow.
    """
    pathlib.Path('/tmp/input/').mkdir(parents=True, exist_ok=True)
    pathlib.Path('/tmp/output/').mkdir(parents=True, exist_ok=True)


def load_params() -> dict:
    """
    Get the parameters for the current task directly from the task parameters.
    """
    helper_logger = get_logger(__name__)
    data: str = os.environ.get("UP42_TASK_PARAMETERS", '{}')
    helper_logger.debug("Fetching parameters for this block: %s", data)
    if data == "":
        data = "{}"
    return json.loads(data)


def load_metadata() -> FeatureCollection:
    """
    Get the geojson metadata from the provided location
    """
    ensure_data_directories_exist()
    if os.path.exists("/tmp/input/data.json"):
        with open("/tmp/input/data.json") as f_p:
            data = json.loads(f_p.read())

        features = []
        for feature in data["features"]:
            features.append(Feature(**feature))
    else:
        features = []

    return FeatureCollection(features)


def save_metadata(result: FeatureCollection):
    """
    Save the geojson metadata to the provided location
    """
    ensure_data_directories_exist()
    with open("/tmp/output/data.json", "w") as f_p:
        f_p.write(json.dumps(result))
