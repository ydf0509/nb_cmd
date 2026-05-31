

# nb_cmd AI Skill 生成器规划文档

> 目标：让 nb_cmd 支持「一次编写，七处运行」——在原有 CLI / REST API / Web UI / TUI / Markdown / Python 本地调用 六种能力基础上，新增 **AI Skill 自动生成**能力，使任何继承 `NbCmd` 的类都能一键输出符合 [agentskills.io](https://agentskills.io) 国际开放标准的 Skill 文件夹。

---

## 一、背景与动机

### 1.1 现状
nb_cmd 已实现「一次编写，六种能力」：

| 能力 | 说明 |
|------|------|
| Python 本地调用 | 类方法直接执行 |
| CLI | 自动生成 argparse 命令行 |
| REST API | FastAPI 路由 + Swagger |
| Web UI | 前端输入框 + WebSocket 实时控制台 |
| TUI | Textual 终端交互界面 |
| Markdown 文档 | CmdGen 自动生成高质量文档 |

### 1.2 痛点
AI 编程工具（Cursor、Claude Code、Codex、GitHub Copilot 等）日益普及，但：
- AI 不了解用户自定义的 nb_cmd 工具具体有哪些命令、参数、用法
- 每次让 AI 调用用户的 nb_cmd 工具，都需要重复解释命令结构和参数含义
- 没有标准化的方式把 nb_cmd 工具封装成 AI 可识别的「Skill」

### 1.3 目标
为任意 `NbCmd` 子类**自动生成**符合 [Agent Skills Open Standard](https://agentskills.io) 的 Skill 文件夹，让 AI 能：
1. 自动识别何时应该调用该工具（通过 `description`）
2. 了解完整的命令结构和参数（通过 `SKILL.md` body）
3. 按规范执行命令或调用 API（通过 scripts/ 辅助脚本）

---

## 二、参考标准与调研结论

### 2.1 agentskills.io 核心规范

**目录结构：**
```
skill-name/
├── SKILL.md          # 必需：YAML frontmatter + Markdown 指令正文
├── scripts/          # 可选：可执行脚本
├── references/       # 可选：参考文档（按需加载）
└── assets/           # 可选：模板、配置等静态资源
```

**SKILL.md Frontmatter 必需字段：**

| 字段 | 约束 | 说明 |
|------|------|------|
| `name` | 1-64字符，小写字母/数字/连字符，必须和文件夹名一致 | Skill 唯一标识 |
| `description` | 1-1024字符，非空 | 描述 WHAT（做什么）+ WHEN（何时用），决定 AI 是否激活本 Skill |

**可选字段：** `license`, `compatibility`, `metadata`, `allowed-tools`

**Progressive Disclosure（渐进式加载）：**
1. **Phase 1: Metadata** (~100 tokens) — 只读取所有 Skill 的 `name` + `description`
2. **Phase 2: Instructions** (< 5000 tokens 推荐) — 激活后读取完整 `SKILL.md`
3. **Phase 3: Resources** (按需) — 需要时才加载 `scripts/` / `references/` / `assets/`

**关键约束：**
- `SKILL.md` 建议不超过 500 行
- 详细参考资料应拆分到 `references/` 目录
- 脚本应自包含、有错误处理

### 2.2 Cursor Skills 实践启示

通过分析 `C:\Users\ydf19\.cursor\skills-cursor` 中的 13 个官方 Skill：

| Skill | 特点 | 可借鉴点 |
|-------|------|---------|
| `shell` | `disable-model-invocation: true`，极简指令 | 命令类 Skill 应禁止自动触发，需显式调用 |
| `create-skill` | 详细的结构说明 + 最佳实践 | Skill 自身的 SKILL.md 也应有清晰的结构模板 |
| `sdk` | 多语言并排示例 + 决策树 | 参数和用法示例要覆盖多种调用方式 |
| `babysit` | 步骤编号 + 明确边界（什么不做）| 指令中要明确 AI 的职责边界 |
| `loop` | 动态/固定两种模式 + 代码示例 | 复杂参数行为要用示例说明 |
| `statusline` | JSON Schema 表格 + 配置示例 | 参数表格化呈现，易于 AI 理解 |

**结论：** 生成的 SKILL.md 应该是「教 AI 如何使用这个 nb_cmd 工具」的说明书，而不是给人看的文档。要强调：
- 什么时候激活这个 Skill
- 有哪些子命令/子命令组
- 每个命令的参数名、类型、默认值、是否必填
- 具体的命令行示例（可直接复制执行）
- Python 直接调用的示例（如 AI 需要程序化调用）

---

## 三、整体设计

### 3.1 新增能力定位

```
用户写的一个 NbCmd 子类
        ↓
   ┌────┴────┬──────────┬──────────┬──────────┬──────────┬──────────┐
   ↓         ↓          ↓          ↓          ↓          ↓          ↓
Python    CLI      REST API    Web UI      TUI      Markdown    AI Skill
调用                                                    文档      (新增)
```

### 3.2 核心类设计：`SkillGen`

参考 `CmdGen` 的实现模式，新增 `SkillGen` 类，专用于生成 AI Skill 文件夹。

```python
from nb_cmd import SkillGen

# 基础用法：生成 Skill 文件夹
g = SkillGen(MyApp, output_dir='./skills/my-app')
g.gen()  # 生成完整的 skill-name/ 文件夹

# 高级用法：自定义元数据
g = SkillGen(
    MyApp,
    output_dir='./skills/my-app',
    name='my-app',                    # 默认从 Meta.name 或类名转 kebab-case
    description='xxx',                # 默认从 Meta.description 或类 docstring
    license='MIT',
    compatibility='Requires Python 3.8+',
    metadata={'author': 'team', 'version': '1.0'},
    scripts=True,                     # 是否生成 scripts/ 辅助脚本
    references=True,                  # 是否生成 references/ 详细参数文档
    include_python_examples=True,     # 是否在 SKILL.md 中包含 Python 调用示例
    include_cli_examples=True,        # 是否在 SKILL.md 中包含 CLI 命令示例
    include_api_examples=False,       # 是否在 SKILL.md 中包含 REST API 调用示例
)
g.gen()
```

### 3.3 生成文件夹结构

以 `MyApp`（Meta.name='cloud-tool'）为例：

```
cloud-tool/                    # 文件夹名 = frontmatter.name
├── SKILL.md                   # 核心文件
├── scripts/
│   ├── run_cli.py             # CLI 命令执行封装（可选）
│   └── call_api.py            # REST API 调用封装（可选）
└── references/
    ├── commands.md            # 完整命令参考（当命令很多时分流）
    └── parameters.md          # 参数详细说明（可选）
```

### 3.4 SKILL.md 内容生成策略

SKILL.md = YAML Frontmatter + Markdown Body，Body 的核心是**教 AI 如何使用这个工具**。

**Body 建议结构：**

```markdown
# <工具名称>

## 概述
简要介绍这个工具是做什么的。

## 何时使用
明确列出 AI 应该在什么场景下激活这个 Skill。这是决定 AI 是否选择本 Skill 的关键。

## 命令结构
说明命令的调用方式：
- CLI: `python script.py [全局参数] <子命令> [命令参数]`
- Python: `app.sub_group.method(param=value)`
- API: `POST /api/v1/sub_group/method`

## 全局参数
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| --region | str | beijing | 部署区域 |

## 命令列表

### db migrate
迁移数据库。

**参数：**
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| --dry-run | bool | False | 仅预览不执行 |

**CLI 示例：**
```bash
python app.py --region beijing db migrate --dry-run
```

**Python 示例：**
```python
app = MyApp(region='beijing')
app.db.migrate(dry_run=True)
```

## 注意事项
- 子命令组通过 `sub_commands` 定义
- 全局参数在 `__init__` 中定义，会自动传递给所有子命令
- ...
```

---

## 四、详细设计

### 4.1 SkillGen 类 API

```python
class SkillGen(object):
    """
    AI Skill 文件夹生成器。

    根据 NbCmd 子类的结构，自动生成符合 agentskills.io 规范的 Skill 文件夹。
    """

    def __init__(
        self,
        entry_cls: Type[NbCmd],
        output_dir: str,
        *,
        script: str = None,              # 脚本名（用于 CLI 示例）
        python: str = None,              # Python 解释器路径
        name: str = None,                # Skill name（默认从 Meta.name 转 kebab-case）
        description: str = None,         # Skill description（默认从 Meta.description）
        license: str = None,
        compatibility: str = None,
        metadata: dict = None,
        allowed_tools: str = None,
        disable_model_invocation: bool = False,  # 默认允许 AI 自动触发
        # 内容生成控制
        include_cli_examples: bool = True,
        include_python_examples: bool = True,
        include_api_examples: bool = False,
        include_tui_guide: bool = False,
        # 可选目录控制
        generate_scripts: bool = False,
        generate_references: bool = False,
        max_skill_md_lines: int = 500,   # 超过则分流到 references/
    ):
        ...

    def gen(self) -> str:
        """
        生成 Skill 文件夹。

        Returns:
            str: 生成的 Skill 文件夹路径
        """
        ...

    def gen_skill_md(self) -> str:
        """生成 SKILL.md 内容字符串"""
        ...

    def gen_scripts(self) -> None:
        """生成 scripts/ 目录下的辅助脚本"""
        ...

    def gen_references(self) -> None:
        """生成 references/ 目录下的参考文档"""
        ...
```

### 4.2 name 生成规则

1. 若用户传入 `name`，校验是否符合 agentskills.io 规范（小写、连字符、长度等）
2. 否则从 `entry_cls.Meta.name` 获取，转为 kebab-case
3. 否则从类名 `entry_cls.__name__` 转 kebab-case（如 `MyApp` → `my-app`）
4. 最终必须和 `output_dir` 的 basename 一致

### 4.3 description 生成规则

1. 若用户传入 `description`，直接使用
2. 否则从 `entry_cls.Meta.description` 获取
3. 否则从类 docstring 获取第一行
4. 若都不存在，根据命令结构自动生成：
   ```
   <工具名称> —— <第一个子命令的 doc> 等。使用当需要执行 <name> 相关命令时。
   ```
5. 必须包含 **WHAT**（做什么）和 **WHEN**（何时用）

### 4.4 Markdown Body 生成策略

参照 `CmdGen._build_md_doc()` 的实现，但目标读者从「人类用户」变为「AI Agent」。

关键差异：

| 方面 | CmdGen (人类文档) | SkillGen (AI 指令) |
|------|-------------------|-------------------|
| 目标 | 给人看的参考手册 | 教 AI 如何调用工具 |
| 重点 | 美观、导航、TOC | 清晰的指令、示例、边界 |
| 示例 | 命令行示例 | CLI + Python + API 多模式示例 |
| 参数 | 表格展示 | 表格 + 强调必填/默认值 |
| 说明 | 功能描述 | 「何时使用」「不要做什么」 |

**Body 生成步骤：**

1. **Overview** — 工具一句话描述
2. **When to Use** — 触发场景（最关键，决定 AI 是否激活）
3. **Command Structure** — 三种调用方式的说明：
   - CLI: `python {script} [global_flags] <command_path> [command_flags]`
   - Python: `instance = EntryClass(**global_args); instance.group.method(**args)`
   - API: `POST /api/v1/{command_path}`（如果工具支持 web 模式）
4. **Global Parameters** — `__init__` 参数表格
5. **Commands** — 递归遍历所有命令和子命令组：
   - 每个命令：说明 + 参数表格 + CLI 示例 + Python 示例
   - 每个子命令组：说明 + 包含的命令列表
6. **Guidelines / Notes** — 使用约束和注意事项：
   - 全局参数自动传递
   - bool 参数的约定（`--flag` 表示 True）
   - 子命令组的调用链
   - 什么情况下不要用（边界控制）

### 4.5 内容过长时的分流策略

当生成的 SKILL.md 超过 `max_skill_md_lines`（默认 500 行）时：

1. 保留核心内容在 SKILL.md：概述、何时使用、命令结构、全局参数、命令索引（不含详细参数）
2. 将每个命令的详细说明拆分到 `references/commands.md`
3. 在 SKILL.md 中用链接引用：
   ```markdown
   See [commands reference](references/commands.md) for full parameter details.
   ```

这符合 Progressive Disclosure 原则：AI 先读 SKILL.md 了解全貌，需要时再读 references。

### 4.6 scripts/ 辅助脚本（可选）

当 `generate_scripts=True` 时，生成以下脚本：

**scripts/run_cli.py** — 封装 CLI 调用，便于 AI 安全执行：
```python
#!/usr/bin/env python3
"""Run a nb_cmd CLI command safely."""
import sys
import subprocess

def run(command_path: str, **kwargs):
    """
    Run a CLI command.
    
    Args:
        command_path: e.g. "db migrate" or "server ops deploy"
        **kwargs: command parameters
    """
    cmd = [sys.executable, "app.py"]  # script path from SkillGen
    # ... build command
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result

if __name__ == "__main__":
    import argparse
    # ...
```

**scripts/call_api.py** — 封装 REST API 调用（如果工具支持 web 模式）：
```python
#!/usr/bin/env python3
"""Call the REST API endpoint."""
import requests

def call(command_path: str, **kwargs):
    url = f"http://localhost:8000/api/v1/{command_path.replace(' ', '/')}"
    # ...
```

### 4.7 与现有 CmdGen 的关系

| | CmdGen | SkillGen |
|--|--------|----------|
| 输出 | 字符串 / Markdown 文件 | 完整文件夹 |
| 读者 | 人类 | AI Agent |
| 标准 | 自定义 Markdown | agentskills.io 国际规范 |
| 内容 | 文档 + 命令示例 | 指令 + 多模式示例 + 可选脚本 |
| 用途 | 给用户看 / 放 README | 给 AI 加载执行 |

实现上 SkillGen 可以复用 `CmdGen` 的以下内部逻辑：
- `_collect_init_params()` — 收集 `__init__` 参数
- `_collect_toc()` / `_collect_md_doc()` — 遍历命令树
- `_format_init_args()` / `_format_method_args()` — 格式化参数
- `discover_commands()` — 发现所有命令

但输出格式完全不同，因此 SkillGen 应作为独立类，内部调用共享的辅助函数（可能需要重构 `gen_cmd.py` 提取公共函数）。

---

## 五、文件变更计划

### 5.1 新增文件

| 文件 | 说明 |
|------|------|
| `nb_cmd/core/gen_skill.py` | `SkillGen` 核心类实现 |
| `tests/ai_codes/regression_testing/test_skill_gen.py` | SkillGen 回归测试 |

### 5.2 修改文件

| 文件 | 变更 |
|------|------|
| `nb_cmd/__init__.py` | 导出 `SkillGen` |
| `nb_cmd/core/gen_cmd.py` | 提取公共辅助函数（如 `_collect_init_params`, `discover_commands` 的结果处理）供 SkillGen 复用 |
| `README.md` | 新增「AI Skill 生成」章节 |

### 5.3 不修改的文件

- `core/base.py`, `core/meta.py` — 无需修改，SkillGen 是只读的「生成器」
- `modes/` 下的各种 mode — Skill 生成不依赖运行模式

---

## 六、实施步骤

### Phase 1: 基础设施（1-2 天）

1. **提取公共函数**
   - 将 `gen_cmd.py` 中的 `_collect_init_params`, `_find_command_path`, `_format_init_args`, `_format_method_args` 等提取为模块级公共函数
   - 确保 `SkillGen` 可以复用这些函数，不重复代码

2. **实现 SkillGen 核心骨架**
   - 实现 `__init__` 参数处理
   - 实现 `name` / `description` 的生成和校验逻辑
   - 实现 `gen()` 的目录创建和文件写入

### Phase 2: SKILL.md 生成（2-3 天）

1. **Frontmatter 生成**
   - YAML 序列化（注意 description 可能有多行，使用 `>-` block style）
   - 字段校验（name 规范、description 长度等）

2. **Body 生成**
   - Overview / When to Use 部分
   - Command Structure 说明（CLI / Python / API）
   - Global Parameters 表格
   - 递归生成 Commands 部分
   - Guidelines / Notes 部分

3. **内容分流逻辑**
   - 行数统计，超过阈值时拆分到 `references/`
   - 生成精简版 SKILL.md + 完整版 references/

### Phase 3: 可选目录生成（1 天）

1. **scripts/ 生成**
   - `run_cli.py` 模板
   - `call_api.py` 模板（如果 entry_cls 支持 web 模式）

2. **references/ 生成**
   - `commands.md` 完整命令参考
   - 参数详细说明文档

### Phase 4: 集成与测试（1-2 天）

1. **导出与集成**
   - `nb_cmd/__init__.py` 导出 `SkillGen`
   - 确保 `from nb_cmd import SkillGen` 可用

2. **回归测试**
   - 测试简单类（无子命令）
   - 测试带子命令组的类
   - 测试带全局参数的类
   - 测试 name/description 自动推导
   - 测试内容分流（大文件）
   - 验证生成的 Skill 能通过 `skills-ref validate`

3. **示例与文档**
   - 在 `examples/` 下添加 `gen_skill_demo.py`
   - 更新 `README.md`

---

## 七、使用示例（目标形态）

### 7.1 最简单用法

```python
from nb_cmd import SkillGen
from my_tool import MyApp

# 一键生成 Skill 文件夹
g = SkillGen(MyApp, output_dir='./skills/my-app')
g.gen()
# 输出: ./skills/my-app/SKILL.md
```

### 7.2 完整用法

```python
from nb_cmd import SkillGen
from my_tool import MyApp

g = SkillGen(
    MyApp,
    output_dir='./skills/cloud-tool',
    script='cloud_tool.py',
    name='cloud-tool',
    description='云平台管理工具。当需要管理服务器、数据库、执行部署操作时使用。',
    license='MIT',
    metadata={'author': 'ops-team', 'version': '2.0'},
    generate_scripts=True,
    generate_references=True,
)
path = g.gen()
print(f'Skill generated at: {path}')
```

### 7.3 生成的 SKILL.md 示例片段

```markdown
---
name: cloud-tool
description: >-
  云平台管理工具 —— 支持数据库备份/迁移、服务器信息查看/SSH连接、部署与重启等操作。
  当需要执行运维命令、管理云资源、部署服务或查看服务器状态时使用。
license: MIT
metadata:
  author: ops-team
  version: "2.0"
---

# Cloud Tool

## Overview
云平台管理工具，支持数据库管理、服务器运维、服务部署等功能。

## When to Use
当用户需要以下操作时激活此 Skill：
- 数据库备份、迁移、状态查看
- 服务器信息查看、SSH 连接
- 服务部署、重启
- 查看全局状态

## Command Structure

### CLI
```bash
python cloud_tool.py [全局参数] <子命令路径> [命令参数]
```

### Python
```python
from cloud_tool import MyApp
app = MyApp(region='beijing', env='prod')
# 直接调用方法
app.db.migrate(dry_run=True)
```

## Global Parameters

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--region` | `str` | `beijing` | 部署区域 |
| `--env` | `str` | `prod` | 运行环境 |
| `--debug` | `bool` | `False` | 开启调试模式 |

## Commands

### `status`
查看全局状态。

```bash
python cloud_tool.py --region beijing status
```

### `db` *(子命令组)*
数据库管理命令组。

#### `db migrate`
执行数据库迁移。

**参数：**
| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--dry-run` | `bool` | `False` | 仅预览不执行 |

**CLI:**
```bash
python cloud_tool.py --region beijing db migrate --dry-run
```

**Python:**
```python
app.db.migrate(dry_run=True)
```

## Guidelines
- 全局参数 `--region` 和 `--env` 会自动传递给所有子命令
- 布尔参数 `--debug` 默认 False，添加即启用
- 子命令组通过点号或空格访问，如 `db migrate` 或 `db.migrate`
- 部署操作前建议使用 `--dry-run` 预览
```

---

## 八、验收标准

1. **规范合规**：生成的 Skill 文件夹能通过 `skills-ref validate` 校验
2. **name 一致性**：文件夹名和 `SKILL.md` 中的 `name` 字段完全一致
3. **description 质量**：包含 WHAT + WHEN，长度在 1-1024 字符之间
4. **命令完整性**：覆盖所有公有方法（除内置方法和隐藏方法外）
5. **参数准确性**：参数名、类型、默认值、必填状态与类定义一致
6. **示例可执行**：生成的 CLI 示例和 Python 示例在语法上正确
7. **内容长度控制**：默认情况下 SKILL.md 不超过 500 行，超长自动分流到 references/
8. **与现有功能零冲突**：新增 SkillGen 不影响原有的六种能力

---

## 九、风险与注意事项

1. **description 质量**：自动生成的 description 可能不够精准，建议用户传入自定义 description
2. **SKILL.md 过长**：复杂工具（多层级子命令 + 大量参数）可能超出 AI 的上下文限制，分流策略很重要
3. **AI 理解差异**：不同 AI Agent（Cursor、Claude Code、Codex）对 Skill 的解析可能有差异，需参考各平台的实际表现调整模板
4. **scripts 安全性**：生成的脚本涉及 subprocess / HTTP 调用，应明确标注为「可选」，默认不生成
5. **渐进披露**： agentskills.io 的 Progressive Disclosure 是推荐实践，但具体 AI 客户端是否真正实现不确定，SkillGen 只需保证目录结构规范即可

---

## 十、附录：参考链接

- [Agent Skills Specification](https://agentskills.io/specification)
- [Agent Skills LLMs.txt](https://agentskills.io/llms.txt)
- [skills-ref 校验工具](https://github.com/agentskills/agentskills/tree/main/skills-ref)
- [Cursor Skills 最佳实践](https://www.cursor.com/blog/skill-protocol)
- [Anthropic Agent Skills 文档](https://docs.anthropic.com/en/docs/agents-and-tools/agent-skills)
