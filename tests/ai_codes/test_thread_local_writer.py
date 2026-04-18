# -*- coding: utf-8 -*-
"""验证 _ThreadLocalWriter 在并发线程下不会串流"""
import sys
import time
import threading

sys.path.insert(0, r'd:\codes\nb_cmd')

try:
    import queue as _queue
except ImportError:
    import Queue as _queue


_tls = threading.local()


class _ThreadLocalWriter(object):
    def __init__(self, original_stream, stream_type):
        self._orig = original_stream
        self._type = stream_type
        self.encoding = getattr(original_stream, 'encoding', 'utf-8')

    def write(self, data):
        q = getattr(_tls, 'output_queue', None)
        if q is not None and data:
            q.put((self._type, data))
        elif data:
            self._orig.write(data)

    def flush(self):
        self._orig.flush()


def worker(name, q, count=20):
    _tls.output_queue = q
    for i in range(count):
        print('{}:{}'.format(name, i))
        time.sleep(0.01)
    _tls.output_queue = None


if __name__ == '__main__':
    original_stdout = sys.stdout
    sys.stdout = _ThreadLocalWriter(original_stdout, 'stdout')

    q_a = _queue.Queue()
    q_b = _queue.Queue()

    t_a = threading.Thread(target=worker, args=('A', q_a, 20))
    t_b = threading.Thread(target=worker, args=('B', q_b, 20))

    t_a.start()
    t_b.start()
    t_a.join()
    t_b.join()

    sys.stdout = original_stdout

    raw_a = []
    while not q_a.empty():
        raw_a.append(q_a.get()[1])
    raw_b = []
    while not q_b.empty():
        raw_b.append(q_b.get()[1])

    text_a = ''.join(raw_a)
    text_b = ''.join(raw_b)

    print('Queue A text: {!r}...'.format(text_a[:60]))
    print('Queue B text: {!r}...'.format(text_b[:60]))

    assert 'B:' not in text_a, 'Queue A contains B messages! LEAK!'
    assert 'A:' not in text_b, 'Queue B contains A messages! LEAK!'
    assert text_a.count('A:') == 20, 'Expected 20 A messages, got {}'.format(text_a.count('A:'))
    assert text_b.count('B:') == 20, 'Expected 20 B messages, got {}'.format(text_b.count('B:'))

    print('\nNo cross-contamination! All 20+20 messages correctly isolated.')
