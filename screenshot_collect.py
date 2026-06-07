#!/usr/bin/env python3
"""Screenshot the spot collect (approval) page"""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from playwright.sync_api import sync_playwright
import os

OUTPUT = r"C:\Users\Administrator\.openclaw\workspace\spot_collect_page.png"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1280, "height": 1200})
    page.goto("http://127.0.0.1:6001/moto/spots/collect", wait_until="networkidle", timeout=15000)
    import time; time.sleep(1)
    page.screenshot(path=OUTPUT, full_page=True)
    browser.close()

print(f"Screenshot saved: {OUTPUT}")
print(f"File size: {os.path.getsize(OUTPUT)} bytes")
