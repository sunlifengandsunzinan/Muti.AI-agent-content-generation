#!/usr/bin/env python3
import json

path = 'moto/data/raw/doubao_summaries.json'
with open(path, 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Keys: {list(data.keys())}")
print(f"total: {data.get('total')}")
print(f"source: {data.get('source')}")
print(f"exported_at: {data.get('exported_at')}")

items = data.get('items', [])
print(f"items count: {len(items)}")
for i, d in enumerate(items[:20]):
    vid = d.get('video_url', '')
    print(f"  [{i}] {d.get('author','?')} | {d.get('title','?')[:40]} | {d.get('summary_at','')} | {vid}")
