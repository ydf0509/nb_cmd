---
noteId: "1a53aa103b2711f18f3255ad17859a5a"
tags: []

---

# nb_cmd 重大设计修改记录

## 2026-05-16: nbcmd 个人命令中心（零代码命令管理器）

**需求**: 用户不需要写任何 Python 代码，直接在终端输入 `nbcmd --tui` 或 `nbcmd --web`，就能启动一个"个人命令中心"——通过 exec 收藏和管理所有常用系统命令。

**实现**:
1. **`nb_cmd/cli.py`**（新增）: 内置一个空壳 `_NbCmdApp(NbCmd)` 类，只有内置的 `exec` 命令，`Meta.db_dir = ~/.nb_cmd` 使收藏数据全局共享
2. **`pyproject.toml`**: 新增 `[project.scripts]` 注册 `nbcmd = nb_cmd.cli:main` 命令行入口
3. **`NbCmdMeta`**: 新增 `db_dir` 配置项，支持自定义 SQLite 目录路径（默认 None=当前工作目录）
4. **`tui_mode.py` / `web_mode.py`**: `_db_path` 逻辑改为读取 `Meta.db_dir`，支持 `~` 展开和自动创建目录

**用法**: `pip install nb-cmd[tui]` 后，直接运行 `nbcmd --tui` 或 `nbcmd --web`

**影响文件**: `nb_cmd/cli.py`(新增), `nb_cmd/core/meta.py`, `nb_cmd/modes/tui_mode.py`, `nb_cmd/modes/web_mode.py`, `pyproject.toml`

---

## 2026-05-16: 收藏夹别名功能（TUI + Web 同步支持）

**需求**: 收藏的命令只显示完整命令字符串，命令一长就难以辨认。希望能给收藏命令设置短别名，方便快速识别和搜索。

**实现**:
1. **数据库**: `saved_commands` 表新增 `alias TEXT DEFAULT NULL` 列，对旧数据库自动执行 `ALTER TABLE` 迁移
2. **TUI 收藏时**: 点击星号后弹出 `AliasInputScreen`（Input + 确定/跳过按钮），用户可输入别名或留空跳过
3. **TUI 收藏夹**: 有别名时显示 `[别名] 命令`；每行新增编辑按钮（✎），点击弹出 `AliasInputScreen` 编辑别名
4. **Web API**: `POST /api/save-command` 接受可选 `alias` 字段；新增 `PUT /api/save-command` 用于更新别名
5. **Web 前端**: 收藏时弹出 `prompt()` 输入别名；收藏夹列表显示 `[别名]` 标签（金色高亮）；每项新增编辑按钮（✎）；搜索同时匹配命令和别名
6. **TUI/Web 数据互通**: 两种模式共用同一个 `nb_cmd_web.db`，别名数据双向同步

**影响文件**: `nb_cmd/modes/tui_mode.py`, `nb_cmd/modes/web_mode.py`

---

## 2026-05-16: TUI _do_execute 异常保护（防止错误导致界面退出）

**问题**: TUI 模式执行命令出错时（如缺少必填参数），`_do_execute` 的 `except` 块虽然把错误信息写入了右侧控制台，但随后调用 `target_inst.on_error(path, exc)` 时如果抛异常（如之前 `self._logger` 未初始化），异常逃逸到 Textual 的 worker 系统，导致整个 TUI 界面直接退出。

**修复**:
1. **`base.py` `on_error()`**（用户手动修复）: `self._logger` → `self.logger`（使用 property 懒初始化）
2. **`tui_mode.py` `_do_execute()`**: 对 `target_inst.on_error(path, exc)` 和 `target_inst.after_run()` 分别包裹 `try/except`，捕获任何钩子异常并以红色文字显示在右侧控制台（`[on_error 钩子异常]` / `[after_run 钩子异常]`），而非让异常逃逸导致 TUI 崩溃退出

**影响文件**: `nb_cmd/core/base.py`, `nb_cmd/modes/tui_mode.py`

---

