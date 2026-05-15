# nb_cmd TUI 模式设计方案

> 创建时间: 2026-05-15
> 状态: 设计阶段，待实现

---

## 一、总体目标

为 nb_cmd 新增 `--tui` 模式，基于 [Textual](https://github.com/textualize/textual) 框架，提供终端内的图形交互界面。

**核心理念**: TUI 模式天然是"一个终端 = 一个进程 = 一个用户"，不需要 Web 模式中的 `_io_dispatch`、`threading.local()`、WebSocket 等多用户隔离机制。

**启动方式**:
```bash
python app.py --tui             # 启动 TUI 模式
python app.py --tui-theme dark  # 可选：指定主题（后续考虑）
```

---

## 二、界面流程（两阶段）

### 阶段 1：Markdown 文档首屏

进入 TUI 后，**全屏显示 CmdGen 自动生成的 Markdown 文档**。

- 使用 Textual 内置的 `Markdown` Widget 渲染
- 内容来源: `CmdGen(cls, fmt='markdown').doc()`，与现有的 `gen-doc` 命令输出一致
- 支持上下滚动浏览
- 底部 Footer 显示快捷键提示："按 Enter 进入交互模式 | 按 Q 退出"
- 按 Enter/空格 后切换到阶段 2 的交互界面

**实现要点**:
- 首屏是一个独立的 Textual `Screen`（命名为 `DocScreen`）
- `CmdGen._build_md_doc()` 已经能生成完整的 Markdown 文档，直接复用

### 阶段 2：左右分栏交互界面（主界面）

按照现有 Web 前端的功能布局，**左右分栏**。

```
┌───────────────────────────────┬────────────────────────────────┐
│  左侧面板 (40%)               │  右侧面板 (60%)                │
│                               │                                │
│  ┌─ 命令树 ─────────────┐    │  ┌─ 输出控制台 ──────────────┐ │
│  │ ▼ (root)             │    │  │                            │ │
│  │   ├─ calc            │    │  │ $ calc --a 3 --b 5         │ │
│  │   ├─ ping            │    │  │ 结果: 8                    │ │
│  │   ├─ scan            │    │  │                            │ │
│  │   └─ gen-doc         │    │  │ $ ping --host google.com   │ │
│  └──────────────────────┘    │  │ PING google.com ...        │ │
│                               │  │ 64 bytes from ...          │ │
│  ┌─ 参数表单 ───────────┐    │  │                            │ │
│  │ 命令: calc            │    │  │                            │ │
│  │ --a: [___________]    │    │  │ ▼ 支持竖向滚动             │ │
│  │ --b: [___________]    │    │  │                            │ │
│  │                       │    │  └────────────────────────────┘ │
│  │ [执行]  [清除]        │    │                                │
│  └──────────────────────┘    │                                │
│                               │                                │
├───────────────────────────────┤                                │
│  Footer: 快捷键提示            │                                │
└───────────────────────────────┴────────────────────────────────┘
```

---

## 三、左侧面板详细设计

### 3.1 命令树（上半部分）

**Widget**: Textual `Tree`

**数据来源**: `discover_commands(instance, base_cls)` 返回的 OrderedDict

**行为**:
- 顶层显示所有命令和子命令组
- 子命令组可展开/折叠，显示内部命令
- 支持多层级嵌套（递归构建 Tree）
- 选中某个可执行命令（叶子节点）后，下方参数表单区域**动态刷新**为该命令的参数
- 选中子命令组（非叶子节点）时，参数区清空或显示组描述

**类比 Web 前端**: 对应 `renderGroup()` 函数的命令折叠面板

### 3.2 全局参数区（可选区域）

如果顶层类有 `__init__` 参数（全局参数），在命令树上方显示一个可折叠的"全局选项"区域。

**数据来源**: `_build_init_params_info(instance)` 返回的参数列表

**类比 Web 前端**: 对应 `#initParamsArea` 区域

### 3.3 参数表单（下半部分）

**动态生成**: 根据选中命令的方法签名，构建输入控件。

**Python 类型 → Textual Widget 映射**:

| Python 类型 | Web Widget | Textual Widget | 备注 |
|------------|-----------|----------------|------|
| `str` | `<input type="text">` | `Input` | 文本输入 |
| `int` | `<input type="number">` | `Input` + `Integer` validator | 整数验证 |
| `float` | `<input type="number">` | `Input` + `Number` validator | 浮点验证 |
| `bool` | `<input type="checkbox">` | `Switch` 或 `Checkbox` | 开关 |
| `Enum` | `<select>` | `Select` | 下拉选择 |
| `list` | tags 输入 | `Input`（逗号分隔） | 简化处理 |

**每个参数显示**:
- 参数名 Label（必填参数标注 `*`）
- 对应的输入控件
- 默认值预填充
- 参数描述（来自 `Annotated` 的 desc）

**底部按钮**:
- `执行` 按钮（`Button(variant="primary")`）
- `清除` 按钮（`Button(variant="default")`）
- 支持快捷键 Ctrl+Enter 执行

**类比 Web 前端**: 对应 `renderParamFields()` + `renderCmdSection()` 的表单区域

---

## 四、右侧面板详细设计

### 4.1 输出控制台

**Widget**: Textual `RichLog`

**核心优势**: `RichLog` 原生支持 Rich 库的所有格式化输出（表格、颜色、进度条、树形结构）。`cmdui` 的 `table()`、`kv()`、`tree()` 等都基于 Rich/print，在 `RichLog` 里可以原生渲染，不需要 Web 模式中的 ANSI-to-HTML 转换。

**特性**:
- **竖向滚动条**: `RichLog` 自带，无需额外处理
- **实时输出**: 方法执行中的 `print()` 实时显示
- **命令回显**: 每次执行前打印 `$ command --arg value` 格式的命令行
- **结果显示**: 执行完成后显示返回值和耗时
- **错误高亮**: 异常信息用红色显示

**类比 Web 前端**: 对应 `#consoleOutput` 的控制台区域，但实现更简单

### 4.2 状态栏

控制台顶部或底部显示执行状态：
- 就绪 / 执行中 / 完成 / 出错
- 执行耗时

---

## 五、stdout 重定向策略

### 5.1 问题

Textual 接管终端后，`print()` 不能直接输出到终端（会破坏 TUI 界面）。需要将用户方法中的 `print()` 重定向到 `RichLog` Widget。

### 5.2 方案

在命令执行线程中，临时将 `sys.stdout` 替换为一个自定义 writer，该 writer 将内容写入 `RichLog`。

```python
class _TuiWriter:
    def __init__(self, rich_log, app):
        self._log = rich_log
        self._app = app

    def write(self, data):
        if data:
            self._app.call_from_thread(self._log.write, data)

    def flush(self):
        pass
```

**关键点**:
- 用户方法在**工作线程**中执行（避免阻塞 Textual 事件循环）
- 通过 `app.call_from_thread()` 安全地从工作线程更新 UI
- **不需要 `threading.local()` 隔离**——因为 TUI 是单用户单进程，任何时刻只有一个命令在执行

### 5.3 与 Web 模式的对比

```
Web 模式:
  print() → _DispatchWriter → threading.local() → Queue → WebSocket → 前端 ANSI-to-HTML
  （7 个环节，需要线程隔离）

TUI 模式:
  print() → _TuiWriter → app.call_from_thread() → RichLog.write()
  （3 个环节，无需隔离）
```

---

## 六、命令执行流程

```
用户选择命令 → 填写参数 → 点击"执行"
    │
    ├── 1. 获取 init_params（全局参数）
    ├── 2. 实例化用户类: instance = _user_cls(**init_params)
    ├── 3. 注入 nbctx: instance.nbctx = instance.make_nbctx()
    ├── 4. 解析命令路径（支持子命令组嵌套）
    ├── 5. 获取目标方法和参数
    ├── 6. 控制台回显命令: "$ command --arg value"
    ├── 7. 在工作线程中执行方法（stdout 重定向到 RichLog）
    │      ├── before_run()
    │      ├── method(**kwargs)
    │      └── after_run()
    ├── 8. 显示返回值和耗时
    └── 9. 异常处理: on_error() + 红色错误信息
```

**复用现有代码**:
- `discover_commands()` — 命令发现
- `_build_init_params_info()` — 全局参数提取
- `_build_cmd_info()` — 命令参数提取
- `_convert_request_params()` — 参数类型转换
- `handle_api_result()` — 结果格式化
- `CmdGen._build_md_doc()` — Markdown 文档生成

---

## 七、从 Web 模式迁移的功能清单

### 需要实现的（Web → TUI 对照）

| Web 前端功能 | TUI 实现方式 | 优先级 |
|-------------|------------|--------|
| 命令折叠面板 | `Tree` Widget | P0 |
| 参数表单（text/number/checkbox/select） | `Input` / `Switch` / `Select` | P0 |
| 实时控制台输出 | `RichLog` | P0 |
| 竖向滚动条 | `RichLog` 自带 | P0 |
| 执行/清除按钮 | `Button` | P0 |
| 全局参数面板 | `Collapsible` + 表单 | P1 |
| 状态栏 | `Footer` 或 `Static` | P1 |
| 命令行输入框 | `Input` + Tab 补全 | P2 |
| 收藏命令 | 本地 JSON 文件 | P3 |
| 命令历史 | 本地 JSON 文件 | P3 |

### 不需要实现的（Web 特有，TUI 无需关心）

| Web 功能 | 原因 |
|----------|------|
| `_io_dispatch.py` / `_DispatchWriter` | 单进程，无需线程级隔离 |
| WebSocket 通信 | 无需 C/S 通信 |
| ANSI-to-HTML 转换 | `RichLog` 原生支持 Rich 格式 |
| CORS 中间件 | 无 HTTP |
| SQLite 历史/收藏 | 用本地 JSON 文件即可 |
| Auth token 中间件 | 本地终端，不需要鉴权 |
| 端口管理 | 无端口 |
| Resizer 拖拽分割条 | 固定比例或快捷键调整 |
| HTTP fallback | 无需 |

---

## 八、文件结构

```
nb_cmd/
  modes/
    cli_mode.py      # 现有
    api_mode.py       # 现有
    web_mode.py       # 现有
    tui_mode.py       # 新增: TUI 入口 + Textual App
  core/
    base.py           # 修改: run() 增加 --tui 分支
    parser.py         # 修改: full-help 的 System Params 增加 --tui 描述
    gen_cmd.py        # 修改: System Params 表格增加 --tui
    meta.py           # 可选: 增加 tui 相关配置
```

### tui_mode.py 内部结构（预估）

```python
# 主要类/函数:

class NbCmdTuiApp(App):
    """Textual App 主类"""

class DocScreen(Screen):
    """首屏：Markdown 文档展示"""

class MainScreen(Screen):
    """主界面：左右分栏交互"""

class CommandTree(Tree):
    """命令树 Widget"""

class ParamForm(Container):
    """动态参数表单容器"""

class OutputConsole(RichLog):
    """右侧输出控制台"""

def start_tui(instance, base_cls):
    """TUI 入口函数（类似 start_web_server）"""
```

---

## 九、修改点清单

### base.py

```python
def run(self, args=None):
    raw_args = args if args is not None else sys.argv[1:]

    help_result = self._handle_help(raw_args)
    if help_result is not None:
        return help_result

    if '--web' in raw_args:
        return self._start_web_server(raw_args)

    if '--tui' in raw_args:                          # 新增
        return self._start_tui(raw_args)              # 新增

    from ..modes.cli_mode import run_cli
    return run_cli(self, NbCmd, args)

def _start_tui(self, raw_args):                       # 新增
    """启动 TUI 模式"""
    from ..modes.tui_mode import start_tui
    start_tui(self, NbCmd)
```

### parser.py / gen_cmd.py

- System Params 表格增加 `--tui` 行
- Quick Start 增加 `--tui` 示例

### pyproject.toml

新增可选依赖组:
```toml
[project.optional-dependencies]
tui = ["textual>=1.0.0"]
```

---

## 十、依赖与兼容性

| 项目 | 要求 |
|------|------|
| Textual | >= 1.0.0（最新 v8.2.3） |
| Python | >= 3.8（Textual 不支持 3.7） |
| nb_cmd 现有 3.7 支持 | 不受影响，TUI 为可选依赖 |
| 安装方式 | `pip install nb-cmd[tui]` |

如果在 Python 3.7 上使用 `--tui`，应给出友好提示:
```
TUI 模式需要 Python 3.8+ 和 textual 库:
  pip install nb-cmd[tui]
```

---

## 十一、实现分期

### Phase 1: 最小可用版本（P0 功能）
1. `tui_mode.py` 基础框架 + `NbCmdTuiApp`
2. `DocScreen`: Markdown 首屏
3. `MainScreen`: 左右分栏
4. 命令树（支持多层级）
5. 参数表单（str / int / float / bool / Enum）
6. `RichLog` 输出控制台（竖向滚动条）
7. 执行按钮 + stdout 重定向
8. `base.py` 增加 `--tui` 入口

### Phase 2: 完善体验（P1 功能）
1. 全局参数面板
2. 状态栏
3. 快捷键（Ctrl+Enter 执行、Ctrl+L 清空控制台等）
4. async 方法支持
5. 命令执行取消
6. 超时控制（`Meta.timeout`）

### Phase 3: 增强功能（P2-P3 功能）
1. 命令行输入框 + Tab 补全
2. 命令历史（本地 JSON）
3. 收藏命令
4. 主题支持（light/dark）
5. `allow_method_list` / `hide_method_list` 支持

---

## 十二、关键设计决策记录

| 决策点 | 选择 | 理由 |
|--------|------|------|
| 首屏与交互界面切换 | 两个 `Screen`，按键切换 | 简单直观，Textual 原生支持 Screen 栈 |
| 左右面板比例 | 固定 40:60 | TUI 不方便做拖拽分割条，固定比例足够 |
| stdout 重定向 | 自定义 Writer + `call_from_thread` | 最简方案，无需隔离 |
| 命令历史存储 | 本地 JSON 文件 `~/.nb_cmd_history.json` | 比 SQLite 轻量，TUI 场景足够 |
| 取消执行 | `ctypes.PyThreadState_SetAsyncExc` | 与 Web 模式一致 |
| 依赖安装 | `pip install nb-cmd[tui]` | 不强制所有用户安装 Textual |
