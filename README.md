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


This block takes a Level 1C GRD file and brings it into a format ready
for analysis. It is based on ESA's Sentinel Application Platform
(SNAP). The applied processing steps are:

* Value conversion to dB
* Speckle filtering (using a median filter)
* Creation of a land-sea mask
* Format conversion to GeoTIFF
* Apply terrain correction 


## Requirements

 1. [docker](https://docs.docker.com/install/).
 2. [GNU make](https://www.gnu.org/software/make/).
 3. [Python](https://python.org/downloads): version >= 3.5.

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

 1. [docker](https://docs.docker.com/install/).
 2. [GNU make](https://www.gnu.org/software/make/).
 3. [Python](https://python.org/downloads): version >= 3.5.

## Usage

### Clone the repository in a given `<directory>`

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

You can additionaly specifiy a custom tag for your image (default tag
is `snap-polarimetric:latest`):

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
```bash
make push UID=<UID>
```
Note that if you specified a custom docker tag when you built the image, you
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

### Run the processing block locally

#### Configure the job

To run the image locally you need first to configure the job with the
parameters specific to this block. Create a  `params.json` like this:

```js
{
  "polarisations": <array polarizations>,
  "mask": <array mask type>,
  "tcorrection": <boolean>
}
```
where:

`<array polarizations>`: JS array of possible polarizations: `"VV"`,
`"VH"`, `"HV"`, `"HH"`. 
`<array of mask type>`: JS array of possible mask `"sea"` or `"land"`.
`<boolean>`: `true` or `false` stating if terrain correction is to be done.

Here is an example `params.json`:

```js
{
  "polarisations": ["VV"],
  "mask": ["sea"],
  "tcorrection": false
}
```
#### Get the data

A image is needed for the block to run. Such image can be obtained by
creating a workflow with a single **Sentinel 1 L1C GRD ** data block
and download the the result.

Then create the directory `/tmp/e2e_snap_polarimetric/`:

```bash
mkdir /tmp/e2e_snap_polarimetric
```

Now untar the tarball with the result in that directory:

```bash
tar -C /tmp/e2e_snap_polarimetric -zxvf <downloaded tarball>
```
#### Run the block

```bash
make run
```
 
If set a custom dpcker tag then the command ro run the block is:

```bash
make run DOCKER_TAG=<docker tag>
```

### Local development
 
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

This project uses [pytest](https://docs.pytest.org/en/latest/) for
testing.  To run the tests, first create two empty `/tmp/input/` and
`/tmp/output` directories. The output will be written to the
`/tmp/output/` directory.  Finally, to run the test do as following:

```bash
cd snap-polarimetric/blocks/snap-polarimetric/
./test.sh
```

Now you need to [build](#build-the-docker-images) and 
[run](#run-the-processing-block-locally) the block locally.

