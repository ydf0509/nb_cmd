# -*- coding: utf-8 -*-
"""
线程安全的 stdout/stderr 分发器。

web_mode 和 api_mode 共用同一个 threading.local() + 分发器，
避免并发请求之间 stdout 串流。

用法:
    注册输出目标:
        _tls.output_queue = some_queue        # WebSocket 推送（队列模式）
        _tls.captured_stdout = StringIO()     # API 捕获（StringIO 模式）
        _tls.captured_stderr = StringIO()

    注销:
        _tls.output_queue = None
        _tls.captured_stdout = None
        _tls.captured_stderr = None

    没有注册时, 写到原始 sys.stdout / sys.stderr。
"""
import sys
import threading

_tls = threading.local()
_original_stdout = sys.stdout
_original_stderr = sys.stderr


class _DispatchWriter(object):
    """
    线程安全的 stdout/stderr 替代品。
    按优先级检查当前线程的输出目标:
      1. _tls.output_queue     → put((stream_type, data))     (WebSocket)
      2. _tls.captured_stdout  → write(data)                  (API StringIO)
      3. 原始流                → write(data)                  (服务器控制台)
    """
    def __init__(self, original, stream_type):
        self._orig = original
        self._type = stream_type
        self._cap_attr = 'captured_stdout' if stream_type == 'stdout' else 'captured_stderr'
        self.encoding = getattr(original, 'encoding', 'utf-8')

    def write(self, data):
        if not data:
            return
        q = getattr(_tls, 'output_queue', None)
        if q is not None:
            q.put((self._type, data))
            return
        cap = getattr(_tls, self._cap_attr, None)
        if cap is not None:
            cap.write(data)
            return
        self._orig.write(data)

    def flush(self):
        self._orig.flush()

    def isatty(self):
        return True

    def fileno(self):
        return self._orig.fileno()

    def __getattr__(self, name):
        return getattr(self._orig, name)


def install():
    """安装分发器（幂等，多次调用安全）"""
    if not isinstance(sys.stdout, _DispatchWriter):
        sys.stdout = _DispatchWriter(_original_stdout, 'stdout')
        sys.stderr = _DispatchWriter(_original_stderr, 'stderr')
