import requests
import re
import json

COOKIE = 'a1=19e69ad5bb9q7zw8k7pok7jyeya06x3a55ca5uhlc50000307356; webId=2779a142fcfcfc60c228994889c521cd; gid=yjdKj0fKf42yyjdKj0f2D27xDjAWuEYTWUlTS1SWVvdv00288KCq02888q8Wq2K84S8JSqJd; abRequestId=2779a142fcfcfc60c228994889c521cd; ets=1779889525696; x-rednote-datactry=CN; x-rednote-holderctry=CN; web_session=040069bb62b63f5a5050c32016384bd1d1df10; id_token=VjEAAMZ0v2u1NECQEmjaVbe86xt3WRj0rbAJ0Y2qz7Tv9BpLC139rWS56/tZr1K7zILmikWgzY0RaWzaKmobr8zmPIK7Ww/ALMQHuM4b/R+a2ICykosYyOCM2UDLKa4/zarBxwji; webBuild=6.15.2; acw_tc=0ad6222d17807591472364775e197aad11b85eb93d5273e4c817a99efa7b54; xsecappid=xhs-pc-web; websectiga=6169c1e84f393779a5f7de7303038f3b47a78e47be716e7bec57ccce17d45f99; sec_poison_id=c7df7266-2fe9-478c-90b8-6bf9a6749122; loadts=1780760419663'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
    'Cookie': COOKIE,
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9',
}

r = requests.get('https://www.xiaohongshu.com/search_result?keyword=%E6%91%A9%E6%97%85%E8%B7%AF%E7%BA%BF&source=web_search_result_notes', headers=HEADERS, timeout=30)
html = r.text

# Save raw
with open('xhs_raw.html', 'w', encoding='utf-8') as f:
    f.write(html)

# Find all script tags that might contain data
scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
for i, s in enumerate(scripts):
    s = s.strip()
    if len(s) > 100 and ('note' in s.lower() or 'search' in s.lower() or 'noteItem' in s or 'feed' in s):
        print(f"\n=== Script #{i} (len={len(s)}) ===")
        # Save matched scripts
        with open(f'xhs_script_{i}.txt', 'w', encoding='utf-8') as f:
            f.write(s[:5000])

# Look for any JSON-like data
for pattern in [
    r'window\.__INITIAL_STATE__\s*=\s*({.*?});',
    r'window\.__NUXT__\s*=\s*({.*?});',
    r'<script id="__NEXT_DATA__"[^>]*>({.*?})</script>',
    r'window\.__ROOT_DATA__\s*=\s*({.*?});',
]:
    match = re.search(pattern, html, re.DOTALL)
    if match:
        print(f"\n=== Matched: {pattern[:40]} ===")
        print(match.group(1)[:1000])
    else:
        print(f"No match: {pattern[:40]}")
