# -*- coding: utf-8 -*-
"""测试面板失焦自动折叠"""
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={'width': 1280, 'height': 800})
        await page.goto('http://127.0.0.1:8093')
        await page.wait_for_selector('#formArea .form-section', timeout=10000)
        await asyncio.sleep(1)

        # 保存一个命令
        inp = await page.query_selector('#cmdInput')
        save_btn = await page.query_selector('.save-cmd-btn')
        await inp.fill("deploy web-01")
        await save_btn.click()
        await asyncio.sleep(0.3)

        # 1) 默认折叠
        b = await page.is_visible('#savedBody')
        print("1. 默认折叠:", not b)

        # 2) 点击收藏搜索框展开
        await page.click('#savedSearch')
        await asyncio.sleep(0.3)
        b2 = await page.is_visible('#savedBody')
        print("2. 点击后展开:", b2)

        # 3) 点击页面其他地方折叠
        await page.click('.console-area')
        await asyncio.sleep(0.3)
        b3 = await page.is_visible('#savedBody')
        print("3. 点击外部后折叠:", not b3)

        # 4) 再次展开再点命令列表折叠
        await page.click('#savedSearch')
        await asyncio.sleep(0.3)
        await page.click('#cmdInput')
        await asyncio.sleep(0.3)
        b4 = await page.is_visible('#savedBody')
        print("4. 点击输入框后折叠:", not b4)

        print("OK")
        await browser.close()

asyncio.run(main())
