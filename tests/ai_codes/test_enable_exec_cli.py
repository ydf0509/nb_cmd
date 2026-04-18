# -*- coding: utf-8 -*-
"""测试 enable_exec=False 时 CLI --help 不显示 exec"""
import sys
sys.path.insert(0, r'd:\codes\nb_cmd')

from nb_cmd import NbCmd, NbCmdMeta


class SafeTool(NbCmd):
    """安全工具（禁用 exec）"""
    class Meta(NbCmdMeta):
        enable_exec = False

    def greet(self, name: str):
        """问好"""
        print('Hello, {}'.format(name))

    def deploy(self, host: str):
        """部署"""
        print('Deploy to {}'.format(host))


if __name__ == '__main__':
    SafeTool().run()
