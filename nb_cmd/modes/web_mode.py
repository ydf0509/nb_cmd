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

    commands = discover_commands(instance, base_cls)
    description = inspect.getdoc(instance) or instance.__class__.__name__

    static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ui', 'static')
    has_built_frontend = os.path.isfile(os.path.join(static_dir, 'index.html'))

    from ..modes.api_mode import _register_routes as _register_pydantic_routes
    _register_pydantic_routes(app, instance, commands, base_cls=base_cls)

    @app.get('/api/commands', summary='获取所有命令及参数定义')
    async def get_commands():
        result = {}
        for name, info in commands.items():
            if info.get('is_group'):
                group_cls = info['cls']
                group_instance = group_cls()
                group_cmds = discover_commands(group_instance, base_cls,
                                               include_builtins=False)
                sub_result = {}
                for sub_name, sub_info in group_cmds.items():
                    if sub_info.get('is_group'):
                        continue
                    sub_result[sub_name] = _build_cmd_info(sub_info)
                result[name] = {
                    'type': 'group',
                    'description': info.get('doc', ''),
                    'sub_commands': sub_result,
                }
                continue
            result[name] = _build_cmd_info(info)
        return result

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

    def _make_instance(raw_init_params=None):
        """每次请求创建一个新的用户类实例，彼此隔离"""
        if not init_params_info:
            return _user_cls()
        from ..core.type_utils import convert_value
        kwargs = {}
        for p in init_params_info:
            pname = p['name']
            if raw_init_params and pname in raw_init_params:
                kwargs[pname] = convert_value(raw_init_params[pname], p['_real_type'])
            elif p.get('required'):
                kwargs[pname] = getattr(instance, pname)
        return _user_cls(**kwargs) if kwargs else _user_cls()

    def _resolve_command(route_path, raw_init_params=None):
        """根据路由路径解析出 (method, target_instance, cmd_info)，每次新建实例"""
        parts = route_path.replace('-', '_').split('/')
        if len(parts) == 1:
            cmd_name = parts[0]
            if cmd_name in commands and not commands[cmd_name].get('is_group'):
                info = commands[cmd_name]
                target_inst = _make_instance(raw_init_params)
                method = getattr(target_inst, cmd_name)
                return method, target_inst, info
        elif len(parts) == 2:
            group_name, sub_name = parts
            if group_name in commands and commands[group_name].get('is_group'):
                group_cls = commands[group_name]['cls']
                group_inst = group_cls()
                group_cmds = discover_commands(group_inst, base_cls,
                                               include_builtins=False)
                if sub_name in group_cmds and not group_cmds[sub_name].get('is_group'):
                    sub_info = group_cmds[sub_name]
                    return sub_info['method'], group_inst, sub_info
        return None, None, None

    class _QueueWriter(object):
        """将 write() 调用转发到 queue 的伪文件对象，伪装为 TTY 以触发颜色输出"""
        def __init__(self, output_queue, stream_type):
            self._q = output_queue
            self._type = stream_type
            self.encoding = 'utf-8'
        def write(self, data):
            if data:
                self._q.put((self._type, data))
        def flush(self):
            pass
        def isatty(self):
            return True

    @app.websocket('/ws/execute')
    async def ws_execute(websocket: WebSocket):
        await websocket.accept()
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
            result_holder = {'result': None, 'error': None}

            def _run():
                old_out, old_err = sys.stdout, sys.stderr
                ws_out = _QueueWriter(output_q, 'stdout')
                ws_err = _QueueWriter(output_q, 'stderr')
                sys.stdout = ws_out
                sys.stderr = ws_err
                saved_streams = []
                if hasattr(target_inst, '_logger') and target_inst._logger:
                    for h in target_inst._logger.handlers:
                        if hasattr(h, 'stream'):
                            saved_streams.append((h, h.stream))
                            if h.stream is old_err or h.stream is old_out:
                                h.stream = ws_err
                try:
                    target_inst.before_run()
                    r = method(**kwargs)
                    result_holder['result'] = handle_api_result(r)
                except Exception as exc:
                    result_holder['error'] = str(exc)
                    target_inst.on_error(route_path, exc)
                finally:
                    for h, orig in saved_streams:
                        h.stream = orig
                    sys.stdout, sys.stderr = old_out, old_err
                    target_inst.after_run()
                    output_q.put(None)

            t = threading.Thread(target=_run, daemon=True)
            start_ts = time.time()
            t.start()

            while True:
                try:
                    item = output_q.get(timeout=0.05)
                    if item is None:
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
                        break
                    await asyncio.sleep(0.02)

            t.join(timeout=1)
            duration = int((time.time() - start_ts) * 1000)

            if result_holder['error']:
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
            pass
        except Exception:
            pass

    if has_built_frontend:
        from fastapi.staticfiles import StaticFiles
        app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
    else:
        html_content = _generate_builtin_html(title, version, description, theme)

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


