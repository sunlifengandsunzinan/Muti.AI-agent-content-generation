import json

with open(r'C:\Users\Administrator\.openclaw\workspace\shared\data.json', 'rb') as f:
    data = json.load(f)

cc = data.get('creatorCenter', {})
print('creatorCenter keys:', list(cc.keys()))

ls = cc.get('lastSnapshot', {})
print('lastSnapshot keys:', list(ls.keys()))

ov = ls.get('overview', {})
print('overview:', json.dumps(ov, ensure_ascii=False))

vs = ls.get('videos', [])
print(f'videos count: {len(vs)}')
for v in vs[-8:]:
    print(f'  {v.get("title","?")} | 播放:{v.get("plays","?")} | 日期:{v.get("date","?")}')

dd = cc.get('depthData', [])
print(f'depthData count: {len(dd)}')
keys = list(dd.keys())[-6:]
for k in keys:
    v = dd[k]
    print(f'  {v.get("title","?")} | 完播:{v.get("completionRate","?")} | 2s跳出:{v.get("exit2sRate","?")} | 涨粉:{v.get("followers","?")} | fansPlay%:{v.get("fansPlayPercent","?")} | recommend%:{v.get("recommendPercent","?")}')

fa = cc.get('followerAnalysis', {})
print('followerAnalysis keys:', list(fa.keys()))
if 'recentVideos' in fa:
    for v in fa['recentVideos']:
        print(f'  {v.get("title","?")} | 涨粉:{v.get("followerGain","?")} | 播放:{v.get("plays","?")} | rate:{v.get("ratePerThousand","?")}')

pt = data.get('postPublishTracking', {}).get('videos', [])
print(f'\npostPublishTracking count: {len(pt)}')
for v in pt[-3:]:
    print(f'  {v.get("title","?")} | 播放:{v.get("latestPlays","?")} | 状态:{v.get("status","?")}')

bm = data.get('benchmarking', {})
print(f'\nbenchmarking keys: {list(bm.keys())}')
bv = bm.get('videos', [])
print(f'benchmarking videos: {len(bv)}')
for v in bv[-5:]:
    print(f'  {v.get("title","?")} | {v.get("author","?")} | 播放:{v.get("plays","?")} | 类型:{v.get("type","?")}')

an = data.get('analyses', {})
print(f'\nanalyses: {json.dumps(an, ensure_ascii=False)[:500]}')

events = data.get('events', [])
print(f'\nevents: {len(events)} items')
for e in events[-3:]:
    print(f'  {e.get("type","?")} | done:{e.get("done","?")} | desc:{str(e.get("description",""))[:80]}')
