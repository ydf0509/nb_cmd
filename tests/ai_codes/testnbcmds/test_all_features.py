# -*- coding: utf-8 -*-
"""
nb_cmd 综合测试套件
覆盖所有核心功能：CLI、API、Web、async、继承、子命令组、全局参数等
"""
import sys
import os
import io
import asyncio
import inspect
from enum import Enum
try:
    from typing import Annotated, List, Optional
except ImportError:
    from typing_extensions import Annotated
    from typing import List, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from nb_cmd import NbCmd, NbCmdMeta, cmdui, Param
from nb_cmd.core.discovery import discover_commands
from nb_cmd.core.parser import build_parser
from nb_cmd.core.type_utils import convert_value
from nb_cmd.core.result_handler import handle_cli_result, handle_api_result
from nb_cmd.modes.cli_mode import run_cli, _run_method
from nb_cmd.ui.colors import print_success, print_warning, print_error, print_info
from nb_cmd.ui.table import print_table, print_kv


# ==================== 1. 基础功能测试 ====================

class TestBasicTool(NbCmd):
    """基础工具测试"""
    def greet(self, name: str, times: int = 1):
        """向某人问好"""
        results = []
        for _ in range(times):
            results.append('你好, {}!'.format(name))
        return results

    def add(self, a: int, b: int):
        """加法运算"""
        return a + b

    def _private_method(self):
        """私有方法，不应暴露为命令"""
        pass


def test_basic_discovery():
    """测试命令发现"""
    tool = TestBasicTool()
    cmds = discover_commands(tool, NbCmd)
    
    assert 'greet' in cmds, 'greet 命令应被发现'
    assert 'add' in cmds, 'add 命令应被发现'
    assert '_private_method' not in cmds, '私有方法不应被发现'
    
    greet_info = cmds['greet']
    assert greet_info['doc'] == '向某人问好'
    assert 'name' in greet_info['type_hints']
    assert greet_info['type_hints']['name'] is str
    assert 'times' in greet_info['type_hints']
    assert greet_info['type_hints']['times'] is int
    
    print('test_basic_discovery passed!')


def test_basic_execution():
    """测试基本执行"""
    tool = TestBasicTool()
    
    result = tool.greet('张三', times=3)
    assert result == ['你好, 张三!', '你好, 张三!', '你好, 张三!']
    
    result = tool.add(10, 20)
    assert result == 30
    
    print('test_basic_execution passed!')


def test_cli_mode():
    """测试 CLI 模式"""
    tool = TestBasicTool()
    
    # 测试 greet 命令
    old_stdout = sys.stdout
    sys.stdout = captured = io.StringIO()
    try:
        run_cli(tool, NbCmd, ['greet', '张三', '--times', '2'])
    finally:
        sys.stdout = old_stdout
    
    output = captured.getvalue()
    assert '你好, 张三!' in output
    
    # 测试 add 命令
    sys.stdout = captured = io.StringIO()
    try:
        run_cli(tool, NbCmd, ['add', '10', '20'])
    finally:
        sys.stdout = old_stdout
    
    output = captured.getvalue()
    assert '30' in output
    
    print('test_cli_mode passed!')


# ==================== 2. Annotated 参数测试 ====================

class TestAnnotatedTool(NbCmd):
    """Annotated 参数测试"""
    def deploy(self, 
               host: Annotated[str, '服务器地址', 'H'],
               port: Annotated[int, '端口号', 'p'] = 22,
               verbose: Annotated[bool, '详细模式', 'v'] = False):
        """部署到远程服务器"""
        return {'host': host, 'port': port, 'verbose': verbose}

    def query(self, 
              name: Annotated[str, Param(desc='用户名', alias='n')],
              age: Annotated[int, Param(desc='年龄')] = 18):
        """查询用户"""
        return {'name': name, 'age': age}


