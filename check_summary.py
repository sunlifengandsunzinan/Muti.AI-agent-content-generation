import sys, json
d = json.load(sys.stdin)
keys = ["state","processed_count","success_count","failure_count","total_urls","done_count","pending_count"]
print(json.dumps({k:d.get(k) for k in keys}, indent=2, ensure_ascii=False))
