# -*- coding: utf-8 -*-
"""
命令发现模块 —— 通过反射发现类中的所有公有方法，自动转换为子命令。
"""
import sys
import inspect

if sys.version_info >= (3, 11):
    from typing import get_type_hints
elif sys.version_info >= (3, 9):
    from typing import get_type_hints
else:
    try:
        from typing_extensions import get_type_hints
    except ImportError:
        from typing import get_type_hints as _get_type_hints

        def get_type_hints(func, **kwargs):
            kwargs.pop('include_extras', None)
            return _get_type_hints(func, **kwargs)

from .arg import unwrap_arg


def discover_commands(instance, base_cls, include_builtins=True, enable_exec=True):
    """
    发现 instance 上所有应暴露为 CLI 子命令的方法，以及 sub_commands 中的子命令组。

    Parameters
    ----------
    include_builtins : bool
        是否包含基类内置命令（如 exec），顶层类为 True，子命令组为 False
    enable_exec : bool
        是否启用内置 exec 命令，由 Meta.enable_exec 控制

    返回: OrderedDict  { cmd_name: cmd_info_dict }
    """
    from collections import OrderedDict
    commands = OrderedDict()

    _BUILTIN_COMMANDS = {'exec'} if (include_builtins and enable_exec) else set()
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
            hints = get_type_hints(attr, include_extras=True)
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
    for group_name, group_val in sub_cmds.items():
        if inspect.isclass(group_val) and issubclass(group_val, base_cls):
            commands[group_name] = {
                'cls': group_val,
                'doc': (inspect.getdoc(group_val) or "").split('\n')[0],
                'is_group': True,
                'init_kwargs': {},
            }
        elif isinstance(group_val, base_cls):
            group_cls = group_val.__class__
            commands[group_name] = {
                'cls': group_cls,
                'doc': (inspect.getdoc(group_cls) or "").split('\n')[0],
                'is_group': True,
                'init_kwargs': _extract_init_kwargs(group_val),
            }

    return commands


def _extract_init_kwargs(instance):
    """从实例上提取 __init__ 参数的当前值，用于子命令组的重新实例化"""
    cls = instance.__class__
    init_method = cls.__init__
    if init_method is object.__init__:
        return {}
    sig = inspect.signature(init_method)
    kwargs = {}
    for pname, param in sig.parameters.items():
        if pname == 'self':
            continue
        if hasattr(instance, pname):
            kwargs[pname] = getattr(instance, pname)
    return kwargs
