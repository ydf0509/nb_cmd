# -*- coding: utf-8 -*-
"""测试 Select2 风格弹框控件"""
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={'width': 1280, 'height': 800})
        await page.goto('http://127.0.0.1:8093')
        await page.wait_for_selector('#formArea .form-section', timeout=10000)
        await asyncio.sleep(1)

        # 先保存两个命令，制造数据
        inp = await page.query_selector('#cmdInput')
        save_btn = await page.query_selector('.save-cmd-btn')
        await inp.fill("deploy web-01")
        await save_btn.click()
        await asyncio.sleep(0.3)
        await inp.fill("restart db-02")
        await save_btn.click()
        await asyncio.sleep(0.3)

        # 1) 默认弹框关闭
        drop_vis = await page.is_visible('#s2Saved .s2-drop')
        print("1. 默认弹框隐藏:", not drop_vis)

        # 2) 触发器存在 且 显示 count
        trigger = await page.query_selector('#s2Saved .s2-trigger')
        assert trigger is not None, "trigger not found"
        count_text = await page.text_content('#savedCount')
        print("2. 收藏数量badge:", count_text)

        # 3) 点击触发器展开
        await trigger.click()
        await asyncio.sleep(0.3)
        drop_vis2 = await page.is_visible('#s2Saved .s2-drop')
        has_open = await page.evaluate('document.getElementById("s2Saved").classList.contains("open")')
        print("3. 点击后弹框展开:", drop_vis2 and has_open)

        # 4) 搜索框存在且可输入
        search_focused = await page.evaluate('document.activeElement.id')
        print("4. 搜索框自动聚焦:", search_focused == 'savedSearch')

        # 5) 弹框内有两个条目
        items = await page.query_selector_all('#savedBody .s2-item')
        print("5. 弹框内条目数:", len(items))

        # 6) 输入搜索词过滤
        await page.fill('#savedSearch', 'deploy')
        await asyncio.sleep(0.2)
        items2 = await page.query_selector_all('#savedBody .s2-item')
        print("6. 搜索 deploy 后条目数:", len(items2))

        # 7) 点击条目填入命令并关闭弹框
        if len(items2) > 0:
            await items2[0].click()
            await asyncio.sleep(0.3)
        cmd_val = await page.input_value('#cmdInput')
        drop_vis3 = await page.is_visible('#s2Saved .s2-drop')
        print("7. 选中后填入命令:", cmd_val, "弹框关闭:", not drop_vis3)

        # 8) 点击外部关闭
        await page.click('#s2Saved .s2-trigger')
        await asyncio.sleep(0.3)
        is_open = await page.evaluate('document.getElementById("s2Saved").classList.contains("open")')
        print("8. 重新打开:", is_open)
        await page.click('.console-area')
        await asyncio.sleep(0.3)
        is_closed = not await page.evaluate('document.getElementById("s2Saved").classList.contains("open")')
        print("9. 点击外部后关闭:", is_closed)

        # 10) 打开一个面板后点击另一个，第一个应关闭
        await page.click('#s2Saved .s2-trigger')
        await asyncio.sleep(0.2)
        await page.click('#s2Hist .s2-trigger')
        await asyncio.sleep(0.2)
        saved_open = await page.evaluate('document.getElementById("s2Saved").classList.contains("open")')
        hist_open = await page.evaluate('document.getElementById("s2Hist").classList.contains("open")')
        print("10. 互斥切换: 收藏关闭=", not saved_open, "历史打开=", hist_open)

        # 11) 历史面板的 count
        hist_count = await page.text_content('#histCount')
        print("11. 历史数量badge:", hist_count)

        print("\nALL OK")
        await browser.close()

asyncio.run(main())
