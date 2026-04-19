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


def discover_commands(instance, base_cls, include_builtins=True, enable_exec=True,
                      allow_method_list=None, hide_method_list=None, command_prefix=''):
    """
    发现 instance 上所有应暴露为 CLI 子命令的方法，以及 sub_commands 中的子命令组。

    Parameters
    ----------
    include_builtins : bool
        是否包含基类内置命令（如 exec），顶层类为 True，子命令组为 False
    enable_exec : bool
        是否启用内置 exec 命令，由 Meta.enable_exec 控制
    allow_method_list : list[str] or None
        命令白名单。为空/None 表示不过滤；有值时仅暴露白名单命令。
        支持写法：['status', 'db.migrate', 'db/migrate', 'db migrate']。
    hide_method_list : list[str] or None
        命令黑名单。为空/None 表示不过滤；有值时隐藏指定命令。
        与 allow_method_list 互斥，同时配置时 allow_method_list 优先。
    command_prefix : str
        当前 discover 所在的命令路径前缀（内部递归使用）。

    返回: OrderedDict  { cmd_name: cmd_info_dict }
    """
    from collections import OrderedDict
    commands = OrderedDict()
    allow_set = _normalize_allow_method_set(allow_method_list)
    hide_set = _normalize_allow_method_set(hide_method_list) if not allow_set else set()
    current_prefix = _normalize_command_path(command_prefix)

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

        full_path = _join_command_path(current_prefix, name)
        if not _is_method_allowed(full_path, allow_set):
            continue
        if _is_method_hidden(full_path, hide_set):
            continue

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
        group_path = _join_command_path(current_prefix, group_name)
        if not _is_group_allowed(group_path, allow_set):
            continue
        if _is_group_hidden(group_path, hide_set):
            continue

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


def _normalize_allow_method_set(allow_method_list):
    """
    归一化 allow_method_list，返回 set。

    - None / [] / () / '' -> 空 set（表示不过滤）
    - str -> 视为单条规则
    - 路径分隔支持 '.', '/', 空格
    - CLI 风格 '-' 自动转为 '_'（与 Python 方法名对齐）
    """
    if allow_method_list is None:
        return set()

    if isinstance(allow_method_list, str):
        raw_items = [allow_method_list]
    elif isinstance(allow_method_list, (list, tuple, set)):
        raw_items = list(allow_method_list)
    else:
        raw_items = [str(allow_method_list)]

    normalized = set()
    for item in raw_items:
        p = _normalize_command_path(item)
        if p:
            normalized.add(p)
    return normalized


def _normalize_command_path(path):
    """将命令路径统一为 'group/sub/cmd' 形式（内部用 '_' 命名）。"""
    if path is None:
        return ''
    s = str(path).strip()
    if not s:
        return ''

    # 支持 db.migrate / db/migrate / db migrate
    s = s.replace('\\', '/').replace('.', '/').replace(' ', '/')
    while '//' in s:
        s = s.replace('//', '/')
    s = s.strip('/')
    if not s:
        return ''

    parts = []
    for part in s.split('/'):
        p = part.strip()
        if not p:
            continue
        parts.append(p.replace('-', '_'))
    return '/'.join(parts)


def _join_command_path(prefix, name):
    """拼接完整命令路径。"""
    p = _normalize_command_path(prefix)
    n = _normalize_command_path(name)
    if not p:
        return n
    if not n:
        return p
    return p + '/' + n


def _iter_ancestor_paths(path):
    """迭代 path 的祖先路径（不含自身），用于白名单祖先命中判断。"""
    p = _normalize_command_path(path)
    if not p:
        return []
    parts = p.split('/')
    ancestors = []
    # issue/list -> ['issue']
    for i in range(1, len(parts)):
        ancestors.append('/'.join(parts[:i]))
    return ancestors


def _is_method_allowed(method_path, allow_set):
    """方法是否在白名单内（支持父组命中）。"""
    if not allow_set:
        return True

    p = _normalize_command_path(method_path)
    if p in allow_set:
        return True

    # allow=['issue'] 时，issue 下所有方法可见
    for anc in _iter_ancestor_paths(p):
        if anc in allow_set:
            return True
    return False


def _is_group_allowed(group_path, allow_set):
    """命令组是否需要暴露（自身命中、祖先命中、或有子命令命中）。"""
    if not allow_set:
        return True

    p = _normalize_command_path(group_path)
    if p in allow_set:
        return True

    # allow=['admin']，admin/ops 也应可见
    for anc in _iter_ancestor_paths(p):
        if anc in allow_set:
            return True

    # allow=['issue/list']，issue 组需保留用于路由到子命令
    prefix = p + '/'
    for item in allow_set:
        if item.startswith(prefix):
            return True
    return False


def _is_method_hidden(method_path, hide_set):
    """方法是否在黑名单内（精确命中或祖先组被隐藏）。"""
    if not hide_set:
        return False
    p = _normalize_command_path(method_path)
    if p in hide_set:
        return True
    for anc in _iter_ancestor_paths(p):
        if anc in hide_set:
            return True
    return False


def _is_group_hidden(group_path, hide_set):
    """命令组是否整体被隐藏（自身命中或祖先命中）。"""
    if not hide_set:
        return False
    p = _normalize_command_path(group_path)
    if p in hide_set:
        return True
    for anc in _iter_ancestor_paths(p):
        if anc in hide_set:
            return True
    return False


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
