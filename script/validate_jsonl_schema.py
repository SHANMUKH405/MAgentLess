#!/usr/bin/env python3
import json
import sys

EXPECTED = {
    "instance_id","org","repo","number","state",
    "title","body","base","resolved_issues",
    "fix_patch","test_patch","language",
    "docker_image","agent"
}

path = sys.argv[1]
with open(path) as f:
    for i, line in enumerate(f,1):
        data = json.loads(line)
        keys = set(data.keys())
        missing = EXPECTED - keys
        extra   = keys - EXPECTED
        if missing or extra:
            print(f"Line {i}: missing={missing}, extra={extra}")
        else:
            print(f"Line {i}: OK")
