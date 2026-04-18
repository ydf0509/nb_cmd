# -*- coding: utf-8 -*-
"""
argparse 解析器自动构建模块。
根据方法签名自动生成 argparse.ArgumentParser。
"""
import argparse
import inspect

from .type_utils import (
    get_argparse_type, get_nargs, get_choices,
    is_optional, unwrap_optional, type_display_name,
)


class _RawDefaultsHelpFormatter(argparse.RawDescriptionHelpFormatter,
                                argparse.ArgumentDefaultsHelpFormatter):
    pass


def build_parser(instance, commands, meta):
    """
    为顶层 NbCmd 实例构建完整的 argparse 解析器。

    Parameters
    ----------
    instance : NbCmd 实例
    commands : dict  由 discover_commands 返回
    meta : Meta 配置类
    """
    description = inspect.getdoc(instance) or instance.__class__.__name__
    version = getattr(meta, 'version', '0.0.1')

    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=_RawDefaultsHelpFormatter,
        add_help=False,
    )

    sys_group = parser.add_argument_group('system params')
    sys_group.add_argument('-h', '--help', action='help',
                           default=argparse.SUPPRESS, help='显示帮助信息')
    sys_group.add_argument('--version', action='version', version=version)
    sys_group.add_argument('--full-help', '-fh', action='store_true',
                           default=False, help='显示所有命令的完整参数详情')
    sys_group.add_argument('--web', action='store_true',
                           help='以Web UI + REST API模式启动')
    sys_group.add_argument('--web-port', type=int, default=None,
                           help='Web UI 服务端口（用于 --web）')

    init_group = parser.add_argument_group('init params')
    _add_init_global_options(init_group, instance)

    subparsers = parser.add_subparsers(dest='_nb_command',
                                       title='commands', help='可用命令')

    for cmd_name, cmd_info in commands.items():
        cli_name = cmd_name.replace('_', '-')

        if cmd_info.get('is_group'):
            group_cls = cmd_info['cls']
            group_doc = cmd_info.get('doc', '')
            group_kwargs = cmd_info.get('init_kwargs', {})
            sub = subparsers.add_parser(
                cli_name,
                help=group_doc + '（子命令组）' if group_doc else '子命令组',
                description=group_doc,
                formatter_class=_RawDefaultsHelpFormatter,
            )
            _build_group_subparser(sub, group_cls, instance.__class__, group_kwargs)
        else:
            param_hint = _build_param_hint(cmd_info)
            help_text = cmd_info['doc']
            if param_hint:
                help_text = '{} {}'.format(help_text, param_hint)
            sub = subparsers.add_parser(
                cli_name,
                help=help_text,
                description=cmd_info['full_doc'],
                formatter_class=_RawDefaultsHelpFormatter,
            )
            _add_method_arguments(sub, cmd_info, meta)

    return parser


def _build_param_hint(cmd_info):
    """为子命令生成简短的参数提示，显示在顶层 --help 的子命令描述后面"""
    sig = cmd_info['signature']
    arg_meta = cmd_info.get('arg_meta', {})
    parts = []
    for pname, param in sig.parameters.items():
        if pname == 'self':
            continue
        has_default = param.default is not inspect.Parameter.empty
        arg_inst = arg_meta.get(pname)
        cli_name = '--' + pname.replace('_', '-')
        if arg_inst and arg_inst.aliases:
            short = arg_inst.aliases[0]
            flag = '{}/{}'.format(short, cli_name)
        else:
            flag = pname.upper() if not has_default else cli_name
        if has_default and param.default is not False and param.default is not True:
            parts.append('{}={}'.format(flag, param.default))
        else:
            parts.append(flag)
    if not parts:
        return ''
    return '({})'.format(', '.join(parts))


