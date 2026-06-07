#!/usr/bin/env python3
"""Copy candidates with name field to normalized path"""
import json

src_path = r"D:\moto\data\raw\openclaw_candidates.json"
dst_path = r"D:\moto\data\normalized\candidate_spots.json"

src = json.load(open(src_path, encoding="utf-8"))
print(f"Source: {len(src)} items")

has_name = all("name" in c for c in src)
print(f"All have name: {has_name}")

if not has_name:
    for c in src:
        if "name" not in c:
            c["name"] = c.get("raw_name", c.get("summary_hint", ""))[:80]

json.dump(src, open(dst_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"Written {len(src)} to candidate_spots.json")
