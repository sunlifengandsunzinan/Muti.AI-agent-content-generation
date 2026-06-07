#!/usr/bin/env python3
"""看页面上所有链接"""
import asyncio
import httpx
import websockets
import json

async def main():
    pages = httpx.get("http://127.0.0.1:18800/json").json()
    for p in pages:
        if p.get("type") == "page":
            target = p["webSocketDebuggerUrl"]
            print("页面:", p.get("url", "")[:80])
            break
    
    async with websockets.connect(target) as ws:
        # 获取所有链接
        await ws.send(json.dumps({"id": 1, "method": "Runtime.evaluate", "params": {
            "expression": "Array.from(document.querySelectorAll('a')).map(a=>a.getAttribute('href')).filter(Boolean).join('|')",
            "returnByValue": True
        }}))
        resp = json.loads(await asyncio.wait_for(ws.recv(), timeout=5))
        links = resp.get("result",{}).get("result",{}).get("value","")
        print("所有链接:")
        for l in links.split("|"):
            print(f"  {l}")
        
        # 看看有没有视频卡片相关元素
        await ws.send(json.dumps({"id": 2, "method": "Runtime.evaluate", "params": {
            "expression": "Array.from(document.querySelectorAll('[class*=\"video\" i]')).slice(0,10).map(e=>e.tagName+'|'+e.className.substring(0,60)).join('\\n')",
            "returnByValue": True
        }}))
        resp = json.loads(await asyncio.wait_for(ws.recv(), timeout=5))
        val = resp.get("result",{}).get("result",{}).get("value","")
        print(f"\nvideo元素:\n{val}")
        
        # 检查搜索区域
        await ws.send(json.dumps({"id": 3, "method": "Runtime.evaluate", "params": {
            "expression": "Array.from(document.querySelectorAll('[class*=\"search\" i]')).slice(0,10).map(e=>e.tagName+'|'+e.className.substring(0,80)).join('\\n')",
            "returnByValue": True
        }}))
        resp = json.loads(await asyncio.wait_for(ws.recv(), timeout=5))
        val = resp.get("result",{}).get("result",{}).get("value","")
        print(f"\nsearch元素:\n{val}")

asyncio.run(main())
