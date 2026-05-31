# -*- coding: utf-8 -*-
"""
AI Skill 文件夹生成器 —— 自动生成符合 agentskills.io 规范的 Skill 文件夹。

用法::

    from nb_cmd import SkillGen

    g = SkillGen(MyApp, output_dir='./skills/my-app')
    g.gen()
"""
import os
import re
import sys
import inspect

from .discovery import discover_commands
from .gen_cmd import (
    _find_base_cls,
    _get_allow_method_list,
    _get_hide_method_list,
    _find_command_path,
    _format_init_args,
    _format_method_args,
    _safe_instantiate,
    _collect_init_params,
)
from .type_utils import is_optional, unwrap_optional, type_display_name


class SkillGen(object):
    """
    AI Skill 文件夹生成器。

    根据 NbCmd 子类的结构，自动生成符合 agentskills.io 规范的 Skill 文件夹。

    Parameters
    ----------
    entry_cls : class
        顶层入口类，如 MyApp
    name : str, optional
        Skill name（默认从 Meta.name 或类名转 kebab-case）。
        最终生成的 Skill 文件夹名即为 name。
    base_dir : str, optional
        父目录路径。默认当前目录 `.`。最终输出路径为 `{base_dir}/{name}/`。
    script : str, optional
        脚本名。默认用 sys.argv[0]。
    python : str, optional
        Python 解释器路径。默认用 sys.executable。
    description : str, optional
        Skill description（默认从 Meta.description 或类 docstring）
    license : str, optional
        License 名称
    compatibility : str, optional
        环境兼容性说明
    metadata : dict, optional
        额外元数据键值对
    allowed_tools : str, optional
        允许使用的工具列表（空格分隔）
    disable_model_invocation : bool, optional
        是否禁用模型自动触发（默认 False，允许自动触发）
    user_highest_priority_skill_prompt : str, optional
        用户自定义的最高优先级提示语，会放在 SKILL.md 的显要位置。
        可用于告知 AI 运行环境信息（如 Python 解释器路径、脚本位置、
        PYTHONPATH 设置等）。
    include_cli_examples : bool, optional
        是否在 SKILL.md 中包含 CLI 命令示例（默认 True）
    include_python_examples : bool, optional
        是否在 SKILL.md 中包含 Python 调用示例（默认 False）
    include_api_examples : bool, optional
        是否在 SKILL.md 中包含 REST API 调用示例（默认 False）
    """

    def __init__(
        self,
        entry_cls,
        name=None,
        base_dir='.',
        script=None,
        python=None,
        description=None,
        license=None,
        compatibility=None,
        metadata=None,
        allowed_tools=None,
        disable_model_invocation=False,
        user_highest_priority_skill_prompt=None,
        include_cli_examples=True,
        include_python_examples=False,
        include_api_examples=False,
    ):
        self.entry_cls = entry_cls
        self._base_dir = base_dir
        self.script = script or self._get_script_name()
        self.python = python or sys.executable
        self._cli_python = 'python'  # CLI 示例中使用简写，提升 AI 阅读体验
        self._base_cls = _find_base_cls(entry_cls)
        self._allow_methods = _get_allow_method_list(entry_cls)
        self._hide_methods = _get_hide_method_list(entry_cls)

        self._user_name = name
        self._user_description = description
        self._license = license
        self._compatibility = compatibility
        self._metadata = metadata or {}
        self._allowed_tools = allowed_tools
        self._disable_model_invocation = disable_model_invocation
        self._user_priority_prompt = user_highest_priority_skill_prompt

        self._include_cli = include_cli_examples
        self._include_python = include_python_examples
        self._include_api = include_api_examples

        self._name = self._resolve_name()
        self._description = self._resolve_description()
        self._validate_name()
        self._validate_description()
        self.output_dir = os.path.join(self._base_dir, self._name)

    def _get_script_name(self):
        import os
        name = sys.argv[0] if sys.argv[0] else 'script.py'
        return os.path.basename(name)

    def _resolve_name(self):
        """解析 Skill name，优先级：用户传入 > Meta.name > 类名转 kebab-case"""
        if self._user_name:
            return self._user_name.strip()
        meta = getattr(self.entry_cls, 'Meta', None)
        if meta:
            meta_name = getattr(meta, 'name', None)
            if meta_name:
                return self._to_kebab_case(meta_name)
        return self._to_kebab_case(self.entry_cls.__name__)

    def _to_kebab_case(self, s):
        """将字符串转为 kebab-case"""
        s = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1-\2', s)
        s = re.sub(r'([a-z\d])([A-Z])', r'\1-\2', s)
        s = s.lower().replace('_', '-').replace(' ', '-')
        s = re.sub(r'-+', '-', s)
        return s.strip('-')

    def _validate_name(self):
        """校验 name 是否符合 agentskills.io 规范"""
        n = self._name
        if not n:
            raise ValueError('Skill name cannot be empty')
        if len(n) > 64:
            raise ValueError('Skill name must be <= 64 characters, got {}'.format(len(n)))
        if n.startswith('-') or n.endswith('-'):
            raise ValueError('Skill name cannot start or end with a hyphen')
        if '--' in n:
            raise ValueError('Skill name cannot contain consecutive hyphens')
        if not re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', n):
            raise ValueError(
                'Skill name must be lowercase alphanumeric with hyphens only, '
                'got: {}'.format(n)
            )

    def _resolve_description(self):
        """解析 Skill description，优先级：用户传入 > Meta.description > 类 docstring > 自动生成"""
        if self._user_description:
            return self._user_description.strip()
        meta = getattr(self.entry_cls, 'Meta', None)
        if meta:
            meta_desc = getattr(meta, 'description', None)
            if meta_desc:
                return meta_desc.strip()
        doc = inspect.getdoc(self.entry_cls)
        if doc:
            lines = [ln.strip() for ln in doc.strip().split('\n') if ln.strip()]
            if lines:
                # 取前几句（不超过 200 字符），确保包含足够信息
                desc = lines[0]
                for ln in lines[1:]:
                    if len(desc) + len(ln) + 1 < 200:
                        desc += ' ' + ln
                    else:
                        break
                return desc
        return self._auto_description()

    def _auto_description(self):
        """自动生成 description"""
        meta = getattr(self.entry_cls, 'Meta', None)
        app_name = getattr(meta, 'name', self.entry_cls.__name__) if meta else self.entry_cls.__name__
        instance = _safe_instantiate(self.entry_cls)
        commands = discover_commands(
            instance, self._base_cls,
            include_builtins=False, enable_exec=False,
            allow_method_list=self._allow_methods,
            hide_method_list=self._hide_methods,
        )
        cmd_names = [k.replace('_', '-') for k in commands.keys() if not commands[k].get('is_group')]
        if not cmd_names:
            cmd_names = [k.replace('_', '-') for k in commands.keys()]
        cmd_preview = ', '.join(cmd_names[:5])
        if len(commands) > 5:
            cmd_preview += ' 等'
        desc = '{} —— 支持 {} 等操作。当需要执行 {} 相关命令时使用。'.format(
            app_name, cmd_preview, app_name
        )
        return desc

    def _validate_description(self):
        """校验 description 长度"""
        if not self._description:
            raise ValueError('Skill description cannot be empty')
        if len(self._description) > 1024:
            raise ValueError(
                'Skill description must be <= 1024 characters, got {}'.format(len(self._description))
            )

    def gen(self):
        """
        生成 Skill 文件夹（仅包含 SKILL.md）。

        Returns
        -------
        str
            生成的 Skill 文件夹路径
        """
        os.makedirs(self.output_dir, exist_ok=True)

        skill_md_content = self.gen_skill_md()
        skill_md_path = os.path.join(self.output_dir, 'SKILL.md')
        with open(skill_md_path, 'w', encoding='utf-8') as f:
            f.write(skill_md_content)

        return self.output_dir

    def gen_skill_md(self):
        """
        生成 SKILL.md 内容字符串。

        Returns
        -------
        str
            SKILL.md 完整内容
        """
        frontmatter = self._gen_frontmatter()
        body = self._gen_body()
        return frontmatter + '\n' + body

    def _gen_frontmatter(self):
        """生成 YAML frontmatter"""
        lines = ['---']
        lines.append('name: {}'.format(self._name))

        # description 使用 >- 折叠块样式（保留换行但折叠为空格）
        desc = self._description
        lines.append('description: >-')
        for paragraph in desc.split('\n\n'):
            for wrap_line in self._wrap_text(paragraph.strip(), 78):
                lines.append('  {}'.format(wrap_line))

        if self._license:
            lines.append('license: {}'.format(self._license))
        if self._compatibility:
            lines.append('compatibility: {}'.format(self._compatibility))
        if self._metadata:
            lines.append('metadata:')
            for k, v in self._metadata.items():
                lines.append('  {}: "{}"'.format(k, v))
        if self._allowed_tools:
            lines.append('allowed-tools: {}'.format(self._allowed_tools))
        if self._disable_model_invocation:
            lines.append('disable-model-invocation: true')

        lines.append('---')
        return '\n'.join(lines)

    def _wrap_text(self, text, width):
        """简单文本折行"""
        if len(text) <= width:
            return [text]
        words = text.split(' ')
        lines = []
        current = ''
        for word in words:
            if len(current) + len(word) + 1 > width:
                if current:
                    lines.append(current)
                current = word
            else:
                current = current + ' ' + word if current else word
        if current:
            lines.append(current)
        return lines if lines else ['']

    def _gen_body(self):
        """生成 Markdown body"""
        instance = _safe_instantiate(self.entry_cls)
        commands = discover_commands(
            instance, self._base_cls,
            include_builtins=False, enable_exec=False,
            allow_method_list=self._allow_methods,
            hide_method_list=self._hide_methods,
        )
        meta = getattr(self.entry_cls, 'Meta', type('Meta', (), {}))
        app_name = getattr(meta, 'name', self.entry_cls.__name__) if meta else self.entry_cls.__name__
        doc = inspect.getdoc(instance) or app_name

        lines = []
        lines.append('# {}'.format(app_name))
        lines.append('')
        lines.append('## Overview')
        lines.append('')
        lines.append(doc)
        lines.append('')

        if self._user_priority_prompt:
            lines.append('## Important')
            lines.append('')
            lines.append(self._user_priority_prompt)
            lines.append('')

        lines.append('## When to Use')
        lines.append('')
        lines.append(self._gen_when_to_use(commands, app_name))
        lines.append('')

        lines.append('## Command Structure')
        lines.append('')
        lines.append(self._gen_command_structure())
        lines.append('')

        init_params = _collect_init_params(self.entry_cls)
        if init_params:
            lines.append('## Global Parameters')
            lines.append('')
            lines.append('These parameters are defined in `__init__` and passed to all subcommands automatically.')
            lines.append('')
            lines.append('| Flag | Type | Default | Description |')
            lines.append('|------|------|---------|-------------|')
            for p in init_params:
                lines.append('| `{}` | `{}` | `{}` | {} |'.format(
                    p['flag'], p['type'], p['default'], p['desc']))
            lines.append('')

        lines.append('## Commands')
        lines.append('')
        self._collect_skill_commands(
            commands, '', lines, depth=0,
            allow_method_list=self._allow_methods,
            hide_method_list=self._hide_methods,
            command_prefix='',
        )
        lines.append('')

        lines.append('## Guidelines')
        lines.append('')
        lines.append(self._gen_guidelines(init_params))

        return '\n'.join(lines)

    def _gen_when_to_use(self, commands, app_name):
        """生成 When to Use 段落（递归收集所有叶子命令）"""
        cmd_names = []
        self._collect_leaf_commands(commands, '', cmd_names)

        when_lines = ['Activate this skill when you need to perform {}-related operations, such as:'.format(app_name)]
        for cmd_name in cmd_names[:15]:
            when_lines.append('- {}'.format(cmd_name))
        if len(cmd_names) > 15:
            when_lines.append('- And other {} commands'.format(app_name))
        return '\n'.join(when_lines)

    def _collect_leaf_commands(self, commands, prefix, result):
        """递归收集所有叶子命令名"""
        for cmd_name, cmd_info in commands.items():
            full_path = '{} {}'.format(prefix, cmd_name).strip() if prefix else cmd_name
            display = full_path.replace('_', '-')
            if cmd_info.get('is_group'):
                group_cls = cmd_info['cls']
                group_instance = _safe_instantiate(group_cls)
                sub_commands = discover_commands(
                    group_instance, self._base_cls,
                    include_builtins=False, enable_exec=False,
                    allow_method_list=self._allow_methods,
                    hide_method_list=self._hide_methods,
                )
                self._collect_leaf_commands(sub_commands, full_path, result)
            else:
                result.append(display)

    def _gen_command_structure(self):
        """生成命令结构说明"""
        lines = []
        if self._include_cli:
            lines.append('### CLI')
            lines.append('```bash')
            lines.append('python {} [global_params] <command_path> [command_params]'.format(self.script))
            lines.append('```')
            lines.append('')
        if self._include_python:
            lines.append('### Python')
            lines.append('```python')
            lines.append('from {} import {}'.format(
                self._module_name_hint(), self.entry_cls.__name__))
            lines.append('app = {}()  # pass global params if needed'.format(self.entry_cls.__name__))
            lines.append('# app.group.method(param=value)')
            lines.append('```')
            lines.append('')
        if self._include_api:
            lines.append('### REST API')
            lines.append('```bash')
            lines.append('curl -X POST http://localhost:8000/api/v1/<command_path> \\')
            lines.append('  -H "Content-Type: application/json" \\')
            lines.append('  -d \'{"param": "value"}\'')
            lines.append('```')
            lines.append('')
        lines.append('**Parameter conventions:**')
        lines.append('- `${value}` — parameter with default value (replace as needed)')
        lines.append('- `$<name>` — **required** parameter (must provide a value)')
        lines.append('- `--flag` (no value) — boolean switch (add to enable)')
        return '\n'.join(lines)

    def _module_name_hint(self):
        """推测模块导入名"""
        module = inspect.getmodule(self.entry_cls)
        if module and hasattr(module, '__name__') and module.__name__ != '__main__':
            return module.__name__
        return self.script.replace('.py', '').replace('/', '.').replace('\\', '.')

    def _collect_skill_commands(self, commands, prefix, lines, depth=0,
                                allow_method_list=None, hide_method_list=None,
                                command_prefix=''):
        """递归收集命令说明（面向 AI 的 Skill 格式）"""
        for cmd_name, cmd_info in commands.items():
            full_path = '{} {}'.format(prefix, cmd_name).strip() if prefix else cmd_name
            display = full_path.replace('_', '-')

            if cmd_info.get('is_group'):
                group_cls = cmd_info['cls']
                group_doc = cmd_info.get('doc', '')
                level = '###'
                lines.append('{} `{}` *(subcommand group)*'.format(level, display))
                lines.append('')
                if group_doc:
                    lines.append(group_doc)
                    lines.append('')
                group_instance = _safe_instantiate(group_cls)
                group_path = '{}/{}'.format(command_prefix, cmd_name) if command_prefix else cmd_name
                sub_commands = discover_commands(
                    group_instance, self._base_cls,
                    include_builtins=False, enable_exec=False,
                    allow_method_list=allow_method_list,
                    hide_method_list=hide_method_list,
                    command_prefix=group_path,
                )
                self._collect_skill_commands(
                    sub_commands, full_path, lines, depth=depth + 1,
                    allow_method_list=allow_method_list,
                    hide_method_list=hide_method_list,
                    command_prefix=group_path,
                )
            else:
                method = cmd_info['method']
                doc = cmd_info.get('doc', '')
                level = '###'
                lines.append('{} `{}`'.format(level, display))
                lines.append('')
                if doc:
                    lines.append(doc)
                    lines.append('')

                # 参数表格
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

                # 示例
                method_args = _format_method_args(method)
                # 清理 CLI 示例：去掉 ${None} 这种无意义的默认值展示
                method_args = self._clean_cli_args(method_args)
                display_name = cmd_name.replace('_', '-')

                if self._include_cli:
                    global_args = _format_init_args(self.entry_cls)
                    parts = [self.python, self.script]
                    if global_args:
                        parts.append(global_args)
                    if prefix:
                        parts.append(prefix.replace('_', '-'))
                    parts.append(display_name)
                    if method_args:
                        parts.append(method_args)
                    cmd_line = ' '.join(parts)
                    lines.append('**CLI:**')
                    lines.append('```bash')
                    lines.append(cmd_line)
                    lines.append('```')
                    lines.append('')

                if self._include_python:
                    lines.append('**Python:**')
                    lines.append('```python')
                    # 生成 Python 调用示例
                    py_parts = ['app']
                    if prefix:
                        for part in prefix.split():
                            py_parts.append(part.replace('_', ''))
                    py_parts.append('{}({})'.format(
                        cmd_name,
                        self._format_python_args(method),
                    ))
                    lines.append('.'.join(py_parts))
                    lines.append('```')
                    lines.append('')

    def _format_python_args(self, method):
        """格式化 Python 调用示例的参数"""
        sig = inspect.signature(method)
        parts = []
        for pname, param in sig.parameters.items():
            if pname == 'self':
                continue
            default = param.default
            if default is inspect.Parameter.empty:
                ptype = param.annotation if param.annotation is not inspect.Parameter.empty else str
                if ptype is bool:
                    parts.append('{}=True'.format(pname))
                else:
                    parts.append('{}=<{}>'.format(pname, pname))
            else:
                if isinstance(default, bool):
                    parts.append('{}={}'.format(pname, default))
                elif isinstance(default, str):
                    parts.append('{}="{}"'.format(pname, default))
                else:
                    parts.append('{}={}'.format(pname, default))
        return ', '.join(parts)

    def _clean_cli_args(self, method_args):
        """清理 CLI 示例参数，去掉 ${None} 等无意义的默认值展示"""
        if not method_args:
            return method_args
        # 移除 --flag ${None} 形式的参数（None 默认值在 CLI 中不需要展示）
        cleaned = re.sub(r'--[\w-]+\s+\$\{None\}(\s+|$)', ' ', method_args)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        return cleaned

    def _gen_guidelines(self, init_params):
        """生成使用指南"""
        lines = []
        if init_params:
            lines.append('- Global parameters defined in `__init__` are automatically passed to all subcommands.')
        lines.append('- Boolean flags default to `False`; add the flag to set it to `True`.')
        lines.append('- Subcommand groups are accessed via space or dot, e.g., `db migrate` or `db.migrate`.')
        lines.append('- Use `--help` or `-h` to see available commands and options.')
        lines.append('- Use `--full-help` or `-fh` to see detailed parameter descriptions.')
        return '\n'.join(lines)


