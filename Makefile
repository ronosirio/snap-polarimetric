## Configuration for Makefile.
SRC := .
MANIFEST_JSON := $(SRC)/UP42Manifest.json
UP42_DOCKERFILE := $(SRC)/Dockerfile
DOCKER_TAG := snap-polarimetric
DOCKER_VERSION := latest

VALIDATE_ENDPOINT := https://api.up42.com/validate-schema/block
REGISTRY := registry.up42.com
CURL := curl
DOCKER := docker

build: $(MANIFEST_JSON)
ifdef UID
	$(DOCKER) build --build-arg manifest="$$(cat $<)" -f $(UP42_DOCKERFILE) -t $(REGISTRY)/$(UID)/$(DOCKER_TAG):$(DOCKER_VERSION) .
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
	$(DOCKER) push $(REGISTRY)/$(UID)/$(DOCKER_TAG):$(DOCKER_VERSION)

login:
	$(DOCKER) login -u $(USER) https://$(REGISTRY)

install:
	./setup.sh

test:
	./test.sh

e2e:
	python e2e.py

.PHONY: build login push test install e2e
