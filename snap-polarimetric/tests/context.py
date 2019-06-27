"""
This module is used in test_snap_polarimetry script.
"""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../libs')))

from src.snap_polarimetry import SNAPPolarimetry #pylint: disable=unused-import,wrong-import-position
