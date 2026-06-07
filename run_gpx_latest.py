import sys, os, json, subprocess

sys.path.insert(0, '/root/moto')
os.chdir('/root/moto')

# 找到最新的 search_*.json
import glob
files = sorted(glob.glob('/root/moto/data/raw/search_*.json'))
if not files:
    print('No search JSON found')
    sys.exit(1)

latest = files[-1]
print(f'Processing: {latest}')

# 读取并重置
with open(latest, 'r') as f:
    data = json.load(f)
for kw, items in data.get('results', {}).items():
    if isinstance(items, list):
        for item in items:
            if isinstance(item, dict) and 'gpx_queue_status' in item:
                del item['gpx_queue_status']
with open(latest, 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# 跑 GPX
from app.services import gpx_service
result = gpx_service.run_gpx_queue_file(latest)
print(json.dumps(result, ensure_ascii=False, indent=2))
