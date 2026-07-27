import json

with open(r'C:\Users\Administrator\.openclaw\workspace\shared\data.json', 'rb') as f:
    data = json.load(f)

vs = data['creatorCenter']['lastSnapshot']['videos']
print("Videos in lastSnapshot:")
for v in vs:
    print(f'  {v.get("title","?"):30s} plays={v.get("plays","?")} date={v.get("date","?")}')

print("\n--- postPublishTracking ---")
pt = data.get('postPublishTracking', {}).get('videos', [])
for v in pt:
    print(f'  {v.get("title","?"):35s} plays={v.get("latestPlays","?")} status={v.get("status","?")} checkpoints={v.get("checkpoints","")}')
