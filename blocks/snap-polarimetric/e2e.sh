#!/bin/bash
set -e

echo "Running End to End test for SNAP polarimetric preprocessing"

# Test setup: only fetch input data if necessary, but make sure output directory is clean
tmp_dir=/tmp/e2e_snap_polarimetric
input_dir="$tmp_dir"/input
output_dir="$tmp_dir"/output

echo "Deleting "$output_dir
rm -rf $output_dir

test_file_uuid=<id>
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