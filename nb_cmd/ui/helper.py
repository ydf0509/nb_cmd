# -*- coding: utf-8 -*-
"""
UI 工具方法集合 —— cmdui 单例的实现。

通过 ``from nb_cmd import cmdui`` 导入使用。
"""
import json
import sys

from .colors import print_success, print_warning, print_error, print_info
from .table import print_table, print_kv
from .progress import progress as _progress_iter


class UIHelper(object):
    """
    NbCmd 的 UI 工具方法集合。

    通过 ``from nb_cmd import cmdui`` 导入使用，避免与用户自定义的子命令方法名冲突。
    包含: 输出(table/kv/tree/json_print)、彩色(success/warning/error/info)、
          交互(confirm/prompt/select)、进度(progress) 等工具。
    """

    def table(self, data, headers=None):
        """表格输出"""
        print_table(data, headers)

    def kv(self, data):
        """键值对输出"""
        print_kv(data)

    def tree(self, data, prefix='', is_last=True):
        """树形输出"""
        if isinstance(data, dict):
            items = list(data.items())
            for i, (key, value) in enumerate(items):
                last = (i == len(items) - 1)
                connector = '└── ' if last else '├── '
                if isinstance(value, dict):
                    sys.stdout.write('{}{}{}\n'.format(prefix, connector, key))
                    extension = '    ' if last else '│   '
                    self.tree(value, prefix + extension, last)
                else:
                    sys.stdout.write('{}{}{}: {}\n'.format(prefix, connector, key, value))

    def json_print(self, data):
        """JSON美化输出"""
        sys.stdout.write(json.dumps(data, ensure_ascii=False, indent=2, default=str) + '\n')
        sys.stdout.flush()

    def progress(self, iterable, desc=None, total=None):
        """进度条迭代器"""
        return _progress_iter(iterable, desc=desc, total=total)

    def confirm(self, message):
        """确认提示，返回 True/False"""
        try:
            answer = input('{} [y/N]: '.format(message)).strip().lower()
            return answer in ('y', 'yes')
        except (EOFError, KeyboardInterrupt):
            return False

    def prompt(self, message, default=None):
        """输入提示"""
        try:
            if default is not None:
                answer = input('{} [{}]: '.format(message, default)).strip()
                return answer if answer else default
            else:
                return input('{}: '.format(message)).strip()
        except (EOFError, KeyboardInterrupt):
            return default

    def select(self, message, choices):
        """选择提示"""
        sys.stdout.write(message + '\n')
        for i, choice in enumerate(choices):
            sys.stdout.write('  {}. {}\n'.format(i + 1, choice))
        sys.stdout.flush()
        try:
            idx = int(input('请选择 [1-{}]: '.format(len(choices))).strip()) - 1
            if 0 <= idx < len(choices):
                return choices[idx]
        except (ValueError, EOFError, KeyboardInterrupt):
            pass
        return choices[0] if choices else None

    def success(self, msg):
        """绿色成功信息"""
        print_success(msg)

    def warning(self, msg):
        """黄色警告信息"""
        print_warning(msg)

    def error(self, msg):
        """红色错误信息"""
        print_error(msg)

    def info(self, msg):
        """蓝色信息"""
        print_info(msg)


cmdui = UIHelper()
