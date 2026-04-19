---
noteId: "1a53aa103b2711f18f3255ad17859a5a"
tags: []

---

# nb_cmd 重大设计修改记录

## 2026-04-18: 帮助系统三级化 (-h / -fh / -eh + help_mode 配置)

**需求**: 很多用户只知道 `-h`，不知道 `-fh` 可以看完整帮助。希望 `-h` 默认显示完整帮助。

**方案**: 三个帮助级别 + `Meta.help_mode` 配置

**帮助选项**:
- `-h` / `--help`: 由 `Meta.help_mode` 决定行为
- `-fh` / `--full-help`: 始终显示完整帮助（所有参数详情）
- `-eh` / `--easy-help`: 始终显示简易帮助（argparse 原生格式）

**`Meta.help_mode` 配置**:
- `'full'`（默认）: `-h` 显示完整帮助
- `'easy'`: `-h` 显示简易帮助

**实现**: 在 `base.py._handle_help()` 中，argparse 解析之前拦截帮助参数，避免和 argparse 的 `-h` action 冲突。

**影响文件**:
- `nb_cmd/core/base.py` (新增 `_handle_help()`)
- `nb_cmd/core/parser.py` (新增 `print_easy_help()`，更新帮助文本)
- `nb_cmd/core/meta.py` (新增 `help_mode` 配置项)

## 2026-04-18: 系统参数 `--version` 改名为 `--cmd-version`

**问题**: 系统参数 `--version`（显示应用版本号）与用户方法参数名 `version`（如 `deploy --version v2`）冲突。argparse 在顶层解析器就拦截了 `--version`，导致子命令方法收不到。

**修复**: 将系统参数从 `--version` 改为 `--cmd-version`，释放 `--version` 给用户业务参数。

**修改前**: `python app.py --version` 显示版本号，但 `deploy --version v2` 会被顶层拦截报错
**修改后**: `python app.py --cmd-version` 显示版本号，`deploy --version v2`（需 Annotated alias）正常传参

**影响文件**:
- `nb_cmd/core/parser.py` (`--version` → `--cmd-version` 注册 + full help 文本)
- `nb_cmd/core/gen_cmd.py` (Markdown System Params 表格 + Quick Start 示例)
- `nb_cmd/core/meta.py` (注释更新)
- `README.md` (所有系统参数 `--version` 引用更新)
- `examples/nbctx_demo/nbctx_demo.py` (`deploy.version` 加 `-v` 别名以支持 `--version` flag 调用)
- `examples/nbctx_demo/nbctx_demo_gen_doc.md` (重新生成)

---

## 2026-04-18: CLI 参数双模式（位置参数 + `--` 风格并存）

**需求**: CLI 既要保持 `deploy 2.0.0` 的简短用法（向后兼容），又希望自动生成的文档用 `deploy --version $<version>` 风格（自文档化、清晰）。

**实现**:
- **无 Annotated alias 的必填参数** → 注册为 argparse 位置参数（如 `deploy VERSION`），位置参数和 `--` 风格都能用
- **有 Annotated alias 的必填参数** → 注册为 `--flag required=True`（如 `deploy --host HOST -H HOST`）
- **`gen_cmd` 文档生成** → 统一用 `--flag` 风格展示（如 `--version $<version>`），即使 CLI 支持位置参数

**CLI 用法**:
```
python app.py deploy 2.0.0              # ✓ 位置参数（简短）
python app.py deploy -H 10.0.0.1        # ✓ Annotated alias
```

**生成文档显示**: `deploy --version $<version>`（推荐风格，自文档化）

**影响文件**:
- `nb_cmd/core/parser.py` (`_add_method_arguments` 无 alias 时保持 positional，有 alias 时用 `--flag required=True`)
- `nb_cmd/core/gen_cmd.py` (`_format_method_args` 中无默认值参数生成 `--flag $<name>`)
- `tests/ai_codes/testnbcmds/test_all_features.py` (测试用例使用位置参数风格)

## 2026-04-18: CmdGen 命令行示例生成器

