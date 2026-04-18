# -*- coding: utf-8 -*-
"""测试固定面板式收藏/历史"""
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={'width': 1280, 'height': 800})
        await page.goto('http://127.0.0.1:8092')
        await page.wait_for_selector('#formArea .form-section', timeout=10000)
        await asyncio.sleep(1)

        # 1) 面板始终可见
        panel = await page.query_selector('#cmdPanel')
        vis = await panel.is_visible()
        text = await page.inner_text('#panelBody')
        print("1. 面板可见:", vis)
        print("2. 空状态:", text.replace('\n', ' | '))

        # 2) 保存命令
        inp = await page.query_selector('#cmdInput')
        save_btn = await page.query_selector('.save-cmd-btn')
        for cmd in ["deploy web-01", "status --verbose"]:
            await inp.fill(cmd)
            await save_btn.click()
            await asyncio.sleep(0.3)

        text2 = await page.inner_text('#panelBody')
        print("3. 保存后:", text2.replace('\n', ' | '))

        # 3) 执行命令生成历史
        await inp.fill("status")
        exec_btn = await page.query_selector('.cmd-input-wrapper button:first-of-type')
        await exec_btn.click()
        await asyncio.sleep(2)
        text3 = await page.inner_text('#panelBody')
        print("4. 执行后:", text3.replace('\n', ' | '))

        # 4) 搜索过滤
        search = await page.query_selector('#panelSearch')
        await search.fill("dep")
        await asyncio.sleep(0.3)
        text4 = await page.inner_text('#panelBody')
        print("5. 搜索dep:", text4.replace('\n', ' | '))

        # 5) 点击命令填入输入框
        item = await page.query_selector('.dd-item')
        if item:
            await item.click()
            await asyncio.sleep(0.3)
            val = await page.eval_on_selector('#cmdInput', 'el => el.value')
            print("6. 点击后输入框:", val)

        # 6) 截图
        await page.screenshot(path='d:/codes/nb_cmd/docs/images/test_panel.png')

        # 7) F5 刷新验证持久化
        await page.reload()
        await page.wait_for_selector('#formArea .form-section', timeout=10000)
        await asyncio.sleep(2)
        panel2 = await page.query_selector('#cmdPanel')
        vis2 = await panel2.is_visible()
        text5 = await page.inner_text('#panelBody')
        has_data = 'deploy' in text5 and 'status' in text5
        print("7. 刷新后面板可见:", vis2, "包含数据:", has_data)

        print("OK")
        await browser.close()

asyncio.run(main())
