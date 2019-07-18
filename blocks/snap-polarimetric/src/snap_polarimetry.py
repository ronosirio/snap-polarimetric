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
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling

from helper import (load_params, load_metadata,
                    ensure_data_directories_exist, save_metadata, get_logger,
                    SENTINEL1_L1C_GRD, SNAP_POLARIMETRIC)
from capabilities import set_capability

LOGGER = get_logger(__name__)
PARAMS_FILE = os.environ.get("PARAMS_FILE")
GPT_CMD = "{gpt_path} {graph_xml_path} -e {source_file}"


# pylint: disable=unnecessary-pass
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

    def __init__(self, params):
        # the SNAP xml graph template path
        self.params = params
        try:
            params['mask']
        except KeyError:
            params['mask'] = None

        try:
            params['tcorrection']
        except KeyError:
            params['tcorrection'] = True

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
        src = self.path_to_template
        path_to_temp = Path(__file__).parent.joinpath('template/')

        shutil.copy(src, Path(path_to_temp).joinpath("snap_polarimetry_graph_%s.xml" % "copy"))
        dst = Path(__file__).parent.joinpath("template/snap_polarimetry_graph_%s.xml" % "copy")

        if self.params['mask'] is None:
            self.revise_graph_xml(dst)
        if self.params['tcorrection'] == 'false':
            self.revise_graph_xml(dst)

        file_pointer = open(dst)
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
        if self.params['mask'] == ['sea']:
            result = self.process_template({
                'read_file_manifest_path': self.manifest_file_location(feature),
                'downcase_polarisation': polarisation.lower(),
                'upcase_polarisation': polarisation.upper(),
                'mask_type': 'false'
            })
        elif self.params['mask'] == ['land']:
            result = self.process_template({
                'read_file_manifest_path': self.manifest_file_location(feature),
                'downcase_polarisation': polarisation.lower(),
                'upcase_polarisation': polarisation.upper(),
                'mask_type': 'true'
            })
        else:
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
        out_path: str = ''
        processed_graphs: List = []
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

        Path(__file__).parent.joinpath("template/snap_polarimetry_graph_%s.xml" % "copy").unlink()
        return FeatureCollection(results), out_path, processed_graphs

    @staticmethod
    def reproject_to_webmercator(output_filepath, list_pol):
        """
        This method maps the pixels of the output image to a different coordinate
        reference system and transform. This process is known as reprojection.
        """
        for pol in list_pol:
            dst_crs = 'epsg:3857'
            init_output = "%s%s.tif" % (output_filepath, pol)
            update_output = "%s%s.tif" % (output_filepath, pol+'_WM')
            with rasterio.open(init_output) as src:
                transform, width, height = calculate_default_transform(
                    src.crs, dst_crs, src.width, src.height, *src.bounds)
                kwargs = src.meta.copy()
                kwargs.update({
                    'crs': dst_crs,
                    'transform': transform,
                    'width': width,
                    'height': height,
                })
                with rasterio.open(update_output, 'w', **kwargs) as dst:
                    for i in range(1, src.count + 1):
                        reproject(
                            source=rasterio.band(src, i),
                            destination=rasterio.band(dst, i),
                            src_transform=src.transform,
                            src_crs=src.crs,
                            dst_transform=transform,
                            dst_crs=dst_crs,
                            resampling=Resampling.nearest)
            Path(output_filepath).joinpath("%s.tif" % pol).unlink()

    @staticmethod
    def post_process(output_filepath, list_pol):
        """
        This method updates the novalue data to be 0 so it
        can be recognized by qgis.
        """
        for pol in list_pol:
            init_output = "%s%s.tif" % (output_filepath, pol+'_WM')
            src = rasterio.open(init_output)
            p_r = src.profile
            p_r.update(nodata=0)
            update_name = "%s%s.tif" % (output_filepath, "updated_" + pol+'_WM')
            image_read = src.read()
            with rasterio.open(update_name, "w", **p_r) as dst:
                for b_i in range(src.count):
                    dst.write(image_read[b_i, :, :], indexes=b_i + 1)

    # pylint: disable=unused-variable
    def revise_graph_xml(self, xml_file):
        """
        This method checks whether, land-sea-mask or terrain-correction
        pre-processing step is needed or not. If not, it removes the
        corresponding node from the .xml file.
        """
        import xml.etree.ElementTree as Et

        tree = Et.parse(xml_file)
        root = tree.getroot()
        all_nodes = root.findall("node")
        if self.params['mask'] is None:
            for index, desc in enumerate(all_nodes):
                if all_nodes[index].attrib['id'] == 'Land-Sea-Mask':
                    root.remove(all_nodes[index])
                    params = all_nodes[index + 1].find('sources')
                    params[0].attrib['refid'] = all_nodes[index - 1].attrib['id']
            tree.write(xml_file)

        if self.params['tcorrection'] == 'false':
            for index, desc in enumerate(all_nodes):
                if all_nodes[index].attrib['id'] == 'Terrain-Correction':
                    root.remove(all_nodes[index])
                    params = all_nodes[index + 1].find('sources')
                    params[0].attrib['refid'] = all_nodes[index - 1].attrib['id']
            tree.write(xml_file)

    @staticmethod
    # pylint: disable=unused-variable
    def run():
        """
        This method is the main entry point for this processing block
        """
        ensure_data_directories_exist()
        params: dict = load_params()
        input_metadata: FeatureCollection = load_metadata()
        pol_processor = SNAPPolarimetry(params)
        result, outfile, outfile_pol = pol_processor.process(input_metadata, params)
        # Reproject to webmercator
        pol_processor.reproject_to_webmercator(outfile, outfile_pol)
        save_metadata(result)
        if params['mask'] is not None:
            pol_processor.post_process(outfile, outfile_pol)
