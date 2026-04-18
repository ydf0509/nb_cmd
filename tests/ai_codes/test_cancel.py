# -*- coding: utf-8 -*-
"""测试 Web UI 执行取消功能"""
import asyncio
from playwright.async_api import async_playwright

URL = "http://127.0.0.1:8089"


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1280, "height": 800})

        await page.goto(URL)
        await page.wait_for_selector("#formArea .form-section", timeout=10000)
        await asyncio.sleep(0.5)

        # 1) 验证初始状态：按钮可点击，停止按钮隐藏
        exec_btn = await page.query_selector(".cmd-input-wrapper button")
        is_disabled = await exec_btn.get_attribute("disabled")
        print("1. 初始状态 - 执行按钮 disabled:", is_disabled)

        stop_btn = await page.query_selector("#stopBtn")
        stop_visible = await stop_btn.is_visible()
        print("2. 初始状态 - 停止按钮可见:", stop_visible)

        # 2) 执行 many-print（长时间命令）
        inp = await page.query_selector("#cmdInput")
        await inp.fill("many-print")
        await exec_btn.click()
        await asyncio.sleep(1)

        # 3) 检查执行中状态
        is_disabled_2 = await exec_btn.get_attribute("disabled")
        print("3. 执行中 - 执行按钮 disabled:", is_disabled_2)

        stop_visible_2 = await stop_btn.is_visible()
        print("4. 执行中 - 停止按钮可见:", stop_visible_2)

        status_text = await page.inner_text("#statusText")
        print("5. 执行中 - 状态栏:", status_text)

        # 4) 点击停止
        await stop_btn.click()
        await asyncio.sleep(2)

        # 5) 检查取消后状态
        is_disabled_3 = await exec_btn.get_attribute("disabled")
        print("6. 取消后 - 执行按钮 disabled:", is_disabled_3)

        stop_visible_3 = await stop_btn.is_visible()
        print("7. 取消后 - 停止按钮可见:", stop_visible_3)

        status_text_2 = await page.inner_text("#statusText")
        print("8. 取消后 - 状态栏:", status_text_2)

        console_text = await page.inner_text("#consoleOutput")
        has_cancelled = "已取消" in console_text
        print("9. 控制台包含[已取消]:", has_cancelled)

        # 6) 截图验证
        await page.screenshot(path="d:/codes/nb_cmd/docs/images/web_ui_cancel_test.png")
        print("OK: 截图已保存")

        await browser.close()


asyncio.run(main())
