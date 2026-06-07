#!/usr/bin/env python3
"""Screenshot using Chrome CDP directly"""
import io, json, sys, base64
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import urllib.request, urllib.parse
import os, time

# Find Chrome debug port from existing processes
import subprocess
r = subprocess.run(['powershell', '-Command', 
    'Get-Process -Name chrome -ErrorAction SilentlyContinue | ForEach-Object { $_.Id }'],
    capture_output=True, text=True, timeout=10)
print(f"Chrome PIDs: {r.stdout.strip()}")

# Try connecting to CDP on existing Chrome via remote debugging
# If that doesn't work, launch a new one

from playwright.sync_api import sync_playwright

OUTPUT = r"C:\Users\Administrator\.openclaw\workspace\collector_monitor.png"

with sync_playwright() as p:
    # Launch with explicit exe path
    browser = p.chromium.launch(
        headless=True,
        executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    )
    page = browser.new_page(viewport={"width": 1280, "height": 900})
    try:
        page.goto("http://192.168.0.112:6001/moto/collector/monitor", wait_until="domcontentloaded", timeout=15000)
    except:
        page.goto("http://127.0.0.1:6001/moto/collector/monitor", wait_until="domcontentloaded", timeout=15000)
    time.sleep(1)
    page.screenshot(path=OUTPUT, full_page=True)
    browser.close()

if os.path.exists(OUTPUT):
    print(f"Screenshot saved: {OUTPUT} ({os.path.getsize(OUTPUT)} bytes)")
else:
    print("FAILED")
