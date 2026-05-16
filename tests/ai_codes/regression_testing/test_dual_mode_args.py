# -*- coding: utf-8 -*-
"""
回归测试：必填参数"双模式"（位置 + --flag 并存）

测试覆盖:
1. 单参数命令 - 位置传参
2. 单参数命令 - --flag 传参
3. 单参数命令 - -短别名 传参
4. 多参数命令 - 全位置
5. 多参数命令 - 全 --flag
6. 多参数命令 - 混合（位置 + --flag）
7. 多参数命令 - --flag 优先于位置（重分配）
8. 缺少必填参数报错
9. exec 命令三种写法
10. 有默认值的参数仍正常工作
"""
import sys
import os
import unittest
import io
from contextlib import redirect_stdout, redirect_stderr

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from nb_cmd import NbCmd
from nb_cmd.core.discovery import discover_commands
from nb_cmd.core.parser import build_parser, reassign_positionals


class DualModeApp(NbCmd):
    """双模式测试应用"""

    class Meta:
        enable_exec = True

    _last_call = None

    def single(self, name: str):
        """单参数命令"""
        DualModeApp._last_call = {'name': name}

    def multi(self, x: int, name: str):
        """多参数命令"""
        DualModeApp._last_call = {'x': x, 'name': name}

    def with_default(self, x: int, y: int = 10):
        """有默认值的命令"""
        DualModeApp._last_call = {'x': x, 'y': y}


def _parse(app, args_str):
    """辅助函数：解析命令行参数"""
    args = args_str.split()
    commands = discover_commands(app, NbCmd, enable_exec=True)
    parser = build_parser(app, commands, app.Meta, base_cls=NbCmd)
    parsed = parser.parse_args(args)
    reassign_positionals(parsed)
    return parsed


class TestDualModeSingle(unittest.TestCase):
    """单参数命令的双模式测试"""

    def setUp(self):
        self.app = DualModeApp()

    def test_positional(self):
        """fa hello → name='hello'"""
        parsed = _parse(self.app, 'single hello')
        self.assertEqual(parsed.name, 'hello')

    def test_long_flag(self):
        """fa --name hello → name='hello'"""
        parsed = _parse(self.app, 'single --name hello')
        self.assertEqual(parsed.name, 'hello')

    def test_missing_required(self):
        """fa（无参数）→ 报错"""
        with self.assertRaises(SystemExit):
            _parse(self.app, 'single')


class TestDualModeMulti(unittest.TestCase):
    """多参数命令的双模式测试"""

    def setUp(self):
        self.app = DualModeApp()

    def test_all_positional(self):
        """multi 5 hello → x=5, name='hello'"""
        parsed = _parse(self.app, 'multi 5 hello')
        self.assertEqual(parsed.x, 5)
        self.assertEqual(parsed.name, 'hello')

    def test_all_flags(self):
        """multi --x 5 --name hello"""
        parsed = _parse(self.app, 'multi --x 5 --name hello')
        self.assertEqual(parsed.x, 5)
        self.assertEqual(parsed.name, 'hello')

    def test_flag_before_positional(self):
        """multi --x 5 hello → x=5, name='hello' (hello 重分配给 name)"""
        parsed = _parse(self.app, 'multi --x 5 hello')
        self.assertEqual(parsed.x, 5)
        self.assertEqual(parsed.name, 'hello')

    def test_positional_then_flag(self):
        """multi 5 --name hello → x=5, name='hello'"""
        parsed = _parse(self.app, 'multi 5 --name hello')
        self.assertEqual(parsed.x, 5)
        self.assertEqual(parsed.name, 'hello')

    def test_flag_name_before_positional_x(self):
        """multi --name hello 5 → x=5, name='hello'"""
        parsed = _parse(self.app, 'multi --name hello 5')
        self.assertEqual(parsed.x, 5)
        self.assertEqual(parsed.name, 'hello')

    def test_missing_one_required(self):
        """multi 5 → name 缺失，报错"""
        with self.assertRaises(SystemExit):
            _parse(self.app, 'multi 5')