## 2026-05-15: TUI 生成命令 + 历史命令 + 收藏命令 + SQLite

**需求**: TUI 模式缺少 Web 模式的生成命令、历史记录、收藏命令功能。

**实现**:
1. **SQLite**: 复用 Web 模式的 `nb_cmd_web.db`，相同 schema（`saved_commands` + `command_history`）
2. **生成命令**: 左栏底部增加 `CLI:` 只读 Input，选择命令/修改参数时自动更新为完整 CLI 命令字符串
3. **历史命令**: 每次执行自动记录到 SQLite（最近1000条），`Ctrl+H` 或"历史"按钮打开 HistoryScreen，去重显示，点击复制到剪贴板
4. **收藏命令**: ⭐ 按钮切换收藏/取消，`Ctrl+F` 或"收藏夹"按钮打开 FavoritesScreen，支持删除和复制
5. **快捷键**: `Ctrl+H` 历史, `Ctrl+F` 收藏夹

**影响文件**: `nb_cmd/modes/tui_mode.py`

---

## 2026-05-15: TUI 全局参数面板（__init__ 参数输入）

**需求**: TUI 模式缺少 Web 模式中的"全局选项"面板，无法输入 `__init__` 参数（如 `verbose`、`path` 等）。

**实现**:
1. 新增 `_detect_init_params()` 函数：提取 `__init__` 方法的参数信息（名称、类型、默认值、描述）
2. 在左栏命令树下方增加"▶ 全局参数"区域，根据参数类型自动生成 Input/Switch/Select widgets
3. 执行时通过 `_collect_init_params()` 收集当前值，`_make_instance()` 创建新实例 + 注入 nbctx
4. 每次执行都使用新实例（与 Web 模式一致），保证全局参数变更即时生效

**影响文件**: `nb_cmd/modes/tui_mode.py`

---

## 2026-05-15: TUI 命令中断（停止按钮 + Ctrl+X）

**需求**: 用户在 TUI 中执行长时间运行的命令（exec 或普通方法）时，需要能中断停止。

**实现**:
1. **`base.py` shell()**: 对 `Popen` 流式模式增加 `except KeyboardInterrupt`，收到中断时 `proc.kill()` 杀掉子进程，然后 re-raise
2. **`tui_mode.py`**: 新增"停止"按钮（`btn-stop`）+ `Ctrl+X` 快捷键
   - 执行中记录 `_worker_tid`（工作线程 ID）
   - 停止时通过 `ctypes.pythonapi.PyThreadState_SetAsyncExc` 向工作线程注入 `KeyboardInterrupt`
   - `_do_execute` 捕获 `KeyboardInterrupt` 显示黄色 `[已取消]`
   - 执行按钮在运行时 disabled，停止按钮反之

**效果**: exec 子进程会被 kill，普通 Python 方法会收到 KeyboardInterrupt 异常中断

**影响文件**: `nb_cmd/core/base.py`, `nb_cmd/modes/tui_mode.py`

---

## 2026-05-15: shell() 命令执行改为 Popen 流式输出

**问题**: `shell(cmd, capture=False)` 使用 `subprocess.run(capture_output=True)` 全量缓冲子进程输出，必须等进程完全结束才一次性 print。在 TUI/Web 模式下，长时间运行的 exec 命令（如 `python print_many.py`）看起来"无反应"，输出不实时。

**修复**: `capture=False` 分支改为 `subprocess.Popen(stdout=PIPE, stderr=STDOUT, bufsize=1)` + 逐行 `print(line, end='')`，实现实时流式输出。`capture=True` 分支保持 `subprocess.run` 不变（用于返回 stdout 字符串）。

**效果**: TUI/Web/CLI 三种模式下的 `exec` 命令和 `self.shell()` 调用均可实时看到子进程输出，无需等待结束。

**影响文件**: `nb_cmd/core/base.py`（`shell()` 方法）

---

## 2026-05-15: 新增 TUI 终端交互模式（基于 Textual）

