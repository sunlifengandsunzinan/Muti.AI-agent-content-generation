#!/usr/bin/env python3
"""直接从搜索结果页中提取 loadingFinished 事件的 response URL 来找到正确的 API"""
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
        
        # 收集 responseReceived（获得 URL）
        responses = []
        async def listen():
            while True:
                try:
                    data = json.loads(await asyncio.wait_for(ws.recv(), timeout=20))
                    if data.get("method") == "Network.responseReceived":
                        url = data.get("params", {}).get("response", {}).get("url", "")
                        req_id = data.get("params", {}).get("requestId", "")
                        mime = data.get("params", {}).get("response", {}).get("mimeType", "")
                        responses.append({"url": url, "id": req_id, "mime": mime})
                except asyncio.TimeoutError:
                    break
                except websockets.ConnectionClosed:
                    break
        
        listener = asyncio.create_task(listen())
        await ws.send(json.dumps({"id": 2, "method": "Page.navigate", "params": {
            "url": "https://www.douyin.com/search/%E6%91%A9%E6%97%85%E8%B7%AF%E7%BA%BF?type=general"
        }}))
        await asyncio.sleep(12)
        listener.cancel()
        try: await listener
        except: pass
        
        # 找 API 请求（aweme/v1/web/general/search）
        api_resps = [r for r in responses if "/aweme/v1/web/general/search" in r["url"]]
        print(f"\n搜索 API 请求数: {len(api_resps)}")
        
        for r in api_resps:
            print(f"\nURL: {r['url'][:150]}")
            print(f"MIME: {r['mime']}")
            print(f"RequestId: {r['id']}")
            
            # 等 loadingFinished
            await asyncio.sleep(2)
            
            # 获取 body
            await ws.send(json.dumps({"id": 100, "method": "Network.getResponseBody", "params": {"requestId": r["id"]}}))
            try:
                resp = json.loads(await asyncio.wait_for(ws.recv(), timeout=3))
                body = resp.get("result", {}).get("body", "")
                is_b64 = resp.get("result", {}).get("base64Encoded", False)
                if body:
                    if is_b64:
                        try:
                            body = base64.b64decode(body).decode("utf-8", errors="replace")
                        except:
                            pass
                    
                    try:
                        data = json.loads(body)
                        print(f"  解析成功! keys: {list(data.keys())}")
                        aweme_list = data.get("aweme_list") or data.get("data") or []
                        print(f"  aweme_list: {len(aweme_list)}")
                        if aweme_list:
                            for item in aweme_list[:3]:
                                if "aweme_info" in item:
                                    item = item["aweme_info"]
                                print(f"    ID: {item.get('aweme_id','')}")
                    except:
                        print(f"  body 前200: {body[:200]}")
                else:
                    print(f"  body 为空")
            except Exception as e:
                print(f"  错误: {e}")

asyncio.run(main())
