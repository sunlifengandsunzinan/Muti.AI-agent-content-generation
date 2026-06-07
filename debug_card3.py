#!/usr/bin/env python3
"""从 search card 中提取所有数据和 video ID"""
import asyncio, httpx, websockets, json

async def main():
    pages = httpx.get("http://127.0.0.1:18800/json").json()
    for p in pages:
        if p.get("type") == "page" and "douyin" in p.get("url", ""):
            target = p["webSocketDebuggerUrl"]
            break
    
    async with websockets.connect(target) as ws:
        # 1. 获取所有 card 的内容 + 寻找 video id 的任何迹象
        await ws.send(json.dumps({"id": 1, "method": "Runtime.evaluate", "params": {
            "expression": """
                (() => {
                    const cards = document.querySelectorAll('[class*="search-result-card"]');
                    const result = [];
                    for (const card of cards) {
                        const info = {};
                        
                        // 所有 img 的 src
                        const imgs = card.querySelectorAll('img');
                        info.imgSrcs = Array.from(imgs).map(i => i.getAttribute('src') || '').filter(Boolean);
                        
                        // 所有有 onclick 的元素
                        const clickables = card.querySelectorAll('[onclick]');
                        info.onclicks = Array.from(clickables).map(e => e.getAttribute('onclick')?.substring(0, 100));
                        
                        // 所有 data-e2e
                        const e2e = card.querySelectorAll('[data-e2e]');
                        info.dataE2e = Array.from(e2e)
                            .map(e => e.getAttribute('data-e2e') + '=' + (e.textContent?.trim()?.substring(0,30) || ''))
                            .filter(Boolean);
                        
                        // 整个 card 的数据属性
                        info.cardDataset = {};
                        for (const attr of card.attributes) {
                            if (attr.name.startsWith('data-')) {
                                info.cardDataset[attr.name] = attr.value.substring(0, 100);
                            }
                        }
                        
                        // 文本
                        info.text = (card.textContent || '').trim().substring(0, 200);
                        
                        result.push(info);
                    }
                    return JSON.stringify(result.slice(0, 3));
                })()
            """,
            "returnByValue": True
        }}))
        resp = json.loads(await asyncio.wait_for(ws.recv(), timeout=5))
        data = resp.get("result",{}).get("result",{}).get("value","[]")
        
        parsed = json.loads(data) if isinstance(data, str) else []
        for i, card in enumerate(parsed):
            print(f"\n卡片 {i}:")
            print(f"  文本: {card.get('text','')[:100]}")
            print(f"  data-e2e: {card.get('dataE2e',[])}")
            print(f"  onclick: {card.get('onclicks',[])}")
            print(f"  img: {card.get('imgSrcs',[])[:2]}")
            print(f"  cardDataset: {card.get('cardDataset',{})}")

asyncio.run(main())
