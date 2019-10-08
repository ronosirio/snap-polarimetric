# SNAP polarimetric processing block
## Introduction

This repository contains the code implementing a
[block](https://docs.up42.com/getting-started/core-concepts.html#blocks)
in [UP42](https://up42.com) that performs
[polarimetric](https://en.wikipedia.org/wiki/Polarimetry)
processing of [**S**ynthetic **A**perture **R**adar](https://www.sandia.gov/radar/what_is_sar/index.html) (SAR)
with [processing Level 1C](https://earth.esa.int/web/sentinel/level-1-post-processing-algorithms)
and **G**round **R**ange **D**etection (GRD) &mdash; geo-referenced.

## Block description

* Block type: processing (data preparation)
* Supported input types:
  * Sentinel1_l1c_grd (Sentinel 1 L1C GRD in SAFE format)
* Provider: [UP42](https://up42.com)
* Tags: SAR, radar, C-Band, imagery, preprocessing, data preparation

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

The output is a [GeoTIFF](https://en.wikipedia.org/wiki/GeoTIFF) file.

### Block capabilities

The block takes a `up42.data.scene.sentinel1_l1c_grd` input
[capability](https://docs.up42.com/specifications/capabilities.html)
and delivers `up42.data.aoiclipped` as output capability.

## Requirements

 1. [git](https://git-scm.com/).
 2. [docker engine](https://docs.docker.com/engine/).
 3. [UP42](https://up42.com) account credentials.
 4. [GNU make](https://www.gnu.org/software/make/).
 5. [Python](https://python.org/downloads): version >= 3.7 &mdash; only
    for [local development](#local-development).

## Usage

### Clone the repository

```bash
git clone https://github.com/up42/snap-polarimetric.git
```

The do `cd snap-polarimetric`.

### Installing the required libraries

First create a virtual environment either by using [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/)
or [virtualenv](https://virtualenv.pypa.io/en/latest/).
In the case of using virtualenvwrapper do:

```bash
mkvirtualenv --python=$(which python3.7) up42-snap
```

In the case of using virtualenv do:

```bash
virtualenv -p $(which python3.7) up42-snap
```

Activate the virtualenv:
```bash
workon up42-snap
```

After creating a virtual environment and activating it, all the necessary libraries can be installed on this environment by doing:
```bash
make install
```

### Run the tests

This project uses [pytest](https://docs.pytest.org/en/latest/) for
testing.  To run the tests, do as following:

```bash
make test
```

### Dockerizing the block

Build the docker image locally:
```bash
make build
```

The e2e tests provided here make sure the blocks output conforms to the platform's
requirements. Run the e2e tests with:

```bash
# WARNING: this test require you set sufficient memory and disk capacity in your
# docker setup. This tests will take a significant amount of time to complete
# in a standard machine! Please be patient.
make e2e
```

### Pushing the block to the UP42 platform

For building the images you should tag the image in a way that can be
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

First make sure the manifest is valid:

```bash
make validate
```

Now you can launch the image building using `make` like this:

```bash
make build UID=<UID>
```

You can additionally specify a custom tag and version for your image (default tag
is `snap-polarimetric:latest` - `<DOCKER_TAG>:<DOCKER_VERSION>`):

```bash
make build UID=<UID> DOCKER_TAG=<docker tag> DOCKER_VERSION=<docker version>
```

#### Push the image to the UP42 registry

You first need to login into the UP42 docker registry.

```bash
make login USER=me@example.com
```

Where `me@example.com` should be replaced by your username, which is
the email address you use in UP42.

Now you can finally push the image to the UP42 docker registry:

```bash
make push UID=<UID>
```

Where `<UID>` is user ID referenced above.

Note that if you specified a custom docker tag or version when you built the image, you
need to pass it now to `make`.

```bash
make push UID=<UID> DOCKER_TAG=<docker tag> DOCKER_VERSION=<docker version>
```

After the image is pushed you should be able to see your custom block
in the [console](https://console.up42.dev/custom-blocks/) and you can
now use the block in a workflow.

## Support

 1. Open an issue here.
 2. Reach out to us on
      [gitter](https://gitter.im/up42-com/community).
 3. Mail us [support@up42.com](mailto:support@up42.com).
