#!/usr/bin/env python3
"""打开审批页第一条并截图"""
import asyncio, json, urllib.parse
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
        page = await browser.new_page(viewport={"width": 1200, "height": 1000})
        
        # 从候选数据中选一个有标题的
        cands = json.load(open(r"D:\moto\data\raw\openclaw_candidates.json", encoding="utf8"))
        # 排一下，找标题长的
        cands_sorted = sorted(cands, key=lambda x: len(x.get("raw_name", "")), reverse=True)
        for c in cands_sorted[:10]:
            print(f"  {c['slug'][:60]} | {c['raw_name'][:80]}")
        
        slug = cands_sorted[0]["slug"]
        name = cands_sorted[0]["raw_name"]
        print(f"\nOpening: {name}")
        
        url = f"http://127.0.0.1:6001/moto/spots/collect?candidate={urllib.parse.quote(slug)}"
        await page.goto(url, wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(3000)
        
        # 检查页面内容
        content = await page.content()
        texts = ["img", "src", "图片", "image", "photo"]
        for t in texts:
            count = content.lower().count(t.lower())
            print(f"'{t}' count: {count}")
        
        # 截图
        await page.screenshot(
            path=r"C:\Users\Administrator\.openclaw\workspace\candidate_detail.png",
            full_page=True
        )
        print("Screenshot saved to candidate_detail.png")
        await browser.close()

asyncio.run(main())
