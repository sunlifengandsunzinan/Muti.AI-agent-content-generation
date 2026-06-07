# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import json

with open(r'D:\摩旅数据采集\辽宁摩旅路线_评分中间结果.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

routes = data['routes']
seen = {}
for r in routes:
    nid = r['note_id']
    seen[nid] = seen.get(nid, 0) + 1

dupes = {k:v for k,v in seen.items() if v > 1}
print("重复笔记: {} 组".format(len(dupes)))
for nid, count in dupes.items():
    r = [x for x in routes if x['note_id']==nid][0]
    title_clean = r['basic_info']['title'][:30]
    print("  {} (ID:{}) 出现{}次".format(title_clean, nid, count))

print("\n总合格: {}, 去重后: {}".format(len(routes), len(seen)))
scores = [r['score'] for r in routes]
print("分数范围: {:.1f} ~ {:.1f}".format(min(scores), max(scores)))
