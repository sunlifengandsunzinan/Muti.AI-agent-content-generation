import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('D:/moto/data/raw/openclaw_export.json', 'r', encoding='utf-8') as f:
    existing_data = json.load(f)
existing_names = set(i['name'] for i in existing_data['items'])

with open('D:/moto/data/raw/douyin_seen_titles.txt', 'r', encoding='utf-8') as f:
    seen_titles = set(line.strip() for line in f if line.strip())

print(f"Existing export items: {len(existing_data['items'])}")
print(f"Unique names in export: {len(existing_names)}")
print(f"Seen titles count: {len(seen_titles)}")

page_items = [
    ("沈阳南骑行路线分享，灯塔粮仓文创园和广佑寺！#骑行vlog #摩托车 #踏板摩托车 #摩旅 #沈阳摩托车", "小七说摩托", "99", "4月1日"),
    ("#摩旅 #摩友 #跑山 #摩托车 #沈阳摩托车", "盛京铁骑", "1275", "5月15日"),
    ("沈阳周边一百五十公里短途骑行进阶路线！#踏板摩托车 #七星山 #摩旅 #日常溜车 #法库古镇", "小七说摩托", "556", "3月19日"),
    ("环华摩旅路线分享 @丁小宝摩旅时况", "丁小宝", "4690", "3月19日"),
    ("今日打卡辽宁滨海公路G228锦州-葫芦岛-兴城。走了好多好玩的景区看完视频你就知道有多美了", "小武爱骑车", "57", "4月22日"),
    ("2024十一摩旅沈阳-大连。七日摩旅路线:沈阳-盖州-长兴岛-旅顺-大连-盖州-沈阳 #摩旅 #我的骑行日记 #保持热爱奔赴山海", "洛 水", "13", "2024年10月15日"),
    ("环华摩旅第37天，绿江村-丹东河口，这山路磨心性练技术享自由 #环华摩旅 #331国道 #山路 #绿江村 #丹东河口景区", "露l姐的旅行", "15", "3月21日"),
]

new_items = []
for name, author, likes, date in page_items:
    name_clean = name.strip()
    found = False
    for ename in existing_names:
        if name_clean[:40] in ename or ename[:40] in name_clean:
            found = True
            break
    if not found:
        for stitle in seen_titles:
            if name_clean[:40] in stitle or stitle[:40] in name_clean:
                found = True
                break
    if not found:
        new_items.append((name, author, likes, date))
        print(f"NEW: {name[:80]} | {author} | {likes} zan | {date}")

if not new_items:
    print("All page items already in existing data")
else:
    print(f"\nFound {len(new_items)} new items!")
