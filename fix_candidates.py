#!/usr/bin/env pytho3
"""Fix candidate_spots.json"""
import json, sys
sys.path.insert(0, r"D:\moto")

path = r"D:\moto\data\normalized\candidate_spots.json"
with open(path, "r", encoding="utf-8") as f:
    data = json.load(f)

for item in data:
    slug = item["slug"]
    item["review_href"] = "/moto/spots/collect?candidate=" + slug
    item["source_count"] = 1
    item.setdefault("summary", item.get("description", "")[:150])
    item.setdefault("confidence_score", 5)
    item.setdefault("status", "pending")

with open(path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

from app.services import get_candidate_spots, get_spot_collection_context
cands = get_candidate_spots()
print("Candidates:", len(cands))
ctx = get_spot_collection_context()
q = ctx.get("collect_wizard", {}).get("candidate_queue", [])
print("Queue:", len(q))
if q:
    print("First:", q[0])
