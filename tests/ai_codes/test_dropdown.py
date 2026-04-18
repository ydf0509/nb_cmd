# -*- coding: utf-8 -*-
"""测试 Web UI 下拉框功能（收藏 + 历史 + 模糊搜索）"""
import asyncio
from playwright.async_api import async_playwright

URL = "http://127.0.0.1:8091"


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1280, "height": 800})

        await page.goto(URL)
        await page.wait_for_selector("#formArea .form-section", timeout=10000)
        await asyncio.sleep(0.5)

        inp = await page.query_selector("#cmdInput")

        # 1) 执行几个命令生成历史
        for cmd in ["status", "show-users", "deploy web-01 --env staging"]:
            await inp.fill(cmd)
            exec_btn = await page.query_selector(".cmd-input-wrapper button")
            await exec_btn.click()
            await asyncio.sleep(2)
        print("1. 执行3个命令完成")

        # 2) 收藏一个命令
        await inp.fill("deploy web-01 --env staging")
        save_btn = await page.query_selector(".save-cmd-btn")
        await save_btn.click()
        await asyncio.sleep(0.5)
        print("2. 收藏命令完成")

        # 3) 点击输入框，看下拉框是否出现
        await inp.click()
        await inp.fill("")
        await asyncio.sleep(0.3)
        await inp.focus()
        await asyncio.sleep(0.5)

        dd = await page.query_selector("#cmdDropdown")
        dd_visible = await dd.is_visible()
        dd_text = await dd.inner_text() if dd_visible else ""
        print("3. 下拉框可见:", dd_visible)
        print("4. 下拉框内容:", dd_text.replace('\n', ' | '))

        # 4) 模糊搜索
        await inp.fill("dep")
        await asyncio.sleep(0.3)
        dd_text2 = await dd.inner_text()
        has_deploy = "deploy" in dd_text2.lower()
        has_status = "status" in dd_text2.lower()
        print("5. 搜索 'dep' - 包含 deploy:", has_deploy, ", 包含 status:", has_status)

        # 5) 截图
        await page.screenshot(path="d:/codes/nb_cmd/docs/images/web_ui_dropdown_test.png")
        print("OK: 截图已保存")

        # 6) 刷新验证持久化
        await page.reload()
        await page.wait_for_selector("#formArea .form-section", timeout=10000)
        await asyncio.sleep(1)
        inp2 = await page.query_selector("#cmdInput")
        await inp2.click()
        await asyncio.sleep(0.5)
        dd2 = await page.query_selector("#cmdDropdown")
        dd2_visible = await dd2.is_visible()
        dd2_text = await dd2.inner_text() if dd2_visible else ""
        print("6. 刷新后下拉框可见:", dd2_visible)
        print("7. 刷新后内容:", dd2_text.replace('\n', ' | '))

        await browser.close()


asyncio.run(main())