**需求**: 用户定义了多层级子命令后，手写 CLI 示例很繁琐。需要自动从类结构生成完整的命令行示例。

**方案**: `CmdGen` 类，公共参数在 `__init__` 中传入

**用法**:
```python
from nb_cmd import CmdGen

g = CmdGen(MyApp, script='app.py')
print(g.cmd(DbTool.migrate))   # 单个命令示例
print(g.doc())                   # 完整文档（含 -fh 帮助 + 所有命令行示例）
```

**`CmdGen.__init__(entry_cls, script=None, python=None, fmt='text')`**
**`CmdGen.cmd(method)`**: 生成单个方法的 CLI 命令行
**`CmdGen.doc()`**: 生成完整文档（前半部分为 full help，后半部分为命令行示例）

**参数值标记**:
- 有默认值的非 bool 参数 → `${默认值}`（如 `--region ${beijing}`）
- 无默认值的必填参数 → `--flag $<参数名>`（如 `--version $<version>`）
- bool 默认 False → `--flag`；默认 True → 不显示
- `python` 参数默认用 `sys.executable`（当前解释器完整路径）

**影响文件**:
- `nb_cmd/core/gen_cmd.py` (新增 CmdGen 类)
- `nb_cmd/__init__.py` (导出 CmdGen)
- `examples/nbctx_demo/nbctx_demo.py` (新增场景 5、6 使用示例)

## 2026-04-18: nbctx 从 property 改为普通属性（IDE 补全修复）

**问题**: `nbctx` 用 `@property` 实现时，子类的 `nbctx: AppCtx` 类型注解被父类的 property descriptor 覆盖，IDE 无法推断返回类型，`self.nbctx.region` 等字段无法代码补全和跳转。

**原因**: Python 中数据描述符（property）优先级高于子类的类型注解，IDE 只看 property 的返回类型（无注解 → 推断为 None），忽略子类的 `nbctx: AppCtx`。

**修复**: 去掉 `@property` 和 `@nbctx.setter`，将 `nbctx` 改为普通类属性 `nbctx = None`。子类的 `nbctx: AppCtx` 类型注解可以正常覆盖普通属性，IDE 补全生效。

**代价**: 去掉了 property 的"lazy 创建"兜底——直接实例化子命令组时 `self.nbctx` 为 `None` 而非自动创建默认值，用户本地调用需手动 `tool.nbctx = AppCtx()`。框架流程（CLI/Web/API）不受影响，自动注入。

**影响文件**:
- `nb_cmd/core/base.py` (去掉 property/setter，改为 `nbctx = None`，删除 `self._nbctx`)
- `nb_cmd/modes/cli_mode.py` (`_ensure_nbctx` 中 `_nbctx` → `nbctx`)
- `examples/nbctx_demo/nbctx_demo.py` (MyApp 加 `nbctx: AppCtx` 注解，场景 3 改为手动设置)
- `tests/ai_codes/testnbcmds/test_nbctx.py` (修改默认值兜底测试)

## 2026-04-18: nbctx 跨层级上下文传递

**需求**: 多层级子命令（sub_commands）无法获取顶层 `__init__` 的全局参数。子命令组完全独立，不知道自己被谁挂载，没有 `_parent` 引用。

**方案**: `self.nbctx` + `make_nbctx()` 模板方法

**核心设计**:
- NbCmd 基类新增 `nbctx = None` 普通类属性和 `make_nbctx()` 模板方法
- 用户在顶层类中覆写 `make_nbctx()` 返回一个 dataclass 实例
- 框架在命令执行前自动调用 `make_nbctx()` 设置顶层的 `self.nbctx`
- 子命令组实例化后，框架自动 `child.nbctx = parent.nbctx`（引用传递）
- 递归传递到任意层级深度
- 子命令组通过类型注解 `nbctx: AppCtx` 获取 IDE 补全

