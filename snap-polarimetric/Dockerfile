FROM interstellar-base-python3-snap

WORKDIR /block

COPY gpt.vmoptions /usr/local/snap/bin/
COPY src/ /block/src
COPY requirements.txt /block

RUN pip3 install -r requirements.txt

ENV LD_LIBRARY_PATH="."

ARG manifest
LABEL "up42_manifest"=$manifest

CMD ["python3", "/block/src/run.py"]
