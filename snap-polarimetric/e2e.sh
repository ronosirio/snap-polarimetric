#!/bin/bash
set -e

echo "Running End to End test for SNAP polarimetric preprocessing"

# Test setup: only fetch input data if necessary, but make sure output directory is clean
tmp_dir=/tmp/e2e_snap_polarimetric
input_dir="$tmp_dir"/input
output_dir="$tmp_dir"/output

echo "Deleting "$output_dir
rm -rf $output_dir

test_file_uuid=aa036ac6-46f8-4ac4-80b4-7b7cb2dc01f1
test_file_dir=$input_dir/$test_file_uuid

echo $test_file_dir

if [ -d "$test_file_dir" ]; then
  echo "Test input data already exist; not re-downloading"
else
  echo "Downloading test data"
  mkdir -p $input_dir
  gsutil -m cp -r gs://blocks-e2e-testing/$test_file_uuid $input_dir
  cp $(pwd)/tests/test_data/data.json $input_dir
fi

docker run -e 'UP42_TASK_PARAMETERS={"polarisations": ["VV"]}' -v $tmp_dir:/tmp -it snap-polarimetric

json_file="$output_dir/data.json"

bbox=$(cat $json_file | jq '.features[0].bbox')
echo "Output json has bbox set to "$bbox


