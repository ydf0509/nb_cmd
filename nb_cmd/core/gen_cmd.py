# -*- coding: utf-8 -*-
"""
命令行示例生成器 —— 自动生成 CLI 用法示例和完整文档。

用法::

    from nb_cmd import CmdGen

    g = CmdGen(MyApp, script='app.py')
    print(g.cmd(DbTool.migrate))
    print(g.doc())
"""
import sys
import inspect

from .discovery import discover_commands


class CmdGen(object):
    """
    命令行示例生成器。

    Parameters
    ----------
    entry_cls : class
        顶层入口类，如 MyApp
    script : str, optional
        脚本名。默认用 sys.argv[0]。
    python : str, optional
        Python 解释器路径。默认用 sys.executable（当前解释器完整路径）。
    fmt : str
        输出格式: 'text' (纯文本) | 'markdown' (markdown 代码块)
    """

    def __init__(self, entry_cls, script=None, python=None, fmt='text'):
        self.entry_cls = entry_cls
        self.script = script or _get_script_name()
        self.python = python or sys.executable
        self.fmt = fmt
        self._base_cls = _find_base_cls(entry_cls)
        self._allow_methods = _get_allow_method_list(entry_cls)

    def cmd(self, method):
        """
        生成单个方法的 CLI 命令行示例。

        Parameters
        ----------
        method : unbound method
            目标方法，如 DbTool.migrate

        Returns
        -------
        str
            生成的命令行示例字符串
        """
        method_name = method.__name__
        method_cls = _get_method_class(method)

        global_args = _format_init_args(self.entry_cls)
        path = _find_command_path(self.entry_cls, method_cls, self._base_cls)

        method_args = _format_method_args(method)
        cmd_name = method_name.replace('_', '-')

        parts = [self.python, self.script]
        if global_args:
            parts.append(global_args)
        if path:
            parts.append(path)
        parts.append(cmd_name)
        if method_args:
            parts.append(method_args)

        cmd_line = ' '.join(parts)
        return _apply_fmt(cmd_line, self.fmt)

    def doc(self, file=None):
        """
        生成入口类的完整命令行文档。

        包含完整帮助信息和每个命令的可复制命令行示例。
        当 fmt='markdown' 或 file 以 .md 结尾时，输出高质量 Markdown 文档。

        Parameters
        ----------
        file : str, optional
            输出文件路径。传入后自动写入文件并返回文件路径。

        Returns
        -------
        str
            生成的完整文档字符串（传了 file 时同时写入文件）
        """
        use_md = self.fmt == 'markdown'
        if not use_md and file and file.endswith('.md'):
            use_md = True

        if use_md:
            text = self._build_md_doc()
        else:
            text = self._build_text_doc()

        if file is not None:
            import os
            dir_name = os.path.dirname(file)
            if dir_name:
                os.makedirs(dir_name, exist_ok=True)
            with open(file, 'w', encoding='utf-8') as f:
                f.write(text)

        return text

    def _build_text_doc(self):
        """构建纯文本格式的完整文档"""
        from .parser import get_full_help_text

        meta = getattr(self.entry_cls, 'Meta', None)
        app_name = getattr(meta, 'name', self.entry_cls.__name__) if meta else self.entry_cls.__name__

        instance = _safe_instantiate(self.entry_cls)
        full_help = get_full_help_text(instance, self._base_cls)

        lines = [full_help.rstrip(), '']
        lines.append('{} 命令行示例'.format(app_name))
        lines.append('=' * (len(app_name) + 14))

        global_args = _format_init_args(self.entry_cls)
        commands = discover_commands(instance, self._base_cls,
                                     include_builtins=False, enable_exec=False,
                                     allow_method_list=self._allow_methods)
        _collect_text_doc(commands, self._base_cls, self.script, self.python,
                          global_args, '', lines, depth=0,
                          allow_method_list=self._allow_methods, command_prefix='')

        return '\n'.join(lines)

    def _build_md_doc(self):
        """构建高质量 Markdown 格式的完整文档"""
        meta = getattr(self.entry_cls, 'Meta', type('Meta', (), {}))
        app_name = getattr(meta, 'name', self.entry_cls.__name__) if meta else self.entry_cls.__name__
        version = getattr(meta, 'version', '0.0.1') if meta else '0.0.1'
        instance = _safe_instantiate(self.entry_cls)
        description = inspect.getdoc(instance) or self.entry_cls.__name__

        commands = discover_commands(instance, self._base_cls,
                                     include_builtins=False, enable_exec=False,
                                     allow_method_list=self._allow_methods)
        global_args = _format_init_args(self.entry_cls)

        lines = []

        lines.append('# {} v{}'.format(app_name, version))
        lines.append('')
        lines.append('> {}'.format(description))
        lines.append('')

        toc_items = _collect_toc(commands, self._base_cls, prefix='',
                                 allow_method_list=self._allow_methods,
                                 command_prefix='')
        if toc_items:
            lines.append('## Table of Contents')
            lines.append('')
            for item in toc_items:
                indent = '  ' * item['depth']
                anchor = item['display'].lower().replace(' ', '-').replace('_', '-')
                if item['is_group']:
                    lines.append('{}- [`{}`  *(子命令组)*](#{}-子命令组)'.format(
                        indent, item['display'], anchor))
                else:
                    lines.append('{}- [`{}`](#{})'.format(indent, item['display'], anchor))
            lines.append('')

        lines.append('---')
        lines.append('')

        lines.append('## System Params')
        lines.append('')
        lines.append('| Flag | Description |')
        lines.append('|------|-------------|')
        sys_params = [
            ('`-h`, `--help`', '显示帮助信息'),
            ('`-fh`, `--full-help`', '显示完整帮助（所有参数详情）'),
            ('`-eh`, `--easy-help`', '显示简易帮助（argparse 原生格式）'),
            ('`--cmd-version`', '显示版本号'),
            ('`--web`', '以 Web UI + REST API 模式启动'),
            ('`--web-port PORT`', 'Web UI 服务端口（用于 `--web`）'),
        ]
        for flag, desc in sys_params:
            lines.append('| {} | {} |'.format(flag, desc))
        lines.append('')

        init_params = _collect_init_params(self.entry_cls)
        if init_params:
            lines.append('## Global Params (`__init__`)')
            lines.append('')
            lines.append('| Flag | Type | Default | Description |')
            lines.append('|------|------|---------|-------------|')
            for p in init_params:
                lines.append('| `{}` | `{}` | `{}` | {} |'.format(
                    p['flag'], p['type'], p['default'], p['desc']))
            lines.append('')

        lines.append('## Quick Start')
        lines.append('')
        lines.append('```bash')
        lines.append('# 查看完整帮助')
        lines.append('{} {} -fh'.format(self.python, self.script))
        lines.append('')
        lines.append('# 查看版本')
        lines.append('{} {} --cmd-version'.format(self.python, self.script))
        lines.append('')
        lines.append('# 启动 Web UI')
        lines.append('{} {} --web'.format(self.python, self.script))
        lines.append('```')
        lines.append('')

        lines.append('## 命令行约定')
        lines.append('')
        lines.append('命令格式：`python script.py [全局参数] <子命令路径> [命令参数]`')
        lines.append('')
        lines.append('| 标记 | 含义 |')
        lines.append('|------|------|')
        lines.append('| `${value}` | 带默认值的参数 — 可按需替换 |')
        lines.append('| `$<name>` | **必填**参数 — 必须提供值 |')
        lines.append('| `--flag`（无值） | 布尔开关，添加即启用 |')
        lines.append('')

        lines.append('---')
        lines.append('')
        lines.append('## Commands')
        lines.append('')

        _collect_md_doc(commands, self._base_cls, self.script, self.python,
                        global_args, '', lines, depth=0,
                        allow_method_list=self._allow_methods, command_prefix='')

        return '\n'.join(lines)