def test_annotated_discovery():
    """测试 Annotated 参数发现"""
    tool = TestAnnotatedTool()
    cmds = discover_commands(tool, NbCmd)
    
    deploy_info = cmds['deploy']
    assert deploy_info['arg_meta']['host'].desc == '服务器地址'
    assert deploy_info['arg_meta']['host'].aliases == ['-H']
    assert deploy_info['arg_meta']['port'].desc == '端口号'
    assert deploy_info['arg_meta']['port'].aliases == ['-p']
    assert deploy_info['arg_meta']['verbose'].desc == '详细模式'
    assert deploy_info['arg_meta']['verbose'].aliases == ['-v']
    
    query_info = cmds['query']
    assert query_info['arg_meta']['name'].desc == '用户名'
    assert query_info['arg_meta']['name'].aliases == ['-n']
    assert query_info['arg_meta']['age'].desc == '年龄'
    
    print('test_annotated_discovery passed!')


def test_annotated_cli():
    """测试 Annotated CLI 执行"""
    tool = TestAnnotatedTool()
    
    old_stdout = sys.stdout
    sys.stdout = captured = io.StringIO()
    try:
        run_cli(tool, NbCmd, ['deploy', '-H', '10.0.0.1', '-p', '8080', '-v'])
    finally:
        sys.stdout = old_stdout
    
    output = captured.getvalue()
    assert '10.0.0.1' in output
    assert '8080' in output
    
    print('test_annotated_cli passed!')


# ==================== 3. Enum 类型测试 ====================

class Environment(Enum):
    DEV = "dev"
    STAGING = "staging"
    PROD = "prod"


class TestEnumTool(NbCmd):
    """Enum 类型测试"""
    def deploy(self, host: str, env: Environment = Environment.DEV):
        """部署到指定环境"""
        return {'host': host, 'env': env.value}


def test_enum_discovery():
    """测试 Enum 参数发现"""
    tool = TestEnumTool()
    cmds = discover_commands(tool, NbCmd)
    
    deploy_info = cmds['deploy']
    assert 'env' in deploy_info['type_hints']
    
    print('test_enum_discovery passed!')


def test_enum_cli():
    """测试 Enum CLI 执行"""
    tool = TestEnumTool()
    
    old_stdout = sys.stdout
    sys.stdout = captured = io.StringIO()
    try:
        run_cli(tool, NbCmd, ['deploy', '10.0.0.1', '--env', 'prod'])
    finally:
        sys.stdout = old_stdout
    
    output = captured.getvalue()
    assert 'prod' in output
    
    print('test_enum_cli passed!')


# ==================== 4. OOP 继承测试 ====================

class BaseDeploy(NbCmd):
    """基础部署"""
    def deploy(self, host: str, version: str = "latest"):
        """基础部署方法"""
        self._pre_deploy(host)
        self._do_deploy(host, version)
        self._post_deploy(host)
        return {'host': host, 'version': version, 'steps': self._steps}

    def _pre_deploy(self, host):
        self._steps = ['pre_deploy: {}'.format(host)]

    def _do_deploy(self, host, version):
        self._steps.append('do_deploy: {} {}'.format(host, version))

    def _post_deploy(self, host):
        self._steps.append('post_deploy: {}'.format(host))


class DockerDeploy(BaseDeploy):
    """Docker 部署——覆写 _do_deploy"""
    def _do_deploy(self, host, version):
        self._steps.append('docker_deploy: {} {}'.format(host, version))


class K8sDeploy(BaseDeploy):
    """K8s 部署——覆写 + 新增命令"""
    def _do_deploy(self, host, version):
        self._steps.append('k8s_deploy: {} {}'.format(host, version))

    def scale(self, replicas: int = 3):
        """扩缩容"""
        return {'replicas': replicas}


