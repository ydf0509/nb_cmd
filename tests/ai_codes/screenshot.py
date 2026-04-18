# -*- coding: utf-8 -*-
"""Playwright 自动截图 Web UI"""
import asyncio
from playwright.async_api import async_playwright

URL = "http://127.0.0.1:8088"
OUT_DIR = "d:/codes/nb_cmd/docs/images"


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1280, "height": 800})

        await page.goto(URL)
        await page.wait_for_selector("#formArea .form-section", timeout=10000)
        await asyncio.sleep(0.5)

        # 展开 deploy 命令
        headers = await page.query_selector_all(".form-section-header")
        for h in headers:
            text = await h.inner_text()
            if "deploy" in text.lower():
                await h.click()
                await asyncio.sleep(0.3)
                break

        await page.screenshot(path=OUT_DIR + "/web_ui_main.png", full_page=False)
        print("OK: web_ui_main.png")

        # 执行 stats 命令
        inp = await page.query_selector("#cmdInput")
        await inp.fill("stats")
        btn = await page.query_selector(".cmd-input-wrapper button")
        await btn.click()
        await asyncio.sleep(3)

        await page.screenshot(path=OUT_DIR + "/web_ui_output.png", full_page=False)
        print("OK: web_ui_output.png")

        await browser.close()


asyncio.run(main())