def _collect_toc(commands, base_cls, prefix='', depth=0, allow_method_list=None,
                 command_prefix=''):
    """递归收集命令目录结构"""
    items = []
    for cmd_name, cmd_info in commands.items():
        full_path = '{} {}'.format(prefix, cmd_name).strip() if prefix else cmd_name
        display = full_path.replace('_', '-')

        if cmd_info.get('is_group'):
            items.append({'display': display, 'is_group': True, 'depth': depth})
            group_cls = cmd_info['cls']
            group_instance = _safe_instantiate(group_cls)
            group_path = '{}/{}'.format(command_prefix, cmd_name) if command_prefix else cmd_name
            sub_commands = discover_commands(group_instance, base_cls,
                                             include_builtins=False, enable_exec=False,
                                             allow_method_list=allow_method_list,
                                             command_prefix=group_path)
            items.extend(_collect_toc(sub_commands, base_cls, prefix=full_path,
                                      depth=depth + 1,
                                      allow_method_list=allow_method_list,
                                      command_prefix=group_path))
        else:
            items.append({'display': display, 'is_group': False, 'depth': depth})
    return items


def _collect_init_params(entry_cls):
    """收集 __init__ 的全局参数信息列表"""
    from .arg import unwrap_arg
    from .type_utils import type_display_name

    init_method = entry_cls.__init__
    if init_method is object.__init__:
        return []

    sig = inspect.signature(init_method)
    results = []
    for pname, param in sig.parameters.items():
        if pname == 'self':
            continue
        has_default = param.default is not inspect.Parameter.empty
        default_val = param.default if has_default else None
        raw_hint = param.annotation
        if raw_hint is inspect.Parameter.empty:
            raw_hint = type(default_val) if default_val is not None else str
        real_type, arg_inst = unwrap_arg(raw_hint)
        desc = arg_inst.desc if arg_inst and arg_inst.desc else ''
        flag = '--{}'.format(pname.replace('_', '-'))
        if arg_inst and arg_inst.aliases:
            flag = '{}, {}'.format(flag, ', '.join(arg_inst.aliases))
        results.append({
            'flag': flag,
            'type': type_display_name(real_type),
            'default': default_val if has_default else '*(required)*',
            'desc': desc or '-',
        })
    return results


