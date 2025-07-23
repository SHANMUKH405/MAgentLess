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
# 3) Where your C++ benchmarks live
#
export FOLDER_NAME=validation-dataset
export SWEBENCH_LANG=cpp

#
# 4) Drive everything from this JSONL
#
export DATASET=local_json
export SPLIT=$TARGET_ID
export INPUT_JSONL=data/local_json_${TARGET_ID}.jsonl

#
# 5) Where we dump our structure JSON
#
export PROJECT_FILE_LOC=structure

#
# 6) (Re)generate *just* this one structure
#
python script/generate_structure.py \
  --bench_list $INPUT_JSONL \
  --output_dir $PROJECT_FILE_LOC \
  --playground playground

ls -lh $PROJECT_FILE_LOC/${TARGET_ID}.json

#
# 7) Create a simple localization file for the repair stage
#
mkdir -p results/${FOLDER_NAME}/edit_location_samples

# Create a simple localization file that points to the original.cpp file
cat > results/${FOLDER_NAME}/edit_location_samples/loc_outputs.jsonl << 'EOF'
{"instance_id": "benchmark_674", "found_files": ["benchmarks/benchmark_674/original.cpp"], "found_edit_locs": {"benchmarks/benchmark_674/original.cpp": ["1-50"]}}
EOF

#
# 8) Run repair stage with Ollama backend
#
echo "Running repair stage with Ollama backend..."
python agentless/repair/repair.py \
  --loc_file results/${FOLDER_NAME}/edit_location_samples/loc_outputs.jsonl \
  --output_folder results/${FOLDER_NAME}/repair_sample_1 \
  --model codellama:7b \
  --backend ollama \
  --max_samples 5

#
# 9) Apply the best patch to create agent_optimized.cpp
#
echo "Applying the best patch to create agent_optimized.cpp..."
python -c "
import json
import os
import re

# Read the repair outputs
repair_file = 'results/${FOLDER_NAME}/repair_sample_1/output.jsonl'
if os.path.exists(repair_file):
    with open(repair_file, 'r') as f:
        repairs = [json.loads(line) for line in f if line.strip()]
    
    if repairs:
        best_repair = repairs[0]
        response = best_repair.get('response', '')
        
        # Try to extract code from the response
        if '```cpp' in response:
            # Extract code between ```cpp and ```
            start = response.find('```cpp') + 6
            end = response.find('```', start)
            if end != -1:
                code_content = response[start:end].strip()
            else:
                code_content = response[start:].strip()
        elif '```' in response:
            # Extract code between ``` and ```
            start = response.find('```') + 3
            end = response.find('```', start)
            if end != -1:
                code_content = response[start:end].strip()
            else:
                code_content = response[start:].strip()
        else:
            code_content = response
        
        # Write the optimized file
        output_path = f'repo/validation-dataset/benchmarks/{TARGET_ID}/agent_optimized.cpp'
        with open(output_path, 'w') as f:
            f.write(code_content)
        print(f'✅ Created {output_path}')
        print(f'Generated {len(code_content)} characters of optimized code')
    else:
        print('❌ No repairs found in output.jsonl')
else:
    print(f'❌ Repair file not found: {repair_file}')
" 