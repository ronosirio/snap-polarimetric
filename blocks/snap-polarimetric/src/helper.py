"""
This module includes necessary helper functions that are used in the snap_polarimetry script.
"""
import json
import os
from pathlib import Path
import logging
import rasterio
from geojson import FeatureCollection, Feature
from stac import STACQuery


LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
SENTINEL1_L1C_GRD = "up42.data.scene.sentinel1_l1c_grd"
SNAP_POLARIMETRIC = "up42.data.aoiclipped"


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
    Path("/tmp/input/").mkdir(parents=True, exist_ok=True)
    Path("/tmp/output/").mkdir(parents=True, exist_ok=True)


def load_params() -> dict:
    """
    Get the parameters for the current task directly from the task parameters.
    """
    logger = get_logger(__name__)
    data: str = os.environ.get(
        "UP42_TASK_PARAMETERS", "{}",
    )
    logger.debug("Fetching parameters for this block: %s", data)
    if data == "":
        data = "{}"
    return json.loads(data)


def load_query(validator=lambda x: True) -> STACQuery:
    """
    Get the query for the current task directly from the task parameters.
    """
    logger = get_logger(__name__)
    data: str = os.environ.get(
        "UP42_TASK_PARAMETERS", "{}",
    )
    logger.debug("Raw task parameters from UP42_TASK_PARAMETERS are: %s", data)
    query_data = json.loads(data)
    return STACQuery.from_dict(query_data, validator)


def load_metadata() -> FeatureCollection:
    """
    Get the geojson metadata from the provided location
    """
    ensure_data_directories_exist()
    if Path("/tmp/input/data.json").exists():
        with Path("/tmp/input/data.json").open() as f_p:
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
    with Path("/tmp/output/data.json").open(mode="w") as f_p:
        f_p.write(json.dumps(result))


def read_write_bigtiff(out_path, pol):
    """
    This method is a proper way to read big GeoTIFF raster data.
    """
    with rasterio.Env():
        with rasterio.open("%s%s.tif" % (out_path, pol[0])) as src0:
            kwargs = src0.profile
            kwargs.update(
                bigtiff="YES", compress="lzw"  # Output will be larger than 4GB
            )

            windows = src0.block_windows(1)

            with rasterio.open("%s%s.tif" % (out_path, "stack"), "w", **kwargs) as dst:
                for b_id, layer in enumerate(pol, start=1):
                    src = rasterio.open("%s%s.tif" % (out_path, layer))
                    for _, window in windows:
                        src_data = src.read(1, window=window)
                        dst.write_band(b_id, src_data, window=window)
                        dst.set_band_description(b_id, layer)
