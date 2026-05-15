# -*- coding: utf-8 -*-
"""
TUI 模式 —— 基于 Textual 的终端图形交互界面。
需要安装: pip install textual (Python 3.8+)
"""
import asyncio
import inspect
import sys
import time

from ..core.discovery import discover_commands
from ..core.result_handler import handle_api_result


class _TuiWriter(object):
    """将 print 输出按行缓冲，通过回调安全地写入 RichLog。"""

    def __init__(self, write_fn):
        self._write = write_fn
        self._buf = ''

    def write(self, data):
        if not data:
            return
        self._buf += data
        lines = self._buf.split('\n')
        for line in lines[:-1]:
            self._write(line)
        self._buf = lines[-1]

    def flush(self):
        if self._buf:
            self._write(self._buf)
            self._buf = ''


def _detect_init_params(instance, unwrap_optional, _is_opt, is_enum_type,
                        get_choices, type_display_name, unwrap_arg):
    """提取 __init__ 中的参数信息，用于 TUI 全局参数面板。"""
    init_method = instance.__class__.__init__
    if init_method is object.__init__:
        return []
    sig = inspect.signature(init_method)
    params = []
    for pname, param in sig.parameters.items():
        if pname == 'self':
            continue
        has_default = param.default is not inspect.Parameter.empty
        raw_hint = param.annotation
        if raw_hint is inspect.Parameter.empty:
            if has_default and param.default is not None:
                raw_hint = type(param.default)
            else:
                raw_hint = str
        real_type, arg_inst = unwrap_arg(raw_hint)
        unwrapped = unwrap_optional(real_type) if _is_opt(real_type) else real_type
        desc = arg_inst.desc if arg_inst and arg_inst.desc else ''
        choices = get_choices(real_type)
        current_val = getattr(instance, pname, param.default if has_default else None)
        params.append({
            'name': pname,
            'type': unwrapped,
            'type_name': type_display_name(unwrapped),
            'real_type': real_type,
            'required': not has_default,
            'default': param.default if has_default else None,
            'current': current_val,
            'choices': choices,
            'desc': desc,
            'is_enum': is_enum_type(unwrapped),
        })
    return params


