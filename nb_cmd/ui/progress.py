# -*- coding: utf-8 -*-
"""
纯标准库的进度条实现，无外部依赖。
"""
import sys
import time


class ProgressBar(object):
    """简易进度条，兼容 Python 3.7+"""

    def __init__(self, iterable=None, desc=None, total=None, bar_width=30, file=None):
        self.iterable = iterable
        self.desc = desc or ''
        self.bar_width = bar_width
        self.file = file or sys.stderr

        if total is not None:
            self.total = total
        elif iterable is not None:
            try:
                self.total = len(iterable)
            except TypeError:
                self.total = None
        else:
            self.total = None

        self.n = 0
        self.start_time = None

    def __iter__(self):
        self.start_time = time.time()
        self.n = 0
        for item in self.iterable:
            yield item
            self.n += 1
            self._display()
        self._display(final=True)
        self.file.write('\n')
        self.file.flush()

    def _display(self, final=False):
        elapsed = time.time() - self.start_time if self.start_time else 0

        if self.total and self.total > 0:
            frac = self.n / self.total
            percent = int(frac * 100)
            filled = int(self.bar_width * frac)
            bar = '█' * filled + '░' * (self.bar_width - filled)

            if elapsed > 0 and self.n > 0:
                rate = self.n / elapsed
                remaining = (self.total - self.n) / rate if rate > 0 else 0
                eta_str = _format_time(remaining)
                elapsed_str = _format_time(elapsed)
            else:
                eta_str = '?'
                elapsed_str = '00:00'

            line = '\r{} {} {}% {}/{} [{}<{}]'.format(
                self.desc, bar, percent, self.n, self.total,
                elapsed_str, eta_str
            )
        else:
            line = '\r{} {} 项已处理 [{:.1f}s]'.format(
                self.desc, self.n, elapsed
            )

        self.file.write(line)
        self.file.flush()


def _format_time(seconds):
    if seconds < 60:
        return '{:02d}:{:02d}'.format(0, int(seconds))
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    if minutes < 60:
        return '{:02d}:{:02d}'.format(minutes, secs)
    hours = minutes // 60
    minutes = minutes % 60
    return '{:d}:{:02d}:{:02d}'.format(hours, minutes, secs)


def progress(iterable, desc=None, total=None):
    """便捷函数：返回带进度条的可迭代对象"""
    return ProgressBar(iterable=iterable, desc=desc, total=total)
