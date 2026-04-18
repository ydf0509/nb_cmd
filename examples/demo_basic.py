# -*- coding: utf-8 -*-
"""
nb_cmd 基础用法 demo —— 对应设计文档 4.1 最简示例

用法:
    python demo_basic.py --help
    python demo_basic.py greet 张三 --times 3
    python demo_basic.py greet -n 张三 -t 3
    python demo_basic.py deploy 192.168.1.1 --port 2222 --verbose
    python demo_basic.py deploy --help
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from nb_cmd import NbCmd, Arg


class MyTool(NbCmd):
    """我的超级工具（自动变成CLI的description）"""

    def greet(self, name: Arg(str, '要问候的人名', alias='n'),
              times: Arg(int, '问候次数', alias='t') = 1):
        """向某人问好（自动变成子命令的帮助信息）"""
        for _ in range(times):
            print('你好, {}!'.format(name))

    def deploy(self, host: Arg(str, '服务器地址', alias='H'),
               port: Arg(int, '端口号', alias='p') = 22,
               verbose: Arg(bool, '详细模式', alias='v') = False):
        """部署到远程服务器"""
        if verbose:
            print('[详细模式] 正在部署到 {}:{} ...'.format(host, port))
        print('部署到 {}:{} 完成'.format(host, port))

    def _private_helper(self):
        """下划线开头的方法不会暴露为子命令"""
        pass


if __name__ == '__main__':
    MyTool().run()

    '''
    D:/ProgramData/Miniconda3/envs/py39b/python.exe examples/demo_basic.py --web --web-port 8081
    
    '''
