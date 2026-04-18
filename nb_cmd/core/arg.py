# -*- coding: utf-8 -*-
"""
参数描述器 —— 通过 Annotated 为方法参数附加描述和别名。

用法::

    from typing import Annotated  # Python 3.9+
    from nb_cmd import NbCmd, Param

    class MyTool(NbCmd):
        # 方式一：位置参数（简洁）
        def greet(self, name: Annotated[str, '要问候的人名', 'n'],
                  times: Annotated[int, '问候次数'] = 1):
            ...

        # 方式二：Param 对象（关键字参数，清晰）
        def deploy(self, host: Annotated[str, Param(desc='服务器地址', alias='H')],
                   port: Annotated[int, Param(desc='端口号', alias='p')] = 22):
            ...

Annotated 规则:
    Annotated[类型]                              → 纯类型，无描述无别名
    Annotated[类型, '描述']                      → 有描述，无别名
    Annotated[类型, '描述', '别名']              → 有描述 + 别名
    Annotated[类型, Param(desc=..., alias=...)]  → 关键字风格
"""
import sys

if sys.version_info >= (3, 9):
    from typing import Annotated, get_args, get_origin
else:
    try:
        from typing_extensions import Annotated, get_args, get_origin
    except ImportError:
        Annotated = None

        def get_args(tp):
            return getattr(tp, '__args__', ())

        def get_origin(tp):
            return getattr(tp, '__origin__', None)


class Param(object):
    """
    参数元数据描述器，用于 Annotated 内部。

    Parameters
    ----------
    desc : str, optional
        参数描述，显示在 CLI --help 和 Web UI 输入框中
    alias : str or list, optional
        CLI 短参数别名，如 'n' 自动转为 '-n'，'host-name' 转为 '--host-name'
    """

    def __init__(self, desc=None, alias=None):
        self.desc = desc
        if alias is None:
            self.aliases = []
        elif isinstance(alias, (list, tuple)):
            self.aliases = [_normalize_alias(a) for a in alias]
        else:
            self.aliases = [_normalize_alias(alias)]

    def __repr__(self):
        parts = []
        if self.desc:
            parts.append('desc={!r}'.format(self.desc))
        if self.aliases:
            parts.append('alias={!r}'.format(self.aliases))
        return 'Param({})'.format(', '.join(parts))


class _ArgMeta(object):
    """内部元数据容器，保存从 Annotated 中提取的描述和别名"""

    def __init__(self, desc=None, aliases=None):
        self.desc = desc
        self.aliases = aliases or []

    def __repr__(self):
        parts = []
        if self.desc:
            parts.append('desc={!r}'.format(self.desc))
        if self.aliases:
            parts.append('alias={!r}'.format(self.aliases))
        return '_ArgMeta({})'.format(', '.join(parts))


def _normalize_alias(alias):
    """将用户给的 alias 标准化为 CLI flag 格式"""
    s = str(alias)
    if s.startswith('-'):
        return s
    if len(s) == 1:
        return '-' + s
    return '--' + s


def unwrap_arg(hint):
    """
    解析类型注解，提取真实类型和元数据。

    支持:
    - Annotated[str, '描述']                     → (str, _ArgMeta(desc='描述'))
    - Annotated[str, '描述', 'n']                → (str, _ArgMeta(desc='描述', aliases=['-n']))
    - Annotated[str, Param(desc='描述', alias='n')]  → 同上
    - str                                        → (str, None)
    """
    if Annotated is not None and get_origin(hint) is Annotated:
        args = get_args(hint)
        real_type = args[0]

        for meta in args[1:]:
            if isinstance(meta, Param):
                return real_type, _ArgMeta(desc=meta.desc, aliases=list(meta.aliases))

        desc = None
        alias_val = None
        if len(args) > 1 and isinstance(args[1], str):
            desc = args[1]
        if len(args) > 2 and isinstance(args[2], str):
            alias_val = args[2]

        if desc is not None or alias_val is not None:
            aliases = [_normalize_alias(alias_val)] if alias_val else []
            return real_type, _ArgMeta(desc=desc, aliases=aliases)
        return real_type, None

    return hint, None
