---
name: devops-tool-py
description: >-
  DevOps 运维工具，支持数据库管理、部署、监控等操作。
---
# devops-tool

## Overview

DevOps 运维工具 —— AI Skill 自动生成演示。

支持数据库管理、部署管理、监控告警三大模块。
全局参数 env/region/verbose 自动穿透到所有子命令组。

## Guidelines

- This tool is implemented using the `nb_cmd` framework. Each public instance method of the `NbCmd` subclass becomes a subcommand.
- If you are unsure about the specific logic of a command, inspect the source code of the corresponding method in the implementation.
- Global parameters defined in `__init__` are automatically passed to all subcommands.
- Boolean flags default to `False`; add the flag to set it to `True`.
- Subcommand groups are accessed via space, e.g., `<group> <command>`.
- Use `--help` or `-h` to see available commands and options.
- Use `--full-help` or `-fh` to see detailed parameter descriptions.

## When to Use

Activate this skill when you need to perform devops-tool-related operations, such as:
- health
- version
- db backup
- db migrate
- db restore
- deploy canary
- deploy rollback
- deploy rolling
- monitor alert
- monitor status

## Command Structure

### CLI
```bash
D:\ProgramData\Miniconda3\envs\py39b\python.exe ai_skill_gen_demo.py [global_params] <command_path> [command_params]
```

### Python
```python
from ai_skill_gen_demo import DevOpsTool
app = DevOpsTool()  # pass global params if needed
# app.subcommand.method(param=value)
```

**Parameter conventions:**
- `${value}` — parameter with default value (replace as needed)
- `$<name>` — **required** parameter (must provide a value)
- `--flag` (no value) — boolean switch (add to enable)

## Global Parameters

These parameters are defined in `__init__` and passed to all subcommands automatically.

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--env` | `str` | `prod` | 运行环境 prod/staging/dev |
| `--region` | `str` | `us-east` | 部署区域 |
| `--verbose` | `bool` | `False` | 输出详细信息 |

## Commands

### `health`

查看全局健康状态

**CLI:**
```bash
D:\ProgramData\Miniconda3\envs\py39b\python.exe ai_skill_gen_demo.py --env ${prod} --region ${us-east} --verbose health
```

**Python:**
```python
app.health()
```

### `version`

查看工具版本

**CLI:**
```bash
D:\ProgramData\Miniconda3\envs\py39b\python.exe ai_skill_gen_demo.py --env ${prod} --region ${us-east} --verbose version
```

**Python:**
```python
app.version()
```

### `db` *(subcommand group)*

数据库管理 (二级子命令组)

### `db backup`

备份数据库

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `--compress` | `bool` | `True` | 启用压缩 |

**CLI:**
```bash
D:\ProgramData\Miniconda3\envs\py39b\python.exe ai_skill_gen_demo.py --env ${prod} --region ${us-east} --verbose db backup
```

**Python:**
```python
app.db.backup(compress=True)
```

### `db migrate`

执行数据库迁移

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `--dry-run` | `bool` | `False` | 仅预览，不执行 |
| `--target` | `str` | `latest` | 目标迁移版本 |

**CLI:**
```bash
D:\ProgramData\Miniconda3\envs\py39b\python.exe ai_skill_gen_demo.py --env ${prod} --region ${us-east} --verbose db migrate --dry-run --target ${latest}
```

**Python:**
```python
app.db.migrate(dry_run=False, target="latest")
```

### `db restore`

从备份恢复数据库

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `--file` | `str` | *(required)* | 备份文件路径 |

**CLI:**
```bash
D:\ProgramData\Miniconda3\envs\py39b\python.exe ai_skill_gen_demo.py --env ${prod} --region ${us-east} --verbose db restore --file $<file>
```

**Python:**
```python
app.db.restore(file=<file>)
```

### `deploy` *(subcommand group)*

部署管理 (二级子命令组)

### `deploy canary`

金丝雀部署

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `--version, -v` | `str` | *(required)* | 部署版本号 |
| `--traffic` | `float` | `0.1` | 流量比例 0-1 |

**CLI:**
```bash
D:\ProgramData\Miniconda3\envs\py39b\python.exe ai_skill_gen_demo.py --env ${prod} --region ${us-east} --verbose deploy canary --version $<version> --traffic ${0.1}
```

**Python:**
```python
app.deploy.canary(version=<version>, traffic=0.1)
```

### `deploy rollback`

回滚到上一个版本

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `--steps` | `int` | `1` | 回退步数 |

**CLI:**
```bash
D:\ProgramData\Miniconda3\envs\py39b\python.exe ai_skill_gen_demo.py --env ${prod} --region ${us-east} --verbose deploy rollback --steps ${1}
```

**Python:**
```python
app.deploy.rollback(steps=1)
```

### `deploy rolling`

滚动部署

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `--version, -v` | `str` | *(required)* | 部署版本号 |
| `--batch-size` | `int` | `3` | 每批实例数 |
| `--wait` | `int` | `30` | 每批等待秒数 |

**CLI:**
```bash
D:\ProgramData\Miniconda3\envs\py39b\python.exe ai_skill_gen_demo.py --env ${prod} --region ${us-east} --verbose deploy rolling --version $<version> --batch-size ${3} --wait ${30}
```

**Python:**
```python
app.deploy.rolling(version=<version>, batch_size=3, wait=30)
```

### `monitor` *(subcommand group)*

监控告警 (二级子命令组)

### `monitor alert`

配置告警规则

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `--rule` | `str` | *(required)* | 告警规则名 |
| `--threshold` | `float` | *(required)* | 阈值 |

**CLI:**
```bash
D:\ProgramData\Miniconda3\envs\py39b\python.exe ai_skill_gen_demo.py --env ${prod} --region ${us-east} --verbose monitor alert --rule $<rule> --threshold $<threshold>
```

**Python:**
```python
app.monitor.alert(rule=<rule>, threshold=<threshold>)
```

### `monitor status`

查看服务状态

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `--service` | `str` | `None` | 服务名 |

**CLI:**
```bash
D:\ProgramData\Miniconda3\envs\py39b\python.exe ai_skill_gen_demo.py --env ${prod} --region ${us-east} --verbose monitor status
```

**Python:**
```python
app.monitor.status(service=None)
```

