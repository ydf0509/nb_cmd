# -*- coding: utf-8 -*-
"""测试下拉框始终显示"""
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={'width': 1280, 'height': 800})
        await page.goto('http://127.0.0.1:8092')
        await page.wait_for_selector('#formArea .form-section', timeout=10000)
        await asyncio.sleep(1)

        # 1) 空状态——没有任何收藏或历史
        await page.click('#cmdInput')
        await asyncio.sleep(0.5)
        dd = await page.query_selector('#cmdDropdown')
        vis = await dd.is_visible()
        text = await dd.inner_text()
        print("1. 空状态 - 可见:", vis)
        print("2. 内容:", text.replace('\n', ' | '))

        await page.screenshot(path='d:/codes/nb_cmd/docs/images/test_empty.png')

        # 2) 执行一个命令，再检查
        inp = await page.query_selector('#cmdInput')
        await inp.fill("status")
        btn = await page.query_selector('.cmd-input-wrapper button:first-of-type')
        await btn.click()
        await asyncio.sleep(2)

        await inp.fill("")
        await inp.click()
        await asyncio.sleep(0.3)
        text2 = await dd.inner_text()
        print("3. 执行后:", text2.replace('\n', ' | '))

        # 3) 搜索无匹配
        await inp.fill("zzzzz")
        await asyncio.sleep(0.3)
        text3 = await dd.inner_text()
        print("4. 搜索无匹配:", text3.replace('\n', ' | '))

        await page.screenshot(path='d:/codes/nb_cmd/docs/images/test_nomatch.png')
        print("OK")

        await browser.close()

asyncio.run(main())
