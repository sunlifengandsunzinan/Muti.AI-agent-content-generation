#!/usr/bin/env python3
"""检查抖音搜索页 DOM"""
import asyncio
import httpx
import websockets
import json

async def main():
    pages = httpx.get("http://127.0.0.1:18800/json").json()
    for p in pages:
        if p.get("type") == "page" and "douyin" in p.get("url", ""):
            target = p["webSocketDebuggerUrl"]
            print("页面:", p.get("url", "")[:80])
            break
    else:
        print("无页面")
        return
    
    async with websockets.connect(target) as ws:
        for expr in [
            "document.title",
            "document.querySelectorAll('a[href*=\"/video/\"]').length",
            "document.querySelectorAll('[href*=\"video\"]').length",
            "document.querySelectorAll('[href*=\"aweme\"]').length",
            "document.querySelectorAll('a').length",
            "Array.from(document.querySelectorAll('[data-e2e]')).slice(0,10).map(e=>e.getAttribute('data-e2e')).join(',')",
            "document.body.innerText.substring(0, 300)",
        ]:
            await ws.send(json.dumps({"id": 1, "method": "Runtime.evaluate", "params": {
                "expression": expr, "returnByValue": True
            }}))
            resp = json.loads(await asyncio.wait_for(ws.recv(), timeout=5))
            val = resp.get("result", {}).get("result", {}).get("value", "?")
            print(f"  {str(val)[:150]}")

asyncio.run(main())
