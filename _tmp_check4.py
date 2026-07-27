# -*- coding: utf-8 -*-
import json

# 看分析报告
try:
    with open(r'D:\摩旅数据采集目录\摩旅路线_完整分析报告_20260607_143002.md', encoding='utf-8') as f:
        content = f.read()
    print(content[:3000])
except Exception as e:
    print(f'read doc err: {e}')
