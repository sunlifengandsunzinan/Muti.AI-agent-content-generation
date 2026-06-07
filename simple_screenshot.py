#!/usr/bin/env python3
"""Simple Playwright headless screenshot"""
import io, sys, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from playwright.sync_api import sync_playwright
import time

OUTPUT = r"C:\Users\Administrator\.openclaw\workspace\collector_monitor.png"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1280, "height": 900})
    page.goto("http://127.0.0.1:6001/moto/collector/monitor", wait_until="domcontentloaded", timeout=30000)
    time.sleep(2)
    page.screenshot(path=OUTPUT, full_page=True)
    browser.close()

print(f"✅ Saved {OUTPUT} ({os.path.getsize(OUTPUT)} bytes)" if os.path.exists(OUTPUT) else "❌ Failed")
