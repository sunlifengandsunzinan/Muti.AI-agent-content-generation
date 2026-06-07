import json
d = json.load(open("/root/moto/data/raw/gpx_queue_status.json"))
for r in d.get("recent_results", [])[-3:]:
    print(json.dumps(r, ensure_ascii=False, indent=2)[:400])
