
# 🤖 AI 上下文阅读协议 (由 nb_ai_context 生成)

> **系统指令**：你正在解析一份由工具 **`nb_ai_context`** 自动生成的**结构化项目快照**。
> **文档性质**：这**不是**一份普通的文档，而是专为 AI 大模型（LLM）设计的上下文数据流。它将项目文档、源代码和 AST 架构元数据进行了特殊的结构化合并。

## 🧠 AI 认知与解析准则

这份由 `nb_ai_context` 生成的文档是你的核心知识库。其中的内容是动态的——它可能包含完整的底层源码，也可能仅包含使用教程，或者是两者的混合。请遵循以下自适应阅读策略：

### 1. 信息的层级与互补
*   **文档即意图**：将 `README`、教程文档和 Docstrings 视为项目设计的**最高意图**。如果文档中详细描述了某个功能的用法，即使生成器没有包含其对应的源码实现，也请完全信任文档中的逻辑，并以此为基础进行回答。
*   **源码即事实**：当遇到 `.py` 源码或 AST 元数据（类/函数签名）时，请以此作为实现细节、类型约束和语法准确性的**事实标准**。
*   **缺失内容的推断**：如果教程演示了调用 `API.process()`，但本文档未包含 `API` 类的源码，**请勿认为该功能不存在**。你应该基于教程中的演示，合理推断该接口的输入输出和行为模式，并据此协助用户。

### 2. 文件边界与架构感知
*   **上下文定界**：`nb_ai_context` 使用以下标记严格界定文件内容：
    `--- **start of file: <路径>** ---` ... 内容 ... `--- **end of file: <路径>** ---`
*   **结构可视化**：请利用“文件树 (File Tree)”章节来建立项目的宏观架构认知，即便某些文件未被展开显示。
*   **依赖关系**：利用工具生成的“文件依赖分析”章节来理解模块间的引用关系，这有助于你在只有部分代码的情况下理清数据流向。

### 3. 代码生成与交互
*   **风格一致性**：在生成代码或解释逻辑时，请严格模仿文档中已有的代码风格和命名规范。
*   **元数据利用**：对于仅展示 AST 元数据（如仅有类定义而无函数体）的 Python 文件，请将其视为有效的接口定义，确保你的代码调用符合这些签名约束。
*   **事实锚定 (Fact Anchoring)**：生成代码时必须严格**锚定**在本文档提供的范围内。
    *   涉及 API 调用时，必须基于**源码中的 AST 签名**或**教程中的演示示例**。
    *   **严禁臆造**文档中既未定义、也未在教程中提及的类名、方法名或参数。确保每一个生成的 Token 都有文档依据。

---
# markdown content namespace: nb_cmd project summary 



- `nb_cmd` is a powerful cron library for Python.
- `NbCron(...)` is the main class to create a cron object. 


## 📋 nb_cmd most core source files metadata (Entry Points)


以下是项目 nb_cmd 最核心的入口文件的结构化元数据，帮助快速理解项目架构：



### the project nb_cmd most core source code files as follows: 
- `nb_cmd/__init__.py`


### 📄 Python File Metadata: `nb_cmd/__init__.py`

#### 📝 Module Docstring

`````
nb_cmd — 万能接口生成器
你写一个 Python class，自动获得 CLI + REST API + Web UI 三种接口。

用法::

    from nb_cmd import NbCmd

    class MyTool(NbCmd):
        def greet(self, name: str, times: int = 1):
            for _ in range(times):
                print(f"你好, {name}!")

    if __name__ == '__main__':
        MyTool().run()
`````

#### 📦 Imports

- `import json`
- `import logging`
- `import sys`
- `from core.arg import Arg`
- `from ui.colors import print_success`
- `from ui.colors import print_warning`
- `from ui.colors import print_error`
- `from ui.colors import print_info`
- `from ui.table import print_table`
- `from ui.table import print_kv`
- `from ui.progress import progress as _progress_iter`
- `from utils.validators import validate`
- `import subprocess`
- `from modes.cli_mode import run_cli`
- `from modes.web_mode import start_web_server`
- `from core.parser import print_full_help`
- `import nb_log`

#### 🏛️ Classes (3)

##### 📌 `class NbCmdMeta(object)`
*Line: 33*

**Docstring:**
`````
NbCmd 的 Meta 配置基类。

子类继承后可覆盖任意字段，IDE 可自动补全所有可用选项。

用法::

    from nb_cmd import NbCmd, NbCmdMeta

    class MyTool(NbCmd):
        class Meta(NbCmdMeta):
            name = "my-tool"
            use_nb_log = True
`````

**Class Variables (14):**
- `name = None`
- `version = '0.0.1'`
- `description = None`
- `use_nb_log = False`
- `log_level = 'INFO'`
- `log_file = None`
- `auto_save_last_args = False`
- `config_file = None`
- `serve_host = '0.0.0.0'`
- `serve_port = 8080`
- `serve_workers = 1`
- `web_title = None`
- `web_theme = 'light'`
- `aliases = {}`

##### 📌 `class UIHelper(object)`
*Line: 64*

**Docstring:**
`````
NbCmd 的 UI 工具方法集合。

通过 ``from nb_cmd import cmdui`` 导入使用，避免与用户自定义的子命令方法名冲突。
包含: 输出(table/kv/tree/json_print)、彩色(success/warning/error/info)、
      交互(confirm/prompt/select)、进度(progress) 等工具。
`````

**Public Methods (12):**
- `def table(self, data, headers = None)`
  - *表格输出*
- `def kv(self, data)`
  - *键值对输出*
- `def tree(self, data, prefix = '', is_last = True)`
  - *树形输出*
- `def json_print(self, data)`
  - *JSON美化输出*
- `def progress(self, iterable, desc = None, total = None)`
  - *进度条迭代器*
- `def confirm(self, message)`
  - *确认提示，返回 True/False*
- `def prompt(self, message, default = None)`
  - *输入提示*
- `def select(self, message, choices)`
  - *选择提示*
- `def success(self, msg)`
  - *绿色成功信息*
- `def warning(self, msg)`
  - *黄色警告信息*
- `def error(self, msg)`
  - *红色错误信息*
- `def info(self, msg)`
  - *蓝色信息*

##### 📌 `class NbCmd(object)`
*Line: 154*

**Docstring:**
`````
NbCmd 基类 —— 所有命令行工具的父类。

用法:
    1. 继承 NbCmd
    2. 定义公有方法（自动成为子命令）
    3. 调用 .run() 启动

功能:
    - 公有方法 → 子命令
    - 方法签名 → 参数自动推导
    - 支持 CLI / REST API / Web UI 三种模式
    - 支持 OOP 继承覆写
    - 支持多层级子命令（sub_commands）

工具方法通过 cmdui 模块级单例访问（from nb_cmd import cmdui）:
    cmdui.table()  cmdui.kv()  cmdui.tree()  cmdui.json_print()
    cmdui.success() cmdui.warning() cmdui.error() cmdui.info()
    cmdui.progress() cmdui.confirm() cmdui.prompt() cmdui.select()
`````

**🔧 Constructor (`__init__`):**
- `def __init__(self)`
  - **Parameters:**
    - `self`

**Public Methods (6):**
- `def before_run(self)`
  - *所有子命令执行前的钩子，子类可覆写*
- `def after_run(self)`
  - *所有子命令执行后的钩子，子类可覆写*
- `def on_error(self, command, error)`
  - *子命令执行出错时的钩子，子类可覆写*
- `def shell(self, cmd, capture = False, check = False)`
  - **Docstring:**
  `````
  执行系统命令。
  
  Parameters
  ----------
  cmd : str  要执行的命令
  capture : bool  是否捕获输出（True 返回 stdout 字符串，False 通过 print 输出）
  check : bool  命令失败时是否抛出异常
  
  Returns
  -------
  str (capture=True 时返回 stdout) 或 None
  `````
- `def exec(self, cmd: str)`
  - *执行任意系统命令*
- `def run(self, args = None)`
  - **Docstring:**
  `````
  主入口方法。根据参数决定运行模式。
  
  Parameters
  ----------
  args : list, optional
      命令行参数列表，默认使用 sys.argv[1:]
  `````

**Properties (1):**
- `@property logger`

**Class Variables (2):**
- `sub_commands = {}`
- `Meta = NbCmdMeta`


---



## 🔗 nb_cmd Some File Dependencies Analysis

以下是项目文件之间的依赖关系，帮助 AI 理解代码结构：

### 📊 Internal Dependencies Graph

`````
Entry Points (not imported by other project files):
  ★ nb_cmd/__init__.py

`````

### 📋 Detailed Dependencies

### 📦 Third-party Dependencies

项目使用的第三方库：

- `nb_log`
- ......以及更多的第三方库......


---
# markdown content namespace: nb_cmd Project Root Dir Some Files 


## nb_cmd File Tree (relative dir: `.`)


`````

├── README.md
├── pyproject.toml
└── setup.py

`````

---


## nb_cmd (relative dir: `.`)  Included Files (total: 3 files)


- `README.md`

- `setup.py`

- `pyproject.toml`


---


--- **start of file: README.md** (project: nb_cmd) --- 

`````markdown
# nb_cmd

**万能接口生成器** —— 你写一个 Python class，自动获得 CLI + REST API + Web UI 三种接口。

[![Python](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

---

## 为什么用 nb_cmd？

现有 CLI 框架（argparse / click / typer / fire）只解决了一件事：**怎么方便地定义 CLI 参数**。

但实际开发中，你一定遇到过：

- 你写了一个 CLI 工具 → 产品说"加个 Web 页面"
- 你写了一个 CLI 工具 → 运维说"要通过 API 远程调用"
- 你写了一个 CLI 工具 → 老板说"能在手机上点个按钮就执行"

**每次都是重写。**

nb_cmd 换了一种思路：**Class 是中心，接口是投影。**

```
             ┌── CLI 模式（默认）
             │
业务逻辑(class) ─┼── REST API 模式（自动 Swagger）
             │
             └── Web UI 模式（自动生成页面）
```

写一次业务逻辑，三种接口自动生成，不改一行代码。

---

## 安装

```bash
# 核心（CLI 模式，零外部依赖）
pip install nb-cmd

# 带 Web UI + REST API 模式（推荐）
pip install nb-cmd[web]

# 全部功能
pip install nb-cmd[all]
```

---

## 5 分钟快速上手

### 第一步：写一个 class

```python
# my_tool.py
from nb_cmd import NbCmd, cmdui

class MyTool(NbCmd):
    """我的超级工具"""

    def greet(self, name: str, times: int = 1):
        """向某人问好"""
        for _ in range(times):
            print('你好, {}!'.format(name))

    def deploy(self, host: str, port: int = 22, verbose: bool = False):
        """部署到远程服务器"""
        if verbose:
            cmdui.info('正在部署到 {}:{} ...'.format(host, port))
        print('部署到 {}:{} 完成'.format(host, port))
        cmdui.success('部署成功!')

if __name__ == '__main__':
    MyTool().run()
```

> **注意：** nb_cmd 强制要求所有公有方法的参数必须声明类型注解（如 `name: str`），启动时自动校验，缺少注解直接报错。

### 第二步：当 CLI 用

```bash
$ python my_tool.py --help
我的超级工具

system params:
  -h, --help           显示帮助信息
  --version            show program's version number and exit
  --full-help, -fh     显示所有命令的完整参数详情
  --web                以Web UI + REST API模式启动
  --web-port WEB_PORT  Web UI 服务端口（用于 --web）

commands:
  {deploy,exec,greet}  可用命令
    deploy             部署到远程服务器 (HOST, --port=22, --verbose)
    exec               执行任意系统命令 (CMD)
    greet              向某人问好 (NAME, --times=1)

# 执行子命令
$ python my_tool.py greet 张三 --times 3
你好, 张三!
你好, 张三!
你好, 张三!

# 查看子命令的详细帮助
$ python my_tool.py deploy --help

# 执行带参数的命令
$ python my_tool.py deploy web-01 --port 2222 --verbose
[INFO] 正在部署到 web-01:2222 ...
部署到 web-01:2222 完成
[OK] 部署成功!
```

### 第三步：切换为 Web UI + REST API

```bash
$ python my_tool.py --web --web-port 8080
Web UI启动在 http://0.0.0.0:8080
API文档: http://0.0.0.0:8080/docs
```

打开浏览器：

- `http://localhost:8080` → **Web UI**：左侧是命令输入 + 参数表单，右侧是实时控制台输出 + 命令历史，中间分割条可自由拖动
- `http://localhost:8080/docs` → **Swagger 文档**：所有命令自动生成 REST API

用 curl 或 requests 调用（和 Web UI 共用同一套接口）：

```bash
$ curl -X POST http://localhost:8080/greet \
    -H "Content-Type: application/json" \
    -d '{"name": "张三", "times": 3}'
```

响应：

```json
{
  "status": "success",
  "result": null,
  "stdout": "你好, 张三!\n你好, 张三!\n你好, 张三!\n",
  "duration_ms": 1
}
```

**不改一行业务代码，CLI 和 Web + API 自由切换。**

---

## 核心特性

### 1. 自动推导规则

nb_cmd 通过 Python 方法签名自动生成 CLI 参数，零配置：

| Python 方法签名元素 | CLI 映射 | 示例 |
|---|---|---|
| 公有方法名 | 子命令名（`snake_case` → `kebab-case`） | `def show_users` → `show-users` |
| 方法的 docstring | 子命令帮助文本 | `"""查看用户"""` → `--help` 里的描述 |
| 无默认值的参数 | 位置参数（必填）；有 `alias` 时为 `--flag`（必填） | `name: str` → `greet 张三`；`name: Arg(str, alias='n')` → `-n 张三` |
| 有默认值的参数 | 可选参数（`--xxx`） | `port: int = 22` → `--port 2222` |
| `bool` 类型 | 开关参数（`--flag`） | `verbose: bool = False` → `--verbose` |
| `int` / `float` 类型 | 自动类型转换和校验 | 输入非数字会报错 |
| `Enum` 类型 | 自动生成选择项 | `env: Environment` → `{dev,staging,prod}` |
| `Arg(type, desc, alias)` | 参数描述 + 短别名 | `name: Arg(str, '用户名', alias='n')` → `-n` |
| `_` 开头的方法 | 不暴露为子命令 | `_helper()` → 内部方法 |

