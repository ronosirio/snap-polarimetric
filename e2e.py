"""
End-to-end test: Fetches data, creates output, stores it in /tmp and checks if output
is valid.
"""
from pathlib import Path
import os

import shutil
import geojson

if __name__ == "__main__":
    TESTNAME = "e2e_snap-polarimetric"
    TEST_DIR = Path("/tmp") / TESTNAME
    TEST_DIR.mkdir(parents=True, exist_ok=True)
    INPUT_DIR = TEST_DIR / "input"
    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    FILES_TO_DELETE = Path(TEST_DIR / "output").glob("*")
    for file_path in FILES_TO_DELETE:
        file_path.unlink()

    # Download file from gsutil
    os.system(
        "gsutil -m cp -r gs://floss-blocks-e2e-testing/e2e_snap_polarimetric/* %s"
        % INPUT_DIR
    )

    RUN_CMD = (
        """docker run -v %s:/tmp \
                 -e 'UP42_TASK_PARAMETERS={"bbox": [14.558086395263674, 
                 53.4138293218823, 14.584178924560549, 53.433673900512616], "mask": null, "tcorrection": false,\
                    "polarisations": ["VV"], "clip_to_aoi": true}' \
                  -it snap-polarimetric"""
        % TEST_DIR
    )

    os.system(RUN_CMD)

    # Print out bbox of one tile
    GEOJSON_PATH = TEST_DIR / "output" / "data.json"

    with open(str(GEOJSON_PATH)) as f:
        FEATURE_COLLECTION = geojson.load(f)

    print(FEATURE_COLLECTION.features[0].bbox)

    OUTPUT_SNAP = (
        TEST_DIR
        / "output"
        / Path(FEATURE_COLLECTION.features[0].properties["up42.data_path"])
    )

    print(OUTPUT_SNAP)

    assert OUTPUT_SNAP.exists()
