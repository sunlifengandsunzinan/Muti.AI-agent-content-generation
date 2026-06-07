#!/usr/bin/env python3
"""调试 v3"""
import asyncio, httpx, websockets, json, base64

async def main():
    pages = httpx.get("http://127.0.0.1:18800/json").json()
    target = None
    for p in pages:
        if p.get("type") == "page" and "douyin" in p.get("url", ""):
            target = p["webSocketDebuggerUrl"]
            break
    
    if not target:
        print("无页面")
        return
    
    async with websockets.connect(target, max_size=20*1024*1024) as ws:
        await ws.send(json.dumps({"id": 1, "method": "Network.enable", "params": {}}))
        await asyncio.sleep(0.3)
        
        responses = {}
        finished = set()
        
        async def listen():
            while True:
                try:
                    data = json.loads(await asyncio.wait_for(ws.recv(), timeout=20))
                    m = data.get("method", "")
                    p = data.get("params", {})
                    if m == "Network.responseReceived":
                        rid = p.get("requestId", "")
                        url = p.get("response", {}).get("url", "")
                        mime = p.get("response", {}).get("mimeType", "")
                        if "/aweme/v1/web/general/search" in url:
                            responses[rid] = {"url": url, "mime": mime}
                            print(f"API: {url[:90]} mime={mime}")
                    elif m == "Network.loadingFinished":
                        finished.add(p.get("requestId", ""))
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
        
        print(f"\n总计: {len(responses)} 个 API")
        for rid, info in responses.items():
            status = "DONE" if rid in finished else "WAIT"
            print(f"  {status} {info['url'][:100]}")
            if rid in finished:
                await ws.send(json.dumps({"id": 100, "method": "Network.getResponseBody", "params": {"requestId": rid}}))
                try:
                    resp = json.loads(await asyncio.wait_for(ws.recv(), timeout=3))
                    body = resp.get("result", {}).get("body", "")
                    if body:
                        is_b64 = resp.get("result", {}).get("base64Encoded", False)
                        if is_b64:
                            body = base64.b64decode(body).decode("utf-8", errors="replace")
                        data = json.loads(body)
                        al = data.get("aweme_list") or data.get("data") or []
                        print(f"    count={len(al)} status={data.get('status_code')}")
                        for item in al[:2]:
                            aweme = item.get("aweme_info", item)
                            print(f"    - {aweme.get('aweme_id','')} @{aweme.get('author',{}).get('nickname','')}")
                except Exception as e:
                    print(f"    error: {e}")

asyncio.run(main())