**需求**: Web 模式在多用户场景下存在先天缺陷——对象状态隔离、stdout 多用户分发、端口管理等问题。TUI 模式基于 Textual 框架，每个用户在独立终端/进程中运行，天然隔离，零配置。

**核心设计**:
1. **两阶段界面**: 首屏（DocScreen）渲染 CmdGen Markdown 文档 → 按 Enter 进入交互界面（MainScreen）
2. **左右分栏**: 左侧 40% 命令树 + 参数表单，右侧 60% 输出控制台（RichLog，支持竖向滚动）
3. **stdout 重定向**: `_TuiWriter` 按行缓冲，通过 `app.call_from_thread()` 安全写入 RichLog（无需 `_io_dispatch` / `threading.local()`）
4. **类型→Widget 映射**: `str`→Input, `int/float`→Input+验证, `bool`→Switch, `Enum`→Select
5. **命令执行**: 使用 Textual `@work(thread=True)` 在工作线程中执行，避免阻塞 UI 事件循环
6. **nbctx 支持**: 与 Web/API 模式一致，执行前自动调用 `make_nbctx()` 并递归注入子命令组

**启动方式**: `python app.py --tui`（与 `--web` 并列）

**依赖**: `pip install nb-cmd[tui]`（Textual >= 1.0.0, Python >= 3.8）

**影响文件**:
- `nb_cmd/modes/tui_mode.py`（新增：TUI 入口 + DocScreen + MainScreen + NbCmdTuiApp）
- `nb_cmd/core/base.py`（`run()` 增加 `--tui` 分支 + `_start_tui()` 方法）
- `nb_cmd/core/parser.py`（argparse 增加 `--tui` 参数 + full-help 文本）
- `nb_cmd/core/gen_cmd.py`（System Params 表格 + Quick Start 增加 `--tui`）
- `pyproject.toml`（新增 `tui` 可选依赖组，`all` 组包含 textual）
- `tests/ai_docs/tui_mode_plan.md`（详细设计方案文档）

---

## 2026-04-20: exec 内置命令始终排在命令列表最前面

**需求**: `exec` 万能命令在 CLI --help、Web UI、API 文档中应始终排在所有命令的最前面，不参与字母排序。

**问题**: `discover_commands()` 中 `for name in sorted(dir(instance))` 按字母排序遍历方法，`exec` 被排在 `e` 开头的位置。

**修复**: 在 `discover_commands()` 返回前，将内置命令（`exec`）从 `OrderedDict` 中提取出来，重新构造一个新的 `OrderedDict`，内置命令在前，其余命令保持字母排序在后。

**设计要点**:
- 仅在 `_BUILTIN_COMMANDS` 非空时（即 `include_builtins=True` 且 `enable_exec=True`）才做排序调整
- 子命令组（`include_builtins=False`）不受影响
- CLI / Web / API 三个模式都使用 `discover_commands` 返回的 `OrderedDict`，因此只需修改一处即可全部生效

**影响文件**:
- `nb_cmd/core/discovery.py`（`discover_commands` 函数末尾新增内置命令置顶逻辑）
- `tests/ai_codes/regression_testing/test_exec_order.py`（新增 5 个专项测试）

---

## 2026-04-19: Meta 新增 hide_method_list / auth_token / timeout 三字段

**需求**: 在 `NbCmdMeta` 中新增三个控制字段，增强框架的安全性和稳定性。

### 1. `hide_method_list: Optional[List[str]] = None`（命令黑名单）
- 与 `allow_method_list`（白名单）互补的黑名单机制
- 当同时配置白名单和黑名单时，白名单优先（黑名单被忽略）
- 仅限制 CLI/API/Web 暴露，Python 直接调用不受影响
- 支持路径写法：`'beta'`、`'sub.inner_b'`、`'sub/inner_b'`
- 支持隐藏整个子命令组：`hide_method_list = ['sub']`

