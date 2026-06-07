#!/usr/bin/env python3
"""从搜索页面获取视频链接 — 通过搜索按钮触发搜索 + 拦截网络请求"""

import asyncio, httpx, websockets, json, urllib.parse

async def main():
    async with httpx.AsyncClient() as c:
        pages = (await c.get("http://127.0.0.1:18800/json")).json()
    
    target = None
    url = ""
    for p in pages:
        if p.get("type") == "page" and "douyin" in p.get("url", ""):
            target = p["webSocketDebuggerUrl"]
            url = p.get("url", "")
            print("页面:", url[:80])
            break
    
    if not target:
        print("无页面")
        return
    
    kw = "摩旅路线"
    encoded = urllib.parse.quote(kw)
    
    async with websockets.connect(target, max_size=10*1024*1024) as ws:
        # 1. 启用 Network 域，拦截搜索 API 响应
        await ws.send(json.dumps({"id": 1, "method": "Network.enable", "params": {}}))
        await asyncio.sleep(0.3)
        
        # 2. 记录即将到来的网络响应
        api_responses = []
        
        async def listen_responses():
            nonlocal api_responses
            while True:
                try:
                    resp = json.loads(await asyncio.wait_for(ws.recv(), timeout=20))
                    method = resp.get("method", "")
                    
                    # 捕获 responseReceived
                    if method == "Network.responseReceived":
                        resp_url = resp.get("params", {}).get("response", {}).get("url", "")
                        if "/search/item" in resp_url or "general/search" in resp_url:
                            req_id = resp.get("params", {}).get("requestId", "")
                            api_responses.append({"url": resp_url, "requestId": req_id})
                            print(f"  📡 API 响应捕获: {resp_url[:80]}")
                    
                    # 捕获 responseBody
                    if method == "Network.loadingFinished":
                        req_id = resp.get("params", {}).get("requestId", "")
                        for a in api_responses:
                            if a["requestId"] == req_id and "body" not in a:
                                # 请求 body
                                await ws.send(json.dumps({"id": 100, "method": "Network.getResponseBody", "params": {"requestId": req_id}}))
                                a["got_body"] = True
                except asyncio.TimeoutError:
                    break
                except websockets.ConnectionClosed:
                    break
        
        # 启动监听
        listener = asyncio.create_task(listen_responses())
        
        # 3. 导航到搜索页（这将触发 API 请求）
        search_url = f"https://www.douyin.com/search/{encoded}?type=general"
        await ws.send(json.dumps({"id": 2, "method": "Page.navigate", "params": {"url": search_url}}))
        
        # 4. 等加载和 API 响应
        print("  等待页面加载 + API 响应...")
        await asyncio.sleep(10)
        
        # 停止监听
        listener.cancel()
        try:
            await listener
        except:
            pass
        
        # 5. 获取 body
        print(f"\n  捕获到 {len(api_responses)} 个 API 响应")
        for a in api_responses:
            try:
                await ws.send(json.dumps({"id": 200, "method": "Network.getResponseBody", "params": {"requestId": a["requestId"]}}))
                resp = json.loads(await asyncio.wait_for(ws.recv(), timeout=5))
                body = resp.get("result", {}).get("body", "")
                if body:
                    data = json.loads(body)
                    aweme_list = data.get("aweme_list") or data.get("data", [])
                    if aweme_list:
                        print(f"\n  ✅ 获取到 {len(aweme_list)} 个视频!")
                        for item in aweme_list[:5]:
                            aid = item.get("aweme_id", "")
                            desc = item.get("desc", "")
                            author = item.get("author", {}).get("nickname", "")
                            print(f"    ID: {aid}")
                            print(f"    URL: https://www.douyin.com/video/{aid}")
                            print(f"    作者: {author}")
                            print(f"    标题: {str(desc)[:60]}")
                            print()
            except Exception as e:
                print(f"  ⚠️ 获取 body 失败: {e}")

asyncio.run(main())
