# Git 命令行工具 — Click vs nb_cmd 实现对比

## 概述

本目录用 **Click** 和 **nb_cmd** 两种框架分别实现了 Git 部分命令，重点演示三个核心特性：

| 特性 | 说明 |
|------|------|
| **全局传参** | `--verbose` / `-v` 和 `--path` / `-C` 两个全局参数穿透到所有子命令 |
| **多层级子命令** | `remote`、`branch`（二级），`config → user`（三级） |
| **深层子命令使用全局参数** | `config user name/email` 读取全局 `--path` 和 `--verbose` |

---

## 文件说明

| 文件 | 框架 | 装饰器数 |
|------|------|---------|
| `git_click.py` | Click | 18 个 |
| `git_nb_cmd.py` | nb_cmd | **0 个** |

---

## 命令结构

```
git-tool
├── --verbose / -v          # 全局参数：详细输出
├── --path / -C             # 全局参数：工作目录路径
│
├── status                  # 一级命令
├── log [--oneline] [--graph] [-n]   # 一级命令
│
├── remote                  # 二级子命令组
│   ├── add <name> <url>
│   ├── remove <name>
│   └── show [name]
│
├── branch                  # 二级子命令组
│   ├── create <name> [--from-branch]
│   ├── delete <name> [--force]
│   └── list [--merged]
│
└── config                  # 二级子命令组
    └── user                # 三级深层子命令组
        ├── name [value]    ← 使用全局 --path 和 --verbose
        └── email [value]   ← 使用全局 --path 和 --verbose
```

---

## 全局传参方式对比

### Click：`@click.pass_context` + `ctx.obj` 字典

```python
@click.group()
@click.option('--verbose', '-v', is_flag=True)
@click.option('--path', '-C', default='.')
@click.pass_context
def cli(ctx, verbose, path):
    ctx.ensure_object(dict)
    ctx.obj.update(verbose=verbose, path=path)

# 每个子命令都要加 @click.pass_context
@remote.command('add')
@click.argument('name')
@click.argument('url')
@click.pass_context
def remote_add(ctx, name, url):
    c = ctx.obj          # 字典取值，无 IDE 补全
    if c['verbose']:     # 字符串 key，拼写错误无提示
        ...
```

**痛点：**
- 每个子命令都要加 `@click.pass_context` 装饰器
- 取值靠 `ctx.obj['key']`（字符串键，无 IDE 补全，拼写错误运行时才暴露）
- 装饰器随层级指数叠加：三级子命令 `config user name` 需要 4 个装饰器

### nb_cmd：`__init__` + `self.nbctx` 强类型属性

```python
@dataclass
class GitCtx:
    verbose: bool = False
    path: str = '.'

class GitTool(NbCmd):
    nbctx: GitCtx

    def __init__(self, verbose: bool = False, path: str = '.'):
        self.nbctx = GitCtx(verbose=verbose, path=path)

    sub_commands = {'remote': RemoteCmd, 'branch': BranchCmd, 'config': ConfigCmd}

# 子命令组中直接通过 self.nbctx 访问
class RemoteCmd(NbCmd):
    nbctx: GitCtx

    def add(self, name: str, url: str):
        if self.nbctx.verbose:    # 强类型属性，IDE 自动补全
            print(self.nbctx.path)
```

**优势：**
- 零装饰器：`__init__` 即全局参数定义
- `self.nbctx.verbose` 强类型访问，IDE 自动补全 + 跳转
- 框架自动 `child.nbctx = parent.nbctx` 递归传递，任意嵌套深度无需额外代码

---

## 多层级子命令定义对比

### Click：装饰器嵌套

```python
# 二级：@cli.group()
@cli.group()
@click.pass_context
def remote(ctx): pass

@remote.command('add')
@click.pass_context
def remote_add(ctx, name, url): ...

# 三级：@cli.group() → @config.group()
@cli.group()
@click.pass_context
def config(ctx): pass

@config.group()
@click.pass_context
def user(ctx): pass

@user.command('name')
@click.pass_context
def user_name(ctx, value): ...
```

**痛点：**
- 每新增一个子命令组需要 `@cli.group()` + 函数定义
- 装饰器用错实例（如 `@remote.command()` 写成 `@branch.command()`），命令跑到错误层级，不报错但行为异常
- 函数散落各处，层级关系靠装饰器维持，代码可读性差

