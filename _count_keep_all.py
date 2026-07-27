import os, re
from collections import defaultdict

root = r'D:\Keep轨迹素材'

total_count = 0
total_km = 0.0
yearly = defaultdict(lambda: {'count':0, 'km':0.0})

for dirpath, dirnames, filenames in os.walk(root):
    for fn in filenames:
        if not fn.endswith('.jpg'):
            continue
        total_count += 1
        # Parse filename: YYYY-MM-DD_XX.Xkm_YYmin_Zhr.jpg
        m = re.search(r'(\d{4})-(\d{2})-\d{2}_([\d.]+)km', fn)
        if m:
            year = m.group(1)
            km = float(m.group(3))
            total_km += km
            yearly[year]['count'] += 1
            yearly[year]['km'] += km

print(f"全量 JPG 总数: {total_count}")
print(f"可解析总里程: {total_km:.1f} km")
print()
print("逐年统计:")
for y in sorted(yearly.keys()):
    d = yearly[y]
    print(f"  {y}: {d['count']}次, {d['km']:.1f}km")
