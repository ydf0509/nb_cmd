# -*- coding: utf-8 -*-
"""
Git 命令行工具 — Click 实现。

演示 Click 在多层级子命令 + 全局参数场景下的典型写法：
  - 全局参数通过 @click.group() + @click.pass_context 传递
  - 子命令组通过 @cli.group() 嵌套
  - 深层子命令 (config → user → name/email) 通过 ctx.obj 访问全局参数
  - 每个子命令都要加 @click.pass_context 才能访问全局参数

用法:
    python git_click.py --verbose status
    python git_click.py -C /etc/git remote add origin https://github.com/user/repo.git
    python git_click.py --verbose branch create feature/login --from-branch develop
    python git_click.py -C ~/my-config config user name "John Doe"
    python git_click.py --verbose config user email
"""
import click


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='详细输出')
@click.option('--path', '-C', default='.', help='工作目录路径')
@click.pass_context
def cli(ctx, verbose, path):
    """Git 命令行工具 (Click 版)"""
    ctx.ensure_object(dict)
    ctx.obj.update(
        verbose=verbose,
        path=path,
    )


# ==================== 一级命令 ====================

@cli.command()
@click.pass_context
def status(ctx):
    """查看仓库状态"""
    c = ctx.obj
    verbose_flag = ' (详细模式)' if c['verbose'] else ''
    print(f'[status] 检查仓库状态{verbose_flag}')
    print(f'  工作目录: {c["path"]}')
    print('  On branch main')
    print('  nothing to commit, working tree clean')


@cli.command()
@click.option('--oneline', is_flag=True, help='单行显示')
@click.option('--graph', is_flag=True, help='图形化显示')
@click.option('--max-count', '-n', default=10, type=int, help='最大显示数量')
@click.pass_context
def log(ctx, oneline, graph, max_count):
    """查看提交历史"""
    c = ctx.obj
    if c['verbose']:
        print(f'[log] 工作目录: {c["path"]}')
    fmt = '--oneline' if oneline else ''
    graph_flag = '--graph' if graph else ''
    print(f'git log {fmt} {graph_flag} -{max_count}')
    print('  commit a1b2c3d4 (HEAD -> main)')
    print('  Author: User <user@example.com>')
    print('  Date:   2026-05-11')
    print('      initial commit')


# ==================== remote 子命令组 (二级) ====================

@cli.group()
@click.pass_context
def remote(ctx):
    """远程仓库管理"""
    pass


@remote.command('add')
@click.argument('name')
@click.argument('url')
@click.pass_context
def remote_add(ctx, name, url):
    """添加远程仓库"""
    c = ctx.obj
    if c['verbose']:
        print(f'[remote add] 工作目录: {c["path"]}')
    print(f'git remote add {name} {url}')


@remote.command('remove')
@click.argument('name')
@click.pass_context
def remote_remove(ctx, name):
    """删除远程仓库"""
    c = ctx.obj
    print(f'git remote remove {name}')
    if c['verbose']:
        print(f'  (工作目录: {c["path"]})')


@remote.command('show')
@click.argument('name', required=False, default=None)
@click.pass_context
def remote_show(ctx, name):
    """显示远程仓库信息"""
    c = ctx.obj
    target = name or 'origin'
    print(f'git remote show {target}')
    if c['verbose']:
        print(f'  工作目录: {c["path"]}')
    print(f'  Fetch URL: https://github.com/user/{target}.git')
    print(f'  Push  URL: https://github.com/user/{target}.git')


# ==================== branch 子命令组 (二级) ====================

@cli.group()
@click.pass_context
def branch(ctx):
    """分支管理"""
    pass


@branch.command('create')
@click.argument('name')
@click.option('--from-branch', default='main', help='基于哪个分支')
@click.pass_context
def branch_create(ctx, name, from_branch):
    """创建分支"""
    c = ctx.obj
    print(f'git checkout -b {name} {from_branch}')
    if c['verbose']:
        print(f'  (工作目录: {c["path"]})')


@branch.command('delete')
@click.argument('name')
@click.option('--force', '-f', is_flag=True, help='强制删除')
@click.pass_context
def branch_delete(ctx, name, force):
    """删除分支"""
    c = ctx.obj
    flag = '-D' if force else '-d'
    print(f'git branch {flag} {name}')
    if c['verbose']:
        print('  (强制模式)')


@branch.command('list')
@click.option('--merged', is_flag=True, help='只显示已合并的分支')
@click.pass_context
def branch_list(ctx, merged):
    """列出分支"""
    c = ctx.obj
    filter_flag = '--merged' if merged else ''
    print(f'git branch {filter_flag}')
    if c['verbose']:
        print(f'  工作目录: {c["path"]}')
    print('  * main')
    print('    develop')
    print('    feature/login')


# ==================== config → user 深层子命令组 (三级) ====================

@cli.group()
@click.pass_context
def config(ctx):
    """配置管理"""
    pass


@config.group()
@click.pass_context
def user(ctx):
    """用户配置"""
    pass


@user.command('name')
@click.argument('value', required=False, default=None)
@click.pass_context
def user_name(ctx, value):
    """获取/设置用户名 — 深层子命令，通过 ctx.obj 访问全局参数"""
    c = ctx.obj
    work_path = c['path']
    if value:
        print(f'git -C {work_path} config user.name "{value}"')
        print(f'  → 用户名已设置为: {value}')
    else:
        print(f'git -C {work_path} config user.name')
        print(f'  → 当前用户名: User')
    if c['verbose']:
        print(f'  (详细模式: 工作目录={work_path})')


@user.command('email')
@click.argument('value', required=False, default=None)
@click.pass_context
def user_email(ctx, value):
    """获取/设置用户邮箱 — 深层子命令，通过 ctx.obj 访问全局参数"""
    c = ctx.obj
    work_path = c['path']
    if value:
        print(f'git -C {work_path} config user.email "{value}"')
        print(f'  → 邮箱已设置为: {value}')
    else:
        print(f'git -C {work_path} config user.email')
        print(f'  → 当前邮箱: user@example.com')
    if c['verbose']:
        print(f'  (详细模式: 工作目录={work_path})')


if __name__ == '__main__':
    cli()