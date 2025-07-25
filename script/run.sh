#!/usr/bin/env bash
set -euxo pipefail

#
# 1) Load your OpenAI key + set up PYTHONPATH & model
#
source script/api_key.sh
export PYTHONPATH="$(pwd)"
export OPENAI_MODEL=gpt-4o-mini-2024-07-18

#
# 2) Pick your one benchmark
#
export TARGET_ID=benchmark_674

#
# 3) Sampling & pipeline parameters
#
export NJ=50
export NUM_SETS=2
export NUM_SAMPLES_PER_SET=2
export NUM_REPRODUCTION=0

#
# 4) Where your C++ benchmarks live
#
export FOLDER_NAME=validation-dataset
export SWEBENCH_LANG=cpp

#
# 5) Drive everything from this JSONL
#
export DATASET=local_json
export SPLIT=$TARGET_ID
export INPUT_JSONL=data/local_json_${TARGET_ID}.jsonl

#
# 6) Where we dump our structure JSON
#
export PROJECT_FILE_LOC=structure

#
# 7) (Re)generate *just* this one structure
#
python script/generate_structure.py \
  --bench_list $INPUT_JSONL \
  --output_dir $PROJECT_FILE_LOC \
  --playground playground

ls -lh $PROJECT_FILE_LOC/${TARGET_ID}.json

#
# 8) Stub out any missing loc/repair outputs so the pipeline never crashes
#
mkdir -p results/${FOLDER_NAME}/{related_elements,edit_location_samples,file_level_irrelevant,file_level_combined,file_level}
: > results/${FOLDER_NAME}/related_elements/loc_outputs.jsonl
: > results/${FOLDER_NAME}/edit_location_samples/loc_outputs.jsonl
: > results/${FOLDER_NAME}/file_level_irrelevant/loc_outputs.jsonl
: > results/${FOLDER_NAME}/file_level/loc_outputs.jsonl

for i in 1 2; do
  mkdir -p results/${FOLDER_NAME}/repair_sample_${i}
  : > results/${FOLDER_NAME}/repair_sample_${i}/output.jsonl
done

#
# 9) Run all localization & repair stages
#
./script/localization1.1.sh
./script/localization1.2.sh
./script/localization1.3.sh
./script/localization1.4.sh
./script/localization2.1.sh
./script/localization3.1.sh
./script/localization3.2.sh

./script/repair.sh

#
# 10) Rerank the two repair_sample outputs and pick a winner
#
PATCH_FOLDERS="results/${FOLDER_NAME}/repair_sample_1,results/${FOLDER_NAME}/repair_sample_2"
python agentless/repair/rerank.py \
  --patch_folder $PATCH_FOLDERS \
  --target $TARGET_ID \
  --num_samples $NUM_SAMPLES_PER_SET \
  --deduplicate \
  --output_file results/${FOLDER_NAME}/final_patches.jsonl

echo "✅ Done!  Final patch for ${TARGET_ID} → results/${FOLDER_NAME}/final_patches.jsonl"
ls -lh results/${FOLDER_NAME}/final_patches.jsonl
