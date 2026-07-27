import openpyxl
import json
from collections import Counter, defaultdict

wb = openpyxl.load_workbook(r'D:\小红书素材\494626.xlsx', data_only=True)
ws = wb['运动记录']

def to_float(v):
    if v is None or v == 'NULL' or v == 'None': return 0.0
    try: return float(v)
    except: return 0.0

records = []
for row in ws.iter_rows(min_row=2, values_only=True):
    rec = {
        'type': str(row[0]) if row[0] else '',
        'duration_s': to_float(row[1]),
        'start': str(row[2]) if row[2] else '',
        'end': str(row[3]) if row[3] else '',
        'calories': to_float(row[4]),
        'distance_m': to_float(row[5]),
        'avg_hr': to_float(row[6]),
        'max_hr': to_float(row[7]),
    }
    records.append(rec)

print(f'总记录数: {len(records)}')

type_counter = Counter(r['type'] for r in records)
print(f'\n运动类型分布:')
for t, c in type_counter.most_common():
    print(f'  {t}: {c}次')

runs = [r for r in records if r['type'] == '跑步']
walk = [r for r in records if r['type'] == '行走']
fitness = [r for r in records if r['type'] == '健身']
cycle = [r for r in records if r['type'] == '骑行']

print(f'\n跑步次数: {len(runs)}')
print(f'行走次数: {len(walk)}')
print(f'健身次数: {len(fitness)}')
print(f'骑行次数: {len(cycle)}')

total_distance = sum(r['distance_m'] for r in runs) / 1000
total_duration = sum(r['duration_s'] for r in runs) / 3600
total_calories = sum(r['calories'] for r in runs)

print(f'\n跑步总距离: {total_distance:.2f} km')
print(f'跑步总时长: {total_duration:.2f} 小时 ({total_duration:.0f}小时)')
print(f'跑步总消耗: {total_calories:.0f} 千卡')
avg_pace_min = total_duration * 60 / total_distance if total_distance else 0
pace_sec = (avg_pace_min - int(avg_pace_min)) * 60
print(f'平均配速: {int(avg_pace_min)}\'{int(pace_sec):02d}\"/km')

# 按年月统计
monthly = defaultdict(lambda: {'count': 0, 'distance': 0.0, 'duration': 0.0, 'calories': 0.0, 'hrs': []})
for r in runs:
    if r['start'] and r['start'] != 'None':
        y = r['start'][:4]
        m = r['start'][5:7]
        key = f'{y}-{m}'
        monthly[key]['count'] += 1
        monthly[key]['distance'] += r['distance_m']
        monthly[key]['duration'] += r['duration_s']
        monthly[key]['calories'] += r['calories']
        if r['avg_hr'] > 0:
            monthly[key]['hrs'].append(r['avg_hr'])

print(f'\n--- 月度跑步统计 ---')
for key in sorted(monthly.keys()):
    d = monthly[key]
    dist_km = d['distance'] / 1000
    hours = d['duration'] / 3600
    pace = hours * 60 / dist_km if dist_km > 0 else 0
    avg_hr = sum(d['hrs']) / len(d['hrs']) if d['hrs'] else 0
    print(f'{key}: {d["count"]}次 {dist_km:.1f}km {hours:.1f}h 配速{pace:.0f}\'/km 心率{avg_hr:.0f} 消耗{int(d["calories"])}千卡')

# 年度统计
yearly = defaultdict(lambda: {'count': 0, 'distance': 0.0, 'duration': 0.0, 'calories': 0.0})
for r in runs:
    if r['start'] and r['start'] != 'None':
        y = r['start'][:4]
        yearly[y]['count'] += 1
        yearly[y]['distance'] += r['distance_m']
        yearly[y]['duration'] += r['duration_s']
        yearly[y]['calories'] += r['calories']

print(f'\n--- 年度跑步统计 ---')
for key in sorted(yearly.keys()):
    d = yearly[key]
    dist_km = d['distance'] / 1000
    hours = d['duration'] / 3600
    pace = hours * 60 / dist_km if dist_km > 0 else 0
    print(f'{key}: {d["count"]}次 {dist_km:.1f}km {hours:.1f}h 配速{pace:.0f}\'/km 消耗{int(d["calories"])}千卡')

