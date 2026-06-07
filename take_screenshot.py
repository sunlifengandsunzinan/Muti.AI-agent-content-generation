from playwright.sync_api import sync_playwright
import urllib.request, json

resp = urllib.request.urlopen('http://127.0.0.1:6001/api/status', timeout=5)
api = json.loads(resp.read())

print(f"Server status: {api['status']} on port {api['port']}")
print("Taking screenshot...")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1280, "height": 800})
    
    page.goto("http://127.0.0.1:6001/", wait_until="networkidle")
    page.screenshot(path="C:\\Users\\Administrator\\.openclaw\\workspace\\moto_screenshot.png", full_page=True)
    print("Screenshot saved (homepage)")
    
    page.goto("http://127.0.0.1:6001/status", wait_until="networkidle")
    page.screenshot(path="C:\\Users\\Administrator\\.openclaw\\workspace\\moto_status_screenshot.png", full_page=True)
    print("Screenshot saved (status page)")
    
    browser.close()

print("Done!")