**用户代码示例**:
```python
@dataclass
class AppCtx:
    region: str = 'beijing'
    env: str = 'prod'

class MyApp(NbCmd):
    nbctx: AppCtx  # IDE 补全
    def __init__(self, region='beijing', env='prod'):
        self.region = region
        self.env = env

    def make_nbctx(self):
        return AppCtx(region=self.region, env=self.env)

    sub_commands = {'db': DbTool}

class DbTool(NbCmd):
    nbctx: AppCtx  # IDE 补全

    def migrate(self):
        print(f'Migrating in {self.nbctx.region}')
```

**三种模式均支持**:
- CLI: `--region shanghai db migrate` → `self.nbctx.region == 'shanghai'`
- Web: `init_params` 面板设置 → 自动传递
- API: `"init_params": {"region": "shanghai"}` → 自动传递

**防御性设计**:
- 未定义 `make_nbctx()` 时默认返回 None，不影响任何现有代码
- 无 nbctx 注解的子命令组 `self.nbctx` 返回 None

**影响文件**:
- `nb_cmd/core/base.py` (新增 nbctx + make_nbctx)
- `nb_cmd/modes/cli_mode.py` (新增 _ensure_nbctx + _inject_nbctx)
- `nb_cmd/modes/web_mode.py` (_make_instance + _resolve_command 注入 nbctx)
- `nb_cmd/modes/api_mode.py` (_fresh + _register_routes 注入 nbctx)

**测试**: `tests/ai_codes/testnbcmds/test_nbctx.py` (11 个测试用例)

## 2026-04-18: 修复三层嵌套子命令 CLI 解析 bug

**问题**: `_build_group_subparser` 中有两个 bug：
1. `build_parser` 传递 `instance.__class__`（用户类）作为 `base_cls`，而非 `NbCmd` 基类。导致 `discover_commands` 用用户类过滤时，子命令组的 `sub_commands` 属性被误过滤掉，第三层子命令组在 CLI 中不显示。
2. 所有层级的 subparsers 都使用 `dest='_nb_sub_command'`，多层嵌套时后层覆盖前层，导致中间层的命令名丢失。

**修复**:
1. `build_parser` 新增 `base_cls` 参数，`cli_mode.py` 传入正确的 `NbCmd` 基类。
2. `_build_group_subparser` 新增 `depth` 参数，不同层级用不同 dest（`_nb_sub_command`, `_nb_sub_command_2`, ...）。
3. `_run_group_command` 新增 `depth` 参数，递归时根据 depth 取正确的 dest。

**影响文件**: `nb_cmd/core/parser.py`, `nb_cmd/modes/cli_mode.py`

## 2026-04-18: asyncio.to_thread 兼容性修复（Python 3.7/3.8）

**问题**: `api_mode.py` 使用了 `asyncio.to_thread()`，该函数在 Python 3.9 才引入。项目声明支持 Python 3.7+，在 3.7/3.8 上会 AttributeError。

**方案**: 新增 `_run_in_thread()` 兼容函数，使用 `loop.run_in_executor(None, functools.partial(func, *args))` 实现等价功能。

**影响文件**: `nb_cmd/modes/api_mode.py`

## 2026-04-18: 子命令组实例化 TypeError 保护

**问题**: `api_mode.py` 和 `web_mode.py` 中子命令组实例化缺少 `try/except TypeError` 保护。当子命令组的 `__init__` 有必填参数且通过 class（非 instance）传入时，`group_cls()` 会失败。`parser.py` 和 `cli_mode.py` 有此保护，但 api_mode 和 web_mode 遗漏了。

**修复**: 对 api_mode 和 web_mode 的 3 处子命令组实例化添加 TypeError fallback（`__new__`）。

**影响文件**: `nb_cmd/modes/api_mode.py`, `nb_cmd/modes/web_mode.py`

## 2026-04-18: discovery.py get_type_hints fallback 安全

**问题**: Python 3.7/3.8 中如果 `typing_extensions` 未安装，fallback 到 `typing.get_type_hints`，但它不接受 `include_extras` 参数，调用时会 TypeError。

**修复**: fallback 分支中包装 `get_type_hints`，自动丢弃 `include_extras` 参数。

**影响文件**: `nb_cmd/core/discovery.py`

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

