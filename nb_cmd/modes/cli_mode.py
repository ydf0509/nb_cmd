# -*- coding: utf-8 -*-
"""
CLI 模式 —— 默认的命令行交互模式。
"""
import asyncio
import inspect

from ..core.discovery import discover_commands
from ..core.parser import build_parser, reassign_positionals
from ..core.type_utils import convert_value
from ..core.result_handler import handle_cli_result


def _run_method(method, kwargs):
    """执行方法，自动处理同步和异步函数"""
    result = method(**kwargs)
    if inspect.iscoroutine(result):
        result = asyncio.run(result)
    return result


def _run_method_with_timeout(method, kwargs, timeout):
    """执行方法并在超时后抛出 TimeoutError（timeout=0 表示不限）"""
    if timeout <= 0:
        return _run_method(method, kwargs)

    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(_run_method, method, kwargs)
        try:
            return future.result(timeout=timeout)
        except concurrent.futures.TimeoutError:
            raise TimeoutError(
                '命令执行超时（{} 秒）。可通过 Meta.timeout 调整超时时间。'.format(timeout)
            )


def run_cli(instance, base_cls, args=None):
    """
    以 CLI 模式执行 NbCmd 实例。

    Parameters
    ----------
    instance : NbCmd 实例
    base_cls : NbCmd 类（用于过滤基类方法）
    args : list, optional  命令行参数列表，默认 sys.argv[1:]
    """
    meta = getattr(instance.__class__, 'Meta', type('Meta', (), {}))
    _enable_exec = getattr(meta, 'enable_exec', True)
    _allow_methods = getattr(meta, 'allow_method_list', None)
    _hide_methods = getattr(meta, 'hide_method_list', None)
    _timeout = getattr(meta, 'timeout', 0)
    commands = discover_commands(instance, base_cls, enable_exec=_enable_exec,
                                 allow_method_list=_allow_methods,
                                 hide_method_list=_hide_methods)
    parser = build_parser(instance, commands, meta, base_cls=base_cls,
                          allow_method_list=_allow_methods,
                          hide_method_list=_hide_methods)

    parsed = parser.parse_args(args)
    reassign_positionals(parsed)

    _apply_init_args(instance, parsed)
    _ensure_nbctx(instance)

    command_name = getattr(parsed, '_nb_command', None)
    if not command_name:
        parser.print_help()
        return

    python_name = command_name.replace('-', '_')

    if python_name in commands and commands[python_name].get('is_group'):
        _run_group_command(instance, commands[python_name], parsed, base_cls, depth=1,
                           allow_method_list=_allow_methods, hide_method_list=_hide_methods,
                           command_prefix=python_name)
        return

    if python_name not in commands:
        parser.print_help()
        return

    cmd_info = commands[python_name]
    method = cmd_info['method']
    kwargs = _extract_kwargs(method, cmd_info, parsed)

    instance.before_run()
    try:
        result = _run_method_with_timeout(method, kwargs, _timeout)
        handle_cli_result(result)
    except Exception as e:
        instance.on_error(command_name, e)
        raise
    finally:
        instance.after_run()


def _apply_init_args(instance, parsed):
    """
    将解析出的全局选项（__init__参数）应用到实例上。

    通过重新调用 __init__（带 CLI 解析值）来更新实例状态，
    这样用户在 __init__ 中直接赋值 self.nbctx = XxxCtx(...) 也能拿到正确的 CLI 值。
    """
    init_method = instance.__class__.__init__
    if init_method is object.__init__:
        return

    sig = inspect.signature(init_method)
    kwargs = {}
    for param_name in sig.parameters:
        if param_name == 'self':
            continue
        attr_name = '_nb_init_' + param_name
        if hasattr(parsed, attr_name):
            cli_val = getattr(parsed, attr_name)
            if cli_val is not None:
                kwargs[param_name] = cli_val
            elif hasattr(instance, param_name):
                kwargs[param_name] = getattr(instance, param_name)
        elif hasattr(instance, param_name):
            kwargs[param_name] = getattr(instance, param_name)

    instance.__init__(**kwargs)


def _extract_kwargs(method, cmd_info, parsed):
    """从 parsed namespace 中提取方法所需的关键字参数"""
    sig = cmd_info['signature']
    hints = cmd_info.get('type_hints', {})
    kwargs = {}

    for param_name, param in sig.parameters.items():
        if param_name == 'self':
            continue

        raw_value = getattr(parsed, param_name, None)
        param_type = hints.get(param_name, str)
        converted = convert_value(raw_value, param_type)
        kwargs[param_name] = converted

    return kwargs


def _ensure_nbctx(instance):
    """确保实例的 nbctx 已初始化（调用 make_nbctx）"""
    if instance.nbctx is None:
        ctx = instance.make_nbctx()
        if ctx is not None:
            instance.nbctx = ctx


def _inject_nbctx(parent, child):
    """将父级的 nbctx 注入到子命令组实例"""
    parent_ctx = parent.nbctx
    if parent_ctx is not None:
        child.nbctx = parent_ctx


def _run_group_command(instance, group_info, parsed, base_cls, depth=1,
                       allow_method_list=None, hide_method_list=None, command_prefix=''):
    """执行子命令组中的命令"""
    group_cls = group_info['cls']
    group_kwargs = group_info.get('init_kwargs', {})

    try:
        group_instance = group_cls(**group_kwargs) if group_kwargs else group_cls()
    except TypeError:
        group_instance = group_cls.__new__(group_cls)

    _inject_nbctx(instance, group_instance)

    dest = '_nb_sub_command' if depth == 1 else '_nb_sub_command_{}'.format(depth)
    sub_command = getattr(parsed, dest, None)
    if not sub_command:
        print('请指定子命令。使用 --help 查看可用子命令。')
        return

    sub_python_name = sub_command.replace('-', '_')
    sub_commands = discover_commands(group_instance, base_cls,
                                     allow_method_list=allow_method_list,
                                     hide_method_list=hide_method_list,
                                     command_prefix=command_prefix)

    if sub_python_name in sub_commands and sub_commands[sub_python_name].get('is_group'):
        next_prefix = '{}/{}'.format(command_prefix, sub_python_name) if command_prefix else sub_python_name
        _run_group_command(group_instance, sub_commands[sub_python_name], parsed, base_cls,
                           depth=depth + 1, allow_method_list=allow_method_list,
                           hide_method_list=hide_method_list,
                           command_prefix=next_prefix)
        return

    if sub_python_name not in sub_commands:
        print('未知子命令: {}'.format(sub_command))
        return

    cmd_info = sub_commands[sub_python_name]
    method = cmd_info['method']
    kwargs = _extract_kwargs(method, cmd_info, parsed)

    meta = getattr(instance.__class__, 'Meta', type('Meta', (), {}))
    _timeout = getattr(meta, 'timeout', 0)

    group_instance.before_run()
    try:
        result = _run_method_with_timeout(method, kwargs, _timeout)
        handle_cli_result(result)
    except Exception as e:
        group_instance.on_error(sub_command, e)
        raise
    finally:
        group_instance.after_run()