# 最近10次
print(f'\n--- 最近10次跑步 ---')
recent_runs = runs[-10:]
for r in reversed(recent_runs):
    dist = r['distance_m'] / 1000
    mins = r['duration_s'] / 60
    pace = mins / dist if dist > 0 else 0
    print(f'{r["start"]}: {dist:.2f}km {mins:.0f}分 配速{pace:.0f}\'/km 心率{int(r["avg_hr"])}/{int(r["max_hr"])}')

# 导出跑步数据JSON
run_export = []
for r in runs:
    dist_km = round(r['distance_m'] / 1000, 2)
    mins = round(r['duration_s'] / 60, 1)
    if dist_km > 0:
        pace = round(mins / dist_km, 1)
    else:
        pace = 0
    run_export.append({
        'start': r['start'],
        'distance_km': dist_km,
        'duration_min': mins,
        'pace_min_per_km': pace,
        'calories': int(r['calories']),
        'avg_hr': int(r['avg_hr']) if r['avg_hr'] > 0 else 0,
        'max_hr': int(r['max_hr']) if r['max_hr'] > 0 else 0
    })

# 导出文字版给AI训练
lines = []
lines.append('# 峰峰的Keep跑步数据（共811条记录）\n')
lines.append(f'## 数据概览\n')
lines.append(f'- 总记录: 2267条（跑步811次 + 行走589次 + 健身854次 + 骑行13次）')
lines.append(f'- 跑步总距离: {total_distance:.2f} 公里')
lines.append(f'- 跑步总时长: {total_duration:.1f} 小时 ({int(total_duration)}小时)')
lines.append(f'- 跑步总消耗: {int(total_calories)} 千卡')
lines.append(f'- 平均配速: {int(avg_pace_min)}\'{int(pace_sec):02d}\"/km\n')

lines.append(f'## 年度跑步里程\n')
for key in sorted(yearly.keys()):
    d = yearly[key]
    lines.append(f'- {key}: {d["count"]}次 {d["distance"]/1000:.1f}公里 {d["duration"]/3600:.1f}小时')

lines.append(f'\n## 月度跑步统计（最近24个月）\n')
sorted_months = sorted(monthly.keys())
for key in sorted_months[-24:]:
    d = monthly[key]
    dist_km = d['distance'] / 1000
    lines.append(f'- {key}: {d["count"]}次 {dist_km:.1f}公里')

lines.append(f'\n## 近30次跑步记录\n')
recent_30 = reversed(runs[-30:])
for r in recent_30:
    dist = r['distance_m'] / 1000
    mins = r['duration_s'] / 60
    pace = mins / dist if dist > 0 else 0
    lines.append(f'- {r["start"]} | {dist:.2f}公里 | {mins:.0f}分钟 | 配速{pace:.1f}\'/km | 心率{int(r["avg_hr"]) if r["avg_hr"]>0 else "-"}/{int(r["max_hr"]) if r["max_hr"]>0 else "-"}')

# 额外：最长距离跑、最快配速跑
longest_run = max(runs, key=lambda r: r['distance_m'])
fastest_run = min((r for r in runs if r['distance_m'] > 1000), key=lambda r: r['duration_s'] / r['distance_m'])

lines.append(f'\n## 个人最佳\n')
ld = longest_run['distance_m'] / 1000
lp = longest_run['duration_s'] / 60 / ld
lines.append(f'- 最长单次: {ld:.2f}公里 {longest_run["start"]} 配速{lp:.1f}\'/km')
fd = fastest_run['distance_m'] / 1000
fp = fastest_run['duration_s'] / 60 / fd
lines.append(f'- 最快配速: {fp:.1f}\'/km {fastest_run["start"]} {fd:.2f}公里')

output = '\n'.join(lines)

with open(r'C:\Users\Administrator\.openclaw\workspace-media\keep_跑步数据报告.txt', 'w', encoding='utf-8') as f:
    f.write(output)

with open(r'C:\Users\Administrator\.openclaw\workspace-media\keep_data_export.json', 'w', encoding='utf-8') as f:
    json.dump(run_export, f, ensure_ascii=False, indent=2)

print(f'\n✅ 数据已导出')
print(f'   - workspace-media/keep_跑步数据报告.txt (文字版)')
print(f'   - workspace-media/keep_data_export.json (JSON版)')
print(f'   文字版大小: {len(output)} 字符')