def print_full_help(instance, base_cls):
    """打印所有命令的完整参数详情"""
    import sys as _sys
    from .discovery import discover_commands

    meta = getattr(instance.__class__, 'Meta', type('Meta', (), {}))
    _enable_exec = getattr(meta, 'enable_exec', True)
    commands = discover_commands(instance, base_cls, enable_exec=_enable_exec)
    description = inspect.getdoc(instance) or instance.__class__.__name__
    version = getattr(meta, 'version', '0.0.1')

    w = _sys.stdout.write
    line = '=' * 56

    w('\n{}\n  {} v{}\n  {}\n{}\n\n'.format(
        line, instance.__class__.__name__, version, description, line))

    w('system params:\n')
    w('    {:<24s} {}\n'.format('--help, -h', '显示简要帮助'))
    w('    {:<24s} {}\n'.format('--full-help, -fh', '显示本完整帮助'))
    w('    {:<24s} {}\n'.format('--version', '显示版本号'))
    w('    {:<24s} {}\n'.format('--web', '以Web UI + REST API模式启动'))
    w('    {:<24s} {}\n'.format('--web-port PORT', 'Web UI 服务端口（用于 --web）'))
    w('\n')

    has_init_params = _has_init_params(instance)
    if has_init_params:
        w('init params:\n')
        _print_init_params(w, instance)
        w('\n')

    w('{}\n'.format('-' * 56))
    _print_group_commands(w, commands, base_cls, prefix='')
    _sys.stdout.flush()


def _print_group_commands(w, commands, base_cls, prefix=''):
    """递归打印命令组及其所有子命令（含嵌套组）"""
    from .discovery import discover_commands

    for cmd_name, cmd_info in commands.items():
        cli_name = cmd_name.replace('_', '-')
        full_name = '{} {}'.format(prefix, cli_name).strip() if prefix else cli_name

        if cmd_info.get('is_group'):
            w('{} \033[36m[子命令组]\033[0m  {}\n'.format(
                full_name, cmd_info.get('doc', '')))
            group_cls = cmd_info['cls']
            group_kwargs = cmd_info.get('init_kwargs', {})
            try:
                group_inst = group_cls(**group_kwargs) if group_kwargs else group_cls()
            except TypeError:
                group_inst = group_cls.__new__(group_cls)
            group_cmds = discover_commands(group_inst, base_cls,
                                           include_builtins=False)
            _print_group_commands(w, group_cmds, base_cls, prefix=full_name)
            w('\n')
        else:
            if prefix:
                w('\n  {} — {}\n'.format(full_name, cmd_info.get('doc', '')))
            else:
                w('{} — {}\n'.format(full_name, cmd_info.get('doc', '')))
            _print_params(w, cmd_info)
            if not prefix:
                w('\n')


def _print_params(write_fn, cmd_info):
    """打印一个命令的完整参数列表"""
    sig = cmd_info['signature']
    hints = cmd_info.get('type_hints', {})
    arg_meta = cmd_info.get('arg_meta', {})

    for pname, param in sig.parameters.items():
        if pname == 'self':
            continue
        ptype = hints.get(pname, str)
        real_type = unwrap_optional(ptype) if is_optional(ptype) else ptype
        type_name = type_display_name(real_type)
        has_default = param.default is not inspect.Parameter.empty
        arg_inst = arg_meta.get(pname)
        desc = arg_inst.desc if arg_inst and arg_inst.desc else ''

        cli_flag = '--' + pname.replace('_', '-')
        if arg_inst and arg_inst.aliases:
            flags_str = '{}, {}'.format(cli_flag, ', '.join(arg_inst.aliases))
        else:
            if not has_default:
                flags_str = pname.upper()
            else:
                flags_str = cli_flag

        if has_default:
            meta_str = '({}, 默认: {})'.format(type_name, param.default)
        else:
            meta_str = '({}, 必填)'.format(type_name)

        if desc:
            write_fn('    {:<24s} {}  {}\n'.format(flags_str, desc, meta_str))
        else:
            write_fn('    {:<24s} {}\n'.format(flags_str, meta_str))


def _has_init_params(instance):
    """判断实例的 __init__ 是否有自定义全局参数"""
    init_method = instance.__class__.__init__
    if init_method is object.__init__:
        return False
    sig = inspect.signature(init_method)
    for pname, param in sig.parameters.items():
        if pname != 'self':
            return True
    return False


