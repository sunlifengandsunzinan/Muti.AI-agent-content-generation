from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1920, "height": 1080})
    
    # 先访问抖音首页，看看会不会有登录弹窗
    page.goto("https://www.douyin.com/", wait_until="networkidle", timeout=30000)
    time.sleep(4)
    page.screenshot(path="C:\\Users\\Administrator\\.openclaw\\workspace\\douyin_home.png")
    print(f"Home URL: {page.url}")
    
    # 点击登录按钮
    login_btn = page.query_selector("text=登录")
    if login_btn:
        print("Found login button, clicking...")
        login_btn.click()
        time.sleep(3)
        page.screenshot(path="C:\\Users\\Administrator\\.openclaw\\workspace\\douyin_login_modal.png")
        print("Login modal screenshot saved")
    else:
        print("No login button found on homepage")
    
    # 再直接打开 login 页
    page.goto("https://www.douyin.com/login/", timeout=30000)
    time.sleep(5)
    page.screenshot(path="C:\\Users\\Administrator\\.openclaw\\workspace\\douyin_login_full.png")
    print(f"Login URL: {page.url}")
    
    browser.close()
