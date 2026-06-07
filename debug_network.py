#!/usr/bin/env python3
"""获取抖音搜索页实际发送的 API 请求"""
import asyncio, httpx, websockets, json

async def main():
    pages = httpx.get("http://127.0.0.1:18800/json").json()
    for p in pages:
        if p.get("type") == "page" and "douyin" in p.get("url", ""):
            target = p["webSocketDebuggerUrl"]
            url = p.get("url", "")
            print("页面:", url[:80])
            break
    else:
        print("无页面")
        return
    
    async with websockets.connect(target, max_size=10*1024*1024) as ws:
        # 启用 Network 域
        await ws.send(json.dumps({"id": 1, "method": "Network.enable", "params": {}}))
        await asyncio.sleep(0.3)
        
        # 立即提取已有的网络请求记录
        await ws.send(json.dumps({"id": 2, "method": "Runtime.evaluate", "params": {
            "expression": """
                (() => {
                    // 通过 performance API 获取已经发出的请求
                    const entries = performance.getEntriesByType('resource');
                    const searchApis = entries
                        .filter(e => e.name.includes('/search/item') || e.name.includes('general/search'))
                        .map(e => ({
                            url: e.name.substring(0, 150),
                            duration: e.duration.toFixed(0),
                            size: e.transferSize || e.encodedBodySize || 0,
                        }));
                    return JSON.stringify(searchApis);
                })()
            """,
            "returnByValue": True
        }}))
        resp = json.loads(await asyncio.wait_for(ws.recv(), timeout=5))
        apis = resp.get("result",{}).get("result",{}).get("value","[]")
        print(f"\n已发送的搜索 API 请求:")
        print(apis)

asyncio.run(main())
