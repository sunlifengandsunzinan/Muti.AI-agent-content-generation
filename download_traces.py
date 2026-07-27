"""
批量下载Keep轨迹图 + 按年月分类 + 精选代表性轨迹
"""
import openpyxl
import requests
import os
import json
from collections import defaultdict
from urllib.parse import urlparse

# ===== 配置 =====
EXCEL_PATH = r'D:\小红书素材\494626.xlsx'
OUTPUT_DIR = r'D:\Keep轨迹素材'
MAX_RETRIES = 3
TIMEOUT = 20

# ===== 读取Excel =====
print('读取Excel...')
wb = openpyxl.load_workbook(EXCEL_PATH, data_only=True)
ws = wb['运动记录']

def to_float(v):
    if v is None or v == 'NULL' or v == 'None': return 0.0
    try: return float(v)
    except: return 0.0

traces = []  # [{year, month, date, dist, duration, pace, hr, url}, ...]
idx = 0
for row in ws.iter_rows(min_row=2, values_only=True):
    idx += 1
    rtype = str(row[0]) if row[0] else ''
    if rtype != '跑步':
        continue
    start = str(row[2]) if row[2] else ''
    trace_url = row[9] if len(row) > 9 else (row[8] if len(row) > 8 else None)
    if not trace_url or str(trace_url) == 'NULL' or str(trace_url).strip() == '':
        continue
    url = str(trace_url).strip()
    if not url.startswith('http'):
        continue

    dist = to_float(row[5]) / 1000  # km
    duration = to_float(row[1]) / 60  # min
    pace = duration / dist if dist > 0 else 0
    calories = to_float(row[4])
    avg_hr = to_float(row[6])
    max_hr = to_float(row[7])

    if start and start != 'None' and len(start) >= 7:
        year = start[:4]
        month = start[5:7]
        date_key = start[:10]
    else:
        year, month, date_key = 'unknown', 'unknown', 'unknown'

    traces.append({
        'year': year,
        'month': month,
        'date': date_key,
        'dist': dist,
        'duration': duration,
        'pace': pace,
        'calories': calories,
        'avg_hr': avg_hr,
        'max_hr': max_hr,
        'url': url,
        'start': start,
        'excel_row': idx
    })

print(f'共 {len(traces)} 条跑步轨迹记录')

# ===== 创建目录结构 =====
def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

ensure_dir(OUTPUT_DIR)

# 按年月分组
by_ym = defaultdict(list)
for t in traces:
    by_ym[f'{t["year"]}-{t["month"]}'].append(t)

# ===== 精选代表性轨迹 =====
print('\n精选代表性轨迹...')

selected = {}  # 分类名 -> list of traces

# 1. 最长距离 TOP5
selected['最长距离_TOP5'] = sorted(traces, key=lambda t: t['dist'], reverse=True)[:5]

# 2. 最快配速 TOP5（距离>5km）
fast_qualified = [t for t in traces if t['dist'] >= 5]
selected['最快配速_TOP5'] = sorted(fast_qualified, key=lambda t: t['pace'])[:5]

# 3. 每年最高月跑量
for y in sorted(set(t['year'] for t in traces)):
    year_traces = [t for t in traces if t['year'] == y]
    monthly_vol = defaultdict(float)
    for t in year_traces:
        monthly_vol[t['month']] += t['dist']
    if monthly_vol:
        top_month = max(monthly_vol, key=monthly_vol.get)
        # 找这个月最具代表性的单次（最长距离）
        month_traces = [t for t in year_traces if t['month'] == top_month]
        best = max(month_traces, key=lambda t: t['dist'])
        selected[f'{y}年最高月跑量_{top_month}月'] = [best]

# 4. 每个月的首次和最后一次跑步（用于"从开始到现在"对比）
# 只挑几个有代表性的月份
for ym in sorted(by_ym.keys()):
    month_traces = sorted(by_ym[ym], key=lambda t: t['start'])
    if len(month_traces) >= 3:
        selected[f'{ym}_首次'] = [month_traces[0]]
        if len(month_traces) > 1:
            selected[f'{ym}_末次'] = [month_traces[-1]]

# 5. 心率最高/最有强度的几次（avg_hr>160 且距离>5km）
high_hr = [t for t in traces if t['avg_hr'] > 160 and t['dist'] > 5]
selected['高心率强度跑'] = sorted(high_hr, key=lambda t: t['avg_hr'], reverse=True)[:5]