### 2. OOP 继承覆写

nb_cmd 基于类继承，天然支持模板方法模式：

```python
class BaseDeploy(NbCmd):
    """基础部署"""
    def deploy(self, host: str, version: str = "latest"):
        self._pre_deploy(host)
        self._do_deploy(host, version)
        self._post_deploy(host)
        cmdui.success('部署完成!')

    def _pre_deploy(self, host):
        cmdui.info('检查 {} 连接...'.format(host))

    def _do_deploy(self, host, version):
        cmdui.info('上传文件并重启服务')

    def _post_deploy(self, host):
        cmdui.info('验证服务状态')

class DockerDeploy(BaseDeploy):
    """Docker 部署——只需覆写一个方法"""
    def _do_deploy(self, host, version):
        cmdui.info('docker pull app:{}'.format(version))
        cmdui.info('docker-compose up -d')

class K8sDeploy(BaseDeploy):
    """K8s 部署——覆写 + 新增命令"""
    def _do_deploy(self, host, version):
        cmdui.info('kubectl set image app=app:{}'.format(version))

    def scale(self, replicas: int = 3):
        """扩缩容（K8s 特有命令）"""
        cmdui.info('kubectl scale --replicas={}'.format(replicas))
        cmdui.success('已扩缩至 {} 个副本'.format(replicas))
```

```bash
# 基础部署
$ python deploy.py deploy web-01

# Docker 部署——同样的命令，不同的实现
$ python docker_deploy.py deploy web-01

# K8s 多了一个 scale 命令
$ python k8s_deploy.py scale --replicas 5
```

其他框架做不到这一点：click/typer 用装饰器绑定函数，无法继承覆写；fire 虽然也基于类，但不支持多层级子命令和 Web/API 投影。

### 3. 多层级子命令

通过 `sub_commands` 定义子命令组，支持 `git remote add` 这样的多级命令：

```python
class GitRemote(NbCmd):
    """远程仓库管理"""
    def add(self, name: str, url: str):
        """添加远程仓库"""
        print('git remote add {} {}'.format(name, url))

    def remove(self, name: str):
        """删除远程仓库"""
        print('git remote remove {}'.format(name))

class GitTool(NbCmd):
    """Git 工具"""
    sub_commands = {'remote': GitRemote}

    def status(self):
        """查看状态"""
        print('当前分支: main')

    def commit(self, message: str, all: bool = False):
        """提交"""
        if all:
            print('git add -A')
        print("git commit -m '{}'".format(message))
```

```bash
$ python git_tool.py status                           # 一级命令
$ python git_tool.py remote add origin https://...    # 二级命令
$ python git_tool.py commit "fix bug" --all           # 一级命令
```

在 Web UI 中，子命令组以蓝色标题 `[组]` 展示，展开后列出每个子命令的参数表单。

### 4. 内置输出工具（通过 cmdui 访问）

所有 UI/交互方法统一通过 `from nb_cmd import cmdui` 导入使用，**独立函数和类方法中均可调用**：

```python
from nb_cmd import NbCmd, cmdui

class DbTool(NbCmd):
    def query(self, sql: str):
        """执行 SQL 查询"""
        result = [
            {"id": 1, "name": "张三", "age": 25},
            {"id": 2, "name": "李四", "age": 30},
        ]
        cmdui.table(result)

    def stats(self):
        """数据库统计"""
        cmdui.kv({
            "数据库": "SQLite",
            "大小": "15.3 MB",
            "表数量": "12",
        })

    def schema(self):
        """数据库结构"""
        cmdui.tree({
            "数据库": {
                "users": {"id": "INT PK", "name": "VARCHAR"},
                "orders": {"id": "INT PK", "total": "DECIMAL"},
            }
        })

    def migrate(self, version: str = "latest"):
        """数据库迁移"""
        import time
        steps = ["检查版本", "备份数据", "执行迁移", "验证结果"]
        for step in cmdui.progress(steps, desc="迁移进度"):
            time.sleep(0.5)
        cmdui.success("迁移完成!")
```

输出效果：

```
# cmdui.table()
┌────┬──────┬─────┐
│ id │ name │ age │
├────┼──────┼─────┤
│ 1  │ 张三 │ 25  │
│ 2  │ 李四 │ 30  │
└────┴──────┴─────┘

# cmdui.kv()
数据库:  SQLite
大小  :  15.3 MB
表数量:  12

# cmdui.tree()
├── 数据库
│   ├── users
│   │   ├── id: INT PK
│   │   └── name: VARCHAR
│   └── orders
│       ├── id: INT PK
│       └── total: DECIMAL

# cmdui.progress()
迁移进度 ████████████████████████ 100% 4/4 [00:02<00:00]
[OK] 迁移完成!
```

### 5. Arg 参数描述器

用 `Arg` 为参数添加描述和短别名，CLI `--help`、Web UI 输入框、Swagger 文档会同步显示：

```python
from nb_cmd import NbCmd, Arg

class MyTool(NbCmd):
    """部署工具"""

    def deploy(self, host: Arg(str, '服务器地址', alias='H'),
               port: Arg(int, '端口号', alias='p') = 22,
               verbose: Arg(bool, '详细模式', alias='v') = False):
        """部署到远程服务器"""
        ...
```

```bash
$ python my_tool.py deploy --help
optional arguments:
  --host HOST, -H HOST  服务器地址 (str, 必填)
  --port PORT, -p PORT  端口号 (int, 默认: 22)
  --verbose, -v         详细模式 (bool, 默认: False)

$ python my_tool.py deploy -H 10.0.0.1 -p 2222 -v
```

`Arg` 的三个参数都是渐进式的——`desc` 和 `alias` 可选，不影响原有的 `name: str` 写法：

```python
name: str                              # 最简写法，完全兼容
name: Arg(str, '用户名')               # 加描述
name: Arg(str, '用户名', alias='n')    # 加描述 + 短别名
name: Arg(str, alias='n')              # 只加短别名
```

> Web UI 中，`Arg` 的 `desc` 会显示在输入框旁边的灰色提示文字和 placeholder 中。

### 6. 全局参数（`__init__` 参数）

当多个子命令需要共享上下文（如机房区域、数据库连接、超时时间），把它们放到 `__init__` 中：

```python
from nb_cmd import NbCmd, Arg, NbCmdMeta, cmdui
from enum import Enum

class Environment(Enum):
    DEV = "dev"
    STAGING = "staging"
    PROD = "prod"

class ServerTool(NbCmd):
    """服务器运维工具"""

    class Meta(NbCmdMeta):
        version = "1.0.0"
        use_nb_log = True

    def __init__(self, region: Arg(str, '机房区域', alias='r'),
                 timeout: Arg(int, '超时秒数') = 30):
        super().__init__()
        self.region = region
        self.timeout = timeout

    def deploy(self, host: str, env: Environment = Environment.DEV):
        """部署服务到目标主机"""
        cmdui.info('部署到 {} (区域: {}, 环境: {})'.format(host, self.region, env.value))
        cmdui.success('部署完成!')

    def stats(self):
        """查看系统状态"""
        cmdui.kv({"区域": self.region, "超时": "{}s".format(self.timeout)})

if __name__ == '__main__':
    ServerTool('beijing').run()
```

> **`region` 是必填参数**（无默认值），`timeout` 是选填参数（默认 30）。`ServerTool('beijing')` 中的 `'beijing'` 作为 `region` 的预设值，CLI / Web UI 均会以此作为默认值。

#### CLI 用法

`__init__` 参数在 CLI 中变为全局选项，放在子命令之前：

```bash
# --help 中会显示 init params 分区
$ python server_tool.py --help
system params:
  -h, --help           显示帮助信息
  --version            show program's version number and exit
  --full-help, -fh     显示所有命令的完整参数详情

init params:
  --region REGION, -r REGION  机房区域 (默认: beijing)
  --timeout TIMEOUT           超时秒数 (默认: 30)

commands:
  {deploy,exec,stats}  可用命令

# 使用预设值
$ python server_tool.py deploy 10.0.0.1

# 覆盖 region
$ python server_tool.py --region shanghai deploy 10.0.0.1 --env prod

# 用短别名
$ python server_tool.py -r shanghai --timeout 60 stats
```

#### Web UI 用法

```bash
$ python server_tool.py --web --web-port 8080
```

Web UI 顶部会自动生成全局参数表单，必填参数带 `*` 标记。修改后执行任意命令，自动携带。

#### curl / REST API 用法

启动 Web 模式后，REST API 端点自动注册：

```bash
# 查看有哪些全局参数及当前预设值
$ curl http://localhost:8080/api/init-params

# 不传 init_params → 使用预设值 region='beijing', timeout=30
$ curl -X POST http://localhost:8080/deploy \
    -H "Content-Type: application/json" \
    -d '{"host": "10.0.0.1", "env": "prod"}'

# 通过 init_params 覆盖全局参数
$ curl -X POST http://localhost:8080/deploy \
    -H "Content-Type: application/json" \
    -d '{
      "host": "10.0.0.1",
      "env": "prod",
      "init_params": {"region": "shanghai", "timeout": 60}
    }'

# 只覆盖部分参数，其余用预设值
$ curl -X POST http://localhost:8080/stats \
    -H "Content-Type: application/json" \
    -d '{"init_params": {"region": "guangzhou"}}'
```

响应示例：

```json
{
  "status": "success",
  "result": null,
  "stdout": "[INFO] 部署到 10.0.0.1 (区域: shanghai, 环境: prod)\n[OK] 部署完成!\n",
  "duration_ms": 5
}
```

> `init_params` 是可选字段，不传时使用 `ServerTool('beijing').run()` 中的预设值。Swagger 文档（`/docs`）中每个接口也会显示该字段。

> **多用户隔离：** Web 模式下，每次命令执行都会创建一个新的 `ServerTool` 实例，不同用户/请求之间互不影响。Web UI / curl 中传入的全局参数只影响当前这次执行。

### 7. 参数校验

```python
from nb_cmd import NbCmd, validate

class MyTool(NbCmd):
    @validate(port=lambda x: 1 <= x <= 65535)
    def deploy(self, host: str, port: int = 22):
        """部署"""
        print('部署到 {}:{}'.format(host, port))
```

```bash
$ python my_tool.py deploy web-01 --port 99999
# 自动报错: port 校验失败
```

### 8. 内置系统命令执行

所有 NbCmd 子类自动拥有 `exec` 子命令和 `self.shell()` 工具方法：

```bash
# exec 子命令——直接在 CLI/Web UI 中执行任意系统命令
$ python my_tool.py exec "docker ps"
$ python my_tool.py exec "ls -la"
```

```python
class MyTool(NbCmd):
    def deploy(self, host: str):
        """部署"""
        self.shell('scp app.tar.gz {}:/opt/'.format(host))
        self.shell('ssh {} "cd /opt && tar xzf app.tar.gz"'.format(host))
        cmdui.success('部署完成!')

    def version(self):
        """查看远程版本"""
        ver = self.shell('python --version', capture=True)
        print('Python: {}'.format(ver))
```

### 9. Meta 配置

通过内部类 `Meta` 自定义工具的行为。继承 `NbCmdMeta` 可获得 IDE 自动补全：

```python
from nb_cmd import NbCmd, NbCmdMeta

class MyTool(NbCmd):
    class Meta(NbCmdMeta):
        name = "mytool"
        version = "1.0.0"
        description = "我的超级工具"
        use_nb_log = True
        log_level = "DEBUG"
        web_theme = "dark"
        serve_port = 9000
```

> 也可以写 `class Meta(NbCmd.Meta):`，效果一样。不继承也行（向后兼容），但无法 IDE 补全。

