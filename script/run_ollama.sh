#!/usr/bin/env bash
set -euxo pipefail

#
# 1) Set up PYTHONPATH & Ollama configuration
#
export PYTHONPATH="$(pwd)"
export OPENAI_MODEL=codellama:7b
export OPENAI_BASE_URL=http://localhost:11434/v1
export OPENAI_API_KEY=ollama

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
# 9) Run all localization & repair stages with Ollama backend
#
echo "Running localization stages with Ollama backend..."
python agentless/fl/localize.py \
  --output_folder results/${FOLDER_NAME}/related_elements \
  --related_level \
  --model codellama:7b \
  --backend ollama \
  --dataset local_json \
  --split $TARGET_ID \
  --target_id $TARGET_ID

python agentless/fl/localize.py \
  --output_folder results/${FOLDER_NAME}/edit_location_samples \
  --fine_grain_line_level \
  --model codellama:7b \
  --backend ollama \
  --dataset local_json \
  --split $TARGET_ID \
  --target_id $TARGET_ID

python agentless/fl/localize.py \
  --output_folder results/${FOLDER_NAME}/file_level_irrelevant \
  --file_level \
  --irrelevant \
  --model codellama:7b \
  --backend ollama \
  --dataset local_json \
  --split $TARGET_ID \
  --target_id $TARGET_ID

python agentless/fl/localize.py \
  --output_folder results/${FOLDER_NAME}/file_level_combined \
  --file_level \
  --model codellama:7b \
  --backend ollama \
  --dataset local_json \
  --split $TARGET_ID \
  --target_id $TARGET_ID

python agentless/fl/localize.py \
  --output_folder results/${FOLDER_NAME}/file_level \
  --file_level \
  --model codellama:7b \
  --backend ollama \
  --dataset local_json \
  --split $TARGET_ID \
  --target_id $TARGET_ID

echo "Running repair stage with Ollama backend..."
python agentless/repair/repair.py \
  --loc_file results/${FOLDER_NAME}/edit_location_samples/loc_outputs.jsonl \
  --output_folder results/${FOLDER_NAME}/repair_sample_1 \
  --model codellama:7b \
  --backend ollama \
  --max_samples 10 \
  --str_replace_format

python agentless/repair/repair.py \
  --loc_file results/${FOLDER_NAME}/edit_location_samples/loc_outputs.jsonl \
  --output_folder results/${FOLDER_NAME}/repair_sample_2 \
  --model codellama:7b \
  --backend ollama \
  --max_samples 10 \
  --str_replace_format

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

#
# 11) Apply the best patch to create agent_optimized.cpp
#
echo "Applying the best patch to create agent_optimized.cpp..."
python -c "
import json
import os
import re

# Read the final patches
with open('results/${FOLDER_NAME}/final_patches.jsonl', 'r') as f:
    patches = [json.loads(line) for line in f if line.strip()]

if patches:
    best_patch = patches[0]
    patch_content = best_patch.get('patch', '')
    
    # Extract the file path and content from the patch
    if 'diff --git' in patch_content:
        # Parse diff format
        lines = patch_content.split('\n')
        file_path = None
        new_content = []
        in_hunk = False
        
        for line in lines:
            if line.startswith('diff --git'):
                # Extract file path from diff header
                parts = line.split()
                if len(parts) >= 3:
                    file_path = parts[2].replace('b/', '')
            elif line.startswith('@@'):
                in_hunk = True
            elif in_hunk and not line.startswith('-') and not line.startswith('+'):
                if line.startswith(' '):
                    new_content.append(line[1:])
                else:
                    new_content.append(line)
            elif in_hunk and line.startswith('+'):
                new_content.append(line[1:])
        
        if file_path and new_content:
            # Write the optimized file
            output_path = f'repo/validation-dataset/benchmarks/{TARGET_ID}/agent_optimized.cpp'
            with open(output_path, 'w') as f:
                f.write('\n'.join(new_content))
            print(f'✅ Created {output_path}')
        else:
            print('❌ Could not parse patch content')
    else:
        # Direct content replacement
        output_path = f'repo/validation-dataset/benchmarks/{TARGET_ID}/agent_optimized.cpp'
        with open(output_path, 'w') as f:
            f.write(patch_content)
        print(f'✅ Created {output_path}')
else:
    print('❌ No patches found in final_patches.jsonl')
" 