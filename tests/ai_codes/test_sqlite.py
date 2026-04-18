# -*- coding: utf-8 -*-
"""测试 Web UI SQLite 收藏和历史功能"""
import asyncio
from playwright.async_api import async_playwright

URL = "http://127.0.0.1:8090"


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1280, "height": 800})

        await page.goto(URL)
        await page.wait_for_selector("#formArea .form-section", timeout=10000)
        await asyncio.sleep(0.5)

        # 1) 执行一个命令——验证历史记录持久化
        inp = await page.query_selector("#cmdInput")
        await inp.fill("status")
        btn = await page.query_selector(".cmd-input-wrapper button")
        await btn.click()
        await asyncio.sleep(2)
        print("1. 执行 status 完成")

        # 2) 在输入框中输入命令并点击保存
        await inp.fill("deploy web-01 --env staging")
        save_btn = await page.query_selector(".save-cmd-btn")
        await save_btn.click()
        await asyncio.sleep(0.5)
        print("2. 保存命令完成")

        # 3) 检查收藏区域是否显示
        saved_area = await page.query_selector("#savedCmdsArea")
        saved_visible = await saved_area.is_visible()
        print("3. 收藏区域可见:", saved_visible)

        saved_text = await saved_area.inner_text()
        has_saved = "deploy web-01" in saved_text
        print("4. 收藏包含命令:", has_saved)

        # 4) 再保存一个命令
        await inp.fill("show-users")
        await save_btn.click()
        await asyncio.sleep(0.5)

        saved_text2 = await saved_area.inner_text()
        print("5. 收藏列表:", saved_text2.replace('\n', ' | '))

        # 5) 重新加载页面——验证持久化
        await page.reload()
        await page.wait_for_selector("#formArea .form-section", timeout=10000)
        await asyncio.sleep(1)

        saved_area2 = await page.query_selector("#savedCmdsArea")
        saved_visible2 = await saved_area2.is_visible()
        print("6. 刷新后收藏仍可见:", saved_visible2)

        history_el = await page.query_selector("#historyList")
        history_text = await history_el.inner_text()
        has_history = "status" in history_text
        print("7. 刷新后历史包含 status:", has_history)

        # 6) 点击收藏命令——填入输入框
        saved_item = await page.query_selector(".saved-cmd-item .saved-text")
        if saved_item:
            await saved_item.click()
            await asyncio.sleep(0.3)
            inp_val = await page.eval_on_selector("#cmdInput", "el => el.value")
            print("8. 点击收藏后输入框:", inp_val)

        # 7) 截图
        await page.screenshot(path="d:/codes/nb_cmd/docs/images/web_ui_sqlite_test.png")
        print("OK: 截图已保存")

        await browser.close()


asyncio.run(main())
