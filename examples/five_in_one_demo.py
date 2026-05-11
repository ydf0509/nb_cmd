# -*- coding: utf-8 -*-
"""
nb_cmd 五重能力演示 —— 一次编写，五处全自动

    1. Python 直接调用（类自身完全照常使用）
    2. 自动生成 CLI 命令行
    3. 自动生成 REST API（含 Swagger 文档）
    4. 自动生成 Markdown 使用文档
    5. 自动生成 Web UI（含 WebSocket 实时控制台）

用法:
    # --- 能力 2: CLI ---
    python five_in_one_demo.py --help
    python five_in_one_demo.py ping 8.8.8.8
    python five_in_one_demo.py scan 192.168.1.0/24 --port 80 --verbose
    python five_in_one_demo.py calc 100 200

    # --- 能力 3+5: API + Web UI ---
    python five_in_one_demo.py --web

    # --- 能力 4: 自动生成 Markdown 文档 ---
    python five_in_one_demo.py gen-doc
"""
import sys
import os
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from nb_cmd import NbCmd, CmdGen, NbCmdMeta


class NetTool(NbCmd):
    """网络小工具 —— 一次编写，五处全自动"""

    class Meta(NbCmdMeta):
        version = '1.0.0'

    def ping(self, host: str, count: int = 4):
        """Ping 指定主机"""
        for i in range(1, count + 1):
            time.sleep(0.3)
            print(f'[{i}/{count}] PING {host} — 64 bytes, time={i * 12}ms')
        print(f'\n--- {host} ping 统计 ---')
        print(f'{count} 个包已发送, {count} 个包已接收, 0% 丢包')

    def scan(self, target: str, port: int = 80, verbose: bool = False):
        """扫描目标端口"""
        if verbose:
            print(f'[*] 正在扫描 {target}:{port} ...')
        time.sleep(0.5)
        print(f'[+] {target}:{port} — OPEN')
        if verbose:
            print(f'[*] 服务: HTTP')
            print(f'[*] 扫描完成')

    def calc(self, a: int, b: int):
        """计算两数之和"""
        result = a + b
        print(f'{a} + {b} = {result}')
        return result

    def gen_doc(self):
        """自动生成 Markdown 使用文档"""
        g = CmdGen(NetTool, script='five_in_one_demo.py', fmt='markdown')
        doc_path = os.path.join(os.path.dirname(__file__), 'five_in_one_demo_doc.md')
        g.doc(file=doc_path)
        print(f'文档已生成: {doc_path}')


if __name__ == '__main__':
    # --- 能力 1: Python 直接调用（类完全照常使用）---
    # tool = NetTool()
    # tool.ping('127.0.0.1', count=2)
    # tool.calc(100, 200)

    # --- 能力 2~5: CLI / API / Web / 文档 全自动 ---
    NetTool().run()
