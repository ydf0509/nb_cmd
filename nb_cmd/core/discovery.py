# -*- coding: utf-8 -*-
"""
命令发现模块 —— 通过反射发现类中的所有公有方法，自动转换为子命令。
"""
import inspect

from typing import get_type_hints

from .arg import unwrap_arg


def discover_commands(instance, base_cls, include_builtins=True):
    """
    发现 instance 上所有应暴露为 CLI 子命令的方法，以及 sub_commands 中的子命令组。

    Parameters
    ----------
    include_builtins : bool
        是否包含基类内置命令（如 exec），顶层类为 True，子命令组为 False

    返回: OrderedDict  { cmd_name: cmd_info_dict }
    """
    from collections import OrderedDict
    commands = OrderedDict()

    _BUILTIN_COMMANDS = {'exec'} if include_builtins else set()
    base_methods = set(dir(base_cls)) - _BUILTIN_COMMANDS

    for name in sorted(dir(instance)):
        if name.startswith('_'):
            continue
        if name in base_methods:
            continue
        if name in ('sub_commands',):
            continue

        attr = getattr(instance, name, None)
        if attr is None:
            continue
        if not callable(attr):
            continue
        if not (inspect.ismethod(attr) or inspect.isfunction(attr)):
            continue

        sig = inspect.signature(attr)
        doc = inspect.getdoc(attr) or ""

        try:
            hints = get_type_hints(attr)
        except Exception:
            hints = {}

        real_hints = {}
        arg_meta = {}
        missing_types = []

        for param_name, param in sig.parameters.items():
            if param_name == 'self':
                continue
            raw_hint = hints.get(param_name)
            if raw_hint is None:
                anno = param.annotation
                if anno is not inspect.Parameter.empty:
                    raw_hint = anno
            if raw_hint is None:
                missing_types.append(param_name)
                continue
            real_type, arg_inst = unwrap_arg(raw_hint)
            real_hints[param_name] = real_type
            if arg_inst is not None:
                arg_meta[param_name] = arg_inst

        if missing_types:
            cls_name = instance.__class__.__name__
            raise TypeError(
                '{cls}.{method}() 的参数 {params} 缺少类型注解。'
                'nb_cmd 要求所有公有方法的参数必须声明类型，例如: '
                'def {method}(self, {example}: str)'.format(
                    cls=cls_name,
                    method=name,
                    params=', '.join("'{}'".format(p) for p in missing_types),
                    example=missing_types[0],
                )
            )

        commands[name] = {
            'method': attr,
            'signature': sig,
            'type_hints': real_hints,
            'arg_meta': arg_meta,
            'doc': doc.split('\n')[0],
            'full_doc': doc,
            'is_group': False,
        }

    sub_cmds = getattr(instance.__class__, 'sub_commands', {})
    for group_name, group_cls in sub_cmds.items():
        if inspect.isclass(group_cls) and issubclass(group_cls, base_cls):
            commands[group_name] = {
                'cls': group_cls,
                'doc': (inspect.getdoc(group_cls) or "").split('\n')[0],
                'is_group': True,
            }

    return commands
