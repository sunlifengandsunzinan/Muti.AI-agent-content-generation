#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pipeline: doubao summary with cookie injection"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', write_through=True)
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', write_through=True)

import json, asyncio
from datetime import datetime
from playwright.async_api import async_playwright

SEARCH_FILE = 'skills/douyin-search/search_results/search_20260601_230504.json'
SUMMARIES_FILE = 'moto/data/raw/doubao_summaries.json'
COOKIES_FILE = 'moto/data/douyin_cookies.json'
MAX_VIDEOS = 8

async def inject_cookies(context, cookies_file):
    """Inject doubao cookies into browser context"""
    with open(cookies_file, 'r', encoding='utf8') as f:
        data = json.load(f)
    
    cookies = data.get('cookies', [])
    # Filter for doubao and related domains
    doubao_cookies = [
        ck for ck in cookies 
        if any(d in ck.get('domain', '') for d in ['doubao', 'bytedance', 'volcengine'])
    ]
    
    # Add any doubao-relevant cookies
    await context.add_cookies(doubao_cookies)
    print(f"Injected {len(doubao_cookies)} cookies for doubao/bytedance", flush=True)

async def check_logged_in(page):
    """Check if doubao session is valid"""
    try:
        # Look for user avatar or username element
        avatar = await page.query_selector('[class*="avatar"], [class*="user"]')
        body = await page.inner_text('body')
        
        # If we see login button prominently, we're not logged in
        login_btn = await page.query_selector('text=登录')
        
        # Check if "登录" is actually a button (visible) vs just text
        if login_btn:
            # Try to check if it's visible/interactable
            is_visible = await login_btn.is_visible()
            if is_visible:
                return False
        
        return True
    except:
        return False

async def ask_doubao(page, video_url, idx, total):
    print(f"[{idx}/{total}] Processing: {video_url[:60]}", flush=True)
    
    try:
        # Find input
        input_box = None
        for sel in ['textarea', '[contenteditable="true"]', '.chat-input', 'div[role="textbox"]']:
            input_box = await page.query_selector(sel)
            if input_box:
                break
        
        if not input_box:
            return "[fail: no input]"
        
        # Type prompt
        prompt = f"总结这个抖音摩旅视频的路线信息，包括途经点、公里数、天数、路线特点等。视频链接: {video_url}"
        tag = await input_box.get_property('tagName')
        tag_name = await tag.json_value()
        
        if tag_name in ('TEXTAREA', 'INPUT'):
            await input_box.fill(prompt)
        else:
            await input_box.click()
            await asyncio.sleep(0.3)
            await input_box.fill(prompt)
        
        await asyncio.sleep(1)
        
        # Send
        send_btn = await page.query_selector('button[type="submit"]') or await page.query_selector('[class*="send"]')
        if send_btn:
            await send_btn.click()
        else:
            await page.keyboard.press('Enter')
        
        print("Waiting for response...", flush=True)
        await asyncio.sleep(8)
        
        last_text = ""
        for poll in range(20):
            await asyncio.sleep(2)
            try:
                msgs = await page.query_selector_all('[class*="message"]')
                for msg in reversed(msgs):
                    text = await msg.inner_text()
                    if text and len(text) > 20:
                        if text.endswith('...') or '思考' in text[-20:]:
                            last_text = text
                            continue
                        print(f"Reply: {len(text)} chars", flush=True)
                        return text.strip()
            except:
                pass
        
        if last_text and len(last_text) > 30:
            return last_text.strip()
        return "[fail: timeout]"
    
    except Exception as e:
        print(f"Error: {e}", flush=True)
        return f"[fail: {str(e)[:60]}]"

async def main():
    print(f"=== START {datetime.now()} ===", flush=True)
    
    # Load search results
    with open(SEARCH_FILE, 'r', encoding='utf8') as f:
        data = json.load(f)
    
    seen, videos = set(), []
    for kw, items in data['results'].items():
        for item in items:
            u = item.get('url', '')
            if u and u not in seen:
                seen.add(u)
                videos.append(item)
    print(f"Total: {len(videos)}", flush=True)
    
    # Load summaries
    try:
        with open(SUMMARIES_FILE, 'r', encoding='utf8') as f:
            summaries = json.load(f)
    except:
        summaries = {"source": "doubao", "total": 0, "items": []}
    
    existing = set(s.get('video_url', '') for s in summaries['items'])
    pending = [v for v in videos if v.get('url', '') not in existing]
    print(f"Existing: {len(existing)}, Pending: {len(pending)}", flush=True)
    
    if not pending:
        print("No new videos", flush=True)
        return
    
    batch = pending[:MAX_VIDEOS]
    print(f"This run: {len(batch)}", flush=True)
    
    print("Starting browser...", flush=True)
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True, args=["--no-sandbox", "--disable-blink-features=AutomationControlled"])
        print("Browser ready", flush=True)
        
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            viewport={"width": 1280, "height": 800}
        )
        
        # Inject cookies
        await inject_cookies(context, COOKIES_FILE)
        
        page = await context.new_page()
        print("Navigating to doubao...", flush=True)
        await page.goto("https://www.doubao.com/chat/", timeout=30000, wait_until='domcontentloaded')
        await asyncio.sleep(3)
        
        # Check if logged in
        logged_in = await check_logged_in(page)
        print(f"Logged in: {logged_in}", flush=True)
        
        if not logged_in:
            await page.screenshot(path='_tmp_doubao_not_logged.png')
            print("NOT logged in - screenshot saved", flush=True)
            await browser.close()
            return
        
        # Process videos
        for idx, video in enumerate(batch):
            url = video.get('url', '')
            author = video.get('author', '')
            title = video.get('title', '')
            print(f"\n[{idx+1}/{len(batch)}] {author}: {title[:30]}", flush=True)
            
            summary = await ask_doubao(page, url, idx+1, len(batch))
            
            entry = {
                'video_url': url,
                'aweme_id': video.get('aweme_id', ''),
                'author': author,
                'title': title,
                'doubao_summary': summary,
                'summary_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'source': 'doubao'
            }
            summaries['items'].append(entry)
            summaries['total'] = len(summaries['items'])
            with open(SUMMARIES_FILE, 'w', encoding='utf8') as f:
                json.dump(summaries, f, ensure_ascii=False, indent=2)
            
            status = 'OK' if not summary.startswith('[fail') else 'FAIL'
            print(f"Saved. Status: {status}", flush=True)
        
        await browser.close()
        print(f"\n=== DONE. Total summaries: {summaries['total']} ===", flush=True)

asyncio.run(main())
