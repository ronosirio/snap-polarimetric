FROM up42-snap:latest

WORKDIR /block

COPY requirements.txt /block
RUN pip3 install -r requirements.txt

COPY src/ /block/src

ENV LD_LIBRARY_PATH="."

ARG manifest
LABEL "up42_manifest"=$manifest

CMD ["python3", "/block/src/run.py"]
