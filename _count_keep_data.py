import json, os, re
from collections import defaultdict

root = r'D:\Keep轨迹素材'

# 读取精选索引
with open(os.path.join(root, '精选素材索引.json'), 'r', encoding='utf-8') as f:
    index = json.load(f)

# 统计所有图片
total_files = 0
total_km = 0
total_cal = 0
monthly = defaultdict(lambda: {'count': 0, 'km': 0})
yearly = defaultdict(lambda: {'count': 0, 'km': 0})

for entry in index:
    fname = os.path.basename(entry['file'])
    # Parse: YYYY-MM-DD_XX.Xkm_YYmin_Zhr.jpg
    m = re.search(r'(\d{4})-(\d{2})-\d{2}_([\d.]+)km', fname)
    if m:
        year = m.group(1)
        month = m.group(2)
        km = float(m.group(3))
        total_files += 1
        total_km += km
        monthly[f'{year}-{month}']['count'] += 1
        monthly[f'{year}-{month}']['km'] += km
        yearly[year]['count'] += 1
        yearly[year]['km'] += km
        if entry.get('calories'):
            total_cal += entry['calories']

print(f"=== Keep 轨迹数据统计 ===")
print(f"总跑步次数: {total_files}")
print(f"总里程: {total_km:.1f} km")
print(f"总消耗: {total_cal:,} 千卡")
print()

print("=== 逐年统计 ===")
for year in sorted(yearly.keys()):
    d = yearly[year]
    print(f"  {year}: {d['count']}次, {d['km']:.1f}km")

print()
print("=== 各月轨迹数 ===")
for ym in sorted(monthly.keys()):
    d = monthly[ym]
    print(f"  {ym}: {d['count']}条, {d['km']:.0f}km")

# 统计最长/最短/平均
dists = []
for entry in index:
    fname = os.path.basename(entry['file'])
    m = re.search(r'_([\d.]+)km', fname)
    if m:
        dists.append(float(m.group(1)))

dists.sort()
print()
print(f"最长单次: {dists[-1]:.1f} km" if dists else "")
print(f"最短单次: {dists[0]:.1f} km" if dists else "")
avg = sum(dists)/len(dists) if dists else 0
print(f"平均每次: {avg:.1f} km")

# 马拉松次数
marathon = sum(1 for d in dists if d >= 42.195)
half = sum(1 for d in dists if d >= 21.0975)
print(f"全马(>=42.2km): {marathon}次")
print(f"半马(>=21.1km): {half}次")
