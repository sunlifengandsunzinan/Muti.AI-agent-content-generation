# -*- coding: utf-8 -*-
import json
try:
    with open(r'D:\摩旅数据采集目录\comment_insights_20260607_142934.json', encoding='utf-8-sig') as f:
        data = json.load(f)
except:
    with open(r'D:\摩旅数据采集目录\comment_insights_20260607_142934.json', encoding='utf-8') as f:
        data = json.load(f)
print(f'类型: {type(data).__name__}')
if isinstance(data, list):
    print(f'共 {len(data)} 条')
    for i, r in enumerate(data[:15]):
        print(f'{i+1}. {str(r)[:120]}')
elif isinstance(data, dict):
    for k in list(data.keys())[:10]:
        v = data[k]
        print(f'{k}: {type(v).__name__} | {str(v)[:100]}')
