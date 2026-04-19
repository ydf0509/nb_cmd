# -*- coding: utf-8 -*-
"""
allow_method_list 白名单测试。

验证目标：
1. 未设置白名单时，CLI/API/Web 暴露全部命令
2. 设置白名单后，仅暴露指定命令（支持多层路径）
3. Python 直接调用类方法不受影响
"""
import io
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from nb_cmd import NbCmd, NbCmdMeta
from nb_cmd.core.discovery import discover_commands
from nb_cmd.modes.cli_mode import run_cli
from nb_cmd.modes.api_mode import _register_routes


class AdminTool(NbCmd):
    """管理命令组"""

    def restart_server(self):
        """重启服务"""
        return 'restart-ok'

    def delete_user(self):
        """删除用户"""
        return 'delete-ok'


class AllowAllTool(NbCmd):
    """未设置白名单，默认暴露全部命令"""
    sub_commands = {'admin': AdminTool}

    def status(self):
        """状态"""
        return 'status-ok'

    def secret(self):
        """敏感命令"""
        return 'secret-ok'


class AllowLimitedTool(NbCmd):
    """设置白名单，仅暴露 status + admin/restart_server"""

    class Meta(NbCmdMeta):
        # 混合三种路径写法，验证 normalize 兼容
        allow_method_list = ['status', 'admin.restart_server', 'admin delete-user-never-match']

    sub_commands = {'admin': AdminTool}

    def status(self):
        """状态"""
        return 'status-ok'

    def secret(self):
        """敏感命令"""
        return 'secret-ok'


def test_allow_method_list_default_expose_all():
    """未指定 allow_method_list -> 暴露全部命令"""
    tool = AllowAllTool()
    root_cmds = discover_commands(tool, NbCmd, enable_exec=False)
    assert 'status' in root_cmds
    assert 'secret' in root_cmds
    assert 'admin' in root_cmds

    admin_inst = AdminTool()
    sub_cmds = discover_commands(admin_inst, NbCmd, include_builtins=False,
                                 enable_exec=False, command_prefix='admin')
    assert 'restart_server' in sub_cmds
    assert 'delete_user' in sub_cmds


def test_allow_method_list_filter_discovery():
    """白名单过滤 discover_commands（含多层路径）"""
    tool = AllowLimitedTool()
    allow_list = tool.Meta.allow_method_list

    root_cmds = discover_commands(tool, NbCmd, enable_exec=False,
                                  allow_method_list=allow_list)
    assert 'status' in root_cmds
    assert 'secret' not in root_cmds
    assert 'admin' in root_cmds  # 因为 admin/restart_server 被允许，组需保留

    admin_inst = AdminTool()
    sub_cmds = discover_commands(admin_inst, NbCmd, include_builtins=False,
                                 enable_exec=False, allow_method_list=allow_list,
                                 command_prefix='admin')
    assert 'restart_server' in sub_cmds
    assert 'delete_user' not in sub_cmds


def test_allow_method_list_cli_filtered_but_python_direct_call_still_ok():
    """
    CLI 被白名单限制，但 Python 直接调用仍可访问全部方法。
    """
    tool = AllowLimitedTool()

    # 1) CLI 允许的命令可以执行
    old_stdout = sys.stdout
    sys.stdout = captured = io.StringIO()
    try:
        run_cli(tool, NbCmd, ['status'])
    finally:
        sys.stdout = old_stdout
    assert 'status-ok' in captured.getvalue()

    # 2) CLI 不允许的命令会被 argparse 拦截（SystemExit）
    try:
        run_cli(tool, NbCmd, ['secret'])
        assert False, '应抛出 SystemExit（secret 未暴露到 CLI）'
    except SystemExit as e:
        assert e.code != 0

    # 3) Python 直接调用不受影响
    assert tool.secret() == 'secret-ok'


class _DummyApp(object):
    """最小 FastAPI 替身，用于收集注册路由路径"""

    def __init__(self):
        self.paths = []

    def post(self, path, summary=None):
        self.paths.append(path)

        def _decorator(func):
            return func

        return _decorator


def test_allow_method_list_api_routes_filtered():
    """API 路由注册应遵守白名单"""
    tool = AllowLimitedTool()
    allow_list = tool.Meta.allow_method_list
    app = _DummyApp()

    commands = discover_commands(tool, NbCmd, enable_exec=False,
                                 allow_method_list=allow_list)
    _register_routes(app, tool, commands, base_cls=NbCmd,
                     allow_method_list=allow_list, command_prefix='')

    assert '/status' in app.paths
    assert '/secret' not in app.paths
    assert '/admin/restart-server' in app.paths
    assert '/admin/delete-user' not in app.paths

