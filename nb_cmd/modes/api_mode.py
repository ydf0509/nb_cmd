# -*- coding: utf-8 -*-
"""
REST API 模式 —— 自动将 NbCmd 类的方法生成 FastAPI 路由。
需要安装: pip install fastapi uvicorn
"""
import asyncio
import functools
import inspect
import io
import time

from ..core.discovery import discover_commands
from ..core.result_handler import handle_api_result


async def _run_in_thread(func, *args):
    """asyncio.to_thread 的 Python 3.7+ 兼容版"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, functools.partial(func, *args))


def start_api_server(instance, base_cls, host=None, port=None):
    """
    启动 REST API 服务。

    Parameters
    ----------
    instance : NbCmd 实例
    base_cls : NbCmd 类
    host : str
    port : int
    """
    try:
        from fastapi import FastAPI
        from fastapi.middleware.cors import CORSMiddleware
        import uvicorn
    except ImportError:
        print("REST API模式需要安装 fastapi 和 uvicorn:")
        print("  pip install fastapi uvicorn")
        return

    meta = getattr(instance.__class__, 'Meta', type('Meta', (), {}))
    title = getattr(meta, 'name', None) or instance.__class__.__name__
    description = inspect.getdoc(instance) or ''
    version = getattr(meta, 'version', None) or '0.0.1'

    if host is None:
        host = getattr(meta, 'serve_host', '0.0.0.0')
    if port is None:
        port = getattr(meta, 'serve_port', 8080)

    app = FastAPI(title=title, description=description, version=version)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    _enable_exec = getattr(meta, 'enable_exec', True)
    commands = discover_commands(instance, base_cls, enable_exec=_enable_exec)
    _register_routes(app, instance, commands, base_cls=base_cls)

    from fastapi.responses import RedirectResponse

    @app.get('/', include_in_schema=False)
    async def root():
        """根路径自动跳转到 Swagger 文档"""
        return RedirectResponse(url='/docs')

    @app.get('/help', summary='所有命令帮助')
    async def help_all():
        result = {}
        for name, info in commands.items():
            if info.get('is_group'):
                result[name] = {'type': 'group', 'description': info.get('doc', '')}
            else:
                params = {}
                for pname, param in info['signature'].parameters.items():
                    if pname == 'self':
                        continue
                    ptype = info['type_hints'].get(pname, str)
                    has_default = param.default is not inspect.Parameter.empty
                    params[pname] = {
                        'type': str(ptype),
                        'required': not has_default,
                        'default': _safe_default(param.default) if has_default else None,
                    }
                result[name] = {
                    'type': 'command',
                    'description': info.get('doc', ''),
                    'parameters': params,
                }
        return result

    print('API服务启动在 http://{}:{}'.format(host, port))
    print('Swagger文档: http://{}:{}/docs'.format(host, port))
    uvicorn.run(app, host=host, port=port)


def _safe_default(value):
    """将默认值转为 JSON 可序列化的形式"""
    import enum
    from pathlib import Path
    if value is inspect.Parameter.empty:
        return None
    if isinstance(value, enum.Enum):
        return value.value
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, (str, int, float, bool, type(None))):
        return value
    if isinstance(value, (list, tuple, dict)):
        return value
    return str(value)


def _register_routes(app, instance, commands, base_cls=None, prefix=''):
    """为每个命令注册 POST 路由，支持递归注册子命令组"""
    for cmd_name, cmd_info in commands.items():
        if cmd_info.get('is_group'):
            if base_cls is not None:
                group_cls = cmd_info['cls']
                group_kwargs = cmd_info.get('init_kwargs', {})
                try:
                    group_instance = group_cls(**group_kwargs) if group_kwargs else group_cls()
                except TypeError:
                    group_instance = group_cls.__new__(group_cls)
                group_commands = discover_commands(group_instance, base_cls,
                                                   include_builtins=False)
                group_prefix = '{}/{}'.format(prefix, cmd_name) if prefix else cmd_name
                _register_routes(app, group_instance, group_commands,
                                 base_cls=base_cls, prefix=group_prefix)
            continue

        sig = cmd_info['signature']
        hints = cmd_info.get('type_hints', {})
        cli_name = cmd_name.replace('_', '-')
        if prefix:
            route_path = '{}/{}'.format(prefix.replace('_', '-'), cli_name)
        else:
            route_path = cli_name
        doc = cmd_info.get('doc', '')

        try:
            from pydantic import create_model as _create_model

            fields = {}
            for param_name, param in sig.parameters.items():
                if param_name == 'self':
                    continue
                param_type = hints.get(param_name, str)

                import enum
                from pathlib import Path
                from ..core.type_utils import unwrap_optional, is_enum_type, is_list_type, is_tuple_type

                real_type = unwrap_optional(param_type)
                if is_enum_type(real_type):
                    real_type = str
                if real_type is Path:
                    real_type = str
                if is_list_type(real_type):
                    real_type = list
                if is_tuple_type(real_type):
                    real_type = list

                has_default = param.default is not inspect.Parameter.empty
                if has_default:
                    default_val = param.default
                    if isinstance(default_val, enum.Enum):
                        default_val = default_val.value
                    if isinstance(default_val, Path):
                        default_val = str(default_val)
                    fields[param_name] = (real_type, default_val)
                else:
                    fields[param_name] = (real_type, ...)

            if _get_init_kwargs(instance):
                from typing import Optional as _Optional
                fields['init_params'] = (_Optional[dict], None)

            model_name = '{}_{}_request'.format(prefix, cmd_name) if prefix else '{}_request'.format(cmd_name)
            RequestModel = _create_model(model_name, **fields)
        except Exception:
            RequestModel = None

        _make_route(app, route_path, doc, cmd_name, instance, RequestModel, hints)


def _get_init_kwargs(instance):
    """从实例上提取 __init__ 参数的当前值，用于重新实例化"""
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


def _get_init_types(instance):
    """获取 __init__ 参数名到真实类型的映射，用于 REST API 中 _init_params 的类型转换"""
    from ..core.arg import unwrap_arg
    cls = instance.__class__
    init_method = cls.__init__
    if init_method is object.__init__:
        return {}
    sig = inspect.signature(init_method)
    types = {}
    for pname, param in sig.parameters.items():
        if pname == 'self':
            continue
        raw_hint = param.annotation
        if raw_hint is inspect.Parameter.empty:
            val = getattr(instance, pname, None)
            types[pname] = type(val) if val is not None else str
        else:
            real_type, _ = unwrap_arg(raw_hint)
            types[pname] = real_type
    return types


def _make_route(app, path, summary, cmd_name, instance, request_model, type_hints):
    """创建单个 API 路由，每次请求新建实例执行命令，支持 init_params 覆盖全局参数"""
    _cmd_name = cmd_name
    _cls = instance.__class__
    _init_kwargs = _get_init_kwargs(instance)
    _init_types = _get_init_types(instance)
    _hints = type_hints
    _path = path

    def _fresh(raw_init_params=None):
        if not raw_init_params or not _init_types:
            return _cls(**_init_kwargs) if _init_kwargs else _cls()
        from ..core.type_utils import convert_value
        merged = dict(_init_kwargs)
        for pname, val in raw_init_params.items():
            if pname in _init_types:
                merged[pname] = convert_value(val, _init_types[pname])
        return _cls(**merged) if merged else _cls()

    def _convert_kwargs(kwargs):
        from ..core.type_utils import convert_value
        converted = {}
        for k, v in kwargs.items():
            if k in _hints:
                converted[k] = convert_value(v, _hints[k])
            else:
                converted[k] = v
        return converted

    from ..core._io_dispatch import _tls as _api_tls, install as _install_io
    _install_io()

    def _exec_in_thread(fresh_inst, kwargs):
        import asyncio as _aio
        captured_out = io.StringIO()
        captured_err = io.StringIO()
        _api_tls.captured_stdout = captured_out
        _api_tls.captured_stderr = captured_err
        try:
            method = getattr(fresh_inst, _cmd_name)
            result = method(**_convert_kwargs(kwargs))
            if inspect.iscoroutine(result):
                result = _aio.run(result)
        finally:
            _api_tls.captured_stdout = None
            _api_tls.captured_stderr = None
        return result, captured_out.getvalue(), captured_err.getvalue()

    if request_model is not None:
        @app.post('/{}'.format(path), summary=summary)
        async def endpoint(request: request_model):
            start = time.time()
            kwargs = request.dict() if hasattr(request, 'dict') else request.model_dump()
            raw_init = kwargs.pop('init_params', None)
            fresh_inst = _fresh(raw_init)
            fresh_inst.before_run()
            try:
                result, stdout_output, stderr_output = await _run_in_thread(
                    _exec_in_thread, fresh_inst, kwargs)
                api_result = handle_api_result(result)
                duration_ms = int((time.time() - start) * 1000)
                return {
                    "status": "success",
                    "result": api_result,
                    "stdout": stdout_output if stdout_output else None,
                    "stderr": stderr_output if stderr_output else None,
                    "duration_ms": duration_ms,
                }
            except Exception as e:
                fresh_inst.on_error(_path, e)
                return {
                    "status": "error",
                    "error": str(e),
                    "duration_ms": int((time.time() - start) * 1000),
                }
            finally:
                fresh_inst.after_run()
    else:
        @app.post('/{}'.format(path), summary=summary)
        async def endpoint(request: dict = {}):
            start = time.time()
            raw_init = request.pop('init_params', None)
            fresh_inst = _fresh(raw_init)
            fresh_inst.before_run()
            try:
                result, stdout_output, stderr_output = await _run_in_thread(
                    _exec_in_thread, fresh_inst, request)
                api_result = handle_api_result(result)
                duration_ms = int((time.time() - start) * 1000)
                return {
                    "status": "success",
                    "result": api_result,
                    "stdout": stdout_output if stdout_output else None,
                    "stderr": stderr_output if stderr_output else None,
                    "duration_ms": duration_ms,
                }
            except Exception as e:
                fresh_inst.on_error(_path, e)
                return {
                    "status": "error",
                    "error": str(e),
                    "duration_ms": int((time.time() - start) * 1000),
                }
            finally:
                fresh_inst.after_run()