### nb_cmd：`sub_commands` 字典

```python
class GitTool(NbCmd):
    sub_commands = {
        'remote': RemoteCmd,    # 二级
        'branch': BranchCmd,    # 二级
        'config': ConfigCmd,    # 二级 → 三级
    }

class ConfigCmd(NbCmd):
    sub_commands = {
        'user': UserConfigCmd,  # 三级
    }

class UserConfigCmd(NbCmd):
    def name(self, value=None): ...   # 三级子命令
    def email(self, value=None): ...  # 三级子命令
```

**优势：**
- 子命令组是独立 Class，层级关系一目了然
- 新增子命令组只需：写一个 Class + 在父级 `sub_commands` 加一项
- 子命令组可单独实例化、单独测试、单独复用

---

## 深层子命令使用全局参数

### Click 版（`config user name` 使用 `--path`）

```python
@user.command('name')
@click.argument('value', required=False, default=None)
@click.pass_context
def user_name(ctx, value):
    c = ctx.obj
    work_path = c['path']               # 从 ctx.obj 取全局参数
    if c['verbose']:                    # 从 ctx.obj 取全局参数
        print(f'详细模式: 工作目录={work_path}')
    print(f'git -C {work_path} config user.name "{value}"')
```

### nb_cmd 版（`config user name` 使用 `--path`）

```python
class UserConfigCmd(NbCmd):
    nbctx: GitCtx

    def name(self, value: str = None):
        work_path = self.nbctx.path     # 强类型属性访问
        if self.nbctx.verbose:          # 强类型属性访问
            print(f'详细模式: 工作目录={work_path}')
        print(f'git -C {work_path} config user.name "{value}"')
```
**关键差异：** nb_cmd 的 `self.nbctx` 由框架自动从父级传递到子级，`UserConfigCmd` 不需要任何额外代码就能拿到全局参数。Click 需要每层都加 `@click.pass_context` 并手动从 `ctx.obj` 取值。

---

## 运行示例

```bash
# 1. 查看状态（带全局参数）
python git_click.py --verbose status
python git_nb_cmd.py --verbose status

# 2. 添加远程仓库（指定工作目录）
python git_click.py -C /etc/git remote add origin https://github.com/user/repo.git
python git_nb_cmd.py -C /etc/git remote add origin https://github.com/user/repo.git

# 3. 创建分支（详细模式）
python git_click.py --verbose branch create feature/login --from-branch develop
python git_nb_cmd.py --verbose branch create feature/login --from-branch develop

# 4. 深层子命令：设置用户名（使用全局 -C）
python git_click.py -C ~/my-config config user name "John Doe"
python git_nb_cmd.py -C ~/my-config config user name "John Doe"

# 5. 深层子命令：查询邮箱（使用全局 --verbose）
python git_click.py --verbose config user email
python git_nb_cmd.py --verbose config user email

# 6. 查看帮助
python git_click.py --help
python git_nb_cmd.py --help

python git_click.py remote --help
python git_nb_cmd.py remote --help

python git_click.py config user --help
python git_nb_cmd.py config user --help
```

---

## 总结

| 维度 | Click | nb_cmd |
|------|-------|--------|
| **全局参数定义** | `@click.group()` + `@click.option()` | `__init__` 方法参数 |
| **全局参数传递** | `@click.pass_context` + `ctx.obj['key']` | `self.nbctx.attr` 自动穿透 |
| **子命令组定义** | `@cli.group()` 装饰器嵌套 | `sub_commands = {...}` 字典 |
| **深层子命令** | 每层都要 `@group()` + `@pass_context` | 框架自动递归传递 `nbctx` |
| **IDE 补全** | ❌ `ctx.obj['key']` 无补全 | ✅ `self.nbctx.attr` 强类型补全 |
| **独立测试** | ❌ 函数绑定到 `cli` 实例 | ✅ Class 可单独实例化测试 |
| **装饰器数量** | 18 个 | **0 个** |
| **代码可读性** | 装饰器散落，层级关系隐式 | Class 嵌套，层级关系显式 |

**结论：** 对于多层级子命令 + 全局参数的 CLI 工具，nb_cmd 的 OOP 设计（`__init__` 定义全局参数、`sub_commands` 声明层级、`self.nbctx` 自动穿透）比 Click 的函数式 + 装饰器方案更简洁、更可维护、更易测试。