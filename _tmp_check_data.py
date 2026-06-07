#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, os, sys

# Check search results
search_file = 'skills/douyin-search/search_results/search_20260601_230504.json'
with open(search_file, 'r', encoding='utf8') as f:
    search_data = json.load(f)
print(f'=== 搜索结果: {len(search_data)} 条 ===')
if isinstance(search_data, list):
    for i, item in enumerate(search_data[:5]):
        url = item.get('url', item.get('video_url', item.get('link', '?')))
        title = item.get('title', '?')
        author = item.get('author', item.get('author_name', '?'))
        print(f'  [{i}] {author}: {title[:40]} | {url[:60]}')
    print(f'  ... ({len(search_data)} total)')

# Check existing summaries
summaries_file = 'moto/data/raw/doubao_summaries.json'
try:
    with open(summaries_file, 'r', encoding='utf8') as f:
        summaries = json.load(f)
    print(f'\n=== 已有总结: {len(summaries)} 条 ===')
    for i, item in enumerate(summaries):
        print(f'  [{i}] {item.get("author","?")}: {item.get("title","?")[:30]} | {item.get("video_url","?")[:60]}')
except FileNotFoundError:
    print(f'\n=== 总结文件不存在，将创建新文件 ===')
    summaries = []
except json.JSONDecodeError:
    print(f'\n=== 总结文件格式错误，将重新创建 ===')
    summaries = []
