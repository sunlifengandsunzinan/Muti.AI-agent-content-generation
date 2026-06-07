#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json

search_file = 'skills/douyin-search/search_results/search_20260601_230504.json'
with open(search_file, 'r', encoding='utf8') as f:
    search_data = json.load(f)

results = search_data['results']
total_videos = 0
for k, v in results.items():
    total_videos += len(v)
    print(f'  [{k}]: {len(v)} 条')
print(f'总计: {total_videos} 条')

# Show first 3 items sample
items = []
for k, v in results.items():
    for item in v:
        items.append(item)
print(f'\nItems list: {len(items)}')
if items:
    item = items[0]
    print(f'Item keys: {list(item.keys())}')
    print(f'Sample item:')
    for k in item:
        print(f'  {k}: {str(item[k])[:80]}')

summaries_file = 'moto/data/raw/doubao_summaries.json'
with open(summaries_file, 'r', encoding='utf8') as f:
    summaries = json.load(f)
items2 = summaries['items']
print(f'\n=== 已有总结: {len(items2)} 条 ===')
for i, item in enumerate(items2):
    print(f'  [{i}] keys: {list(item.keys()) if isinstance(item, dict) else type(item)}')
    if isinstance(item, dict):
        print(f'       author={item.get("author","")}, title={str(item.get("title",""))[:30]}')
        print(f'       video_url={str(item.get("video_url",""))[:60]}')
    break