def _print_init_params(write_fn, instance):
    """打印 __init__ 全局选项的详情（用于 --full-help）"""
    from .arg import unwrap_arg

    init_method = instance.__class__.__init__
    if init_method is object.__init__:
        return

    sig = inspect.signature(init_method)

    for pname, param in sig.parameters.items():
        if pname == 'self':
            continue

        has_default = param.default is not inspect.Parameter.empty
        if has_default:
            default_val = param.default
        else:
            default_val = getattr(instance, pname, None)

        raw_hint = param.annotation
        if raw_hint is inspect.Parameter.empty:
            if default_val is not None:
                raw_hint = type(default_val)
            else:
                raw_hint = str

        real_type, arg_inst = unwrap_arg(raw_hint)
        type_name = type_display_name(real_type)
        desc = arg_inst.desc if arg_inst and arg_inst.desc else ''

        cli_flag = '--' + pname.replace('_', '-')
        if arg_inst and arg_inst.aliases:
            flags_str = '{}, {}'.format(cli_flag, ', '.join(arg_inst.aliases))
        else:
            flags_str = cli_flag

        meta_str = '(全局, {}, 默认: {})'.format(type_name, default_val)

        if desc:
            write_fn('    {:<24s} {}  {}\n'.format(flags_str, desc, meta_str))
        else:
            write_fn('    {:<24s} {}\n'.format(flags_str, meta_str))


def _add_init_global_options(parser, instance):
    """将 __init__ 中的自定义参数变为全局选项，支持 Arg 描述器"""
    from .arg import unwrap_arg

    init_method = instance.__class__.__init__
    if init_method is object.__init__:
        return

    sig = inspect.signature(init_method)

    for param_name, param in sig.parameters.items():
        if param_name == 'self':
            continue

        has_default = param.default is not inspect.Parameter.empty
        if has_default:
            default_val = param.default
        else:
            default_val = getattr(instance, param_name, None)

        raw_hint = param.annotation
        if raw_hint is inspect.Parameter.empty:
            if default_val is not None:
                raw_hint = type(default_val)
            else:
                raw_hint = str

        param_type, arg_inst = unwrap_arg(raw_hint)

        cli_flag = '--' + param_name.replace('_', '-')
        extra_flags = arg_inst.aliases if arg_inst and arg_inst.aliases else []
        desc = arg_inst.desc if arg_inst and arg_inst.desc else None

        metavar = param_name.upper()
        if param_type is bool:
            flags = [cli_flag] + extra_flags
            auto_help = '(全局选项, bool, 默认: {})'.format(default_val)
            parser.add_argument(
                *flags,
                action='store_true' if not default_val else 'store_false',
                default=default_val,
                dest='_nb_init_' + param_name,
                help='{} {}'.format(desc, auto_help) if desc else auto_help,
            )
        else:
            flags = [cli_flag] + extra_flags
            auto_help = '(全局选项, {}, 默认: {})'.format(
                type_display_name(param_type), default_val)
            parser.add_argument(
                *flags,
                type=get_argparse_type(param_type),
                default=default_val,
                dest='_nb_init_' + param_name,
                metavar=metavar,
                help='{} {}'.format(desc, auto_help) if desc else auto_help,
            )


