#!/usr/bin/env python3
"""完整流程：先等加载完成 + 再拿 body"""
import asyncio, httpx, websockets, json, base64

async def main():
    pages = httpx.get("http://127.0.0.1:18800/json").json()
    for p in pages:
        if p.get("type") == "page" and "douyin" in p.get("url", ""):
            target = p["webSocketDebuggerUrl"]
            break
    
    async with websockets.connect(target, max_size=20*1024*1024) as ws:
        await ws.send(json.dumps({"id": 1, "method": "Network.enable", "params": {}}))
        await asyncio.sleep(0.3)
        
        # 收集所有 response 和 loadingFinished
        responses = {}  # requestId -> url
        finished = set()  # requestId
        
        async def listen():
            while True:
                try:
                    data = json.loads(await asyncio.wait_for(ws.recv(), timeout=20))
                    m = data.get("method", "")
                    p = data.get("params", {})
                    if m == "Network.responseReceived":
                        req_id = p.get("requestId", "")
                        url = p.get("response", {}).get("url", "")
                        mime = p.get("response", {}).get("mimeType", "")
                        if "/aweme/v1/web/general/search" in url:
                            responses[req_id] = {"url": url, "mime": mime}
                            print(f"  📡 API: {url[:100]}...")
                    elif m == "Network.loadingFinished":
                        finished.add(p.get("requestId", ""))
                except asyncio.TimeoutError:
                    break
                except websockets.ConnectionClosed:
                    break
        
        listener = asyncio.create_task(listen())
        print("  导航搜索页...")
        await ws.send(json.dumps({"id": 2, "method": "Page.navigate", "params": {
            "url": "https://www.douyin.com/search/%E6%91%A9%E6%97%85%E8%B7%AF%E7%BA%BF?type=general"
        }}))
        await asyncio.sleep(15)
        listener.cancel()
        try: await listener
        except: pass
        
        print(f"\n  搜索 API: {len(responses)} 个")
        print(f"  已完成: {sum(1 for rid in responses if rid in finished)} 个")
        
        for rid, info in responses.items():
            if rid in finished:
                print(f"\n  获取 body: {info['url'][:80]}")
                await ws.send(json.dumps({"id": 100, "method": "Network.getResponseBody", "params": {"requestId": rid}}))
                try:
                    resp = json.loads(await asyncio.wait_for(ws.recv(), timeout=5))
                    body = resp.get("result", {}).get("body", "")
                    is_b64 = resp.get("result", {}).get("base64Encoded", False)
                    if body:
                        if is_b64:
                            body = base64.b64decode(body).decode("utf-8", errors="replace")
                        data = json.loads(body)
                        print(f"    ✅ JSON keys: {list(data.keys())}")
                        al = data.get("aweme_list") or data.get("data") or []
                        print(f"    aweme_list: {len(al)}")
                        if "status_code" in data:
                            print(f"    status_code: {data['status_code']}")
                        if al:
                            for item in al[:3]:
                                if "aweme_info" in item:
                                    item = item["aweme_info"]
                                print(f"    - {item.get('aweme_id','')} | {item.get('author',{}).get('nickname','')} | {item.get('desc','')[:50]}")
                except Exception as e:
                    print(f"    ❌ {e}")

asyncio.run(main())
