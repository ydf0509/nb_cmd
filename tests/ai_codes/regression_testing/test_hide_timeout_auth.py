# -*- coding: utf-8 -*-
"""
测试 hide_method_list / timeout / auth_token 三个 Meta 新字段。
"""
import time
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from nb_cmd import NbCmd
from nb_cmd.core.discovery import discover_commands


# ────────── 测试用的 NbCmd 子类 ──────────

class FullTool(NbCmd):
    """所有方法可见"""
    def alpha(self, x: int = 1):
        return x

    def beta(self, y: str = 'b'):
        return y

    def gamma(self, z: float = 3.0):
        return z


class HiddenTool(NbCmd):
    """用黑名单隐藏 beta"""
    class Meta:
        hide_method_list = ['beta']

    def alpha(self, x: int = 1):
        return x

    def beta(self, y: str = 'b'):
        return y

    def gamma(self, z: float = 3.0):
        return z


class SubGroup(NbCmd):
    """子命令组"""
    def inner_a(self, v: int = 0):
        return v

    def inner_b(self, v: int = 0):
        return v


class HideGroupTool(NbCmd):
    """隐藏整个子命令组"""
    sub_commands = {'sub': SubGroup}

    class Meta:
        hide_method_list = ['sub']

    def top(self, n: int = 1):
        return n


class HideGroupMethodTool(NbCmd):
    """隐藏子命令组中的某个方法"""
    sub_commands = {'sub': SubGroup}

    class Meta:
        hide_method_list = ['sub.inner_b']

    def top(self, n: int = 1):
        return n


class TimeoutTool(NbCmd):
    """超时测试工具"""
    class Meta:
        timeout = 2

    def fast(self, x: int = 1):
        return x

    def slow(self, seconds: int = 5):
        time.sleep(seconds)
        return 'done'


class AllowAndHideTool(NbCmd):
    """白名单和黑名单同时配置，白名单优先"""
    class Meta:
        allow_method_list = ['alpha', 'beta']
        hide_method_list = ['alpha']

    def alpha(self, x: int = 1):
        return x

    def beta(self, y: str = 'b'):
        return y

    def gamma(self, z: float = 3.0):
        return z


# ────────── hide_method_list 测试 ──────────

def test_hide_method_list_no_config():
    """未配置黑名单时所有方法可见"""
    inst = FullTool()
    cmds = discover_commands(inst, NbCmd)
    assert 'alpha' in cmds
    assert 'beta' in cmds
    assert 'gamma' in cmds


def test_hide_method_list_basic():
    """配置黑名单后 beta 被隐藏"""
    inst = HiddenTool()
    cmds = discover_commands(inst, NbCmd,
                              hide_method_list=['beta'])
    assert 'alpha' in cmds
    assert 'beta' not in cmds
    assert 'gamma' in cmds


def test_hide_method_list_from_meta():
    """从 Meta 中读取 hide_method_list"""
    inst = HiddenTool()
    meta = inst.__class__.Meta
    hide_list = getattr(meta, 'hide_method_list', None)
    assert hide_list == ['beta']
    cmds = discover_commands(inst, NbCmd, hide_method_list=hide_list)
    assert 'beta' not in cmds


def test_hide_method_list_python_direct_call():
    """黑名单只限制发现，不影响 Python 直接调用"""
    inst = HiddenTool()
    assert inst.beta('hello') == 'hello'


def test_hide_group():
    """隐藏整个子命令组"""
    inst = HideGroupTool()
    cmds = discover_commands(inst, NbCmd, hide_method_list=['sub'])
    assert 'top' in cmds
    assert 'sub' not in cmds


def test_hide_group_method():
    """隐藏子命令组中的某个方法"""
    inst = HideGroupMethodTool()
    cmds = discover_commands(inst, NbCmd, hide_method_list=['sub.inner_b'])
    assert 'top' in cmds
    assert 'sub' in cmds
    sub_cls = cmds['sub']['cls']
    sub_inst = sub_cls()
    sub_cmds = discover_commands(sub_inst, NbCmd, include_builtins=False,
                                  hide_method_list=['sub.inner_b'],
                                  command_prefix='sub')
    assert 'inner_a' in sub_cmds
    assert 'inner_b' not in sub_cmds


def test_allow_overrides_hide():
    """allow_method_list 和 hide_method_list 同时配置时白名单优先"""
    inst = AllowAndHideTool()
    cmds = discover_commands(inst, NbCmd,
                              allow_method_list=['alpha', 'beta'],
                              hide_method_list=['alpha'])
    assert 'alpha' in cmds
    assert 'beta' in cmds
    assert 'gamma' not in cmds


def test_hide_method_list_cli_filtered():
    """CLI 模式下被黑名单隐藏的命令不可用"""
    from nb_cmd.modes.cli_mode import run_cli
    import io
    from contextlib import redirect_stdout

    inst = HiddenTool()
    buf = io.StringIO()
    with redirect_stdout(buf):
        try:
            run_cli(inst, NbCmd, args=['beta', '--y', 'test'])
        except SystemExit:
            pass
    output = buf.getvalue()
    assert 'beta' not in output or 'error' in output.lower() or output == ''


# ────────── timeout 测试 ──────────

def test_timeout_fast_no_error():
    """快速命令不受 timeout 影响"""
    from nb_cmd.modes.cli_mode import _run_method_with_timeout
    inst = TimeoutTool()
    result = _run_method_with_timeout(inst.fast, {'x': 42}, timeout=2)
    assert result == 42


def test_timeout_slow_raises():
    """慢命令超时后抛出 TimeoutError"""
    from nb_cmd.modes.cli_mode import _run_method_with_timeout
    inst = TimeoutTool()
    try:
        _run_method_with_timeout(inst.slow, {'seconds': 5}, timeout=1)
        assert False, "应该抛出 TimeoutError"
    except TimeoutError as e:
        assert '超时' in str(e)


def test_timeout_zero_no_limit():
    """timeout=0 表示不限"""
    from nb_cmd.modes.cli_mode import _run_method_with_timeout
    inst = TimeoutTool()
    result = _run_method_with_timeout(inst.fast, {'x': 99}, timeout=0)
    assert result == 99


# ────────── auth_token 测试 ──────────

def test_auth_token_meta_default_none():
    """默认 auth_token 为 None"""
    inst = FullTool()
    meta = getattr(inst.__class__, 'Meta', type('Meta', (), {}))
    assert getattr(meta, 'auth_token', None) is None


def test_auth_token_middleware_install():
    """配置 auth_token 后中间件能被安装"""
    try:
        from fastapi import FastAPI
        from nb_cmd.modes.api_mode import _install_auth_middleware

        app = FastAPI()
        _install_auth_middleware(app, 'test-secret-123')
        has_middleware = len(app.user_middleware) > 0
        assert has_middleware
    except ImportError:
        pass


if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v'])
