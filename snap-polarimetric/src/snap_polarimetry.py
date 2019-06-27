"""
This module is the main script for applying pre-processing steps based on
SNAP software on Sentinel 1 L1C GRD images.
"""
import os
import sys
from typing import List
from pathlib import Path
import shutil
from string import Template
import uuid
import copy

from geojson import FeatureCollection, Feature

from helper import (load_params, load_metadata,
                    ensure_data_directories_exist, save_metadata, get_logger,
                    SENTINEL1_L1C_GRD, SNAP_POLARIMETRIC)
from capabilities import set_capability

LOGGER = get_logger(__name__)
PARAMS_FILE = os.environ.get("PARAMS_FILE")
GPT_CMD = "{gpt_path} {graph_xml_path} -e {source_file}"


class WrongPolarizationError(ValueError):
    """
    This class passes to the next input file, if the current input file
    does not include the polarization.
    """
    pass


class SNAPPolarimetry:
    """
    Polarimetric data preparation using SNAP
    """

    def __init__(self):
        # the SNAP xml graph template path
        self.path_to_template = Path(__file__).parent.\
            joinpath('template/snap_polarimetry_graph.xml')

        # the temporary output path for the generated SNAP graphs
        self.path_to_tmp_out = Path('/tmp')

    @staticmethod
    def validate_polarisations(req_polarisations: list, avail_polarisations: list):
        """
        Check if requested polarisations are available
        """

        available = True
        for pol in req_polarisations:
            available = available and (pol in avail_polarisations)

        return available

    @staticmethod
    def safe_file_name(feature: Feature) -> str:
        """
        Returns the safe file name for the given feature (e.g. <safe_file_id>.SAFE)
        """

        safe_file_id = feature.properties.get(SENTINEL1_L1C_GRD)
        safe_path = Path("/tmp/input").joinpath(safe_file_id)

        return list(safe_path.glob("*.SAFE"))[0].name

    @staticmethod
    def extract_polarisations(safe_file_path: Path):
        """
        This methods extract the existing polarisations from the input data.
        """

        tiff_file_list = list(safe_file_path.joinpath("measurement").glob("*.tiff"))

        pols = [(str(tiff_file_path.stem).split("-")[3]).upper()
                for tiff_file_path in tiff_file_list]

        return pols

    def safe_file_path(self, feature: Feature) -> Path:
        """
        Returns the safe file path for the given feature
        (e.g. /tmp/input/<scene_id>/<safe_file_id>.SAFE)
        """

        safe_file_id = feature.properties.get(SENTINEL1_L1C_GRD)

        return Path("/tmp/input/").joinpath(safe_file_id, self.safe_file_name(feature))

    def manifest_file_location(self, feature: Feature) -> Path:
        """
        Generates the manifest.safe file location for a given feature
        Looks up any *.SAFE files within the feature folder
        (expects one file to be present)
        """

        return self.safe_file_path(feature).joinpath("manifest.safe")

    def process_template(self, substitutes: dict) -> str:
        """
        Processes the snap default template and substitutes
        variables based on the given substitutions
        """

        file_pointer = open(self.path_to_template)
        template = Template(file_pointer.read())

        return template.substitute(substitutes)

    def target_snap_graph_path(self, feature: Feature, polarisation: str) -> Path:
        """
        Returns the target path where the generated SNAP xml graph file should be stored
        """

        return Path(self.path_to_tmp_out).joinpath("%s_%s.xml"
                                                   % (self.safe_file_name(feature), polarisation))

    def generate_snap_graph(self, feature: Feature, polarisation: str):
        """
        Generates the snap graph xml file for the
        given feature, based on the snap graph xml template
        """

        result = self.process_template({
            'read_file_manifest_path': self.manifest_file_location(feature),
            'downcase_polarisation': polarisation.lower(),
            'upcase_polarisation': polarisation.upper(),
        })

        self.target_snap_graph_path(feature, polarisation).write_text(result)

    def process_snap(self, feature: Feature, requested_pols) -> list:
        """
        Wrapper method to facilitate the setup and the actual execution of the SNAP processing
        command for the given feature
        """

        out_files = []

        input_file_path = self.safe_file_path(feature)
        available_pols = self.extract_polarisations(input_file_path)

        if not self.validate_polarisations(requested_pols, available_pols):
            raise WrongPolarizationError("Polarization missing; proceeding to next file")

        for polarisation in requested_pols:

            self.generate_snap_graph(feature, polarisation)

            cmd = GPT_CMD.format(
                gpt_path="gpt",
                graph_xml_path=self.target_snap_graph_path(feature, polarisation),
                source_file=input_file_path
            )

            LOGGER.info("Running SNAP command: %s", cmd)
            # Need to use os.system; subprocess does not work
            return_value = os.system(cmd)

            if return_value:
                LOGGER.error("SNAP did not finish successfully with error code %d", return_value)
                sys.exit(return_value)

            out_files.append(polarisation.lower())

        return out_files

    def process(self, metadata: FeatureCollection, params: dict):
        """
        Main wrapper method to facilitate snap processing per feature
        """
        polarisations: List = params.get("polarisations", ["VV"]) or ["VV"]

        results: List[Feature] = []
        for in_feature in metadata.get("features"):
            try:
                processed_graphs = self.process_snap(in_feature, polarisations)

                for out_polarisation in processed_graphs:
                    # Besides the path we only need to change the capabilities
                    out_feature = copy.deepcopy(in_feature)
                    processed_tif_uuid = str(uuid.uuid4())
                    out_path = "/tmp/output/%s/" % processed_tif_uuid
                    os.mkdir(out_path)
                    shutil.move(("%s.tif" % out_polarisation),
                                ("%s%s.tif" % (out_path, out_polarisation)))

                    del out_feature["properties"][SENTINEL1_L1C_GRD]

                    set_capability(out_feature,
                                   SNAP_POLARIMETRIC,
                                   processed_tif_uuid)

                    results.append(out_feature)

            except WrongPolarizationError:
                continue

        return FeatureCollection(results)

    @staticmethod
    def run():
        """
        This method is the main entry point for this processing block
        """
        ensure_data_directories_exist()
        params: dict = load_params()
        input_metadata: FeatureCollection = load_metadata()
        pol_processor = SNAPPolarimetry()
        result: FeatureCollection = pol_processor.process(input_metadata, params)
        save_metadata(result)
