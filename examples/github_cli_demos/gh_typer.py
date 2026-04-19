# -*- coding: utf-8 -*-
"""
GitHub CLI — Typer 实现。

演示 Typer 在多层级子命令 + 全局参数场景下的典型写法：
  - 必须用模块级全局 state 字典穿透参数（破坏封装、非线程安全）
  - add_typer() 手动管理多个 Typer 实例
  - 子命令与全局状态强耦合，无法独立测试

用法:
    python gh_typer.py --repo myorg/api issue list --state all
    python gh_typer.py --repo prod/web --debug pr merge --number 42 --squash
    python gh_typer.py -R team/cli --no-prompt --auth-token ghp_xxx issue create --title "Deploy failed"
"""
import typer
from typing import Optional

app = typer.Typer(help="gh-cli: GitHub 命令行工具 (Typer 版)")

# ⚠️ 模块级全局字典 — 破坏封装，非线程安全
state = {}


@app.callback()
def main(
    repo: str = typer.Option(..., "--repo", "-R", help="目标仓库 (owner/repo)"),
    hostname: Optional[str] = typer.Option(None, help="GitHub Enterprise 域名"),
    auth_token: Optional[str] = typer.Option(None, help="访问令牌 (覆盖配置)"),
    debug: bool = typer.Option(False, help="开启调试模式"),
    no_prompt: bool = typer.Option(False, help="禁用交互提示"),
):
    """全局参数入口"""
    state.update(
        repo=repo,
        hostname=hostname,
        auth_token=auth_token,
        debug=debug,
        no_prompt=no_prompt,
    )


# ==================== issue 子命令组 ====================

issue_app = typer.Typer(help="Issue 管理")
app.add_typer(issue_app, name="issue")


@issue_app.command("list")
def issue_list(
    state_filter: str = typer.Option("open", "--state", help="Issue 状态过滤 (open/closed/all)"),
    label: Optional[str] = typer.Option(None, help="按标签过滤"),
    limit: int = typer.Option(30, help="最大返回数量"),
):
    """列出 Issues"""
    print(f"[issue list] repo={state['repo']}, state={state_filter}, label={label}, limit={limit}")
    if state['debug']:
        print(f"  DEBUG: hostname={state['hostname']}, no_prompt={state['no_prompt']}")


@issue_app.command("create")
def issue_create(
    title: str = typer.Option(..., "--title", "-t", help="Issue 标题"),
    body: str = typer.Option("", "--body", "-b", help="Issue 正文"),
    assignee: Optional[str] = typer.Option(None, "--assignee", "-a", help="指定负责人"),
):
    """创建新 Issue"""
    print(f"[issue create] repo={state['repo']}, title={title}")
    if body:
        print(f"  body={body}")
    if assignee:
        print(f"  assignee={assignee}")


@issue_app.command("view")
def issue_view(
    number: int = typer.Argument(..., help="Issue 编号"),
):
    """查看 Issue 详情"""
    print(f"[issue view] repo={state['repo']}, #{number}")


# ==================== pr 子命令组 ====================

pr_app = typer.Typer(help="Pull Request 管理")
app.add_typer(pr_app, name="pr")


@pr_app.command("list")
def pr_list(
    state_filter: str = typer.Option("open", "--state", help="PR 状态过滤 (open/closed/merged/all)"),
    author: Optional[str] = typer.Option(None, help="按作者过滤"),
):
    """列出 Pull Requests"""
    print(f"[pr list] repo={state['repo']}, state={state_filter}, author={author}")


@pr_app.command("create")
def pr_create(
    title: str = typer.Option(..., "--title", "-t", help="PR 标题"),
    body: str = typer.Option("", "--body", "-b", help="PR 描述"),
    base: str = typer.Option("main", help="目标分支"),
    draft: bool = typer.Option(False, help="创建为 Draft PR"),
):
    """创建新 Pull Request"""
    kind = 'Draft PR' if draft else 'PR'
    print(f"[pr create] repo={state['repo']}, {kind}: {title} → {base}")
    if state['debug']:
        tok = '***' if state['auth_token'] else 'default'
        print(f"  DEBUG: auth={tok}")


@pr_app.command("merge")
def pr_merge(
    number: int = typer.Option(..., "--number", "-n", help="PR 编号"),
    squash: bool = typer.Option(False, help="Squash 合并"),
    delete_branch: bool = typer.Option(False, help="合并后删除分支"),
):
    """合并 Pull Request"""
    method = 'squash' if squash else 'merge'
    tok = '***' if state['auth_token'] else 'default'
    print(f"[pr merge] repo={state['repo']}, #{number}, method={method}, auth={tok}")
    if delete_branch:
        print("  → 合并后将删除源分支")


# ==================== repo 子命令组 ====================

repo_app = typer.Typer(help="仓库管理")
app.add_typer(repo_app, name="repo")


@repo_app.command("clone")
def repo_clone(
    target_repo: str = typer.Argument(..., help="要克隆的仓库"),
    depth: int = typer.Option(0, help="浅克隆深度 (0=完整)"),
):
    """克隆仓库"""
    depth_info = f' (depth={depth})' if depth else ''
    print(f"[repo clone] {target_repo}{depth_info}")
    if state['hostname']:
        print(f"  → 从 {state['hostname']} 克隆")


@repo_app.command("fork")
def repo_fork(
    org: Optional[str] = typer.Option(None, help="Fork 到指定组织"),
):
    """Fork 仓库"""
    target = f" → {org}" if org else ''
    print(f"[repo fork] {state['repo']}{target}")


if __name__ == "__main__":
    app()