### 2. `auth_token: Optional[str] = None`（简易 Bearer token 鉴权）
- 配置后 API/Web 请求须带 `Authorization: Bearer <token>` 头
- 不影响 `/docs`、`/redoc`、`/openapi.json` 等文档路径
- 无 token 返回 401，token 错误返回 403
- 通过 Starlette `BaseHTTPMiddleware` 实现

### 3. `timeout: int = 0`（命令执行超时）
- 0 表示不限时间（默认）
- CLI 模式：通过 `concurrent.futures.ThreadPoolExecutor` 实现超时
- API 模式：通过 `asyncio.wait_for` 实现超时
- Web UI 模式：通过后台定时器线程自动取消正在执行的命令

**影响文件**:
- `nb_cmd/core/meta.py`（新增 3 个字段定义）
- `nb_cmd/core/discovery.py`（`discover_commands` 新增 `hide_method_list` 参数 + `_is_method_hidden`/`_is_group_hidden` 判断函数）
- `nb_cmd/modes/cli_mode.py`（传递 hide_method_list + `_run_method_with_timeout` 超时执行）
- `nb_cmd/modes/api_mode.py`（传递 hide_method_list + `_install_auth_middleware` + `asyncio.wait_for` 超时）
- `nb_cmd/modes/web_mode.py`（传递 hide_method_list + auth_token 中间件 + 后台超时定时器）
- `nb_cmd/core/parser.py`（全链路传递 hide_method_list）
- `nb_cmd/core/gen_cmd.py`（全链路传递 hide_method_list + `_get_hide_method_list`）
- `tests/ai_codes/testnbcmds/test_hide_timeout_auth.py`（新增 13 个专项测试）

---

## 2026-04-19: allow_method_list 命令白名单（仅限制 CLI/API/Web）

**需求**: 增加 `Meta.allow_method_list`，当用户指定白名单时，仅暴露指定命令；未指定时暴露全部命令。该限制只作用于 CLI / REST API / Web UI，Python 代码直接调用类方法不受影响。

**实现**:
1. `discover_commands()` 新增 `allow_method_list` + `command_prefix` 参数，统一做命令过滤
2. 支持路径写法：`status`、`db.migrate`、`db/migrate`、`db migrate`
3. 对命令组做“前缀保留”逻辑：当白名单包含 `db/migrate` 时，`db` 组自动保留
4. CLI/API/Web/Help/CmdGen 全链路接入白名单参数，行为一致

**影响文件**:
- `nb_cmd/core/discovery.py`（新增路径归一化、祖先命中、组前缀保留过滤逻辑）
- `nb_cmd/modes/cli_mode.py`（CLI 执行链路接入 allow_method_list）
- `nb_cmd/core/parser.py`（argparse + full-help + easy-help 接入 allow_method_list）
- `nb_cmd/modes/api_mode.py`（REST 路由注册递归接入 allow_method_list）
- `nb_cmd/modes/web_mode.py`（Web 命令树与执行解析接入 allow_method_list）
- `nb_cmd/core/gen_cmd.py`（CmdGen 文档/目录接入 allow_method_list）
- `nb_cmd/core/meta.py`（新增字段注释，默认 `None`）
- `examples/github_cli_demos/gh_nb_cmd.py`（Meta 中补充 allow_method_list 用法示例注释）
- `tests/ai_codes/testnbcmds/test_allow_method_list.py`（新增专项测试）

## 2026-04-19: README 全面更新（nbctx + async + help_mode + 并发安全）

**更新内容**:
1. 新增 "nbctx 跨层级上下文传递" 章节（第 7 节），展示 dataclass + 直接赋值模式
2. 竞品对比表新增 "跨层级强类型上下文" 和 "async 方法支持" 两行
3. "你写什么→你得到什么" 表格新增 `self.nbctx` 行
4. Meta 配置表新增 `help_mode` 字段说明
5. 帮助系统章节补充 `Meta.help_mode` 配置用法
6. 新增 "async 方法支持" 章节（第 14 节）
7. Web UI 特性表新增 "并发安全" 行

**影响文件**: `README.md`

## 2026-04-19: CLI 模式 _apply_init_args 改为重新调用 __init__（Plan A）

