# -*- coding: utf-8 -*-
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={'width': 1280, 'height': 800})
        await page.goto('http://127.0.0.1:8092')
        await page.wait_for_selector('#formArea .form-section', timeout=10000)
        await asyncio.sleep(2)

        active = await page.evaluate("document.activeElement ? document.activeElement.id : 'none'")
        print("1. activeElement:", active)

        area = await page.evaluate("document.querySelector('.cmd-input-area') ? 'found' : 'NOT FOUND'")
        print("2. .cmd-input-area:", area)

        # click and check
        await page.click('#cmdInput')
        await asyncio.sleep(0.3)
        active2 = await page.evaluate("document.activeElement ? document.activeElement.id : 'none'")
        dd_cls = await page.evaluate("document.getElementById('cmdDropdown').className")
        print("3. After click activeElement:", active2)
        print("4. dropdown class:", dd_cls)

        # try manual showDropdown
        await page.evaluate("showDropdown()")
        await asyncio.sleep(0.3)
        dd_cls2 = await page.evaluate("document.getElementById('cmdDropdown').className")
        print("5. After manual showDropdown:", dd_cls2)
        
        await browser.close()

asyncio.run(main())
