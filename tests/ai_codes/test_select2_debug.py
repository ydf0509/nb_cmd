# -*- coding: utf-8 -*-
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={'width': 1280, 'height': 800})
        await page.goto('http://127.0.0.1:8093')
        await page.wait_for_selector('#formArea .form-section', timeout=10000)
        await asyncio.sleep(1)

        # check s2-wrap exists
        s2_wrap = await page.query_selector('.s2-wrap')
        print("s2-wrap exists:", s2_wrap is not None)

        s2_box = await page.query_selector('#s2Saved')
        print("s2Saved exists:", s2_box is not None)

        s2_trigger = await page.query_selector('#s2Saved .s2-trigger')
        print("s2-trigger exists:", s2_trigger is not None)

        # dump a snippet of html near cmd-input-area
        html_snippet = await page.evaluate('''() => {
            var el = document.querySelector('.cmd-input-area');
            if (!el) return 'cmd-input-area not found';
            var next = el.nextElementSibling;
            return next ? next.outerHTML.substring(0, 500) : 'no next sibling';
        }''')
        print("Next sibling after cmd-input-area:", html_snippet)

        await browser.close()

asyncio.run(main())
