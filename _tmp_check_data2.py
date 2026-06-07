#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json

search_file = 'skills/douyin-search/search_results/search_20260601_230504.json'
with open(search_file, 'r', encoding='utf8') as f:
    search_data = json.load(f)
print(f'=== 搜索结果 ===')
print(f'Type: {type(search_data).__name__}')
print(f'Keys: {list(search_data.keys())}')
for k, v in search_data.items():
    if isinstance(v, list):
        print(f'  {k}: list[{len(v)}]')
        if v:
            item = v[0]
            print(f'    item type: {type(item).__name__}')
            if isinstance(item, dict):
                for kk, vv in item.items():
                    print(f'      {kk}: {str(vv)[:80]}')
    elif isinstance(v, dict):
        print(f'  {k}: dict[{len(v)} keys] {list(v.keys())[:5]}')
    else:
        print(f'  {k}: {type(v).__name__} = {str(v)[:100]}')

summaries_file = 'moto/data/raw/doubao_summaries.json'
try:
    with open(summaries_file, 'r', encoding='utf8') as f:
        summaries = json.load(f)
    print(f'\n=== 已有总结 ===')
    print(f'Type: {type(summaries).__name__}')
    if isinstance(summaries, list):
        print(f'Length: {len(summaries)}')
        if summaries:
            item = summaries[0]
            print(f'Item type: {type(item).__name__}')
            if isinstance(item, dict):
                for k in item:
                    print(f'  {k}: {str(item[k])[:80]}')
            elif isinstance(item, str):
                print(f'  Item content: {item[:200]}')
    elif isinstance(summaries, dict):
        print(f'Keys: {list(summaries.keys())}')
except Exception as e:
    print(f'\nError: {e}')
