#!/usr/bin/env python3
"""Debug candidate_spots keys"""
import json

path = r"D:\moto\data\raw\openclaw_candidates.json"
with open(path, encoding="utf-8") as f:
    data = json.load(f)

print(f"Total: {len(data)}")
if data and isinstance(data[0], dict):
    k = data[0].keys()
    print(f"Keys: {list(k)}")
    has_name = "name" in k
    has_title = "title" in k
    print(f"Has name: {has_name}, Has title: {has_title}")
    # if no name, check what's closest
    for candidate in data:
        if "name" not in candidate:
            print(f"Missing name in: {json.dumps(candidate, ensure_ascii=False)[:200]}")
            break
        else:
            print(f"Has name: {candidate['name'][:60]}")
            break
