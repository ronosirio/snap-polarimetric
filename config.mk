# -*- mode: makefile-gmake ; mode: pabbrev; mode: electric-pair -*-
## Configuration for Makefile.
SRC := blocks/snap-polarimetric
MANIFEST_JSON := $(SRC)/UP42Manifest.json
UP42_DOCKERFILE := $(SRC)/Dockerfile
JOB_CONFIG := $(SRC)/params.json  
DOCKER_TAG := snap-polarimetric
DOCKER_RUN_OPTIONS := --mount type=bind,src=/tmp/e2e_snap_polarimetric/output,dst=/tmp/output --mount type=bind,src=/tmp/e2e_snap_polarimetric/input,dst=/tmp/input
## Extra images needed by the block image.
LIBS_DIR := $(SRC)/libs
ESA_SNAP_DOCKERFILE := $(LIBS_DIR)/Dockerfile-esa-snap
UP42_SNAP_DOCKERFILE := $(LIBS_DIR)/Dockerfile-up42-snap