def _collect_text_doc(commands, base_cls, script_name, python_path, global_args,
                      prefix, lines, depth, allow_method_list=None, command_prefix=''):
    """递归收集纯文本格式的命令文档"""
    for cmd_name, cmd_info in commands.items():
        full_path = '{} {}'.format(prefix, cmd_name).strip() if prefix else cmd_name

        if cmd_info.get('is_group'):
            group_cls = cmd_info['cls']
            group_doc = cmd_info.get('doc', '')
            indent = '  ' * depth
            lines.append('')
            lines.append('{}[{}]  {}'.format(indent, full_path, group_doc))
            group_instance = _safe_instantiate(group_cls)
            group_path = '{}/{}'.format(command_prefix, cmd_name) if command_prefix else cmd_name
            sub_commands = discover_commands(group_instance, base_cls,
                                             include_builtins=False, enable_exec=False,
                                             allow_method_list=allow_method_list,
                                             command_prefix=group_path)
            _collect_text_doc(sub_commands, base_cls, script_name, python_path,
                              global_args, full_path, lines, depth=depth + 1,
                              allow_method_list=allow_method_list,
                              command_prefix=group_path)
        else:
            method = cmd_info['method']
            doc = cmd_info.get('doc', '')
            method_args = _format_method_args(method)
            display_name = cmd_name.replace('_', '-')
            parts = [python_path, script_name]
            if global_args:
                parts.append(global_args)
            if prefix:
                parts.append(prefix)
            parts.append(display_name)
            if method_args:
                parts.append(method_args)
            cmd_line = ' '.join(parts)
            indent = '  ' * depth
            lines.append('')
            lines.append('{}{}  {}'.format(indent, full_path.replace('_', '-'), doc))
            lines.append('{}  {}'.format(indent, cmd_line))


def _collect_md_doc(commands, base_cls, script_name, python_path, global_args,
                    prefix, lines, depth, allow_method_list=None, command_prefix=''):
    """递归收集 Markdown 格式的命令文档"""
    from .type_utils import (
        is_optional, unwrap_optional, type_display_name,
    )

    for cmd_name, cmd_info in commands.items():
        full_path = '{} {}'.format(prefix, cmd_name).strip() if prefix else cmd_name
        display = full_path.replace('_', '-')

        if cmd_info.get('is_group'):
            group_cls = cmd_info['cls']
            group_doc = cmd_info.get('doc', '')
            level = '#' * min(depth + 3, 6)
            lines.append('{} `{}` *(子命令组)*'.format(level, display))
            lines.append('')
            if group_doc:
                lines.append('> {}'.format(group_doc))
                lines.append('')
            group_instance = _safe_instantiate(group_cls)
            group_path = '{}/{}'.format(command_prefix, cmd_name) if command_prefix else cmd_name
            sub_commands = discover_commands(group_instance, base_cls,
                                             include_builtins=False, enable_exec=False,
                                             allow_method_list=allow_method_list,
                                             command_prefix=group_path)
            _collect_md_doc(sub_commands, base_cls, script_name, python_path,
                            global_args, full_path, lines, depth=depth + 1,
                            allow_method_list=allow_method_list,
                            command_prefix=group_path)
        else:
            method = cmd_info['method']
            doc = cmd_info.get('doc', '')
            method_args = _format_method_args(method)
            display_name = cmd_name.replace('_', '-')

            parts = [python_path, script_name]
            if global_args:
                parts.append(global_args)
            if prefix:
                parts.append(prefix)
            parts.append(display_name)
            if method_args:
                parts.append(method_args)
            cmd_line = ' '.join(parts)

            level = '#' * min(depth + 3, 6)
            lines.append('{} `{}`'.format(level, display))
            lines.append('')
            if doc:
                lines.append(doc)
                lines.append('')

            sig = cmd_info['signature']
            hints = cmd_info.get('type_hints', {})
            arg_meta = cmd_info.get('arg_meta', {})
            param_rows = []
            for pname, param in sig.parameters.items():
                if pname == 'self':
                    continue
                ptype = hints.get(pname, str)
                real_type = unwrap_optional(ptype) if is_optional(ptype) else ptype
                tname = type_display_name(real_type)
                has_default = param.default is not inspect.Parameter.empty
                arg_inst = arg_meta.get(pname)
                desc = arg_inst.desc if arg_inst and arg_inst.desc else '-'
                flag = '--{}'.format(pname.replace('_', '-'))
                if arg_inst and arg_inst.aliases:
                    flag = '{}, {}'.format(flag, ', '.join(arg_inst.aliases))
                default_str = '`{}`'.format(param.default) if has_default else '*(required)*'
                param_rows.append((flag, tname, default_str, desc))

            if param_rows:
                lines.append('| Param | Type | Default | Description |')
                lines.append('|-------|------|---------|-------------|')
                for flag, tname, default_str, desc in param_rows:
                    lines.append('| `{}` | `{}` | {} | {} |'.format(
                        flag, tname, default_str, desc))
                lines.append('')

            lines.append('```bash')
            lines.append(cmd_line)
            lines.append('```')
            lines.append('')


