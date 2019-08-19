# Sentinel-1 polarimetric preprocessing

## General information

* Block type: processing (data preparation)
* Supported input types:
  * Sentinel1_l1c_grd (Sentinel 1 L1C GRD in SAFE format)
* Provider: Up42
* Tags: SAR, radar, C-Band, imagery, preprocessing, data preparation

## Description

This repository contains the code implementing a
[block](https://docs.up42.com/getting-started/core-concepts.html#blocks)
in [UP42](https://up42.com) that performs
[polarimetric](https://en.wikipedia.org/wiki/Polarimetry)
processing of [**S**ynthetic **A**perture **R**adar](https://www.sandia.gov/radar/what_is_sar/index.html) (SAR)
with [processing Level 1C
](https://earth.esa.int/web/sentinel/level-1-post-processing-algorithms)
and **G**round **R**ange **D**etection (GRD) &mdash: geo-referenced.

### Inputs & outputs

This block takes as input a Level 1C GRD file and brings it into a format ready
for analysis. It is based on ESA's 
[**S**e**N**tinel **A**pplication **P**latform](http://step.esa.int/main/toolboxes/snap/)
(SNAP). The applied processing steps are:

 * Value conversion: linear to dB. 
 * Speckle filtering (using a median filter).
 * Creation of a land-sea mask.
 * Format conversion to GeoTIFF.
 * Apply terrain correction. 

## Requirements

 1. [docker](https://docs.docker.com/install/).
 2. [GNU make](https://www.gnu.org/software/make/).
 3. [Python](https://python.org/downloads): version >= 3.5.

## Usage

### Clone the repository in a given `<directory>`:
```bash
git clone https://github.com/up42/snap-polarimetric.git <directory>
``` 

### Build the docker images

For building the images you should tag the image such that it can bu
pushed to the UP42 docker registry, enabling you to run it as a custom
block. For that you need to pass your user ID (UID) in the `make`
command.

The quickest way to get that is just to go into the UP42 console and
copy & paste from the last clipboard that you get at the
[custom-blocks](https://console.up42.com/custom-blocks) page and after
clicking on **PUSH a BLOCK to THE PLATFORM**. For example, it will be
something like:

```bash
docker push registry.up42.com/<UID>/<image_name>:<tag>
```

Now you can launch the image building using `make` like this:

```bash
make build UID=<UID>
```

You can avoid selecting the exact UID by using `pbpaste` in a Mac (OS
X) or `xsel --clipboard --output` in Linux and do:

```bash
# mac: OS X.
make build UID=$(pbpaste | cut -f 2 -d '/')

# Linux.
make build UID=$(xsel --clipboard --output | cut -f 2 -d '/') 
```

You can additionaly specifiy a tag for your image:

```bash
make build UID=<UID> DOCKER_TAG=<docker tag>
```

if you don't specify the docker tag, it gets the default value of `latest`.

### Push the image to the UP42 registry

You first need to login into the UP42 docker registry.

```bash
make login USER=me@example.com
```

where `me@example.com` should be replaced by your username, which is
the email address you use in UP42.

Now you can finally push the image to the UP42 docker registry:

```bash
make push UID=<UID>
```

where `<UID>` is user ID referenced above. Again using the copy &
pasting on the clipboard.

```bash
# mac: OS X.
make build UID=$(pbpaste | cut -f 2 -d '/')

# Linux.
make build UID=$(xsel --clipboard --output | cut -f 2 -d '/') 
```

Note that if you specified a docker tag when you built the image, you
need to pass it now to `make`.

```bash
make push UID=<UID> DOCKER_TAG=<docker tag>
```

where `<UID>` is user ID referenced above. Again using the copy &
pasting on the clipboard.

```bash
# mac: OS X.
make build UID=$(pbpaste | cut -f 2 -d '/') DOCKER_TAG=<docker tag>

# Linux.
make build UID=$(xsel --clipboard --output | cut -f 2 -d '/') DOCKER_TAG=<docker tag>
```

After the image is pushed you should be able to see your custom block
in the [console](https://console.up42.dev/custom-blocks/) and you can
now use the block in a workflow.

### Local development HOWTO

#### Install the required libraries

First create a virtual environment either by using [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/) 
or [virtualenv](https://virtualenv.pypa.io/en/latest/).

In the case of using virtualenvwrapper do:

```bash
mkvirtualenv -p $(which python3.7) up42-snap
```

In the case of using virtualenv do:

```bash
virtualenv -p $(which python3.7) up42-snap
```

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

You can create an example `params.json` file like this:

```js
{
  "polarisations": ["VV"],
  "mask": ["sea"],
  "tcorrection": false
}
```

#### Run the processing block

 * To run an end-to-end test locally you first need to download a Sentinel-1 dataset from the UP42 platform. Run a job
 with the `Sentinel-1 L1C GRD Full Scenes` block and download its result. Copy the result (both the folder as well as
 data.json) into a new directory with the name `/tmp/e2e_snap_polarimetric/`.
 * Build the docker image as outlined above.
 * Run the following command: 
 
```bash
 docker run -e UP42_TASK_PARAMETERS="$(cat params.json)" --mount type=bind,src=/tmp/e2e_snap_polarimetric/output,dst=/tmp/output --mount type=bind,src=/tmp/e2e_snap_polarimetric/input,dst=/tmp/input snap-polarimetric:latest
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
The block takes a `up42.data.scene.sentinel1_l1c_grd` product and delivers `up42.data.aoiclipped` as output capability.

## Related information

http://step.esa.int/main/toolboxes/snap/


