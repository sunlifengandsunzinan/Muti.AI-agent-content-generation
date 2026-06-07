#!/usr/bin/env python3
import json
import os

path = 'moto/data/raw/doubao_summaries.json'
if os.path.exists(path):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    if isinstance(data, list):
        print(f"已有总结: {len(data)} 条")
        for i, d in enumerate(data):
            vid = d.get('video_url', '')
            aid = d.get('aweme_id', '') or vid.split('/')[-1] if vid else ''
            print(f"  [{i}] {d.get('author','?')} | {d.get('title','?')[:40]} | {aid}")
    elif isinstance(data, dict):
        print(f"Keys: {list(data.keys())}")
else:
    print("文件不存在")
    os.makedirs('moto/data/raw', exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump([], f, ensure_ascii=False, indent=2)
    print("已创建空文件")
