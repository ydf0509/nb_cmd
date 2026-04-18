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