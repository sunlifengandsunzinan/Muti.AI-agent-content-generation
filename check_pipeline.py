import json

# 检查 export
with open("D:\\moto\\data\\raw\\openclaw_export.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print("=== openclaw_export.json ===")
print("Items:", len(data.get("items", [])))
print("Exported at:", data.get("exported_at", "N/A"))

# 检查 candidates
with open("D:\\moto\\data\\raw\\openclaw_candidates.json", "r", encoding="utf-8") as f:
    candidates = json.load(f)
print("\n=== openclaw_candidates.json ===")
print("Items:", len(candidates))

# 检查 normalized
with open("D:\\moto\\data\\normalized\\candidate_spots.json", "r", encoding="utf-8") as f:
    spots = json.load(f)
print("\n=== candidate_spots.json ===")
print("Items:", len(spots))
for s in spots:
    print(f"  - [{s.get('city','?')}] {s.get('name','?')} ({s.get('spot_type','?')})")
