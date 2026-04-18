# -*- coding: utf-8 -*-
"""
nb_cmd 综合入口 demo —— 把多个 NbCmd 类组合到一个统一的 CLI / Web UI / REST API

用法:
    python bigone_cmd.py --help
    python bigone_cmd.py mytool greet 张三 --times 3
    python bigone_cmd.py deploy deploy web-01 --env prod
    python bigone_cmd.py k8s scale --replicas 5
    python bigone_cmd.py db query "SELECT 1"
    python bigone_cmd.py git status
    python bigone_cmd.py git remote add origin https://github.com/x/x.git
    python bigone_cmd.py server deploy 10.0.0.1 --env staging
    python bigone_cmd.py server stats
    python bigone_cmd.py --web --web-port 8025
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from nb_cmd import NbCmd
from demo_basic import MyTool
from demo_advanced import DeployTool
from demo_inherit import K8sDeploy
from demo_full import DbTool
from demo_subcommands import GitTool
from demo_nb_log import ServerTool


class OneAllTool(NbCmd):
    """
    综合工具，在一个网页运行所有NbCmd其他类
    """

    sub_commands = {
        'mytool': MyTool,
        'deploy': DeployTool,
        'k8s': K8sDeploy,
        'db': DbTool,
        'git': GitTool,
        'server': ServerTool('beijing'),
    }


if __name__ == '__main__':
    OneAllTool().run()

    '''
    D:/ProgramData/Miniconda3/envs/py39b/python.exe D:/codes/nb_cmd/examples/bigone_cmd.py --web --web-port 8025

    curl -X POST http://localhost:8025/mytool/greet -H "Content-Type: application/json" -d "{\"name\": \"张三\", \"times\": 3}"
    curl -X POST http://localhost:8025/deploy/deploy -H "Content-Type: application/json" -d "{\"host\": \"web-01\", \"env\": \"prod\"}"
    curl -X POST http://localhost:8025/deploy/status
    curl -X POST http://localhost:8025/k8s/deploy -H "Content-Type: application/json" -d "{\"host\": \"10.0.0.1\"}"
    curl -X POST http://localhost:8025/k8s/scale -H "Content-Type: application/json" -d "{\"replicas\": 5}"
    curl -X POST http://localhost:8025/db/query -H "Content-Type: application/json" -d "{\"sql\": \"SELECT * FROM users\"}"
    curl -X POST http://localhost:8025/db/stats
    curl -X POST http://localhost:8025/git/status
    curl -X POST http://localhost:8025/git/commit -H "Content-Type: application/json" -d "{\"message\": \"fix bug\", \"all\": true}"
    curl -X POST http://localhost:8025/server/deploy -H "Content-Type: application/json" -d "{\"host\": \"10.0.0.1\", \"env\": \"staging\"}"
    curl -X POST http://localhost:8025/server/stats
    '''

