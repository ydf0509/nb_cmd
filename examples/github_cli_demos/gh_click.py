# -*- coding: utf-8 -*-
"""
GitHub CLI — Click 实现。

演示 Click 在多层级子命令 + 全局参数场景下的典型写法：
  - 每个子命令/组必须 @click.pass_context
  - 取值靠 ctx.obj['key']（字符串键，无 IDE 补全）
  - 装饰器随层级指数叠加

用法:
    python gh_click.py -R myorg/api issue list --state all
    python gh_click.py --repo prod/web --debug pr merge --number 42 --squash
    python gh_click.py -R team/cli --no-prompt --auth-token ghp_xxx issue create --title "Deploy failed"
"""
import click


@click.group()
@click.option('--repo', '-R', required=True, help='目标仓库 (owner/repo)')
@click.option('--hostname', default=None, help='GitHub Enterprise 域名')
@click.option('--auth-token', default=None, help='访问令牌 (覆盖配置)')
@click.option('--debug', is_flag=True, help='开启调试模式')
@click.option('--no-prompt', is_flag=True, help='禁用交互提示')
@click.pass_context
def cli(ctx, repo, hostname, auth_token, debug, no_prompt):
    """gh-cli: GitHub 命令行工具 (Click 版)"""
    ctx.ensure_object(dict)
    ctx.obj.update(
        repo=repo,
        hostname=hostname,
        auth_token=auth_token,
        debug=debug,
        no_prompt=no_prompt,
    )


# ==================== issue 子命令组 ====================

@cli.group()
@click.pass_context
def issue(ctx):
    """Issue 管理"""
    pass


@issue.command('list')
@click.option('--state', default='open', type=click.Choice(['open', 'closed', 'all']),
              help='Issue 状态过滤')
@click.option('--label', default=None, help='按标签过滤')
@click.option('--limit', default=30, type=int, help='最大返回数量')
@click.pass_context
def issue_list(ctx, state, label, limit):
    """列出 Issues"""
    c = ctx.obj
    print(f"[issue list] repo={c['repo']}, state={state}, label={label}, limit={limit}")
    if c['debug']:
        print(f"  DEBUG: hostname={c['hostname']}, no_prompt={c['no_prompt']}")


@issue.command('create')
@click.option('--title', '-t', required=True, help='Issue 标题')
@click.option('--body', '-b', default='', help='Issue 正文')
@click.option('--assignee', '-a', default=None, help='指定负责人')
@click.pass_context
def issue_create(ctx, title, body, assignee):
    """创建新 Issue"""
    c = ctx.obj
    print(f"[issue create] repo={c['repo']}, title={title}")
    if body:
        print(f"  body={body}")
    if assignee:
        print(f"  assignee={assignee}")


@issue.command('view')
@click.argument('number', type=int)
@click.pass_context
def issue_view(ctx, number):
    """查看 Issue 详情"""
    c = ctx.obj
    print(f"[issue view] repo={c['repo']}, #{number}")


# ==================== pr 子命令组 ====================

@cli.group()
@click.pass_context
def pr(ctx):
    """Pull Request 管理"""
    pass


@pr.command('list')
@click.option('--state', default='open', type=click.Choice(['open', 'closed', 'merged', 'all']),
              help='PR 状态过滤')
@click.option('--author', default=None, help='按作者过滤')
@click.pass_context
def pr_list(ctx, state, author):
    """列出 Pull Requests"""
    c = ctx.obj
    print(f"[pr list] repo={c['repo']}, state={state}, author={author}")


@pr.command('create')
@click.option('--title', '-t', required=True, help='PR 标题')
@click.option('--body', '-b', default='', help='PR 描述')
@click.option('--base', default='main', help='目标分支')
@click.option('--draft', is_flag=True, help='创建为 Draft PR')
@click.pass_context
def pr_create(ctx, title, body, base, draft):
    """创建新 Pull Request"""
    c = ctx.obj
    kind = 'Draft PR' if draft else 'PR'
    print(f"[pr create] repo={c['repo']}, {kind}: {title} → {base}")
    if c['debug']:
        tok = '***' if c['auth_token'] else 'default'
        print(f"  DEBUG: auth={tok}")


@pr.command('merge')
@click.option('--number', '-n', required=True, type=int, help='PR 编号')
@click.option('--squash', is_flag=True, help='Squash 合并')
@click.option('--delete-branch', is_flag=True, help='合并后删除分支')
@click.pass_context
def pr_merge(ctx, number, squash, delete_branch):
    """合并 Pull Request"""
    c = ctx.obj
    method = 'squash' if squash else 'merge'
    tok = '***' if c['auth_token'] else 'default'
    print(f"[pr merge] repo={c['repo']}, #{number}, method={method}, auth={tok}")
    if delete_branch:
        print("  → 合并后将删除源分支")


# ==================== repo 子命令组 ====================

@cli.group()
@click.pass_context
def repo(ctx):
    """仓库管理"""
    pass


@repo.command('clone')
@click.argument('target_repo')
@click.option('--depth', default=0, type=int, help='浅克隆深度 (0=完整)')
@click.pass_context
def repo_clone(ctx, target_repo, depth):
    """克隆仓库"""
    c = ctx.obj
    depth_info = f' (depth={depth})' if depth else ''
    print(f"[repo clone] {target_repo}{depth_info}")
    if c['hostname']:
        print(f"  → 从 {c['hostname']} 克隆")


@repo.command('fork')
@click.option('--org', default=None, help='Fork 到指定组织')
@click.pass_context
def repo_fork(ctx, org):
    """Fork 仓库"""
    c = ctx.obj
    target = f" → {org}" if org else ''
    print(f"[repo fork] {c['repo']}{target}")


if __name__ == '__main__':
    cli()
