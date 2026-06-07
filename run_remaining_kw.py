#!/usr/bin/env python3
"""Run remaining Xiaohongshu keywords for Liaoning motorcycle travel data."""
import subprocess
import sys
import os
import json
import time
from datetime import datetime

WORKDIR = r'C:\Users\Administrator\.openclaw\workspace\MediaCrawler'
PYTHON = os.path.join(WORKDIR, '.venv', 'Scripts', 'python')
MAIN = os.path.join(WORKDIR, 'main.py')
CONTENT_FILE = os.path.join(WORKDIR, 'data', 'xhs', 'jsonl', 'search_contents_2026-06-03.jsonl')

# Remaining 7 keywords
KEYWORDS = [
    "辽宁沿海摩旅",
    "沈阳摩旅路线",
    "大连滨海路骑行",
    "本桓公路摩托",
    "丹东绿江村骑行",
    "辽宁山路压弯",
    "鞍山摩旅路线",
]

def count_lines():
    try:
        with open(CONTENT_FILE, 'r', encoding='utf-8') as f:
            return len(f.readlines())
    except:
        return 0

def run_keyword(kw):
    print(f"\n{'='*60}")
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Keyword: {kw}")
    print(f"{'='*60}")

    before = count_lines()
    print(f"Before: {before} content lines")

    cmd = [
        PYTHON, MAIN,
        "--platform", "xhs",
        "--lt", "qrcode",
        "--keywords", kw,
        "--crawler_max_notes_count", "20",
    ]

    result = subprocess.run(cmd, cwd=WORKDIR, capture_output=True, text=True, timeout=600)

    after = count_lines()
    new = after - before
    print(f"After: {after} content lines (new: {new})")

    out_lines = result.stdout.strip().split('\n')
    for l in out_lines[-5:]:
        if 'ERROR' in l or 'finished' in l.lower() or 'Crawler' in l or 'Sleep' in l:
            print(f"  {l}")
    if result.returncode != 0:
        for l in out_lines[-3:]:
            print(f"  {l}")
        print(f"  stderr (last 300): {result.stderr[-300:]}")
        return False

    return True

def main():
    total_kw = len(KEYWORDS)
    print(f"Starting {total_kw} remaining keywords at {datetime.now().strftime('%H:%M:%S')}")
    print(f"Initial content lines: {count_lines()}")

    for i, kw in enumerate(KEYWORDS):
        print(f"\n--- Keyword {i+1}/{total_kw}: {kw} ---")

        success = run_keyword(kw)
        if success:
            print(f"  OK: {kw} completed")
        else:
            print(f"  FAIL: {kw} had errors, continuing...")

    final = count_lines()
    print(f"\n{'='*60}")
    print(f"ALL DONE at {datetime.now().strftime('%H:%M:%S')}")
    print(f"Total content lines: {final}")

if __name__ == '__main__':
    main()
