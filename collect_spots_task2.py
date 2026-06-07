#!/usr/bin/env python3
"""
摩旅景点采集任务 v2
通过 Nominatim API (OpenStreetMap) 搜索辽宁景点/驿站
不需要浏览器，不需要登录
"""
import io, json, os, sys, time, urllib.parse, urllib.request
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

OUTPUT_DIR = r"D:\moto\data\raw"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "openclaw_export.json")
SEEN_FILE = os.path.join(OUTPUT_DIR, "collected_names.txt")

# 辽宁各城市景点搜索词
SEED_QUERIES = [
    # (city, keyword, category)
    ("沈阳", "摩旅驿站", "moto-station"),
    ("沈阳", "森林公园", "scenic-spot"),
    ("沈阳", "环湖骑行", "scenic-spot"),
    ("本溪", "摩旅路线", "moto-station"),
    ("本溪", "关门山", "scenic-spot"),
    ("本溪", "大峡谷", "scenic-spot"),
    ("丹东", "沿江公路", "scenic-spot"),
    ("丹东", "鸭绿江", "scenic-spot"),
    ("丹东", "虎山长城", "scenic-spot"),
    ("大连", "滨海路", "scenic-spot"),
    ("大连", "金石滩", "scenic-spot"),
    ("鞍山", "千山", "scenic-spot"),
    ("鞍山", "岫岩", "scenic-spot"),
    ("抚顺", "大伙房水库", "scenic-spot"),
    ("铁岭", "冰砬山", "scenic-spot"),
    ("朝阳", "凤凰山", "scenic-spot"),
    ("沈阳", "东陵公园", "scenic-spot"),
    ("丹东", "宽甸", "scenic-spot"),
    ("本溪", "桓仁", "scenic-spot"),
]

def fetch_nominatim(city: str, query: str) -> list[dict]:
    """通过 OpenStreetMap Nominatim API 搜索地点"""
    params = urllib.parse.urlencode({
        "q": f"{city} {query}",
        "format": "jsonv2",
        "limit": 5,
        "addressdetails": "1",
    })
    url = f"https://nominatim.openstreetmap.org/search?{params}"
    headers = {"User-Agent": "moto-planner/1.0 (spot-collector)"}
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"  [error] {city} {query}: {e}")
        return []

def convert_to_item(raw: dict, city: str, query: str, category: str) -> dict:
    """转换 Nominatim 结果为景点条目"""
    name = raw.get("display_name", query).split(",")[0].strip()
    lat = float(raw.get("lat", 0))
    lon = float(raw.get("lon", 0))
    return {
        "platform": "osm",
        "poiId": f"osm-{lat}-{lon}",
        "name": name,
        "sourceUrl": f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=15/{lat}/{lon}",
        "owner": "OpenStreetMap",
        "provider": "nominatim",
        "location": {
            "city": city,
            "region": "辽宁",
            "latitude": lat,
            "longitude": lon,
        },
        "poiType": category,
        "keywords": [query],
        "excerpt": f"{city} {query} - OSM采集",
        "photoTags": [],
        "supportTags": ["viewpoint"] if category == "scenic-spot" else ["fuel", "viewpoint"],
        "routeType": "mountain" if category == "scenic-spot" else "supply-stop",
        "collected_at": datetime.now().isoformat(),
    }

def load_existing_names() -> set:
    names = set()
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            items = data.get("items", []) if isinstance(data, dict) else data
            for item in items:
                names.add(item.get("name", ""))
        except:
            pass
    return names

def load_existing_items() -> list:
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("items", []) if isinstance(data, dict) else data
        except:
            pass
    return []

def save_items(items: list):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output = {
        "exported_at": datetime.now().isoformat(),
        "source": "openstreetmap-nominatim",
        "total": len(items),
        "items": items,
    }
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\n已保存 {len(items)} 条数据到 {OUTPUT_FILE}")

def main():
    target = 5
    print(f"摩旅景点采集 v2 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    existing = load_existing_items()
    existing_names = load_existing_names()
    print(f"已有数据: {len(existing)} 条")

    new_items = []
    collected = 0

    for city, query, category in SEED_QUERIES:
        if collected >= target:
            break
        
        print(f"\n搜索: {city} {query}")
        results = fetch_nominatim(city, query)
        
        for raw in results[:3]:
            item = convert_to_item(raw, city, query, category)
            name = item["name"]
            if name and name not in existing_names and name not in [n.get("name") for n in new_items]:
                new_items.append(item)
                collected += 1
                existing_names.add(name)
                print(f"  + [{collected}] {name}")
                if collected >= target:
                    break
        
        time.sleep(1.5)  # Nominatim 使用限制，1请求/秒

    all_items = existing + new_items
    save_items(all_items)
    
    print(f"\n本轮新增: {collected} 条, 总计: {len(all_items)} 条")

    # 返回值方便外部判断
    if collected >= 0:
        print(f"NOTIFY: 已采集 {len(all_items)} 条数据，请查收！")

if __name__ == "__main__":
    main()
