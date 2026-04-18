# -*- coding: utf-8 -*-
"""
彩色终端输出，纯标准库实现，无外部依赖。
在不支持 ANSI 的终端上自动降级为无色输出。
"""
import os
import sys


def _supports_color():
    """检测当前终端是否支持 ANSI 颜色"""
    if os.getenv('NO_COLOR'):
        return False
    if os.getenv('FORCE_COLOR'):
        return True
    if not hasattr(sys.stdout, 'isatty'):
        return False
    if not sys.stdout.isatty():
        return False
    if sys.platform == 'win32':
        return os.getenv('ANSICON') is not None or 'WT_SESSION' in os.environ or os.getenv('TERM_PROGRAM') == 'vscode'
    return True


_COLOR_ENABLED = _supports_color()

_COLORS = {
    'reset': '\033[0m',
    'bold': '\033[1m',
    'red': '\033[31m',
    'green': '\033[32m',
    'yellow': '\033[33m',
    'blue': '\033[34m',
    'magenta': '\033[35m',
    'cyan': '\033[36m',
    'white': '\033[37m',
    'bright_red': '\033[91m',
    'bright_green': '\033[92m',
    'bright_yellow': '\033[93m',
    'bright_blue': '\033[94m',
}


def _colorize(text, color_name):
    if not _COLOR_ENABLED:
        return text
    color_code = _COLORS.get(color_name, '')
    reset = _COLORS['reset']
    return '{}{}{}'.format(color_code, text, reset)


def print_success(msg):
    sys.stdout.write(_colorize('[OK] {}'.format(msg), 'bright_green') + '\n')
    sys.stdout.flush()


def print_warning(msg):
    sys.stdout.write(_colorize('[WARN] {}'.format(msg), 'bright_yellow') + '\n')
    sys.stdout.flush()


def print_error(msg):
    sys.stderr.write(_colorize('[ERROR] {}'.format(msg), 'bright_red') + '\n')
    sys.stderr.flush()


def print_info(msg):
    sys.stdout.write(_colorize('[INFO] {}'.format(msg), 'bright_blue') + '\n')
    sys.stdout.flush()
