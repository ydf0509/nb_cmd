# -*- coding: utf-8 -*-
"""
Web UI 模式 —— 自动生成 Web 界面，支持命令行输入 + 参数表单 + 实时控制台。
需要安装: pip install fastapi uvicorn websockets
"""
import asyncio
import inspect
import json
import os
import sys
import threading
import time

from ..core.discovery import discover_commands
from ..core.result_handler import handle_api_result


def start_web_server(instance, base_cls, host=None, port=None):
    """启动 Web UI 服务"""
    try:
        from fastapi import FastAPI
        from fastapi.responses import HTMLResponse
        from fastapi.middleware.cors import CORSMiddleware
        from starlette.websockets import WebSocket, WebSocketDisconnect
        import uvicorn
    except ImportError:
        print("Web UI模式需要安装 fastapi, uvicorn 和 websockets:")
        print("  pip install fastapi uvicorn websockets")
        return

    meta = getattr(instance.__class__, 'Meta', type('Meta', (), {}))
    title = getattr(meta, 'web_title', None) or getattr(meta, 'name', None) or instance.__class__.__name__
    version = getattr(meta, 'version', None) or '0.0.1'
    theme = getattr(meta, 'web_theme', 'light')

    if host is None:
        host = getattr(meta, 'serve_host', '0.0.0.0')
    if port is None:
        port = getattr(meta, 'serve_port', 8080)

    app = FastAPI(title=title, version=version)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    from ..ui import colors as _colors_mod
    _colors_mod._COLOR_ENABLED = True

    _enable_exec = getattr(meta, 'enable_exec', True)
    _allow_methods = getattr(meta, 'allow_method_list', None)
    _hide_methods = getattr(meta, 'hide_method_list', None)
    _auth_token = getattr(meta, 'auth_token', None)
    _timeout = getattr(meta, 'timeout', 0)
    commands = discover_commands(instance, base_cls, enable_exec=_enable_exec,
                                 allow_method_list=_allow_methods,
                                 hide_method_list=_hide_methods)
    description = inspect.getdoc(instance) or instance.__class__.__name__

    from ..core._io_dispatch import _tls, install as _install_io
    _install_io()

    static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ui', 'static')
    has_built_frontend = os.path.isfile(os.path.join(static_dir, 'index.html'))

    if _auth_token:
        from ..modes.api_mode import _install_auth_middleware
        _install_auth_middleware(app, _auth_token, exempt_prefixes=[
            '/api/', '/ws/', '/static/',
        ])

    from ..modes.api_mode import _register_routes as _register_pydantic_routes
    _register_pydantic_routes(app, instance, commands, base_cls=base_cls,
                              allow_method_list=_allow_methods,
                              hide_method_list=_hide_methods,
                              command_prefix='', timeout=_timeout)

    def _build_group_result(cmds_dict, command_prefix=''):
        """递归构建命令组的结构（含嵌套子命令组）"""
        result = {}
        for name, info in cmds_dict.items():
            if info.get('is_group'):
                g_cls = info['cls']
                g_kwargs = info.get('init_kwargs', {})
                group_path = '{}/{}'.format(command_prefix, name) if command_prefix else name
                try:
                    g_inst = g_cls(**g_kwargs) if g_kwargs else g_cls()
                except TypeError:
                    g_inst = g_cls.__new__(g_cls)
                g_cmds = discover_commands(g_inst, base_cls, include_builtins=False,
                                           allow_method_list=_allow_methods,
                                           hide_method_list=_hide_methods,
                                           command_prefix=group_path)
                result[name] = {
                    'type': 'group',
                    'description': info.get('doc', ''),
                    'sub_commands': _build_group_result(g_cmds, group_path),
                }
            else:
                result[name] = _build_cmd_info(info)
        return result

    @app.get('/api/commands', summary='获取所有命令及参数定义')
    async def get_commands():
        return _build_group_result(commands, '')

    init_params_info = _build_init_params_info(instance)
    _user_cls = instance.__class__

    @app.get('/api/init-params', summary='获取 __init__ 全局参数定义')
    async def get_init_params():
        result = []
        for p in init_params_info:
            result.append({
                'name': p['name'],
                'type': p['type'],
                'widget': p['widget'],
                'required': p.get('required', False),
                'default': p['default'],
                'current': _serialize_default(getattr(instance, p['name'], p['default'])),
                'choices': p['choices'],
                'description': p['description'],
            })
        return result

    @app.get('/api/help/{command}', summary='获取命令帮助')
    async def get_help(command: str):
        python_name = command.replace('-', '_')
        if python_name not in commands:
            return {"error": "未知命令: {}".format(command)}
        info = commands[python_name]
        return {
            "command": command,
            "description": info.get('full_doc', info.get('doc', '')),
        }

    import queue as _queue
    import sqlite3 as _sqlite3

    _db_path = os.path.join(os.getcwd(), 'nb_cmd_web.db')

    def _get_db():
        conn = _sqlite3.connect(_db_path)
        conn.execute('CREATE TABLE IF NOT EXISTS saved_commands '
                     '(id INTEGER PRIMARY KEY AUTOINCREMENT, '
                     'command TEXT UNIQUE NOT NULL, '
                     'created_at TEXT DEFAULT CURRENT_TIMESTAMP)')
        conn.execute('CREATE TABLE IF NOT EXISTS command_history '
                     '(id INTEGER PRIMARY KEY AUTOINCREMENT, '
                     'command TEXT NOT NULL, '
                     'executed_at TEXT DEFAULT CURRENT_TIMESTAMP)')
        return conn

    _get_db().close()

    @app.get('/api/saved-commands', summary='获取收藏命令列表')
    async def get_saved_commands():
        conn = _get_db()
        rows = conn.execute(
            'SELECT id, command, created_at FROM saved_commands ORDER BY id DESC'
        ).fetchall()
        conn.close()
        return [{'id': r[0], 'command': r[1], 'created_at': r[2]} for r in rows]

    @app.post('/api/save-command', summary='收藏命令（去重）')
    async def save_command(body: dict):
        cmd = body.get('command', '').strip()
        if not cmd:
            return {'status': 'error', 'message': '命令不能为空'}
        conn = _get_db()
        try:
            conn.execute('INSERT OR IGNORE INTO saved_commands (command) VALUES (?)', (cmd,))
            conn.commit()
        finally:
            conn.close()
        return {'status': 'ok'}

    @app.delete('/api/save-command', summary='取消收藏命令')
    async def delete_saved_command(body: dict):
        cmd = body.get('command', '').strip()
        conn = _get_db()
        try:
            conn.execute('DELETE FROM saved_commands WHERE command = ?', (cmd,))
            conn.commit()
        finally:
            conn.close()
        return {'status': 'ok'}

    @app.get('/api/history', summary='获取命令执行历史（最近1000条）')
    async def get_history():
        conn = _get_db()
        rows = conn.execute(
            'SELECT id, command, executed_at FROM command_history '
            'ORDER BY id DESC LIMIT 1000'
        ).fetchall()
        conn.close()
        return [{'id': r[0], 'command': r[1], 'executed_at': r[2]} for r in rows]

    @app.post('/api/history', summary='记录一条执行历史')
    async def post_history(body: dict):
        cmd = body.get('command', '').strip()
        if not cmd:
            return {'status': 'error'}
        conn = _get_db()
        try:
            conn.execute('INSERT INTO command_history (command) VALUES (?)', (cmd,))
            conn.execute(
                'DELETE FROM command_history WHERE id NOT IN '
                '(SELECT id FROM command_history ORDER BY id DESC LIMIT 1000)')
            conn.commit()
        finally:
            conn.close()
        return {'status': 'ok'}

    def _make_instance(raw_init_params=None):
        """每次请求创建一个新的用户类实例，彼此隔离"""
        if not init_params_info:
            inst = _user_cls()
        else:
            from ..core.type_utils import convert_value
            kwargs = {}
            for p in init_params_info:
                pname = p['name']
                if raw_init_params and pname in raw_init_params:
                    kwargs[pname] = convert_value(raw_init_params[pname], p['_real_type'])
                elif p.get('required'):
                    kwargs[pname] = getattr(instance, pname)
            inst = _user_cls(**kwargs) if kwargs else _user_cls()
        ctx = inst.make_nbctx()
        if ctx is not None:
            inst.nbctx = ctx
        return inst

    def _resolve_command(route_path, raw_init_params=None):
        """根据路由路径解析出 (method, target_instance, cmd_info)，支持多层嵌套"""
        parts = route_path.replace('-', '_').split('/')
        if len(parts) == 1:
            cmd_name = parts[0]
            if cmd_name in commands and not commands[cmd_name].get('is_group'):
                info = commands[cmd_name]
                target_inst = _make_instance(raw_init_params)
                method = getattr(target_inst, cmd_name)
                return method, target_inst, info
        elif len(parts) >= 2:
            root_inst = _make_instance(raw_init_params)
            current_cmds = commands
            current_inst = root_inst
            current_path = ''
            for i, part in enumerate(parts):
                if part not in current_cmds:
                    break
                info = current_cmds[part]
                if info.get('is_group'):
                    current_path = '{}/{}'.format(current_path, part) if current_path else part
                    g_cls = info['cls']
                    g_kwargs = info.get('init_kwargs', {})
                    try:
                        child_inst = g_cls(**g_kwargs) if g_kwargs else g_cls()
                    except TypeError:
                        child_inst = g_cls.__new__(g_cls)
                    parent_ctx = current_inst.nbctx if current_inst is not None else None
                    if parent_ctx is not None:
                        child_inst.nbctx = parent_ctx
                    current_inst = child_inst
                    current_cmds = discover_commands(current_inst, base_cls,
                                                     include_builtins=False,
                                                     allow_method_list=_allow_methods,
                                                     hide_method_list=_hide_methods,
                                                     command_prefix=current_path)
                elif i == len(parts) - 1 and current_inst is not None:
                    return info['method'], current_inst, info
        return None, None, None

    def _cancel_thread(tid):
        """向指定线程注入 KeyboardInterrupt，模拟 Ctrl+C"""
        import ctypes
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
            ctypes.c_ulong(tid), ctypes.py_object(KeyboardInterrupt))
        return res == 1

    @app.websocket('/ws/execute')
    async def ws_execute(websocket: WebSocket):
        await websocket.accept()
        cancel_event = threading.Event()
        worker_thread = None
        try:
            msg = await websocket.receive_json()
            route_path = msg.get('command', '')
            raw_kwargs = msg.get('args', {})
            raw_init_params = msg.get('init_params', None)

            method, target_inst, cmd_info = _resolve_command(
                route_path, raw_init_params)
            if method is None:
                await websocket.send_json({
                    'type': 'error', 'error': '未知命令: {}'.format(route_path)
                })
                return

            kwargs = _convert_request_params(raw_kwargs, cmd_info)
            output_q = _queue.Queue()
            result_holder = {'result': None, 'error': None, 'cancelled': False}

            def _run():
                _tls.output_queue = output_q
                saved_streams = []
                for h in target_inst.logger.handlers:
                    if hasattr(h, 'stream'):
                        saved_streams.append((h, h.stream))
                        h.stream = sys.stderr
                try:
                    target_inst.before_run()
                    r = method(**kwargs)
                    if inspect.iscoroutine(r):
                        r = asyncio.run(r)
                    result_holder['result'] = handle_api_result(r)
                except KeyboardInterrupt:
                    result_holder['cancelled'] = True
                except Exception as exc:
                    if cancel_event.is_set():
                        result_holder['cancelled'] = True
                    else:
                        result_holder['error'] = str(exc)
                        target_inst.on_error(route_path, exc)
                finally:
                    for h, orig in saved_streams:
                        h.stream = orig
                    _tls.output_queue = None
                    target_inst.after_run()
                    output_q.put(None)

            t = threading.Thread(target=_run, daemon=True)
            worker_thread = t
            start_ts = time.time()
            t.start()

            if _timeout > 0:
                def _auto_timeout():
                    if not cancel_event.wait(_timeout):
                        cancel_event.set()
                        if t.is_alive() and t.ident:
                            _cancel_thread(t.ident)
                        result_holder['error'] = '命令执行超时（{} 秒）'.format(_timeout)
                _timer = threading.Thread(target=_auto_timeout, daemon=True)
                _timer.start()

            async def _listen_cancel():
                """后台监听客户端的取消消息"""
                try:
                    while not cancel_event.is_set():
                        client_msg = await asyncio.wait_for(
                            websocket.receive_json(), timeout=0.1)
                        if client_msg.get('action') == 'cancel':
                            cancel_event.set()
                            if t.is_alive() and t.ident:
                                _cancel_thread(t.ident)
                            return
                except asyncio.TimeoutError:
                    pass
                except (WebSocketDisconnect, Exception):
                    cancel_event.set()

            while True:
                listen_task = asyncio.ensure_future(_listen_cancel())
                try:
                    item = output_q.get(timeout=0.05)
                    if item is None:
                        listen_task.cancel()
                        break
                    stream_type, data = item
                    await websocket.send_json({'type': stream_type, 'data': data})
                except _queue.Empty:
                    if not t.is_alive():
                        while not output_q.empty():
                            item = output_q.get_nowait()
                            if item is None:
                                break
                            await websocket.send_json({
                                'type': item[0], 'data': item[1]
                            })
                        listen_task.cancel()
                        break
                    await asyncio.sleep(0.02)
                finally:
                    if not listen_task.done():
                        listen_task.cancel()

            t.join(timeout=2)
            duration = int((time.time() - start_ts) * 1000)

            if result_holder['cancelled'] or cancel_event.is_set():
                await websocket.send_json({
                    'type': 'cancelled',
                    'duration_ms': duration,
                })
            elif result_holder['error']:
                await websocket.send_json({
                    'type': 'error',
                    'error': result_holder['error'],
                    'duration_ms': duration,
                })
            else:
                await websocket.send_json({
                    'type': 'complete',
                    'result': result_holder['result'],
                    'duration_ms': duration,
                })
        except WebSocketDisconnect:
            cancel_event.set()
            if worker_thread and worker_thread.is_alive() and worker_thread.ident:
                _cancel_thread(worker_thread.ident)
        except Exception:
            pass

    if has_built_frontend:
        from fastapi.staticfiles import StaticFiles
        app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
    else:
        html_content = _generate_builtin_html(title, version, description, theme, _enable_exec)

        @app.get('/', response_class=HTMLResponse, include_in_schema=False)
        async def index():
            return html_content

    print('Web UI启动在 http://{}:{}'.format(host, port))
    print('API文档: http://{}:{}/docs'.format(host, port))
    uvicorn.run(app, host=host, port=port)


