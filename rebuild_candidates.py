#!/usr/bin/env python3
"""Direct convert export to candidates with name field"""
import sys, json
sys.path.insert(0, r"D:\moto")

from scripts.adapt_openclaw_candidates import adapt_openclaw_candidate
from app.services.candidate_spots import get_candidate_spots

EXPORT_PATH = r"D:\moto\data\raw\openclaw_export.json"
CANDIDATE_PATH = r"D:\moto\data\raw\openclaw_candidates.json"
NORM_PATH = r"D:\moto\data\normalized\candidate_spots.json"

export = json.load(open(EXPORT_PATH, encoding="utf-8"))
items = export.get("items", [])
print(f"Export: {len(items)} items")

# 转格式喂给适配器
converted = []
for item in items:
    name = item.get("name", "")
    if not name:
        continue
    entry = {
        "platform": "douyin",
        "sourceUrl": "",
        "title": name,
        "name": name,
        "author": item.get("author", ""),
        "owner": item.get("author", ""),
        "summary": name[:200],
        "description": name,
        "keywords": ["摩旅", "辽宁"],
        "tags": [],
        "imageUrls": [],
        "text": name,
        "likes": item.get("likes", 0),
        "date": item.get("date", ""),
    }
    converted.append(entry)

candidates = []
for c in converted:
    try:
        cand = adapt_openclaw_candidate(c)
        candidates.append(cand)
    except Exception as e:
        print(f"  SKIP: {str(e)[:80]}")

print(f"Adapted: {len(candidates)}")

# 检查所有候选都有 name 字段
has_name = all("name" in c for c in candidates)
print(f"All have 'name': {has_name}")
if not has_name:
    # 补 name 字段
    for c in candidates:
        if "name" not in c:
            c["name"] = c.get("title", c.get("summary", ""))[:80]

# 写入候选文件
json.dump(candidates, open(CANDIDATE_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"Written to {CANDIDATE_PATH}")

# 测试
from app.services import get_candidate_spots
cands = get_candidate_spots()
print(f"get_candidate_spots(): {len(cands)}")
if cands:
    print(f"Sample keys: {list(cands[0].keys())}")