def test_inheritance():
    """测试 OOP 继承"""
    # 基础部署
    base = BaseDeploy()
    result = base.deploy('web-01', version='v1.0')
    assert result['host'] == 'web-01'
    assert result['version'] == 'v1.0'
    assert len(result['steps']) == 3
    
    # Docker 部署——覆写 _do_deploy
    docker = DockerDeploy()
    result = docker.deploy('web-01', version='v1.0')
    assert 'docker_deploy' in result['steps'][1]
    
    # K8s 部署——覆写 + 新增命令
    k8s = K8sDeploy()
    result = k8s.deploy('web-01', version='v1.0')
    assert 'k8s_deploy' in result['steps'][1]
    
    # K8s 特有命令
    result = k8s.scale(replicas=5)
    assert result['replicas'] == 5
    
    print('test_inheritance passed!')


def test_inheritance_discovery():
    """测试继承类的命令发现"""
    k8s = K8sDeploy()
    cmds = discover_commands(k8s, NbCmd)
    
    assert 'deploy' in cmds, '继承的 deploy 命令应被发现'
    assert 'scale' in cmds, '新增的 scale 命令应被发现'
    
    print('test_inheritance_discovery passed!')


# ==================== 5. 多层级子命令测试 ====================

class GitRemote(NbCmd):
    """远程仓库管理"""
    def add(self, name: str, url: str):
        """添加远程仓库"""
        return {'action': 'add', 'name': name, 'url': url}

    def remove(self, name: str):
        """删除远程仓库"""
        return {'action': 'remove', 'name': name}


class GitTool(NbCmd):
    """Git 工具"""
    sub_commands = {'remote': GitRemote}

    def status(self):
        """查看状态"""
        return {'branch': 'main'}

    def commit(self, message: str, all: bool = False):
        """提交"""
        return {'message': message, 'all': all}


def test_subcommands_discovery():
    """测试子命令组发现"""
    git = GitTool()
    cmds = discover_commands(git, NbCmd)
    
    assert 'status' in cmds
    assert 'commit' in cmds
    assert 'remote' in cmds
    assert cmds['remote'].get('is_group') == True
    
    print('test_subcommands_discovery passed!')


def test_subcommands_cli():
    """测试子命令组 CLI 执行"""
    git = GitTool()
    
    old_stdout = sys.stdout
    sys.stdout = captured = io.StringIO()
    try:
        run_cli(git, NbCmd, ['status'])
    finally:
        sys.stdout = old_stdout
    
    output = captured.getvalue()
    assert 'main' in output
    
    print('test_subcommands_cli passed!')


# ==================== 6. 全局参数（__init__）测试 ====================

class TestInitParamsTool(NbCmd):
    """全局参数测试"""
    def __init__(self, region: Annotated[str, '机房区域', 'r'] = 'beijing',
                 timeout: Annotated[int, '超时秒数'] = 30):
        super().__init__()
        self.region = region
        self.timeout = timeout

    def deploy(self, host: str):
        """部署"""
        return {'host': host, 'region': self.region, 'timeout': self.timeout}

    def stats(self):
        """统计"""
        return {'region': self.region, 'timeout': self.timeout}


def test_init_params():
    """测试全局参数"""
    # 默认值
    tool = TestInitParamsTool()
    assert tool.region == 'beijing'
    assert tool.timeout == 30
    
    # 自定义值
    tool = TestInitParamsTool(region='shanghai', timeout=60)
    assert tool.region == 'shanghai'
    assert tool.timeout == 60
    
    result = tool.deploy('10.0.0.1')
    assert result['region'] == 'shanghai'
    assert result['timeout'] == 60
    
    print('test_init_params passed!')


def test_init_params_cli():
    """测试全局参数 CLI"""
    tool = TestInitParamsTool(region='shanghai')
    
    old_stdout = sys.stdout
    sys.stdout = captured = io.StringIO()
    try:
        run_cli(tool, NbCmd, ['deploy', '10.0.0.1'])
    finally:
        sys.stdout = old_stdout
    
    output = captured.getvalue()
    # 输出是 JSON 格式，包含 region 字段
    assert 'shanghai' in output or '10.0.0.1' in output
    
    print('test_init_params_cli passed!')


# ==================== 7. async 函数测试 ====================

