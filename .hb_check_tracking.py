import json
d = json.load(open(r'C:\Users\Administrator\.openclaw\workspace\shared\data.json', 'r', encoding='utf-8'))

# Post-publish tracking
ppt = d.get('postPublishTracking', {})
vs = ppt.get('videos', [])
print("=== Post-Publish Tracking ===")
for v in vs:
    print(f'  {v["title"]} | status={v["status"]} | plays={v.get("plays","?")} | latestPlays={v.get("latestPlays","?")}')

# Creator center videos
cr = d.get('creatorCenter', {}).get('lastSnapshot', {}).get('videos', [])
print("\n=== Creator Center Videos ===")
for v in cr:
    print(f'  {v["title"]} | pub={v.get("publishDate","?")} | plays={v.get("playCount","?")}')
