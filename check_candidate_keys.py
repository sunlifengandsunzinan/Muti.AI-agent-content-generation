#!/usr/bin/env python3
"""Check candidate_spots.json for name field"""
import json

path = r"D:\moto\data\raw\openclaw_candidates.json"
with open(path, encoding="utf-8") as f:
    data = json.load(f)

if data:
    print(f"Total: {len(data)}")
    print(f"Keys: {list(data[0].keys())}")
    print(f"Has 'name': {'name' in data[0]}")
    print(f"Has 'title': {'title' in data[0]}")
    print(f"First item:")
    print(json.dumps(data[0], ensure_ascii=False, indent=2)[:600])
else:
    print("Empty")
