# -*- coding: utf-8 -*-
"""测试修复后的持久化功能"""
import asyncio
from playwright.async_api import async_playwright

URL = "http://127.0.0.1:8092"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={'width': 1280, 'height': 800})

        await page.goto(URL)
        await page.wait_for_selector('#formArea .form-section', timeout=10000)
        await asyncio.sleep(1)

        # 1) 清理旧数据并保存新命令
        inp = await page.query_selector('#cmdInput')
        save_btn = await page.query_selector('.save-cmd-btn')

        for cmd in ["test-cmd-1", "test-cmd-2", "test-cmd-3"]:
            await inp.fill(cmd)
            await save_btn.click()
            await asyncio.sleep(0.3)
        print("1. 保存3个命令完成")

        # 2) 检查下拉框
        await inp.fill("")
        await asyncio.sleep(0.3)
        dd = await page.query_selector('#cmdDropdown')
        dd_vis = await dd.is_visible()
        dd_text = await dd.inner_text()
        print("2. 下拉框可见:", dd_vis)
        has_all = "test-cmd-1" in dd_text and "test-cmd-2" in dd_text and "test-cmd-3" in dd_text
        print("3. 包含所有3个命令:", has_all)

        # 3) F5 刷新
        await page.reload()
        await page.wait_for_selector('#formArea .form-section', timeout=10000)
        await asyncio.sleep(2)

        # 4) 点击输入框
        await page.click('#cmdInput')
        await asyncio.sleep(0.5)
        dd2 = await page.query_selector('#cmdDropdown')
        dd2_vis = await dd2.is_visible()
        dd2_text = await dd2.inner_text() if dd2_vis else ""
        has_all2 = "test-cmd-1" in dd2_text and "test-cmd-2" in dd2_text and "test-cmd-3" in dd2_text
        print("4. 刷新后点击 - 下拉框可见:", dd2_vis)
        print("5. 刷新后包含所有3个命令:", has_all2)

        # 5) 截图
        await page.screenshot(path="d:/codes/nb_cmd/docs/images/test_fixed.png")
        print("OK: 截图已保存")

        await browser.close()

asyncio.run(main())
