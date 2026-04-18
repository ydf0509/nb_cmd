---
noteId: "1a53aa103b2711f18f3255ad17859a5a"
tags: []

---

# nb_cmd 重大设计修改记录

## 2026-04-17: 线程安全 stdout 分发器（并发串流修复）

**问题**: web_mode 和 api_mode 中，每个请求直接替换 `sys.stdout`，并发时互相覆盖导致输出串流到错误的前端。

**方案**: 新建 `nb_cmd/core/_io_dispatch.py`，统一管理线程安全的 stdout/stderr 分发。

**核心设计**:
- `threading.local()` 存储每个线程的输出目标
- `_DispatchWriter` 替代 `sys.stdout`，按优先级分发：
  1. `_tls.output_queue` → WebSocket 推送（Queue 模式）
  2. `_tls.captured_stdout` → API 捕获（StringIO 模式）
  3. 原始流 → 服务器控制台
- `install()` 幂等安装，只设置一次 `sys.stdout`
- web_mode 的 `_run()` 中通过 `_tls.output_queue = q` 注册
- api_mode 的 `_exec_in_thread()` 中通过 `_tls.captured_stdout = StringIO()` 注册

**影响文件**:
- `nb_cmd/core/_io_dispatch.py` (新增)
- `nb_cmd/modes/web_mode.py` (移除 _QueueWriter, _ThreadLocalWriter)
- `nb_cmd/modes/api_mode.py` (移除直接 sys.stdout 替换)

## 2026-04-17: API 模式 async 方法并发安全

**问题**: `_exec_async` 跑在主 asyncio 线程中，`threading.local()` 无法隔离多个 async 请求。

**方案**: 移除 `_exec_async`，统一使用 `_exec_in_thread`（同步函数，内部用 `asyncio.run()` 处理协程），所有请求通过 `asyncio.to_thread()` 派到线程池，`threading.local()` 自然隔离。

## 2026-04-17: 子命令组不再暴露 exec

**问题**: `parser.py` 中 `_build_group_subparser` 调用 `discover_commands` 时未传 `include_builtins=False`，导致子命令组也显示 `exec` 命令。

**修复**: 添加 `include_builtins=False` 参数。

## 2026-04-17 之前: Annotated 迁移 + Param 对象

**方案**: 移除自定义 `Arg` 类，迁移到 `typing.Annotated`，新增 `Param` 关键字参数对象。

**详见**: `nb_cmd/core/arg.py` 中的 `unwrap_arg` 函数和 `Param` 类。

