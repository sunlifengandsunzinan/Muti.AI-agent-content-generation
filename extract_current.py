#!/usr/bin/env python3
"""提取当前页面上所有视频链接"""
import asyncio
import httpx
import websockets
import json

async def main():
    pages = httpx.get("http://127.0.0.1:18800/json").json()
    target = None
    for p in pages:
        if p.get("type") == "page" and "douyin" in p.get("url", ""):
            target = p["webSocketDebuggerUrl"]
            print("页面:", p.get("url", "")[:80])
            break
    
    async with websockets.connect(target) as ws:
        # 从 search-result-card 提取视频信息
        await ws.send(json.dumps({"id": 1, "method": "Runtime.evaluate", "params": {
            "expression": """
                JSON.stringify(
                    (() => {
                        const items = [];
                        const seen = new Set();
                        
                        // 从所有 search-result-card 提取
                        const cards = document.querySelectorAll('[class*="search-result-card"]');
                        for (const card of cards) {
                            try {
                                // 找视频链接
                                const link = card.querySelector('a[href*="/video/"]');
                                if (!link) continue;
                                const href = link.getAttribute('href');
                                if (!href) continue;
                                const m = href.match(/\\/video\\/(\\d+)/);
                                if (!m || seen.has(m[1])) continue;
                                seen.add(m[1]);
                                
                                const title = link.getAttribute('title') || link.textContent?.trim() || '';
                                const url = 'https://www.douyin.com' + (href.startsWith('/') ? href : '/video/' + m[1]);
                                
                                // 找作者
                                let author = '';
                                const authorEl = card.querySelector('[class*="author"], [class*="nickname"]');
                                if (authorEl) author = authorEl.textContent?.trim() || '';
                                
                                // 找统计
                                let likes = '', plays = '';
                                const countEls = card.querySelectorAll('[class*="count"], [class*="number"]');
                                for (const el of countEls) {
                                    const t = el.textContent?.trim() || '';
                                    if (t.match(/\\d/)) {
                                        if (!likes) likes = t;
                                        else if (!plays) plays = t;
                                    }
                                }
                                
                                items.push({aweme_id: m[1], url: url, title: title, author: author, likes: likes, plays: plays});
                            } catch(e) {}
                        }
                        
                        // 也检查 videoImage 容器
                        const vids = document.querySelectorAll('[class*="videoImage"], [class*="video-image"]');
                        for (const v of vids) {
                            const link = v.closest('a') || v.querySelector('a');
                            if (!link) continue;
                            const href = link.getAttribute('href');
                            if (!href) continue;
                            const m = href.match(/\\/video\\/(\\d+)/);
                            if (m && !seen.has(m[1])) {
                                seen.add(m[1]);
                                items.push({
                                    aweme_id: m[1],
                                    url: 'https://www.douyin.com/video/' + m[1],
                                    title: link.getAttribute('title') || '',
                                });
                            }
                        }
                        
                        return items;
                    })()
                )
            """,
            "returnByValue": True
        }}))
        resp = json.loads(await asyncio.wait_for(ws.recv(), timeout=5))
        raw = resp.get("result",{}).get("result",{}).get("value","[]")
        
        results = json.loads(raw) if isinstance(raw, str) else []
        print(f"\n提取到 {len(results)} 个视频:")
        print("=" * 60)
        for i, r in enumerate(results, 1):
            print(f"\n  [{i}] {r.get('title','')[:60]}")
            print(f"      作者: {r.get('author','?')}")
            print(f"      链接: {r.get('url','')}")
        
        # 保存到文件
        import os
        output_dir = r"C:\Users\Administrator\.openclaw\workspace\skills\douyin-search\search_results"
        os.makedirs(output_dir, exist_ok=True)
        from datetime import datetime
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        links_path = os.path.join(output_dir, f"links_{ts}.txt")
        with open(links_path, "w", encoding="utf-8") as f:
            for r in results:
                f.write(r.get("url", "") + "\n")
        
        json_path = os.path.join(output_dir, f"search_{ts}.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump({"time": ts, "count": len(results), "results": results}, f, ensure_ascii=False, indent=2)
        
        print(f"\n保存: {links_path} ({len(results)} 条)")
        print(f"     {json_path}")

asyncio.run(main())
