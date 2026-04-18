# -*- coding: utf-8 -*-
"""
CLI 模式 —— 默认的命令行交互模式。
"""
import asyncio
import inspect

from ..core.discovery import discover_commands
from ..core.parser import build_parser
from ..core.type_utils import convert_value
from ..core.result_handler import handle_cli_result


def _run_method(method, kwargs):
    """执行方法，自动处理同步和异步函数"""
    result = method(**kwargs)
    if inspect.iscoroutine(result):
        result = asyncio.run(result)
    return result


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
    commands = discover_commands(instance, base_cls, enable_exec=_enable_exec)
    parser = build_parser(instance, commands, meta)

    parsed = parser.parse_args(args)

    _apply_init_args(instance, parsed)

    command_name = getattr(parsed, '_nb_command', None)
    if not command_name:
        parser.print_help()
        return

    python_name = command_name.replace('-', '_')

    if python_name in commands and commands[python_name].get('is_group'):
        _run_group_command(instance, commands[python_name], parsed, base_cls)
        return

    if python_name not in commands:
        parser.print_help()
        return

    cmd_info = commands[python_name]
    method = cmd_info['method']
    kwargs = _extract_kwargs(method, cmd_info, parsed)

    instance.before_run()
    try:
        result = _run_method(method, kwargs)
        handle_cli_result(result)
    except Exception as e:
        instance.on_error(command_name, e)
        raise
    finally:
        instance.after_run()


def _apply_init_args(instance, parsed):
    """将解析出的全局选项（__init__参数）应用到实例上"""
    init_method = instance.__class__.__init__
    if init_method is object.__init__:
        return

    sig = inspect.signature(init_method)
    for param_name in sig.parameters:
        if param_name == 'self':
            continue
        attr_name = '_nb_init_' + param_name
        if hasattr(parsed, attr_name):
            val = getattr(parsed, attr_name)
            if val is not None:
                setattr(instance, param_name, val)


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


def _run_group_command(instance, group_info, parsed, base_cls):
    """执行子命令组中的命令"""
    group_cls = group_info['cls']
    group_kwargs = group_info.get('init_kwargs', {})

    try:
        group_instance = group_cls(**group_kwargs) if group_kwargs else group_cls()
    except TypeError:
        group_instance = group_cls.__new__(group_cls)

    sub_command = getattr(parsed, '_nb_sub_command', None)
    if not sub_command:
        print('请指定子命令。使用 --help 查看可用子命令。')
        return

    sub_python_name = sub_command.replace('-', '_')
    sub_commands = discover_commands(group_instance, base_cls)

    if sub_python_name in sub_commands and sub_commands[sub_python_name].get('is_group'):
        _run_group_command(group_instance, sub_commands[sub_python_name], parsed, base_cls)
        return

    if sub_python_name not in sub_commands:
        print('未知子命令: {}'.format(sub_command))
        return

    cmd_info = sub_commands[sub_python_name]
    method = cmd_info['method']
    kwargs = _extract_kwargs(method, cmd_info, parsed)

    group_instance.before_run()
    try:
        result = _run_method(method, kwargs)
        handle_cli_result(result)
    except Exception as e:
        group_instance.on_error(sub_command, e)
        raise
    finally:
        group_instance.after_run()
