import json

with open("D:\\moto\\data\\raw\\openclaw_export.json", "r", encoding="utf-8") as f:
    export = json.load(f)

new_items = [
    {
      "platform": "web",
      "poiId": "web-dalian-binhai",
      "name": "大连滨海路观景摩旅线",
      "sourceUrl": "https://www.baidu.com/s?wd=大连滨海路摩旅",
      "owner": "百度收录",
      "provider": "openclaw",
      "location": {"city": "大连", "region": "辽南", "latitude": 38.8704, "longitude": 121.6317},
      "poiType": "scenic-spot",
      "keywords": ["滨海路", "海景", "弯道", "打卡"],
      "excerpt": "大连经典的滨海路摩旅线，串联星海广场、棒棰岛、渔人码头、银沙滩等打卡点。",
      "photoTags": ["滨海公路", "海景", "弯道压弯"],
      "supportTags": ["viewpoint", "fuel"],
      "routeType": "coast"
    },
    {
      "platform": "web",
      "poiId": "web-zhuanghe-zhuanjiao",
      "name": "庄河转角楼水库（松转线）",
      "sourceUrl": "https://www.baidu.com/s?wd=庄河转角楼水库摩旅",
      "owner": "百度收录",
      "provider": "openclaw",
      "location": {"city": "大连", "region": "辽南", "latitude": 39.8275, "longitude": 122.9876},
      "poiType": "scenic-spot",
      "keywords": ["水库", "湖光山色", "避暑", "松转线"],
      "excerpt": "庄河松转线沿水库而建的静谧路线，湖光山色相映成趣，适合休闲骑行。",
      "photoTags": ["湖景", "山路", "避暑"],
      "supportTags": ["viewpoint", "lodging"],
      "routeType": "mountain"
    },
    {
      "platform": "web",
      "poiId": "web-lvshun-lvyou",
      "name": "旅顺探索摩旅线",
      "sourceUrl": "https://www.baidu.com/s?wd=旅顺摩旅路线",
      "owner": "百度收录",
      "provider": "openclaw",
      "location": {"city": "大连", "region": "辽南", "latitude": 38.8113, "longitude": 121.2579},
      "poiType": "scenic-spot",
      "keywords": ["旅顺", "历史", "跨海大桥", "博物馆"],
      "excerpt": "旅顺跨海大桥到旅顺博物馆，感受近代历史与山海风光。",
      "photoTags": ["跨海大桥", "历史建筑", "海景"],
      "supportTags": ["viewpoint", "fuel"],
      "routeType": "city-riverside"
    },
    {
      "platform": "web",
      "poiId": "web-jinshitan",
      "name": "金石滩地质公园摩旅线",
      "sourceUrl": "https://www.baidu.com/s?wd=金石滩摩旅",
      "owner": "百度收录",
      "provider": "openclaw",
      "location": {"city": "大连", "region": "辽南", "latitude": 39.0928, "longitude": 122.0061},
      "poiType": "scenic-spot",
      "keywords": ["地质公园", "渔村", "海岸"],
      "excerpt": "金石滩地质公园与渔村风情，地质奇观与沿海公路兼具的摩旅打卡地。",
      "photoTags": ["奇石海岸", "渔村", "地质景观"],
      "supportTags": ["viewpoint", "fuel"],
      "routeType": "coast"
    },
    {
      "platform": "web",
      "poiId": "web-dalian-guixiaoshi",
      "name": "大连版鬼笑石观景台",
      "sourceUrl": "https://www.baidu.com/s?wd=大连鬼笑石摩旅",
      "owner": "百度收录",
      "provider": "openclaw",
      "location": {"city": "大连", "region": "辽南", "latitude": 38.9042, "longitude": 121.6615},
      "poiType": "scenic-spot",
      "keywords": ["鬼笑石", "全景", "日出"],
      "excerpt": "大连版鬼笑石观景台，可俯瞰大连全景和海上日出，环渤海摩旅打卡地。",
      "photoTags": ["全景", "日出", "城市夜景"],
      "supportTags": ["viewpoint"],
      "routeType": "mountain"
    },
    {
      "platform": "web",
      "poiId": "web-xianyuwan",
      "name": "仙浴湾骑行线（瓦房店）",
      "sourceUrl": "https://www.baidu.com/s?wd=仙浴湾摩旅",
      "owner": "百度收录",
      "provider": "openclaw",
      "location": {"city": "大连", "region": "辽南", "latitude": 39.6833, "longitude": 121.5833},
      "poiType": "scenic-spot",
      "keywords": ["仙浴湾", "秋日骑行", "海滩"],
      "excerpt": "瓦房店仙浴湾，大理的治愈系海滩骑行路线。",
      "photoTags": ["海滩", "秋景", "治愈骑行"],
      "supportTags": ["viewpoint", "lodging"],
      "routeType": "coast"
    },
    {
      "platform": "web",
      "poiId": "web-benxi-huanshu",
      "name": "本溪本桓公路（中华枫叶大道）",
      "sourceUrl": "https://www.baidu.com/s?wd=本溪本桓公路摩旅",
      "owner": "百度收录",
      "provider": "openclaw",
      "location": {"city": "本溪", "region": "辽东", "latitude": 41.2993, "longitude": 125.3669},
      "poiType": "scenic-spot",
      "keywords": ["枫叶", "秋季", "盘山路"],
      "excerpt": "本溪本桓公路被誉为中华枫叶大道，秋季红叶漫山是摩旅经典路线。",
      "photoTags": ["枫叶", "盘山路", "秋景"],
      "supportTags": ["viewpoint", "fuel", "lodging"],
      "routeType": "mountain"
    },
    {
      "platform": "web",
      "poiId": "web-bingyugou",
      "name": "大连冰峪沟摩旅线",
      "sourceUrl": "https://www.baidu.com/s?wd=冰峪沟摩旅",
      "owner": "百度收录",
      "provider": "openclaw",
      "location": {"city": "大连", "region": "辽南", "latitude": 40.0308, "longitude": 122.8212},
      "poiType": "scenic-spot",
      "keywords": ["冰峪沟", "山水", "峡谷"],
      "excerpt": "大连庄河冰峪沟山水峡谷风光，适合摩旅途中自然打卡。",
      "photoTags": ["山水", "峡谷", "自然风光"],
      "supportTags": ["viewpoint", "lodging"],
      "routeType": "mountain"
    },
    {
      "platform": "web",
      "poiId": "web-anshan-qianshan",
      "name": "鞍山千山摩旅线",
      "sourceUrl": "https://www.baidu.com/s?wd=鞍山千山摩旅",
      "owner": "百度收录",
      "provider": "openclaw",
      "location": {"city": "鞍山", "region": "辽中", "latitude": 41.0767, "longitude": 123.0786},
      "poiType": "scenic-spot",
      "keywords": ["千山", "寺庙", "登山"],
      "excerpt": "鞍山千山风景区，辽东半岛著名山岳景观，摩旅至鞍山的经典目的地。",
      "photoTags": ["山景", "寺庙", "自然"],
      "supportTags": ["viewpoint", "fuel"],
      "routeType": "mountain"
    },
    {
      "platform": "web",
      "poiId": "web-huludao-xingcheng",
      "name": "兴城海滨摩旅线",
      "sourceUrl": "https://www.baidu.com/s?wd=兴城海滨摩旅",
      "owner": "百度收录",
      "provider": "openclaw",
      "location": {"city": "葫芦岛", "region": "辽南", "latitude": 40.5812, "longitude": 120.6899},
      "poiType": "scenic-spot",
      "keywords": ["兴城", "海滨", "古城"],
      "excerpt": "兴城古城与海滨浴场结合的摩旅路线。",
      "photoTags": ["古城", "海滨", "沿海公路"],
      "supportTags": ["viewpoint", "lodging"],
      "routeType": "coast"
    }
]

old_count = len(export["items"])
export["items"].extend(new_items)
export["exported_at"] = "2026-05-27T16:30:00+08:00"

with open("D:\\moto\\data\\raw\\openclaw_export.json", "w", encoding="utf-8") as f:
    json.dump(export, f, ensure_ascii=False, indent=2)

print("原有 items:", old_count)
print("新增 items:", len(new_items))
print("总计 items:", len(export["items"]))
print("已完成写入！")