**Meta 完整字段一览：**

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `name` | str | `None` | CLI/API 名称（默认用类名） |
| `version` | str | `'0.0.1'` | 版本号（`--version` 显示） |
| `description` | str | `None` | 描述（默认用类的 docstring） |
| `use_nb_log` | bool | `False` | 启用 [nb_log](https://github.com/ydf0509/nb_log) 增强日志 |
| `log_level` | str | `'INFO'` | 日志级别 |
| `log_file` | str | `None` | 日志文件路径 |
| `auto_save_last_args` | bool | `False` | 自动保存上次参数（规划中） |
| `config_file` | str | `None` | 配置持久化文件路径（规划中） |
| `serve_host` | str | `'0.0.0.0'` | Web/API 绑定地址 |
| `serve_port` | int | `8080` | Web/API 默认端口 |
| `serve_workers` | int | `1` | 工作进程数（规划中） |
| `web_title` | str | `None` | Web UI 页面标题 |
| `web_theme` | str | `'light'` | Web UI 主题（`'light'` / `'dark'`） |
| `aliases` | dict | `{}` | 参数别名（推荐用 `Arg(alias=...)` 替代） |

### 10. 生命周期钩子

```python
class MyTool(NbCmd):
    def before_run(self):
        """所有子命令执行前"""
        self.logger.info("工具启动")

    def after_run(self):
        """所有子命令执行后"""
        self.logger.info("操作完成")

    def on_error(self, command, error):
        """出错时"""
        self.logger.error("命令 {} 失败: {}".format(command, error))
```

### 11. 帮助系统

nb_cmd 提供三级帮助：

```bash
# 一级：总览（所有命令 + 简要参数提示）
$ python server_tool.py --help

# 二级：单个子命令的详细帮助
$ python server_tool.py deploy --help
usage: server_tool.py deploy [-h] [--env {dev,staging,prod}] HOST

部署服务到目标主机

positional arguments:
  HOST                     (str, 必填)

optional arguments:
  --env {dev,staging,prod}  (str, 默认: dev)

# 三级：所有命令的完整参数详情（对应前文第 6 节的 ServerTool 示例）
$ python server_tool.py --full-help   # 或 -fh
========================================================
  ServerTool v1.0.0
  服务器运维工具
========================================================

system params:
    --help, -h               显示简要帮助
    --full-help, -fh         显示本完整帮助
    --version                显示版本号
    --web                    以Web UI + REST API模式启动
    --web-port PORT          Web UI 服务端口

init params:
    --region, -r             机房区域  (全局, str, 默认: beijing)
    --timeout                超时秒数  (全局, int, 默认: 30)

--------------------------------------------------------
deploy — 部署服务到目标主机
    HOST                     (str, 必填)
    --env                    (Environment, 默认: Environment.DEV)

stats — 查看系统状态
```

---

## 完整 API 速查

### 导入

```python
from nb_cmd import NbCmd, Arg, NbCmdMeta, cmdui, validate
```

### cmdui（UI / 交互工具）

`from nb_cmd import cmdui` —— 模块级单例，类方法和独立函数中均可使用：

| 方法 | 说明 |
|------|------|
| `cmdui.table(data, headers)` | 表格输出（list[dict]） |
| `cmdui.kv(data)` | 键值对输出（dict） |
| `cmdui.tree(data)` | 树形输出（嵌套 dict） |
| `cmdui.json_print(data)` | JSON 美化输出 |
| `cmdui.progress(iter, desc, total)` | 进度条迭代器 |
| `cmdui.confirm(msg)` | 确认提示 `[y/N]` → bool |
| `cmdui.prompt(msg, default)` | 输入提示 → str |
| `cmdui.select(msg, choices)` | 选择提示 → str |
| `cmdui.success(msg)` / `warning` / `error` / `info` | 彩色状态输出 |

### self 直属方法 / 属性

| 方法 / 属性 | 说明 |
|------|------|
| `self.shell(cmd, capture, check)` | 执行系统命令。`capture=True` 返回 stdout 字符串 |
| `self.logger` | 日志器（`use_nb_log=True` 时为 nb_log 增强版） |
| `self.before_run()` / `after_run()` | 钩子：子命令执行前后调用 |
| `self.on_error(command, error)` | 钩子：子命令出错时调用 |
| `exec <cmd>` (内置子命令) | 执行任意系统命令（CLI 和 Web UI 均可用） |

### Arg 描述器

| 参数 | 必填 | 说明 |
|------|------|------|
| `type_` | 是 | 参数类型（`str`, `int`, `bool`, `Enum`, `List[str]` 等） |
| `desc` | 否 | 参数描述（`--help`、Web UI placeholder、Swagger 同步显示） |
| `alias` | 否 | 短别名（`'n'` → `-n`，`'host-name'` → `--host-name`） |

---

## 从零到完整：渐进式示例

展示如何从最简单的 class 逐步添加功能，每一步都是独立可运行的。

### Level 1：最简 — 3 行代码

```python
from nb_cmd import NbCmd

class Hi(NbCmd):
    def say(self, name: str):
        """打招呼"""
        print('Hello, {}!'.format(name))

if __name__ == '__main__':
    Hi().run()
```

```bash
$ python hi.py say 张三          # CLI
$ python hi.py --web             # 一键变 Web UI + REST API
```

### Level 2：加 Arg 描述 + 短别名

```python
from nb_cmd import NbCmd, Arg, cmdui

class Hi(NbCmd):
    def say(self, name: Arg(str, '要问候的人', alias='n'),
            times: Arg(int, '次数', alias='t') = 1):
        """打招呼"""
        for _ in range(times):
            print('Hello, {}!'.format(name))
        cmdui.success('完成!')

if __name__ == '__main__':
    Hi().run()
```

```bash
$ python hi.py say -n 张三 -t 3
```

### Level 3：加全局参数 + Meta 配置

```python
from nb_cmd import NbCmd, Arg, NbCmdMeta, cmdui

class ServerTool(NbCmd):
    """服务器运维工具"""

    class Meta(NbCmdMeta):
        version = "2.0.0"
        use_nb_log = True
        web_theme = "dark"

    def __init__(self, region: Arg(str, '机房区域', alias='r') = 'cn-east',
                 timeout: Arg(int, '超时秒数') = 30):
        super().__init__()
        self.region = region
        self.timeout = timeout

    def deploy(self, host: str, port: int = 22):
        """部署到远程服务器"""
        self.shell('echo "部署到 {} (区域: {})"'.format(host, self.region))
        cmdui.success('部署完成!')

    def stats(self):
        """查看状态"""
        cmdui.kv({"区域": self.region, "超时": "{}s".format(self.timeout)})

if __name__ == '__main__':
    ServerTool().run()
```

```bash
$ python server_tool.py --region shanghai deploy 10.0.0.1
$ python server_tool.py --web --web-port 9000
$ curl -X POST http://localhost:9000/stats \
    -H "Content-Type: application/json" \
    -d '{"init_params": {"region": "guangzhou"}}'
```

### Level 4：加继承 + 子命令组

```python
from nb_cmd import NbCmd, cmdui

class BaseDeploy(NbCmd):
    def deploy(self, host: str):
        self._do_deploy(host)
        cmdui.success('部署完成!')

    def _do_deploy(self, host):
        cmdui.info('基础部署到 {}'.format(host))

class DockerDeploy(BaseDeploy):
    """Docker 部署——只覆写一个方法"""
    def _do_deploy(self, host):
        cmdui.info('docker pull && docker-compose up -d on {}'.format(host))

class K8sDeploy(BaseDeploy):
    """K8s 部署——覆写 + 新增命令"""
    def _do_deploy(self, host):
        cmdui.info('kubectl apply on {}'.format(host))

    def scale(self, replicas: int = 3):
        """扩缩容"""
        cmdui.info('kubectl scale --replicas={}'.format(replicas))
```

---

## 和竞品对比

### 功能矩阵

| 功能 | argparse | click | typer | fire | **nb_cmd** |
|------|:--------:|:-----:|:-----:|:----:|:----------:|
| 零配置 | ✗ | ✗ | 部分 | ✓ | **✓** |
| 类型驱动 | 手动 | 手动 | ✓ | ✗ | **✓** |
| OOP 继承/覆写 | ✗ | ✗ | ✗ | 有限 | **✓** |
| 自动生成 REST API | ✗ | ✗ | ✗ | ✗ | **✓** |
| 自动生成 Web UI | ✗ | ✗ | ✗ | ✗ | **✓** |
| 多层级子命令 | 手动 | ✓ | ✓ | 有限 | **✓** |
| 进度条/表格/彩色 | ✗ | ✓ | ✓(rich) | ✗ | **✓** |
| 生命周期钩子 | ✗ | 有限 | ✗ | ✗ | **✓** |
| Swagger 文档 | ✗ | ✗ | ✗ | ✗ | **✓** |
| 系统命令执行 | ✗ | ✗ | ✗ | ✗ | **✓** |

### 代码对比：实现同一个工具

**argparse（30+ 行样板代码）：**

```python
import argparse

parser = argparse.ArgumentParser(description='部署工具')
subparsers = parser.add_subparsers(dest='command')

deploy_parser = subparsers.add_parser('deploy', help='部署服务')
deploy_parser.add_argument('host', type=str, help='目标主机')
deploy_parser.add_argument('--port', type=int, default=22, help='端口')
deploy_parser.add_argument('--verbose', action='store_true', help='详细输出')

status_parser = subparsers.add_parser('status', help='查看状态')

args = parser.parse_args()
if args.command == 'deploy':
    deploy(args.host, args.port, args.verbose)
elif args.command == 'status':
    status()
# 还需要手动实现 API 和 Web UI...
```

**click（装饰器地狱）：**

```python
import click

@click.group()
def cli():
    """部署工具"""
    pass

@cli.command()
@click.argument('host')
@click.option('--port', default=22, type=int, help='端口')
@click.option('--verbose', is_flag=True, help='详细输出')
def deploy(host, port, verbose):
    """部署服务"""
    ...

@cli.command()
def status():
    """查看状态"""
    ...
# 想加 API？对不起，请重写一遍...
```

**nb_cmd（写一次，三种接口）：**

```python
from nb_cmd import NbCmd

class DeployTool(NbCmd):
    """部署工具"""

    def deploy(self, host: str, port: int = 22, verbose: bool = False):
        """部署服务"""
        ...

    def status(self):
        """查看状态"""
        ...

if __name__ == '__main__':
    DeployTool().run()
```

```bash
python deploy.py deploy web-01            # CLI
python deploy.py --web --web-port 8080     # Web UI + REST API
```

**核心差异：** argparse / click / typer 的世界观是"CLI 是终点"。nb_cmd 的世界观是"Class 是中心，接口是投影"——CLI、API、Web UI 只是同一份业务逻辑的不同表现形式。

---

## nb_cmd vs 传统前后端开发

传统方式：**写后端 → 写接口 → 写文档 → 写前端 → 联调**，5 步缺一不可。

### 传统方式：以实现一个"部署工具"为例

**第 1 步：手写 API 接口（每个功能一个路由）**

```python
from fastapi import FastAPI
app = FastAPI()

@app.post("/api/deploy")
async def deploy(host: str, port: int = 22, env: str = "dev"):
    ...

@app.post("/api/status")
async def status():
    ...

# 10 个功能 = 10 个路由 + 10 个 Pydantic 模型
```

**第 2 步：手写前端表单（每个接口一套 HTML/JS）**

```html
<form id="deployForm">
  <input name="host" required />
  <input name="port" type="number" value="22" />
  <select name="env">
    <option value="dev">dev</option>
    <option value="prod">prod</option>
  </select>
  <button>部署</button>
</form>
<script>
  // 每个表单都要写 fetch + 结果展示 + 错误处理...
</script>
```

**第 3 步：前后端联调**——参数名对不上？类型转换出错？文档过时？

### nb_cmd 方式：只写 class

```python
class DeployTool(NbCmd):
    def deploy(self, host: str, port: int = 22, env: Environment = Environment.DEV):
        ...
    def status(self):
        ...
```

**然后你自动获得：**

| 能力 | 传统方式 | nb_cmd |
|------|---------|--------|
| REST API（含 Swagger） | 手写路由 + 模型 | **方法签名自动生成** |
| Web UI（表单 + 控件） | 手写 HTML/CSS/JS | **类型注解自动推导控件** |
| WebSocket 实时输出 | 手写 WS 端点 + 前端接收 | **print() 自动流式推送** |
| ANSI 颜色渲染 | 不支持 | **自动转 HTML 彩色** |
| 命令行 CLI | 另写 argparse | **同一份代码** |
| 文档同步 | 手动维护 | **永远一致（同一个类）** |
| 新增参数 | 改后端 + 改前端 + 改文档 | **加一个参数，三处自动更新** |

### 工作量对比

| | 传统前后端 | nb_cmd |
|---|-----------|--------|
| 10 个功能的工具 | **20-30 小时** | **加几行类型注解** |
| 新增 1 个参数 | 改 3 处（后端/前端/文档） | **改 1 处（方法签名）** |
| 前端开发者 | 需要 | **不需要** |

> **本质区别：** 传统开发是"手动映射"——后端定义接口，前端照着文档手写表单；nb_cmd 是"自动投影"——Python 类是唯一真相源，CLI/API/Web UI 是它的三个不同维度的影子。改真相源，影子自动跟着变。

---

## 项目结构

```
nb_cmd/
├── __init__.py          # NbCmd 基类 + UIHelper
├── core/
│   ├── arg.py           # Arg 参数描述器
│   ├── discovery.py     # 命令发现（反射 + 类型检查）
│   ├── parser.py        # argparse 解析器构建
│   ├── type_utils.py    # 类型工具（Enum/Optional/List 等）
│   └── result_handler.py # 返回值自动处理
├── modes/
│   ├── cli_mode.py      # CLI 执行引擎
│   ├── api_mode.py      # REST API 路由生成（FastAPI）
│   └── web_mode.py      # Web UI 页面生成 + API
├── ui/
│   ├── colors.py        # ANSI 彩色输出
│   ├── table.py         # 表格 / 键值对输出
│   └── progress.py      # 进度条
└── utils/
    ├── validators.py    # @validate 装饰器
    └── config.py        # 配置持久化
```

---

## 依赖

| 模式 | 额外依赖 | 说明 |
|------|----------|------|
| CLI 模式 | **无** | 纯标准库，开箱即用 |
| Web UI + REST API | fastapi + uvicorn | `pip install nb-cmd[web]` |
| nb_log 增强日志 | nb_log | 可选，`pip install nb_log` |

---

## License

MIT

`````

--- **end of file: README.md** (project: nb_cmd) --- 

---


--- **start of file: setup.py** (project: nb_cmd) --- 

`````python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='nb-cmd',
    version='0.1.0',
    description='万能接口生成器——你写一个 Python class，自动获得 CLI + REST API + Web UI 三种接口',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='ydf',
    author_email='ydf0509@sohu.com',
    url='https://github.com/ydf0509/nb_cmd',
    license='MIT',
    packages=find_packages(),
    package_data={'nb_cmd': ['ui/static/**/*']},
    python_requires='>=3.7',
    install_requires=[],
    extras_require={
        'api': ['fastapi>=0.68.0', 'uvicorn>=0.15.0', 'pydantic>=1.8.0'],
        'web': ['fastapi>=0.68.0', 'uvicorn>=0.15.0', 'websockets>=10.0'],
        'all': ['fastapi>=0.68.0', 'uvicorn>=0.15.0', 'pydantic>=1.8.0', 'websockets>=10.0'],
        'nb': ['nb_log'],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
)

`````

--- **end of file: setup.py** (project: nb_cmd) --- 

---


--- **start of file: pyproject.toml** (project: nb_cmd) --- 

`````text
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "nb-cmd"
version = "0.1.0"
description = "万能接口生成器——你写一个 Python class，自动获得 CLI + REST API + Web UI 三种接口"
readme = "README.md"
license = {text = "MIT"}
requires-python = ">=3.7"
authors = [
    {name = "ydf", email = "ydf0509@sohu.com"},
]
keywords = ["cli", "api", "webui", "command", "argparse", "fastapi"]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: Utilities",
]

[project.optional-dependencies]
api = ["fastapi>=0.68.0", "uvicorn>=0.15.0", "pydantic>=1.8.0"]
web = ["fastapi>=0.68.0", "uvicorn>=0.15.0", "websockets>=10.0"]
all = ["fastapi>=0.68.0", "uvicorn>=0.15.0", "pydantic>=1.8.0", "websockets>=10.0"]
nb = ["nb_log"]

