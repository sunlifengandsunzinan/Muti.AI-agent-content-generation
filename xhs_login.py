from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1920, "height": 1080})
    
    # 先打开小红书首页看看
    page.goto("https://www.xiaohongshu.com/", wait_until="networkidle", timeout=30000)
    time.sleep(4)
    page.screenshot(path="C:\\Users\\Administrator\\.openclaw\\workspace\\xhs_home.png")
    print(f"XHS Home URL: {page.url}")
    
    # 再打开小红书登录页
    page.goto("https://www.xiaohongshu.com/login", wait_until="networkidle", timeout=30000)
    time.sleep(5)
    page.screenshot(path="C:\\Users\\Administrator\\.openclaw\\workspace\\xhs_login.png")
    print(f"XHS Login URL: {page.url}")
    
    # 也试试另一个登录地址
    page.goto("https://account.xiaohongshu.com/login", wait_until="networkidle", timeout=30000)
    time.sleep(5)
    page.screenshot(path="C:\\Users\\Administrator\\.openclaw\\workspace\\xhs_account_login.png")
    print(f"XHS Account URL: {page.url}")
    
    browser.close()
