from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1280, "height": 2000})
    
    page.goto("http://127.0.0.1:6001/moto/spots/collect", wait_until="networkidle", timeout=15000)
    page.screenshot(path="C:\\Users\\Administrator\\.openclaw\\workspace\\moto_collect_16.png", full_page=True)
    print("Screenshot saved")
    
    browser.close()
