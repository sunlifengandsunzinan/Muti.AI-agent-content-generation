#!/usr/bin/env python3
"""Test search_live_items for douyin"""
import sys
sys.path.insert(0, r"D:\moto")
from scripts.run_local_social_collection import search_live_items, fetch_remote_text

task = {"platform": "douyin", "keyword": "辽宁摩旅路线推荐", "province": "辽宁", "limit": 3}
items = search_live_items(task)
print("Items found:", len(items))
for i, item in enumerate(items):
    name = item.get("name", "?")[:50]
    src = item.get("sourceUrl", "?")[:60]
    print(f"  {i}: {name} | {src}")

# Also test directly fetching douyin search
url = "https://www.douyin.com/search/辽宁摩旅路线推荐?type=general"
resp = fetch_remote_text(url, timeout_seconds=15)
print(f"\nFetch search page: {len(resp)} chars")
print(resp[:500])
