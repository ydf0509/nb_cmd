# -*- coding: utf-8 -*-
"""
参数校验装饰器。
"""
import functools


def validate(**validators):
    """
    参数校验装饰器。
    每个关键字参数是一个 lambda/callable，接收参数值，返回 True/False。

    示例::

        @validate(port=lambda x: 1 <= x <= 65535)
        def deploy(self, host: str, port: int = 22):
            ...

    校验失败时抛出 ValueError。
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            import inspect
            sig = inspect.signature(func)
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()

            for param_name, check_fn in validators.items():
                if param_name in bound.arguments:
                    value = bound.arguments[param_name]
                    if not check_fn(value):
                        raise ValueError(
                            '参数 {} 校验失败 (当前值: {})'.format(param_name, value)
                        )
            return func(*args, **kwargs)
        return wrapper
    return decorator
