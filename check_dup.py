import json
from collections import Counter

with open('D:/moto/data/raw/openclaw_export.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

names = [i['name'] for i in data['items']]
c = Counter(names)
for k, v in c.items():
    if v > 1:
        print(f"DUP: {k[:80]} x{v}")

print(f"Total: {len(data['items'])}, Unique: {len(set(names))}")
