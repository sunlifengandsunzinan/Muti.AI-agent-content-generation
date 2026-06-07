#!/usr/bin/env python3
"""调试 v2：看第二次导航后 API 的 URL 详情"""
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
        
        responses = {}
        finished_ids = {}
        
        async def listen():
            while True:
                try:
                    data = json.loads(await asyncio.wait_for(ws.recv(), timeout=20))
                    m, p = data.get("method", ""), data.get("params", {})
                    if m == "Network.responseReceived":
                        rid, url = p.get("requestId", ""), p.get("response", {}).get("url", "")
                        responses[rid] = url
                    elif m == "Network.loadingFinished":
                        finished_ids[p.get("requestId", "")] = True
                except asyncio.TimeoutError:
                    break
                except websockets.ConnectionClosed:
                    break
        
        listener = asyncio.create_task(listen())
        await ws.send(json.dumps({"id": 2, "method": "Page.navigate", "params": {
            "url": "https://www.douyin.com/search/%E6%91%A9%E6%97%85%E8%B7%AF%E7%BA%BF?type=general"
        }}))
        await asyncio.sleep(10)
        listener.cancel()
        try: await listener
        except: pass
        
        # 看所有 search API
        search_apis = {rid: url for rid, url in responses.items() if "/aweme/v1/web/general/search" in url}
        print(f"搜索 API 请求: {len(search_apis)}")
        for rid, url in search_apis.items():
            is_single = "single" in url
            has_body = rid in finished_ids
            print(f"  single={is_single} | finished={has_body} | {url[:120]}")
            
            if has_body:
                await ws.send(json.dumps({"id": 200, "method": "Network.getResponseBody", "params": {"requestId": rid}}))
                try:
                    resp = json.loads(await asyncio.wait_for(ws.recv(), timeout=3))
                    body = resp.get("result", {}).get("body", "")
                    is_b64 = resp.get("result", {}).get("base64Encoded", False)
                    if body:
                        if is_b64:
                            body = base64.b64decode(body).decode("utf-8", errors="replace")
                        data = json.loads(body)
                        al = data.get("aweme_list") or data.get("data") or []
                        print(f"    aweme_list: {len(al)} status: {data.get('status_code')}")

asyncio.run(main())
