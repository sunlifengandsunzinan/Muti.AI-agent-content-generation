import json, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('D:/moto/data/raw/openclaw_export.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Print all existing titles for comparison
print("=== EXISTING TITLES ===")
for i, item in enumerate(data['items']):
    print(f"{i+1}. [{item['author']}] {item['name'][:80]}... date={item['date']} likes={item['likes']}")

print("\n\n=== Check specific items ===")

# Check the "new" items against existing
new_candidates = [
    "沈阳南骑行路线分享，灯塔粮仓文创园和广佑寺！#骑行vlog #摩托车 #踏板摩托车 #摩旅 #沈阳摩托车",
    "环华摩旅路线分享 @丁小宝摩旅时况",
    "大连骑行小队 2026 初春 环普兰店巡航之旅",
    "沉浸式跨海 大连-威海 摩托车过海教程",
    "音乐一响，神兵登场 挑战 2026 骑完辽宁 第一站之法库财湖",
    "2024十一摩旅沈阳-大连。七日摩旅路线",
    "环华摩旅第37天，绿江村-丹东河口",
]

for nc in new_candidates:
    found = False
    for item in data['items']:
        en = item['name']
        # Check significant overlap
        if nc[:30] in en or en[:30] in nc:
            found = True
            print(f"FOUND: '{nc[:50]}' -> '{en[:50]}'")
            break
    if not found:
        print(f"*** TRULY NEW: '{nc[:60]}'")