class TestDualModeWithDefault(unittest.TestCase):
    """有默认值参数的混合测试"""

    def setUp(self):
        self.app = DualModeApp()

    def test_positional_only(self):
        """with-default 5 → x=5, y=10"""
        parsed = _parse(self.app, 'with-default 5')
        self.assertEqual(parsed.x, 5)
        self.assertEqual(parsed.y, 10)

    def test_positional_with_flag(self):
        """with-default 5 --y 3 → x=5, y=3"""
        parsed = _parse(self.app, 'with-default 5 --y 3')
        self.assertEqual(parsed.x, 5)
        self.assertEqual(parsed.y, 3)

    def test_flag_x_with_flag_y(self):
        """with-default --x 5 --y 3 → x=5, y=3"""
        parsed = _parse(self.app, 'with-default --x 5 --y 3')
        self.assertEqual(parsed.x, 5)
        self.assertEqual(parsed.y, 3)

    def test_flag_x_only(self):
        """with-default --x 5 → x=5, y=10"""
        parsed = _parse(self.app, 'with-default --x 5')
        self.assertEqual(parsed.x, 5)
        self.assertEqual(parsed.y, 10)


class TestExecDualMode(unittest.TestCase):
    """exec 命令三种写法测试"""

    def setUp(self):
        self.app = DualModeApp()

    def test_exec_positional(self):
        """exec 'echo hello' → cmd='echo hello'（位置传参）"""
        args = ['exec', 'echo hello']
        commands = discover_commands(self.app, NbCmd, enable_exec=True)
        parser = build_parser(self.app, commands, self.app.Meta, base_cls=NbCmd)
        parsed = parser.parse_args(args)
        reassign_positionals(parsed)
        self.assertEqual(parsed.cmd, 'echo hello')

    def test_exec_long_flag(self):
        """exec --cmd 'echo hello' → cmd='echo hello'"""
        args = ['exec', '--cmd', 'echo hello']
        commands = discover_commands(self.app, NbCmd, enable_exec=True)
        parser = build_parser(self.app, commands, self.app.Meta, base_cls=NbCmd)
        parsed = parser.parse_args(args)
        reassign_positionals(parsed)
        self.assertEqual(parsed.cmd, 'echo hello')

    def test_exec_short_flag(self):
        """exec -c 'echo hello' → cmd='echo hello'"""
        args = ['exec', '-c', 'echo hello']
        commands = discover_commands(self.app, NbCmd, enable_exec=True)
        parser = build_parser(self.app, commands, self.app.Meta, base_cls=NbCmd)
        parsed = parser.parse_args(args)
        reassign_positionals(parsed)
        self.assertEqual(parsed.cmd, 'echo hello')


class TestReassignPositionals(unittest.TestCase):
    """后处理重分配逻辑的专项测试"""

    def test_no_pos_map(self):
        """无位置参数映射时不做任何事"""
        import argparse
        ns = argparse.Namespace(x=5)
        reassign_positionals(ns)
        self.assertEqual(ns.x, 5)

    def test_flag_priority(self):
        """--flag 的值优先于位置值"""
        import argparse
        ns = argparse.Namespace(
            _nb_pos_map=[('_nb_pos_0', 'x', int)],
            _nb_pos_0=99,
            x=42,
        )
        reassign_positionals(ns)
        self.assertEqual(ns.x, 42)

    def test_cleanup(self):
        """后处理完成后 _nb_pos_X 属性被清理"""
        import argparse
        ns = argparse.Namespace(
            _nb_pos_map=[('_nb_pos_0', 'x', int)],
            _nb_pos_0='5',
            x=None,
        )
        reassign_positionals(ns)
        self.assertEqual(ns.x, 5)
        self.assertFalse(hasattr(ns, '_nb_pos_0'))


if __name__ == '__main__':
    unittest.main(verbosity=2)
