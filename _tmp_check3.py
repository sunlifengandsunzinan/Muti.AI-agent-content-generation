# -*- coding: utf-8 -*-
import json, os

base = r'D:\摩旅数据采集目录'

# 看看 route_templates_merged.json 里的传播数据
fns = ['route_templates_merged.json', 'route_templates_from_mac.json', 'ln_filtered_199.json']
for fn in fns:
    fp = os.path.join(base, fn)
    if not os.path.exists(fp):
        print(f'{fn} 不存在')
        continue
    try:
        with open(fp, encoding='utf-8-sig') as f:
            data = json.load(f)
    except:
        with open(fp, encoding='utf-8') as f:
            data = json.load(f)
    print(f'\n=== {fn} ({os.path.getsize(fp)/1024:.0f}KB) ===')
    print(f'类型: {type(data).__name__}')
    if isinstance(data, list):
        print(f'共 {len(data)} 条')
        for i, r in enumerate(data[:10]):
            title = r.get('title', str(r))[:60]
            likes = r.get('likes', r.get('like_count', r.get('数字', '')))
            print(f'{i+1}. likes={likes} | {title}')
    elif isinstance(data, dict):
        for k in list(data.keys())[:5]:
            v = data[k]
            if isinstance(v, list):
                print(f'{k}: 列表({len(v)}条)')
                if len(v) > 0:
                    item = v[0]
                    print(f'  首项: {str(item)[:100]}')
            else:
                print(f'{k}: {str(v)[:100]}')
