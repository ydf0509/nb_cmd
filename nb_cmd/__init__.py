# -*- coding: utf-8 -*-
"""
nb_cmd — 万能接口生成器
你写一个 Python class，自动获得 CLI + REST API + Web UI 三种接口。

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
