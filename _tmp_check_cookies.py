#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, os

# Check if we have any cookies for doubao
cookies_file = 'moto/data/douyin_cookies.json'
if os.path.exists(cookies_file):
    with open(cookies_file, 'r', encoding='utf8') as f:
        c = json.load(f)
    print(f'Cookies file keys: {list(c.keys())}')
    cookies = c.get('cookies', [])
    if isinstance(cookies, list):
        doubao_cookies = [ck for ck in cookies if 'doubao' in ck.get('domain', '') or 'bytedance' in ck.get('domain', '')]
        print(f'Total cookies: {len(cookies)}')
        print(f'Doubao/bytedance cookies: {len(doubao_cookies)}')
        for ck in doubao_cookies[:5]:
            print(f'  {ck.get("domain")}: {ck.get("name")}={ck.get("value", "")[:30]}')
    else:
        print(f'Cookies is not a list: {type(cookies)}')
else:
    print('No cookies file found')