[project.urls]
Homepage = "https://github.com/ydf0509/nb_cmd"

[tool.setuptools.packages.find]
include = ["nb_cmd*"]

[tool.setuptools.package-data]
nb_cmd = ["ui/static/**/*"]

`````

--- **end of file: pyproject.toml** (project: nb_cmd) --- 

---

# markdown content namespace: nb_cmd examples 


## nb_cmd File Tree (relative dir: `examples`)


`````

└── examples
    ├── demo_advanced.py
    ├── demo_basic.py
    ├── demo_full.py
    ├── demo_inherit.py
    ├── demo_nb_log.py
    └── demo_subcommands.py

`````

---


## nb_cmd (relative dir: `examples`)  Included Files (total: 6 files)


- `examples/demo_advanced.py`

- `examples/demo_basic.py`

- `examples/demo_full.py`

- `examples/demo_inherit.py`

- `examples/demo_nb_log.py`

- `examples/demo_subcommands.py`


---


--- **start of file: examples/demo_advanced.py** (project: nb_cmd) --- 

`````python
# -*- coding: utf-8 -*-
"""
nb_cmd 高级用法 demo —— 继承覆写 + 子命令组 + 高级类型
"""
import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from nb_cmd import NbCmd, Arg, NbCmdMeta, cmdui
from enum import Enum


class Environment(Enum):
    DEV = "dev"
    STAGING = "staging"
    PROD = "prod"


class DeployTool(NbCmd):
    """部署工具"""

    class Meta(NbCmdMeta):
        use_nb_log = True
        log_level = "DEBUG"
        log_file = "deploy_tool.log"
        web_theme = "dark"
        serve_port = 8082
        serve_workers = 1
        web_title = "部署工具"

    def deploy(self,
               host: Arg(str, '目标服务器地址', alias='H'),
               port: Arg(int, '端口号', alias='p') = 22,
               env: Arg(Environment, '部署环境', alias='e') = Environment.DEV,
               dry_run: Arg(bool, '试运行模式') = False,
               ):
        """执行部署到指定服务器"""
        print('环境: {}'.format(env.value if hasattr(env, 'value') else env))
        print('目标: {}:{}'.format(host, port))
        if dry_run:
            print('** 试运行模式，不会实际执行 **')
        else:
            print('部署完成!')

    def status(self):
        """查看部署状态"""
        cmdui.kv({
            "当前环境": "dev",
            "最后部署": "2026-04-17 10:30",
            "服务状态": "运行中",
        })

    def show_users(self):
        """展示用户列表"""
        data = [
            {"名字": "张三", "年龄": 25, "城市": "北京"},
            {"名字": "李四", "年龄": 30, "城市": "上海"},
            {"名字": "王五", "年龄": 28, "城市": "广州"},
        ]
        cmdui.table(data)

    def process(self):
        """模拟处理任务（带进度条）"""
        
        items = list(range(20))
        for _ in cmdui.progress(items, desc="处理中"):
            time.sleep(0.1)
        cmdui.success("处理完成!")
    
    def many_print(self):
        """持续打印多行（用于测试 WebSocket 实时流式输出）"""
        for i in range(10):
            time.sleep(1)
            print(f'print {i}')
            self.logger.debug(f'logger debug {i}')
            self.logger.info(f'logger info {i}')
            self.logger.warning(f'logger warning {i}')
            self.logger.error(f'logger error {i}')
            self.logger.critical(f'logger critical {i}')

            cmdui.info(f'ui info {i}')
            cmdui.success(f'ui success {i}')
            cmdui.error(f'ui error {i}')
            cmdui.warning(f'ui warning {i}')



if __name__ == '__main__':
    DeployTool().run()


    '''
    D:/ProgramData/Miniconda3/envs/py39b/python.exe examples/demo_advanced.py --web --web-port 8082
    
    '''

`````

--- **end of file: examples/demo_advanced.py** (project: nb_cmd) --- 

---


--- **start of file: examples/demo_basic.py** (project: nb_cmd) --- 

`````python
# -*- coding: utf-8 -*-
"""
nb_cmd 基础用法 demo —— 对应设计文档 4.1 最简示例

用法:
    python demo_basic.py --help
    python demo_basic.py greet 张三 --times 3
    python demo_basic.py greet -n 张三 -t 3
    python demo_basic.py deploy 192.168.1.1 --port 2222 --verbose
    python demo_basic.py deploy --help
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from nb_cmd import NbCmd, Arg


class MyTool(NbCmd):
    """我的超级工具（自动变成CLI的description）"""

    def greet(self, name: Arg(str, '要问候的人名', alias='n'),
              times: Arg(int, '问候次数', alias='t') = 1):
        """向某人问好（自动变成子命令的帮助信息）"""
        for _ in range(times):
            print('你好, {}!'.format(name))

    def deploy(self, host: Arg(str, '服务器地址', alias='H'),
               port: Arg(int, '端口号', alias='p') = 22,
               verbose: Arg(bool, '详细模式', alias='v') = False):
        """部署到远程服务器"""
        if verbose:
            print('[详细模式] 正在部署到 {}:{} ...'.format(host, port))
        print('部署到 {}:{} 完成'.format(host, port))

    def _private_helper(self):
        """下划线开头的方法不会暴露为子命令"""
        pass


if __name__ == '__main__':
    MyTool().run()

    '''
    D:/ProgramData/Miniconda3/envs/py39b/python.exe examples/demo_basic.py --web --web-port 8081
    
    '''

`````

--- **end of file: examples/demo_basic.py** (project: nb_cmd) --- 

---


--- **start of file: examples/demo_full.py** (project: nb_cmd) --- 

`````python
# -*- coding: utf-8 -*-
"""
nb_cmd 完整功能 demo —— 对应设计文档附录A (数据库管理工具)

用法:
    python demo_full.py --help
    python demo_full.py query "SELECT * FROM users"
    python demo_full.py query "SELECT * FROM users" --output json
    python demo_full.py stats
    python demo_full.py migrate --version v2.0 --dry-run

    # REST API 模式
    # Web UI 模式
    python demo_full.py --web --web-port 9904
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from nb_cmd import NbCmd, Arg, NbCmdMeta, cmdui
from enum import Enum


class OutputFormat(Enum):
    TABLE = "table"
    JSON = "json"
    CSV = "csv"


class DbTool(NbCmd):
    """数据库管理工具 - 支持多种数据库的通用管理"""

    class Meta(NbCmdMeta):
        name = "dbtool"
        version = "1.0.0"

    def query(self, sql: Arg(str, 'SQL查询语句'),
              output: Arg(OutputFormat, '输出格式') = OutputFormat.TABLE,
              limit: Arg(int, '返回行数上限') = 100):
        """执行SQL查询并展示结果"""
        cmdui.info('执行: {}'.format(sql))
        result = [
            {"id": 1, "name": "张三", "age": 25},
            {"id": 2, "name": "李四", "age": 30},
            {"id": 3, "name": "王五", "age": 28},
        ]

        if output == OutputFormat.TABLE or output == 'table':
            cmdui.table(result)
        elif output == OutputFormat.JSON or output == 'json':
            cmdui.json_print(result)
        elif output == OutputFormat.CSV or output == 'csv':
            print("id,name,age")
            for row in result:
                print(",".join(str(v) for v in row.values()))

    def migrate(self, version: Arg(str, '目标版本号') = "latest",
                dry_run: Arg(bool, '试运行，不实际执行') = False):
        """执行数据库迁移"""
        if dry_run:
            cmdui.warning("试运行模式，不会实际执行")
        cmdui.info('迁移到版本: {}'.format(version))
        import time
        steps = ["检查版本", "备份数据", "执行迁移", "验证结果"]
        for step in cmdui.progress(steps, desc="迁移进度"):
            time.sleep(0.3)
        cmdui.success("迁移完成")

    def stats(self):
        """显示数据库统计信息"""
        cmdui.kv({
            "数据库类型": "SQLite",
            "数据库大小": "15.3 MB",
            "表数量": "12",
            "总行数": "1,234,567",
            "最后备份": "2026-04-17 10:30:00",
            "连接池状态": "5/20 活跃",
        })

    def tree_demo(self):
        """树形结构展示 demo"""
        cmdui.tree({
            "数据库": {
                "users": {
                    "id": "INT PRIMARY KEY",
                    "name": "VARCHAR(100)",
                    "age": "INT",
                },
                "orders": {
                    "id": "INT PRIMARY KEY",
                    "user_id": "INT FOREIGN KEY",
                    "total": "DECIMAL(10,2)",
                },
            },
            "配置": {
                "max_connections": "20",
                "timeout": "30s",
            },
        })


if __name__ == '__main__':
    DbTool().run()

    '''
    D:/ProgramData/Miniconda3/envs/py39b/python.exe examples/demo_full.py --web --web-port 8083
    
    '''

`````

--- **end of file: examples/demo_full.py** (project: nb_cmd) --- 

---


--- **start of file: examples/demo_inherit.py** (project: nb_cmd) --- 

`````python
# -*- coding: utf-8 -*-
"""
nb_cmd 继承覆写 demo —— 对应设计文档 5.2 和附录B

用法:
    python demo_inherit.py deploy web-01 --version v2.0
    python demo_inherit.py status
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from nb_cmd import NbCmd, cmdui


class BaseDeploy(NbCmd):
    """基础部署工具"""

    def deploy(self, host: str, version: str = "latest"):
        """部署服务到目标主机"""
        self._pre_deploy(host)
        self._do_deploy(host, version)
        self._post_deploy(host)
        cmdui.success('{}@{} 已部署到 {}'.format("app", version, host))

    def status(self):
        """查看部署状态"""
        cmdui.kv({
            "部署方式": self._deploy_type(),
            "最后部署": "2026-04-17 15:00",
            "状态": "运行中",
        })

    def _deploy_type(self):
        return "基础部署"

    def _pre_deploy(self, host):
        cmdui.info('部署前检查: {}'.format(host))

    def _do_deploy(self, host, version):
        cmdui.info('上传文件到 {} ...'.format(host))
        cmdui.info('重启服务 ...')

    def _post_deploy(self, host):
        cmdui.info('验证服务状态: OK')


class DockerDeploy(BaseDeploy):
    """Docker部署——只需覆写部署逻辑"""

    def _deploy_type(self):
        return "Docker"

    def _do_deploy(self, host, version):
        cmdui.info('docker pull app:{}'.format(version))
        cmdui.info('docker-compose up -d')


class K8sDeploy(BaseDeploy):
    """K8s部署——覆写部署逻辑，还新增了 scale 命令"""

    def _deploy_type(self):
        return "Kubernetes"

    def _do_deploy(self, host, version):
        cmdui.info('kubectl set image deployment/app app=app:{}'.format(version))
        cmdui.info('kubectl rollout status deployment/app')

    def scale(self, replicas: int = 3):
        """扩缩容（K8s特有命令）"""
        cmdui.info('kubectl scale deployment/app --replicas={}'.format(replicas))
        cmdui.success('app 已扩缩至 {} 个副本'.format(replicas))


if __name__ == '__main__':
    import sys as _sys
    ops_map = {'base': BaseDeploy, 'docker': DockerDeploy, 'k8s': K8sDeploy}
    if len(_sys.argv) > 1 and _sys.argv[1] in ops_map:
        mode = _sys.argv.pop(1)
        ops_map[mode]().run()
    else:
        BaseDeploy().run()

`````

--- **end of file: examples/demo_inherit.py** (project: nb_cmd) --- 

---


--- **start of file: examples/demo_nb_log.py** (project: nb_cmd) --- 

`````python
# -*- coding: utf-8 -*-
"""
nb_cmd 集成 nb_log 的 demo —— 对应设计文档 7.1 Meta 配置类

演示 use_nb_log = True 时的效果:
  - self.logger 变为 nb_log 增强版 logger（彩色、文件名行号等）
  - 日志自动写入 log_file

前提: pip install nb_log

用法:
    python demo_nb_log.py --help
    python demo_nb_log.py deploy 10.0.0.1 --env staging
    python demo_nb_log.py stats
    python demo_nb_log.py --web --web-port 9911
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from nb_cmd import NbCmd, Arg, NbCmdMeta, cmdui
from enum import Enum


class Environment(Enum):
    DEV = "dev"
    STAGING = "staging"
    PROD = "prod"


class ServerTool(NbCmd):
    """服务器运维工具（启用 nb_log 增强日志）"""

    class Meta(NbCmdMeta):
        name = "server-tool"
        version = "1.0.0"

        use_nb_log = True
        log_level = "DEBUG"
        log_file = "server_tool.log"

        web_theme = "dark"

    def __init__(self, region: Arg(str, '机房区域', alias='r'),
                 timeout: Arg(int, '超时秒数') = 30):
        super().__init__()
        self.region = region
        self.timeout = timeout

    def before_run(self):
        """所有子命令执行前的钩子"""
        self.logger.info('服务器运维工具启动 (区域: {}, 超时: {}s)'.format(
            self.region, self.timeout))

    def after_run(self):
        """所有子命令执行后的钩子"""
        self.logger.info('运维操作完成')

    def deploy(self, host: str, env: Environment = Environment.DEV, dry_run: bool = False):
        """部署服务到目标主机"""
        self.logger.debug('参数: host={}, env={}, dry_run={}'.format(host, env.value, dry_run))

        if dry_run:
            cmdui.warning('试运行模式，不会实际部署')

        self.logger.info('正在部署到 {} (环境: {})'.format(host, env.value))
        cmdui.info('检查服务器连接...')
        cmdui.info('上传代码包...')
        cmdui.info('重启服务...')
        cmdui.success('部署完成: {} ({})'.format(host, env.value))

    def stats(self):
        """查看系统状态"""
        self.logger.info('查询系统状态')
        cmdui.kv({
            "CPU使用率": "45%",
            "内存使用": "2.3GB / 8GB",
            "磁盘使用": "120GB / 500GB",
            "运行时间": "3天12小时",
            "活跃连接": "128",
        })

    def check(self, host: str):
        """健康检查"""
        self.logger.info('检查 {} 健康状态'.format(host))
        data = [
            {"服务": "nginx", "状态": "running", "端口": 80},
            {"服务": "mysql", "状态": "running", "端口": 3306},
            {"服务": "redis", "状态": "running", "端口": 6379},
        ]
        cmdui.table(data)
        cmdui.success('所有服务运行正常')

    def logs(self, service: str = "nginx", lines: int = 10):
        """查看服务日志"""
        self.logger.info('查看 {} 最近 {} 行日志'.format(service, lines))
        for i in range(lines):
            print('[2026-04-17 15:{:02d}:00] {} - 请求处理完成'.format(30 + i, service))