def _serialize_default(value):
    """将默认值转换为 JSON 可序列化的形式"""
    if value is inspect.Parameter.empty or value is None:
        return None
    import enum
    from pathlib import Path
    if isinstance(value, enum.Enum):
        return value.value
    if isinstance(value, Path):
        return str(value)
    try:
        json.dumps(value)
        return value
    except (TypeError, ValueError):
        return str(value)


def _build_init_params_info(instance):
    """提取 __init__ 中带默认值的参数，返回前端所需的参数定义列表"""
    from ..core.arg import unwrap_arg
    from ..core.type_utils import (
        type_display_name, is_enum_type, unwrap_optional,
        is_optional as _is_opt, is_list_type, get_choices,
    )

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
        type_name = type_display_name(unwrapped)
        choices = get_choices(real_type)

        widget = 'text'
        if unwrapped is bool:
            widget = 'checkbox'
        elif unwrapped is int:
            widget = 'number'
        elif unwrapped is float:
            widget = 'number'
        elif is_enum_type(unwrapped):
            widget = 'select'
        elif is_list_type(unwrapped):
            widget = 'tags'

        desc = arg_inst.desc if arg_inst and arg_inst.desc else ''

        params.append({
            'name': pname,
            'type': type_name,
            'widget': widget,
            'required': not has_default,
            'default': _serialize_default(param.default) if has_default else None,
            'choices': choices,
            'description': desc,
            '_real_type': real_type,
        })
    return params


