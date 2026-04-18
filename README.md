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

**Web UI 界面预览：**

![Web UI 主界面](https://raw.githubusercontent.com/ydf0509/nb_cmd/main/docs/images/web_ui_main.png)

执行命令后，右侧实时显示彩色日志输出、结果数据和命令历史：

![Web UI 执行输出](https://raw.githubusercontent.com/ydf0509/nb_cmd/main/docs/images/web_ui_output.png)

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
