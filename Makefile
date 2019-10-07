## Configuration for Makefile.
SRC := blocks/snap-polarimetric
MANIFEST_JSON := $(SRC)/UP42Manifest.json
UP42_DOCKERFILE := $(SRC)/Dockerfile
DOCKER_TAG := snap-polarimetric
## Extra images needed by the block image.
LIBS_DIR := $(SRC)/libs
ESA_SNAP_DOCKERFILE := $(LIBS_DIR)/Dockerfile-esa-snap
UP42_SNAP_DOCKERFILE := $(LIBS_DIR)/Dockerfile-up42-snap

VALIDATE_ENDPOINT := https://api.up42.com/validate-schema/block
REGISTRY := registry.up42.com
CURL := curl
DOCKER := docker

build-image-esa-snap:
	$(DOCKER) build -f $(ESA_SNAP_DOCKERFILE) -t up42-esa-snap .

build-image-up42-snap:
	$(DOCKER) build -f $(UP42_SNAP_DOCKERFILE) -t up42-snap .

build: $(MANIFEST_JSON) build-image-esa-snap build-image-up42-snap
ifdef UID
	$(DOCKER) build --build-arg manifest="$$(cat $<)" -f $(UP42_DOCKERFILE) -t $(REGISTRY)/$(UID)/$(DOCKER_TAG) .
else
	$(DOCKER) build --build-arg manifest="$$(cat $<)" -f $(UP42_DOCKERFILE) -t $(DOCKER_TAG) .
endif

clean:
	find . -name "__pycache__" -exec rm -rf {} +
	find . -name ".mypy_cache" -exec rm -rf {} +
	find . -name ".pytest_cache" -exec rm -rf {} +
	find . -name ".coverage" -exec rm -f {} +

validate: $(MANIFEST_JSON)
	$(CURL) -X POST -H 'Content-Type: application/json' -d @$^ $(VALIDATE_ENDPOINT)

push:
	$(DOCKER) push $(REGISTRY)/$(UID)/$(DOCKER_TAG)

login:
	$(DOCKER) login -u $(USER) https://$(REGISTRY)

install:
	cd $(SRC) && ./setup.sh && cd $(CURDIR)

test:
	cd $(SRC) && ./test.sh && cd $(CURDIR)

e2e:
	python e2e.py

.PHONY: build login push test install e2e
