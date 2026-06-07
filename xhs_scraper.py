"""
独立小红书搜索采集器 - 直接用 Cookie 调用小红书搜索 API
不依赖 xhshow 签名库
"""
import requests
import json
import time
import re
import os
from datetime import datetime

# Cookie 配置
COOKIE = 'a1=19e69ad5bb9q7zw8k7pok7jyeya06x3a55ca5uhlc50000307356; webId=2779a142fcfcfc60c228994889c521cd; gid=yjdKj0fKf42yyjdKj0f2D27xDjAWuEYTWUlTS1SWVvdv00288KCq02888q8Wq2K84S8JSqJd; abRequestId=2779a142fcfcfc60c228994889c521cd; ets=1779889525696; x-rednote-datactry=CN; x-rednote-holderctry=CN; web_session=040069bb62b63f5a5050c32016384bd1d1df10; id_token=VjEAAMZ0v2u1NECQEmjaVbe86xt3WRj0rbAJ0Y2qz7Tv9BpLC139rWS56/tZr1K7zILmikWgzY0RaWzaKmobr8zmPIK7Ww/ALMQHuM4b/R+a2ICykosYyOCM2UDLKa4/zarBxwji; webBuild=6.15.2; acw_tc=0ad6222d17807591472364775e197aad11b85eb93d5273e4c817a99efa7b54; xsecappid=xhs-pc-web; unread={%22ub%22:%226a2213300000000022015319%22%2C%22ue%22:%226a1b748b000000000702c35e%22%2C%22uc%22:31}; websectiga=6169c1e84f393779a5f7de7303038f3b47a78e47be716e7bec57ccce17d45f99; sec_poison_id=c7df7266-2fe9-478c-90b8-6bf9a6749122; loadts=1780760419663'

# 从 Cookie 中提取关键参数
def extract_cookie_value(cookie, key):
    for part in cookie.split(';'):
        part = part.strip()
        if part.startswith(key + '='):
            return part[len(key)+1:]
    return ''

A1 = extract_cookie_value(COOKIE, 'a1')
WEB_SESSION = extract_cookie_value(COOKIE, 'web_session')
X_S = ''  # 需要签名，但搜索接口可能不需要

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
    'Cookie': COOKIE,
    'Origin': 'https://www.xiaohongshu.com',
    'Referer': 'https://www.xiaohongshu.com/explore',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'zh-CN,zh;q=0.9',
}

def search_xhs(keyword, page=1, page_size=20):
    """搜索小红书笔记"""
    url = 'https://edith.xiaohongshu.com/api/sns/web/v1/search/notes'
    params = {
        'keyword': keyword,
        'page': str(page),
        'page_size': str(page_size),
        'sort': 'general',
        'note_type': '0',  # 不限
    }
    
    # 尝试 GET 方式
    try:
        r = requests.get('https://www.xiaohongshu.com/search_result', 
                        params={'keyword': keyword, 'source': 'web_search_result_notes'},
                        headers=HEADERS, timeout=15)
        print(f"  Search page: {r.status_code}, len={len(r.text)}")
        return r
    except Exception as e:
        print(f"  FAIL: {e}")
        return None

def extract_notes_from_html(html):
    """从 HTML 页面中提取笔记卡片信息"""
    notes = []
    
    # 尝试找 JSON 数据
    # 1. window.__INITIAL_STATE__
    match = re.search(r'window\.__INITIAL_STATE__\s*=\s*({.*?});', html, re.DOTALL)
    if match:
        try:
            data = json.loads(match.group(1))
            print(f"  Found __INITIAL_STATE__ keys: {list(data.keys())}")
            # 尝试各种可能的路径
            for path in ['note', 'searchResult', 'feed']:
                if path in data:
                    print(f"  Found {path}: {json.dumps(data[path], ensure_ascii=False)[:500]}")
            return data
        except:
            pass
    
    # 2. 找笔记列表 JSON
    match = re.search(r'<script[^>]*id="__NEXT_DATA__"[^>]*>({.*?})</script>', html, re.DOTALL)
    if match:
        try:
            data = json.loads(match.group(1))
            print(f"  Found __NEXT_DATA__")
            return data
        except:
            pass
    
    # 3. 找 noteItem 模式
    items = re.findall(r'noteItem["\']?\s*[:=]\s*({[^;]+})', html)
    if items:
        print(f"  Found {len(items)} noteItems")
        for item in items[:3]:
            print(f"  Sample: {item[:200]}")
    
    # 4. 找直接包含的笔记标题/链接
    titles = re.findall(r'"note_card_title"[^:]*:\s*"([^"]+)"', html)
    if titles:
        print(f"  Found {len(titles)} note card titles: {titles[:5]}")
    
    return None

keywords = [
    "摩旅路线", "摩托车路书", "摩旅攻略",
    "骑行路线推荐", "摩托车旅行路线"
]

for kw in keywords:
    print(f"\n{'='*50}")
    print(f"搜索: {kw}")
    result = search_xhs(kw)
    if result and result.status_code == 200:
        extract_notes_from_html(result.text)
    time.sleep(3)
