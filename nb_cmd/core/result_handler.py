# -*- coding: utf-8 -*-
"""
返回值自动处理模块。
根据返回值类型决定如何在 CLI / API 中展示结果。
"""
import json
from pathlib import Path

from ..ui.table import _display_width as _cjk_display_width


def handle_cli_result(result):
    """
    CLI 模式下自动处理方法返回值。

    规则:
    - None          → 不输出
    - str           → 直接 print
    - int / float   → 直接 print
    - dict          → JSON 格式化输出
    - list[dict]    → 表格输出（降级为 JSON）
    - list          → 每行一个
    - Path          → 输出路径字符串
    """
    if result is None:
        return

    if isinstance(result, str):
        print(result)
        return

    if isinstance(result, (int, float)):
        print(result)
        return

    if isinstance(result, dict):
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if isinstance(result, (list, tuple)):
        if result and isinstance(result[0], dict):
            _print_list_of_dicts_as_table(result)
        else:
            for item in result:
                print(item)
        return

    if isinstance(result, Path):
        print(str(result))
        return

    print(result)


def handle_api_result(result):
    """API 模式下处理返回值"""
    if result is None:
        return None

    if isinstance(result, (str, int, float)):
        return {"result": result}

    if isinstance(result, dict):
        return result

    if isinstance(result, (list, tuple)):
        return {"result": result}

    if isinstance(result, Path):
        return {"result": str(result)}

    return {"result": str(result)}


def _print_list_of_dicts_as_table(data):
    """简易表格输出 list[dict]，无外部依赖"""
    if not data:
        return

    headers = list(data[0].keys())
    col_widths = {}
    for h in headers:
        col_widths[h] = len(str(h))
    for row in data:
        for h in headers:
            val = str(row.get(h, ''))
            if len(val) > col_widths[h]:
                col_widths[h] = len(val)

    for h in headers:
        col_widths[h] = max(col_widths[h], _cjk_display_width(str(h)))
    for row in data:
        for h in headers:
            w = _cjk_display_width(str(row.get(h, '')))
            if w > col_widths[h]:
                col_widths[h] = w

    def _pad(text, width):
        dw = _cjk_display_width(text)
        return text + ' ' * (width - dw)

    sep_line = '+' + '+'.join('-' * (col_widths[h] + 2) for h in headers) + '+'
    header_line = '| ' + ' | '.join(_pad(str(h), col_widths[h]) for h in headers) + ' |'

    print(sep_line)
    print(header_line)
    print(sep_line)
    for row in data:
        vals = [_pad(str(row.get(h, '')), col_widths[h]) for h in headers]
        print('| ' + ' | '.join(vals) + ' |')
    print(sep_line)


