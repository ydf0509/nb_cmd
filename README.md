# nb_cmd

**Python 码农的低代码平台** —— 写一个 class，自动获得 CLI + REST API + Web UI + Python 直接调用 四种接口。不写路由、不写前端、不写文档，全自动。

[![Python](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

## why nb_cmd?

为什么要用nb_cmd?nb_cmd是不是装逼？是不是重复造轮子？抛开nb_cmd自带低代码平台的气质，只看命令行最本质的功能本身，比较下nb_cmd对其他顶流命令行框架的碾压优势。

> 详细的多维度对比（含多层级子命令 + 全局参数的完整代码对比）请看：[nb_cmd vs click vs typer vs fire](https://github.com/ydf0509/nb_cmd/blob/main/nb_cmd_vs_click_vs_typer.md)

## 目录

- [为什么用 nb_cmd？](#为什么用-nb_cmd)
- [核心价值与典型场景](#核心价值与典型场景)
- [安装](#安装)
- [5 分钟快速上手](#5-分钟快速上手)
- [核心特性](#核心特性)
- [完整 API 速查](#完整-api-速查)
- [和竞品对比](#和竞品对比)
- [项目结构](#项目结构)

---

## 为什么用 nb_cmd？

现有 CLI 框架（argparse / click / typer / fire）只解决了一件事：**怎么方便地定义 CLI 参数**。

但实际开发中，你一定遇到过：

- 你写了一个 CLI 工具 → 产品说"加个 Web 页面"
- 你写了一个 CLI 工具 → 运维说"要通过 API 远程调用"
- 你写了一个 CLI 工具 → 老板说"能让不懂命令行的人也能用吗"

**每次都是重写。**

nb_cmd 换了一种思路：**Class 是中心，接口是投影。**

```
             ┌── CLI 模式（默认）
             │
业务逻辑(class) ─┼── REST API 模式（自动 Swagger）
             │
             └── Web UI 模式（自动生成页面）
```

写一次业务逻辑，四种接口自动生成，不改一行代码。

**你写什么 → 你得到什么：**

| 你写的 | 自动获得 |
|--------|----------|
| 方法签名 `def deploy(self, host: str, port: int = 22)` | CLI 参数 + API 端点 + Web 表单（输入框/数字框/复选框） |
| 方法的 docstring `"""部署到远程服务器"""` | CLI --help + Swagger 文档 + Web UI 描述 |
| 类型注解 `env: Environment`（Enum） | CLI choices + API 校验 + Web 下拉选择 |
| `print()` / `cmdui.table()` | CLI 终端输出 + Web 实时流式推送（WebSocket + ANSI 彩色渲染） |
| `sub_commands = {'git': GitTool}` | CLI 多级子命令 + API 嵌套路由 + Web UI 折叠分组 |
| `CmdGen(MyApp).doc(file='cli.md')` | **自动生成带 TOC + 参数表格 + 可复制命令行的 Markdown 文档** |
| `MyTool().greet('张三', 3)` | **方法就是普通 Python 方法，随时直接调用、单元测试、import 复用** |

**不需要写的：** 路由定义、Pydantic 模型、HTML 表单、CSS 样式、JavaScript 交互、WebSocket 端点、Swagger 注解、前后端联调、**CLI 使用文档**。

> **零装饰器，方法可直接调用：** click/typer 的装饰器把函数变成了 `click.Command` 对象，无法直接 `greet('张三', 3)` 调用——必须用 `CliRunner().invoke()` 模拟 CLI 或自己拆两层。nb_cmd 的方法始终是普通的 Python 类方法，`MyTool().greet('张三', 3)` 直接就能跑，IDE 补全、断点调试、单元测试全部正常。

> **文档生成吊打 `--help`：** 传统框架的文档止步于 `--help` 纯文本，click 需要第三方 `sphinx-click`，typer 只是搬运 `--help` 输出。nb_cmd 的 `CmdGen` 一行代码生成完整的 Markdown 文档——自动目录、参数表格、默认值/必填标注、可复制的 bash 命令行模板，测试人员拿到直接能用。[查看示例](https://github.com/ydf0509/nb_cmd/blob/main/examples/nbctx_demo/nbctx_demo_gen_doc.md)

| 功能 | argparse | click | typer | fire | **nb_cmd** |
|------|:--------:|:-----:|:-----:|:----:|:----------:|
| 零配置 | ✗ | ✗ | 部分 | ✓ | **✓** |
| 类型驱动 | 手动 | 手动 | ✓ | ✗ | **✓** |
| OOP 继承/覆写 | ✗ | ✗ | ✗ | 有限 | **✓** |
| 自动生成 REST API | ✗ | ✗ | ✗ | ✗ | **✓** |
| 自动生成 Web UI | ✗ | ✗ | ✗ | ✗ | **✓** |
| 多层级子命令 | 手动 | ✓ | ✓ | 有限 | **✓** |
| Swagger 文档 | ✗ | ✗ | ✗ | ✗ | **✓** |
| 进度条/表格/彩色 | ✗ | ✓ | ✓(rich) | ✗ | **✓** |
| 自动生成 CLI 文档 | ✗ | 第三方 | 基础 | ✗ | **✓（Markdown+表格+TOC+可复制命令行）** |
| 方法可直接调用 | ✓ | ✗ | ✗ | ✓ | **✓（零装饰器，普通类方法）** |

---

## 核心价值与典型场景

### 打破企业内部工具开发的"死循环"

在企业开发中，经常遇到这样的困境：

```
产品经理："这个工具不是公司核心业务，不立项"
    ↓
前端码农："没立项就没有需求排期，我不开发"
    ↓
Python 码农："我会写逻辑，但不会写前端"
    ↓
结果：工具永远停留在 CLI，只有技术人员能用
    ↓
测试/运营/产品："能不能给我们也用用？"
    ↓
Python 码农："等我学学 Vue/React..."（然后就没有然后了）
   ↓
最终：工具被遗忘，需求依然存在，问题继续存在
```

**nb_cmd 打破了这个死循环：**

```
Python 码农：写一个 class（30分钟）
    ↓
nb_cmd：自动生成 cli  + API +  Web UI
    ↓
测试/运营/产品：直接用网页操作
    ↓
前端人员：完全不需要介入！
```

### 效率对比

**传统方式的成本：**
```
需求沟通：2小时
前端开发：2-3天
前后端联调：1天
测试：0.5天
总计：约 4-5 天
```

**用 nb_cmd 的成本：**
```
写 Python class：1小时
启动 Web 模式：1分钟
总计：约 1 小时
```

**效率提升：40-50 倍！**

### 零成本优势

#### 1. 零前端成本
- 不需要懂 HTML/CSS/JavaScript
- 不需要学 Vue/React/Angular
- 不需要配置 webpack/vite
- 不需要处理前后端联调

#### 2. 零立项成本
- 产品经理不需要评估 ROI
- 不需要排期会议
- 不需要跨部门协调
- Python 码农自己就能搞定

#### 3. 零学习成本（对使用者）
- 测试人员：打开网页，填表单，点按钮
- 产品经理：看到的是专业的 UI，不是黑乎乎的命令行
- 运维人员：可以用 API 集成到自动化流程

### 典型应用场景

- **数据处理** — 导入 Excel、导出报表，测试和产品经理自己就能跑
- **测试辅助** — 创建测试用户、清理测试数据，测试人员自助操作
- **运维管理** — 重启服务、检查状态，运维用 API 集成到监控告警
- **配置管理** — 更新配置、查看配置，运营人员不用找开发

每个场景只需写一个 NbCmd 子类，`--web` 启动后发给团队即可使用。

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

## nb_cmd 网页截图

> `nb_cmd` 只要你写了一个继承 `NbCmd` 的类，就自动生成 FastAPI 接口和接口文档，自动生成前端输入框和按钮。让你只写普通的类，无需接触 Web 后端接口开发，更无需接触前端界面开发，更无需接触 WebSocket 实时输出——你的方法中的任何普通的日志和 `print` 都会自动实时推送到 Web 前端页面上。

![nb_cmd 网页截图](https://github.com/ydf0509/nb_cmd/blob/main/docs/images/nb_cmd_web.png)

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
  --cmd-version        show program's version number and exit
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

- `http://localhost:8080` → **Web UI**：左侧是命令输入 + 收藏/历史搜索 + 参数表单，右侧是实时控制台输出，中间分割条可自由拖动
- `http://localhost:8080/docs` → **Swagger 文档**：所有命令自动生成 REST API

**Web UI 主要功能：**

- 命令行直接输入任意命令（非 NbCmd 命令自动通过 `exec` 执行）
- 参数表单自动生成（根据方法签名推导控件类型）
- WebSocket 实时流式输出（支持 ANSI 彩色渲染）
- 长时间命令可随时取消（停止按钮，类似 Ctrl+C）
- 命令收藏 + 执行历史（SQLite 持久化，Select2 风格弹框搜索）

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
| 无默认值的参数 | 位置参数（必填）；有短别名时为 `--flag`（必填） | `name: str` → `greet 张三`；`name: Annotated[str, '', 'n']` → `-n 张三` |
| 有默认值的参数 | 可选参数（`--xxx`） | `port: int = 22` → `--port 2222` |
| `bool` 类型 | 开关参数（`--flag`） | `verbose: bool = False` → `--verbose` |
| `int` / `float` 类型 | 自动类型转换和校验 | 输入非数字会报错 |
| `Enum` 类型 | 自动生成选择项 | `env: Environment` → `{dev,staging,prod}` |
| `Annotated[type, desc, alias]` | 参数描述 + 短别名 | `name: Annotated[str, '用户名', 'n']` → `-n` |
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

#### 方法可直接调用——零装饰器设计

click/typer 的装饰器会把函数**变成 `click.Command` 对象**，你无法像普通函数一样调用它：

```python
# click —— 装饰器改变了函数本质
@click.command()
@click.argument('name')
@click.option('--times', default=1)
def greet(name, times):
    print(f'Hello, {name}!')

greet('张三', 3)  # TypeError! greet 已经不是普通函数了
# 必须绕路：CliRunner().invoke(greet, ['张三', '--times', '3'])
# 或者自己拆两层：_greet_impl() + @click.command() 包一层
```

nb_cmd 的方法始终是**普通的 Python 类方法**，框架只在 `run()` 时通过反射发现它们：

```python
# nb_cmd —— 就是普通方法，零装饰器
class MyTool(NbCmd):
    def greet(self, name: str, times: int = 1):
        for _ in range(times):
            print(f'Hello, {name}!')

# 直接调用 —— 完全OK
MyTool().greet('张三', 3)

# 当 CLI 用 —— 也OK
MyTool().run()  # python script.py greet --name 张三 --times 3

# import 到别的模块 —— 也OK
from my_tool import MyTool
result = MyTool().greet('张三', 3)
```

**这意味着：** 你的业务逻辑（方法）永远可以直接调用、单元测试、import 复用，不被 CLI 框架绑架。

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

启动 Web 模式后，用 curl 调用多层级子命令：

```bash
# 启动 Web UI + REST API
$ python git_tool.py --web --web-port 8080

# 一级命令：POST /status（无参数）
$ curl -X POST http://localhost:8080/status

# 一级命令带参数：POST /commit
$ curl -X POST http://localhost:8080/commit \
    -H "Content-Type: application/json" \
    -d '{"message": "fix bug", "all": true}'

# 二级命令（子命令组）：POST /remote/add
$ curl -X POST http://localhost:8080/remote/add \
    -H "Content-Type: application/json" \
    -d '{"name": "origin", "url": "https://github.com/user/repo.git"}'

# 二级命令：POST /remote/remove
$ curl -X POST http://localhost:8080/remote/remove \
    -H "Content-Type: application/json" \
    -d '{"name": "origin"}'
```

> **路由规则：** 一级命令路由为 `/{command}`，子命令组中的命令路由为 `/{group}/{sub_command}`，与 CLI 的层级结构一一对应。所有接口在 Swagger 文档 `http://localhost:8080/docs` 中可查看。

在 Web UI 中，子命令组以蓝色标题 `[组]` 展示，展开后列出每个子命令的参数表单。

#### 组合多个 NbCmd 类为统一入口

已有的多个 NbCmd 类可以通过 `sub_commands` 组合成一个"大一统"工具，共享同一个 Web UI / API 入口：

```python
from nb_cmd import NbCmd

class MyTool(NbCmd):
    """基础工具"""
    def greet(self, name: str, times: int = 1):
        """问好"""
        for _ in range(times):
            print('你好, {}!'.format(name))

class DeployTool(NbCmd):
    """部署工具"""
    def deploy(self, host: str, port: int = 22):
        """部署"""
        print('部署到 {}:{}'.format(host, port))

    def status(self):
        """查看状态"""
        print('当前状态: 运行中')

class OneAllTool(NbCmd):
    """综合工具，在一个网页运行所有NbCmd其他类"""

    sub_commands = {
        'mytool': MyTool,
        'deploy-tool': DeployTool,
    }

if __name__ == '__main__':
    OneAllTool().run()
```

```bash
# CLI 用法
$ python bigone.py mytool greet 张三 --times 3
$ python bigone.py deploy-tool deploy web-01 --port 2222
$ python bigone.py deploy-tool status
```

启动 Web 模式后，所有子类的命令统一暴露为 REST API：

```bash
$ python bigone.py --web --web-port 8025

# mytool 组的 greet 命令
$ curl -X POST http://localhost:8025/mytool/greet \
    -H "Content-Type: application/json" \
    -d '{"name": "张三", "times": 3}'

# deploy-tool 组的 deploy 命令
$ curl -X POST http://localhost:8025/deploy-tool/deploy \
    -H "Content-Type: application/json" \
    -d '{"host": "web-01", "port": 2222}'

# deploy-tool 组的 status 命令（无参数）
$ curl -X POST http://localhost:8025/deploy-tool/status
```

> 这样可以把团队中各个人写的 NbCmd 类"插拔式"地组合到一个统一入口，Web UI 中每个组独立折叠展示。

#### sub_commands 支持传入实例

如果子类的 `__init__` 有必填参数，直接传 class 会因为无法无参实例化而报错。此时可以传入**实例**，nb_cmd 会自动提取 init 参数用于后续重建实例：

```python
from typing import Annotated

from nb_cmd import NbCmd

class ServerTool(NbCmd):
    def __init__(self, region: Annotated[str, '机房区域']):
        super().__init__()
        self.region = region

    def stats(self):
        print('区域: {}'.format(self.region))

class OneAllTool(NbCmd):
    sub_commands = {
        'mytool': MyTool,                    # 传 class（无 __init__ 参数）
        'server': ServerTool('beijing'),     # 传实例（有 __init__ 参数）
    }
```

> `sub_commands` 的 value 可以是 **class** 或 **instance**。传 instance 时，nb_cmd 从实例上提取 init 参数值，Web/API 模式下每次请求仍会新建隔离实例。

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

### 5. Annotated 参数描述

用 `typing.Annotated` 为参数添加描述和短别名，CLI `--help`、Web UI 输入框、Swagger 文档会同步显示：

```python
from typing import Annotated

from nb_cmd import NbCmd

class MyTool(NbCmd):
    """部署工具"""

    def deploy(self, host: Annotated[str, '服务器地址', 'H'],
               port: Annotated[int, '端口号', 'p'] = 22,
               verbose: Annotated[bool, '详细模式', 'v'] = False):
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

`Annotated` 的元数据是渐进式的——描述与短别名可选，不影响原有的 `name: str` 写法：

```python
name: str                                    # 最简写法，完全兼容
name: Annotated[str, '用户名']               # 加描述
name: Annotated[str, '用户名', 'n']          # 加描述 + 短别名
name: Annotated[str, '', 'n']                # 只加短别名
```

也可以用 `Param` 对象获得关键字参数风格（IDE 可补全字段名）：

```python
from nb_cmd import Param

name: Annotated[str, Param(desc='用户名', alias='n')]
port: Annotated[int, Param(desc='端口号')] = 22
```

> `Param(desc, alias)` 和位置字符串完全等价。Web UI 中，描述会显示在输入框旁边的灰色提示文字和 placeholder 中。

### 6. 全局参数（`__init__` 参数）

当多个子命令需要共享上下文（如机房区域、数据库连接、超时时间），把它们放到 `__init__` 中：

```python
from typing import Annotated
from enum import Enum

from nb_cmd import NbCmd, NbCmdMeta, cmdui

class Environment(Enum):
    DEV = "dev"
    STAGING = "staging"
    PROD = "prod"

class ServerTool(NbCmd):
    """服务器运维工具"""

    class Meta(NbCmdMeta):
        version = "1.0.0"
        use_nb_log = True

    def __init__(self, region: Annotated[str, '机房区域', 'r'],
                 timeout: Annotated[int, '超时秒数'] = 30):
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
  --cmd-version        show program's version number and exit
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

> **Web UI 智能路由：** 在 Web UI 的命令输入框中，输入非 NbCmd 命令（如 `python script.py`、`docker ps`、`ls -la`）会自动通过 `exec` 执行，无需手动加 `exec` 前缀。

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
| `version` | str | `'0.0.1'` | 版本号（`--cmd-version` 显示） |
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
| `enable_exec` | bool | `True` | 是否暴露内置 `exec` 命令（设为 `False` 可防止恶意执行系统命令） |
| `aliases` | dict | `{}` | 参数别名（推荐用 `Annotated[..., 'desc', 'a']` 指定短别名替代） |

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
    --cmd-version            显示版本号
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

### 12. 自动文档生成（CmdGen）—— 吊打 `--help`

传统 CLI 框架的文档能力止步于 `--help`：一段纯文本，不能复制、不能跳转、不能分享。即使 typer 有 `typer utils docs`，也只是把 `--help` 搬到 Markdown 里而已。

nb_cmd 的 `CmdGen` 是真正的**面向用户的 API 文档生成器**——自动生成带 TOC 目录、参数表格、可复制命令行、占位符约定的**高质量 Markdown 文档**，测试人员和运维人员拿到就能直接用。

```python
from nb_cmd import CmdGen

g = CmdGen(MyApp, script='my_tool.py')

# 生成单个命令的可复制命令行
print(g.cmd(DbTool.migrate))
# python my_tool.py --region ${beijing} --env ${prod} --debug db migrate --dry-run

# 一键生成完整 Markdown 文档到文件
g.doc(file='docs/cli_reference.md')
```

**生成的 Markdown 包含：**

| 区域 | 内容 |
|------|------|
| 标题 + 版本 | `# cloud-tool v1.0.0` |
| Table of Contents | 自动递归生成，支持多层级子命令组，可点击跳转 |
| System Params | 系统参数表格（`-h` / `-fh` / `--web` 等） |
| Global Params | 全局参数表格（类型 + 默认值 + 描述） |
| Quick Start | 三条最常用命令（查看帮助/版本/启动 Web） |
| 命令行约定 | `${value}` / `$<required>` / `--flag` 含义说明 |
| 每个命令 | 标题 + 描述 + 参数表格 + 可复制 `bash` 代码块 |

**vs 其他框架的文档能力：**

| 功能 | click | typer | nb_cmd `CmdGen` |
|------|-------|-------|-----------------|
| 终端 `--help` | 有 | 有（Rich） | 有（三级帮助系统） |
| 自动生成 Markdown | 需第三方 `sphinx-click` | 基础版（搬运 `--help`） | **完整版（表格+TOC+代码块）** |
| 可复制命令行模板 | ✗ | ✗ | **✓** `${default}` / `$<required>` |
| 参数表格（类型/默认/描述） | ✗ | ✗ | **✓** 每个命令自动生成 |
| 单命令示例生成 | ✗ | ✗ | **✓** `g.cmd(DbTool.migrate)` |
| 一键写入文件 | ✗ | ✗ | **✓** `g.doc(file='xxx.md')` |
| 智能格式路由 | ✗ | ✗ | **✓** `.md` 文件自动用 Markdown 格式 |

> 完整示例见 [examples/nbctx_demo/nbctx_demo_gen_doc.md](https://github.com/ydf0509/nb_cmd/blob/main/examples/nbctx_demo/nbctx_demo_gen_doc.md)

### 13. Web UI 交互特性

以下功能在 `--web` 模式下自动可用，无需额外配置：

| 功能 | 说明 |
|------|------|
| 实时流式输出 | WebSocket 推送，print() 实时显示在控制台，支持 ANSI 彩色渲染 |
| 命令取消 | 长时间运行的命令可点击"停止"按钮随时取消（类似 Ctrl+C），执行中"执行"按钮自动置灰 |
| 命令收藏 | 点击 ★ 按钮将常用命令保存到 SQLite，自动去重 |
| 执行历史 | 每次执行自动记录到 SQLite，保留最近 1000 条 |
| Select2 搜索 | 收藏和历史各有独立的 Select2 风格弹框，支持模糊搜索、键盘导航，点击即填入命令行 |
| 智能路由 | 命令行输入非 NbCmd 命令时自动通过 exec 执行，可直接输入 `python xxx.py`、`docker ps` 等 |
| 参数表单 | 根据方法签名自动推导控件（文本框、数字框、复选框、下拉选择等） |
| 可拖拽布局 | 左右面板中间的分割条可自由拖动调整比例 |

---

## 完整 API 速查

### 导入

```python
from typing import Annotated
from nb_cmd import NbCmd, NbCmdMeta, Param, cmdui, validate, CmdGen
```

### CmdGen（自动文档生成）

```python
from nb_cmd import CmdGen

g = CmdGen(entry_cls, script='app.py', python='python', fmt='text')
```

| 方法 | 说明 |
|------|------|
| `CmdGen(cls, script, python, fmt)` | 创建生成器。`fmt`: `'text'` / `'markdown'` |
| `g.cmd(Method)` | 生成单个方法的可复制 CLI 命令行 |
| `g.doc()` | 生成完整文档字符串 |
| `g.doc(file='path.md')` | 生成完整文档并写入文件（`.md` 自动用 Markdown 格式） |

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

### Annotated 参数描述

两种等价写法：

**位置字符串：** `Annotated[类型, '描述', '别名']`

| 位置 | 必填 | 说明 |
|------|------|------|
| 第一个参数（类型） | 是 | 实际参数类型（`str`, `int`, `bool`, `Enum`, `List[str]` 等） |
| 第二个参数（字符串） | 否 | 参数描述（`--help`、Web UI placeholder、Swagger 同步显示） |
| 第三个参数（字符串） | 否 | 短别名（`'n'` → `-n`，`'host-name'` → `--host-name`） |

**Param 对象：** `Annotated[类型, Param(desc='描述', alias='别名')]`

| 参数 | 必填 | 说明 |
|------|------|------|
| `desc` | 否 | 参数描述 |
| `alias` | 否 | 短别名 |

---

## 和竞品对比

> 详细的多维度对比（含多层级子命令 + 全局参数的完整代码对比）请看：[nb_cmd vs click vs typer vs fire](https://github.com/ydf0509/nb_cmd/blob/main/nb_cmd_vs_click_vs_typer.md)

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

**nb_cmd（写一次，四种接口）：**

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

### vs 传统前后端开发

传统方式：**写后端 → 写接口 → 写文档 → 写前端 → 联调**，5 步缺一不可。nb_cmd 方式：只写 class，其余自动生成。

| 能力 | 传统方式 | nb_cmd |
|------|---------|--------|
| REST API（含 Swagger） | 手写路由 + 模型 | **方法签名自动生成** |
| Web UI（表单 + 控件） | 手写 HTML/CSS/JS | **类型注解自动推导控件** |
| WebSocket 实时输出 | 手写 WS 端点 + 前端接收 | **print() 自动流式推送** |
| 命令行 CLI | 另写 argparse | **同一份代码** |
| 文档同步 | 手动维护 | **永远一致（同一个类）** |
| 新增 1 个参数 | 改 3 处（后端/前端/文档） | **改 1 处（方法签名）** |
| 前端开发者 | 需要 | **不需要** |

> **本质区别：** 传统开发是"手动映射"——后端定义接口，前端照着文档手写表单；nb_cmd 是"自动投影"——Python 类是唯一真相源，CLI/API/Web UI/Python 直接调用 是它的四个不同维度的影子。改真相源，影子自动跟着变。

---

## 项目结构

```
nb_cmd/
├── __init__.py            # 统一导出（from nb_cmd import ...）
├── core/
│   ├── base.py            # NbCmd 基类
│   ├── meta.py            # NbCmdMeta 配置基类
│   ├── arg.py             # Annotated / Param 参数元数据解析
│   ├── discovery.py       # 命令发现（反射 + 类型检查）
│   ├── parser.py          # argparse 解析器构建
│   ├── type_utils.py      # 类型工具（Enum/Optional/List 等）
│   ├── gen_cmd.py         # CmdGen 自动文档/命令行示例生成器
│   ├── result_handler.py  # 返回值自动处理
│   └── _io_dispatch.py    # 线程安全的 stdout/stderr 分发器
├── modes/
│   ├── cli_mode.py        # CLI 执行引擎
│   ├── api_mode.py        # REST API 路由生成（FastAPI）
│   └── web_mode.py        # Web UI 页面生成 + WebSocket 实时输出
├── ui/
│   ├── helper.py          # UIHelper（cmdui 单例）
│   ├── colors.py          # ANSI 彩色输出
│   ├── table.py           # 表格 / 键值对输出
│   └── progress.py        # 进度条
└── utils/
    ├── validators.py      # @validate 装饰器
    └── config.py          # 配置持久化
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