def _generate_builtin_html(title, version, description, theme):
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
                   font-size: 13px; padding: 12px 16px; overflow-y: auto; white-space: pre-wrap; word-break: break-all; }
.console-output .ts { color: #636e72; }
.console-output .cmd-echo { color: var(--primary); }
.console-output .err { color: var(--error); }
.console-output .ok { color: var(--success); }
.history-area { max-height: 200px; overflow-y: auto; border-top: 1px solid var(--border);
                 background: var(--card-bg); }
.history-area .history-label { padding: 6px 16px; font-size: 13px; color: var(--info);
                                border-bottom: 1px solid var(--border); }
.history-item { padding: 6px 16px; cursor: pointer; font-family: monospace; font-size: 13px;
                 border-bottom: 1px solid var(--border); display: flex; align-items: center;
                 justify-content: space-between; }
.history-item:hover { background: var(--hover-bg); }
.history-item .hist-text { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.history-item .copy-btn { flex-shrink: 0; margin-left: 8px; padding: 2px 8px; font-size: 11px;
                          border: 1px solid var(--border); border-radius: 3px; cursor: pointer;
                          background: var(--card-bg); color: var(--text); opacity: 0;
                          transition: opacity 0.15s; }
.history-item:hover .copy-btn { opacity: 1; }
.history-item .copy-btn:hover { background: var(--primary); color: #fff; border-color: var(--primary); }
.status-bar { padding: 6px 16px; font-size: 12px; border-top: 1px solid var(--border);
               background: var(--card-bg); display: flex; justify-content: space-between; color: #888; }
.arrow { transition: transform 0.2s; } .arrow.open { transform: rotate(90deg); }
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
      <div class="console-label">&#128203; 实时控制台输出</div>
      <div class="console-output" id="consoleOutput"></div>
    </div>
    <div class="history-area">
      <div class="history-label">&#128220; 命令历史</div>
      <div id="historyList"></div>
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
let history = JSON.parse(localStorage.getItem('nb_cmd_history') || '[]');
let historyIdx = -1;
let execCount = 0;

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
  if (commands[pyName]) return commands[pyName];
  var slash = pyName.indexOf('/');
  if (slash > 0) {
    var grp = pyName.substring(0, slash);
    var sub = pyName.substring(slash + 1);
    if (commands[grp] && commands[grp].type === 'group' && commands[grp].sub_commands) {
      return commands[grp].sub_commands[sub] || null;
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

function renderForms() {
  const area = document.getElementById('formArea');
  let html = '';
  for (const [name, info] of Object.entries(commands)) {
    if (info.type === 'group') {
      var grpCliName = name.replace(/_/g, '-');
      html += '<div class="form-section"><div class="form-section-header" onclick="toggleSection(this)">';
      html += '<span><span class="arrow">&#9654;</span> <span class="cmd-name" style="color:var(--primary);">' + grpCliName + '</span>';
      html += '<span class="cmd-desc">[组] ' + (info.description||'') + '</span></span></div>';
      html += '<div class="form-section-body">';
      if (info.sub_commands) {
        for (const [subName, subInfo] of Object.entries(info.sub_commands)) {
          var subCliLabel = grpCliName + ' ' + subName.replace(/_/g, '-');
          var formId = name + '/' + subName;
          html += renderCmdSection(formId, subCliLabel, subInfo.description, subInfo.parameters);
        }
      }
      html += '</div></div>';
      continue;
    }
    var cliName = name.replace(/_/g, '-');
    html += renderCmdSection(name, cliName, info.description, info.parameters);
  }
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
  } else {
    cmdInfo = commands[firstPy] || null;
    routePath = parts[0];
    argStart = 1;
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
        }
      }
    }
  }
  var overrideInit = Object.keys(inputInitP).length > 0 ? inputInitP : null;
  await doExecute(routePath, kwargs, overrideInit);
  input.value = '';
}

function doExecute(routePath, kwargs, initParamsOverride) {
  var consoleEl = document.getElementById('consoleOutput');
  var ts = new Date().toLocaleTimeString();
  var initP = initParamsOverride || getInitParams();
  var cmdStr = routePath.replace(/\\//g, ' ');
  Object.entries(kwargs).forEach(function(e) {
    if (typeof e[1] === 'boolean') { if(e[1]) cmdStr += ' --' + e[0].replace(/_/g,'-'); }
    else cmdStr += ' --' + e[0].replace(/_/g,'-') + ' ' + e[1];
  });

  consoleEl.innerHTML += '<span class="ts">[' + ts + ']</span> <span class="cmd-echo">$ ' + cmdStr + '</span>\\n';
  document.getElementById('statusText').innerText = '状态: 执行中... ' + cmdStr;

  var wsProto = location.protocol === 'https:' ? 'wss:' : 'ws:';
  var wsUrl = wsProto + '//' + location.host + '/ws/execute';

  try {
    var ws = new WebSocket(wsUrl);
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
        document.getElementById('statusText').innerText = '状态: 就绪  |  最后执行: ' + cmdStr + ' ' + ts;
      } else if (msg.type === 'error') {
        consoleEl.innerHTML += '<span class="err">[错误] ' + esc(msg.error||'未知错误') + '</span>\\n\\n';
        document.getElementById('statusText').innerText = '状态: 就绪  |  出错: ' + cmdStr;
      }
      consoleEl.scrollTop = consoleEl.scrollHeight;
    };
    ws.onerror = function() {
      _doExecuteFallback(routePath, kwargs, cmdStr, ts);
    };
    ws.onclose = function() {};
  } catch(e) {
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

function addHistory(cmd) {
  history.unshift(cmd);
  if (history.length > 50) history.pop();
  localStorage.setItem('nb_cmd_history', JSON.stringify(history));
  renderHistory();
}

function renderHistory() {
  const el = document.getElementById('historyList');
  el.innerHTML = '';
  history.forEach(function(cmd, i) {
    const div = document.createElement('div');
    div.className = 'history-item';
    var span = document.createElement('span');
    span.className = 'hist-text';
    span.textContent = (i+1) + '. ' + cmd;
    span.onclick = function() { document.getElementById('cmdInput').value = cmd; };
    div.appendChild(span);
    var btn = document.createElement('button');
    btn.className = 'copy-btn';
    btn.textContent = '复制';
    btn.onclick = function(e) {
      e.stopPropagation();
      navigator.clipboard.writeText(cmd).then(function() {
        btn.textContent = '已复制';
        setTimeout(function() { btn.textContent = '复制'; }, 1500);
      });
    };
    div.appendChild(btn);
    el.appendChild(div);
  });
}

const cmdInput = document.getElementById('cmdInput');
cmdInput.addEventListener('keydown', function(e) {
  if (e.key === 'Enter') { executeFromInput(); }
  else if (e.key === 'ArrowUp') {
    e.preventDefault();
    if (historyIdx < history.length - 1) { historyIdx++; cmdInput.value = history[historyIdx]; }
  } else if (e.key === 'ArrowDown') {
    e.preventDefault();
    if (historyIdx > 0) { historyIdx--; cmdInput.value = history[historyIdx]; }
    else { historyIdx = -1; cmdInput.value = ''; }
  } else if (e.key === 'Tab') {
    e.preventDefault();
    var val = cmdInput.value.trim();
    var allNames = [];
    Object.keys(commands).forEach(function(n) { allNames.push(n.replace(/_/g,'-')); });
    var matches = allNames.filter(function(n){return n.startsWith(val);});
    if (matches.length === 1) cmdInput.value = matches[0] + ' ';
  }
});

renderHistory();
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
