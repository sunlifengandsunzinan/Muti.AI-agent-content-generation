# -*- coding: utf-8 -*-
import json
try:
    with open(r'D:\摩旅数据采集目录\routes_v8_new_LN.json', encoding='utf-8-sig') as f:
        data = json.load(f)
    print(f'共 {len(data)} 条路线')
    for i, r in enumerate(data[:40]):
        title = r.get('title','')[:70]
        likes = r.get('likes','')
        favs = r.get('favorites','')
        comments = r.get('comments','')
        print(f'{i+1}. likes={likes} favs={favs} comments={comments} | {title}')
except Exception as e:
    print(f'ERROR: {e}')
