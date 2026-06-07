#!/usr/bin/env python3
"""提取第一个 search card 的完整 HTML"""
import asyncio, httpx, websockets, json

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
        await ws.send(json.dumps({"id": 1, "method": "Runtime.evaluate", "params": {
            "expression": """
                (() => {
                    const card = document.querySelector('[class*="search-result-card"]');
                    if (!card) return "no cards found";
                    return card.outerHTML.substring(0, 3000);
                })()
            """,
            "returnByValue": True
        }}))
        resp = json.loads(await asyncio.wait_for(ws.recv(), timeout=5))
        html = resp.get("result",{}).get("result",{}).get("value","")
        print("Card HTML:")
        print(html)

asyncio.run(main())
