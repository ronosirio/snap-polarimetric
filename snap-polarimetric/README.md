# Sentinel-1 polarimetric preprocessing

## General information

* Block type: processing (data preparation)
* Supported input types:
  * Sentinel1_l1c_grd (Sentinel 1 L1C GRD in SAFE format)
* Provider: Up42
* Tags: SAR, radar, C-Band, imagery, preprocessing, data preparation

## Description
This block takes a Level 1C GRD file and brings it into a format ready for analysis. It is based on ESA's Sentinel Application Platform (SNAP). The applied processing steps are:
* Value conversion to dB
* Speckle filtering (using a median filter)
* Creation of a land-sea mask
* Format conversion to GeoTIFF 

## Supported parameters

* ``polarisations`` - Requested polarisations, either one of [VV, VH], [HH, HV], [VV], [VH], [HV] or [HH]. The operation will fail and give a corresponding error message if the requested polarization is not part of the input file.

NOTE: The current implementation only delivers output of the VV polarisation.

Output format
-------------
GeoTIFF

Capabilities
------------
The block takes a ``data.sentinel1_l1c_grd`` product and delivers ``up42.processing.snap_polarimetric`` as capability.

## Related information

http://step.esa.int/main/toolboxes/snap/
