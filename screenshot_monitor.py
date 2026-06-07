#!/usr/bin/env python3
"""Screenshot the collect monitor page using Playwright"""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from playwright.sync_api import sync_playwright
import os, time

OUTPUT = r"C:\Users\Administrator\.openclaw\workspace\collect_monitor.png"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=['--disable-web-security'])
    page = browser.new_page(viewport={"width": 1280, "height": 900})
    page.goto("http://127.0.0.1:6001/moto/collector/monitor", wait_until="networkidle", timeout=15000)
    time.sleep(1)
    page.screenshot(path=OUTPUT, full_page=True)
    browser.close()

print(f"Screenshot saved: {OUTPUT}")
print(f"File size: {os.path.getsize(OUTPUT)} bytes")
