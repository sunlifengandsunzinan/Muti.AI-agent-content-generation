#!/usr/bin/env python3
import json

# Read search results
with open('skills/douyin-search/search_results/search_20260601_231459.json', 'r', encoding='utf-8') as f:
    search_data = json.load(f)

# Read existing summaries
with open('moto/data/raw/doubao_summaries.json', 'r', encoding='utf-8') as f:
    summary_data = json.load(f)

# Collect all searched video IDs
all_search_entries = []
seen_ids = set()
for kw, items in search_data['results'].items():
    for item in items:
        aid = item['aweme_id']
        if aid not in seen_ids:
            seen_ids.add(aid)
            all_search_entries.append(item)

# Collect already summarized URLs and IDs
existing_ids = set()
existing_urls = set()
for d in summary_data.get('items', []):
    url = d.get('video_url', '')
    existing_urls.add(url)
    aid = url.split('/')[-1] if url else ''
    if aid:
        existing_ids.add(aid)

# Find new entries
new_entries = [e for e in all_search_entries if e['aweme_id'] not in existing_ids]

print(f"搜索总视频: {len(all_search_entries)}")
print(f"去重搜索视频: {len(seen_ids)}")
print(f"已有总结: {len(existing_ids)}")
print(f"新视频: {len(new_entries)}")
print()
for e in new_entries[:10]:
    print(f"  {e['url']} | {e.get('title','')[:50]} | {e.get('author','')}")

# Also check if any existing are in the new search
print(f"\n已有总结中在搜索范围内的: {len([u for u in existing_urls if any(u.split('/')[-1] in e['aweme_id'] for e in all_search_entries) or u in {e['url'] for e in all_search_entries}])}")
