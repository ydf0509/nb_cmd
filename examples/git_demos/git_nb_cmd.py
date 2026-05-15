# -*- coding: utf-8 -*-
"""
Git 命令行工具 — nb_cmd 实现。

演示 nb_cmd 在多层级子命令 + 全局参数场景下的优势：
  - 零装饰器：所有命令通过纯 Class + 方法定义
  - __init__ 即全局参数：self.nbctx 自动穿透到所有子命令组
  - self.nbctx 强类型 + IDE 补全：子命令组通过类型注解获取代码补全
  - 子命令独立可测：每个 NbCmd 子类可脱离父级单独实例化和测试
  - 深层子命令 (config → user → name/email) 通过 self.nbctx 访问全局参数

用法:
    python git_nb_cmd.py --verbose status
    python git_nb_cmd.py -C /etc/git remote add origin https://github.com/user/repo.git
    python git_nb_cmd.py --verbose branch create feature/login --from-branch develop
    python git_nb_cmd.py -C ~/my-config config user name "John Doe"
    python git_nb_cmd.py --verbose config user email

D:/ProgramData/Miniconda3/envs/py39b/python.exe D:\codes/nb_cmd/examples/git_demos/git_nb_cmd.py --tui


"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from dataclasses import dataclass
from typing import Annotated
from nb_cmd import NbCmd


# ==================== 1. 定义全局上下文 ====================

@dataclass
class GitCtx:
    """Git 全局上下文，所有子命令组共享"""
    verbose: bool = False
    path: str = '.'


# ==================== 2. 子命令组（纯 Class，可独立测试）====================

class RemoteCmd(NbCmd):
    """远程仓库管理 (二级子命令组)"""
    nbctx: GitCtx

    def add(self, name: Annotated[str, '远程仓库名'], url: Annotated[str, '仓库 URL']):
        """添加远程仓库"""
        if self.nbctx.verbose:
            print(f'[remote add] 工作目录: {self.nbctx.path}')
        print(f'git remote add {name} {url}')

    def remove(self, name: Annotated[str, '要删除的远程名']):
        """删除远程仓库"""
        print(f'git remote remove {name}')
        if self.nbctx.verbose:
            print(f'  (工作目录: {self.nbctx.path})')

    def show(self, name: Annotated[str, '远程仓库名'] = None):
        """显示远程仓库信息"""
        target = name or 'origin'
        print(f'git remote show {target}')
        if self.nbctx.verbose:
            print(f'  工作目录: {self.nbctx.path}')
        print(f'  Fetch URL: https://github.com/user/{target}.git')
        print(f'  Push  URL: https://github.com/user/{target}.git')


class BranchCmd(NbCmd):
    """分支管理 (二级子命令组)"""
    nbctx: GitCtx

    def create(self, name: Annotated[str, '分支名'],
               from_branch: Annotated[str, '基于哪个分支'] = 'main'):
        """创建分支"""
        print(f'git checkout -b {name} {from_branch}')
        if self.nbctx.verbose:
            print(f'  (工作目录: {self.nbctx.path})')

    def delete(self, name: Annotated[str, '分支名'],
               force: Annotated[bool, '强制删除', 'f'] = False):
        """删除分支"""
        flag = '-D' if force else '-d'
        print(f'git branch {flag} {name}')
        if self.nbctx.verbose:
            print('  (强制模式)')

    def list(self, merged: Annotated[bool, '只显示已合并的分支'] = False):
        """列出分支"""
        filter_flag = '--merged' if merged else ''
        print(f'git branch {filter_flag}')
        if self.nbctx.verbose:
            print(f'  工作目录: {self.nbctx.path}')
        print('  * main')
        print('    develop')
        print('    feature/login')


class UserConfigCmd(NbCmd):
    """用户配置 (三级深层子命令组，通过 self.nbctx 访问全局参数)"""
    nbctx: GitCtx

    def name(self, value: Annotated[str, '用户名 (不传则查询)'] = None):
        """获取/设置用户名 — 深层子命令，（通过 self.nbctx 访问全局参数）"""
        work_path = self.nbctx.path
        if value:
            print(f'git -C {work_path} config user.name "{value}"')
            print(f'  → 用户名已设置为: {value}')
        else:
            print(f'git -C {work_path} config user.name')
            print(f'  → 当前用户名: User')
        if self.nbctx.verbose:
            print(f'  (详细模式: 工作目录={work_path})')

    def email(self, value: Annotated[str, '用户邮箱 (不传则查询)'] = None):
        """获取/设置用户邮箱 — 深层子命令，（通过 self.nbctx 访问全局参数，传入 value 则设置，不传入则查询）"""
        work_path = self.nbctx.path
        if value:
            print(f'git -C {work_path} config user.email "{value}"')
            print(f'  → 邮箱已设置为: {value}')
        else:
            print(f'git -C {work_path} config user.email')
            print(f'  → 当前邮箱: user@example.com')
        if self.nbctx.verbose:
            print(f'  (详细模式: 工作目录={work_path})')


class ConfigCmd(NbCmd):
    """配置管理 (二级子命令组，挂载三级子命令)"""
    nbctx: GitCtx

    sub_commands = {
        'user': UserConfigCmd,
    }


# ==================== 3. 顶层入口 ====================

class GitTool(NbCmd):
    """
    Git 命令行工具 (nb_cmd 版)

    全局参数 verbose/config_dir 自动穿透到所有子命令组。
    演示多层级子命令: remote, branch (二级), config → user (三级)
    """
    nbctx: GitCtx

    def __init__(
        self,
        verbose: Annotated[bool, '详细输出', 'v'] = False,
        path: Annotated[str, '工作目录路径', 'C'] = '.',
    ):
        self.verbose = verbose
        self.path = path
        self.nbctx = GitCtx(
            verbose=self.verbose,
            path=self.path,
        )

    sub_commands = {
        'remote': RemoteCmd,
        'branch': BranchCmd,
        'config': ConfigCmd,
    }

    def status(self):
        """查看仓库状态"""
        verbose_flag = ' (详细模式)' if self.nbctx.verbose else ''
        print(f'[status] 检查仓库状态{verbose_flag}')
        print(f'  工作目录: {self.nbctx.path}')
        print('  On branch main')
        print('  nothing to commit, working tree clean')

    def log(self,
            oneline: Annotated[bool, '单行显示'] = False,
            graph: Annotated[bool, '图形化显示'] = False,
            max_count: Annotated[int, '最大显示数量', 'n'] = 10):
        """查看提交历史"""
        if self.nbctx.verbose:
            print(f'[log] 工作目录: {self.nbctx.path}')
        fmt = '--oneline' if oneline else ''
        graph_flag = '--graph' if graph else ''
        print(f'git log {fmt} {graph_flag} -{max_count}')
        print('  commit a1b2c3d4 (HEAD -> main)')
        print('  Author: User <user@example.com>')
        print('  Date:   2026-05-11')
        print('      initial commit')


if __name__ == '__main__':
    GitTool().run()