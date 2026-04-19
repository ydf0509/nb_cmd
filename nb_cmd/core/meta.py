# -*- coding: utf-8 -*-
"""
NbCmd Meta 配置基类。

用法::

    from nb_cmd import NbCmd, NbCmdMeta

    class MyTool(NbCmd):
        class Meta(NbCmdMeta):
            name = "my-tool"
            version = "1.0.0"
            use_nb_log = True
"""


class NbCmdMeta(object):
    """
    NbCmd 的 Meta 配置基类。

    子类继承后可覆盖任意字段，IDE 可自动补全所有可用选项。
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
    help_mode = 'full'         # type: str   # -h 帮助模式: 'full'(完整帮助) / 'easy'(简易帮助)
    aliases = {}               # type: dict  # 参数别名（推荐用 Annotated 替代）
