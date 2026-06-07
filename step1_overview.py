# -*- coding: utf-8 -*-
import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

with open(r'D:\摩旅数据采集\辽宁摩旅路线_全量分析.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"总条数: {len(data)}")
print(f"包含坐标的 (distance_km > 0): {sum(1 for d in data if d['route_analysis']['distance_km'] > 0)}")
print(f"辽宁省内: {sum(1 for d in data if d['qualification_assessment']['is_liaoning_related'])}")

# 打印前5条标题看看
for d in data[:5]:
    ra = d['route_analysis']
    title = d['basic_info']['title'][:30]
    wp = ra['waypoint_names']
    print(f"  {title} | {ra['distance_km']}km | 途经点: {wp}")
