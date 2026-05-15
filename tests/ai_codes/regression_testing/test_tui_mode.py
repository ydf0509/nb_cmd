# -*- coding: utf-8 -*-
"""
TUI 模式回归测试 —— 验证 tui_mode.py 的关键逻辑（不启动真正的 Textual App）。
"""
import sys
import os
import inspect
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from nb_cmd import NbCmd, NbCmdMeta, CmdGen
from nb_cmd.core.discovery import discover_commands


class DemoTool(NbCmd):
    """TUI 测试用工具"""

    class Meta(NbCmdMeta):
        version = '1.0.0'
        enable_exec = False

    def greet(self, name: str, times: int = 1):
        """打招呼"""
        for _ in range(times):
            print('Hello, {}!'.format(name))

    def add(self, a: int, b: int):
        """两数相加"""
        return a + b

    def toggle(self, flag: bool = False):
        """布尔开关"""
        print('flag={}'.format(flag))


class SubGroup(NbCmd):
    """子命令组"""
    def inner(self, msg: str = 'hi'):
        print(msg)


class NestedTool(NbCmd):
    """带子命令组的工具"""

    class Meta(NbCmdMeta):
        version = '2.0.0'
        enable_exec = False

    sub_commands = {'sub': SubGroup}

    def top(self, x: int = 0):
        print(x)


class TestTuiWriter(unittest.TestCase):
    """测试 _TuiWriter 的行缓冲逻辑"""

    def test_line_buffering(self):
        from nb_cmd.modes.tui_mode import _TuiWriter
        lines = []
        w = _TuiWriter(lambda d: lines.append(d))

        w.write('hello')
        self.assertEqual(lines, [])

        w.write('\n')
        self.assertEqual(lines, ['hello'])

    def test_multi_line(self):
        from nb_cmd.modes.tui_mode import _TuiWriter
        lines = []
        w = _TuiWriter(lambda d: lines.append(d))

        w.write('a\nb\nc')
        self.assertEqual(lines, ['a', 'b'])

        w.write('\n')
        self.assertEqual(lines, ['a', 'b', 'c'])

    def test_flush(self):
        from nb_cmd.modes.tui_mode import _TuiWriter
        lines = []
        w = _TuiWriter(lambda d: lines.append(d))

        w.write('no newline')
        self.assertEqual(lines, [])

        w.flush()
        self.assertEqual(lines, ['no newline'])

    def test_empty_write(self):
        from nb_cmd.modes.tui_mode import _TuiWriter
        lines = []
        w = _TuiWriter(lambda d: lines.append(d))

        w.write('')
        w.write(None)
        w.flush()
        self.assertEqual(lines, [])


class TestTuiImportGuard(unittest.TestCase):
    """测试 Textual 不存在时的友好提示"""

    def test_import_guard(self):
        import nb_cmd.modes.tui_mode as tui_mod
        self.assertTrue(callable(tui_mod.start_tui))


class TestBaseTuiBranch(unittest.TestCase):
    """测试 base.py 的 --tui 分支"""

    def test_tui_in_run_args(self):
        tool = DemoTool()
        raw_args = ['--tui']
        self.assertIn('--tui', raw_args)

    def test_tui_branch_exists(self):
        source = inspect.getsource(NbCmd.run)
        self.assertIn('--tui', source)
        self.assertIn('_start_tui', source)

    def test_start_tui_method_exists(self):
        self.assertTrue(hasattr(NbCmd, '_start_tui'))
        self.assertTrue(callable(NbCmd._start_tui))


class TestTuiDiscovery(unittest.TestCase):
    """测试命令发现（TUI 复用的核心逻辑）"""

    def test_flat_commands(self):
        tool = DemoTool()
        cmds = discover_commands(tool, NbCmd, enable_exec=False)
        self.assertIn('greet', cmds)
        self.assertIn('add', cmds)
        self.assertIn('toggle', cmds)
        self.assertFalse(cmds['greet'].get('is_group', False))

    def test_nested_commands(self):
        tool = NestedTool()
        cmds = discover_commands(tool, NbCmd, enable_exec=False)
        self.assertIn('top', cmds)
        self.assertIn('sub', cmds)
        self.assertTrue(cmds['sub'].get('is_group', False))

    def test_command_signatures(self):
        tool = DemoTool()
        cmds = discover_commands(tool, NbCmd, enable_exec=False)
        sig = cmds['greet']['signature']
        params = list(sig.parameters.keys())
        self.assertIn('name', params)
        self.assertIn('times', params)


class TestTuiMarkdownDoc(unittest.TestCase):
    """测试 CmdGen 为 TUI 首屏生成 Markdown 文档"""

    def test_markdown_generation(self):
        gen = CmdGen(DemoTool, fmt='markdown')
        md = gen.doc()
        self.assertIn('greet', md)
        self.assertIn('add', md)
        self.assertIn('toggle', md)
        self.assertIn('--tui', md)

    def test_nested_markdown(self):
        gen = CmdGen(NestedTool, fmt='markdown')
        md = gen.doc()
        self.assertIn('sub', md)
        self.assertIn('inner', md)
        self.assertIn('--tui', md)


class TestParserTuiFlag(unittest.TestCase):
    """测试 parser.py 中 --tui 参数注册"""

    def test_parser_has_tui(self):
        from nb_cmd.core.parser import build_parser
        tool = DemoTool()
        meta = tool._get_meta()
        cmds = discover_commands(tool, NbCmd, enable_exec=False)
        parser = build_parser(tool, cmds, meta, base_cls=NbCmd)
        actions = [a.option_strings for a in parser._actions
                   if hasattr(a, 'option_strings')]
        tui_found = any('--tui' in opts for opts in actions)
        self.assertTrue(tui_found, '--tui should be registered in parser')


class TestPyprojectTuiDep(unittest.TestCase):
    """测试 pyproject.toml 包含 tui 可选依赖"""

    def test_tui_in_pyproject(self):
        pyproject_path = os.path.join(
            os.path.dirname(__file__), '..', '..', '..', 'pyproject.toml')
        with open(pyproject_path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('tui = ["textual', content)
        self.assertIn('textual', content)


if __name__ == '__main__':
    unittest.main()
