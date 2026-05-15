# -*- coding: utf-8 -*-
"""
nb_cmd — Python 码农的低代码平台
写一个 class，自动获得六种能力：Python 直接调用 + CLI + REST API + Web UI + TUI 终端交互 + Markdown 文档。

用法::

    from nb_cmd import NbCmd

    class MyTool(NbCmd):
        def greet(self, name: str, times: int = 1):
            for _ in range(times):
                print('你好, {}!'.format(name))

    if __name__ == '__main__':
        MyTool().run()
"""

__version__ = '0.1.0'

from .core.base import NbCmd  # noqa: F401
from .core.meta import NbCmdMeta  # noqa: F401
from .core.arg import Annotated, Param  # noqa: F401
from .ui.helper import UIHelper, cmdui  # noqa: F401
from .utils.validators import validate  # noqa: F401
from .core.gen_cmd import CmdGen  # noqa: F401
