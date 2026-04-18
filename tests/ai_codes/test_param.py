# -*- coding: utf-8 -*-
"""测试 Param 关键字写法"""
import sys
sys.path.insert(0, r'd:\codes\nb_cmd')

from typing import Annotated
from nb_cmd import NbCmd, Param
from nb_cmd.core.discovery import discover_commands


class TestTool(NbCmd):
    """测试 Param"""
    def method_a(self, name: Annotated[str, '用户名', 'n'], times: Annotated[int, '次数'] = 1):
        """位置参数写法"""
        pass

    def method_b(self, name: Annotated[str, Param(desc='用户名', alias='n')],
                 times: Annotated[int, Param(desc='次数')] = 1):
        """Param 关键字写法"""
        pass

    def method_c(self, host: str, port: int = 22):
        """纯类型注解"""
        pass


if __name__ == '__main__':
    tool = TestTool()
    cmds = discover_commands(tool, NbCmd)

    a = cmds['method_a']
    b = cmds['method_b']
    c = cmds['method_c']

    assert a['type_hints']['name'] is str
    assert a['arg_meta']['name'].desc == '用户名'
    assert a['arg_meta']['name'].aliases == ['-n']

    assert b['type_hints']['name'] is str
    assert b['arg_meta']['name'].desc == '用户名'
    assert b['arg_meta']['name'].aliases == ['-n']
    assert b['arg_meta']['times'].desc == '次数'

    assert c['type_hints']['host'] is str
    assert 'host' not in c['arg_meta']

    print('method_a meta:', a['arg_meta'])
    print('method_b meta:', b['arg_meta'])
    print('method_c meta:', c['arg_meta'])
    print('\nAll Param tests passed!')
