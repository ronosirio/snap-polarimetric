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
* Apply terrain correction 

## Usage

### Local development HOWTO

Clone the repository in a given `<directory>`:

```bash
git clone https://github.com/up42/snap-polarimetric.git <directory>
``` 

then do `cd <directory>`.
#### Install the required libraries
First create a virtual environment either by using [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/) 
or [virtualenv](https://virtualenv.pypa.io/en/latest/).
In the case of using virtualenvwrapper do:

```mkvirtualenv --python=$(which python3.7) up42-snap```

In the case of using virtualenv do:

````
virtualenv -p $(which python3.7) up42-snap
````

After creating a virtual environment and activating it, all the necessary libraries can be installed on this environment by doing:

```bash
cd snap-polarimetric/blocks/snap-polarimetric/
./setup.sh
```

### Run the tests

This project uses [pytest](https://docs.pytest.org/en/latest/) for testing.
To run the tests, first create two empty `/tmp/input/` and `/tmp/output` directories. The output will be written to the `/tmp/output/` directory.
Finally, to run the test do as following:

```bash
cd snap-polarimetric/blocks/snap-polarimetric/
./test.sh
```

### Build and run the docker image locally

To build the Docker image for local using, first you need to create two local images as follow:
```bash
cd snap-polarimetric/blocks/snap-polarimetric/libs
docker build -f Dockerfile-esa-snap -t up42-esa-snap:latest .
docker build -f Dockerfile-up42-snap -t up42-snap:latest .
``` 
Note that the second command above, creates a base image with the newest version of SNAP. The third command creates the second
image which has the necessary installation of python 3.7 and then it will be used in the main Dockerfile located in `snap-polarimetric/blocks/snap-polarimetric/`.

finally you can run the following shell command from the repository that contains the Dockerfile: 

```bash
cd snap-polarimetric/blocks/snap-polarimetric/
# Build the image.
docker build -t snap-polarimetric -f Dockerfile . 

```
In the next step you can use the `params.json` file to define which polarization you want to work
and whether you want to have land-sea mask or terrain-correction as pre-processing steps. Please note that if you choose to have land-sea mask, you can only set `land` or `sea` as a parameter.

An example of params.json file is shown below:

``
{
  "polarisations": ["VV"],
  "mask": ["sea"],
  "tcorrection": "false"
}
``

#### Run the processing block 
 * First you need to get corresponding id after having the outcome of the `Sentinel-1 L1C GRD Full Scenes` data block and replace
 `<id>` in the `e2e.sh` file with the corresponding data id. Note that, this id also provide `data.json` file as well. 
 * Then you can run the following shell command:
```bash
    cd snap-polarimetric/blocks/snap-polarimetric/
    ./e2e.sh
 ```
 * The above command creates a directory `/tmp/e2e_snap_polarimetric/` with two subdirectories `input` and `output`.
  In the `/tmp/e2e_snap_polarimetric/input` there are an example of `Sentinel-1 L1C GRD full Scenes` in SAFE format and `data.json` which is a
  [GeoJSON](https://en.wikipedia.org/wiki/GeoJSON) file.
 * Build the docker image as outlined above.
 * Run the following command: 
 
```
 docker run -e UP42_TASK_PARAMETERS="$(cat params.json)" --mount type=bind,src=/tmp/e2e_snap_polarimetric/output,dst=/tmp/output --mount type=bind,src=/tmpe2e_snap_polarimetric/input,dst=/tmp/input superresolution:latest
```
This [bind mounts](https://docs.docker.com/storage/bind-mounts/) the
host and container `/tmp/e2e_snap_polarimetric/input` and `/tmp/e2e_snap_polarimetric/output` directories into the
**input** and **output** directories respectively. If you wish you can
set it to some other directory that is convenient to you.
 
Output format
-------------
GeoTIFF

Capabilities
------------
The block takes a ``data.sentinel1_l1c_grd`` product and delivers ``up42.processing.snap_polarimetric`` as capability.

## Related information

http://step.esa.int/main/toolboxes/snap/
