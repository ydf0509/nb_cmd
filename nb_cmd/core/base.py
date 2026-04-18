# -*- coding: utf-8 -*-
"""
NbCmd 基类 —— 所有命令行工具的父类。
"""
import logging
import sys

from .meta import NbCmdMeta


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
            from .parser import print_full_help
            return print_full_help(self, NbCmd)

        if '--web' in raw_args:
            return self._start_web_server(raw_args)

        from ..modes.cli_mode import run_cli
        return run_cli(self, NbCmd, args)

    def _start_web_server(self, raw_args):
        """启动 Web UI 服务"""
        port = self._extract_port(raw_args)
        meta = self._get_meta()
        host = getattr(meta, 'serve_host', '0.0.0.0')
        if port is None:
            port = getattr(meta, 'serve_port', 8080)

        from ..modes.web_mode import start_web_server
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
