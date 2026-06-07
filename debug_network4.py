#!/usr/bin/env python3
"""捕获正确的搜索 API 响应 — 只针对 aweme/v1/web/general/search"""

import asyncio, httpx, websockets, json, base64, urllib.parse

async def main():
    pages = httpx.get("http://127.0.0.1:18800/json").json()
    target = None
    for p in pages:
        if p.get("type") == "page" and "douyin" in p.get("url", ""):
            target = p["webSocketDebuggerUrl"]
            print("页面:", p.get("url", "")[:80])
            break
    
    async with websockets.connect(target, max_size=20*1024*1024) as ws:
        # 启用 Network
        await ws.send(json.dumps({"id": 1, "method": "Network.enable", "params": {}}))
        await asyncio.sleep(0.3)
        
        # 收集 loadingFinished 事件（body 可用时）
        finished = []
        
        async def listen():
            while True:
                try:
                    data = json.loads(await asyncio.wait_for(ws.recv(), timeout=20))
                    if data.get("method") == "Network.loadingFinished":
                        finished.append(data.get("params", {}))
                except asyncio.TimeoutError:
                    break
                except websockets.ConnectionClosed:
                    break
        
        listener = asyncio.create_task(listen())
        
        # 导航
        print("  导航到搜索页...")
        await ws.send(json.dumps({"id": 2, "method": "Page.navigate", "params": {
            "url": "https://www.douyin.com/search/摩旅路线?type=general"
        }}))
        
        await asyncio.sleep(12)
        listener.cancel()
        try: await listener
        except: pass
        
        print(f"  loadingFinished 事件: {len(finished)}")
        
        # 对于所有完成的请求，尝试获取 body 看哪个是搜索 API
        search_responses = []
        MAX_CHECK = 50
        for i, f in enumerate(finished):
            if i >= MAX_CHECK:
                break
            req_id = f.get("requestId", "")
            if not req_id:
                continue
            
            await ws.send(json.dumps({"id": 100+i, "method": "Network.getResponseBody", "params": {"requestId": req_id}}))
            try:
                resp = json.loads(await asyncio.wait_for(ws.recv(), timeout=3))
                body = resp.get("result", {}).get("body", "")
                is_base64 = resp.get("result", {}).get("base64Encoded", False)
                
                if body:
                    try:
                        if is_base64:
                            body = base64.b64decode(body).decode("utf-8", errors="replace")
                        # 尝试解析 JSON
                        data = json.loads(body)
                        if isinstance(data, dict) and ("aweme_list" in data or "data" in data):
                            aweme_list = data.get("aweme_list") or data.get("data") or []
                            search_responses.append({
                                "requestId": req_id,
                                "aweme_count": len(aweme_list),
                                "has_more": data.get("has_more", 0),
                                "data": data,
                            })
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        pass
            except:
                pass
        
        print(f"\n搜索 API 响应: {len(search_responses)}")
        for sr in search_responses[:2]:
            data = sr["data"]
            aweme_list = data.get("aweme_list") or data.get("data") or []
            print(f"  视频数: {len(aweme_list)} (has_more: {sr['has_more']})")
            
            for i, item in enumerate(aweme_list[:5]):
                if "aweme_info" in item:
                    item = item["aweme_info"]
                aid = item.get("aweme_id", "")
                desc = item.get("desc", "")
                author = item.get("author", {}).get("nickname", "")
                print(f"\n  [{i+1}] ID: {aid}")
                print(f"      链接: https://www.douyin.com/video/{aid}")
                print(f"      作者: {author}")
                print(f"      标题: {str(desc)[:60]}")

asyncio.run(main())
