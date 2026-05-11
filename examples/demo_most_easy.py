# -*- coding: utf-8 -*-
"""
nb_cmd 最简 demo —— 不使用 Annotated，只用基本类型注解

用法:
    python demo_most_easy.py --help
    python demo_most_easy.py hello 世界
    python demo_most_easy.py add 3 5
    python demo_most_easy.py greet 张三 --times 3
    python demo_most_easy.py say-hi --loud
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from nb_cmd import NbCmd


class Demo(NbCmd):
    """最简示例 —— 连 Annotated 都不需要"""

    def hello(self, name: str):
        """向某人打招呼"""
        print(f'你好, {name}!')

    def add(self, a: int, b: int):
        """两数相加"""
        print(f'{a} + {b} = {a + b}')

    def greet(self, name: str, times: int = 1):
        """重复问候"""
        for _ in range(times):
            print(f'Hi, {name}!')

    def say_hi(self, loud: bool = False):
        """打个招呼"""
        msg = 'HI!!!' if loud else 'hi~'
        print(msg)


if __name__ == '__main__':
    Demo().run()
