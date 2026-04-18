# -*- coding: utf-8 -*-
"""
Python类型 → argparse类型/nargs/choices 的映射工具。
兼容 Python 3.7+。
"""
import enum
from pathlib import Path


def _get_origin(tp):
    """兼容 3.7 的 typing.get_origin"""
    return getattr(tp, '__origin__', None)


def _get_args(tp):
    """兼容 3.7 的 typing.get_args"""
    return getattr(tp, '__args__', ())


def is_optional(tp):
    """判断是否是 Optional[X] (即 Union[X, None])"""
    origin = _get_origin(tp)
    if origin is not None:
        import typing
        if origin is getattr(typing, 'Union', None):
            args = _get_args(tp)
            return type(None) in args
    return False


def unwrap_optional(tp):
    """Optional[X] → X"""
    if is_optional(tp):
        args = _get_args(tp)
        non_none = [a for a in args if a is not type(None)]
        if len(non_none) == 1:
            return non_none[0]
    return tp


def is_enum_type(tp):
    return isinstance(tp, type) and issubclass(tp, enum.Enum)


def is_list_type(tp):
    origin = _get_origin(tp)
    return origin is list


def is_tuple_type(tp):
    origin = _get_origin(tp)
    return origin is tuple


def get_argparse_type(python_type):
    """Python类型 → argparse type 参数"""
    real_type = unwrap_optional(python_type)

    if real_type is bool:
        return None
    if real_type in (int, float, str):
        return real_type
    if real_type is Path:
        return str
    if is_enum_type(real_type):
        return str
    if is_list_type(real_type):
        args = _get_args(real_type)
        if args:
            inner = args[0]
            if inner in (int, float, str):
                return inner
        return str
    if is_tuple_type(real_type):
        return str
    return str


def get_nargs(python_type):
    """Python类型 → argparse nargs"""
    real_type = unwrap_optional(python_type)
    if is_list_type(real_type):
        return '+'
    if is_tuple_type(real_type):
        args = _get_args(real_type)
        if args:
            return len(args)
    return None


def get_choices(python_type):
    """Python类型 → argparse choices"""
    real_type = unwrap_optional(python_type)
    if is_enum_type(real_type):
        return [e.value for e in real_type]
    return None


def convert_value(value, python_type):
    """将 argparse 解析出的字符串值转为目标 Python 类型"""
    real_type = unwrap_optional(python_type)

    if value is None:
        return None

    if real_type is bool:
        return value

    if real_type in (int, float, str):
        return real_type(value)

    if real_type is Path:
        return Path(value)

    if is_enum_type(real_type):
        for member in real_type:
            if member.value == value:
                return member
        return real_type(value)

    if is_list_type(real_type):
        args = _get_args(real_type)
        inner = args[0] if args else str
        if isinstance(value, (list, tuple)):
            return [inner(v) for v in value]
        return [inner(value)]

    if is_tuple_type(real_type):
        args = _get_args(real_type)
        if isinstance(value, (list, tuple)) and args:
            return tuple(args[i](value[i]) for i in range(min(len(args), len(value))))
        return value

    return value


def type_display_name(python_type):
    """获取类型的可读显示名"""
    if hasattr(python_type, '__name__'):
        return python_type.__name__
    return str(python_type).replace('typing.', '')
