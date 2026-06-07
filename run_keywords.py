# -*- coding: utf-8 -*-
import subprocess
import sys

keywords = [
    "本溪摩旅路线",
    "辽宁金秋摩旅",
    "辽东峡谷骑行",
    "辽宁沿海摩旅",
    "沈阳摩旅路线",
    "大连滨海路骑行",
    "本桓公路摩托",
    "丹东绿江村骑行",
    "辽宁山路压弯",
    "鞍山摩旅路线",
]

venv_python = r"C:\Users\Administrator\.openclaw\workspace\MediaCrawler\.venv\Scripts\python.exe"
base_dir = r"C:\Users\Administrator\.openclaw\workspace\MediaCrawler"

for kw in keywords:
    print(f"\n{'='*60}")
    print(f"Starting keyword: {kw}")
    print(f"{'='*60}")
    
    cmd = [
        venv_python,
        "main.py",
        "--platform", "xhs",
        "--lt", "qrcode",
        "--keywords", kw,
        "--crawler_max_notes_count", "20",
    ]
    
    result = subprocess.run(cmd, cwd=base_dir, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Keyword {kw} FAILED with exit code {result.returncode}")
        print(result.stderr[-500:] if result.stderr else "")
        continue
    
    print(f"Keyword {kw} completed successfully")

print(f"\n{'='*60}")
print("ALL KEYWORDS COMPLETED!")
print(f"{'='*60}")
