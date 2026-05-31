# -*- coding: utf-8 -*-
"""
SkillGen 回归测试
"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from nb_cmd import SkillGen, NbCmd, NbCmdMeta
from typing import Annotated


# ========== 简单工具类 ==========

class SimpleTool(NbCmd):
    """简单工具 —— 测试 SkillGen 基本功能"""

    class Meta(NbCmdMeta):
        name = 'simple-tool'
        version = '1.0.0'
        description = 'A simple tool for testing SkillGen'

    def greet(self, name: str, times: int = 1):
        """打招呼"""
        for _ in range(times):
            print('Hello, {}!'.format(name))

    def calc(self, a: int, b: int = 0):
        """计算两数之和"""
        return a + b


# ========== 带子命令组的工具类 ==========

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


# ========== 测试用例 ==========

def test_simple_skill_gen():
    """测试简单工具的 Skill 生成（默认 base_dir=当前目录）"""
    with tempfile.TemporaryDirectory() as tmpdir:
        g = SkillGen(SimpleTool, base_dir=tmpdir)
        path = g.gen()

        # 输出路径应为 {base_dir}/{name}/
        expected_path = os.path.join(tmpdir, 'simple-tool')
        assert path == expected_path
        assert os.path.isdir(path)

        skill_md_path = os.path.join(path, 'SKILL.md')
        assert os.path.isfile(skill_md_path)

        with open(skill_md_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查 frontmatter
        assert '---' in content
        assert 'name: simple-tool' in content
        assert 'description: >-' in content

        # 检查 body
        assert '# simple-tool' in content or '# Simple' in content
        assert '## Overview' in content
        assert '## When to Use' in content
        assert '## Command Structure' in content
        assert '## Commands' in content
        assert '### `greet`' in content
        assert '### `calc`' in content
        assert '## Guidelines' in content

        # 检查参数表格
        assert '| Param | Type | Default | Description |' in content

        # CLI 示例默认开启
        assert '```bash' in content
        # Python 调用示例默认关闭（Implementation Note 中可能有解释性代码块，不属于调用示例）
        assert '**Python:**' not in content

        print('test_simple_skill_gen PASSED')


def test_nested_skill_gen():
    """测试带子命令组的 Skill 生成"""
    with tempfile.TemporaryDirectory() as tmpdir:
        g = SkillGen(NestedTool, base_dir=tmpdir)
        path = g.gen()

        skill_md_path = os.path.join(path, 'SKILL.md')
        with open(skill_md_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查子命令组
        assert '### `sub` *(subcommand group)*' in content
        assert '### `sub inner`' in content

        print('test_nested_skill_gen PASSED')


def test_name_validation():
    """测试 name 校验"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # 有效的 name
        g = SkillGen(SimpleTool, base_dir=tmpdir, name='my-app')
        assert g._name == 'my-app'

        # 无效的 name —— 大写
        try:
            SkillGen(SimpleTool, base_dir=tmpdir, name='MyApp')
            assert False, 'Should raise ValueError'
        except ValueError as e:
            assert 'lowercase' in str(e)

        # 无效的 name —— 连续连字符
        try:
            SkillGen(SimpleTool, base_dir=tmpdir, name='my--app')
            assert False, 'Should raise ValueError'
        except ValueError as e:
            assert 'consecutive hyphens' in str(e)

        print('test_name_validation PASSED')


def test_description_auto_generation():
    """测试 description 自动生成"""
    g = SkillGen(SimpleTool, base_dir='/tmp')
    # description 应该从 Meta.description 获取
    assert 'A simple tool for testing SkillGen' in g._description

    print('test_description_auto_generation PASSED')


def test_custom_metadata():
    """测试自定义元数据"""
    with tempfile.TemporaryDirectory() as tmpdir:
        g = SkillGen(
            SimpleTool,
            base_dir=tmpdir,
            license='MIT',
            compatibility='Requires Python 3.8+',
            metadata={'author': 'test-team', 'version': '1.0'},
            disable_model_invocation=True,
        )
        path = g.gen()

        skill_md_path = os.path.join(path, 'SKILL.md')
        with open(skill_md_path, 'r', encoding='utf-8') as f:
            content = f.read()

        assert 'license: MIT' in content
        assert 'compatibility: Requires Python 3.8+' in content
        assert 'author: "test-team"' in content
        assert 'version: "1.0"' in content
        assert 'disable-model-invocation: true' in content

        print('test_custom_metadata PASSED')


def test_user_priority_prompt():
    """测试 user_highest_priority_skill_prompt"""
    with tempfile.TemporaryDirectory() as tmpdir:
        prompt = '线上服务器请使用 /usr/bin/python3，本地开发请使用 python。运行前请设置 PYTHONPATH=/opt/app。'
        g = SkillGen(
            SimpleTool,
            base_dir=tmpdir,
            user_highest_priority_skill_prompt=prompt,
        )
        path = g.gen()

        skill_md_path = os.path.join(path, 'SKILL.md')
        with open(skill_md_path, 'r', encoding='utf-8') as f:
            content = f.read()

        assert '## Important' in content
        assert prompt in content
        # Important 应在 When to Use 之前
        important_pos = content.index('## Important')
        when_to_use_pos = content.index('## When to Use')
        assert important_pos < when_to_use_pos

        print('test_user_priority_prompt PASSED')


def test_include_python_examples():
    """测试开启 Python 示例"""
    with tempfile.TemporaryDirectory() as tmpdir:
        g = SkillGen(SimpleTool, base_dir=tmpdir, include_python_examples=True)
        path = g.gen()

        skill_md_path = os.path.join(path, 'SKILL.md')
        with open(skill_md_path, 'r', encoding='utf-8') as f:
            content = f.read()

        assert '```python' in content
        print('test_include_python_examples PASSED')


def test_gen_skill_md_only():
    """测试仅生成 SKILL.md 内容字符串"""
    g = SkillGen(SimpleTool, base_dir='/tmp')
    content = g.gen_skill_md()

    assert content.startswith('---')
    assert 'name: simple-tool' in content
    assert '## Overview' in content

    print('test_gen_skill_md_only PASSED')


if __name__ == '__main__':
    test_simple_skill_gen()
    test_nested_skill_gen()
    test_name_validation()
    test_description_auto_generation()
    test_custom_metadata()
    test_user_priority_prompt()
    test_include_python_examples()
    test_gen_skill_md_only()
    print('\nAll tests passed!')
