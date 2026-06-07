#!/usr/bin/env python3
"""Screenshot spot detail page"""
import asyncio, json, urllib.parse
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
        page = await browser.new_page(viewport={"width": 1300, "height": 900})
        
        cands = json.load(open(r"D:\moto\data\raw\openclaw_candidates.json", encoding="utf8"))
        cands.sort(key=lambda x: len(x.get("raw_name", "")), reverse=True)
        c = cands[0]
        slug, name = c["slug"], c["raw_name"]
        print(f"Opening: {name}")
        
        url = "http://127.0.0.1:6001/moto/spots/collect?candidate=" + urllib.parse.quote(slug)
        await page.goto(url, wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(2000)
        
        # 截完整页
        await page.screenshot(
            path=r"C:\Users\Administrator\.openclaw\workspace\spot_page.png",
            full_page=True
        )
        await page.screenshot(
            path=r"C:\Users\Administrator\.openclaw\workspace\spot_visible.png"
        )
        
        # 检查图片
        imgs = await page.query_selector_all("img")
        print(f"Total img elements: {len(imgs)}")
        for i, img in enumerate(imgs):
            src = await img.get_attribute("src")
            alt = await img.get_attribute("alt")
            s = src[:100] if src else "None"
            a = alt[:100] if alt else "None"
            print(f"  img[{i}]: src={s}, alt={a}")
        
        # 正文
        text = await page.inner_text("body")
        print(f"\nPage text:\n{text[:3000]}")
        
        await browser.close()

asyncio.run(main())
