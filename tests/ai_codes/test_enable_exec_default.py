# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, r'd:\codes\nb_cmd')

from nb_cmd import NbCmd


class NormalTool(NbCmd):
    """普通工具（exec 默认启用）"""
    def greet(self, name: str):
        """问好"""
        print('Hello, {}'.format(name))


if __name__ == '__main__':
    NormalTool().run()