def _add_method_arguments(sub_parser, cmd_info, meta):
    """根据方法签名向 subparser 添加参数"""
    sig = cmd_info['signature']
    hints = cmd_info.get('type_hints', {})
    arg_meta = cmd_info.get('arg_meta', {})
    method_name = cmd_info['method'].__name__

    aliases_map = getattr(meta, 'aliases', {})

    for param_name, param in sig.parameters.items():
        if param_name == 'self':
            continue

        param_type = hints.get(param_name, str)
        if is_optional(param_type):
            param_type_unwrapped = unwrap_optional(param_type)
        else:
            param_type_unwrapped = param_type

        has_default = param.default is not inspect.Parameter.empty
        is_keyword_only = param.kind == inspect.Parameter.KEYWORD_ONLY

        arg_inst = arg_meta.get(param_name)
        if arg_inst and arg_inst.aliases:
            extra_flags = list(arg_inst.aliases)
        else:
            alias_key = '{}.{}'.format(method_name, param_name)
            extra_flags = aliases_map.get(alias_key, [])

        desc = arg_inst.desc if arg_inst and arg_inst.desc else None

        cli_flag = '--' + param_name.replace('_', '-')
        nargs = get_nargs(param_type)
        choices = get_choices(param_type)
        ap_type = get_argparse_type(param_type)
        type_name = type_display_name(param_type_unwrapped)

        if param_type_unwrapped is bool:
            flags = [cli_flag] + extra_flags
            auto_help = '(bool, 默认: {})'.format(param.default if has_default else False)
            sub_parser.add_argument(
                *flags,
                action='store_true' if not (has_default and param.default) else 'store_false',
                default=param.default if has_default else False,
                dest=param_name,
                help='{} {}'.format(desc, auto_help) if desc else auto_help,
            )
        elif has_default or is_keyword_only:
            flags = [cli_flag] + extra_flags
            auto_help = '({}, 默认: {})'.format(type_name, param.default if has_default else 'None')
            kwargs = dict(
                type=ap_type,
                default=param.default if has_default else None,
                dest=param_name,
                help='{} {}'.format(desc, auto_help) if desc else auto_help,
            )
            if nargs is not None:
                kwargs['nargs'] = nargs
            if choices is not None:
                kwargs['choices'] = choices
            sub_parser.add_argument(*flags, **kwargs)
        else:
            auto_help = '({}, 必填)'.format(type_name)
            if extra_flags:
                flags = [cli_flag] + extra_flags
                kwargs = dict(
                    type=ap_type,
                    required=True,
                    dest=param_name,
                    help='{} {}'.format(desc, auto_help) if desc else auto_help,
                )
                if nargs is not None:
                    kwargs['nargs'] = nargs
                if choices is not None:
                    kwargs['choices'] = choices
                sub_parser.add_argument(*flags, **kwargs)
            else:
                kwargs = dict(
                    type=ap_type,
                    help='{} {}'.format(desc, auto_help) if desc else auto_help,
                )
                if nargs is not None:
                    kwargs['nargs'] = nargs
                if choices is not None:
                    kwargs['choices'] = choices
                sub_parser.add_argument(param_name, **kwargs)


def _build_group_subparser(parent_parser, group_cls, base_cls, init_kwargs=None):
    """递归为子命令组构建 subparser"""
    from .discovery import discover_commands

    if init_kwargs:
        group_instance = group_cls(**init_kwargs)
    else:
        group_instance = group_cls.__new__(group_cls)
        if hasattr(group_cls.__init__, '__func__') and group_cls.__init__ is not object.__init__:
            try:
                group_cls.__init__(group_instance)
            except TypeError:
                pass

    group_commands = discover_commands(group_instance, base_cls)

    if not group_commands:
        return

    sub_group_meta = getattr(group_cls, 'Meta', type('Meta', (), {}))

    group_subparsers = parent_parser.add_subparsers(dest='_nb_sub_command', help='可用子命令')

    for cmd_name, cmd_info in group_commands.items():
        cli_name = cmd_name.replace('_', '-')

        if cmd_info.get('is_group'):
            nested_cls = cmd_info['cls']
            nested_doc = cmd_info.get('doc', '')
            nested_kwargs = cmd_info.get('init_kwargs', {})
            nested_sub = group_subparsers.add_parser(
                cli_name,
                help=nested_doc + '（子命令组）' if nested_doc else '子命令组',
                description=nested_doc,
                formatter_class=_RawDefaultsHelpFormatter,
            )
            _build_group_subparser(nested_sub, nested_cls, base_cls, nested_kwargs)
        else:
            sub = group_subparsers.add_parser(
                cli_name,
                help=cmd_info['doc'],
                description=cmd_info['full_doc'],
                formatter_class=_RawDefaultsHelpFormatter,
            )
            _add_method_arguments(sub, cmd_info, sub_group_meta)
