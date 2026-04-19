# -*- coding: utf-8 -*-
"""
GitHub CLI — nb_cmd 实现。

演示 nb_cmd 在多层级子命令 + 全局参数场景下的碾压优势：
  - 零装饰器：所有命令通过纯 Class + 方法定义
  - __init__ 直接赋值 self.nbctx：无需 make_nbctx()，CLI/Web/API 所有模式均正确传参
  - self.nbctx 强类型 + IDE 补全：子命令组通过类型注解获取代码补全和跳转
  - 子命令独立可测：每个 NbCmd 子类可脱离父级单独实例化和测试
  - CmdGen 自动文档：一行代码生成完整 Markdown 文档

用法:
    1. CLI:  python gh_nb_cmd.py --repo myorg/api issue list --state all
    2. CLI:  python gh_nb_cmd.py --repo prod/web --debug pr merge --number 42 --squash
    3. CLI:  python gh_nb_cmd.py -R team/cli --no-prompt --auth-token ghp_xxx issue create --title "Deploy failed"
    4. Web:  python gh_nb_cmd.py --web --web-port 8090
    5. 本地: python gh_nb_cmd.py  (无参数，进入本地演示)
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from dataclasses import dataclass
from typing import Optional
from typing import Annotated
from nb_cmd import NbCmd, CmdGen
from nb_cmd.core.meta import NbCmdMeta


# ==================== 1. 定义全局上下文 ====================

@dataclass
class GhCtx:
    """GitHub CLI 全局上下文，所有子命令组共享"""
    repo: Optional[str] = None
    hostname: Optional[str] = None
    auth_token: Optional[str] = None
    debug: bool = False
    no_prompt: bool = False


# ==================== 2. 子命令组（纯 Class，可独立测试）====================

class IssueCmd(NbCmd):
    """Issue 管理"""
    nbctx: GhCtx

    def list(self, state: Annotated[str, 'Issue 状态过滤 (open/closed/all)'] = 'open',
             label: Annotated[str, '按标签过滤'] = None,
             limit: Annotated[int, '最大返回数量'] = 30):
        """列出 Issues"""
        print(f"[issue list] repo={self.nbctx.repo}, state={state}, label={label}, limit={limit}")
        if self.nbctx.debug:
            print(f"  DEBUG: hostname={self.nbctx.hostname}, no_prompt={self.nbctx.no_prompt}")

    def create(self, title: Annotated[str, 'Issue 标题', 't'],
               body: Annotated[str, 'Issue 正文', 'b'] = '',
               assignee: Annotated[str, '指定负责人', 'a'] = None):
        """创建新 Issue"""
        print(f"[issue create] repo={self.nbctx.repo}, title={title}")
        if body:
            print(f"  body={body}")
        if assignee:
            print(f"  assignee={assignee}")

    def view(self, number: Annotated[int, 'Issue 编号']):
        """查看 Issue 详情"""
        print(f"[issue view] repo={self.nbctx.repo}, #{number}")


class PrCmd(NbCmd):
    """Pull Request 管理"""
    nbctx: GhCtx

    def list(self, state: Annotated[str, 'PR 状态过滤 (open/closed/merged/all)'] = 'open',
             author: Annotated[str, '按作者过滤'] = None):
        """列出 Pull Requests"""
        print(f"[pr list] repo={self.nbctx.repo}, state={state}, author={author}")

    def create(self, title: Annotated[str, 'PR 标题', 't'],
               body: Annotated[str, 'PR 描述', 'b'] = '',
               base: Annotated[str, '目标分支'] = 'main',
               draft: Annotated[bool, '创建为 Draft PR'] = False):
        """创建新 Pull Request"""
        kind = 'Draft PR' if draft else 'PR'
        print(f"[pr create] repo={self.nbctx.repo}, {kind}: {title} → {base}")
        if self.nbctx.debug:
            tok = '***' if self.nbctx.auth_token else 'default'
            print(f"  DEBUG: auth={tok}")

    def merge(self, number: Annotated[int, 'PR 编号', 'n'],
              squash: Annotated[bool, 'Squash 合并'] = False,
              delete_branch: Annotated[bool, '合并后删除分支'] = False):
        """合并 Pull Request"""
        method = 'squash' if squash else 'merge'
        tok = '***' if self.nbctx.auth_token else 'default'
        print(f"[pr merge] repo={self.nbctx.repo}, #{number}, method={method}, auth={tok}")
        if delete_branch:
            print("  → 合并后将删除源分支")


class RepoCmd(NbCmd):
    """仓库管理"""
    nbctx: GhCtx

    def clone(self, target_repo: Annotated[str, '要克隆的仓库'],
              depth: Annotated[int, '浅克隆深度 (0=完整)'] = 0):
        """克隆仓库"""
        depth_info = f' (depth={depth})' if depth else ''
        print(f"[repo clone] {target_repo}{depth_info}")
        if self.nbctx.hostname:
            print(f"  → 从 {self.nbctx.hostname} 克隆")

    def fork(self, org: Annotated[str, 'Fork 到指定组织'] = None):
        """Fork 仓库"""
        target = f" → {org}" if org else ''
        print(f"[repo fork] {self.nbctx.repo}{target}")


# ==================== 3. 顶层入口 ====================

class GhCli(NbCmd):
    """
    gh-cli: GitHub 命令行工具 (nb_cmd 版)

    全局参数 repo/hostname/auth_token/debug/no_prompt 自动穿透到所有子命令组。
    """
    nbctx: GhCtx

    class Meta(NbCmdMeta):
        name = 'gh-cli'
        version = '1.0.0'
        enable_exec = False
        # 白名单示例：仅暴露 status + issue/list + pr/merge（Python 直接调用不受影响）
        # allow_method_list = ['status', 'issue.list', 'pr/merge']
        # 黑名单示例：隐藏 status（与白名单互斥，白名单优先）
        # hide_method_list = ['status']
        # 鉴权示例：API/Web 请求须带 Authorization: Bearer <token>
        auth_token = 'my-secret-token'
        # 超时示例：命令执行超过 60 秒自动终止
        # timeout = 60

    def __init__(
        self,
        repo: Annotated[str, '目标仓库 (owner/repo)', 'R'] = None,
        hostname: Annotated[str, 'GitHub Enterprise 域名'] = None,
        auth_token: Annotated[str, '访问令牌 (覆盖配置)'] = None,
        debug: Annotated[bool, '开启调试模式'] = False,
        no_prompt: Annotated[bool, '禁用交互提示'] = False,
    ):
        self.repo = repo
        self.hostname = hostname
        self.auth_token = auth_token
        self.debug = debug
        self.no_prompt = no_prompt
        # 直接赋值 nbctx，CLI/Web/API 所有模式均能拿到正确的参数值
        self.nbctx = GhCtx(
            repo=self.repo,
            hostname=self.hostname,
            auth_token=self.auth_token,
            debug=self.debug,
            no_prompt=self.no_prompt,
        )
        # 也可以用 make_nbctx() 模板方法替代上面的直接赋值（两种方式均可）：
        # def make_nbctx(self):
        #     return GhCtx(repo=self.repo, ...)

    sub_commands = {
        'issue': IssueCmd,
        'pr': PrCmd,
        'repo': RepoCmd,
    }

    def status(self):
        """查看 CLI 全局配置状态"""
        print("=== gh-cli 全局配置 ===")
        print(f"repo:       {self.nbctx.repo}")
        print(f"hostname:   {self.nbctx.hostname}")
        print(f"auth_token: {'***' if self.nbctx.auth_token else 'None'}")
        print(f"debug:      {self.nbctx.debug}")
        print(f"no_prompt:  {self.nbctx.no_prompt}")


if __name__ == '__main__':
    import sys as _sys

    if len(_sys.argv) > 1:
        GhCli().run()
    else:
        print('=' * 60)
        print('GitHub CLI (nb_cmd 版) — 本地直接调用 + CmdGen 文档演示')
        print('=' * 60)

        # 场景 1: 本地直接调用（子命令独立测试）
        print('\n--- 场景 1: 子命令独立测试（无需启动整个 CLI）---')
        ctx = GhCtx(repo='myorg/api', debug=True)
        issue = IssueCmd()
        issue.nbctx = ctx
        issue.list(state='all', limit=10)
        issue.create(title='Bug: login failed')

        # 场景 2: 多个子命令组共享同一个 ctx
        print('\n--- 场景 2: 多子命令组共享 ctx ---')
        ctx = GhCtx(repo='prod/web', auth_token='ghp_xxx')
        pr = PrCmd()
        repo = RepoCmd()
        pr.nbctx = ctx
        repo.nbctx = ctx
        pr.merge(number=42, squash=True)
        repo.fork(org='my-team')

        # 场景 3: CmdGen 自动生成命令行示例
        print('\n--- 场景 3: CmdGen 命令行示例 ---')
        g = CmdGen(GhCli, script='gh_nb_cmd.py')
        print(g.cmd(IssueCmd.list))
        print(g.cmd(IssueCmd.create))
        print(g.cmd(PrCmd.merge))
        print(g.cmd(RepoCmd.clone))
        print(g.cmd(GhCli.status))

        # 场景 4: CmdGen.doc() 生成完整 Markdown 文档
        print('\n--- 场景 4: CmdGen.doc() 生成 Markdown ---')
        g_md = CmdGen(GhCli, script='gh_nb_cmd.py', fmt='markdown')
        doc_path = os.path.join(os.path.dirname(__file__), 'gh_nb_cmd_gen_doc.md')
        g_md.doc(file=doc_path)
        print(f'Markdown 文档已生成: {doc_path}')
