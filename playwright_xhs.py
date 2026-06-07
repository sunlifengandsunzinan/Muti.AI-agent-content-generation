"""
通过 Playwright 浏览器自动化采集小红书搜索笔记
直接在本地 Chrome 上操作，所有签名自动处理
"""
from playwright.sync_api import sync_playwright
import json
import time
import os
import re

COOKIE_STR = 'a1=19e69ad5bb9q7zw8k7pok7jyeya06x3a55ca5uhlc50000307356; webId=2779a142fcfcfc60c228994889c521cd; gid=yjdKj0fKf42yyjdKj0f2D27xDjAWuEYTWUlTS1SWVvdv00288KCq02888q8Wq2K84S8JSqJd; abRequestId=2779a142fcfcfc60c228994889c521cd; ets=1779889525696; x-rednote-datactry=CN; x-rednote-holderctry=CN; web_session=040069bb62b63f5a5050c32016384bd1d1df10; id_token=VjEAAMZ0v2u1NECQEmjaVbe86xt3WRj0rbAJ0Y2qz7Tv9BpLC139rWS56/tZr1K7zILmikWgzY0RaWzaKmobr8zmPIK7Ww/ALMQHuM4b/R+a2ICykosYyOCM2UDLKa4/zarBxwji; webBuild=6.15.2; acw_tc=0ad6222d17807591472364775e197aad11b85eb93d5273e4c817a99efa7b54; xsecappid=xhs-pc-web; unread={%22ub%22:%226a2213300000000022015319%22%2C%22ue%22:%226a1b748b000000000702c35e%22%2C%22uc%22:31}; websectiga=6169c1e84f393779a5f7de7303038f3b47a78e47be716e7bec57ccce17d45f99; sec_poison_id=c7df7266-2fe9-478c-90b8-6bf9a6749122; loadts=1780760419663'

def parse_cookies(cookie_str):
    cookies = []
    for item in cookie_str.split(';'):
        item = item.strip()
        if '=' in item:
            name, value = item.split('=', 1)
            cookies.append({'name': name.strip(), 'value': value.strip(), 'domain': '.xiaohongshu.com', 'path': '/'})
    return cookies

keywords = [
    "摩旅路线", "摩托车路书", "摩旅攻略",
    "骑行路线", "摩旅路书"
]

output_path = r'D:\MediaCrawlerResult\小红书_摩旅路书'
os.makedirs(output_path, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36'
    )
    
    # Add cookies
    for c in parse_cookies(COOKIE_STR):
        context.add_cookies([c])
    
    page = context.new_page()
    all_notes = []
    
    for kw in keywords:
        print(f"\n=== 搜索: {kw} ===")
        try:
            page.goto(f'https://www.xiaohongshu.com/search_result?keyword={kw}&source=web_search_result_notes', 
                     wait_until='networkidle', timeout=30000)
            time.sleep(3)
            
            # Try to get JSON data from API responses
            notes_data = page.evaluate('''() => {
                // Find all note items from the page
                const items = document.querySelectorAll('[id^="note-item-"], [class*="note-item"], [class*="feeds"] a');
                const results = [];
                items.forEach(item => {
                    const link = item.href || item.getAttribute('href');
                    const title = item.querySelector('[class*="title"], [class*="note"]')?.textContent?.trim();
                    if (link && link.includes('discovery/item/')) {
                        results.push({ url: link.startsWith('http') ? link : 'https://www.xiaohongshu.com' + link, title: title });
                    }
                });
                
                // Also try to extract from page data
                const serialized = document.getElementById('__NEXT_DATA__')?.textContent;
                if (serialized) return { serialized, items: results };
                return { items: results };
            }''')
            
            print(f"  找到 {len(notes_data.get('items', []))} 个笔记链接")
            
            # If serialized data found, parse it
            if 'serialized' in notes_data:
                data = json.loads(notes_data['serialized'])
                print(f"  有 __NEXT_DATA__")
                with open(f'{output_path}/{kw}_nextdata.json', 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            
            # Save found items
            items = notes_data.get('items', [])
            for item in items[:5]:
                print(f"  {item.get('title', 'N/A')[:50]} -> {item.get('url', 'N/A')}")
            
            all_notes.extend(items)
            time.sleep(2)
            
        except Exception as e:
            print(f"  FAIL: {e}")
    
    # Save all results
    with open(f'{output_path}/all_notes.json', 'w', encoding='utf-8') as f:
        json.dump(all_notes, f, ensure_ascii=False, indent=2)
    
    print(f"\n总共找到 {len(all_notes)} 个笔记")
    browser.close()
