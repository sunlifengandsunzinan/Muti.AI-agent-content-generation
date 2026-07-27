import requests, json, re

url = 'https://www.douyin.com/search/48881167027?type=user'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
}
try:
    r = requests.get(url, headers=headers, timeout=15)
    matches = re.findall(r'<script[^>]*>window\.__INITIAL_STATE__\s*=\s*({.*?})</script>', r.text, re.DOTALL)
    if matches:
        data = json.loads(matches[0])
        print(json.dumps(data, ensure_ascii=False, indent=2)[:3000])
    else:
        print(f'Status: {r.status_code}, Length: {len(r.text)}')
        titles = re.findall(r'<title>(.*?)</title>', r.text)
        if titles:
            print(f'Title: {titles[0]}')
        # search for nickname/signature in raw HTML
        name_match = re.search(r'nickname["\']\s*[:=]\s*["\']([^"\']+)["\']', r.text, re.I)
        if name_match:
            print(f'Nickname: {name_match.group(1)}')
        desc_match = re.search(r'signature["\']\s*[:=]\s*["\']([^"\']+)["\']', r.text, re.I)
        if desc_match:
            print(f'Signature: {desc_match.group(1)}')
        # also search for sec_uid which might be present
        uid_match = re.search(r'sec_uid["\']\s*[:=]\s*["\']([^"\']+)["\']', r.text, re.I)
        if uid_match:
            print(f'SecUid: {uid_match.group(1)}')
        print('---First 1500 chars---')
        print(r.text[:1500])
except Exception as e:
    print(f'Error: {e}')
