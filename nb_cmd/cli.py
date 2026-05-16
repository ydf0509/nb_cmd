# -*- coding: utf-8 -*-
"""
nbcmd —— 个人命令中心。

零代码启动，通过 exec 收藏和管理所有常用系统命令。

用法:
    nbcmd --tui          # TUI 终端交互模式
    nbcmd --web          # Web 浏览器模式
    nbcmd exec <命令>    # 直接执行系统命令
    nbcmd -h             # 查看帮助
"""
import os

from .core.base import NbCmd
from .core.meta import NbCmdMeta


class _NbCmdApp(NbCmd):
    """个人命令中心 —— 收藏和管理常用系统命令"""

    class Meta(NbCmdMeta):
        name = 'nbcmd'
        version = '0.2.1'
        description = '个人命令中心 —— 通过 exec 收藏和管理所有常用系统命令'
        web_title = 'NbCmd 命令中心'
        db_dir = os.path.join(os.path.expanduser('~'), '.nb_cmd')


def main():
    app = _NbCmdApp()
    app.run()


if __name__ == '__main__':
    main()
