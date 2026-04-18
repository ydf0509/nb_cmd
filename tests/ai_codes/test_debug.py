# -*- coding: utf-8 -*-
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={'width': 1280, 'height': 800})
        errors = []
        page.on('console', lambda m: errors.append(m.text) if m.type == 'error' else None)
        page.on('pageerror', lambda e: errors.append(str(e)))

        await page.goto('http://127.0.0.1:8092')
        await page.wait_for_selector('#formArea .form-section', timeout=10000)
        await asyncio.sleep(2)
        print('JS errors:', errors)

        n = await page.evaluate('window.savedCmds ? savedCmds.length : -1')
        print('savedCmds.length:', n)

        js = """
        (function() {
            try {
                renderDropdown();
                var dd = document.getElementById('cmdDropdown');
                return {cls: dd.className, html: dd.innerHTML.substring(0, 300), items: dd._items ? dd._items.length : -1};
            } catch(e) {
                return {error: e.message};
            }
        })()
        """
        result = await page.evaluate(js)
        print('result:', result)

        await browser.close()

asyncio.run(main())
