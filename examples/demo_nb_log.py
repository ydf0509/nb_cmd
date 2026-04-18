# -*- coding: utf-8 -*-
"""
nb_cmd 集成 nb_log 的 demo —— 对应设计文档 7.1 Meta 配置类

演示 use_nb_log = True 时的效果:
  - self.logger 变为 nb_log 增强版 logger（彩色、文件名行号等）
  - 日志自动写入 log_file

前提: pip install nb_log

用法:
    python demo_nb_log.py --help
    python demo_nb_log.py deploy 10.0.0.1 --env staging
    python demo_nb_log.py stats
    python demo_nb_log.py --web --web-port 9911
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from nb_cmd import NbCmd, Arg, NbCmdMeta, cmdui
from enum import Enum


class Environment(Enum):
    DEV = "dev"
    STAGING = "staging"
    PROD = "prod"


class ServerTool(NbCmd):
    """服务器运维工具（启用 nb_log 增强日志）"""

    class Meta(NbCmdMeta):
        name = "server-tool"
        version = "1.0.0"

        use_nb_log = True
        log_level = "DEBUG"
        log_file = "server_tool.log"

        web_theme = "dark"

    def __init__(self, region: Arg(str, '机房区域', alias='r'),
                 timeout: Arg(int, '超时秒数') = 30):
        super().__init__()
        self.region = region
        self.timeout = timeout

    def before_run(self):
        """所有子命令执行前的钩子"""
        self.logger.info('服务器运维工具启动 (区域: {}, 超时: {}s)'.format(
            self.region, self.timeout))

    def after_run(self):
        """所有子命令执行后的钩子"""
        self.logger.info('运维操作完成')

    def deploy(self, host: str, env: Environment = Environment.DEV, dry_run: bool = False):
        """部署服务到目标主机"""
        self.logger.debug('参数: host={}, env={}, dry_run={}'.format(host, env.value, dry_run))

        if dry_run:
            cmdui.warning('试运行模式，不会实际部署')

        self.logger.info('正在部署到 {} (环境: {})'.format(host, env.value))
        cmdui.info('检查服务器连接...')
        cmdui.info('上传代码包...')
        cmdui.info('重启服务...')
        cmdui.success('部署完成: {} ({})'.format(host, env.value))

    def stats(self):
        """查看系统状态"""
        self.logger.info('查询系统状态')
        cmdui.kv({
            "CPU使用率": "45%",
            "内存使用": "2.3GB / 8GB",
            "磁盘使用": "120GB / 500GB",
            "运行时间": "3天12小时",
            "活跃连接": "128",
        })

    def check(self, host: str):
        """健康检查"""
        self.logger.info('检查 {} 健康状态'.format(host))
        data = [
            {"服务": "nginx", "状态": "running", "端口": 80},
            {"服务": "mysql", "状态": "running", "端口": 3306},
            {"服务": "redis", "状态": "running", "端口": 6379},
        ]
        cmdui.table(data)
        cmdui.success('所有服务运行正常')

    def logs(self, service: str = "nginx", lines: int = 10):
        """查看服务日志"""
        self.logger.info('查看 {} 最近 {} 行日志'.format(service, lines))
        for i in range(lines):
            print('[2026-04-17 15:{:02d}:00] {} - 请求处理完成'.format(30 + i, service))


if __name__ == '__main__':
    ServerTool('beijing').run()

    '''
    D:/ProgramData/Miniconda3/envs/py39b/python.exe examples/demo_nb_log.py --web --web-port 8087

    '''
