import json
d = json.load(open("/root/moto/data/raw/gpx_queue_status.json"))
for r in d.get("recent_results", [])[-1:]:
    print(json.dumps(r.get("detail", ""), ensure_ascii=False)[200:500])
