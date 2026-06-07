#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Quick test: run playwright chromium headless"""
import asyncio
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from playwright.async_api import async_playwright

async def test():
    print("[*] Testing Playwright Chromium...")
    async with async_playwright() as pw:
        print("[*] Launching headless Chromium...")
        browser = await pw.chromium.launch(headless=True, args=["--no-sandbox"])
        print("[*] Browser launched!")
        
        page = await browser.new_page()
        print("[*] Page created")
        
        await page.goto("https://www.doubao.com/chat/", timeout=30000, wait_until='domcontentloaded')
        print("[*] Page loaded")
        
        await asyncio.sleep(2)
        title = await page.title()
        print(f"[*] Page title: {title}")
        
        content = await page.content()
        print(f"[*] Content length: {len(content)}")
        print(f"[*] First 500 chars: {content[:500]}")
        
        await page.screenshot(path='_tmp_test_screenshot.png')
        print("[*] Screenshot saved")
        
        await browser.close()
        print("[*] Done")

asyncio.run(test())
