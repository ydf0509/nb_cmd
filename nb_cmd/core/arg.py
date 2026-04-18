# -*- coding: utf-8 -*-
"""
Arg —— 参数描述器，为方法参数附加描述和别名。

用法::

    from nb_cmd import NbCmd, Arg

    class MyTool(NbCmd):
        def greet(self, name: Arg(str, '要问候的人名', alias='n'),
                  times: Arg(int, '问候次数', alias='t') = 1):
            ...
"""


class Arg(object):
    """
    参数元数据描述器。

    Parameters
    ----------
    type_ : type
        参数的真实类型（str, int, bool, Enum, List[str] 等）
    desc : str, optional
        参数描述，显示在 CLI --help 和 Web UI 输入框中
    alias : str or list, optional
        CLI 短参数别名，如 'n' 自动转为 '-n'，'host-name' 转为 '--host-name'
    """

    def __init__(self, type_, desc=None, alias=None):
        self.type = type_
        self.desc = desc
        if alias is None:
            self.aliases = []
        elif isinstance(alias, (list, tuple)):
            self.aliases = [_normalize_alias(a) for a in alias]
        else:
            self.aliases = [_normalize_alias(alias)]

    def __repr__(self):
        parts = [self.type.__name__ if hasattr(self.type, '__name__') else str(self.type)]
        if self.desc:
            parts.append('desc={!r}'.format(self.desc))
        if self.aliases:
            parts.append('alias={!r}'.format(self.aliases))
        return 'Arg({})'.format(', '.join(parts))


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
    如果 hint 是 Arg 实例，返回 (real_type, arg_instance)；
    否则返回 (hint, None)。
    """
    if isinstance(hint, Arg):
        return hint.type, hint
    return hint, None
