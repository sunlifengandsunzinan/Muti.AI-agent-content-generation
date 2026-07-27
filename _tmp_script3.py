# -*- coding: utf-8 -*-
import json
import sys
sys.stdout.reconfigure(encoding='utf-8')
with open(r'D:\摩旅数据采集目录\ln_filtered_199.json', encoding='utf-8-sig') as f:
    data = json.load(f)
for r in data:
    title = r.get('title', '')
    clean = title.encode('ascii', errors='ignore').decode('ascii')
    if any(kw in clean for kw in ['331','丹东','集安','边境','dandong','Dandong']):
        print(title[:80])