def start_tui(instance, base_cls):
    """启动 TUI 模式"""
    try:
        from textual.app import App, ComposeResult
        from textual.screen import Screen
        from textual.widgets import (
            Header, Footer, Tree, RichLog, Input, Button,
            Switch, Select, Static, Markdown, Label,
        )
        from textual.containers import Horizontal, Vertical, VerticalScroll
        from textual import work
        from rich.text import Text
    except ImportError:
        print("TUI 模式需要安装 textual:")
        print("  pip install nb-cmd[tui]")
        if sys.version_info < (3, 8):
            print("  注意: TUI 模式需要 Python 3.8+")
        return

    from ..core.type_utils import (
        type_display_name, is_enum_type, unwrap_optional,
        is_optional as _is_opt, get_choices, convert_value,
    )
    from ..core.gen_cmd import CmdGen
    import re as _re

    _ANSI_FG = {
        '30': '#b0bec5', '31': '#ff6b6b', '32': '#69f0ae', '33': '#fff176',
        '34': '#64b5f6', '35': '#ce93d8', '36': '#80deea', '37': '#ffffff',
        '90': '#cfd8dc', '91': '#ff1744', '92': '#b9f6ca', '93': '#ffff8d',
        '94': '#90caf9', '95': '#ea80fc', '96': '#b2ebf2', '97': '#ffffff',
    }
    _ANSI_BG = {
        '40': '#78909c', '41': '#ff1744', '42': '#00e676', '43': '#ffea00',
        '44': '#2979ff', '45': '#d500f9', '46': '#00e5ff', '47': '#ffffff',
    }

    def _ansi_to_rich(data):
        """ANSI → Rich Text, stateful parser with vivid bg + auto-contrast."""
        parts = _re.split(r'\x1b\[([0-9;]*)m', data)
        txt = Text()
        st_fg = None
        st_bg = None
        st_bold = False
        st_ul = False
        for i, part in enumerate(parts):
            if i % 2 == 0:
                if part:
                    sp = []
                    if st_bold:
                        sp.append('bold')
                    if st_ul:
                        sp.append('underline')
                    if st_bg:
                        sp.append('on ' + st_bg)
                        h = st_bg.lstrip('#')
                        r = int(h[0:2], 16)
                        g = int(h[2:4], 16)
                        b = int(h[4:6], 16)
                        lum = 0.299 * r + 0.587 * g + 0.114 * b
                        sp.insert(0, '#000000' if lum > 128 else '#ffffff')
                    elif st_fg:
                        sp.insert(0, st_fg)
                    txt.append(part, style=' '.join(sp) if sp else None)
            else:
                for c in part.split(';'):
                    if c == '0' or c == '':
                        st_fg = st_bg = None
                        st_bold = st_ul = False
                    elif c == '1':
                        st_bold = True
                    elif c == '4':
                        st_ul = True
                    elif c in _ANSI_FG:
                        st_fg = _ANSI_FG[c]
                    elif c in _ANSI_BG:
                        st_bg = _ANSI_BG[c]
        return txt

    import os as _os
    import sqlite3 as _sqlite3

    _db_path = _os.path.join(_os.getcwd(), 'nb_cmd_web.db')

    def _get_db():
        conn = _sqlite3.connect(_db_path)
        conn.execute(
            'CREATE TABLE IF NOT EXISTS saved_commands '
            '(id INTEGER PRIMARY KEY AUTOINCREMENT, '
            'command TEXT UNIQUE NOT NULL, '
            'created_at TEXT DEFAULT CURRENT_TIMESTAMP)')
        conn.execute(
            'CREATE TABLE IF NOT EXISTS command_history '
            '(id INTEGER PRIMARY KEY AUTOINCREMENT, '
            'command TEXT NOT NULL, '
            'executed_at TEXT DEFAULT CURRENT_TIMESTAMP)')
        return conn

    _get_db().close()

    meta = getattr(instance.__class__, 'Meta', type('Meta', (), {}))
    title = (getattr(meta, 'web_title', None)
             or getattr(meta, 'name', None)
             or instance.__class__.__name__)
    version = getattr(meta, 'version', None) or '0.0.1'
    _enable_exec = getattr(meta, 'enable_exec', True)
    _allow = getattr(meta, 'allow_method_list', None)
    _hide = getattr(meta, 'hide_method_list', None)
    _timeout = getattr(meta, 'timeout', 0)

    commands = discover_commands(
        instance, base_cls,
        enable_exec=_enable_exec,
        allow_method_list=_allow,
        hide_method_list=_hide,
    )
    user_cls = instance.__class__

    from ..core.arg import unwrap_arg
    init_params_info = _detect_init_params(instance, unwrap_optional, _is_opt,
                                           is_enum_type, get_choices,
                                           type_display_name, unwrap_arg)

    gen = CmdGen(user_cls, fmt='markdown')
    md_doc = gen.doc()

    # ================================================================
    #  HistoryScreen — 命令执行历史
    # ================================================================
    class HistoryScreen(Screen):
        BINDINGS = [("escape", "dismiss_screen", "返回")]

        def compose(self):
            yield Header()
            yield Static(" \u25b6 命令执行历史 (最近100条)", id="hist-title")
            yield VerticalScroll(id="hist-list")
            yield Footer()

        async def on_mount(self):
            container = self.query_one("#hist-list")
            conn = _get_db()
            rows = conn.execute(
                'SELECT command, executed_at FROM command_history '
                'ORDER BY id DESC LIMIT 100'
            ).fetchall()
            conn.close()
            if not rows:
                await container.mount(
                    Static("暂无历史记录", classes="hist-empty"))
                return
            seen = set()
            for cmd, ts in rows:
                if cmd in seen:
                    continue
                seen.add(cmd)
                btn = Button(
                    '{} ({})'.format(cmd, ts[:16] if ts else ''),
                    classes="hist-item",
                )
                btn._hist_cmd = cmd
                await container.mount(btn)

        def on_button_pressed(self, event):
            cmd = getattr(event.button, '_hist_cmd', None)
            if cmd:
                try:
                    self.app.copy_to_clipboard(cmd)
                    self.notify("已复制: {}".format(cmd[:40]), timeout=2)
                except Exception:
                    pass

        def action_dismiss_screen(self):
            self.app.pop_screen()

    # ================================================================
    #  FavoritesScreen — 收藏命令
    # ================================================================
    class FavoritesScreen(Screen):
        BINDINGS = [("escape", "dismiss_screen", "返回")]

        def compose(self):
            yield Header()
            yield Static(" \u2605 收藏命令列表", id="fav-title")
            yield VerticalScroll(id="fav-list")
            yield Footer()

        async def on_mount(self):
            await self._load_items()

        async def _load_items(self):
            container = self.query_one("#fav-list")
            await container.remove_children()
            conn = _get_db()
            rows = conn.execute(
                'SELECT command, created_at FROM saved_commands '
                'ORDER BY id DESC'
            ).fetchall()
            conn.close()
            if not rows:
                await container.mount(
                    Static("暂无收藏命令", classes="fav-empty"))
                return
            for cmd, ts in rows:
                row = Horizontal(classes="fav-row")
                await container.mount(row)
                btn = Button(cmd, classes="fav-item")
                btn._fav_cmd = cmd
                del_btn = Button("\u2716", variant="error", classes="fav-del")
                del_btn._fav_cmd = cmd
                await row.mount(btn, del_btn)

        def on_button_pressed(self, event):
            cmd = getattr(event.button, '_fav_cmd', None)
            if not cmd:
                return
            if 'fav-del' in event.button.classes:
                conn = _get_db()
                try:
                    conn.execute(
                        'DELETE FROM saved_commands WHERE command = ?', (cmd,))
                    conn.commit()
                finally:
                    conn.close()
                self.notify("已取消收藏", timeout=2)
                self.call_later(self._load_items)
            else:
                try:
                    self.app.copy_to_clipboard(cmd)
                    self.notify("已复制: {}".format(cmd[:40]), timeout=2)
                except Exception:
                    pass

        def action_dismiss_screen(self):
            self.app.pop_screen()

    # ================================================================
    #  DocScreen — 首屏: CmdGen 生成的 Markdown 文档
    # ================================================================
    class DocScreen(Screen):
        BINDINGS = [
            ("enter", "go_main", "进入交互模式"),
            ("escape", "go_main", "进入交互模式"),
            ("ctrl+q", "quit_app", "退出"),
        ]

        def compose(self):
            yield Header()
            with VerticalScroll():
                yield Markdown(md_doc, id="doc-md")
            yield Footer()

        def action_go_main(self):
            self.app.switch_screen("main")

        def action_quit_app(self):
            self.app.exit()

    # ================================================================
    #  MainScreen — 左右分栏交互界面
    # ================================================================
    class MainScreen(Screen):
        BINDINGS = [
            ("ctrl+e", "execute", "执行"),
            ("ctrl+x", "stop", "停止"),
            ("ctrl+h", "show_history", "历史"),
            ("ctrl+f", "show_favorites", "收藏夹"),
            ("ctrl+l", "clear_log", "清空控制台"),
            ("ctrl+y", "copy_log", "复制输出"),
            ("ctrl+d", "show_doc", "查看文档"),
            ("ctrl+q", "quit_app", "退出"),
        ]

        def __init__(self):
            super().__init__()
            self._current_cmd = None
            self._current_path = None
            self._log_buffer = []
            self._worker_tid = None
            self._param_cache = {}

        def compose(self):
            yield Header()
            with Horizontal(id="main-split"):
                with Vertical(id="left-panel"):
                    yield Static(" \u25b6 命令列表", id="tree-title")
                    tree = Tree(title, id="cmd-tree")
                    tree.root.expand()
                    self._build_tree(tree.root, commands, '')
                    yield tree

                    if init_params_info:
                        yield Static(" \u25b6 全局参数", id="init-title")
                        init_form = VerticalScroll(id="init-form")
                        yield init_form

                    yield Static(" \u25b6 参数", id="form-title")
                    yield VerticalScroll(
                        Static("\u2190 请在上方选择一个命令", id="form-hint"),
                        id="param-form",
                    )
                    with Horizontal(id="cmd-gen-bar"):
                        yield Label("CLI:", classes="cmd-gen-label")
                        yield Input(
                            placeholder="选择命令后自动生成",
                            id="cmd-gen",
                            disabled=True,
                        )
                        yield Button("\u2605", id="btn-star")
                    with Horizontal(id="btn-bar"):
                        yield Button("执行", variant="primary", id="btn-exec")
                        yield Button("停止", variant="error", id="btn-stop", disabled=True)
                        yield Button("历史", id="btn-history")
                        yield Button("收藏夹", id="btn-favs")
                        yield Button("复制输出", variant="success", id="btn-copy")
                        yield Button("清空控制台", variant="warning", id="btn-clear")
                        yield Button("退出", id="btn-quit")

                with Vertical(id="right-panel"):
                    yield Static(" \u25b6 输出控制台", id="log-title")
                    yield RichLog(
                        highlight=True,
                        markup=True,
                        auto_scroll=True,
                        wrap=True,
                        id="output-log",
                    )
            yield Footer()

        # ---------- Init params form ----------

        async def on_mount(self):
            if not init_params_info:
                return
            form = self.query_one("#init-form")
            for p in init_params_info:
                pname = p['name']
                wid = 'init-{}'.format(pname)
                req = ' *' if p['required'] else ''
                label_text = '--{}{}:'.format(pname.replace('_', '-'), req)
                if p['desc']:
                    label_text += ' ({})'.format(p['desc'])

                val = p['current']
                if p['type'] is bool:
                    widget = Switch(value=bool(val) if val else False, id=wid)
                elif p['is_enum'] and p['choices']:
                    opts = [(str(c), c) for c in p['choices']]
                    sel_val = Select.BLANK
                    if val is not None:
                        dv = val.value if hasattr(val, 'value') else val
                        for _, v in opts:
                            if v == dv:
                                sel_val = dv
                                break
                    widget = Select(options=opts, value=sel_val, id=wid)
                else:
                    sv = str(val) if val is not None else ''
                    widget = Input(value=sv, placeholder=p['type_name'], id=wid)

                row = Horizontal(classes="form-row")
                await form.mount(row)
                await row.mount(
                    Label(label_text, classes="param-label"),
                    widget,
                )

        def _collect_init_params(self):
            """Collect init params from widgets, return dict or None."""
            if not init_params_info:
                return None
            form = self.query_one("#init-form")
            kwargs = {}
            for p in init_params_info:
                wid = '#init-{}'.format(p['name'])
                try:
                    w = form.query_one(wid)
                except Exception:
                    continue
                if isinstance(w, Switch):
                    kwargs[p['name']] = w.value
                elif isinstance(w, Select):
                    if w.value != Select.BLANK:
                        kwargs[p['name']] = convert_value(w.value, p['real_type'])
                elif isinstance(w, Input):
                    if w.value.strip():
                        kwargs[p['name']] = convert_value(w.value.strip(), p['real_type'])
                    elif p['default'] is not None:
                        kwargs[p['name']] = p['default']
            return kwargs if kwargs else None

        def _make_instance(self, init_kwargs=None):
            """Create a fresh instance with optional init param overrides."""
            if not init_kwargs:
                inst = user_cls()
            else:
                inst = user_cls(**init_kwargs)
            ctx = inst.make_nbctx()
            if ctx is not None:
                inst.nbctx = ctx
            return inst

        # ---------- Tree building ----------

        def _build_tree(self, parent, cmds, prefix):
            for name, info in cmds.items():
                cli_name = name.replace('_', '-')
                full_path = '{}/{}'.format(prefix, name) if prefix else name
                if info.get('is_group'):
                    doc = info.get('doc', '')
                    label = '{} {}'.format(
                        cli_name,
                        '({})'.format(doc[:30]) if doc else '',
                    )
                    node = parent.add(
                        label,
                        data={'type': 'group', 'path': full_path, 'info': info},
                    )
                    g_cls = info['cls']
                    g_kw = info.get('init_kwargs', {})
                    try:
                        g_inst = g_cls(**g_kw) if g_kw else g_cls()
                    except TypeError:
                        g_inst = g_cls.__new__(g_cls)
                    g_cmds = discover_commands(
                        g_inst, base_cls, include_builtins=False,
                        allow_method_list=_allow,
                        hide_method_list=_hide,
                        command_prefix=full_path,
                    )
                    self._build_tree(node, g_cmds, full_path)
                    node.expand()
                else:
                    doc = info.get('doc', '')
                    label = cli_name
                    if doc:
                        label = '{}  {}'.format(cli_name, doc[:40])
                    parent.add_leaf(
                        label,
                        data={'type': 'command', 'path': full_path, 'info': info},
                    )

        # ---------- Tree selection → form update ----------

        async def on_tree_node_selected(self, event):
            node_data = event.node.data
            if not node_data or node_data['type'] != 'command':
                return
            if self._current_path and self._current_cmd:
                self._param_cache[self._current_path] = self._collect_params()
            self._current_cmd = node_data['info']
            self._current_path = node_data['path']
            await self._refresh_form(node_data['info'])
            self._update_cmd_gen()

        async def _refresh_form(self, cmd_info):
            form = self.query_one("#param-form")
            await form.remove_children()

            sig = cmd_info['signature']
            hints = cmd_info.get('type_hints', {})
            arg_meta = cmd_info.get('arg_meta', {})

            rows = []
            for pname, param in sig.parameters.items():
                if pname == 'self':
                    continue
                ptype = hints.get(pname, str)
                has_default = param.default is not inspect.Parameter.empty
                default = param.default if has_default else None
                real_type = unwrap_optional(ptype) if _is_opt(ptype) else ptype
                choices = get_choices(ptype)

                arg_inst = arg_meta.get(pname)
                desc = arg_inst.desc if arg_inst and arg_inst.desc else ''
                req = ' *' if not has_default else ''
                label_text = '--{}{}:'.format(pname.replace('_', '-'), req)
                if desc:
                    label_text += ' ({})'.format(desc)

                wid = 'param-{}'.format(pname)
                if real_type is bool:
                    widget = Switch(
                        value=bool(default) if default else False,
                        id=wid,
                    )
                elif is_enum_type(real_type) and choices:
                    opts = [(str(c), c) for c in choices]
                    sel_val = Select.BLANK
                    if default is not None:
                        dv = default.value if hasattr(default, 'value') else default
                        for _, v in opts:
                            if v == dv:
                                sel_val = dv
                                break
                    widget = Select(options=opts, value=sel_val, id=wid)
                else:
                    val = str(default) if default is not None else ''
                    ph = type_display_name(real_type)
                    widget = Input(value=val, placeholder=ph, id=wid)

                rows.append((label_text, widget))

            if not rows:
                await form.mount(
                    Static("该命令没有参数，直接点击执行", id="no-params")
                )
                return

            for label_text, widget in rows:
                row = Horizontal(classes="form-row")
                await form.mount(row)
                await row.mount(
                    Label(label_text, classes="param-label"),
                    widget,
                )

            cached = self._param_cache.get(self._current_path)
            if cached:
                for pname, val in cached.items():
                    wid = '#param-{}'.format(pname)
                    try:
                        w = form.query_one(wid)
                    except Exception:
                        continue
                    if isinstance(w, Switch):
                        w.value = bool(val)
                    elif isinstance(w, Select):
                        w.value = val
                    elif isinstance(w, Input):
                        w.value = str(val) if val is not None else ''

        # ---------- Collect form values ----------

        def _collect_params(self):
            if not self._current_cmd:
                return {}
            form = self.query_one("#param-form")
            sig = self._current_cmd['signature']
            hints = self._current_cmd.get('type_hints', {})
            kwargs = {}
            for pname, param in sig.parameters.items():
                if pname == 'self':
                    continue
                wid = '#param-{}'.format(pname)
                try:
                    w = form.query_one(wid)
                except Exception:
                    continue
                ptype = hints.get(pname, str)
                if isinstance(w, Switch):
                    kwargs[pname] = w.value
                elif isinstance(w, Select):
                    if w.value != Select.BLANK:
                        kwargs[pname] = convert_value(w.value, ptype)
                elif isinstance(w, Input):
                    if w.value.strip():
                        kwargs[pname] = convert_value(w.value.strip(), ptype)
                    elif param.default is not inspect.Parameter.empty:
                        kwargs[pname] = param.default
            return kwargs

        def _build_cmd_str(self, path=None, kwargs=None):
            if path is None:
                path = self._current_path or ''
            if kwargs is None:
                kwargs = self._collect_params()
            cmd = path.replace('/', ' ').replace('_', '-')
            for k, v in kwargs.items():
                if isinstance(v, bool):
                    if v:
                        cmd += ' --{}'.format(k.replace('_', '-'))
                else:
                    cmd += ' --{} {}'.format(k.replace('_', '-'), v)
            init_kw = self._collect_init_params()
            if init_kw:
                for k, v in init_kw.items():
                    if isinstance(v, bool):
                        if v:
                            cmd += ' --{}'.format(k.replace('_', '-'))
                    else:
                        cmd += ' --{} {}'.format(k.replace('_', '-'), v)
            return cmd

        def _update_cmd_gen(self):
            try:
                gen_input = self.query_one("#cmd-gen", Input)
                gen_input.value = self._build_cmd_str()
            except Exception:
                pass

        # ---------- Resolve command path → (method, instance) ----------

        def _resolve(self, route_path):
            parts = route_path.split('/')
            init_kwargs = self._collect_init_params()
            if init_kwargs is not None:
                root_inst = self._make_instance(init_kwargs)
            else:
                root_inst = self._make_instance()

            if len(parts) == 1:
                name = parts[0]
                if name in commands and not commands[name].get('is_group'):
                    return getattr(root_inst, name), root_inst
                return None, None

            current_inst = root_inst
            current_cmds = commands
            current_prefix = ''
            for i, part in enumerate(parts):
                if part not in current_cmds:
                    return None, None
                info = current_cmds[part]
                if info.get('is_group'):
                    g_cls = info['cls']
                    g_kw = info.get('init_kwargs', {})
                    try:
                        child = g_cls(**g_kw) if g_kw else g_cls()
                    except TypeError:
                        child = g_cls.__new__(g_cls)
                    if current_inst.nbctx is not None:
                        child.nbctx = current_inst.nbctx
                    current_inst = child
                    current_prefix = (
                        '{}/{}'.format(current_prefix, part)
                        if current_prefix else part
                    )
                    current_cmds = discover_commands(
                        current_inst, base_cls,
                        include_builtins=False,
                        allow_method_list=_allow,
                        hide_method_list=_hide,
                        command_prefix=current_prefix,
                    )
                elif i == len(parts) - 1:
                    return getattr(current_inst, part), current_inst
            return None, None

        # ---------- Execution ----------

        def on_button_pressed(self, event):
            bid = event.button.id
            if bid == 'btn-exec':
                self.action_execute()
            elif bid == 'btn-stop':
                self.action_stop()
            elif bid == 'btn-star':
                self._toggle_star()
            elif bid == 'btn-history':
                self.action_show_history()
            elif bid == 'btn-favs':
                self.action_show_favorites()
            elif bid == 'btn-copy':
                self.action_copy_log()
            elif bid == 'btn-clear':
                self.action_clear_log()
            elif bid == 'btn-quit':
                self.action_quit_app()

        def on_input_submitted(self, event):
            if event.input.id == 'cmd-gen':
                return
            self.action_execute()

        def action_execute(self):
            if not self._current_cmd or not self._current_path:
                return
            if self._worker_tid is not None:
                self.notify("有命令正在执行中", timeout=2)
                return
            self._exec_log = self.query_one("#output-log", RichLog)
            self._exec_kwargs = self._collect_params()
            self._exec_path = self._current_path
            self._update_cmd_gen()
            self.query_one("#btn-exec", Button).disabled = True
            self.query_one("#btn-stop", Button).disabled = False
            self._do_execute()

        def action_stop(self):
            tid = self._worker_tid
            if tid is None:
                return
            import ctypes
            try:
                ctypes.pythonapi.PyThreadState_SetAsyncExc(
                    ctypes.c_ulong(tid),
                    ctypes.py_object(KeyboardInterrupt),
                )
            except Exception:
                pass

        def action_clear_log(self):
            self.query_one("#output-log", RichLog).clear()
            self._log_buffer.clear()

        def action_copy_log(self):
            text = '\n'.join(self._log_buffer)
            if text.strip():
                try:
                    self.app.copy_to_clipboard(text)
                    self.notify("已复制到剪贴板", timeout=2)
                except Exception:
                    self.notify("复制失败，请用 Shift+鼠标 选择文字", timeout=3)
            else:
                self.notify("控制台为空", timeout=2)

        def action_show_doc(self):
            self.app.switch_screen("doc")

        def action_show_history(self):
            self.app.push_screen(HistoryScreen())

        def action_show_favorites(self):
            self.app.push_screen(FavoritesScreen())

        def _toggle_star(self):
            cmd = self._build_cmd_str()
            if not cmd.strip():
                self.notify("请先选择命令", timeout=2)
                return
            conn = _get_db()
            try:
                exists = conn.execute(
                    'SELECT 1 FROM saved_commands WHERE command = ?',
                    (cmd,),
                ).fetchone()
                if exists:
                    conn.execute(
                        'DELETE FROM saved_commands WHERE command = ?', (cmd,))
                    self.notify("已取消收藏", timeout=2)
                else:
                    conn.execute(
                        'INSERT OR IGNORE INTO saved_commands (command) VALUES (?)',
                        (cmd,))
                    self.notify("已收藏", timeout=2)
                conn.commit()
            finally:
                conn.close()

        def action_quit_app(self):
            self.app.exit()

        def _buf_write(self, log, content, plain_text=None):
            """Write to RichLog and buffer plain text for clipboard copy."""
            buf_text = plain_text if plain_text is not None else str(content)
            self._log_buffer.append(buf_text)
            self.app.call_from_thread(log.write, content)

        def _reset_btn_state(self):
            try:
                self.query_one("#btn-exec", Button).disabled = False
                self.query_one("#btn-stop", Button).disabled = True
            except Exception:
                pass

        @work(thread=True)
        def _do_execute(self):
            import threading
            self._worker_tid = threading.current_thread().ident

            log = self._exec_log
            path = self._exec_path
            kwargs = self._exec_kwargs

            cmd_str = self._build_cmd_str(path, kwargs)
            echo = '$ {}'.format(cmd_str)

            try:
                conn = _get_db()
                conn.execute(
                    'INSERT INTO command_history (command) VALUES (?)',
                    (cmd_str,))
                conn.execute(
                    'DELETE FROM command_history WHERE id NOT IN '
                    '(SELECT id FROM command_history '
                    'ORDER BY id DESC LIMIT 1000)')
                conn.commit()
                conn.close()
            except Exception:
                pass
            self._buf_write(log, echo)

            method, target_inst = self._resolve(path)
            if method is None:
                err = '[错误] 无法解析命令: {}'.format(path)
                self._buf_write(
                    log, Text.from_markup('[bold red]{}[/]'.format(err)), err,
                )
                self._worker_tid = None
                self.app.call_from_thread(self._reset_btn_state)
                return

            old_stdout = sys.stdout
            old_stderr = sys.stderr

            def _on_line(d):
                self._log_buffer.append(d)
                self.app.call_from_thread(
                    log.write, _ansi_to_rich(d) if d else d,
                )

            writer = _TuiWriter(_on_line)
            sys.stdout = writer
            sys.stderr = writer

            start = time.time()
            try:
                target_inst.before_run()
                result = method(**kwargs)
                if inspect.iscoroutine(result):
                    result = asyncio.run(result)
                result = handle_api_result(result)
                if result is not None:
                    self._buf_write(log, str(result))
                elapsed = int((time.time() - start) * 1000)
                done = '[完成] {}ms'.format(elapsed)
                self._buf_write(
                    log, Text.from_markup('[bold green]{}[/]'.format(done)), done,
                )
            except KeyboardInterrupt:
                elapsed = int((time.time() - start) * 1000)
                msg = '[已取消] {}ms'.format(elapsed)
                self._buf_write(
                    log, Text.from_markup('[bold yellow]{}[/]'.format(msg)), msg,
                )
            except Exception as exc:
                elapsed = int((time.time() - start) * 1000)
                err = '[错误] {} ({}ms)'.format(str(exc), elapsed)
                self._buf_write(
                    log, Text.from_markup('[bold red]{}[/]'.format(err)), err,
                )
                target_inst.on_error(path, exc)
            finally:
                writer.flush()
                sys.stdout = old_stdout
                sys.stderr = old_stderr
                target_inst.after_run()
                self._worker_tid = None
                self.app.call_from_thread(self._reset_btn_state)

    # ================================================================
    #  App
    # ================================================================
    class NbCmdTuiApp(App):
        TITLE = '{} v{}'.format(title, version)

        CSS = """
        #main-split {
            height: 1fr;
        }
        #left-panel {
            width: 2fr;
            border-right: solid $primary;
        }
        #right-panel {
            width: 3fr;
        }
        #tree-title, #form-title, #log-title, #init-title {
            background: $surface;
            color: $text;
            text-style: bold;
            height: 1;
            padding: 0 1;
        }
        #init-title {
            color: $warning;
        }
        #cmd-tree {
            height: 4fr;
            border-bottom: solid $surface;
        }
        #init-form {
            height: auto;
            max-height: 8;
            border-bottom: solid $surface;
        }
        #param-form {
            height: 2fr;
        }
        .form-row {
            height: auto;
            max-height: 4;
            padding: 0 1;
        }
        .param-label {
            width: 24;
            min-width: 16;
            height: 3;
            content-align: left middle;
            padding-right: 1;
            color: $text-muted;
        }
        .form-row Input {
            width: 1fr;
        }
        .form-row Switch {
            width: auto;
            height: auto;
        }
        .form-row Select {
            width: 1fr;
        }
        #form-hint, #no-params {
            padding: 1;
            color: $text-disabled;
        }
        #cmd-gen-bar {
            height: 3;
            padding: 0 1;
            dock: bottom;
            margin-bottom: 3;
        }
        .cmd-gen-label {
            width: 5;
            height: 3;
            content-align: right middle;
            color: $text-muted;
        }
        #cmd-gen {
            width: 1fr;
        }
        #btn-star {
            width: 5;
            min-width: 5;
            background: $warning;
            color: $text;
        }
        #btn-bar {
            height: 3;
            align: right middle;
            padding: 0 1;
            dock: bottom;
            background: $surface;
        }
        #btn-bar Button {
            margin: 0 1;
        }
        #btn-stop {
            background: #d32f2f;
            color: white;
        }
        #btn-stop:disabled {
            background: #7f1d1d;
            color: #999999;
        }
        #output-log {
            height: 1fr;
        }
        #hist-title, #fav-title {
            background: $surface;
            color: $text;
            text-style: bold;
            height: 1;
            padding: 0 1;
        }
        .hist-item {
            width: 100%;
            margin: 0 0 1 0;
        }
        .hist-empty, .fav-empty {
            padding: 2;
            color: $text-disabled;
        }
        .fav-row {
            height: auto;
            max-height: 4;
        }
        .fav-item {
            width: 1fr;
        }
        .fav-del {
            width: 5;
            min-width: 5;
        }
        """

        def on_mount(self):
            self.install_screen(DocScreen(), name="doc")
            self.install_screen(MainScreen(), name="main")
            self.push_screen("doc")

    app = NbCmdTuiApp()
    app.run()
