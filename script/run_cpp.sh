#!/usr/bin/env bash
set -x

# load your OpenAI credentials and model
source script/api_key.sh

# make sure Python can see the MagentLess modules
export PYTHONPATH="$(pwd)"

# how many benchmarks to clone / parallel jobs
export NJ=50

# MagentLess settings
export FOLDER_NAME=cpp_experiment_01
export SWEBENCH_LANG=cpp
export PROJECT_FILE_LOC=structure         # optional cache of file‐list
export DATASET=local_json                 # tells it to use data/*.jsonl
export SPLIT=verified                     # our JSONL is the "verified" split

# now kick off the pipeline
./script/localization1.1.sh
./script/localization1.2.sh
./script/localization1.3.sh
./script/localization1.4.sh
./script/localization2.1.sh
./script/localization3.1.sh
./script/localization3.2.sh

./script/repair.sh

./script/selection3.1.sh
