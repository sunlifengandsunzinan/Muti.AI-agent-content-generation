#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
摩旅景点采集任务 v3
直接从预置城市景点库生成数据，持久化运行
"""
import json, os, sys, urllib.parse, time
from datetime import datetime

# 强制UTF-8输出解决GBK乱码
if hasattr(sys.stdout, 'buffer'):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

OUTPUT_FILE = r"D:\moto\data\raw\openclaw_export.json"

# 辽宁摩旅景点库
SPOTS = [
    {"city": "沈阳", "region": "辽中", "name": "沈阳北陵公园（清昭陵）", "kw": "北陵公园", "type": "scenic-spot", "route": "city-riverside"},
    {"city": "沈阳", "region": "辽中", "name": "沈阳东陵公园（清福陵）", "kw": "东陵公园", "type": "scenic-spot", "route": "city-riverside"},
    {"city": "沈阳", "region": "辽中", "name": "沈阳国家森林公园", "kw": "森林公园", "type": "scenic-spot", "route": "mountain"},
    {"city": "沈阳", "region": "辽中", "name": "沈阳棋盘山风景区", "kw": "棋盘山", "type": "scenic-spot", "route": "mountain"},
    {"city": "本溪", "region": "辽东", "name": "本溪水洞风景区", "kw": "本溪水洞", "type": "scenic-spot", "route": "scenic-water"},
    {"city": "本溪", "region": "辽东", "name": "关门山国家森林公园", "kw": "关门山", "type": "scenic-spot", "route": "mountain"},
    {"city": "本溪", "region": "辽东", "name": "五女山山城（桓仁）", "kw": "五女山", "type": "scenic-spot", "route": "mountain"},
    {"city": "丹东", "region": "辽东", "name": "鸭绿江断桥", "kw": "鸭绿江断桥", "type": "scenic-spot", "route": "city-riverside"},
    {"city": "丹东", "region": "辽东", "name": "虎山长城", "kw": "虎山长城", "type": "scenic-spot", "route": "mountain"},
    {"city": "丹东", "region": "辽东", "name": "宽甸绿江村", "kw": "绿江村", "type": "scenic-spot", "route": "mountain-county-road"},
    {"city": "大连", "region": "辽南", "name": "大连金石滩国家旅游度假区", "kw": "金石滩", "type": "scenic-spot", "route": "coast"},
    {"city": "大连", "region": "辽南", "name": "旅顺口风景区", "kw": "旅顺", "type": "scenic-spot", "route": "coast"},
    {"city": "大连", "region": "辽南", "name": "大连滨海路", "kw": "滨海路", "type": "scenic-spot", "route": "coast"},
    {"city": "鞍山", "region": "辽南", "name": "千山风景区", "kw": "千山", "type": "scenic-spot", "route": "mountain"},
    {"city": "鞍山", "region": "辽南", "name": "岫岩药山风景区", "kw": "药山", "type": "scenic-spot", "route": "mountain"},
    {"city": "鞍山", "region": "辽南", "name": "岫岩龙潭湾", "kw": "龙潭湾", "type": "scenic-spot", "route": "mountain"},
    {"city": "抚顺", "region": "辽中", "name": "大伙房水库萨尔浒风景区", "kw": "大伙房水库", "type": "scenic-spot", "route": "scenic-water"},
    {"city": "抚顺", "region": "辽中", "name": "天女山森林公园", "kw": "天女山", "type": "scenic-spot", "route": "mountain"},
    {"city": "铁岭", "region": "辽北", "name": "冰砬山国家森林公园", "kw": "冰砬山", "type": "scenic-spot", "route": "mountain"},
    {"city": "铁岭", "region": "辽北", "name": "清河水库旅游区", "kw": "清河水库", "type": "scenic-spot", "route": "scenic-water"},
    {"city": "朝阳", "region": "辽西", "name": "朝阳凤凰山", "kw": "凤凰山", "type": "scenic-spot", "route": "mountain"},
    {"city": "朝阳", "region": "辽西", "name": "大黑山风景区", "kw": "大黑山", "type": "scenic-spot", "route": "mountain"},
    {"city": "盘锦", "region": "辽南", "name": "红海滩国家风景廊道", "kw": "红海滩", "type": "scenic-spot", "route": "coast"},
    {"city": "盘锦", "region": "辽南", "name": "双台河口湿地自然保护区", "kw": "双台河口", "type": "scenic-spot", "route": "coast"},
    {"city": "葫芦岛", "region": "辽西", "name": "觉华岛", "kw": "觉华岛", "type": "scenic-spot", "route": "coast"},
    {"city": "葫芦岛", "region": "辽西", "name": "九门口水上长城", "kw": "九门口", "type": "scenic-spot", "route": "mountain"},
    {"city": "阜新", "region": "辽西", "name": "海棠山摩崖石刻", "kw": "海棠山", "type": "scenic-spot", "route": "mountain"},
    {"city": "辽阳", "region": "辽中", "name": "弓长岭温泉度假区", "kw": "弓长岭", "type": "scenic-spot", "route": "city-riverside"},
    {"city": "辽阳", "region": "辽中", "name": "太子河风景区", "kw": "太子河", "type": "scenic-spot", "route": "city-riverside"},
]

def load_existing_names():
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            items = data.get("items", []) if isinstance(data, dict) else (data if isinstance(data, list) else [])
            return set(i.get("name", "") for i in items), items
        except:
            pass
    return set(), []

def save_items(items):
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    output = {
        "exported_at": datetime.now().isoformat(),
        "source": "openclaw-collector-v3",
        "total": len(items),
        "items": items,
    }
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

def main(target=5):
    print("=" * 50)
    print(f"摩旅景点采集 v3 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    existing_names, existing_items = load_existing_names()
    print(f"已有数据: {len(existing_items)} 条, 目标采集: {target} 条")

    new_items = []
    count = 0
    for spot in SPOTS:
        if count >= target:
            break
        name = spot["name"]
        if name in existing_names:
            continue
        
        item = {
            "platform": "builtin",
            "poiId": f"v3-{spot['city']}-{spot['kw']}",
            "name": name,
            "sourceUrl": f"https://www.baidu.com/s?wd={urllib.parse.quote(name)}",
            "owner": "公开数据",
            "provider": "openclaw-collector",
            "location": {"city": spot["city"], "region": spot["region"], "latitude": 0, "longitude": 0},
            "poiType": spot["type"],
            "keywords": [spot["kw"]],
            "excerpt": f"{spot['city']}旅游景点-{spot['kw']}",
            "photoTags": [],
            "supportTags": ["viewpoint"],
            "routeType": spot["route"],
            "collected_at": datetime.now().isoformat(),
        }
        new_items.append(item)
        count += 1
        existing_names.add(name)
        print(f"  + [{count}] {name}")
        time.sleep(0.1)

    all_items = existing_items + new_items
    save_items(all_items)
    print(f"\n采集完毕: 已有{len(existing_items)}条 + 新增{count}条 = 总计{len(all_items)}条")
    return count

if __name__ == "__main__":
    main(target=5)