class TestAsyncTool(NbCmd):
    """async 函数测试"""
    async def async_deploy(self, host: str, port: int = 22):
        """异步部署"""
        await asyncio.sleep(0.1)
        return {'host': host, 'port': port, 'async': True}

    def sync_deploy(self, host: str, port: int = 22):
        """同步部署"""
        return {'host': host, 'port': port, 'async': False}


def test_async_function():
    """测试 async 函数执行"""
    tool = TestAsyncTool()
    
    # 测试 _run_method 对 async 函数的处理
    result = _run_method(tool.async_deploy, {'host': '10.0.0.1', 'port': 8080})
    assert result['host'] == '10.0.0.1'
    assert result['port'] == 8080
    assert result['async'] == True
    
    # 测试 _run_method 对 sync 函数的处理
    result = _run_method(tool.sync_deploy, {'host': '10.0.0.1', 'port': 8080})
    assert result['host'] == '10.0.0.1'
    assert result['port'] == 8080
    assert result['async'] == False
    
    print('test_async_function passed!')


def test_async_cli():
    """测试 async CLI 执行"""
    tool = TestAsyncTool()
    
    old_stdout = sys.stdout
    sys.stdout = captured = io.StringIO()
    try:
        run_cli(tool, NbCmd, ['async-deploy', '10.0.0.1', '--port', '8080'])
    finally:
        sys.stdout = old_stdout
    
    output = captured.getvalue()
    assert '10.0.0.1' in output
    assert '8080' in output
    
    print('test_async_cli passed!')


def test_async_detection():
    """测试 async 函数检测"""
    tool = TestAsyncTool()
    cmds = discover_commands(tool, NbCmd)
    
    async_deploy_info = cmds['async_deploy']
    assert inspect.iscoroutinefunction(async_deploy_info['method'])
    
    sync_deploy_info = cmds['sync_deploy']
    assert not inspect.iscoroutinefunction(sync_deploy_info['method'])
    
    print('test_async_detection passed!')


# ==================== 8. cmdui 工具测试 ====================

def test_cmdui_output():
    """测试 cmdui 输出工具"""
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    sys.stdout = captured = io.StringIO()
    sys.stderr = err_captured = io.StringIO()
    try:
        # 测试 table
        cmdui.table([
            {"id": 1, "name": "张三"},
            {"id": 2, "name": "李四"},
        ])
        
        # 测试 kv
        cmdui.kv({"数据库": "SQLite", "大小": "15.3 MB"})
        
        # 测试 tree
        cmdui.tree({
            "数据库": {
                "users": {"id": "INT", "name": "VARCHAR"},
            }
        })
        
        # 测试彩色输出
        cmdui.success("成功消息")
        cmdui.warning("警告消息")
        cmdui.info("信息消息")
        # cmdui.error 输出到 stderr
        cmdui.error("错误消息")
        
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr
    
    output = captured.getvalue()
    err_output = err_captured.getvalue()
    assert '张三' in output
    assert '李四' in output
    assert '数据库' in output
    assert 'SQLite' in output
    assert '成功消息' in output
    assert '警告消息' in output
    assert '信息消息' in output
    # 错误消息在 stderr 中
    assert '错误消息' in err_output
    
    print('test_cmdui_output passed!')


# ==================== 9. 参数校验测试 ====================

class TestValidationTool(NbCmd):
    """参数校验测试"""
    def process(self, count: int, ratio: float = 1.0):
        """处理数据"""
        return {'count': count, 'ratio': ratio}


def test_type_conversion():
    """测试类型转换"""
    assert convert_value('123', int) == 123
    assert convert_value('3.14', float) == 3.14
    # bool 类型在 convert_value 中直接返回原值（argparse 不转换）
    assert convert_value(True, bool) == True
    assert convert_value(False, bool) == False
    assert convert_value('hello', str) == 'hello'
    
    print('test_type_conversion passed!')


