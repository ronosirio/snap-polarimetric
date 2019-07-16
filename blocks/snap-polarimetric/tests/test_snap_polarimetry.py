"""
This module include multiple test cases to check the performance of the snap_polarimetry script.
"""
import os
import sys

from unittest.mock import patch
import shutil
from pathlib import Path, PosixPath
from xml.etree import ElementTree as ET

import attr
import geojson
import pytest

# pylint: disable=wrong-import-position
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from context import SNAPPolarimetry, ensure_data_directories_exist

TEST_POLARISATIONS = [
    (["VV"], ["VV"], True),
    (["HH"], ["HH"], True),
    (["VV"], ["HH"], False),
    (["VV", "VH"], ["VV", "VH"], True),
    (["VV", "VH"], ["HH", "HV"], False),
    (["VV", "VH"], ["VV"], False),
    (["HH"], ["HH", "HV"], True),
]


@pytest.fixture(scope="session", autouse=True)
# pylint: disable=redefined-outer-name
def fixture_mainclass():
    """
    This method initiates the SNAPPolarimetry( class from snap_polarimetry to be
    used to testing.
    """
    params = {'mask': ['sea'], 'tcorrection': 'false'}
    return SNAPPolarimetry(params)


@pytest.mark.parametrize("requested,available,expected", TEST_POLARISATIONS)
# pylint: disable=redefined-outer-name
def test_validate_polarisations(fixture_mainclass, requested, available, expected):
    """
    This methods checks whether the available polarization of the input
    data is equal to the expected polarizations.
    """
    assert fixture_mainclass.validate_polarisations(requested, available) == expected


# pylint: disable=redefined-outer-name
# pylint: disable=too-few-public-methods
@attr.s
class DummySafeFile:
    """
    This class initiate a dummy .SAFE file.
    """
    # pylint: disable-msg=R0913, R0902
    location = attr.ib()
    file_path = attr.ib()
    manifest_path = attr.ib()
    measurement_path = attr.ib()
    vh_file = attr.ib()
    vv_file = attr.ib()
    feature_collection = attr.ib()
    feature = attr.ib()


@pytest.fixture(scope="session")
def safe_file():
    """
    This method creats a dummy .SAFE file and also dummy output
    after applying pre-processing steps with snap.
    :return:
    """
    # pylint: disable=too-many-locals
    ensure_data_directories_exist()

    # Set up the whole dummy input
    input_path = Path("/tmp/input")
    safe_path = input_path / "0a99c5a1-75c0-4a0d-a7dc-c2a551936be4"
    if safe_path.exists():
        shutil.rmtree(str(safe_path))
    safe_path.mkdir()

    safe_file_path = safe_path / "S1B_IW_GRDH_1SDV_" \
                                 "20190220T050359_20190220T050424_015025_01C12F_4EA4.SAFE"
    safe_file_path.mkdir()

    _location_ = os.path.realpath(os.path.join(os.getcwd(),
                                               os.path.dirname(__file__)))

    with open(os.path.join(_location_, 'mock_data/data.json'), "rb") as f_p:
        test_featurecollection = geojson.load(f_p)
    test_feature = test_featurecollection.features[0]

    manifest_path = safe_file_path / "manifest.safe"
    manifest_path.write_text("")

    measurement_file_path = safe_file_path / "measurement"
    measurement_file_path.mkdir()

    vh_file = measurement_file_path / "s1b-iw-grd-vh-" \
                                      "20190220t050359-20190220t050424-015025-01c12f-002.tiff"
    vv_file = measurement_file_path / "s1b-iw-grd-vv-" \
                                      "20190220t050359-20190220t050424-015025-01c12f-001.tiff"

    vh_file.write_text("")
    vv_file.write_text("")

    test_safe_file = DummySafeFile(safe_path, safe_file_path,
                                   manifest_path, measurement_file_path,
                                   vh_file, vv_file, test_featurecollection, test_feature)

    # set up dummy output files that would be created by snap
    output_file_vv_before_move = Path("vv.tif")
    output_file_vv_before_move.write_text("")

    output_file_vh_before_move = Path("vh.tif")
    output_file_vh_before_move.write_text("")

    out_path = Path("/tmp/output/0a99c5a1-75c0-4a0d-a7dc-c2a551936be4")
    if out_path.exists():
        shutil.rmtree(str(out_path))
    out_path.mkdir()
    output_file_vv = out_path / "vv.tif"
    output_file_vv.write_text("")

    output_file_vh = out_path / "vh.tif"
    output_file_vh.write_text("")

    return test_safe_file


