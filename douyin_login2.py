from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    # 用有头模式启动
    browser = p.chromium.launch(headless=False)
    page = browser.new_page(viewport={"width": 1280, "height": 900})
    
    print("Opening Douyin login page...")
    page.goto("https://www.douyin.com/login/", wait_until="networkidle", timeout=30000)
    time.sleep(5)
    
    # 看看页面上有什么内容
    title = page.title()
    print(f"Page title: {title}")
    
    # 截全屏
    page.screenshot(path="C:\\Users\\Administrator\\.openclaw\\workspace\\douyin_login_full.png")
    
    # 找二维码或扫码元素
    elements = page.query_selector_all("img, canvas, [class*='qr'], [class*='QR'], [class*='scan'], [class*='code']")
    print(f"Found {len(elements)} potential QR/scan elements")
    
    for el in elements[:10]:
        tag = el.evaluate("el => el.tagName")
        cls = el.evaluate("el => el.className")
        src = el.evaluate("el => el.src || ''")
        alt = el.evaluate("el => el.alt || ''")
        visible = el.is_visible()
        print(f"  {tag} class='{cls[:60]}' src='{src[:80]}' alt='{alt[:40]}' visible={visible}")
    
    browser.close()