**问题**: 用户在 `__init__` 中直接赋值 `self.nbctx = GhCtx(repo=self.repo, ...)` 时，CLI 模式下 `self.nbctx` 拿到的是默认值而非 CLI 传入的值。原因是 CLI 执行流程为：
1. `instance = Cls()` → `__init__` 用默认参数执行，`self.nbctx` 拿到默认值
2. `_apply_init_args(instance, parsed)` → 用 `setattr` 逐个更新 `self.repo` 等属性
3. `_ensure_nbctx(instance)` → 但 `self.nbctx` 已经不是 `None`，跳过 `make_nbctx()`
结果：`self.nbctx` 仍是步骤 1 的默认值。

**修复（Plan A）**: 将 `_apply_init_args` 从"setattr 逐个设属性"改为"收集 kwargs 后重新调用 `instance.__init__(**kwargs)`"。这样 `__init__` 中的 `self.nbctx = GhCtx(...)` 第二次执行时能拿到 CLI 解析的值。

**Web/API 模式无需修改**: Web 模式的 `_user_cls(**kwargs)` 和 API 模式的 `_cls(**merged)` 已经直接带参数调用 `__init__`，直接赋值本身就能工作。

**影响文件**:
- `nb_cmd/modes/cli_mode.py` (`_apply_init_args` 改为收集 kwargs + 重新调用 `__init__`)
- `examples/github_cli_demos/gh_nb_cmd.py` (从 `make_nbctx()` 模式改为直接赋值模式)
- `tests/ai_codes/test_direct_nbctx.py` (新增直接赋值测试脚本)

**用户现在有两种等价的上下文传递方式**:
```python
# 方式 1: 直接赋值（更简洁）
def __init__(self, repo=None):
    self.repo = repo
    self.nbctx = GhCtx(repo=self.repo)

# 方式 2: make_nbctx 模板方法（经典方式）
def __init__(self, repo=None):
    self.repo = repo
def make_nbctx(self):
    return GhCtx(repo=self.repo)
```

## 2026-04-19: unwrap_arg 修复 Optional[Annotated[...]] 解析

**问题**: `get_type_hints(method, include_extras=True)` 会把 `default=None` 的 `Annotated[str, '描述']` 参数自动包装为 `Optional[Annotated[str, '描述']]`（即 `Union[Annotated[str, '描述'], None]`）。`unwrap_arg` 只处理了直接的 `Annotated[...]`，没有处理外层 `Optional` 包装的情况，导致：
- 类型显示为 `Annotated[str, '描述']` 而非 `str`
- 描述和别名丢失（显示为 `-`）

**修复**: 在 `unwrap_arg` 中增加 `Optional[Annotated[...]]` 的检测。如果 hint 是 `Optional` 类型，先 unwrap Optional 得到内层类型，再检查内层是否为 `Annotated`，递归调用 `unwrap_arg` 处理。

**影响文件**:
- `nb_cmd/core/arg.py` (新增 `_is_optional()`, `_unwrap_optional()` 辅助函数，`unwrap_arg` 增加 Optional 分支)

## 2026-04-19: GitHub CLI 三框架对比示例

**需求**: 创建 GitHub CLI (`gh`) 风格的对比示例，展示 nb_cmd 在多层级命令+全参数场景下对 Click/Typer 的碾压优势。

**文件**:
- `examples/github_cli_demos/gh_click.py` — Click 实现（49 个装饰器，ctx.obj 字典传递）
- `examples/github_cli_demos/gh_typer.py` — Typer 实现（模块全局变量，add_typer 管理）
- `examples/github_cli_demos/gh_nb_cmd.py` — nb_cmd 实现（零装饰器，make_nbctx 强类型穿透，CmdGen 自动文档）
- `examples/github_cli_demos/gh_nb_cmd_gen_doc.md` — CmdGen 自动生成的 Markdown 文档
- `examples/github_cli_demos/gh_comparison.md` — 三框架对比总结文档

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

**四种模式均支持**:
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