# pylint: disable=redefined-outer-name
def test_extract_polarisations(fixture_mainclass, safe_file):
    """
    This methods checks whether extract_polarisation method
    returns the expected polarisations.
    """
    assert set(fixture_mainclass.extract_polarisations
               (safe_file.file_path)) == set(["VH", "VV"])


# pylint: disable=redefined-outer-name
def test_safe_file_name(fixture_mainclass, safe_file):
    """
    This methods checks whether safe_file_name methods creates the
    expected .SAFE file name.
    """

    expected_safe_file_name = "S1B_IW_GRDH_1SDV_" \
                              "20190220T050359_20190220T050424_015025_01C12F_4EA4.SAFE"

    assert fixture_mainclass.safe_file_name(safe_file.feature) == expected_safe_file_name


# pylint: disable=redefined-outer-name
def test_manifest_file_location(fixture_mainclass, safe_file):
    """
    This method checks whether the manifest file is located inside
    the expected directory.
    """
    assert fixture_mainclass.manifest_file_location(safe_file.feature) == safe_file.manifest_path


# pylint: disable=redefined-outer-name
def test_generate_snap_graph(fixture_mainclass, safe_file):
    """
    This method apply generate_snap_graph method to create a .xml file
    for snap graph template and checks whether this file reads the
    manifest.safe file from the expected directory.
    """
    fixture_mainclass.generate_snap_graph(safe_file.feature, "VV")

    graph_xml_file = PosixPath('/tmp/S1B_IW_GRDH_1SDV_'
                               '20190220T050359_20190220T050424_015025_01C12F_4EA4.SAFE_VV.xml')
    tree = ET.parse(str(graph_xml_file))
    all_nodes = tree.findall("node")

    for graph_node in all_nodes:
        if graph_node.attrib['id'] == 'Read':

            params = graph_node.find("parameters")
            subnodes = [snode for snode in params]
            path_to_manifest = subnodes[0].text

    expected_substring = \
        "0a99c5a1-75c0-4a0d-a7dc-c2a551936be4/" +\
        "S1B_IW_GRDH_1SDV_20190220T050359_20190220T050424_015025_01C12F_4EA4.SAFE/manifest.safe"

    assert path_to_manifest.endswith(expected_substring)


@patch('os.system', lambda x: 0)
# pylint: disable=redefined-outer-name
def test_process_snap(fixture_mainclass, safe_file):
    """
    This method tests the functionality of process_snap method. And checks
    whether the expected polarization is created.
    """
    test_feature = safe_file.feature

    output_file = fixture_mainclass.process_snap(test_feature, ['VV'])
    assert output_file == ['vv']


@patch('os.system', lambda x: 0)
# pylint: disable=redefined-outer-name
def test_process_snap_multiple_polarisations(fixture_mainclass, safe_file):
    """
    This method tests the functionality of process_snap method for
    multiple polarizations.
    """
    test_feature = safe_file.feature

    output_file = fixture_mainclass.process_snap(test_feature, ['VV', 'VH'])
    assert output_file == ['vv', 'vh']


# pylint: disable=unused-variable
@patch('os.system', lambda x: 0)
def test_process_multiple_polarisations(fixture_mainclass, safe_file):
    """
    This method test the functionality of precess method. It checks
    whether the expected bbox and properties is included in the
    output.
    """
    test_fc = safe_file.feature_collection

    params = {"polarisations": ["VV", "VH"]}

    output_fc, outpath_fc, pol_fc = fixture_mainclass.process(test_fc, params)

    expected_bbox = [13.319549560546875, 38.20473446610163, 13.3209228515625, 38.205813598134746]
    assert len(output_fc.features) == 2
    assert output_fc.features[0]["bbox"] == expected_bbox
    assert output_fc.features[0]["properties"]["up42.processing.snap_polarimetric"] != ""
    assert output_fc.features[1]["bbox"] == expected_bbox
    assert output_fc.features[1]["properties"]["up42.processing.snap_polarimetric"] != ""
