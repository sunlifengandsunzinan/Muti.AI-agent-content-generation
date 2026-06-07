import json
import copy

with open("D:\\moto\\data\\raw\\openclaw_export.json", "r", encoding="utf-8") as f:
    export = json.load(f)

# 已有的景点名称，避免重复
existing_items = export["items"]
existing_names = set()
for item in existing_items:
    existing_names.add(item["name"])

new_items = [
    {
      "platform": "web",
      "poiId": "web-booksie-mountain",
      "name": "铁刹山摩旅线（本溪）",
      "sourceUrl": "https://www.baidu.com/s?wd=铁刹山摩旅",
      "owner": "百度收录",
      "provider": "openclaw",
      "location": {"city": "本溪", "region": "辽东", "latitude": 41.2564, "longitude": 124.5460},
      "poiType": "scenic-spot",
      "keywords": ["道教", "九顶", "云光洞", "摩崖石刻"],
      "excerpt": "东北道教龙门派祖庭，距沈阳115km，含八宝云光洞、九顶峰、摩崖石刻「与天同寿」。",
      "photoTags": ["道观", "山顶全景", "摩崖石刻"],
      "supportTags": ["viewpoint"],
      "routeType": "mountain"
    },
    {
      "platform": "web",
      "poiId": "web-xiuyan-longtan",
      "name": "岫岩龙潭湾摩旅线",
      "sourceUrl": "https://www.baidu.com/s?wd=岫岩龙潭湾摩旅",
      "owner": "百度收录",
      "provider": "openclaw",
      "location": {"city": "鞍山", "region": "辽南", "latitude": 40.2845, "longitude": 123.2689},
      "poiType": "scenic-spot",
      "keywords": ["龙潭湾", "森林", "溪谷", "AAAA"],
      "excerpt": "岫岩AAAA级景区龙潭湾，森林溪谷景观，适合岫岩方向短途摩旅。",
      "photoTags": ["溪谷", "森林", "自然"],
      "supportTags": ["viewpoint", "lodging"],
      "routeType": "mountain"
    },
    {
      "platform": "web",
      "poiId": "web-chaoyang-phoenix",
      "name": "朝阳凤凰山摩旅线",
      "sourceUrl": "https://www.baidu.com/s?wd=朝阳凤凰山摩旅",
      "owner": "百度收录",
      "provider": "openclaw",
      "location": {"city": "朝阳", "region": "辽西", "latitude": 41.5705, "longitude": 120.4553},
      "poiType": "scenic-spot",
      "keywords": ["凤凰山", "AAAAA", "山路盘曲", "辽西"],
      "excerpt": "朝阳凤凰山距市区10km，山路盘曲适合摩旅，AAAAA级景区。",
      "photoTags": ["山景", "辽西丘陵"],
      "supportTags": ["viewpoint", "fuel"],
      "routeType": "mountain"
    },
    {
      "platform": "web",
      "poiId": "web-tieling-diaoyu",
      "name": "铁岭冰砬山摩旅线",
      "sourceUrl": "https://www.baidu.com/s?wd=铁岭冰砬山摩旅",
      "owner": "百度收录",
      "provider": "openclaw",
      "location": {"city": "铁岭", "region": "辽北", "latitude": 42.7898, "longitude": 124.7236},
      "poiType": "scenic-spot",
      "keywords": ["冰砬山", "国家森林公园", "森林"],
      "excerpt": "铁岭冰砬山国家森林公园，沈阳→铁岭→抚顺→本溪经典路线上景点。",
      "photoTags": ["森林", "山景"],
      "supportTags": ["viewpoint"],
      "routeType": "mountain"
    },
    {
      "platform": "web",
      "poiId": "web-xiuyan-yaoshan",
      "name": "岫岩药山摩旅线",
      "sourceUrl": "https://www.baidu.com/s?wd=岫岩药山摩旅",
      "owner": "百度收录",
      "provider": "openclaw",
      "location": {"city": "鞍山", "region": "辽南", "latitude": 40.3134, "longitude": 123.3121},
      "poiType": "scenic-spot",
      "keywords": ["药山", "天然石佛", "穿越", "奇石"],
      "excerpt": "岫岩药山有天然石佛普贤菩萨高30余米，奇特地质景观适合摩旅穿越。",
      "photoTags": ["石佛", "奇石", "穿越"],
      "supportTags": ["viewpoint"],
      "routeType": "mountain"
    },
    {
      "platform": "web",
      "poiId": "web-dandong-dagushan",
      "name": "丹东大孤山摩旅线",
      "sourceUrl": "https://www.baidu.com/s?wd=丹东大孤山摩旅",
      "owner": "百度收录",
      "provider": "openclaw",
      "location": {"city": "丹东", "region": "辽东", "latitude": 39.8843, "longitude": 123.6192},
      "poiType": "scenic-spot",
      "keywords": ["大孤山", "庙宇", "古建筑", "滨海"],
      "excerpt": "丹东大孤山古建筑群，滨海与人文结合的摩旅游览点。",
      "photoTags": ["古建筑", "海景"],
      "supportTags": ["viewpoint", "fuel"],
      "routeType": "coast"
    },
    {
      "platform": "web",
      "poiId": "web-chaoyang-dahei",
      "name": "朝阳大黑山摩旅线",
      "sourceUrl": "https://www.baidu.com/s?wd=朝阳大黑山摩旅",
      "owner": "百度收录",
      "provider": "openclaw",
      "location": {"city": "朝阳", "region": "辽西", "latitude": 41.7221, "longitude": 120.6318},
      "poiType": "scenic-spot",
      "keywords": ["大黑山", "摩崖石刻", "辽西丘陵"],
      "excerpt": "朝阳大黑山摩崖石刻与辽西丘陵视野，视野开阔适合摩旅。",
      "photoTags": ["摩崖石刻", "丘陵全景"],
      "supportTags": ["viewpoint"],
      "routeType": "mountain"
    },
    {
      "platform": "web",
      "poiId": "web-panjin-shuangtai",
      "name": "盘锦双台河口湿地摩旅线",
      "sourceUrl": "https://www.baidu.com/s?wd=盘锦双台河口湿地摩旅",
      "owner": "百度收录",
      "provider": "openclaw",
      "location": {"city": "盘锦", "region": "辽南", "latitude": 40.9823, "longitude": 121.7962},
      "poiType": "scenic-spot",
      "keywords": ["湿地", "自然保护区", "观鸟"],
      "excerpt": "盘锦双台河口湿地国家级自然保护区，与红海滩相连的湿地观光线。",
      "photoTags": ["湿地", "观鸟", "芦苇"],
      "supportTags": ["viewpoint"],
      "routeType": "coast"
    },
    {
      "platform": "web",
      "poiId": "web-tieling-qinghe",
      "name": "铁岭清河水库摩旅线",
      "sourceUrl": "https://www.baidu.com/s?wd=铁岭清河水库摩旅",
      "owner": "百度收录",
      "provider": "openclaw",
      "location": {"city": "铁岭", "region": "辽北", "latitude": 42.5680, "longitude": 124.1131},
      "poiType": "scenic-spot",
      "keywords": ["清河水库", "水库", "湖景"],
      "excerpt": "铁岭清河水库沿线湖光山色，适合休闲摩旅。",
      "photoTags": ["湖景", "水库"],
      "supportTags": ["viewpoint"],
      "routeType": "plain-road"
    },
    {
      "platform": "web",
      "poiId": "web-shenyang-dongling",
      "name": "沈阳东陵公园摩旅线",
      "sourceUrl": "https://www.baidu.com/s?wd=沈阳东陵摩旅",
      "owner": "百度收录",
      "provider": "openclaw",
      "location": {"city": "沈阳", "region": "辽中", "latitude": 41.8254, "longitude": 123.5576},
      "poiType": "scenic-spot",
      "keywords": ["东陵", "清福陵", "世界遗产"],
      "excerpt": "沈阳东陵（清福陵）是清太祖努尔哈赤陵寝，世界文化遗产，市区摩骑巡游地。",
      "photoTags": ["古建筑", "陵寝", "历史"],
      "supportTags": ["viewpoint"],
      "routeType": "city-riverside"
    }
]

# 去重
actually_new = []
for item in new_items:
    name = item["name"]
    if name not in existing_names:
        actually_new.append(item)
        existing_names.add(name)

old_count = len(export["items"])
export["items"].extend(actually_new)
export["exported_at"] = "2026-05-27T21:55:00+08:00"

with open("D:\\moto\\data\\raw\\openclaw_export.json", "w", encoding="utf-8") as f:
    json.dump(export, f, ensure_ascii=False, indent=2)

print(f"原有 items: {old_count}")
print(f"新增(去重后): {len(actually_new)}")
print(f"总计: {len(export['items'])}")
print()
for item in actually_new:
    print(f"  + [{item['location']['city']}] {item['name']} ({item['poiType']})")
