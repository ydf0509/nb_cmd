# -*- coding: utf-8 -*-
"""测试折叠面板：搜索框始终可见，点击展开，点击外部折叠"""
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={'width': 1280, 'height': 800})
        await page.goto('http://127.0.0.1:8093')
        await page.wait_for_selector('#formArea .form-section', timeout=10000)
        await asyncio.sleep(1)

        # 1) 搜索框可见，内容区折叠
        search_vis = await page.is_visible('#panelSearch')
        body_vis = await page.is_visible('#panelBody')
        print("1. 搜索框可见:", search_vis, "内容区可见:", body_vis)

        # 2) 点击搜索框展开
        await page.click('#panelSearch')
        await asyncio.sleep(0.3)
        body_vis2 = await page.is_visible('#panelBody')
        text = await page.inner_text('#panelBody')
        print("2. 点击搜索框后内容区可见:", body_vis2)
        print("3. 内容:", text.replace('\n', ' | '))

        # 截图——展开状态
        await page.screenshot(path='d:/codes/nb_cmd/docs/images/test_expanded.png')

        # 3) 点击外部折叠
        await page.click('.console-area')
        await asyncio.sleep(0.3)
        body_vis3 = await page.is_visible('#panelBody')
        print("4. 点击外部后内容区可见:", body_vis3)

        # 截图——折叠状态
        await page.screenshot(path='d:/codes/nb_cmd/docs/images/test_collapsed.png')

        # 4) 保存命令并验证
        inp = await page.query_selector('#cmdInput')
        save_btn = await page.query_selector('.save-cmd-btn')
        await inp.fill("deploy web-01")
        await save_btn.click()
        await asyncio.sleep(0.5)

        # 展开搜索
        await page.click('#panelSearch')
        await asyncio.sleep(0.3)
        text2 = await page.inner_text('#panelBody')
        has_deploy = 'deploy' in text2
        print("5. 保存后展开包含deploy:", has_deploy)

        print("OK")
        await browser.close()

asyncio.run(main())
