#!/usr/bin/env python3
"""Screenshot moto spot collect page"""
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
        page = await browser.new_page(viewport={"width": 1400, "height": 1000})
        
        url = "http://127.0.0.1:6001/moto/spots/collect"
        await page.goto(url, wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(2000)
        
        await page.screenshot(
            path=r"C:\Users\Administrator\.openclaw\workspace\spot_collect.png",
            full_page=True
        )
        print("Screenshot saved")
        
        # 也看看队列里有啥
        text = await page.inner_text("body")
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        queue_section = False
        for l in lines:
            if "候选队列" in l or "采集待审核" in l:
                queue_section = True
            if queue_section:
                print(l[:100])
        
        await browser.close()

asyncio.run(main())
