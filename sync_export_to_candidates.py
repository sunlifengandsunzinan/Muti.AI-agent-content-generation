#!/usr/bin/env python3
"""将 openclaw_export.json 数据转为候选格式写入 candidate_spots.json"""
import sys, json, os
sys.path.insert(0, r"D:\moto")

from scripts.adapt_openclaw_candidates import adapt_openclaw_candidate
from scripts.run_local_social_collection import read_json_list, write_json, CANDIDATE_QUEUE_PATH

EXPORT_PATH = r"D:\moto\data\raw\openclaw_export.json"

# 读取 export 数据
export = json.load(open(EXPORT_PATH, encoding="utf-8"))
items = export.get("items", [])
print(f"export 数据: {len(items)} 条")

# 转换为适配器输入格式
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
        "summary": name,
        "description": name,
        "keywords": ["摩旅", "辽宁"],
        "tags": [],
        "imageUrls": [],
        "text": name,
    }
    converted.append(entry)

print(f"转换后: {len(converted)} 条")

# 用适应器处理
candidates = []
for c in converted:
    try:
        cand = adapt_openclaw_candidate(c)
        candidates.append(cand)
    except Exception as e:
        print(f"  SKIP: {str(e)[:60]}")

print(f"适配后候选: {len(candidates)} 条")
if candidates:
    # 读取已有候选
    existing = read_json_list(CANDIDATE_QUEUE_PATH)
    print(f"已有候选: {len(existing)} 条")
    
    existing_slugs = {s.get("slug", "") for s in existing if isinstance(s, dict)}
    new_count = 0
    for c in candidates:
        slug = c.get("slug", "")
        if slug not in existing_slugs:
            existing.append(c)
            existing_slugs.add(slug)
            new_count += 1
    
    # 写入候选队列
    os.makedirs(os.path.dirname(CANDIDATE_QUEUE_PATH), exist_ok=True)
    with open(CANDIDATE_QUEUE_PATH, "w", encoding="utf-8") as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)
    
    print(f"新增: {new_count} 条, 总计: {len(existing)} 条")

# 验证
from app.services import get_candidate_spots
cands = get_candidate_spots()
print(f"审批页候选队列: {len(cands)} 条")
