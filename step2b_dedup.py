# -*- coding: utf-8 -*-
"""
Step 2b: 去重 - keep only highest-scoring entry per note_id
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import json

with open(r'D:\摩旅数据采集\辽宁摩旅路线_评分中间结果.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

routes = data['routes']

# Deduplicate: keep highest score per note_id
best_by_nid = {}
for r in routes:
    nid = r['note_id']
    if nid not in best_by_nid or r['score'] > best_by_nid[nid]['score']:
        best_by_nid[nid] = r

unique_routes = list(best_by_nid.values())
unique_routes.sort(key=lambda x: -x['score'])

# Re-rank
for i, r in enumerate(unique_routes):
    r['rank'] = i + 1

print("去重后路线数: {}".format(len(unique_routes)))
print("排名前10:")
for r in unique_routes[:10]:
    print("  #{} [{:.1f}/10] {} | {}km | 点赞{} 收藏{}".format(
        r['rank'], r['score'], r['basic_info']['title'][:35],
        r['route_analysis']['distance_km'], r['engagement']['likes'],
        r['engagement']['collects']))

# Save deduplicated
with open(r'D:\摩旅数据采集\辽宁摩旅路线_去重评分.json', 'w', encoding='utf-8') as f:
    json.dump({
        'total_raw': data['total_raw'],
        'liaoning_related': data['liaoning_related'],
        'has_route_info': data['has_route_info'],
        'qualified_count': len(unique_routes),
        'routes': unique_routes
    }, f, ensure_ascii=False, indent=2)

print("\n去重结果已保存: D:\\摩旅数据采集\\辽宁摩旅路线_去重评分.json")
