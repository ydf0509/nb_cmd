# -*- coding: utf-8 -*-
"""
nb_cmd — 万能接口生成器
你写一个 Python class，自动获得 CLI + REST API + Web UI 三种接口。

用法::

    from nb_cmd import NbCmd

    class MyTool(NbCmd):
        def greet(self, name: str, times: int = 1):
            for _ in range(times):
                print(f"你好, {name}!")

    if __name__ == '__main__':
        MyTool().run()
"""

__version__ = '0.1.0'

import json
import logging
import sys

from .core.arg import Arg  # noqa: F401
# 模块级 cmdui 单例，在延后创建（类定义之后）
from .ui.colors import print_success, print_warning, print_error, print_info
from .ui.table import print_table, print_kv
from .ui.progress import progress as _progress_iter
from .utils.validators import validate  # noqa: F401


class NbCmdMeta(object):
    """
    NbCmd 的 Meta 配置基类。

    子类继承后可覆盖任意字段，IDE 可自动补全所有可用选项。

    用法::

        from nb_cmd import NbCmd, NbCmdMeta

        class MyTool(NbCmd):
            class Meta(NbCmdMeta):
                name = "my-tool"
                use_nb_log = True
    """
    name = None               # type: str   # CLI/API 名称（默认用类名）
    version = '0.0.1'         # type: str   # 版本号（--version 显示）
    description = None        # type: str   # 描述（默认用类的 docstring）
    use_nb_log = False         # type: bool  # 启用 nb_log 增强日志
    log_level = 'INFO'         # type: str   # 日志级别
    log_file = None            # type: str   # 日志文件路径
    auto_save_last_args = False  # type: bool  # 自动保存上次参数
    config_file = None         # type: str   # 配置持久化文件路径
    serve_host = '0.0.0.0'    # type: str   # Web/API 绑定地址
    serve_port = 8080          # type: int   # Web/API 默认端口
    serve_workers = 1          # type: int   # 工作进程数
    web_title = None           # type: str   # Web UI 页面标题
    web_theme = 'light'        # type: str   # Web UI 主题 ('light' / 'dark')
    enable_exec = True         # type: bool  # 是否暴露内置 exec 命令（False 可防止恶意执行）
    aliases = {}               # type: dict  # 参数别名（推荐用 Arg(alias=...) 替代）


class UIHelper(object):
    """
    NbCmd 的 UI 工具方法集合。

    通过 ``from nb_cmd import cmdui`` 导入使用，避免与用户自定义的子命令方法名冲突。
    包含: 输出(table/kv/tree/json_print)、彩色(success/warning/error/info)、
          交互(confirm/prompt/select)、进度(progress) 等工具。
    """

    def table(self, data, headers=None):
        """表格输出"""
        print_table(data, headers)

    def kv(self, data):
        """键值对输出"""
        print_kv(data)

    def tree(self, data, prefix='', is_last=True):
        """树形输出"""
        if isinstance(data, dict):
            items = list(data.items())
            for i, (key, value) in enumerate(items):
                last = (i == len(items) - 1)
                connector = '└── ' if last else '├── '
                if isinstance(value, dict):
                    sys.stdout.write('{}{}{}\n'.format(prefix, connector, key))
                    extension = '    ' if last else '│   '
                    self.tree(value, prefix + extension, last)
                else:
                    sys.stdout.write('{}{}{}: {}\n'.format(prefix, connector, key, value))

    def json_print(self, data):
        """JSON美化输出"""
        sys.stdout.write(json.dumps(data, ensure_ascii=False, indent=2, default=str) + '\n')
        sys.stdout.flush()

    def progress(self, iterable, desc=None, total=None):
        """进度条迭代器"""
        return _progress_iter(iterable, desc=desc, total=total)

    def confirm(self, message):
        """确认提示，返回 True/False"""
        try:
            answer = input('{} [y/N]: '.format(message)).strip().lower()
            return answer in ('y', 'yes')
        except (EOFError, KeyboardInterrupt):
            return False

    def prompt(self, message, default=None):
        """输入提示"""
        try:
            if default is not None:
                answer = input('{} [{}]: '.format(message, default)).strip()
                return answer if answer else default
            else:
                return input('{}: '.format(message)).strip()
        except (EOFError, KeyboardInterrupt):
            return default

    def select(self, message, choices):
        """选择提示"""
        sys.stdout.write(message + '\n')
        for i, choice in enumerate(choices):
            sys.stdout.write('  {}. {}\n'.format(i + 1, choice))
        sys.stdout.flush()
        try:
            idx = int(input('请选择 [1-{}]: '.format(len(choices))).strip()) - 1
            if 0 <= idx < len(choices):
                return choices[idx]
        except (ValueError, EOFError, KeyboardInterrupt):
            pass
        return choices[0] if choices else None

    def success(self, msg):
        """绿色成功信息"""
        print_success(msg)

    def warning(self, msg):
        """黄色警告信息"""
        print_warning(msg)

    def error(self, msg):
        """红色错误信息"""
        print_error(msg)

    def info(self, msg):
        """蓝色信息"""
        print_info(msg)


