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
        - 六种能力：Python 直接调用 / CLI / REST API / Web UI / TUI 终端交互 / Markdown 文档
        - 支持 OOP 继承覆写
        - 支持多层级子命令（sub_commands）
        - 支持 nbctx 跨层级上下文传递

    工具方法通过 cmdui 模块级单例访问（from nb_cmd import cmdui）:
        cmdui.table()  cmdui.kv()  cmdui.tree()  cmdui.json_print()
        cmdui.success() cmdui.warning() cmdui.error() cmdui.info()
        cmdui.progress() cmdui.confirm() cmdui.prompt() cmdui.select()
    """

    sub_commands = {}

    Meta = NbCmdMeta

    nbctx = None  # 跨层级共享的上下文对象，子类通过 nbctx: AppCtx 注解获取 IDE 补全

    def __init__(self):
        self._logger = None
        self._setup_logging()

    def make_nbctx(self):
        """
        模板方法：创建跨层级共享的上下文对象。

        覆写此方法以返回一个 dataclass 实例，框架会自动将其传递给
        所有子命令组的 self.nbctx。

        用法::

            @dataclass
            class AppCtx:
                region: str = 'beijing'
                env: str = 'prod'

            class MyApp(NbCmd):
                def __init__(self, region='beijing', env='prod'):
                    self.region = region
                    self.env = env

                def make_nbctx(self):
                    return AppCtx(region=self.region, env=self.env)

        Returns
        -------
        object or None
            上下文对象，返回 None 表示不启用 nbctx。
        """
        return None

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
        if capture:
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True,
            )
            if check and result.returncode != 0:
                raise RuntimeError(
                    '命令执行失败 (exit {}): {}\n{}'.format(
                        result.returncode, cmd, result.stderr
                    )
                )
            return result.stdout.strip()

        proc = subprocess.Popen(
            cmd, shell=True,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, bufsize=1,
        )
        try:
            if proc.stdout:
                for line in proc.stdout:
                    print(line, end='')
            proc.wait()
        except KeyboardInterrupt:
            proc.kill()
            proc.wait()
            raise
        if check and proc.returncode != 0:
            raise RuntimeError(
                '命令执行失败 (exit {}): {}'.format(proc.returncode, cmd)
            )

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

        help_result = self._handle_help(raw_args)
        if help_result is not None:
            return help_result

        if '--web' in raw_args:
            return self._start_web_server(raw_args)

        if '--tui' in raw_args:
            return self._start_tui()

        from ..modes.cli_mode import run_cli
        return run_cli(self, NbCmd, args)

    _HELP_HANDLED = object()

    def _handle_help(self, raw_args):
        """
        处理帮助参数（在 argparse 解析之前拦截）。
        -fh/--full-help: 始终显示完整帮助
        -eh/--easy-help: 始终显示简易帮助
        -h/--help: 由 Meta.help_mode 决定

        返回 _HELP_HANDLED 表示已处理，应结束。返回 None 表示未处理。
        """
        if '--full-help' in raw_args or '-fh' in raw_args:
            from .parser import print_full_help
            print_full_help(self, NbCmd)
            return self._HELP_HANDLED

        if '--easy-help' in raw_args or '-eh' in raw_args:
            from .parser import print_easy_help
            print_easy_help(self, NbCmd)
            return self._HELP_HANDLED

        meta = self._get_meta()
        help_mode = getattr(meta, 'help_mode', 'full')
        if help_mode == 'full' and ('--help' in raw_args or '-h' in raw_args):
            from .parser import print_full_help
            print_full_help(self, NbCmd)
            return self._HELP_HANDLED

        return None

    def _start_web_server(self, raw_args):
        """启动 Web UI 服务"""
        port = self._extract_port(raw_args)
        meta = self._get_meta()
        host = getattr(meta, 'serve_host', '0.0.0.0')
        if port is None:
            port = getattr(meta, 'serve_port', 8080)

        from ..modes.web_mode import start_web_server
        start_web_server(self, NbCmd, host=host, port=port)

    def _start_tui(self):
        """启动 TUI 模式"""
        from ..modes.tui_mode import start_tui
        start_tui(self, NbCmd)

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
