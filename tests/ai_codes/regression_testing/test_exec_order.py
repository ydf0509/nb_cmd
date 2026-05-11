# -*- coding: utf-8 -*-
"""
回归测试：exec 命令始终排在命令列表最前面
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from nb_cmd import NbCmd, NbCmdMeta
from nb_cmd.core.discovery import discover_commands


class SimpleTool(NbCmd):
    def zebra(self, name: str):
        """Z 开头"""
        pass

    def alpha(self, name: str):
        """A 开头"""
        pass

    def middle(self, count: int = 1):
        """M 开头"""
        pass


class SubGroup(NbCmd):
    def inner_a(self, x: int):
        pass

    def inner_b(self, y: str):
        pass


class ToolWithSub(NbCmd):
    def zzz(self, name: str):
        pass

    def aaa(self, name: str):
        pass

    sub_commands = {'sub': SubGroup}


class ExecDisabledTool(NbCmd):
    class Meta(NbCmdMeta):
        enable_exec = False

    def hello(self, name: str):
        pass


def test_exec_is_first():
    """exec 在顶层命令列表中排第一"""
    inst = SimpleTool()
    cmds = discover_commands(inst, NbCmd, include_builtins=True, enable_exec=True)
    names = list(cmds.keys())
    assert names[0] == 'exec', f'exec 应排第一，实际: {names}'
    assert names[1:] == ['alpha', 'middle', 'zebra'], f'其余按字母排序: {names}'
    print('test_exec_is_first passed!')


def test_exec_is_first_with_subcommands():
    """有子命令组时 exec 也排第一"""
    inst = ToolWithSub()
    cmds = discover_commands(inst, NbCmd, include_builtins=True, enable_exec=True)
    names = list(cmds.keys())
    assert names[0] == 'exec', f'exec 应排第一，实际: {names}'
    assert 'sub' in names, f'子命令组应存在: {names}'
    print('test_exec_is_first_with_subcommands passed!')


def test_exec_disabled_no_exec():
    """enable_exec=False 时不含 exec"""
    inst = ExecDisabledTool()
    cmds = discover_commands(inst, NbCmd, include_builtins=True, enable_exec=False)
    names = list(cmds.keys())
    assert 'exec' not in names, f'exec 不应存在: {names}'
    assert names == ['hello'], f'应只有 hello: {names}'
    print('test_exec_disabled_no_exec passed!')


def test_sub_group_no_exec():
    """子命令组 include_builtins=False 时不含 exec"""
    inst = SubGroup()
    cmds = discover_commands(inst, NbCmd, include_builtins=False)
    names = list(cmds.keys())
    assert 'exec' not in names, f'子命令组不应有 exec: {names}'
    print('test_sub_group_no_exec passed!')


def test_exec_first_in_full_help():
    """full help 文本中 exec 排在第一个命令"""
    from nb_cmd.core.parser import get_full_help_text
    inst = SimpleTool()
    text = get_full_help_text(inst, NbCmd)
    sep_idx = text.index('-' * 56)
    after_sep = text[sep_idx:]
    cmd_lines = [l for l in after_sep.split('\n') if '—' in l and not l.startswith(' ')]
    assert len(cmd_lines) > 0, 'help 中应有命令行'
    first_cmd_line = cmd_lines[0].strip()
    assert first_cmd_line.startswith('exec'), f'第一个命令应是 exec: {first_cmd_line}'
    print('test_exec_first_in_full_help passed!')


if __name__ == '__main__':
    test_exec_is_first()
    test_exec_is_first_with_subcommands()
    test_exec_disabled_no_exec()
    test_sub_group_no_exec()
    test_exec_first_in_full_help()
    print('\n=== 所有 exec 排序测试通过! ===')
