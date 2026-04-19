# -*- coding: utf-8 -*-
"""测试 __init__ 直接赋值 self.nbctx 在 CLI 模式下是否工作"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from dataclasses import dataclass
from typing import Annotated
from nb_cmd import NbCmd


@dataclass
class Ctx:
    repo: str = None
    debug: bool = False


class SubCmd(NbCmd):
    nbctx: Ctx

    def show(self):
        """显示上下文"""
        print(f"repo={self.nbctx.repo}, debug={self.nbctx.debug}")


class App(NbCmd):
    """直接赋值 self.nbctx 测试"""
    nbctx: Ctx

    class Meta:
        enable_exec = False

    def __init__(self,
                 repo: Annotated[str, '仓库'] = None,
                 debug: Annotated[bool, '调试'] = False):
        self.repo = repo
        self.debug = debug
        self.nbctx = Ctx(repo=self.repo, debug=self.debug)

    sub_commands = {'sub': SubCmd}

    def status(self):
        """状态"""
        print(f"repo={self.nbctx.repo}, debug={self.nbctx.debug}")


if __name__ == '__main__':
    App().run()