class NbCmd(object):
    """
    NbCmd 基类 —— 所有命令行工具的父类。

    用法:
        1. 继承 NbCmd
        2. 定义公有方法（自动成为子命令）
        3. 调用 .run() 启动

    功能:
        - 公有方法 → 子命令
        - 方法签名 → 参数自动推导
        - 支持 CLI / REST API / Web UI 三种模式
        - 支持 OOP 继承覆写
        - 支持多层级子命令（sub_commands）

    工具方法通过 cmdui 模块级单例访问（from nb_cmd import cmdui）:
        cmdui.table()  cmdui.kv()  cmdui.tree()  cmdui.json_print()
        cmdui.success() cmdui.warning() cmdui.error() cmdui.info()
        cmdui.progress() cmdui.confirm() cmdui.prompt() cmdui.select()
    """

    sub_commands = {}

    Meta = NbCmdMeta

    def __init__(self):
        self._logger = None
        self._setup_logging()

    def _setup_logging(self):
        """设置日志"""
        meta = self._get_meta()
        use_nb_log = getattr(meta, 'use_nb_log', False)
        log_level = getattr(meta, 'log_level', 'INFO')

        if use_nb_log:
            try:
                import nb_log
                self._logger = nb_log.get_logger(
                    self.__class__.__name__,
                    log_level_int=getattr(logging, log_level, logging.INFO),
                    log_filename=getattr(meta, 'log_file', None),
                )
                return
            except ImportError:
                pass

        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.setLevel(getattr(logging, log_level, logging.INFO))
        if not self._logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter(
                '%(asctime)s [%(name)s] %(levelname)s: %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            ))
            self._logger.addHandler(handler)

    def _get_meta(self):
        """获取 Meta 配置类"""
        return getattr(self.__class__, 'Meta', NbCmd.Meta)

    @property
    def logger(self):
        """日志器"""
        return self._logger

    # ==================== 生命周期钩子 ====================

    def before_run(self):
        """所有子命令执行前的钩子，子类可覆写"""
        pass

    def after_run(self):
        """所有子命令执行后的钩子，子类可覆写"""
        pass

    def on_error(self, command, error):
        """子命令执行出错时的钩子，子类可覆写"""
        if self._logger:
            self._logger.error('命令 {} 执行失败: {}'.format(command, error))

    # ==================== 系统命令工具 ====================

    def shell(self, cmd, capture=False, check=False):
        """
        执行系统命令。

        Parameters
        ----------
        cmd : str  要执行的命令
        capture : bool  是否捕获输出（True 返回 stdout 字符串，False 通过 print 输出）
        check : bool  命令失败时是否抛出异常

        Returns
        -------
        str (capture=True 时返回 stdout) 或 None
        """
        import subprocess
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True,
        )
        if check and result.returncode != 0:
            raise RuntimeError(
                '命令执行失败 (exit {}): {}\n{}'.format(
                    result.returncode, cmd, result.stderr
                )
            )
        if capture:
            return result.stdout.strip()
        else:
            if result.stdout:
                print(result.stdout, end='')
            if result.stderr:
                print(result.stderr, end='', file=sys.stderr)

    def exec(self, cmd: str):
        """执行任意系统命令"""
        self.shell(cmd)

    # ==================== 主入口 ====================

    def run(self, args=None):
        """
        主入口方法。根据参数决定运行模式。

        Parameters
        ----------
        args : list, optional
            命令行参数列表，默认使用 sys.argv[1:]
        """
        raw_args = args if args is not None else sys.argv[1:]

        if '--full-help' in raw_args or '-fh' in raw_args:
            from .core.parser import print_full_help
            return print_full_help(self, NbCmd)

        if '--web' in raw_args:
            return self._start_web_server(raw_args)

        from .modes.cli_mode import run_cli
        return run_cli(self, NbCmd, args)

    def _start_web_server(self, raw_args):
        """启动 Web UI 服务"""
        port = self._extract_port(raw_args)
        meta = self._get_meta()
        host = getattr(meta, 'serve_host', '0.0.0.0')
        if port is None:
            port = getattr(meta, 'serve_port', 8080)

        from .modes.web_mode import start_web_server
        start_web_server(self, NbCmd, host=host, port=port)

    @staticmethod
    def _extract_port(raw_args):
        """从参数列表中提取 --web-port 的值"""
        if '--web-port' in raw_args:
            idx = raw_args.index('--web-port')
            if idx + 1 < len(raw_args):
                try:
                    return int(raw_args[idx + 1])
                except ValueError:
                    pass
        return None


cmdui = UIHelper()