def _build_cmd_info(info):
    """将一条 discover_commands 返回的命令信息转为前端所需的格式"""
    from ..core.type_utils import (
        type_display_name, is_enum_type, unwrap_optional,
        is_optional as _is_opt, is_list_type,
        get_choices,
    )
    arg_meta = info.get('arg_meta', {})
    params = []
    for pname, param in info['signature'].parameters.items():
        if pname == 'self':
            continue
        ptype = info['type_hints'].get(pname, str)
        has_default = param.default is not inspect.Parameter.empty
        is_kw_only = param.kind == inspect.Parameter.KEYWORD_ONLY

        real_type = unwrap_optional(ptype)
        type_name = type_display_name(real_type)
        choices = get_choices(ptype)

        widget = 'text'
        if real_type is bool:
            widget = 'checkbox'
        elif real_type is int:
            widget = 'number'
        elif real_type is float:
            widget = 'number'
        elif is_enum_type(real_type):
            widget = 'select'
        elif is_list_type(real_type):
            widget = 'tags'

        arg_inst = arg_meta.get(pname)
        desc = arg_inst.desc if arg_inst and arg_inst.desc else ''

        params.append({
            'name': pname,
            'type': type_name,
            'widget': widget,
            'required': not has_default and not is_kw_only,
            'default': _serialize_default(param.default if has_default else None),
            'choices': choices,
            'optional': _is_opt(ptype),
            'description': desc,
        })
    return {
        'type': 'command',
        'description': info.get('doc', ''),
        'full_doc': info.get('full_doc', ''),
        'parameters': params,
    }


def _convert_request_params(request, cmd_info):
    """将 HTTP 请求参数转换为方法调用参数"""
    from ..core.type_utils import convert_value
    sig = cmd_info['signature']
    hints = cmd_info.get('type_hints', {})
    kwargs = {}
    for pname, param in sig.parameters.items():
        if pname == 'self':
            continue
        if pname in request:
            ptype = hints.get(pname, str)
            kwargs[pname] = convert_value(request[pname], ptype)
        elif param.default is not inspect.Parameter.empty:
            kwargs[pname] = param.default
    return kwargs


