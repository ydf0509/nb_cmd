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

        # check if focus event triggers dropdown
        await page.click('#cmdInput')
        await asyncio.sleep(0.5)

        dd_cls = await page.evaluate("document.getElementById('cmdDropdown').className")
        print("1. After click class:", dd_cls)

        # manually trigger focus event
        await page.evaluate("document.getElementById('cmdInput').dispatchEvent(new Event('focus'))")
        await asyncio.sleep(0.3)
        dd_cls2 = await page.evaluate("document.getElementById('cmdDropdown').className")
        print("2. After dispatchEvent class:", dd_cls2)

        # manually call showDropdown
        await page.evaluate("showDropdown()")
        await asyncio.sleep(0.3)
        dd_cls3 = await page.evaluate("document.getElementById('cmdDropdown').className")
        items = await page.evaluate("document.getElementById('cmdDropdown')._items ? document.getElementById('cmdDropdown')._items.length : -1")
        print("3. After showDropdown class:", dd_cls3, "items:", items)

        # screenshot
        await page.screenshot(path="d:/codes/nb_cmd/docs/images/test_debug2.png")
        print("OK")

        await browser.close()

asyncio.run(main())