def _get_script_name():
    """获取当前脚本名"""
    import os
    name = sys.argv[0] if sys.argv[0] else 'script.py'
    return os.path.basename(name)


def _get_method_class(method):
    """从 unbound method 获取所属类"""
    qualname = getattr(method, '__qualname__', '')
    parts = qualname.split('.')
    if len(parts) >= 2:
        cls_name = parts[-2]
        module = inspect.getmodule(method)
        if module:
            cls = getattr(module, cls_name, None)
            if cls is not None:
                return cls
    return None


def _find_base_cls(entry_cls):
    """找到 NbCmd 基类"""
    from .base import NbCmd
    return NbCmd


def _get_allow_method_list(entry_cls):
    """从 entry_cls.Meta 获取命令白名单（为空表示不过滤）。"""
    meta = getattr(entry_cls, 'Meta', None)
    if meta is None:
        return None
    return getattr(meta, 'allow_method_list', None)


def _find_command_path(entry_cls, target_cls, base_cls):
    """
    从 entry_cls 的 sub_commands 树中递归搜索 target_cls，
    返回子命令组路径字符串（如 'db' 或 'server ops'）。
    """
    if target_cls is None or target_cls is entry_cls:
        return ''

    sub_cmds = getattr(entry_cls, 'sub_commands', {})
    for group_name, group_val in sub_cmds.items():
        group_cls = group_val if inspect.isclass(group_val) else group_val.__class__
        if group_cls is target_cls:
            return group_name

        deeper = _find_command_path(group_cls, target_cls, base_cls)
        if deeper:
            return '{} {}'.format(group_name, deeper)

    return ''


def _format_init_args(entry_cls):
    """将 entry_cls 的 __init__ 参数格式化为 CLI 全局参数字符串"""
    init_method = entry_cls.__init__
    if init_method is object.__init__:
        return ''

    sig = inspect.signature(init_method)
    parts = []
    for pname, param in sig.parameters.items():
        if pname == 'self':
            continue
        flag = '--{}'.format(pname.replace('_', '-'))
        default = param.default
        if default is inspect.Parameter.empty:
            ptype = param.annotation if param.annotation is not inspect.Parameter.empty else str
            if ptype is bool:
                parts.append(flag)
            else:
                parts.append('{} $<{}>'.format(flag, pname))
        else:
            if isinstance(default, bool):
                if not default:
                    parts.append(flag)
            else:
                parts.append('{} ${{{}}}'.format(flag, default))

    return ' '.join(parts)


def _format_method_args(method):
    """将方法的参数格式化为 CLI 参数字符串"""
    sig = inspect.signature(method)
    parts = []
    for pname, param in sig.parameters.items():
        if pname == 'self':
            continue
        flag = '--{}'.format(pname.replace('_', '-'))
        default = param.default
        ptype = param.annotation if param.annotation is not inspect.Parameter.empty else str

        if default is inspect.Parameter.empty:
            if ptype is bool:
                parts.append(flag)
            else:
                parts.append('{} $<{}>'.format(flag, pname))
        else:
            if isinstance(default, bool):
                if not default:
                    parts.append(flag)
            else:
                parts.append('{} ${{{}}}'.format(flag, default))

    return ' '.join(parts)


def _safe_instantiate(cls):
    """安全实例化类，失败时用 __new__"""
    try:
        return cls()
    except TypeError:
        return cls.__new__(cls)


def _apply_fmt(cmd_line, fmt):
    """应用输出格式"""
    if fmt == 'markdown':
        return '```bash\n{}\n```'.format(cmd_line)
    return cmd_line
