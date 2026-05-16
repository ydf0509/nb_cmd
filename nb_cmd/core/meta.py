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

from typing import Dict, List, Optional


class NbCmdMeta(object):
    """
    NbCmd 的 Meta 配置基类。

    子类继承后可覆盖任意字段，IDE 可自动补全所有可用选项。
    """
    name: Optional[str] = None               # CLI/API 名称（默认用类名）
    version: str = '0.0.1'                   # 版本号（--cmd-version 显示）
    description: Optional[str] = None        # 描述（默认用类的 docstring）
    use_nb_log: bool = False                 # 启用 nb_log 增强日志
    log_level: str = 'INFO'                  # 日志级别
    log_file: Optional[str] = None           # 日志文件路径
    auto_save_last_args: bool = False        # 自动保存上次参数
    config_file: Optional[str] = None        # 配置持久化文件路径
    serve_host: str = '0.0.0.0'              # Web/API 绑定地址
    serve_port: int = 8080                   # Web/API 默认端口
    serve_workers: int = 1                   # 工作进程数
    web_title: Optional[str] = None          # Web UI 页面标题
    web_theme: str = 'light'                 # Web UI 主题 ('light' / 'dark')
    enable_exec: bool = True                 # 是否暴露内置 exec 命令（False 可防止恶意执行）
    help_mode: str = 'full'                  # -h 帮助模式: 'full'(完整帮助) / 'easy'(简易帮助)
    aliases: Dict[str, List[str]] = {}       # 参数别名（推荐用 Annotated 替代）
    allow_method_list: Optional[List[str]] = None  # 命令白名单（仅限制 CLI/API/Web 暴露；Python 直接调用不受影响）
    hide_method_list: Optional[List[str]] = None   # 命令黑名单（与白名单互斥；仅限制 CLI/API/Web 暴露）
    auth_token: Optional[str] = None               # 简易鉴权 token（配置后 API/Web 请求须带 Authorization: Bearer <token>）
    timeout: int = 0                               # 命令执行超时秒数（0=不限；仅作用于 CLI/API/Web 模式）
    db_dir: Optional[str] = None                     # SQLite 数据库目录（默认 None=当前工作目录；可设为 ~/.nb_cmd 等固定路径）
