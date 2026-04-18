# -*- coding: utf-8 -*-
"""测试 SQLite 持久化 — 多次保存 + 刷新不丢失"""
import asyncio
from playwright.async_api import async_playwright

URL = "http://127.0.0.1:8092"


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1280, "height": 800})

        await page.goto(URL)
        await page.wait_for_selector("#formArea .form-section", timeout=10000)
        await asyncio.sleep(0.5)

        inp = await page.query_selector("#cmdInput")
        save_btn = await page.query_selector(".save-cmd-btn")

        # 1) 连续保存3个命令
        for cmd in ["deploy web-01", "status", "show-users"]:
            await inp.fill(cmd)
            await save_btn.click()
            await asyncio.sleep(0.5)
        print("1. 保存3个命令完成")

        # 2) 聚焦输入框，检查下拉框
        await inp.click()
        await inp.fill("")
        await asyncio.sleep(0.3)
        dd = await page.query_selector("#cmdDropdown")
        dd_text = await dd.inner_text()
        saved_count = dd_text.count("★")
        print("2. 下拉框收藏数:", saved_count, "(期望3)")
        print("   内容:", dd_text.replace('\n', ' | '))

        # 3) 截图——保存后状态
        await page.screenshot(path="d:/codes/nb_cmd/docs/images/test_persist_before.png")

        # 4) 再保存2个
        for cmd in ["process", "many-print"]:
            await inp.fill(cmd)
            await save_btn.click()
            await asyncio.sleep(0.5)
        print("3. 再保存2个命令完成")

        await inp.fill("")
        await asyncio.sleep(0.3)
        dd_text2 = await dd.inner_text()
        saved_count2 = dd_text2.count("★")
        print("4. 下拉框收藏数:", saved_count2, "(期望5)")

        # 5) F5 刷新
        await page.reload()
        await page.wait_for_selector("#formArea .form-section", timeout=10000)
        await asyncio.sleep(2)

        inp2 = await page.query_selector("#cmdInput")
        await inp2.click()
        await asyncio.sleep(0.5)
        dd2 = await page.query_selector("#cmdDropdown")
        dd2_vis = await dd2.is_visible()
        dd2_text = await dd2.inner_text() if dd2_vis else ""
        saved_count3 = dd2_text.count("★") if dd2_text else 0
        print("5. 刷新后下拉框可见:", dd2_vis)
        print("6. 刷新后收藏数:", saved_count3, "(期望5)")
        print("   内容:", dd2_text.replace('\n', ' | '))

        # 6) 截图——刷新后状态
        await page.screenshot(path="d:/codes/nb_cmd/docs/images/test_persist_after.png")
        print("OK: 截图已保存")

        await browser.close()


asyncio.run(main())
