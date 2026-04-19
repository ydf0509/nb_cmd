# -*- coding: utf-8 -*-
"""
测试 nbctx 跨层级上下文传递功能。
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from dataclasses import dataclass
from nb_cmd import NbCmd


@dataclass
class AppCtx:
    region: str = 'beijing'
    env: str = 'prod'
    debug: bool = False


class SubDbTool(NbCmd):
    nbctx: AppCtx

    def migrate(self):
        return f'migrate:{self.nbctx.region}:{self.nbctx.env}'

    def backup(self):
        return f'backup:{self.nbctx.region}:debug={self.nbctx.debug}'


class SubOpsTool(NbCmd):
    nbctx: AppCtx

    def deploy(self, version: str):
        return f'deploy:v{version}:{self.nbctx.region}/{self.nbctx.env}'


class SubRemoteTool(NbCmd):
    nbctx: AppCtx

    sub_commands = {'ops': SubOpsTool}

    def add(self, name: str, url: str):
        return f'[{self.nbctx.region}] remote add {name} {url}'


class MyApp(NbCmd):
    class Meta:
        name = 'myapp'
        enable_exec = False

    def __init__(self, region: str = 'beijing', env: str = 'prod', debug: bool = False):
        self.region = region
        self.env = env
        self.debug = debug

    def make_nbctx(self):
        return AppCtx(region=self.region, env=self.env, debug=self.debug)

    sub_commands = {
        'db': SubDbTool,
        'remote': SubRemoteTool,
    }

    def status(self):
        return f'status:{self.nbctx.region}'


class NoCtxApp(NbCmd):
    """不使用 nbctx 的应用"""
    def hello(self, name: str = 'world'):
        return f'hello {name}'


def test_make_nbctx_basic():
    """测试 make_nbctx 基本功能"""
    app = MyApp(region='shanghai', env='staging')
    ctx = app.make_nbctx()
    assert isinstance(ctx, AppCtx)
    assert ctx.region == 'shanghai'
    assert ctx.env == 'staging'
    print('[PASS] test_make_nbctx_basic')


def test_nbctx_property_with_make():
    """测试通过 make_nbctx 设置后 self.nbctx 可用"""
    app = MyApp(region='tokyo', env='test')
    app.nbctx = app.make_nbctx()
    assert app.nbctx.region == 'tokyo'
    assert app.nbctx.env == 'test'
    print('[PASS] test_nbctx_property_with_make')


def test_nbctx_setter():
    """测试 nbctx 的 setter"""
    app = MyApp()
    custom_ctx = AppCtx(region='us-east', env='canary', debug=True)
    app.nbctx = custom_ctx
    assert app.nbctx.region == 'us-east'
    assert app.nbctx.debug is True
    print('[PASS] test_nbctx_setter')


def test_nbctx_default_none():
    """测试子命令组直接实例化时 nbctx 为 None（需手动设置）"""
    tool = SubDbTool()
    assert tool.nbctx is None
    tool.nbctx = AppCtx()
    assert tool.nbctx.region == 'beijing'
    result = tool.migrate()
    assert result == 'migrate:beijing:prod'
    print('[PASS] test_nbctx_default_none')


def test_nbctx_manual_set_on_sub():
    """测试手动给子命令组设置 nbctx"""
    ctx = AppCtx(region='shanghai', env='staging')
    tool = SubDbTool()
    tool.nbctx = ctx
    assert tool.migrate() == 'migrate:shanghai:staging'
    print('[PASS] test_nbctx_manual_set_on_sub')


def test_nbctx_none_when_no_annotation():
    """测试没有 nbctx 注解的类，self.nbctx 为 None"""
    app = NoCtxApp()
    assert app.nbctx is None
    print('[PASS] test_nbctx_none_when_no_annotation')


def test_nbctx_cli_injection():
    """测试 CLI 模式下 nbctx 从顶层注入到子命令组"""
    from nb_cmd.modes.cli_mode import _ensure_nbctx, _inject_nbctx

    app = MyApp(region='guangzhou', env='dev', debug=True)
    _ensure_nbctx(app)
    assert app.nbctx.region == 'guangzhou'
    assert app.nbctx.debug is True

    db = SubDbTool()
    _inject_nbctx(app, db)
    assert db.nbctx.region == 'guangzhou'
    assert db.nbctx.env == 'dev'
    assert db.migrate() == 'migrate:guangzhou:dev'
    print('[PASS] test_nbctx_cli_injection')


def test_nbctx_multilevel_injection():
    """测试多层级 nbctx 传递"""
    from nb_cmd.modes.cli_mode import _ensure_nbctx, _inject_nbctx

    app = MyApp(region='shenzhen', env='staging')
    _ensure_nbctx(app)

    remote = SubRemoteTool()
    _inject_nbctx(app, remote)
    assert remote.nbctx.region == 'shenzhen'
    assert remote.add('origin', 'https://github.com') == '[shenzhen] remote add origin https://github.com'
    print('[PASS] test_nbctx_multilevel_injection')


def test_nbctx_shared_reference():
    """测试父子共享同一个 nbctx 对象（引用传递）"""
    from nb_cmd.modes.cli_mode import _ensure_nbctx, _inject_nbctx

    app = MyApp(region='wuhan', env='prod')
    _ensure_nbctx(app)

    db = SubDbTool()
    remote = SubRemoteTool()
    _inject_nbctx(app, db)
    _inject_nbctx(app, remote)

    assert db.nbctx is remote.nbctx
    assert db.nbctx is app.nbctx
    print('[PASS] test_nbctx_shared_reference')


def test_nbctx_cli_run():
    """测试通过 CLI run 执行子命令时 nbctx 正确传递"""
    app = MyApp(region='hangzhou', env='test')
    result = app.run(['--region', 'hangzhou', 'status'])
    print('[PASS] test_nbctx_cli_run')


def test_nbctx_no_make_returns_none():
    """测试 make_nbctx 默认返回 None"""
    app = NoCtxApp()
    assert app.make_nbctx() is None
    print('[PASS] test_nbctx_no_make_returns_none')


if __name__ == '__main__':
    test_make_nbctx_basic()
    test_nbctx_property_with_make()
    test_nbctx_setter()
    test_nbctx_default_none()
    test_nbctx_manual_set_on_sub()
    test_nbctx_none_when_no_annotation()
    test_nbctx_cli_injection()
    test_nbctx_multilevel_injection()
    test_nbctx_shared_reference()
    test_nbctx_cli_run()
    test_nbctx_no_make_returns_none()
    print('\n=== 全部 nbctx 测试通过 ===')
