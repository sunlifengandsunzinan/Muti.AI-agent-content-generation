"""
通过 CDP 连接到现有 Chrome - 使用你的登录态
要求：先关闭所有 Chrome 窗口，然后用命令行启动：
  "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222
"""
from playwright.sync_api import sync_playwright
import json
import time
import os
import re

output_path = r'D:\MediaCrawlerResult\小红书_摩旅路书'
os.makedirs(output_path, exist_ok=True)

keywords = [
    "摩旅路线", "摩托车路书", "摩旅攻略",
    "骑行路线", "摩旅路书"
]

with sync_playwright() as p:
    # Connect to existing Chrome via CDP
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    
    # Use existing context (with your login)
    print(f"已连接到 Chrome，已有 {len(browser.contexts)} 个上下文")
    
    # Create a new page in the default context (which has your cookies)
    page = browser.new_page()
    
    # Check login status
    page.goto('https://www.xiaohongshu.com', wait_until='networkidle', timeout=30000)
    time.sleep(2)
    logged_in = page.evaluate('() => document.cookie.includes("web_session")')
    print(f"登录状态: {'已登录' if logged_in else '未登录'}")
    
    all_notes = []
    
    for kw in keywords:
        print(f"\n=== 搜索: {kw} ===")
        try:
            page.goto(f'https://www.xiaohongshu.com/search_result?keyword={kw}&source=web_search_result_notes',
                     wait_until='networkidle', timeout=30000)
            time.sleep(4)
            
            # Scroll to load more
            for _ in range(3):
                page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                time.sleep(2)
            
            # Extract notes
            data = page.evaluate('''() => {
                // Try intercepting API response data from the page
                const items = document.querySelectorAll('section[class*="note"], a[href*="discovery/item"]');
                const results = [];
                items.forEach(item => {
                    const link = item.href || item.getAttribute('href') || '';
                    const title = item.querySelector('[id*="title"], [class*="title"]')?.textContent?.trim() || '';
                    const img = item.querySelector('img')?.src || '';
                    const author = item.querySelector('[class*="author"], [class*="name"]')?.textContent?.trim() || '';
                    if (link && link.includes('discovery/item/')) {
                        results.push({
                            url: link.startsWith('http') ? link : 'https://www.xiaohongshu.com' + link,
                            title: title,
                            img: img,
                            author: author
                        });
                    }
                });
                return results;
            }''')
            
            print(f"  提取到 {len(data)} 个笔记")
            for item in data[:5]:
                print(f"  [{item.get('author','?')}] {item.get('title','')[:40]}")
            
            all_notes.extend(data)
            time.sleep(2)
            
        except Exception as e:
            print(f"  FAIL: {e}")
    
    # Save
    with open(f'{output_path}/notes.json', 'w', encoding='utf-8') as f:
        json.dump(all_notes, f, ensure_ascii=False, indent=2)
    print(f"\n总计 {len(all_notes)} 个笔记 → {output_path}")
    page.close()
