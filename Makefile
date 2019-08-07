# -*- mode: makefile-gmake -*-
include config.mk

DIR=$(CURDIR)

build-image-esa-snap:
	docker build -f $(ESA_SNAP_DOCKERFILE) -t up42-esa-snap .

build-image-up42-snap:
	docker build -f $(UP42_SNAP_DOCKERFILE) -t up42-snap .

debug:
	@echo $(ESA_SNAP_DOCKERFILE)

.PHONY: build-image-esa-nap
