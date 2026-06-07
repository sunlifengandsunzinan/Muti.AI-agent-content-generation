#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Stage 1.5: Analyze new videos vs existing summaries"""
import json

# 1. Load search results
with open('skills/douyin-search/search_results/search_20260601_230504.json', encoding='utf8') as f:
    data = json.load(f)

# Collect all unique video URLs from all keywords
seen = set()
new_videos = []
for kw, items in data['results'].items():
    for item in items:
        url = item.get('url', '')
        if url and url not in seen:
            seen.add(url)
            new_videos.append({
                'url': url,
                'aweme_id': item.get('aweme_id', ''),
                'title': item.get('title', ''),
                'author': item.get('author', '')
            })

print(f'Total unique videos from search: {len(new_videos)}')

# 2. Load existing summaries
with open('moto/data/raw/doubao_summaries.json', encoding='utf8') as f:
    summaries = json.load(f)

existing_urls = set()
for s in summaries['items']:
    existing_urls.add(s.get('video_url', ''))

# 3. Filter out already summarized
to_process = [v for v in new_videos if v['url'] not in existing_urls]
print(f'Already summarized: {len(existing_urls)}')
print(f'New videos to process: {len(to_process)}')
print()

for i, v in enumerate(to_process[:20]):
    print(f'  [{i}] {v["author"]}: {v["title"][:40]} | {v["url"][:55]}')
if len(to_process) > 20:
    print(f'  ... and {len(to_process)-20} more')

# Save for next step
output = {'to_process': to_process, 'total_new': len(to_process)}
with open('_tmp_pending_videos.json', 'w', encoding='utf8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)
print(f'\nSaved {len(to_process)} pending videos to _tmp_pending_videos.json')