if __name__ == '__main__':
    ServerTool('beijing').run()

    '''
    D:/ProgramData/Miniconda3/envs/py39b/python.exe examples/demo_nb_log.py --web --web-port 8087

    '''

`````

--- **end of file: examples/demo_nb_log.py** (project: nb_cmd) --- 

---


--- **start of file: examples/demo_subcommands.py** (project: nb_cmd) --- 

`````python
# -*- coding: utf-8 -*-
"""
nb_cmd 多层级子命令 demo —— 对应设计文档 5.3
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from nb_cmd import NbCmd, Arg


class GitRemote(NbCmd):
    """远程仓库管理"""

    def add(self, name: Arg(str, '远程仓库名'), url: Arg(str, '仓库URL')):
        """添加远程仓库"""
        print('git remote add {} {}'.format(name, url))

    def remove(self, name: Arg(str, '要删除的远程名')):
        """删除远程仓库"""
        print('git remote remove {}'.format(name))

    def show(self):
        """列出所有远程仓库"""
        print('origin  https://github.com/xxx/xxx.git (fetch)')


class GitBranch(NbCmd):
    """分支管理"""

    def create(self, name: Arg(str, '分支名'),
               from_branch: Arg(str, '基于哪个分支') = "main"):
        """创建分支"""
        print('git checkout -b {} {}'.format(name, from_branch))

    def delete(self, name: Arg(str, '分支名'),
               force: Arg(bool, '强制删除', alias='f') = False):
        """删除分支"""
        flag = "-D" if force else "-d"
        print('git branch {} {}'.format(flag, name))

    def show(self):
        """列出所有分支"""
        print('* main')
        print('  develop')
        print('  feature/login')


class GitTool(NbCmd):
    """简易Git工具"""

    sub_commands = {
        'remote': GitRemote,
        'branch': GitBranch,
    }

    def status(self):
        """查看状态"""
        print('当前分支: main')

    def commit(self, message: Arg(str, '提交信息', alias='m'),
               all: Arg(bool, '自动 add 所有文件', alias='a') = False):
        """提交"""
        if all:
            print('git add -A')
        print("git commit -m '{}'".format(message))


if __name__ == '__main__':
    GitTool().run()
   
    '''
    D:/ProgramData/Miniconda3/envs/py39b/python.exe examples/demo_subcommands.py --web --web-port 8084
    
    '''
`````

--- **end of file: examples/demo_subcommands.py** (project: nb_cmd) --- 

---

# markdown content namespace: nb_cmd codes 


## nb_cmd File Tree (relative dir: `nb_cmd`)


`````

└── nb_cmd
    ├── __init__.py
    ├── core
    │   ├── __init__.py
    │   ├── arg.py
    │   ├── discovery.py
    │   ├── parser.py
    │   ├── result_handler.py
    │   └── type_utils.py
    ├── modes
    │   ├── __init__.py
    │   ├── api_mode.py
    │   ├── cli_mode.py
    │   └── web_mode.py
    ├── ui
    │   ├── __init__.py
    │   ├── colors.py
    │   ├── progress.py
    │   └── table.py
    └── utils
        ├── __init__.py
        ├── config.py
        └── validators.py

`````

---


## nb_cmd (relative dir: `nb_cmd`)  Included Files (total: 18 files)


- `nb_cmd/__init__.py`

- `nb_cmd/core/arg.py`

- `nb_cmd/core/discovery.py`

- `nb_cmd/core/parser.py`

- `nb_cmd/core/result_handler.py`

- `nb_cmd/core/type_utils.py`

- `nb_cmd/core/__init__.py`

- `nb_cmd/modes/api_mode.py`

- `nb_cmd/modes/cli_mode.py`

- `nb_cmd/modes/web_mode.py`

- `nb_cmd/modes/__init__.py`

- `nb_cmd/ui/colors.py`

- `nb_cmd/ui/progress.py`

- `nb_cmd/ui/table.py`

- `nb_cmd/ui/__init__.py`

- `nb_cmd/utils/config.py`

- `nb_cmd/utils/validators.py`

- `nb_cmd/utils/__init__.py`


---


--- **start of file: nb_cmd/__init__.py** (project: nb_cmd) --- 

`````python
# -*- coding: utf-8 -*-
"""
nb_cmd — 万能接口生成器
你写一个 Python class，自动获得 CLI + REST API + Web UI 三种接口。

用法::

    from nb_cmd import NbCmd

    class MyTool(NbCmd):
        def greet(self, name: str, times: int = 1):
            for _ in range(times):
                print(f"你好, {name}!")

    if __name__ == '__main__':
        MyTool().run()
"""

__version__ = '0.1.0'

import json
import logging
import sys

from .core.arg import Arg  # noqa: F401
# 模块级 cmdui 单例，在延后创建（类定义之后）
from .ui.colors import print_success, print_warning, print_error, print_info
from .ui.table import print_table, print_kv
from .ui.progress import progress as _progress_iter
from .utils.validators import validate  # noqa: F401


class NbCmdMeta(object):
    """
    NbCmd 的 Meta 配置基类。

    子类继承后可覆盖任意字段，IDE 可自动补全所有可用选项。

    用法::

        from nb_cmd import NbCmd, NbCmdMeta

        class MyTool(NbCmd):
            class Meta(NbCmdMeta):
                name = "my-tool"
                use_nb_log = True
    """
    name = None               # type: str   # CLI/API 名称（默认用类名）
    version = '0.0.1'         # type: str   # 版本号（--version 显示）
    description = None        # type: str   # 描述（默认用类的 docstring）
    use_nb_log = False         # type: bool  # 启用 nb_log 增强日志
    log_level = 'INFO'         # type: str   # 日志级别
    log_file = None            # type: str   # 日志文件路径
    auto_save_last_args = False  # type: bool  # 自动保存上次参数
    config_file = None         # type: str   # 配置持久化文件路径
    serve_host = '0.0.0.0'    # type: str   # Web/API 绑定地址
    serve_port = 8080          # type: int   # Web/API 默认端口
    serve_workers = 1          # type: int   # 工作进程数
    web_title = None           # type: str   # Web UI 页面标题
    web_theme = 'light'        # type: str   # Web UI 主题 ('light' / 'dark')
    aliases = {}               # type: dict  # 参数别名（推荐用 Arg(alias=...) 替代）


class UIHelper(object):
    """
    NbCmd 的 UI 工具方法集合。

    通过 ``from nb_cmd import cmdui`` 导入使用，避免与用户自定义的子命令方法名冲突。
    包含: 输出(table/kv/tree/json_print)、彩色(success/warning/error/info)、
          交互(confirm/prompt/select)、进度(progress) 等工具。
    """

    def table(self, data, headers=None):
        """表格输出"""
        print_table(data, headers)

    def kv(self, data):
        """键值对输出"""
        print_kv(data)

    def tree(self, data, prefix='', is_last=True):
        """树形输出"""
        if isinstance(data, dict):
            items = list(data.items())
            for i, (key, value) in enumerate(items):
                last = (i == len(items) - 1)
                connector = '└── ' if last else '├── '
                if isinstance(value, dict):
                    sys.stdout.write('{}{}{}\n'.format(prefix, connector, key))
                    extension = '    ' if last else '│   '
                    self.tree(value, prefix + extension, last)
                else:
                    sys.stdout.write('{}{}{}: {}\n'.format(prefix, connector, key, value))

    def json_print(self, data):
        """JSON美化输出"""
        sys.stdout.write(json.dumps(data, ensure_ascii=False, indent=2, default=str) + '\n')
        sys.stdout.flush()

    def progress(self, iterable, desc=None, total=None):
        """进度条迭代器"""
        return _progress_iter(iterable, desc=desc, total=total)

    def confirm(self, message):
        """确认提示，返回 True/False"""
        try:
            answer = input('{} [y/N]: '.format(message)).strip().lower()
            return answer in ('y', 'yes')
        except (EOFError, KeyboardInterrupt):
            return False

    def prompt(self, message, default=None):
        """输入提示"""
        try:
            if default is not None:
                answer = input('{} [{}]: '.format(message, default)).strip()
                return answer if answer else default
            else:
                return input('{}: '.format(message)).strip()
        except (EOFError, KeyboardInterrupt):
            return default

    def select(self, message, choices):
        """选择提示"""
        sys.stdout.write(message + '\n')
        for i, choice in enumerate(choices):
            sys.stdout.write('  {}. {}\n'.format(i + 1, choice))
        sys.stdout.flush()
        try:
            idx = int(input('请选择 [1-{}]: '.format(len(choices))).strip()) - 1
            if 0 <= idx < len(choices):
                return choices[idx]
        except (ValueError, EOFError, KeyboardInterrupt):
            pass
        return choices[0] if choices else None

    def success(self, msg):
        """绿色成功信息"""
        print_success(msg)

    def warning(self, msg):
        """黄色警告信息"""
        print_warning(msg)

    def error(self, msg):
        """红色错误信息"""
        print_error(msg)

    def info(self, msg):
        """蓝色信息"""
        print_info(msg)


class NbCmd(object):
    """
    NbCmd 基类 —— 所有命令行工具的父类。

    用法:
        1. 继承 NbCmd
        2. 定义公有方法（自动成为子命令）
        3. 调用 .run() 启动

    功能:
        - 公有方法 → 子命令
        - 方法签名 → 参数自动推导
        - 支持 CLI / REST API / Web UI 三种模式
        - 支持 OOP 继承覆写
        - 支持多层级子命令（sub_commands）

    工具方法通过 cmdui 模块级单例访问（from nb_cmd import cmdui）:
        cmdui.table()  cmdui.kv()  cmdui.tree()  cmdui.json_print()
        cmdui.success() cmdui.warning() cmdui.error() cmdui.info()
        cmdui.progress() cmdui.confirm() cmdui.prompt() cmdui.select()
    """

    sub_commands = {}

    Meta = NbCmdMeta

    def __init__(self):
        self._logger = None
        self._setup_logging()

    def _setup_logging(self):
        """设置日志"""
        meta = self._get_meta()
        use_nb_log = getattr(meta, 'use_nb_log', False)
        log_level = getattr(meta, 'log_level', 'INFO')

        if use_nb_log:
            try:
                import nb_log
                self._logger = nb_log.get_logger(
                    self.__class__.__name__,
                    log_level_int=getattr(logging, log_level, logging.INFO),
                    log_filename=getattr(meta, 'log_file', None),
                )
                return
            except ImportError:
                pass

        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.setLevel(getattr(logging, log_level, logging.INFO))
        if not self._logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter(
                '%(asctime)s [%(name)s] %(levelname)s: %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            ))
            self._logger.addHandler(handler)

    def _get_meta(self):
        """获取 Meta 配置类"""
        return getattr(self.__class__, 'Meta', NbCmd.Meta)

    @property
    def logger(self):
        """日志器"""
        return self._logger

    # ==================== 生命周期钩子 ====================

    def before_run(self):
        """所有子命令执行前的钩子，子类可覆写"""
        pass

    def after_run(self):
        """所有子命令执行后的钩子，子类可覆写"""
        pass

    def on_error(self, command, error):
        """子命令执行出错时的钩子，子类可覆写"""
        if self._logger:
            self._logger.error('命令 {} 执行失败: {}'.format(command, error))

    # ==================== 系统命令工具 ====================

    def shell(self, cmd, capture=False, check=False):
        """
        执行系统命令。

        Parameters
        ----------
        cmd : str  要执行的命令
        capture : bool  是否捕获输出（True 返回 stdout 字符串，False 通过 print 输出）
        check : bool  命令失败时是否抛出异常

        Returns
        -------
        str (capture=True 时返回 stdout) 或 None
        """
        import subprocess
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True,
        )
        if check and result.returncode != 0:
            raise RuntimeError(
                '命令执行失败 (exit {}): {}\n{}'.format(
                    result.returncode, cmd, result.stderr
                )
            )
        if capture:
            return result.stdout.strip()
        else:
            if result.stdout:
                print(result.stdout, end='')
            if result.stderr:
                print(result.stderr, end='', file=sys.stderr)

    def exec(self, cmd: str):
        """执行任意系统命令"""
        self.shell(cmd)

    # ==================== 主入口 ====================

    def run(self, args=None):
        """
        主入口方法。根据参数决定运行模式。

        Parameters
        ----------
        args : list, optional
            命令行参数列表，默认使用 sys.argv[1:]
        """
        raw_args = args if args is not None else sys.argv[1:]

        if '--full-help' in raw_args or '-fh' in raw_args:
            from .core.parser import print_full_help
            return print_full_help(self, NbCmd)

        if '--web' in raw_args:
            return self._start_web_server(raw_args)

        from .modes.cli_mode import run_cli
        return run_cli(self, NbCmd, args)

    def _start_web_server(self, raw_args):
        """启动 Web UI 服务"""
        port = self._extract_port(raw_args)
        meta = self._get_meta()
        host = getattr(meta, 'serve_host', '0.0.0.0')
        if port is None:
            port = getattr(meta, 'serve_port', 8080)

        from .modes.web_mode import start_web_server
        start_web_server(self, NbCmd, host=host, port=port)

    @staticmethod
    def _extract_port(raw_args):
        """从参数列表中提取 --web-port 的值"""
        if '--web-port' in raw_args:
            idx = raw_args.index('--web-port')
            if idx + 1 < len(raw_args):
                try:
                    return int(raw_args[idx + 1])
                except ValueError:
                    pass
        return None


cmdui = UIHelper()

`````

--- **end of file: nb_cmd/__init__.py** (project: nb_cmd) --- 

---


--- **start of file: nb_cmd/core/arg.py** (project: nb_cmd) --- 

`````python
# -*- coding: utf-8 -*-
"""
Arg —— 参数描述器，为方法参数附加描述和别名。

