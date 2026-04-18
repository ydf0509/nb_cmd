# -*- coding: utf-8 -*-
"""
nb_cmd 高级用法 demo —— 继承覆写 + 子命令组 + 高级类型
"""
import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from typing import Annotated

from nb_cmd import NbCmd, NbCmdMeta, cmdui
from enum import Enum


class Environment(Enum):
    DEV = "dev"
    STAGING = "staging"
    PROD = "prod"


class DeployTool(NbCmd):
    """部署工具"""

    class Meta(NbCmdMeta):
        use_nb_log = True
        log_level = "DEBUG"
        log_file = "deploy_tool.log"
        web_theme = "dark"
        serve_port = 8082
        serve_workers = 1
        web_title = "部署工具"

    def deploy(self,
               host: Annotated[str, '目标服务器地址', 'H'],
               port: Annotated[int, '端口号', 'p'] = 22,
               env: Annotated[Environment, '部署环境', 'e'] = Environment.DEV,
               dry_run: Annotated[bool, '试运行模式'] = False,
               ):
        """执行部署到指定服务器"""
        print('环境: {}'.format(env.value if hasattr(env, 'value') else env))
        print('目标: {}:{}'.format(host, port))
        if dry_run:
            print('** 试运行模式，不会实际执行 **')
        else:
            print('部署完成!')

    def status(self):
        """查看部署状态"""
        cmdui.kv({
            "当前环境": "dev",
            "最后部署": "2026-04-17 10:30",
            "服务状态": "运行中",
        })

    def show_users(self):
        """展示用户列表"""
        data = [
            {"名字": "张三", "年龄": 25, "城市": "北京"},
            {"名字": "李四", "年龄": 30, "城市": "上海"},
            {"名字": "王五", "年龄": 28, "城市": "广州"},
        ]
        cmdui.table(data)

    def process(self):
        """模拟处理任务（带进度条）"""
        
        items = list(range(20))
        for _ in cmdui.progress(items, desc="处理中"):
            time.sleep(0.1)
        cmdui.success("处理完成!")
    
    def many_print(self):
        """持续打印多行（用于测试 WebSocket 实时流式输出）"""
        for i in range(10):
            time.sleep(1)
            print('print {}'.format(i))
            self.logger.debug('logger debug {}'.format(i))
            self.logger.info('logger info {}'.format(i))
            self.logger.warning('logger warning {}'.format(i))
            self.logger.error('logger error {}'.format(i))
            self.logger.critical('logger critical {}'.format(i))

            cmdui.info('ui info {}'.format(i))
            cmdui.success('ui success {}'.format(i))
            cmdui.error('ui error {}'.format(i))
            cmdui.warning('ui warning {}'.format(i))



if __name__ == '__main__':
    DeployTool().run()


    '''
    D:/ProgramData/Miniconda3/envs/py39b/python.exe examples/demo_advanced.py --web --web-port 8082
    
    '''
