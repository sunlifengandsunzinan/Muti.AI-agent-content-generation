from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1280, "height": 800})
    
    # 打开抖音登录页
    page.goto("https://www.douyin.com/login/", wait_until="networkidle")
    time.sleep(3)
    
    # 截图整个页面
    page.screenshot(path="C:\\Users\\Administrator\\.openclaw\\workspace\\douyin_login.png", full_page=False)
    print("Login page screenshot saved")
    
    # 尝试找二维码区域截图
    qr_el = page.query_selector("canvas, img[alt*='二维码'], img[alt*='扫码'], .qr-code, .qrcode, [class*='qr'], [class*='qrcode']")
    if qr_el:
        qr_el.screenshot(path="C:\\Users\\Administrator\\.openclaw\\workspace\\douyin_qr.png")
        print("QR code screenshot saved")
    else:
        print("No QR element found, saving full page instead")
    
    browser.close()
