import json
d = json.load(open("/root/moto/data/raw/gpx_queue_status.json"))
print("State:", d.get("state"))
print("Stage:", d.get("current_stage"))
print("Task:", d.get("current_task"))
print("URL:", d.get("current_url"))
print("Processed:", d.get("processed_count"), "Success:", d.get("success_count"), "Fail:", d.get("failure_count"))
r = d.get("recent_results", [])
if r:
    print("Last result:", json.dumps(r[-1], ensure_ascii=False)[:300])
