# -*- coding: utf-8 -*-
"""测试 Annotated 替代 Arg 的核心功能"""
import sys
sys.path.insert(0, r'd:\codes\nb_cmd')

from typing import Annotated
from nb_cmd import NbCmd
from nb_cmd.core.discovery import discover_commands


class TestTool(NbCmd):
    """测试工具"""
    def greet(self, name: Annotated[str, '用户名', 'n'], times: Annotated[int, '次数'] = 1):
        """问好"""
        for _ in range(times):
            print('Hello, {}'.format(name))

    def deploy(self, host: str, port: int = 22):
        """部署（纯类型注解）"""
        print('Deploy to {}:{}'.format(host, port))


if __name__ == '__main__':
    tool = TestTool()
    cmds = discover_commands(tool, NbCmd)

    print('Commands:', list(cmds.keys()))
    assert 'greet' in cmds
    assert 'deploy' in cmds

    greet_info = cmds['greet']
    print('greet type_hints:', greet_info['type_hints'])
    print('greet arg_meta:', greet_info['arg_meta'])

    assert greet_info['type_hints']['name'] is str, 'name should be str, got {}'.format(greet_info['type_hints']['name'])
    assert greet_info['type_hints']['times'] is int
    assert 'name' in greet_info['arg_meta'], 'name should have arg_meta'
    assert greet_info['arg_meta']['name'].desc == '用户名'
    assert greet_info['arg_meta']['name'].aliases == ['-n']

    deploy_info = cmds['deploy']
    assert deploy_info['type_hints']['host'] is str
    assert 'host' not in deploy_info['arg_meta'], 'deploy.host should have no arg_meta'

    print('\nAll Annotated tests passed!')
