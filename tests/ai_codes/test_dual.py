# -*- coding: utf-8 -*-
"""测试双独立搜索面板"""
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={'width': 1280, 'height': 800})
        await page.goto('http://127.0.0.1:8093')
        await page.wait_for_selector('#formArea .form-section', timeout=10000)
        await asyncio.sleep(1)

        # 1) 两个搜索框都可见，内容折叠
        s1 = await page.is_visible('#savedSearch')
        s2 = await page.is_visible('#histSearch')
        b1 = await page.is_visible('#savedBody')
        b2 = await page.is_visible('#histBody')
        print("1. 收藏搜索框:", s1, "历史搜索框:", s2)
        print("2. 收藏内容:", b1, "历史内容:", b2, "(期望False)")

        # 2) 保存命令 + 执行命令
        inp = await page.query_selector('#cmdInput')
        save_btn = await page.query_selector('.save-cmd-btn')
        for cmd in ["deploy web-01", "status --verbose"]:
            await inp.fill(cmd)
            await save_btn.click()
            await asyncio.sleep(0.3)
        await inp.fill("show-users")
        exec_btn = await page.query_selector('.cmd-input-wrapper button:first-of-type')
        await exec_btn.click()
        await asyncio.sleep(2)
        print("3. 保存2个+执行1个完成")

        # 3) 点击收藏搜索框展开
        await page.click('#savedSearch')
        await asyncio.sleep(0.3)
        b1_2 = await page.is_visible('#savedBody')
        b2_2 = await page.is_visible('#histBody')
        t1 = await page.inner_text('#savedBody')
        print("4. 收藏展开:", b1_2, "历史仍折叠:", not b2_2)
        print("5. 收藏内容:", t1.replace('\n', ' | '))

        # 4) 点击历史搜索框展开
        await page.click('#histSearch')
        await asyncio.sleep(0.3)
        b2_3 = await page.is_visible('#histBody')
        t2 = await page.inner_text('#histBody')
        print("6. 历史展开:", b2_3)
        print("7. 历史内容:", t2.replace('\n', ' | '))

        # 5) 搜索过滤
        await page.fill('#savedSearch', 'dep')
        await asyncio.sleep(0.3)
        t3 = await page.inner_text('#savedBody')
        print("8. 收藏搜索dep:", t3.replace('\n', ' | '))

        # 6) 截图
        await page.screenshot(path='d:/codes/nb_cmd/docs/images/test_dual.png')

        # 7) 刷新验证
        await page.reload()
        await page.wait_for_selector('#formArea .form-section', timeout=10000)
        await asyncio.sleep(2)
        await page.click('#savedSearch')
        await asyncio.sleep(0.3)
        t4 = await page.inner_text('#savedBody')
        has = 'deploy' in t4
        print("9. 刷新后收藏包含deploy:", has)

        print("OK")
        await browser.close()

asyncio.run(main())
