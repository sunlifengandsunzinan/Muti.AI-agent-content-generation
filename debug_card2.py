#!/usr/bin/env python3
"""提取全部 search card 的完整 HTML"""
import asyncio, httpx, websockets, json

async def main():
    pages = httpx.get("http://127.0.0.1:18800/json").json()
    for p in pages:
        if p.get("type") == "page" and "douyin" in p.get("url", ""):
            target = p["webSocketDebuggerUrl"]
            print("页面:", p.get("url", "")[:80])
            break
    else:
        return
    
    async with websockets.connect(target) as ws:
        # 获取所有 card 的 outerHTML
        await ws.send(json.dumps({"id": 1, "method": "Runtime.evaluate", "params": {
            "expression": """
                (() => {
                    const cards = document.querySelectorAll('[class*="search-result-card"]');
                    if (!cards.length) return "no cards";
                    return Array.from(cards).slice(0,3).map((c, i) => {
                        // 找视频 ID (可能藏在 data-* 或 onclick 或 img 里)
                        const html = c.outerHTML;
                        
                        // 找标题
                        const titleEl = c.querySelector('[class*="desc"], [class*="title"]');
                        const title = titleEl ? titleEl.textContent?.trim()?.substring(0,60) : '';
                        
                        // 找作者
                        const authorEl = c.querySelector('[class*="author"], [class*="nickname"]');
                        const author = authorEl ? authorEl.textContent?.trim() : '';
                        
                        // 找 img 的 alt 或 data-*
                        const img = c.querySelector('img');
                        const imgAlt = img ? img.getAttribute('alt') || '' : '';
                        const imgSrc = img ? (img.getAttribute('src') || '').substring(0,80) : '';
                        
                        // 找所有 data-* 属性
                        const dataset = {};
                        for (const attr of c.attributes) {
                            if (attr.name.startsWith('data-')) {
                                dataset[attr.name] = attr.value.substring(0,100);
                            }
                        }
                        for (const attr of (titleEl?.attributes || [])) {
                            if (attr.name.startsWith('data-')) {
                                dataset[attr.name] = attr.value.substring(0,100);
                            }
                        }
                        
                        return {i, title, author, imgAlt, imgSrc, dataset, htmlLength: html.length};
                    });
                })()
            """,
            "returnByValue": True
        }}))
        resp = json.loads(await asyncio.wait_for(ws.recv(), timeout=5))
        data = resp.get("result",{}).get("result",{}).get("value",[])
        
        print(f"\n共 {len(data)} 张卡片:\n")
        for d in data:
            print(f"  [{d.get('i')}] 标题: {d.get('title','')[:50]}")
            print(f"      作者: {d.get('author','')}")
            print(f"      imgAlt: {d.get('imgAlt','')}")
            print(f"      dataset: {d.get('dataset',{})}")
            print()

asyncio.run(main())
