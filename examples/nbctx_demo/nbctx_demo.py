# -*- coding: utf-8 -*-
"""
nb_cmd nbctx 跨层级上下文传递 demo。

演示：顶层全局参数（region/env/debug）如何自动穿透到任意深度的子命令组。

六种能力：
    1. Python 直接调用: 见本文件底部 if __name__ == '__main__' 部分
    2. CLI:  python nbctx_demo.py --region shanghai db migrate
    3. REST API:  curl -X POST http://localhost:8085/db/migrate -d '{"init_params":{"region":"shanghai"}}'
    4. Web UI:  python nbctx_demo.py --web --web-port 8085
    5. TUI:  python nbctx_demo.py --tui
    6. 文档生成: 见本文件底部 CmdGen 示例
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from dataclasses import dataclass
from typing import Annotated
from nb_cmd import NbCmd


# ==================== 1. 定义全局上下文 ====================

@dataclass
class AppCtx:
    """应用级上下文，所有子命令组共享"""
    region: str = 'beijing'
    env: str = 'prod'
    debug: bool = False


# ==================== 2. 子命令组（多层嵌套）====================

class OpsTool(NbCmd):
    """运维操作（第三级子命令组）"""
    nbctx: AppCtx

    def deploy(self, version: Annotated[str, '目标版本号', '-v'], rollback: Annotated[bool, '是否回滚'] = False):
        """部署指定版本"""
        action = '回滚' if rollback else '部署'
        print(f'[{self.nbctx.region}/{self.nbctx.env}] {action} v{version}')
        if self.nbctx.debug:
            print(f'  DEBUG: deploy(version={version}, rollback={rollback})')

    def restart(self):
        """重启服务"""
        print(f'[{self.nbctx.region}/{self.nbctx.env}] 重启服务')


class DbTool(NbCmd):
    """数据库工具（第二级子命令组）"""
    nbctx: AppCtx

    def migrate(self, dry_run: Annotated[bool, '仅模拟，不执行'] = False):
        """执行数据库迁移"""
        mode = 'DRY-RUN' if dry_run else 'EXECUTE'
        print(f'[{self.nbctx.region}/{self.nbctx.env}] 数据库迁移 ({mode})')
        if self.nbctx.debug:
            print(f'  DEBUG: migrate(dry_run={dry_run})')

    def backup(self, compress: Annotated[bool, '启用压缩'] = True):
        """备份数据库"""
        fmt = 'tar.gz' if compress else 'sql'
        print(f'[{self.nbctx.region}/{self.nbctx.env}] 备份数据库 → backup.{fmt}')

    def status(self):
        """查看数据库连接状态"""
        print(f'[{self.nbctx.region}] 数据库连接正常 (env={self.nbctx.env})')


class ServerTool(NbCmd):
    """服务器管理（第二级子命令组，包含第三级 ops）"""
    nbctx: AppCtx

    sub_commands = {
        'ops': OpsTool,
    }

    def info(self):
        """查看服务器信息"""
        print(f'[{self.nbctx.region}] 服务器: {self.nbctx.env} 环境')
        print(f'  Region: {self.nbctx.region}')
        print(f'  Env:    {self.nbctx.env}')
        print(f'  Debug:  {self.nbctx.debug}')

    def ssh(self, user: Annotated[str, '登录用户名'] = 'root'):
        """SSH 登录"""
        host = f'{self.nbctx.region}-{self.nbctx.env}.example.com'
        print(f'ssh {user}@{host}')


# ==================== 3. 顶层命令 ====================

class MyApp(NbCmd):
    """
    云平台管理工具 —— nbctx 跨层级上下文传递 demo。

    全局参数 region/env/debug 会自动传递给所有子命令组。
    """
    nbctx: AppCtx  # 类型注解，让 IDE 补全 self.nbctx.region 等

    class Meta:
        name = 'cloud-tool'
        version = '1.0.0'
        enable_exec = False

    def __init__(self,
                 region: Annotated[str, '部署区域，如 beijing/shanghai/tokyo'] = 'beijing',
                 env: Annotated[str, '运行环境，如 prod/staging/test'] = 'prod',
                 debug: Annotated[bool, '开启调试模式'] = False):
        self.region = region
        self.env = env
        self.debug = debug

    def make_nbctx(self):
        """构造上下文，框架自动传给所有子命令组"""
        return AppCtx(region=self.region, env=self.env, debug=self.debug)

    sub_commands = {
        'db': DbTool,
        'server': ServerTool,
    }

    def status(self):
        """查看全局状态"""
        print(f'=== 云平台状态 ===')
        print(f'Region: {self.nbctx.region}')
        print(f'Env:    {self.nbctx.env}')
        print(f'Debug:  {self.nbctx.debug}')

    def whoami(self):
        """显示当前用户信息"""
        return {'user': 'admin', 'region': self.nbctx.region, 'env': self.nbctx.env}


if __name__ == '__main__':
    import sys as _sys

    if len(_sys.argv) > 1:
        # CLI / Web / API 模式
        MyApp().run()
    else:
        # 本地直接调用演示
        print('='*50)
        print('本地直接调用演示（不走 CLI/Web/API）')
        print('='*50)

        # 场景 1: 顶层命令使用 nbctx
        print('\n--- 场景 1: 顶层命令 ---')
        app = MyApp(region='shanghai', env='staging', debug=True)
        app.nbctx = app.make_nbctx()
        app.status()

        # 场景 2: 子命令组手动注入 nbctx
        print('\n--- 场景 2: 子命令组手动注入 nbctx ---')
        ctx = AppCtx(region='tokyo', env='test', debug=True)
        db = DbTool()
        db.nbctx = ctx
        db.migrate(dry_run=True)
        db.backup()

        # 场景 3: 用默认 ctx
        print('\n--- 场景 3: 用默认 ctx ---')
        db2 = DbTool()
        db2.nbctx = AppCtx()  # 使用 dataclass 默认值
        db2.migrate()

        # 场景 4: 多个子命令组共享同一个 ctx
        print('\n--- 场景 4: 多子命令组共享 ctx ---')
        ctx = AppCtx(region='us-east', env='canary')
        db = DbTool()
        server = ServerTool()
        ops = OpsTool()
        db.nbctx = ctx
        server.nbctx = ctx
        ops.nbctx = ctx
        db.status()
        server.info()
        ops.deploy('2.0.0')

        # 场景 5: CmdGen 自动生成命令行示例
        print('\n--- 场景 5: CmdGen 自动生成命令行示例 ---')
        from nb_cmd import CmdGen

        g = CmdGen(MyApp, script='nbctx_demo.py')
        print(g.cmd(DbTool.migrate))
        print(g.cmd(OpsTool.deploy))
        print(g.cmd(MyApp.status))
        print(g.cmd(ServerTool.ssh))
        print()
        g_md = CmdGen(MyApp, script='d:/codes/nb_cmd/examples/nbctx_demo/nbctx_demo.py', fmt='markdown')
        print(g_md.cmd(DbTool.migrate))

        # 场景 6: CmdGen.doc() 生成完整文档
        print('\n--- 场景 6: CmdGen.doc() 生成完整文档 ---')
        print(g.doc())
        print()
        print('--- Markdown 格式 ---')
        print(g_md.doc(file='d:/codes/nb_cmd/examples/nbctx_demo/nbctx_demo_gen_doc.md'))
