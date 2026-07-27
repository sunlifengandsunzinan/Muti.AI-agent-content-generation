# -*- coding: utf-8 -*-
import json
with open(r'D:\摩旅数据采集目录\route_templates_merged.json', encoding='utf-8-sig') as f:
    data = json.load(f)
count = len(data)
print(f'共 {count} 条路线')
# 找 331/丹东/集安 相关的
for r in data:
    name = r.get('name', '')
    desc = r.get('description', '')
    rname = r.get('route_name', '')
    tags = r.get('tags', [])
    wps = r.get('waypoints', [])
    days = r.get('days_plan', [])
    if any(kw in name+desc+rname+str(tags) for kw in ['331','丹东','集安','边境']):
        print(f'\n=== {r.get("name", r.get("route_name",""))} ===')
        print(f'描述: {desc[:200]}')
        print(f'标签: {tags}')
        print(f'途经点: {len(wps)} 个')
        for w in wps[:10]:
            print(f'  - {w}')
        print(f'天数：{days}')
        print(f'详细日程: {len(days) if isinstance(days, list) else "N/A"} 天')
