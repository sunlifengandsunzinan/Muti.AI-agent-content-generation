#!/usr/bin/env python3
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp('http://127.0.0.1:18800')
        context = browser.contexts[0]
        page = await context.new_page()
        await page.goto('https://www.doubao.com/chat', wait_until='domcontentloaded', timeout=20000)
        await page.wait_for_timeout(5000)
        
        await page.screenshot(path='doubao_check.png', full_page=True)
        print('截图已保存')
        
        html = await page.content()
        with open('doubao_html.txt', 'w', encoding='utf-8') as f:
            f.write(html[:30000])
        print(f'HTML 长度: {len(html)}')
        
        textareas = await page.query_selector_all('textarea')
        print(f'textarea数量: {len(textareas)}')
        
        editable = await page.query_selector_all('[contenteditable]')
        print(f'contenteditable数量: {len(editable)}')
        for el in editable:
            outer = await el.get_attribute('outerHTML') or ''
            print(f'  outerHTML[:150]: {outer[:150]}')
        
        textbox = await page.query_selector_all('[role="textbox"]')
        print(f'role=textbox数量: {len(textbox)}')
        for el in textbox:
            outer = await el.get_attribute('outerHTML') or ''
            print(f'  outerHTML[:150]: {outer[:150]}')
        
        buttons = await page.query_selector_all('button')
        print(f'button数量: {len(buttons)}')
        for b in buttons[:5]:
            text = await b.inner_text()
            print(f'  button: "{text[:30]}"')
        
        await browser.close()

asyncio.run(main())