def _generate_builtin_html(title, version, description, theme, enable_exec=True):
    """生成内置的 Web UI HTML 页面（当没有 Vue 前端构建产物时使用）"""
    dark_css = """
        :root { --bg: #1a1a2e; --card-bg: #16213e; --text: #e0e0e0; --border: #0f3460;
                --primary: #0097e6; --primary-hover: #00b4d8; --input-bg: #0f3460;
                --console-bg: #0d1b2a; --success: #2ecc71; --warning: #f39c12;
                --error: #e74c3c; --info: #3498db; --hover-bg: #1b2838; }
    """ if theme == 'dark' else """
        :root { --bg: #f5f6fa; --card-bg: #ffffff; --text: #2c3e50; --border: #dcdde1;
                --primary: #0097e6; --primary-hover: #0078b8; --input-bg: #ffffff;
                --console-bg: #1e272e; --success: #2ecc71; --warning: #f39c12;
                --error: #e74c3c; --info: #3498db; --hover-bg: #f0f0f0; }
    """

    return '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>''' + title + '''</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
''' + dark_css + '''
body { font-family: -apple-system, "Segoe UI", "Microsoft YaHei", sans-serif;
       background: var(--bg); color: var(--text); height: 100vh; display: flex; flex-direction: column; }
.header { padding: 12px 24px; border-bottom: 1px solid var(--border); display: flex;
           align-items: center; justify-content: space-between; background: var(--card-bg); }
.header h1 { font-size: 18px; }
.header .version { color: var(--primary); font-size: 13px; }
.main { flex: 1; display: flex; overflow: hidden; }
.left-panel { width: 45%; min-width: 200px; display: flex; flex-direction: column; overflow: hidden; }
.resizer { width: 5px; cursor: col-resize; background: var(--border); flex-shrink: 0;
           transition: background 0.15s; }
.resizer:hover, .resizer.active { background: var(--primary); }
.right-panel { flex: 1; min-width: 200px; display: flex; flex-direction: column; overflow: hidden; }
.cmd-input-area { padding: 16px; border-bottom: 1px solid var(--border); background: var(--card-bg); }
.cmd-input-area label { font-size: 13px; color: var(--info); margin-bottom: 6px; display: block; }
.cmd-input-wrapper { display: flex; align-items: center; background: var(--input-bg);
                      border: 1px solid var(--border); border-radius: 6px; padding: 0 12px; }
.cmd-input-wrapper span.prompt { color: var(--primary); font-family: monospace; margin-right: 8px; font-weight: bold; }
.cmd-input-wrapper input { flex: 1; border: none; outline: none; background: transparent;
                            color: var(--text); font-family: monospace; font-size: 15px; padding: 10px 0; }
.cmd-input-wrapper button { background: var(--primary); color: #fff; border: none; padding: 6px 16px;
                             border-radius: 4px; cursor: pointer; font-size: 13px; margin-left: 8px; }
.cmd-input-wrapper button:hover { background: var(--primary-hover); }
.form-area { flex: 1; overflow-y: auto; padding: 0; }
.form-section { border-bottom: 1px solid var(--border); }
.form-section-header { padding: 10px 16px; cursor: pointer; display: flex; align-items: center;
                        justify-content: space-between; background: var(--card-bg); }
.form-section-header:hover { background: var(--hover-bg); }
.form-section-header .cmd-name { font-weight: bold; font-size: 14px; }
.form-section-header .cmd-desc { font-size: 12px; color: #888; margin-left: 8px; }
.form-section-body { padding: 12px 16px; display: none; background: var(--bg); }
.form-section-body.open { display: block; }
.form-group { margin-bottom: 10px; display: flex; align-items: center; }
.form-group label { min-width: 120px; font-size: 13px; text-align: right; padding-right: 12px; white-space: nowrap; }
.form-group input, .form-group select { flex: 1; padding: 6px 10px; border: 1px solid var(--border);
                                          border-radius: 4px; background: var(--input-bg); color: var(--text);
                                          font-size: 13px; }
.form-group input[type=checkbox] { flex: none; width: 18px; height: 18px; }
.form-actions { margin-top: 8px; display: flex; gap: 8px; justify-content: flex-end; }
.form-actions button { padding: 6px 14px; border-radius: 4px; border: 1px solid var(--border);
                        cursor: pointer; font-size: 13px; background: var(--card-bg); color: var(--text); }
.form-actions button.primary { background: var(--primary); color: #fff; border-color: var(--primary); }
.console-area { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
.console-label { padding: 8px 16px; font-size: 13px; color: var(--info); background: var(--card-bg);
                  border-bottom: 1px solid var(--border); }
.console-output { flex: 1; background: var(--console-bg); color: #a8e6cf; font-family: "Consolas","Courier New",monospace;
                   font-size: 13px; line-height: 1.6; padding: 12px 16px; overflow-y: auto; white-space: pre-wrap; word-break: break-all; }
.console-output .ts { color: #636e72; }
.console-output .cmd-echo { color: var(--primary); }
.console-output .err { color: var(--error); }
.console-output .ok { color: var(--success); }
.status-bar { padding: 6px 16px; font-size: 12px; border-top: 1px solid var(--border);
               background: var(--card-bg); display: flex; justify-content: space-between; color: #888; }
.arrow { transition: transform 0.2s; } .arrow.open { transform: rotate(90deg); }
.save-cmd-btn { background: transparent; color: #888; border: none; font-size: 18px; cursor: pointer;
               padding: 4px 8px; margin-left: 4px; line-height: 1; }
.save-cmd-btn:hover { color: #ffd740; }
.s2-wrap { display: flex; flex-direction: column; gap: 6px; padding: 6px 16px; background: var(--card-bg); border-bottom: 1px solid var(--border); }
.s2-box { position: relative; flex: 1; }
.s2-trigger { display: flex; align-items: center; gap: 6px; padding: 7px 10px; border: 1px solid var(--border);
              border-radius: 4px; background: var(--input-bg); cursor: pointer; font-size: 13px;
              transition: border-color 0.15s; user-select: none; }
.s2-trigger:hover { border-color: var(--primary); }
.s2-box.open .s2-trigger { border-color: var(--primary); border-radius: 4px 4px 0 0; }
.s2-icon { flex-shrink: 0; font-size: 14px; }
.s2-label { flex-shrink: 0; font-size: 13px; }
.s2-count { font-size: 11px; color: #888; background: var(--bg); padding: 0 6px; border-radius: 8px; margin-left: auto; }
.s2-arrow { flex-shrink: 0; font-size: 10px; color: #888; transition: transform 0.2s; }
.s2-box.open .s2-arrow { transform: rotate(180deg); }
.s2-drop { display: none; position: absolute; top: 100%; left: 0; right: 0; z-index: 1000;
           background: var(--card-bg); border: 1px solid var(--primary); border-top: none;
           border-radius: 0 0 4px 4px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
.s2-box.open .s2-drop { display: block; }
.s2-search { width: 100%; padding: 7px 10px; border: none; border-bottom: 1px solid var(--border);
             outline: none; background: var(--input-bg); color: var(--text); font-size: 12px; box-sizing: border-box; }
.s2-list { max-height: 200px; overflow-y: auto; }
.s2-item { padding: 6px 10px; cursor: pointer; font-family: monospace; font-size: 12px;
           display: flex; align-items: center; white-space: nowrap; overflow: hidden; }
.s2-item:hover { background: var(--hover-bg); }
.s2-item .s2-iico { margin-right: 6px; flex-shrink: 0; font-size: 11px; }
.s2-item .s2-itxt { flex: 1; overflow: hidden; text-overflow: ellipsis; }
.s2-item .s2-idel { flex-shrink: 0; margin-left: 6px; color: #888; cursor: pointer;
                     border: none; background: none; font-size: 13px; padding: 0 4px; }
.s2-item .s2-idel:hover { color: var(--error); }
.s2-empty { padding: 10px; font-size: 11px; color: #636e72; text-align: center; }
button:disabled, .form-actions button:disabled { opacity: 0.4; cursor: not-allowed; }
.clear-btn { background: transparent; color: #888; border: 1px solid var(--border); padding: 2px 10px;
             border-radius: 4px; cursor: pointer; font-size: 12px; margin-left: 12px; }
.clear-btn:hover { color: #fff; background: var(--error); border-color: var(--error); }
.stop-btn { display: none; background: var(--error); color: #fff; border: none; padding: 2px 10px;
            border-radius: 4px; cursor: pointer; font-size: 12px; margin-left: 8px; }
.stop-btn:hover { opacity: 0.85; }
.stop-btn.visible { display: inline-block; }
</style>
</head>
<body>
<div class="header">
  <h1>''' + title + ''' <span class="version">v''' + version + '''</span></h1>
  <span>''' + description + '''</span>
</div>
<div class="main">
  <div class="left-panel">
    <div class="cmd-input-area">
      <label>&#128421; 命令行输入</label>
      <div class="cmd-input-wrapper">
        <span class="prompt">$</span>
        <input id="cmdInput" type="text" placeholder="输入命令..." autofocus autocomplete="off" />
        <button onclick="executeFromInput()">执行</button>
        <button class="save-cmd-btn" onclick="saveCurrentCmd()" onmousedown="event.preventDefault()" title="收藏当前命令">&#9733;</button>
      </div>
    </div>
    <div class="s2-wrap">
      <div class="s2-box" id="s2Saved">
        <div class="s2-trigger" onclick="toggleS2('s2Saved')">
          <span class="s2-icon" style="color:#ffd740;">&#9733;</span>
          <span class="s2-label">收藏</span>
          <span class="s2-count" id="savedCount">0</span>
          <span class="s2-arrow">&#9662;</span>
        </div>
        <div class="s2-drop" onmousedown="event.stopPropagation()">
          <input class="s2-search" id="savedSearch" type="text" placeholder="搜索收藏..." oninput="renderSaved()" />
          <div class="s2-list" id="savedBody"></div>
        </div>
      </div>
      <div class="s2-box" id="s2Hist">
        <div class="s2-trigger" onclick="toggleS2('s2Hist')">
          <span class="s2-icon" style="color:#82b1ff;">&#128339;</span>
          <span class="s2-label">历史</span>
          <span class="s2-count" id="histCount">0</span>
          <span class="s2-arrow">&#9662;</span>
        </div>
        <div class="s2-drop" onmousedown="event.stopPropagation()">
          <input class="s2-search" id="histSearch" type="text" placeholder="搜索历史..." oninput="renderHist()" />
          <div class="s2-list" id="histBody"></div>
        </div>
      </div>
    </div>
    <div id="initParamsArea" style="display:none;"></div>
    <div class="form-area" id="formArea">
      <p style="padding:16px;color:#888;">加载中...</p>
    </div>
  </div>
  <div class="resizer" id="resizer"></div>
  <div class="right-panel">
    <div class="console-area">
      <div class="console-label">&#128203; 实时控制台输出<button class="clear-btn" onclick="clearConsole()" title="清空控制台">&#128465; 清空</button><button class="stop-btn" id="stopBtn" onclick="cancelExecution()" title="停止执行">&#9632; 停止</button></div>
      <div class="console-output" id="consoleOutput"></div>
    </div>
  </div>
</div>
<div class="status-bar">
  <span id="statusText">状态: 就绪</span>
  <span id="execCount">执行次数: 0</span>
</div>

<script>
let commands = {};
let initParamNames = [];
let enableExec = ''' + ('true' if enable_exec else 'false') + ''';
let history = [];
let historyIdx = -1;
let execCount = 0;
let isExecuting = false;
let activeWs = null;

function setExecuting(running) {
  isExecuting = running;
  var btns = document.querySelectorAll('.form-actions button.primary, .cmd-input-wrapper button');
  btns.forEach(function(b) { b.disabled = running; });
  var stopBtn = document.getElementById('stopBtn');
  if (running) { stopBtn.classList.add('visible'); } else { stopBtn.classList.remove('visible'); }
}

function cancelExecution() {
  if (activeWs && activeWs.readyState === WebSocket.OPEN) {
    activeWs.send(JSON.stringify({action: 'cancel'}));
  }
}

function clearConsole() {
  document.getElementById('consoleOutput').innerHTML = '';
}

function esc(s) { var d=document.createElement('div'); d.textContent=String(s); return d.innerHTML; }

function ansiToHtml(raw) {
  var fgMap = {
    '30':'#b0bec5','31':'#ff6b6b','32':'#69f0ae','33':'#ffd740',
    '34':'#82b1ff','35':'#b388ff','36':'#84ffff','37':'#ffffff',
    '90':'#cfd8dc','91':'#ff1744','92':'#76ff03','93':'#ffff00',
    '94':'#40c4ff','95':'#ea80fc','96':'#18ffff','97':'#ffffff'
  };
  var bgMap = {
    '40':'#90a4ae','41':'#ff5252','42':'#69f0ae','43':'#ffff00',
    '44':'#448aff','45':'#7c4dff','46':'#18ffff','47':'#e0e0e0',
    '100':'#b0bec5','101':'#ff8a80','102':'#b9f6ca','103':'#ffff8d',
    '104':'#82b1ff','105':'#b388ff','106':'#84ffff','107':'#eeeeee'
  };
  var bgTxt = {
    '40':'#fff','41':'#fff','42':'#000','43':'#000',
    '44':'#fff','45':'#fff','46':'#000','47':'#000',
    '100':'#000','101':'#000','102':'#000','103':'#000',
    '104':'#000','105':'#000','106':'#000','107':'#000'
  };
  var parts = String(raw).split(/\\x1b\\[([0-9;]*)m/);
  var html = '', spans = 0;
  for (var i = 0; i < parts.length; i++) {
    if (i % 2 === 0) {
      html += esc(parts[i]);
    } else {
      var codes = parts[i].split(';');
      for (var j = 0; j < codes.length; j++) {
        var c = codes[j];
        if (c === '0' || c === '') {
          while (spans > 0) { html += '</span>'; spans--; }
        } else if (c === '1') {
          html += '<span style="font-weight:bold">'; spans++;
        } else if (c === '4') {
          html += '<span style="text-decoration:underline">'; spans++;
        } else if (fgMap[c]) {
          html += '<span style="color:' + fgMap[c] + '">'; spans++;
        } else if (bgMap[c]) {
          html += '<span style="background:' + bgMap[c] + ';color:' + (bgTxt[c]||'#fff') + ';padding:2px 6px;border-radius:3px">'; spans++;
        }
      }
    }
  }
  while (spans > 0) { html += '</span>'; spans--; }
  return html;
}

function findCmdInfo(pyName) {
  var parts = pyName.split('/');
  var node = commands;
  for (var i = 0; i < parts.length; i++) {
    if (!node || !node[parts[i]]) return null;
    if (i === parts.length - 1) return node[parts[i]];
    if (node[parts[i]].type === 'group' && node[parts[i]].sub_commands) {
      node = node[parts[i]].sub_commands;
    } else {
      return null;
    }
  }
  return null;
}

async function loadCommands() {
  try {
    const resp = await fetch('/api/commands');
    commands = await resp.json();
    renderForms();
  } catch(e) { console.error(e); }
}

async function loadInitParams() {
  try {
    var resp = await fetch('/api/init-params');
    var params = await resp.json();
    if (!params || params.length === 0) return;
    initParamNames = params.map(function(p) { return p.name; });
    var area = document.getElementById('initParamsArea');
    area.style.display = 'block';
    var html = '<div class="form-section"><div class="form-section-header" onclick="toggleSection(this)">';
    html += '<span><span class="arrow open">&#9654;</span> <span class="cmd-name" style="color:var(--warning);">&#9881; 全局选项</span>';
    html += '<span class="cmd-desc">__init__ 参数，每次执行自动携带</span></span></div>';
    html += '<div class="form-section-body open" id="initParamsForm">';
    params.forEach(function(p) {
      var descHtml = p.description ? '<span style="font-size:11px;color:#888;margin-left:4px;">' + esc(p.description) + '</span>' : '';
      html += '<div class="form-group"><label>' + p.name + (p.required?' *':'') + ':' + descHtml + '</label>';
      var val = p.current != null ? p.current : (p.default != null ? p.default : '');
      if (p.widget === 'checkbox') {
        html += '<input type="checkbox" data-init-param="' + p.name + '"' + (val ? ' checked' : '') + '/>';
      } else if (p.widget === 'select' && p.choices) {
        html += '<select data-init-param="' + p.name + '">';
        p.choices.forEach(function(c) {
          html += '<option value="' + c + '"' + (c == val ? ' selected' : '') + '>' + c + '</option>';
        });
        html += '</select>';
      } else if (p.widget === 'number') {
        html += '<input type="number" data-init-param="' + p.name + '" value="' + val + '"/>';
      } else {
        html += '<input type="text" data-init-param="' + p.name + '" value="' + val + '"/>';
      }
      html += '</div>';
    });
    html += '</div></div>';
    area.innerHTML = html;
  } catch(e) { console.error(e); }
}

function getInitParams() {
  var form = document.getElementById('initParamsForm');
  if (!form) return null;
  var data = {};
  var hasAny = false;
  form.querySelectorAll('[data-init-param]').forEach(function(el) {
    var name = el.dataset.initParam;
    if (el.type === 'checkbox') { data[name] = el.checked; hasAny = true; }
    else if (el.type === 'number' && el.value !== '') { data[name] = Number(el.value); hasAny = true; }
    else if (el.value !== '') { data[name] = el.value; hasAny = true; }
  });
  return hasAny ? data : null;
}

function renderParamFields(params) {
  var html = '';
  if (!params) return html;
  params.forEach(function(p) {
    var descHtml = p.description ? '<span style="font-size:11px;color:#888;margin-left:4px;">' + esc(p.description) + '</span>' : '';
    html += '<div class="form-group"><label>' + p.name + (p.required?' *':'') + ':' + descHtml + '</label>';
    var ph = p.description || p.type;
    if (p.widget === 'checkbox') {
      html += '<input type="checkbox" data-param="' + p.name + '"' + (p.default?' checked':'') + '/>';
    } else if (p.widget === 'select' && p.choices) {
      html += '<select data-param="' + p.name + '">';
      p.choices.forEach(function(c) {
        html += '<option value="' + c + '"' + (c==p.default?' selected':'') + '>' + c + '</option>';
      });
      html += '</select>';
    } else if (p.widget === 'number') {
      html += '<input type="number" data-param="' + p.name + '" placeholder="' + esc(ph) + '" value="' + (p.default!=null?p.default:'') + '"/>';
    } else {
      html += '<input type="text" data-param="' + p.name + '" placeholder="' + esc(ph) + '" value="' + (p.default!=null?p.default:'') + '"/>';
    }
    html += '</div>';
  });
  return html;
}

function renderCmdSection(formId, cliLabel, description, params) {
  var html = '<div class="form-section"><div class="form-section-header" onclick="toggleSection(this)">';
  html += '<span><span class="arrow">&#9654;</span> <span class="cmd-name">' + cliLabel + '</span>';
  html += '<span class="cmd-desc">' + (description||'') + '</span></span></div>';
  html += '<div class="form-section-body" id="form_' + formId + '">';
  html += renderParamFields(params);
  html += '<div class="form-actions">';
  html += '<button onclick="generateCmd(\\'' + formId + '\\')">生成命令</button>';
  html += '<button class="primary" onclick="executeForm(\\'' + formId + '\\')">直接执行</button>';
  html += '</div></div></div>';
  return html;
}

function renderGroup(cmds, prefix) {
  var html = '';
  for (var [name, info] of Object.entries(cmds)) {
    var cliName = name.replace(/_/g, '-');
    var fullPrefix = prefix ? prefix + '/' + name : name;
    var fullLabel = prefix ? prefix.replace(/_/g,'-').replace(/\\//g,' ') + ' ' + cliName : cliName;
    if (info.type === 'group') {
      html += '<div class="form-section"><div class="form-section-header" onclick="toggleSection(this)">';
      html += '<span><span class="arrow">&#9654;</span> <span class="cmd-name" style="color:var(--primary);">' + fullLabel + '</span>';
      html += '<span class="cmd-desc">[组] ' + (info.description||'') + '</span></span></div>';
      html += '<div class="form-section-body">';
      if (info.sub_commands) { html += renderGroup(info.sub_commands, fullPrefix); }
      html += '</div></div>';
    } else {
      html += renderCmdSection(fullPrefix, fullLabel, info.description, info.parameters);
    }
  }
  return html;
}

function renderForms() {
  const area = document.getElementById('formArea');
  var html = renderGroup(commands, '');
  area.innerHTML = html || '<p style="padding:16px;color:#888;">无可用命令</p>';
}

function toggleSection(el) {
  const body = el.nextElementSibling;
  const arrow = el.querySelector('.arrow');
  body.classList.toggle('open');
  arrow.classList.toggle('open');
}

function getFormData(formId) {
  const form = document.getElementById('form_' + formId);
  if (!form) return {};
  const data = {};
  form.querySelectorAll('[data-param]').forEach(function(el) {
    const name = el.dataset.param;
    if (el.type === 'checkbox') { data[name] = el.checked; }
    else if (el.type === 'number' && el.value) { data[name] = Number(el.value); }
    else if (el.value) { data[name] = el.value; }
  });
  return data;
}

function generateCmd(formId) {
  var data = getFormData(formId);
  var cliName = formId.replace(/_/g, '-').replace('/', ' ');
  var parts = cliName.split(' ');
  var pyName = formId.replace(/-/g, '_');
  var info = findCmdInfo(pyName);
  if (info && info.parameters) {
    info.parameters.forEach(function(p) {
      if (p.name in data) {
        if (p.required && p.widget !== 'checkbox') {
          parts.push(String(data[p.name]));
        } else if (p.widget === 'checkbox') {
          if (data[p.name]) parts.push('--' + p.name.replace(/_/g, '-'));
        } else {
          parts.push('--' + p.name.replace(/_/g, '-') + ' ' + String(data[p.name]));
        }
      }
    });
  }
  var initP = getInitParams();
  if (initP) {
    Object.entries(initP).forEach(function(e) {
      if (typeof e[1] === 'boolean') {
        if (e[1]) parts.push('--' + e[0].replace(/_/g, '-'));
      } else {
        parts.push('--' + e[0].replace(/_/g, '-'));
        parts.push(String(e[1]));
      }
    });
  }
  document.getElementById('cmdInput').value = parts.join(' ');
  document.getElementById('cmdInput').focus();
}

async function executeForm(formId) {
  var data = getFormData(formId);
  var routePath = formId.replace(/_/g, '-');
  await doExecute(routePath, data);
}

async function executeFromInput() {
  const input = document.getElementById('cmdInput');
  const raw = input.value.trim();
  if (!raw) return;
  const parts = raw.split(/\\s+/);
  const firstPy = parts[0].replace(/-/g, '_');
  var routePath, cmdInfo, argStart;
  if (commands[firstPy] && commands[firstPy].type === 'group' && parts.length > 1) {
    var subPy = parts[1].replace(/-/g, '_');
    var grpInfo = commands[firstPy];
    cmdInfo = grpInfo.sub_commands ? grpInfo.sub_commands[subPy] : null;
    routePath = parts[0] + '/' + parts[1];
    argStart = 2;
  } else if (commands[firstPy]) {
    cmdInfo = commands[firstPy];
    routePath = parts[0];
    argStart = 1;
  } else if (enableExec) {
    await doExecute('exec', {cmd: raw});
    return;
  } else {
    appendLog('[错误] 未知命令: ' + parts[0], 'error');
    return;
  }
  const kwargs = {};
  const inputInitP = {};
  if (cmdInfo && cmdInfo.parameters) {
    let posIdx = 0;
    const positionals = cmdInfo.parameters.filter(function(p){return p.required;});
    for (let i = argStart; i < parts.length; i++) {
      if (parts[i].startsWith('--')) {
        const flag = parts[i].substring(2).replace(/-/g, '_');
        if (initParamNames.indexOf(flag) >= 0) {
          if (i + 1 < parts.length && !parts[i+1].startsWith('--')) { i++; inputInitP[flag] = parts[i]; }
          continue;
        }
        const param = cmdInfo.parameters.find(function(p){return p.name === flag;});
        if (param && param.widget === 'checkbox') { kwargs[flag] = true; }
        else if (i + 1 < parts.length) { i++; kwargs[flag] = parts[i]; }
      } else {
        if (posIdx < positionals.length) {
          kwargs[positionals[posIdx].name] = parts[i]; posIdx++;
        } else if (positionals.length > 0) {
          var lastP = positionals[positionals.length - 1].name;
          kwargs[lastP] += ' ' + parts[i];
        }
      }
    }
  }
  var overrideInit = Object.keys(inputInitP).length > 0 ? inputInitP : null;
  await doExecute(routePath, kwargs, overrideInit);
}

function doExecute(routePath, kwargs, initParamsOverride) {
  if (isExecuting) return;
  setExecuting(true);
  var consoleEl = document.getElementById('consoleOutput');
  var ts = new Date().toLocaleTimeString();
  var initP = initParamsOverride || getInitParams();
  var cmdStr = routePath.replace(/\\//g, ' ');
  Object.entries(kwargs).forEach(function(e) {
    if (typeof e[1] === 'boolean') { if(e[1]) cmdStr += ' --' + e[0].replace(/_/g,'-'); }
    else cmdStr += ' --' + e[0].replace(/_/g,'-') + ' ' + e[1];
  });

  function _finish(statusMsg) {
    setExecuting(false);
    activeWs = null;
    document.getElementById('statusText').innerText = statusMsg;
  }

  consoleEl.innerHTML += '<span class="ts">[' + ts + ']</span> <span class="cmd-echo">$ ' + cmdStr + '</span>\\n';
  document.getElementById('statusText').innerText = '状态: 执行中... ' + cmdStr;

  var wsProto = location.protocol === 'https:' ? 'wss:' : 'ws:';
  var wsUrl = wsProto + '//' + location.host + '/ws/execute';

  try {
    var ws = new WebSocket(wsUrl);
    activeWs = ws;
    ws.onopen = function() {
      var payload = {command: routePath, args: kwargs};
      if (initP) payload.init_params = initP;
      ws.send(JSON.stringify(payload));
    };
    ws.onmessage = function(event) {
      var msg = JSON.parse(event.data);
      if (msg.type === 'stdout') {
        consoleEl.innerHTML += ansiToHtml(msg.data);
      } else if (msg.type === 'stderr') {
        consoleEl.innerHTML += ansiToHtml(msg.data);
      } else if (msg.type === 'complete') {
        if (msg.result != null) {
          var resultStr = typeof msg.result === 'object'
            ? JSON.stringify(msg.result, null, 2) : String(msg.result);
          consoleEl.innerHTML += '<span class="ok">' + esc(resultStr) + '</span>\\n';
        }
        consoleEl.innerHTML += '<span class="ok">[完成] ' + (msg.duration_ms||0) + 'ms</span>\\n\\n';
        execCount++;
        document.getElementById('execCount').innerText = '执行次数: ' + execCount;
        _finish('状态: 就绪  |  最后执行: ' + cmdStr + ' ' + ts);
      } else if (msg.type === 'cancelled') {
        consoleEl.innerHTML += '<span class="err">[已取消] ' + (msg.duration_ms||0) + 'ms</span>\\n\\n';
        _finish('状态: 就绪  |  已取消: ' + cmdStr);
      } else if (msg.type === 'error') {
        consoleEl.innerHTML += '<span class="err">[错误] ' + esc(msg.error||'未知错误') + '</span>\\n\\n';
        _finish('状态: 就绪  |  出错: ' + cmdStr);
      }
      consoleEl.scrollTop = consoleEl.scrollHeight;
    };
    ws.onerror = function() {
      setExecuting(false); activeWs = null;
      _doExecuteFallback(routePath, kwargs, cmdStr, ts);
    };
    ws.onclose = function() {
      if (isExecuting) { setExecuting(false); activeWs = null; }
    };
  } catch(e) {
    setExecuting(false); activeWs = null;
    _doExecuteFallback(routePath, kwargs, cmdStr, ts);
  }
  addHistory(cmdStr);
}

function _doExecuteFallback(routePath, kwargs, cmdStr, ts) {
  var consoleEl = document.getElementById('consoleOutput');
  fetch('/' + routePath, {
    method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(kwargs)
  }).then(function(resp) { return resp.json(); }).then(function(data) {
    if (data.stdout) consoleEl.innerHTML += ansiToHtml(data.stdout);
    if (data.stderr) consoleEl.innerHTML += ansiToHtml(data.stderr);
    if (data.status === 'success') {
      if (data.result != null) {
        var resultStr = typeof data.result === 'object'
          ? JSON.stringify(data.result, null, 2) : String(data.result);
        consoleEl.innerHTML += '<span class="ok">' + esc(resultStr) + '</span>\\n';
      }
      consoleEl.innerHTML += '<span class="ok">[完成] ' + (data.duration_ms||0) + 'ms</span>\\n\\n';
    } else {
      consoleEl.innerHTML += '<span class="err">[错误] ' + esc(data.error||'未知错误') + '</span>\\n\\n';
    }
    execCount++;
    document.getElementById('execCount').innerText = '执行次数: ' + execCount;
    document.getElementById('statusText').innerText = '状态: 就绪  |  最后执行: ' + cmdStr + ' ' + ts;
    consoleEl.scrollTop = consoleEl.scrollHeight;
  }).catch(function(e) {
    consoleEl.innerHTML += '<span class="err">[网络错误] ' + e.message + '</span>\\n\\n';
  });
}

let savedCmds = [];

function addHistory(cmd) {
  history.unshift(cmd);
  if (history.length > 100) history.pop();
  fetch('/api/history', {
    method: 'POST', headers: {'Content-Type':'application/json'},
    body: JSON.stringify({command: cmd})
  }).catch(function(){});
  renderSaved(); renderHist();
}

async function loadHistory() {
  try {
    var resp = await fetch('/api/history');
    var data = await resp.json();
    history = data.map(function(d){ return d.command; });
  } catch(e) { console.error(e); }
}

async function saveCurrentCmd() {
  var cmd = document.getElementById('cmdInput').value.trim();
  if (!cmd) return;
  await fetch('/api/save-command', {
    method: 'POST', headers: {'Content-Type':'application/json'},
    body: JSON.stringify({command: cmd})
  });
  await loadSavedCmds();
  renderSaved();
}

async function deleteSavedCmd(cmd, ev) {
  if (ev) ev.stopPropagation();
  await fetch('/api/save-command', {
    method: 'DELETE', headers: {'Content-Type':'application/json'},
    body: JSON.stringify({command: cmd})
  });
  await loadSavedCmds();
  renderSaved();
}

async function loadSavedCmds() {
  try {
    var resp = await fetch('/api/saved-commands');
    savedCmds = await resp.json();
  } catch(e) { console.error(e); }
}

function fuzzyMatch(query, text) {
  if (!query) return true;
  var q = query.toLowerCase();
  var t = text.toLowerCase();
  if (t.indexOf(q) >= 0) return true;
  var qi = 0;
  for (var ti = 0; ti < t.length && qi < q.length; ti++) {
    if (t[ti] === q[qi]) qi++;
  }
  return qi === q.length;
}

function renderSaved() {
  var body = document.getElementById('savedBody');
  var q = document.getElementById('savedSearch').value.trim();
  var filtered = savedCmds.filter(function(s) { return fuzzyMatch(q, s.command); });
  document.getElementById('savedCount').textContent = savedCmds.length;
  var html = '';
  if (filtered.length > 0) {
    filtered.forEach(function(s) {
      html += '<div class="s2-item" onclick="fillCmd(\\''+s.command.replace(/'/g,"\\\\'")+'\\')">';
      html += '<span class="s2-iico" style="color:#ffd740;">&#9733;</span>';
      html += '<span class="s2-itxt">' + esc(s.command) + '</span>';
      html += '<button class="s2-idel" onclick="deleteSavedCmd(\\''+s.command.replace(/'/g,"\\\\'")+'\\'  ,event)" title="取消收藏">&times;</button>';
      html += '</div>';
    });
  } else {
    html += '<div class="s2-empty">' + (q ? '无匹配' : '点击 ★ 收藏命令') + '</div>';
  }
  body.innerHTML = html;
}

function renderHist() {
  var body = document.getElementById('histBody');
  var q = document.getElementById('histSearch').value.trim();
  var seen = {};
  var filtered = [];
  history.forEach(function(h) {
    if (!seen[h] && fuzzyMatch(q, h)) { filtered.push(h); seen[h]=true; }
  });
  document.getElementById('histCount').textContent = history.length;
  var html = '';
  if (filtered.length > 0) {
    filtered.forEach(function(h) {
      html += '<div class="s2-item" onclick="fillCmd(\\''+h.replace(/'/g,"\\\\'")+'\\')">';
      html += '<span class="s2-iico" style="color:#82b1ff;">&#128339;</span>';
      html += '<span class="s2-itxt">' + esc(h) + '</span>';
      html += '</div>';
    });
  } else {
    html += '<div class="s2-empty">' + (q ? '无匹配' : '执行命令后自动记录') + '</div>';
  }
  body.innerHTML = html;
}

function fillCmd(cmd) {
  document.getElementById('cmdInput').value = cmd;
  document.getElementById('cmdInput').focus();
  document.querySelectorAll('.s2-box.open').forEach(function(b) { b.classList.remove('open'); });
}

function toggleS2(id) {
  var el = document.getElementById(id);
  var wasOpen = el.classList.contains('open');
  document.querySelectorAll('.s2-box.open').forEach(function(b) { b.classList.remove('open'); });
  if (!wasOpen) {
    el.classList.add('open');
    var si = el.querySelector('.s2-search');
    if (si) { si.value = ''; si.focus(); }
    if (id === 's2Saved') renderSaved();
    else renderHist();
  }
}

document.addEventListener('mousedown', function(e) {
  document.querySelectorAll('.s2-box.open').forEach(function(box) {
    if (!box.contains(e.target)) box.classList.remove('open');
  });
});

const cmdInput = document.getElementById('cmdInput');
cmdInput.addEventListener('keydown', function(e) {
  if (e.key === 'Enter') { executeFromInput(); }
  else if (e.key === 'Tab') {
    e.preventDefault();
    var val = cmdInput.value.trim();
    var allNames = [];
    Object.keys(commands).forEach(function(n) { allNames.push(n.replace(/_/g,'-')); });
    var matches = allNames.filter(function(n){return n.startsWith(val);});
    if (matches.length === 1) cmdInput.value = matches[0] + ' ';
  }
});

Promise.all([loadHistory(), loadSavedCmds()]).then(function() { renderSaved(); renderHist(); });
loadCommands();
loadInitParams();

(function() {
  var resizer = document.getElementById('resizer');
  var left = document.querySelector('.left-panel');
  var main = document.querySelector('.main');
  var dragging = false;
  resizer.addEventListener('mousedown', function(e) {
    dragging = true;
    resizer.classList.add('active');
    document.body.style.cursor = 'col-resize';
    document.body.style.userSelect = 'none';
    e.preventDefault();
  });
  document.addEventListener('mousemove', function(e) {
    if (!dragging) return;
    var rect = main.getBoundingClientRect();
    var offset = e.clientX - rect.left;
    var pct = (offset / rect.width) * 100;
    if (pct < 15) pct = 15;
    if (pct > 80) pct = 80;
    left.style.width = pct + '%';
  });
  document.addEventListener('mouseup', function() {
    if (!dragging) return;
    dragging = false;
    resizer.classList.remove('active');
    document.body.style.cursor = '';
    document.body.style.userSelect = '';
  });
})();
</script>
</body>
</html>'''
