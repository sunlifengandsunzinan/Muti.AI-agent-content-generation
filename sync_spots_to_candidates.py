#!/usr/bin/env python3
"""Sync douyin_spots.json -> candidate_spots.json"""
import json, os

SPOTS_FILE = r"D:\moto\data\raw\douyin_spots.json"
CANDIDATE_FILE = r"D:\moto\data\normalized\candidate_spots.json"

# 读取现有点位
spots = json.load(open(SPOTS_FILE, encoding="utf-8"))

# 读取现有候选
if os.path.exists(CANDIDATE_FILE):
    existing = json.load(open(CANDIDATE_FILE, encoding="utf-8"))
else:
    existing = []

existing_slugs = {s.get("slug", "") for s in existing if isinstance(s, dict)}
new_count = 0

for spot in spots:
    slug = spot.get("slug", "")
    if slug in existing_slugs:
        continue
    
    # 补全 _candidate_card 需要的字段
    spot.setdefault("summary", spot.get("name", ""))
    spot.setdefault("confidence_score", 5)
    spot.setdefault("source_count", 1)
    spot.setdefault("review_href", f'/moto/spots/collect?candidate={slug}')
    
    existing.append(spot)
    existing_slugs.add(slug)
    new_count += 1

if new_count > 0:
    json.dump(existing, open(CANDIDATE_FILE, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

print(f"新增 {new_count} 条，候选队列共 {len(existing)} 条")
