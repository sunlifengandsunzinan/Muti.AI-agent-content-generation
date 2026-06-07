#!/usr/bin/env python3
"""Screenshot via Playwright connecting to existing Chrome"""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from playwright.sync_api import sync_playwright
import os

OUTPUT = r"C:\Users\Administrator\.openclaw\workspace\collector_monitor.png"

with sync_playwright() as p:
    # Connect to the Chrome already running on :9223
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9223")
    
    # Try to find existing tab, or create new one
    context = browser.contexts[0]
    page = context.new_page()
    page.goto("http://127.0.0.1:6001/moto/collector/monitor", wait_until="domcontentloaded", timeout=20000)
    
    import time; time.sleep(2)
    page.screenshot(path=OUTPUT, full_page=True)
    page.close()
    browser.close()

if os.path.exists(OUTPUT):
    print(f"✅ Screenshot: {OUTPUT} ({os.path.getsize(OUTPUT)} bytes)")
else:
    print("❌ Failed")