def test_validation_cli():
    """测试 CLI 参数校验"""
    tool = TestValidationTool()
    
    old_stdout = sys.stdout
    sys.stdout = captured = io.StringIO()
    try:
        run_cli(tool, NbCmd, ['process', '100', '--ratio', '2.5'])
    finally:
        sys.stdout = old_stdout
    
    output = captured.getvalue()
    assert '100' in output
    assert '2.5' in output
    
    print('test_validation_cli passed!')


# ==================== 10. 生命周期钩子测试 ====================

class TestHooksTool(NbCmd):
    """生命周期钩子测试"""
    def __init__(self):
        super().__init__()
        self.before_called = False
        self.after_called = False
        self.error_called = False

    def before_run(self):
        self.before_called = True

    def after_run(self):
        self.after_called = True

    def on_error(self, command, error):
        self.error_called = True

    def success_cmd(self):
        """成功命令"""
        return 'ok'

    def error_cmd(self):
        """失败命令"""
        raise ValueError('测试错误')


def test_hooks():
    """测试生命周期钩子"""
    tool = TestHooksTool()
    
    # 测试成功命令
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    try:
        run_cli(tool, NbCmd, ['success-cmd'])
    finally:
        sys.stdout = old_stdout
    
    assert tool.before_called == True
    assert tool.after_called == True
    assert tool.error_called == False
    
    # 测试失败命令
    tool2 = TestHooksTool()
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    try:
        run_cli(tool2, NbCmd, ['error-cmd'])
    except ValueError:
        pass
    finally:
        sys.stdout = old_stdout
    
    assert tool2.before_called == True
    assert tool2.after_called == True
    assert tool2.error_called == True
    
    print('test_hooks passed!')


# ==================== 11. Meta 配置测试 ====================

class TestMetaTool(NbCmd):
    """Meta 配置测试"""
    class Meta(NbCmdMeta):
        name = "test-meta-tool"
        version = "2.0.0"
        description = "测试 Meta 配置"
        use_nb_log = False
        log_level = 'DEBUG'
        serve_host = '127.0.0.1'
        serve_port = 9999
        web_title = "测试标题"
        web_theme = 'dark'
        enable_exec = False

    def hello(self):
        """你好"""
        return 'hello'


def test_meta_config():
    """测试 Meta 配置"""
    tool = TestMetaTool()
    meta = tool._get_meta()
    
    assert meta.name == "test-meta-tool"
    assert meta.version == "2.0.0"
    assert meta.description == "测试 Meta 配置"
    assert meta.use_nb_log == False
    assert meta.log_level == 'DEBUG'
    assert meta.serve_host == '127.0.0.1'
    assert meta.serve_port == 9999
    assert meta.web_title == "测试标题"
    assert meta.web_theme == 'dark'
    assert meta.enable_exec == False
    
    print('test_meta_config passed!')


# ==================== 12. shell/exec 命令测试 ====================

class TestShellTool(NbCmd):
    """shell 命令测试"""
    def run_cmd(self, cmd: str):
        """执行命令"""
        return self.shell(cmd, capture=True)


def test_shell():
    """测试 shell 命令"""
    tool = TestShellTool()
    
    # 测试简单命令
    result = tool.shell('echo hello', capture=True)
    assert 'hello' in result
    
    # 测试带返回值的命令
    result = tool.shell('python -c "print(1+1)"', capture=True)
    assert '2' in result
    
    print('test_shell passed!')


# ==================== 13. 组合多个 NbCmd 测试 ====================

class ToolA(NbCmd):
    """工具 A"""
    def cmd_a(self):
        """命令 A"""
        return 'A'


class ToolB(NbCmd):
    """工具 B"""
    def cmd_b(self):
        """命令 B"""
        return 'B'


class CombinedTool(NbCmd):
    """组合工具"""
    sub_commands = {
        'tool-a': ToolA,
        'tool-b': ToolB,
    }


def test_combined_tool():
    """测试组合工具"""
    tool = CombinedTool()
    cmds = discover_commands(tool, NbCmd)
    
    assert 'tool-a' in cmds
    assert 'tool-b' in cmds
    assert cmds['tool-a'].get('is_group') == True
    assert cmds['tool-b'].get('is_group') == True
    
    print('test_combined_tool passed!')


