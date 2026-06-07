import subprocess, json, sys, os, urllib.request, urllib.parse, re, time

# 摩托范路书搜索
SEARCH_URLS = [
    "https://moto.yiche.com/route/",
    "https://moto.yiche.com/route/list?keywords=",
    "https://moto.yiche.com/route/search?keyword=",
]

keywords = ["摩旅路线","摩托车路书","骑行路线","摩旅"]

for kw in keywords:
    url = f"https://moto.yiche.com/route/search?keyword={urllib.parse.quote(kw)}"
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://moto.yiche.com/route/"
    })
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        data = resp.read().decode('utf-8', errors='replace')
        print(f"=== {kw} === (len={len(data)})")
        print(data[:2000])
    except Exception as e:
        print(f"FAIL {kw}: {e}")
        time.sleep(2)

# 尝试获取首页路书列表
req = urllib.request.Request(SEARCH_URLS[0], headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"})
try:
    resp = urllib.request.urlopen(req, timeout=15)
    html = resp.read().decode('utf-8', errors='replace')
    # find any JSON data embedded
    scripts = re.findall(r'window\.__INITIAL_STATE__\s*=\s*({.*?});', html, re.DOTALL)
    for s in scripts:
        data = json.loads(s)
        print(json.dumps(data, ensure_ascii=False, indent=2)[:3000])
    # Also check for route data
    routes = re.findall(r'routeList["\':]*\s*[=:]\s*(\[.*?\])\s*[,;]', html, re.DOTALL)
    for r in routes:
        print("ROUTE DATA:", r[:2000])
except Exception as e:
    print(f"FAIL index: {e}")
