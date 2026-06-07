import json, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('D:/moto/data/raw/openclaw_export.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

with open('D:/moto/data/raw/douyin_seen_titles.txt', 'r', encoding='utf-8') as f:
    seen_titles = [l.strip() for l in f if l.strip()]

existing_names = set(i['name'] for i in data['items'])

# Items from the page that are NOT in existing export
# (verified by checking page snapshot data carefully)
truly_new = [
    {
        "name": "沈阳南骑行路线分享，灯塔粮仓文创园和广佑寺！#骑行vlog #摩托车 #踏板摩托车 #摩旅 #沈阳摩托车",
        "author": "小七说摩托",
        "likes": 99,
        "date": "4月1日",
        "source": "抖音"
    },
    {
        "name": "沈阳周边一百五十公里短途骑行进阶路线！#踏板摩托车 #七星山 #摩旅 #日常溜车 #法库古镇",
        "author": "小七说摩托",
        "likes": 556,
        "date": "3月19日",
        "source": "抖音"
    },
    {
        "name": "环华摩旅路线分享 @丁小宝摩旅时况",
        "author": "丁小宝",
        "likes": 4690,
        "date": "3月19日",
        "source": "抖音"
    },
    {
        "name": "2024十一摩旅沈阳-大连。七日摩旅路线:沈阳-盖州-长兴岛-旅顺-大连-盖州-沈阳 #摩旅 #我的骑行日记 #保持热爱奔赴山海",
        "author": "洛 水",
        "likes": 13,
        "date": "2024年10月15日",
        "source": "抖音"
    },
    {
        "name": "环华摩旅第37天，绿江村-丹东河口，这山路磨心性练技术享自由 #环华摩旅 #331国道 #山路 #绿江村 #丹东河口景区",
        "author": "露l姐的旅行",
        "likes": 15,
        "date": "3月21日",
        "source": "抖音"
    }
]

# Filter: make sure none is already in export
final_new = []
for item in truly_new:
    name = item['name']
    # Check name
    found = False
    for en in existing_names:
        if name[:35] in en or en[:35] in name:
            found = True
            print(f"SKIP (exists): {name[:50]}")
            break
    if not found:
        final_new.append(item)

print(f"\nTruly new items to add: {len(final_new)}")

if final_new:
    for item in final_new:
        print(f"  + [{item['author']}] {item['name'][:50]} | {item['likes']}zan | {item['date']}")
    
    # Append to export
    for item in final_new:
        data['items'].append(item)
    data['total'] = len(data['items'])
    
    with open('D:/moto/data/raw/openclaw_export.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"Updated export: {data['total']} total items")
    
    # Add to seen titles
    new_seen = []
    for item in final_new:
        # Extract hashtags from name
        import re
        hashtags = re.findall(r'#[^\s#]+', item['name'])
        for ht in hashtags:
            if ht not in seen_titles and ht not in new_seen:
                new_seen.append(ht)
        
        # Also add key name segments
        simple_name = item['name'].strip()
        if simple_name not in seen_titles and simple_name not in new_seen:
            new_seen.append(simple_name)
    
    with open('D:/moto/data/raw/douyin_seen_titles.txt', 'a', encoding='utf-8') as f:
        for line in new_seen:
            f.write(line + '\n')
    
    print(f"Added {len(new_seen)} new lines to douyin_seen_titles.txt")
else:
    print("No changes needed")
