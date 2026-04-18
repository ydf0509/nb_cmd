# -*- coding: utf-8 -*-
"""
纯标准库的表格输出，支持 CJK 字符对齐。
"""
import sys


def _write(text):
    sys.stdout.write(text + '\n')
    sys.stdout.flush()


def _display_width(text):
    width = 0
    for ch in str(text):
        code = ord(ch)
        if (0x4E00 <= code <= 0x9FFF) or (0x3400 <= code <= 0x4DBF) or \
           (0xF900 <= code <= 0xFAFF) or (0xFF00 <= code <= 0xFFEF) or \
           (0x3000 <= code <= 0x303F):
            width += 2
        else:
            width += 1
    return width


def _pad(text, width):
    text = str(text)
    dw = _display_width(text)
    return text + ' ' * max(0, width - dw)


def print_table(data, headers=None):
    """
    将 list[dict] 或 list[list] 格式化为表格输出。

    Parameters
    ----------
    data : list[dict] 或 list[list]
    headers : list[str], optional
    """
    if not data:
        _write('(空)')
        return

    if isinstance(data[0], dict):
        if headers is None:
            headers = list(data[0].keys())
        rows = [[row.get(h, '') for h in headers] for row in data]
    else:
        if headers is None:
            headers = ['列{}'.format(i + 1) for i in range(len(data[0]))]
        rows = data

    col_widths = [_display_width(str(h)) for h in headers]
    for row in rows:
        for i, val in enumerate(row):
            w = _display_width(str(val))
            if w > col_widths[i]:
                col_widths[i] = w

    top = '┌' + '┬'.join('─' * (w + 2) for w in col_widths) + '┐'
    mid = '├' + '┼'.join('─' * (w + 2) for w in col_widths) + '┤'
    bot = '└' + '┴'.join('─' * (w + 2) for w in col_widths) + '┘'

    header_line = '│ ' + ' │ '.join(_pad(str(h), col_widths[i]) for i, h in enumerate(headers)) + ' │'

    _write(top)
    _write(header_line)
    _write(mid)
    for row in rows:
        line = '│ ' + ' │ '.join(_pad(str(row[i]) if i < len(row) else '', col_widths[i]) for i in range(len(headers))) + ' │'
        _write(line)
    _write(bot)


def print_kv(data):
    """
    键值对格式化输出。

    Parameters
    ----------
    data : dict
    """
    if not data:
        return

    max_key_width = max(_display_width(str(k)) for k in data.keys())

    for key, value in data.items():
        padded_key = _pad(str(key), max_key_width)
        _write('{}:  {}'.format(padded_key, value))