# ==================== 14. 结果处理测试 ====================

def test_result_handler():
    """测试结果处理"""
    # CLI 结果处理
    old_stdout = sys.stdout
    sys.stdout = captured = io.StringIO()
    try:
        handle_cli_result('hello')
        handle_cli_result(123)
        handle_cli_result([1, 2, 3])
        handle_cli_result({'key': 'value'})
        handle_cli_result(None)
    finally:
        sys.stdout = old_stdout
    
    output = captured.getvalue()
    assert 'hello' in output
    assert '123' in output
    
    # API 结果处理 - handle_api_result 会包装结果
    result = handle_api_result('hello')
    assert result == {"result": "hello"}
    
    result = handle_api_result({'key': 'value'})
    assert result == {'key': 'value'}
    
    print('test_result_handler passed!')


# ==================== 15. 边界情况测试 ====================

class TestEdgeCases(NbCmd):
    """边界情况测试"""
    def no_params(self):
        """无参数命令"""
        return 'no_params'

    def many_params(self, a: str, b: int, c: float, d: bool = False, e: str = 'default'):
        """多参数命令"""
        return {'a': a, 'b': b, 'c': c, 'd': d, 'e': e}

    def return_none(self):
        """返回 None"""
        return None

    def return_empty(self):
        """返回空"""
        return []


def test_edge_cases():
    """测试边界情况"""
    tool = TestEdgeCases()
    
    # 无参数
    result = tool.no_params()
    assert result == 'no_params'
    
    # 多参数
    result = tool.many_params('test', 100, 3.14, d=True, e='custom')
    assert result['a'] == 'test'
    assert result['b'] == 100
    assert result['c'] == 3.14
    assert result['d'] == True
    assert result['e'] == 'custom'
    
    # 返回 None
    result = tool.return_none()
    assert result is None
    
    # 返回空列表
    result = tool.return_empty()
    assert result == []
    
    print('test_edge_cases passed!')


# ==================== 主测试入口 ====================

def run_all_tests():
    """运行所有测试"""
    print('=' * 60)
    print('nb_cmd 综合测试套件')
    print('=' * 60)
    
    tests = [
        ('1. 基础功能', [test_basic_discovery, test_basic_execution, test_cli_mode]),
        ('2. Annotated 参数', [test_annotated_discovery, test_annotated_cli]),
        ('3. Enum 类型', [test_enum_discovery, test_enum_cli]),
        ('4. OOP 继承', [test_inheritance, test_inheritance_discovery]),
        ('5. 多层级子命令', [test_subcommands_discovery, test_subcommands_cli]),
        ('6. 全局参数', [test_init_params, test_init_params_cli]),
        ('7. async 函数', [test_async_function, test_async_cli, test_async_detection]),
        ('8. cmdui 工具', [test_cmdui_output]),
        ('9. 参数校验', [test_type_conversion, test_validation_cli]),
        ('10. 生命周期钩子', [test_hooks]),
        ('11. Meta 配置', [test_meta_config]),
        ('12. shell 命令', [test_shell]),
        ('13. 组合工具', [test_combined_tool]),
        ('14. 结果处理', [test_result_handler]),
        ('15. 边界情况', [test_edge_cases]),
    ]
    
    passed = 0
    failed = 0
    errors = []
    
    for category, test_funcs in tests:
        print('\n{}'.format(category))
        print('-' * 40)
        for test_func in test_funcs:
            try:
                test_func()
                passed += 1
            except Exception as e:
                failed += 1
                import traceback
                errors.append((test_func.__name__, traceback.format_exc()))
                print('  FAIL: {} - {}'.format(test_func.__name__, e))
    
    print('\n' + '=' * 60)
    print('测试结果: {} 通过, {} 失败'.format(passed, failed))
    
    if errors:
        print('\n失败的测试:')
        for name, error in errors:
            print('  - {}: {}'.format(name, error))
    
    print('=' * 60)
    
    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
