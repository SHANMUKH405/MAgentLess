#!/usr/bin/env python3

import sys
import os
sys.path.append('.')

# Set the environment variable
os.environ['SWEBENCH_LANG'] = 'cpp'

from agentless.multilang.utils import load_local_json
from agentless.multilang.const import LANGUAGE

print(f"LANGUAGE: {LANGUAGE}")

# Load the data
data = load_local_json()
print(f"Loaded {len(data)} items")
for item in data:
    print(f"Instance ID: {item['instance_id']}")
    print(f"Repo: {item['repo']}")
    print(f"Base commit: {item['base_commit']}")
    print(f"Problem statement: {item['problem_statement'][:100]}...")
    print("---") 