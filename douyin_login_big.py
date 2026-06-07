from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    # 连接到已经运行的 Chrome
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:18800")
    
    # 获取已有页面或开新页面
    pages = browser.contexts[0].pages if browser.contexts else []
    if pages:
        page = pages[0]
    else:
        page = browser.new_page()
    
    # 调大窗口
    page.set_viewport_size({"width": 1920, "height": 1080})
    
    # 导航到抖音登录
    page.goto("https://www.douyin.com/login/", wait_until="networkidle", timeout=30000)
    time.sleep(4)
    
    # 截全屏大图
    page.screenshot(path="C:\\Users\\Administrator\\.openclaw\\workspace\\douyin_login_big.png", full_page=False)
    print(f"Saved: big screenshot")
    print(f"Title: {page.title()}")
    print(f"URL: {page.url}")
    
    browser.close()
