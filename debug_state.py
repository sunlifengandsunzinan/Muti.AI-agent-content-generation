#!/usr/bin/env python3
"""检查抖音页面全局数据"""
import asyncio, httpx, websockets, json

async def main():
    pages = httpx.get("http://127.0.0.1:18800/json").json()
    for p in pages:
        if p.get("type") == "page" and "douyin" in p.get("url", ""):
            target = p["webSocketDebuggerUrl"]
            print("页面:", p.get("url", "")[:80])
            break
    else:
        print("无页面")
        return
    
    async with websockets.connect(target) as ws:
        checks = [
            "typeof window.__INITIAL_STATE__ !== 'undefined'",
            "typeof window.__NEXT_DATA__ !== 'undefined'",
            "typeof window.__NUXT__ !== 'undefined'",
            "typeof window.pageData !== 'undefined'",
            "typeof window.STORE !== 'undefined'",
            "typeof window.__ROOT_DATA__ !== 'undefined'",
            "typeof window.__PRELOADED_STATE__ !== 'undefined'",
        ]
        
        for expr in checks:
            await ws.send(json.dumps({"id": 1, "method": "Runtime.evaluate", "params": {
                "expression": expr, "returnByValue": True
            }}))
            resp = json.loads(await asyncio.wait_for(ws.recv(), timeout=3))
            found = resp.get("result",{}).get("result",{}).get("value", False)
            var_name = expr.split("typeof ")[1].split(" !== ")[0]
            if found:
                print(f"  ✅ {var_name}")
            else:
                print(f"  ❌ {var_name}")
        
        # 检查 __NEXT_DATA__ 或 __INITIAL_STATE__ 的内容
        await ws.send(json.dumps({"id": 2, "method": "Runtime.evaluate", "params": {
            "expression": """
                (() => {
                    let data = null;
                    if (window.__INITIAL_STATE__) data = window.__INITIAL_STATE__;
                    else if (window.__NEXT_DATA__) data = window.__NEXT_DATA__;
                    if (data) {
                        const keys = Object.keys(data).join(', ');
                        const len = JSON.stringify(data).length;
                        return `KEYS: ${keys} | SIZE: ${len}`;
                    }
                    return 'NO_DATA';
                })()
            """,
            "returnByValue": True
        }}))
        resp = json.loads(await asyncio.wait_for(ws.recv(), timeout=3))
        print(f"\n数据源: {resp.get('result',{}).get('result',{}).get('value','')}")
        
        # 检查页面里有没有 video id 相关的数据属性
        await ws.send(json.dumps({"id": 3, "method": "Runtime.evaluate", "params": {
            "expression": """
                (() => {
                    const cards = document.querySelectorAll('[class*="search-result-card"]');
                    const first = cards[0];
                    if (!first) return "no cards";
                    
                    // 看所有属性
                    const attrs = [];
                    for (const attr of first.attributes) {
                        attrs.push(attr.name + '=' + (attr.value || '').substring(0, 80));
                    }
                    
                    // 找 img 的 parent 有没有 data
                    const img = first.querySelector('img');
                    const imgAttrs = img ? Array.from(img.attributes).map(a => a.name + '=' + (a.value || '').substring(0,60)).join(' | ') : 'no img';
                    
                    // 找 title 内容
                    const allText = first.textContent?.trim()?.substring(0, 300) || '';
                    
                    return {
                        attrs: attrs.join('\\n'),
                        imgAttrs: imgAttrs,
                        text: allText,
                    };
                })()
            """,
            "returnByValue": True
        }}))
        resp = json.loads(await asyncio.wait_for(ws.recv(), timeout=5))
        val = resp.get("result",{}).get("result",{}).get("value",{})
        print(f"\n卡片属性:\n{val.get('attrs','')}")
        print(f"\n图片属性:\n{val.get('imgAttrs','')}")
        print(f"\n文本 (前300):\n{val.get('text','')}")

asyncio.run(main())
