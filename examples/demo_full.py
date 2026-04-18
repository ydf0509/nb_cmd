# -*- coding: utf-8 -*-
"""
nb_cmd 完整功能 demo —— 对应设计文档附录A (数据库管理工具)

用法:
    python demo_full.py --help
    python demo_full.py query "SELECT * FROM users"
    python demo_full.py query "SELECT * FROM users" --output json
    python demo_full.py stats
    python demo_full.py migrate --version v2.0 --dry-run

    # REST API 模式
    # Web UI 模式
    python demo_full.py --web --web-port 9904
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from nb_cmd import NbCmd, Arg, NbCmdMeta, cmdui
from enum import Enum


class OutputFormat(Enum):
    TABLE = "table"
    JSON = "json"
    CSV = "csv"


class DbTool(NbCmd):
    """数据库管理工具 - 支持多种数据库的通用管理"""

    class Meta(NbCmdMeta):
        name = "dbtool"
        version = "1.0.0"

    def query(self, sql: Arg(str, 'SQL查询语句'),
              output: Arg(OutputFormat, '输出格式') = OutputFormat.TABLE,
              limit: Arg(int, '返回行数上限') = 100):
        """执行SQL查询并展示结果"""
        cmdui.info('执行: {}'.format(sql))
        result = [
            {"id": 1, "name": "张三", "age": 25},
            {"id": 2, "name": "李四", "age": 30},
            {"id": 3, "name": "王五", "age": 28},
        ]

        if output == OutputFormat.TABLE or output == 'table':
            cmdui.table(result)
        elif output == OutputFormat.JSON or output == 'json':
            cmdui.json_print(result)
        elif output == OutputFormat.CSV or output == 'csv':
            print("id,name,age")
            for row in result:
                print(",".join(str(v) for v in row.values()))

    def migrate(self, version: Arg(str, '目标版本号') = "latest",
                dry_run: Arg(bool, '试运行，不实际执行') = False):
        """执行数据库迁移"""
        if dry_run:
            cmdui.warning("试运行模式，不会实际执行")
        cmdui.info('迁移到版本: {}'.format(version))
        import time
        steps = ["检查版本", "备份数据", "执行迁移", "验证结果"]
        for step in cmdui.progress(steps, desc="迁移进度"):
            time.sleep(0.3)
        cmdui.success("迁移完成")

    def stats(self):
        """显示数据库统计信息"""
        cmdui.kv({
            "数据库类型": "SQLite",
            "数据库大小": "15.3 MB",
            "表数量": "12",
            "总行数": "1,234,567",
            "最后备份": "2026-04-17 10:30:00",
            "连接池状态": "5/20 活跃",
        })

    def tree_demo(self):
        """树形结构展示 demo"""
        cmdui.tree({
            "数据库": {
                "users": {
                    "id": "INT PRIMARY KEY",
                    "name": "VARCHAR(100)",
                    "age": "INT",
                },
                "orders": {
                    "id": "INT PRIMARY KEY",
                    "user_id": "INT FOREIGN KEY",
                    "total": "DECIMAL(10,2)",
                },
            },
            "配置": {
                "max_connections": "20",
                "timeout": "30s",
            },
        })


if __name__ == '__main__':
    DbTool().run()

    '''
    D:/ProgramData/Miniconda3/envs/py39b/python.exe examples/demo_full.py --web --web-port 8083
    
    '''