用法::

    from nb_cmd import NbCmd, Arg

    class MyTool(NbCmd):
        def greet(self, name: Arg(str, '要问候的人名', alias='n'),
                  times: Arg(int, '问候次数', alias='t') = 1):
            ...
"""


class Arg(object):
    """
    参数元数据描述器。

    Parameters
    ----------
    type_ : type
        参数的真实类型（str, int, bool, Enum, List[str] 等）
    desc : str, optional
        参数描述，显示在 CLI --help 和 Web UI 输入框中
    alias : str or list, optional
        CLI 短参数别名，如 'n' 自动转为 '-n'，'host-name' 转为 '--host-name'
    """

    def __init__(self, type_, desc=None, alias=None):
        self.type = type_
        self.desc = desc
        if alias is None:
            self.aliases = []
        elif isinstance(alias, (list, tuple)):
            self.aliases = [_normalize_alias(a) for a in alias]
        else:
            self.aliases = [_normalize_alias(alias)]

    def __repr__(self):
        parts = [self.type.__name__ if hasattr(self.type, '__name__') else str(self.type)]
        if self.desc:
            parts.append('desc={!r}'.format(self.desc))
        if self.aliases:
            parts.append('alias={!r}'.format(self.aliases))
        return 'Arg({})'.format(', '.join(parts))


def _normalize_alias(alias):
    """将用户给的 alias 标准化为 CLI flag 格式"""
    s = str(alias)
    if s.startswith('-'):
        return s
    if len(s) == 1:
        return '-' + s
    return '--' + s


def unwrap_arg(hint):
    """
    如果 hint 是 Arg 实例，返回 (real_type, arg_instance)；
    否则返回 (hint, None)。
    """
    if isinstance(hint, Arg):
        return hint.type, hint
    return hint, None

`````

--- **end of file: nb_cmd/core/arg.py** (project: nb_cmd) --- 

---


--- **start of file: nb_cmd/core/discovery.py** (project: nb_cmd) --- 

`````python
# -*- coding: utf-8 -*-
"""
命令发现模块 —— 通过反射发现类中的所有公有方法，自动转换为子命令。
"""
import inspect

from typing import get_type_hints

from .arg import unwrap_arg


def discover_commands(instance, base_cls, include_builtins=True):
    """
    发现 instance 上所有应暴露为 CLI 子命令的方法，以及 sub_commands 中的子命令组。

    Parameters
    ----------
    include_builtins : bool
        是否包含基类内置命令（如 exec），顶层类为 True，子命令组为 False

    返回: OrderedDict  { cmd_name: cmd_info_dict }
    """
    from collections import OrderedDict
    commands = OrderedDict()

    _BUILTIN_COMMANDS = {'exec'} if include_builtins else set()
    base_methods = set(dir(base_cls)) - _BUILTIN_COMMANDS

    for name in sorted(dir(instance)):
        if name.startswith('_'):
            continue
        if name in base_methods:
            continue
        if name in ('sub_commands',):
            continue

        attr = getattr(instance, name, None)
        if attr is None:
            continue
        if not callable(attr):
            continue
        if not (inspect.ismethod(attr) or inspect.isfunction(attr)):
            continue

        sig = inspect.signature(attr)
        doc = inspect.getdoc(attr) or ""

        try:
            hints = get_type_hints(attr)
        except Exception:
            hints = {}

        real_hints = {}
        arg_meta = {}
        missing_types = []

        for param_name, param in sig.parameters.items():
            if param_name == 'self':
                continue
            raw_hint = hints.get(param_name)
            if raw_hint is None:
                anno = param.annotation
                if anno is not inspect.Parameter.empty:
                    raw_hint = anno
            if raw_hint is None:
                missing_types.append(param_name)
                continue
            real_type, arg_inst = unwrap_arg(raw_hint)
            real_hints[param_name] = real_type
            if arg_inst is not None:
                arg_meta[param_name] = arg_inst

        if missing_types:
            cls_name = instance.__class__.__name__
            raise TypeError(
                '{cls}.{method}() 的参数 {params} 缺少类型注解。'
                'nb_cmd 要求所有公有方法的参数必须声明类型，例如: '
                'def {method}(self, {example}: str)'.format(
                    cls=cls_name,
                    method=name,
                    params=', '.join("'{}'".format(p) for p in missing_types),
                    example=missing_types[0],
                )
            )

        commands[name] = {
            'method': attr,
            'signature': sig,
            'type_hints': real_hints,
            'arg_meta': arg_meta,
            'doc': doc.split('\n')[0],
            'full_doc': doc,
            'is_group': False,
        }

    sub_cmds = getattr(instance.__class__, 'sub_commands', {})
    for group_name, group_cls in sub_cmds.items():
        if inspect.isclass(group_cls) and issubclass(group_cls, base_cls):
            commands[group_name] = {
                'cls': group_cls,
                'doc': (inspect.getdoc(group_cls) or "").split('\n')[0],
                'is_group': True,
            }

    return commands

`````

--- **end of file: nb_cmd/core/discovery.py** (project: nb_cmd) --- 

---


--- **start of file: nb_cmd/core/parser.py** (project: nb_cmd) --- 

`````python
# -*- coding: utf-8 -*-
"""
argparse 解析器自动构建模块。
根据方法签名自动生成 argparse.ArgumentParser。
"""
import argparse
import inspect

from .type_utils import (
    get_argparse_type, get_nargs, get_choices,
    is_optional, unwrap_optional, type_display_name,
)


class _RawDefaultsHelpFormatter(argparse.RawDescriptionHelpFormatter,
                                argparse.ArgumentDefaultsHelpFormatter):
    pass


def build_parser(instance, commands, meta):
    """
    为顶层 NbCmd 实例构建完整的 argparse 解析器。

    Parameters
    ----------
    instance : NbCmd 实例
    commands : dict  由 discover_commands 返回
    meta : Meta 配置类
    """
    description = inspect.getdoc(instance) or instance.__class__.__name__
    version = getattr(meta, 'version', '0.0.1')

    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=_RawDefaultsHelpFormatter,
        add_help=False,
    )

    sys_group = parser.add_argument_group('system params')
    sys_group.add_argument('-h', '--help', action='help',
                           default=argparse.SUPPRESS, help='显示帮助信息')
    sys_group.add_argument('--version', action='version', version=version)
    sys_group.add_argument('--full-help', '-fh', action='store_true',
                           default=False, help='显示所有命令的完整参数详情')
    sys_group.add_argument('--web', action='store_true',
                           help='以Web UI + REST API模式启动')
    sys_group.add_argument('--web-port', type=int, default=None,
                           help='Web UI 服务端口（用于 --web）')

    init_group = parser.add_argument_group('init params')
    _add_init_global_options(init_group, instance)

    subparsers = parser.add_subparsers(dest='_nb_command',
                                       title='commands', help='可用命令')

    for cmd_name, cmd_info in commands.items():
        cli_name = cmd_name.replace('_', '-')

        if cmd_info.get('is_group'):
            group_cls = cmd_info['cls']
            group_doc = cmd_info.get('doc', '')
            sub = subparsers.add_parser(
                cli_name,
                help=group_doc + '（子命令组）' if group_doc else '子命令组',
                description=group_doc,
                formatter_class=_RawDefaultsHelpFormatter,
            )
            _build_group_subparser(sub, group_cls, instance.__class__)
        else:
            param_hint = _build_param_hint(cmd_info)
            help_text = cmd_info['doc']
            if param_hint:
                help_text = '{} {}'.format(help_text, param_hint)
            sub = subparsers.add_parser(
                cli_name,
                help=help_text,
                description=cmd_info['full_doc'],
                formatter_class=_RawDefaultsHelpFormatter,
            )
            _add_method_arguments(sub, cmd_info, meta)

    return parser


def _build_param_hint(cmd_info):
    """为子命令生成简短的参数提示，显示在顶层 --help 的子命令描述后面"""
    sig = cmd_info['signature']
    arg_meta = cmd_info.get('arg_meta', {})
    parts = []
    for pname, param in sig.parameters.items():
        if pname == 'self':
            continue
        has_default = param.default is not inspect.Parameter.empty
        arg_inst = arg_meta.get(pname)
        cli_name = '--' + pname.replace('_', '-')
        if arg_inst and arg_inst.aliases:
            short = arg_inst.aliases[0]
            flag = '{}/{}'.format(short, cli_name)
        else:
            flag = pname.upper() if not has_default else cli_name
        if has_default and param.default is not False and param.default is not True:
            parts.append('{}={}'.format(flag, param.default))
        else:
            parts.append(flag)
    if not parts:
        return ''
    return '({})'.format(', '.join(parts))


def print_full_help(instance, base_cls):
    """打印所有命令的完整参数详情"""
    import sys as _sys
    from .discovery import discover_commands

    meta = getattr(instance.__class__, 'Meta', type('Meta', (), {}))
    commands = discover_commands(instance, base_cls)
    description = inspect.getdoc(instance) or instance.__class__.__name__
    version = getattr(meta, 'version', '0.0.1')

    w = _sys.stdout.write
    line = '=' * 56

    w('\n{}\n  {} v{}\n  {}\n{}\n\n'.format(
        line, instance.__class__.__name__, version, description, line))

    w('system params:\n')
    w('    {:<24s} {}\n'.format('--help, -h', '显示简要帮助'))
    w('    {:<24s} {}\n'.format('--full-help, -fh', '显示本完整帮助'))
    w('    {:<24s} {}\n'.format('--version', '显示版本号'))
    w('    {:<24s} {}\n'.format('--web', '以Web UI + REST API模式启动'))
    w('    {:<24s} {}\n'.format('--web-port PORT', 'Web UI 服务端口（用于 --web）'))
    w('\n')

    has_init_params = _has_init_params(instance)
    if has_init_params:
        w('init params:\n')
        _print_init_params(w, instance)
        w('\n')

    w('{}\n'.format('-' * 56))
    for cmd_name, cmd_info in commands.items():
        cli_name = cmd_name.replace('_', '-')

        if cmd_info.get('is_group'):
            w('{} \033[36m[子命令组]\033[0m  {}\n'.format(
                cli_name, cmd_info.get('doc', '')))
            group_cls = cmd_info['cls']
            try:
                group_inst = group_cls()
            except TypeError:
                group_inst = group_cls.__new__(group_cls)
            group_cmds = discover_commands(group_inst, base_cls,
                                           include_builtins=False)
            for sub_name, sub_info in group_cmds.items():
                if sub_info.get('is_group'):
                    continue
                sub_cli = '{} {}'.format(cli_name, sub_name.replace('_', '-'))
                w('\n  {} — {}\n'.format(sub_cli, sub_info.get('doc', '')))
                _print_params(w, sub_info)
            w('\n')
        else:
            w('{} — {}\n'.format(cli_name, cmd_info.get('doc', '')))
            _print_params(w, cmd_info)
            w('\n')

    _sys.stdout.flush()


def _print_params(write_fn, cmd_info):
    """打印一个命令的完整参数列表"""
    sig = cmd_info['signature']
    hints = cmd_info.get('type_hints', {})
    arg_meta = cmd_info.get('arg_meta', {})

    for pname, param in sig.parameters.items():
        if pname == 'self':
            continue
        ptype = hints.get(pname, str)
        real_type = unwrap_optional(ptype) if is_optional(ptype) else ptype
        type_name = type_display_name(real_type)
        has_default = param.default is not inspect.Parameter.empty
        arg_inst = arg_meta.get(pname)
        desc = arg_inst.desc if arg_inst and arg_inst.desc else ''

        cli_flag = '--' + pname.replace('_', '-')
        if arg_inst and arg_inst.aliases:
            flags_str = '{}, {}'.format(cli_flag, ', '.join(arg_inst.aliases))
        else:
            if not has_default:
                flags_str = pname.upper()
            else:
                flags_str = cli_flag

        if has_default:
            meta_str = '({}, 默认: {})'.format(type_name, param.default)
        else:
            meta_str = '({}, 必填)'.format(type_name)

        if desc:
            write_fn('    {:<24s} {}  {}\n'.format(flags_str, desc, meta_str))
        else:
            write_fn('    {:<24s} {}\n'.format(flags_str, meta_str))


def _has_init_params(instance):
    """判断实例的 __init__ 是否有自定义全局参数"""
    init_method = instance.__class__.__init__
    if init_method is object.__init__:
        return False
    sig = inspect.signature(init_method)
    for pname, param in sig.parameters.items():
        if pname != 'self':
            return True
    return False


def _print_init_params(write_fn, instance):
    """打印 __init__ 全局选项的详情（用于 --full-help）"""
    from .arg import unwrap_arg

    init_method = instance.__class__.__init__
    if init_method is object.__init__:
        return

    sig = inspect.signature(init_method)

    for pname, param in sig.parameters.items():
        if pname == 'self':
            continue

        has_default = param.default is not inspect.Parameter.empty
        if has_default:
            default_val = param.default
        else:
            default_val = getattr(instance, pname, None)

        raw_hint = param.annotation
        if raw_hint is inspect.Parameter.empty:
            if default_val is not None:
                raw_hint = type(default_val)
            else:
                raw_hint = str

        real_type, arg_inst = unwrap_arg(raw_hint)
        type_name = type_display_name(real_type)
        desc = arg_inst.desc if arg_inst and arg_inst.desc else ''

        cli_flag = '--' + pname.replace('_', '-')
        if arg_inst and arg_inst.aliases:
            flags_str = '{}, {}'.format(cli_flag, ', '.join(arg_inst.aliases))
        else:
            flags_str = cli_flag

        meta_str = '(全局, {}, 默认: {})'.format(type_name, default_val)

        if desc:
            write_fn('    {:<24s} {}  {}\n'.format(flags_str, desc, meta_str))
        else:
            write_fn('    {:<24s} {}\n'.format(flags_str, meta_str))


def _add_init_global_options(parser, instance):
    """将 __init__ 中的自定义参数变为全局选项，支持 Arg 描述器"""
    from .arg import unwrap_arg

    init_method = instance.__class__.__init__
    if init_method is object.__init__:
        return

    sig = inspect.signature(init_method)

    for param_name, param in sig.parameters.items():
        if param_name == 'self':
            continue

        has_default = param.default is not inspect.Parameter.empty
        if has_default:
            default_val = param.default
        else:
            default_val = getattr(instance, param_name, None)

        raw_hint = param.annotation
        if raw_hint is inspect.Parameter.empty:
            if default_val is not None:
                raw_hint = type(default_val)
            else:
                raw_hint = str

        param_type, arg_inst = unwrap_arg(raw_hint)

        cli_flag = '--' + param_name.replace('_', '-')
        extra_flags = arg_inst.aliases if arg_inst and arg_inst.aliases else []
        desc = arg_inst.desc if arg_inst and arg_inst.desc else None

        metavar = param_name.upper()
        if param_type is bool:
            flags = [cli_flag] + extra_flags
            auto_help = '(全局选项, bool, 默认: {})'.format(default_val)
            parser.add_argument(
                *flags,
                action='store_true' if not default_val else 'store_false',
                default=default_val,
                dest='_nb_init_' + param_name,
                help='{} {}'.format(desc, auto_help) if desc else auto_help,
            )
        else:
            flags = [cli_flag] + extra_flags
            auto_help = '(全局选项, {}, 默认: {})'.format(
                type_display_name(param_type), default_val)
            parser.add_argument(
                *flags,
                type=get_argparse_type(param_type),
                default=default_val,
                dest='_nb_init_' + param_name,
                metavar=metavar,
                help='{} {}'.format(desc, auto_help) if desc else auto_help,
            )


def _add_method_arguments(sub_parser, cmd_info, meta):
    """根据方法签名向 subparser 添加参数"""
    sig = cmd_info['signature']
    hints = cmd_info.get('type_hints', {})
    arg_meta = cmd_info.get('arg_meta', {})
    method_name = cmd_info['method'].__name__

    aliases_map = getattr(meta, 'aliases', {})

    for param_name, param in sig.parameters.items():
        if param_name == 'self':
            continue

        param_type = hints.get(param_name, str)
        if is_optional(param_type):
            param_type_unwrapped = unwrap_optional(param_type)
        else:
            param_type_unwrapped = param_type

        has_default = param.default is not inspect.Parameter.empty
        is_keyword_only = param.kind == inspect.Parameter.KEYWORD_ONLY

        arg_inst = arg_meta.get(param_name)
        if arg_inst and arg_inst.aliases:
            extra_flags = list(arg_inst.aliases)
        else:
            alias_key = '{}.{}'.format(method_name, param_name)
            extra_flags = aliases_map.get(alias_key, [])

        desc = arg_inst.desc if arg_inst and arg_inst.desc else None

        cli_flag = '--' + param_name.replace('_', '-')
        nargs = get_nargs(param_type)
        choices = get_choices(param_type)
        ap_type = get_argparse_type(param_type)
        type_name = type_display_name(param_type_unwrapped)

        if param_type_unwrapped is bool:
            flags = [cli_flag] + extra_flags
            auto_help = '(bool, 默认: {})'.format(param.default if has_default else False)
            sub_parser.add_argument(
                *flags,
                action='store_true' if not (has_default and param.default) else 'store_false',
                default=param.default if has_default else False,
                dest=param_name,
                help='{} {}'.format(desc, auto_help) if desc else auto_help,
            )
        elif has_default or is_keyword_only:
            flags = [cli_flag] + extra_flags
            auto_help = '({}, 默认: {})'.format(type_name, param.default if has_default else 'None')
            kwargs = dict(
                type=ap_type,
                default=param.default if has_default else None,
                dest=param_name,
                help='{} {}'.format(desc, auto_help) if desc else auto_help,
            )
            if nargs is not None:
                kwargs['nargs'] = nargs
            if choices is not None:
                kwargs['choices'] = choices
            sub_parser.add_argument(*flags, **kwargs)
        else:
            auto_help = '({}, 必填)'.format(type_name)
            if extra_flags:
                flags = [cli_flag] + extra_flags
                kwargs = dict(
                    type=ap_type,
                    required=True,
                    dest=param_name,
                    help='{} {}'.format(desc, auto_help) if desc else auto_help,
                )
                if nargs is not None:
                    kwargs['nargs'] = nargs
                if choices is not None:
                    kwargs['choices'] = choices
                sub_parser.add_argument(*flags, **kwargs)
            else:
                kwargs = dict(
                    type=ap_type,
                    help='{} {}'.format(desc, auto_help) if desc else auto_help,
                )
                if nargs is not None:
                    kwargs['nargs'] = nargs
                if choices is not None:
                    kwargs['choices'] = choices
                sub_parser.add_argument(param_name, **kwargs)


def _build_group_subparser(parent_parser, group_cls, base_cls):
    """递归为子命令组构建 subparser"""
    from .discovery import discover_commands

    group_instance = group_cls.__new__(group_cls)
    if hasattr(group_cls.__init__, '__func__') and group_cls.__init__ is not object.__init__:
        try:
            group_cls.__init__(group_instance)
        except TypeError:
            pass

    group_commands = discover_commands(group_instance, base_cls)

    if not group_commands:
        return

    sub_group_meta = getattr(group_cls, 'Meta', type('Meta', (), {}))

    group_subparsers = parent_parser.add_subparsers(dest='_nb_sub_command', help='可用子命令')

    for cmd_name, cmd_info in group_commands.items():
        cli_name = cmd_name.replace('_', '-')

        if cmd_info.get('is_group'):
            nested_cls = cmd_info['cls']
            nested_doc = cmd_info.get('doc', '')
            nested_sub = group_subparsers.add_parser(
                cli_name,
                help=nested_doc + '（子命令组）' if nested_doc else '子命令组',
                description=nested_doc,
                formatter_class=_RawDefaultsHelpFormatter,
            )
            _build_group_subparser(nested_sub, nested_cls, base_cls)
        else:
            sub = group_subparsers.add_parser(
                cli_name,
                help=cmd_info['doc'],
                description=cmd_info['full_doc'],
                formatter_class=_RawDefaultsHelpFormatter,
            )
            _add_method_arguments(sub, cmd_info, sub_group_meta)

`````

--- **end of file: nb_cmd/core/parser.py** (project: nb_cmd) --- 

---


--- **start of file: nb_cmd/core/result_handler.py** (project: nb_cmd) --- 

`````python
# -*- coding: utf-8 -*-
"""
返回值自动处理模块。
根据返回值类型决定如何在 CLI / API 中展示结果。
"""
import json
from pathlib import Path

from ..ui.table import _display_width as _cjk_display_width


def handle_cli_result(result):
    """
    CLI 模式下自动处理方法返回值。

    规则:
    - None          → 不输出
    - str           → 直接 print
    - int / float   → 直接 print
    - dict          → JSON 格式化输出
    - list[dict]    → 表格输出（降级为 JSON）
    - list          → 每行一个
    - Path          → 输出路径字符串
    """
    if result is None:
        return

    if isinstance(result, str):
        print(result)
        return

    if isinstance(result, (int, float)):
        print(result)
        return

    if isinstance(result, dict):
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if isinstance(result, (list, tuple)):
        if result and isinstance(result[0], dict):
            _print_list_of_dicts_as_table(result)
        else:
            for item in result:
                print(item)
        return

    if isinstance(result, Path):
        print(str(result))
        return

    print(result)


def handle_api_result(result):
    """API 模式下处理返回值"""
    if result is None:
        return None

    if isinstance(result, (str, int, float)):
        return {"result": result}

    if isinstance(result, dict):
        return result

    if isinstance(result, (list, tuple)):
        return {"result": result}

    if isinstance(result, Path):
        return {"result": str(result)}

    return {"result": str(result)}


def _print_list_of_dicts_as_table(data):
    """简易表格输出 list[dict]，无外部依赖"""
    if not data:
        return

    headers = list(data[0].keys())
    col_widths = {}
    for h in headers:
        col_widths[h] = len(str(h))
    for row in data:
        for h in headers:
            val = str(row.get(h, ''))
            if len(val) > col_widths[h]:
                col_widths[h] = len(val)

    for h in headers:
        col_widths[h] = max(col_widths[h], _cjk_display_width(str(h)))
    for row in data:
        for h in headers:
            w = _cjk_display_width(str(row.get(h, '')))
            if w > col_widths[h]:
                col_widths[h] = w

    def _pad(text, width):
        dw = _cjk_display_width(text)
        return text + ' ' * (width - dw)

    sep_line = '+' + '+'.join('-' * (col_widths[h] + 2) for h in headers) + '+'
    header_line = '| ' + ' | '.join(_pad(str(h), col_widths[h]) for h in headers) + ' |'

    print(sep_line)
    print(header_line)
    print(sep_line)
    for row in data:
        vals = [_pad(str(row.get(h, '')), col_widths[h]) for h in headers]
        print('| ' + ' | '.join(vals) + ' |')
    print(sep_line)



`````

--- **end of file: nb_cmd/core/result_handler.py** (project: nb_cmd) --- 

---


--- **start of file: nb_cmd/core/type_utils.py** (project: nb_cmd) --- 

`````python
# -*- coding: utf-8 -*-
"""
Python类型 → argparse类型/nargs/choices 的映射工具。
兼容 Python 3.7+。
"""
import enum
from pathlib import Path


def _get_origin(tp):
    """兼容 3.7 的 typing.get_origin"""
    return getattr(tp, '__origin__', None)


def _get_args(tp):
    """兼容 3.7 的 typing.get_args"""
    return getattr(tp, '__args__', ())


def is_optional(tp):
    """判断是否是 Optional[X] (即 Union[X, None])"""
    origin = _get_origin(tp)
    if origin is not None:
        import typing
        if origin is getattr(typing, 'Union', None):
            args = _get_args(tp)
            return type(None) in args
    return False


def unwrap_optional(tp):
    """Optional[X] → X"""
    if is_optional(tp):
        args = _get_args(tp)
        non_none = [a for a in args if a is not type(None)]
        if len(non_none) == 1:
            return non_none[0]
    return tp


def is_enum_type(tp):
    return isinstance(tp, type) and issubclass(tp, enum.Enum)


def is_list_type(tp):
    origin = _get_origin(tp)
    return origin is list


def is_tuple_type(tp):
    origin = _get_origin(tp)
    return origin is tuple


def get_argparse_type(python_type):
    """Python类型 → argparse type 参数"""
    real_type = unwrap_optional(python_type)

    if real_type is bool:
        return None
    if real_type in (int, float, str):
        return real_type
    if real_type is Path:
        return str
    if is_enum_type(real_type):
        return str
    if is_list_type(real_type):
        args = _get_args(real_type)
        if args:
            inner = args[0]
            if inner in (int, float, str):
                return inner
        return str
    if is_tuple_type(real_type):
        return str
    return str


def get_nargs(python_type):
    """Python类型 → argparse nargs"""
    real_type = unwrap_optional(python_type)
    if is_list_type(real_type):
        return '+'
    if is_tuple_type(real_type):
        args = _get_args(real_type)
        if args:
            return len(args)
    return None


def get_choices(python_type):
    """Python类型 → argparse choices"""
    real_type = unwrap_optional(python_type)
    if is_enum_type(real_type):
        return [e.value for e in real_type]
    return None


def convert_value(value, python_type):
    """将 argparse 解析出的字符串值转为目标 Python 类型"""
    real_type = unwrap_optional(python_type)

    if value is None:
        return None

    if real_type is bool:
        return value

    if real_type in (int, float, str):
        return real_type(value)

    if real_type is Path:
        return Path(value)

    if is_enum_type(real_type):
        for member in real_type:
            if member.value == value:
                return member
        return real_type(value)

    if is_list_type(real_type):
        args = _get_args(real_type)
        inner = args[0] if args else str
        if isinstance(value, (list, tuple)):
            return [inner(v) for v in value]
        return [inner(value)]

    if is_tuple_type(real_type):
        args = _get_args(real_type)
        if isinstance(value, (list, tuple)) and args:
            return tuple(args[i](value[i]) for i in range(min(len(args), len(value))))
        return value

    return value


def type_display_name(python_type):
    """获取类型的可读显示名"""
    if hasattr(python_type, '__name__'):
        return python_type.__name__
    return str(python_type).replace('typing.', '')

`````

--- **end of file: nb_cmd/core/type_utils.py** (project: nb_cmd) --- 

---


--- **start of file: nb_cmd/core/__init__.py** (project: nb_cmd) --- 

`````python

`````

--- **end of file: nb_cmd/core/__init__.py** (project: nb_cmd) --- 

---


--- **start of file: nb_cmd/modes/api_mode.py** (project: nb_cmd) --- 

`````python
# -*- coding: utf-8 -*-
"""
REST API 模式 —— 自动将 NbCmd 类的方法生成 FastAPI 路由。
需要安装: pip install fastapi uvicorn
"""
import inspect
import io
import sys
import time

from ..core.discovery import discover_commands
from ..core.result_handler import handle_api_result


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

    commands = discover_commands(instance, base_cls)
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
                group_instance = group_cls()
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

    def _exec(fresh_inst, kwargs):
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = captured_out = io.StringIO()
        sys.stderr = captured_err = io.StringIO()
        try:
            method = getattr(fresh_inst, _cmd_name)
            result = method(**_convert_kwargs(kwargs))
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
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
                result, stdout_output, stderr_output = _exec(fresh_inst, kwargs)
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
                result, stdout_output, stderr_output = _exec(fresh_inst, request)
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

`````

--- **end of file: nb_cmd/modes/api_mode.py** (project: nb_cmd) --- 

---


--- **start of file: nb_cmd/modes/cli_mode.py** (project: nb_cmd) --- 

`````python
# -*- coding: utf-8 -*-
"""
CLI 模式 —— 默认的命令行交互模式。
"""
import inspect

from ..core.discovery import discover_commands
from ..core.parser import build_parser
from ..core.type_utils import convert_value
from ..core.result_handler import handle_cli_result


def run_cli(instance, base_cls, args=None):
    """
    以 CLI 模式执行 NbCmd 实例。

    Parameters
    ----------
    instance : NbCmd 实例
    base_cls : NbCmd 类（用于过滤基类方法）
    args : list, optional  命令行参数列表，默认 sys.argv[1:]
    """
    meta = getattr(instance.__class__, 'Meta', type('Meta', (), {}))
    commands = discover_commands(instance, base_cls)
    parser = build_parser(instance, commands, meta)

    parsed = parser.parse_args(args)

    _apply_init_args(instance, parsed)

    command_name = getattr(parsed, '_nb_command', None)
    if not command_name:
        parser.print_help()
        return

    python_name = command_name.replace('-', '_')

    if python_name in commands and commands[python_name].get('is_group'):
        _run_group_command(instance, commands[python_name], parsed, base_cls)
        return

    if python_name not in commands:
        parser.print_help()
        return

    cmd_info = commands[python_name]
    method = cmd_info['method']
    kwargs = _extract_kwargs(method, cmd_info, parsed)

    instance.before_run()
    try:
        result = method(**kwargs)
        handle_cli_result(result)
    except Exception as e:
        instance.on_error(command_name, e)
        raise
    finally:
        instance.after_run()


def _apply_init_args(instance, parsed):
    """将解析出的全局选项（__init__参数）应用到实例上"""
    init_method = instance.__class__.__init__
    if init_method is object.__init__:
        return

    sig = inspect.signature(init_method)
    for param_name in sig.parameters:
        if param_name == 'self':
            continue
        attr_name = '_nb_init_' + param_name
        if hasattr(parsed, attr_name):
            val = getattr(parsed, attr_name)
            if val is not None:
                setattr(instance, param_name, val)


def _extract_kwargs(method, cmd_info, parsed):
    """从 parsed namespace 中提取方法所需的关键字参数"""
    sig = cmd_info['signature']
    hints = cmd_info.get('type_hints', {})
    kwargs = {}

    for param_name, param in sig.parameters.items():
        if param_name == 'self':
            continue

        raw_value = getattr(parsed, param_name, None)
        param_type = hints.get(param_name, str)
        converted = convert_value(raw_value, param_type)
        kwargs[param_name] = converted

    return kwargs


def _run_group_command(instance, group_info, parsed, base_cls):
    """执行子命令组中的命令"""
    group_cls = group_info['cls']

    try:
        group_instance = group_cls()
    except TypeError:
        group_instance = group_cls.__new__(group_cls)

    sub_command = getattr(parsed, '_nb_sub_command', None)
    if not sub_command:
        print('请指定子命令。使用 --help 查看可用子命令。')
        return

    sub_python_name = sub_command.replace('-', '_')
    sub_commands = discover_commands(group_instance, base_cls)

    if sub_python_name in sub_commands and sub_commands[sub_python_name].get('is_group'):
        _run_group_command(group_instance, sub_commands[sub_python_name], parsed, base_cls)
        return

    if sub_python_name not in sub_commands:
        print('未知子命令: {}'.format(sub_command))
        return

    cmd_info = sub_commands[sub_python_name]
    method = cmd_info['method']
    kwargs = _extract_kwargs(method, cmd_info, parsed)

    group_instance.before_run()
    try:
        result = method(**kwargs)
        handle_cli_result(result)
    except Exception as e:
        group_instance.on_error(sub_command, e)
        raise
    finally:
        group_instance.after_run()

`````

--- **end of file: nb_cmd/modes/cli_mode.py** (project: nb_cmd) --- 

---


--- **start of file: nb_cmd/modes/web_mode.py** (project: nb_cmd) --- 

`````python
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

`````

--- **end of file: nb_cmd/modes/web_mode.py** (project: nb_cmd) --- 

---


--- **start of file: nb_cmd/modes/__init__.py** (project: nb_cmd) --- 

`````python

`````

--- **end of file: nb_cmd/modes/__init__.py** (project: nb_cmd) --- 

---


--- **start of file: nb_cmd/ui/colors.py** (project: nb_cmd) --- 

`````python
# -*- coding: utf-8 -*-
"""
彩色终端输出，纯标准库实现，无外部依赖。
在不支持 ANSI 的终端上自动降级为无色输出。
"""
import os
import sys


def _supports_color():
    """检测当前终端是否支持 ANSI 颜色"""
    if os.getenv('NO_COLOR'):
        return False
    if os.getenv('FORCE_COLOR'):
        return True
    if not hasattr(sys.stdout, 'isatty'):
        return False
    if not sys.stdout.isatty():
        return False
    if sys.platform == 'win32':
        return os.getenv('ANSICON') is not None or 'WT_SESSION' in os.environ or os.getenv('TERM_PROGRAM') == 'vscode'
    return True


_COLOR_ENABLED = _supports_color()

_COLORS = {
    'reset': '\033[0m',
    'bold': '\033[1m',
    'red': '\033[31m',
    'green': '\033[32m',
    'yellow': '\033[33m',
    'blue': '\033[34m',
    'magenta': '\033[35m',
    'cyan': '\033[36m',
    'white': '\033[37m',
    'bright_red': '\033[91m',
    'bright_green': '\033[92m',
    'bright_yellow': '\033[93m',
    'bright_blue': '\033[94m',
}


def _colorize(text, color_name):
    if not _COLOR_ENABLED:
        return text
    color_code = _COLORS.get(color_name, '')
    reset = _COLORS['reset']
    return '{}{}{}'.format(color_code, text, reset)


def print_success(msg):
    sys.stdout.write(_colorize('[OK] {}'.format(msg), 'bright_green') + '\n')
    sys.stdout.flush()


def print_warning(msg):
    sys.stdout.write(_colorize('[WARN] {}'.format(msg), 'bright_yellow') + '\n')
    sys.stdout.flush()


def print_error(msg):
    sys.stderr.write(_colorize('[ERROR] {}'.format(msg), 'bright_red') + '\n')
    sys.stderr.flush()


def print_info(msg):
    sys.stdout.write(_colorize('[INFO] {}'.format(msg), 'bright_blue') + '\n')
    sys.stdout.flush()

`````

--- **end of file: nb_cmd/ui/colors.py** (project: nb_cmd) --- 

---


--- **start of file: nb_cmd/ui/progress.py** (project: nb_cmd) --- 

`````python
# -*- coding: utf-8 -*-
"""
纯标准库的进度条实现，无外部依赖。
"""
import sys
import time


class ProgressBar(object):
    """简易进度条，兼容 Python 3.7+"""

    def __init__(self, iterable=None, desc=None, total=None, bar_width=30, file=None):
        self.iterable = iterable
        self.desc = desc or ''
        self.bar_width = bar_width
        self.file = file or sys.stderr

        if total is not None:
            self.total = total
        elif iterable is not None:
            try:
                self.total = len(iterable)
            except TypeError:
                self.total = None
        else:
            self.total = None

        self.n = 0
        self.start_time = None

    def __iter__(self):
        self.start_time = time.time()
        self.n = 0
        for item in self.iterable:
            yield item
            self.n += 1
            self._display()
        self._display(final=True)
        self.file.write('\n')
        self.file.flush()

    def _display(self, final=False):
        elapsed = time.time() - self.start_time if self.start_time else 0

        if self.total and self.total > 0:
            frac = self.n / self.total
            percent = int(frac * 100)
            filled = int(self.bar_width * frac)
            bar = '█' * filled + '░' * (self.bar_width - filled)

            if elapsed > 0 and self.n > 0:
                rate = self.n / elapsed
                remaining = (self.total - self.n) / rate if rate > 0 else 0
                eta_str = _format_time(remaining)
                elapsed_str = _format_time(elapsed)
            else:
                eta_str = '?'
                elapsed_str = '00:00'

            line = '\r{} {} {}% {}/{} [{}<{}]'.format(
                self.desc, bar, percent, self.n, self.total,
                elapsed_str, eta_str
            )
        else:
            line = '\r{} {} 项已处理 [{:.1f}s]'.format(
                self.desc, self.n, elapsed
            )

        self.file.write(line)
        self.file.flush()


def _format_time(seconds):
    if seconds < 60:
        return '{:02d}:{:02d}'.format(0, int(seconds))
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    if minutes < 60:
        return '{:02d}:{:02d}'.format(minutes, secs)
    hours = minutes // 60
    minutes = minutes % 60
    return '{:d}:{:02d}:{:02d}'.format(hours, minutes, secs)


def progress(iterable, desc=None, total=None):
    """便捷函数：返回带进度条的可迭代对象"""
    return ProgressBar(iterable=iterable, desc=desc, total=total)

`````

--- **end of file: nb_cmd/ui/progress.py** (project: nb_cmd) --- 

---


--- **start of file: nb_cmd/ui/table.py** (project: nb_cmd) --- 

`````python
# -*- coding: utf-8 -*-
"""
纯标准库的表格输出，支持 CJK 字符对齐。
"""
import sys


def _write(text):
    sys.stdout.write(text + '\n')
    sys.stdout.flush()


def _display_width(text):
    width = 0
    for ch in str(text):
        code = ord(ch)
        if (0x4E00 <= code <= 0x9FFF) or (0x3400 <= code <= 0x4DBF) or \
           (0xF900 <= code <= 0xFAFF) or (0xFF00 <= code <= 0xFFEF) or \
           (0x3000 <= code <= 0x303F):
            width += 2
        else:
            width += 1
    return width


def _pad(text, width):
    text = str(text)
    dw = _display_width(text)
    return text + ' ' * max(0, width - dw)


def print_table(data, headers=None):
    """
    将 list[dict] 或 list[list] 格式化为表格输出。

    Parameters
    ----------
    data : list[dict] 或 list[list]
    headers : list[str], optional
    """
    if not data:
        _write('(空)')
        return

    if isinstance(data[0], dict):
        if headers is None:
            headers = list(data[0].keys())
        rows = [[row.get(h, '') for h in headers] for row in data]
    else:
        if headers is None:
            headers = ['列{}'.format(i + 1) for i in range(len(data[0]))]
        rows = data

    col_widths = [_display_width(str(h)) for h in headers]
    for row in rows:
        for i, val in enumerate(row):
            w = _display_width(str(val))
            if w > col_widths[i]:
                col_widths[i] = w

    top = '┌' + '┬'.join('─' * (w + 2) for w in col_widths) + '┐'
    mid = '├' + '┼'.join('─' * (w + 2) for w in col_widths) + '┤'
    bot = '└' + '┴'.join('─' * (w + 2) for w in col_widths) + '┘'

    header_line = '│ ' + ' │ '.join(_pad(str(h), col_widths[i]) for i, h in enumerate(headers)) + ' │'

    _write(top)
    _write(header_line)
    _write(mid)
    for row in rows:
        line = '│ ' + ' │ '.join(_pad(str(row[i]) if i < len(row) else '', col_widths[i]) for i in range(len(headers))) + ' │'
        _write(line)
    _write(bot)


def print_kv(data):
    """
    键值对格式化输出。

    Parameters
    ----------
    data : dict
    """
    if not data:
        return

    max_key_width = max(_display_width(str(k)) for k in data.keys())

    for key, value in data.items():
        padded_key = _pad(str(key), max_key_width)
        _write('{}:  {}'.format(padded_key, value))

`````

--- **end of file: nb_cmd/ui/table.py** (project: nb_cmd) --- 

---


--- **start of file: nb_cmd/ui/__init__.py** (project: nb_cmd) --- 

`````python

`````

--- **end of file: nb_cmd/ui/__init__.py** (project: nb_cmd) --- 

---


--- **start of file: nb_cmd/utils/config.py** (project: nb_cmd) --- 

`````python
# -*- coding: utf-8 -*-
"""
参数持久化模块 —— 自动保存/恢复上一次执行的参数。
"""
import json
import os


class ConfigManager(object):
    """管理参数持久化到 JSON 文件"""

    def __init__(self, config_file=None):
        if config_file:
            self.config_file = os.path.expanduser(config_file)
        else:
            self.config_file = None
        self._data = {}
        if self.config_file:
            self._load()

    def _load(self):
        if self.config_file and os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self._data = json.load(f)
            except Exception:
                self._data = {}

    def save_args(self, command, kwargs):
        """保存命令的参数"""
        if not self.config_file:
            return
        serializable = {}
        for k, v in kwargs.items():
            try:
                json.dumps(v)
                serializable[k] = v
            except (TypeError, ValueError):
                serializable[k] = str(v)
        self._data[command] = serializable
        self._write()

    def load_args(self, command):
        """加载命令上次保存的参数"""
        return self._data.get(command, {})

    def _write(self):
        if not self.config_file:
            return
        dir_path = os.path.dirname(self.config_file)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

`````

--- **end of file: nb_cmd/utils/config.py** (project: nb_cmd) --- 

---


--- **start of file: nb_cmd/utils/validators.py** (project: nb_cmd) --- 

`````python
# -*- coding: utf-8 -*-
"""
参数校验装饰器。
"""
import functools


def validate(**validators):
    """
    参数校验装饰器。
    每个关键字参数是一个 lambda/callable，接收参数值，返回 True/False。

    示例::

        @validate(port=lambda x: 1 <= x <= 65535)
        def deploy(self, host: str, port: int = 22):
            ...

    校验失败时抛出 ValueError。
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            import inspect
            sig = inspect.signature(func)
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()

            for param_name, check_fn in validators.items():
                if param_name in bound.arguments:
                    value = bound.arguments[param_name]
                    if not check_fn(value):
                        raise ValueError(
                            '参数 {} 校验失败 (当前值: {})'.format(param_name, value)
                        )
            return func(*args, **kwargs)
        return wrapper
    return decorator

`````

--- **end of file: nb_cmd/utils/validators.py** (project: nb_cmd) --- 

---


--- **start of file: nb_cmd/utils/__init__.py** (project: nb_cmd) --- 

`````python

`````

--- **end of file: nb_cmd/utils/__init__.py** (project: nb_cmd) --- 

---

