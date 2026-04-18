# -*- coding: utf-8 -*-
"""测试 Meta.enable_exec 控制 exec 命令是否暴露"""
import sys
sys.path.insert(0, r'd:\codes\nb_cmd')

from nb_cmd import NbCmd, NbCmdMeta
from nb_cmd.core.discovery import discover_commands


class ToolWithExec(NbCmd):
    """exec 默认启用"""
    def greet(self, name: str):
        print('Hello, {}'.format(name))


class ToolNoExec(NbCmd):
    """exec 禁用"""
    class Meta(NbCmdMeta):
        enable_exec = False

    def greet(self, name: str):
        print('Hello, {}'.format(name))


if __name__ == '__main__':
    t1 = ToolWithExec()
    cmds1 = discover_commands(t1, NbCmd, enable_exec=True)
    print('ToolWithExec commands:', list(cmds1.keys()))
    assert 'exec' in cmds1, 'exec should be present when enable_exec=True'
    assert 'greet' in cmds1

    t2 = ToolNoExec()
    meta2 = getattr(t2.__class__, 'Meta', type('Meta', (), {}))
    _enable = getattr(meta2, 'enable_exec', True)
    cmds2 = discover_commands(t2, NbCmd, enable_exec=_enable)
    print('ToolNoExec commands:', list(cmds2.keys()))
    assert 'exec' not in cmds2, 'exec should NOT be present when enable_exec=False'
    assert 'greet' in cmds2

    print('\nAll tests passed!')
