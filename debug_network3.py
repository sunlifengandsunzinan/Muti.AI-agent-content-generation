#!/usr/bin/env python3
"""正确捕获搜索 API 响应体"""
import asyncio, httpx, websockets, json

async def main():
    pages = httpx.get("http://127.0.0.1:18800/json").json()
    target = None
    for p in pages:
        if p.get("type") == "page" and "douyin" in p.get("url", ""):
            target = p["webSocketDebuggerUrl"]
            print("页面:", p.get("url", "")[:80])
            break
    
    async with websockets.connect(target, max_size=10*1024*1024) as ws:
        await ws.send(json.dumps({"id": 1, "method": "Network.enable", "params": {}}))
        await asyncio.sleep(0.3)
        
        # 导航新搜索词
        await ws.send(json.dumps({"id": 2, "method": "Page.navigate", "params": {
            "url": "https://www.douyin.com/search/%E6%91%A9%E6%97%85%E8%B7%AF%E7%BA%BF?type=general"
        }}))
        
        # 收集网络事件
        events = []
        start = asyncio.get_event_loop().time()
        while asyncio.get_event_loop().time() - start < 15:
            try:
                resp = json.loads(await asyncio.wait_for(ws.recv(), timeout=15))
                events.append(resp)
            except asyncio.TimeoutError:
                break
            except websockets.ConnectionClosed:
                break
        
        # 分析事件
        responses = [e for e in events if e.get("method") == "Network.responseReceived"]
        search_apis = [e for e in responses if "/search/" in e.get("params",{}).get("response",{}).get("url","") or "general/search" in e.get("params",{}).get("response",{}).get("url","")]
        
        print(f"\n全部事件: {len(events)}")
        print(f"响应事件: {len(responses)}")
        print(f"搜索 API: {len(search_apis)}")
        
        for sa in search_apis:
            url = sa.get("params",{}).get("response",{}).get("url","")
            req_id = sa.get("params",{}).get("requestId","")
            print(f"\nAPI URL: {url[:120]}")
            print(f"RequestId: {req_id}")
            
            # 请求 body
            await ws.send(json.dumps({"id": 100, "method": "Network.getResponseBody", "params": {"requestId": req_id}}))
            try:
                body_resp = json.loads(await asyncio.wait_for(ws.recv(), timeout=5))
                body = body_resp.get("result", {}).get("body", "")
                if body:
                    try:
                        data = json.loads(body)
                    except:
                        # try base64
                        import base64
                        if body_resp.get("result",{}).get("base64Encoded"):
                            body = base64.b64decode(body).decode("utf-8")
                            data = json.loads(body)
                        else:
                            print(f"  ❌ 解析失败, body前200: {body[:200]}")
                            continue
                    
                    print(f"  ✅ 解析成功! keys: {list(data.keys())}")
                    
                    aweme_list = data.get("aweme_list") or []
                    data_list = data.get("data") or []
                    
                    if aweme_list:
                        print(f"  视频数: {len(aweme_list)}")
                        for item in aweme_list[:3]:
                            print(f"    ID: {item.get('aweme_id','')} | {item.get('desc','')[:50]}")
                    elif data_list:
                        print(f"  data 数: {len(data_list)}")
                        for d in data_list[:3]:
                            aweme = d.get("aweme_info", {})
                            if aweme:
                                print(f"    ID: {aweme.get('aweme_id','')} | {aweme.get('desc','')[:50]}")
                            else:
                                print(f"    keys: {list(d.keys())}")
                    else:
                        print(f"  没有视频列表, 检查其他字段...")
                        for k, v in data.items():
                            if isinstance(v, list) and len(v) > 0:
                                print(f"    {k}: {len(v)} 条 - 样本: {str(v[0])[:100]}")
                            elif isinstance(v, dict):
                                print(f"    {k}: dict with {list(v.keys())}")
                            elif k not in ('status_code', 'has_more', 'cursor', 'extra', 'log_pb', 'backtrace', 'global_doodle_config', 'path'):
                                print(f"    {k}: {str(v)[:80]}")
            except Exception as e:
                print(f"  ❌ 错误: {e}")

asyncio.run(main())