# ===== 下载 =====
print('\n开始下载...')

downloaded = 0
failed = 0
all_ym_dirs = set()

session = requests.Session()
session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})

for t in traces:
    ym = f'{t["year"]}-{t["month"]}'
    ym_dir = os.path.join(OUTPUT_DIR, ym)
    all_ym_dirs.add(ym_dir)

    # 文件名：日期_距离_配速_心率.jpg
    filename = f'{t["date"]}_{t["dist"]:.1f}km_{t["pace"]:.0f}min_{int(t["avg_hr"]) if t["avg_hr"]>0 else 0}hr.jpg'
    # 避免特殊字符
    filename = filename.replace(':', '_').replace(' ', '_')
    filepath = os.path.join(ym_dir, filename)

    if os.path.exists(filepath):
        downloaded += 1
        continue

    ensure_dir(ym_dir)

    for attempt in range(MAX_RETRIES):
        try:
            r = session.get(t['url'], timeout=TIMEOUT)
            if r.status_code == 200 and len(r.content) > 1000:
                with open(filepath, 'wb') as f:
                    f.write(r.content)
                downloaded += 1
                if downloaded % 50 == 0:
                    print(f'  已下载 {downloaded}/{len(traces)}...')
                break
            else:
                failed += 1
                break
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                import time
                time.sleep(1)
            else:
                failed += 1

print(f'\n批量下载完成：成功 {downloaded} 张，失败 {failed} 张')

# ===== 保存精选列表 =====
print('\n生成精选素材索引...')
selected_meta = []
for category, items in selected.items():
    for t in items:
        ym = f'{t["year"]}-{t["month"]}'
        filename = f'{t["date"]}_{t["dist"]:.1f}km_{t["pace"]:.0f}min_{int(t["avg_hr"]) if t["avg_hr"]>0 else 0}hr.jpg'
        filepath = os.path.join(OUTPUT_DIR, ym, filename)
        selected_meta.append({
            'category': category,
            'file': filepath.replace('/', '\\'),
            'date': t['start'],
            'dist_km': round(t['dist'], 2),
            'pace_min_km': round(t['pace'], 1),
            'avg_hr': int(t['avg_hr']) if t['avg_hr'] > 0 else 0,
            'max_hr': int(t['max_hr']) if t['max_hr'] > 0 else 0,
            'calories': int(t['calories'])
        })

with open(os.path.join(OUTPUT_DIR, '精选素材索引.json'), 'w', encoding='utf-8') as f:
    json.dump(selected_meta, f, ensure_ascii=False, indent=2)

# 生成素材目录说明
with open(os.path.join(OUTPUT_DIR, '_素材目录说明.txt'), 'w', encoding='utf-8') as f:
    f.write(f'Keep轨迹素材库\n')
    f.write(f'来源: {EXCEL_PATH}\n')
    f.write(f'总数: {len(traces)} 条轨迹\n')
    f.write(f'下载: {downloaded} 张 (部分已存在跳过)\n')
    f.write(f'失败: {failed} 张\n\n')
    f.write(f'目录说明:\n')
    f.write(f'- 按月分组: YYYY-MM/ 文件夹\n')
    f.write(f'- 文件命名: 日期_距离_配速_心率.jpg\n\n')
    f.write(f'精选分类:\n')
    for item in selected_meta:
        f.write(f'  [{item["category"]}] {item["dist_km"]}km @ {item["pace_min_km"]}/km | {item["date"]}\n')

# 复制精选索引和素材说明给 media agent
import shutil
agent_media_dir = r'C:\Users\Administrator\.openclaw\workspace-media\keep_traces'
ensure_dir(agent_media_dir)
shutil.copy(os.path.join(OUTPUT_DIR, '精选素材索引.json'),
            os.path.join(agent_media_dir, '精选素材索引.json'))
shutil.copy(os.path.join(OUTPUT_DIR, '_素材目录说明.txt'),
            os.path.join(agent_media_dir, '_素材目录说明.txt'))

print(f'\n全部完成！素材已保存到: {OUTPUT_DIR}')
print(f'精选素材索引已同步到 agent: {agent_media_dir}')
print(f'\n=== 精选素材概览 ===')
for item in selected_meta:
    print(f'  [{item["category"]}] {item["dist_km"]}km | 配速{item["pace_min_km"]}/km | 心率{item["avg_hr"]}/{item["max_hr"]} | {item["date"]}')
