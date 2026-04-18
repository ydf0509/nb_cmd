# -*- coding: utf-8 -*-
"""验证 _io_dispatch 分发器在多种场景下的线程安全"""
import sys
import io
import time
import threading

sys.path.insert(0, r'd:\codes\nb_cmd')

try:
    import queue as _queue
except ImportError:
    import Queue as _queue

from nb_cmd.core._io_dispatch import _tls, _DispatchWriter, install


def test_ws_isolation():
    """模拟两个 WebSocket 并发推送"""
    install()

    q_a = _queue.Queue()
    q_b = _queue.Queue()

    def ws_worker(name, q, count=30):
        _tls.output_queue = q
        for i in range(count):
            print('{}:{}'.format(name, i))
            time.sleep(0.005)
        _tls.output_queue = None

    t_a = threading.Thread(target=ws_worker, args=('WS_A', q_a))
    t_b = threading.Thread(target=ws_worker, args=('WS_B', q_b))
    t_a.start()
    t_b.start()
    t_a.join()
    t_b.join()

    text_a = ''.join(item[1] for item in _drain(q_a))
    text_b = ''.join(item[1] for item in _drain(q_b))

    assert 'WS_B' not in text_a, 'WS_A queue has WS_B data!'
    assert 'WS_A' not in text_b, 'WS_B queue has WS_A data!'
    assert text_a.count('WS_A:') == 30
    assert text_b.count('WS_B:') == 30
    print('[PASS] test_ws_isolation')


def test_api_isolation():
    """模拟两个 API 请求并发捕获"""
    install()

    results = {}

    def api_worker(name, count=30):
        cap = io.StringIO()
        _tls.captured_stdout = cap
        for i in range(count):
            print('{}:{}'.format(name, i))
            time.sleep(0.005)
        _tls.captured_stdout = None
        results[name] = cap.getvalue()

    t_a = threading.Thread(target=api_worker, args=('API_A',))
    t_b = threading.Thread(target=api_worker, args=('API_B',))
    t_a.start()
    t_b.start()
    t_a.join()
    t_b.join()

    assert 'API_B' not in results['API_A'], 'API_A captured API_B data!'
    assert 'API_A' not in results['API_B'], 'API_B captured API_A data!'
    assert results['API_A'].count('API_A:') == 30
    assert results['API_B'].count('API_B:') == 30
    print('[PASS] test_api_isolation')


def test_ws_and_api_mixed():
    """模拟 WebSocket 和 API 并发"""
    install()

    ws_q = _queue.Queue()
    api_result = {}

    def ws_worker():
        _tls.output_queue = ws_q
        for i in range(30):
            print('WS:{}'.format(i))
            time.sleep(0.005)
        _tls.output_queue = None

    def api_worker():
        cap = io.StringIO()
        _tls.captured_stdout = cap
        for i in range(30):
            print('API:{}'.format(i))
            time.sleep(0.005)
        _tls.captured_stdout = None
        api_result['text'] = cap.getvalue()

    t_ws = threading.Thread(target=ws_worker)
    t_api = threading.Thread(target=api_worker)
    t_ws.start()
    t_api.start()
    t_ws.join()
    t_api.join()

    ws_text = ''.join(item[1] for item in _drain(ws_q))
    api_text = api_result['text']

    assert 'API:' not in ws_text, 'WS queue has API data!'
    assert 'WS:' not in api_text, 'API captured WS data!'
    assert ws_text.count('WS:') == 30
    assert api_text.count('API:') == 30
    print('[PASS] test_ws_and_api_mixed')


def test_queue_priority_over_capture():
    """output_queue 优先级高于 captured_stdout"""
    install()

    q = _queue.Queue()
    cap = io.StringIO()

    def worker():
        _tls.output_queue = q
        _tls.captured_stdout = cap
        print('PRIORITY_TEST')
        _tls.output_queue = None
        _tls.captured_stdout = None

    t = threading.Thread(target=worker)
    t.start()
    t.join()

    q_text = ''.join(item[1] for item in _drain(q))
    assert 'PRIORITY_TEST' in q_text, 'Should go to queue'
    assert cap.getvalue() == '', 'Should NOT go to StringIO when queue is set'
    print('[PASS] test_queue_priority_over_capture')


def _drain(q):
    items = []
    while not q.empty():
        items.append(q.get_nowait())
    return items


if __name__ == '__main__':
    test_ws_isolation()
    test_api_isolation()
    test_ws_and_api_mixed()
    test_queue_priority_over_capture()
    print('\n=== All tests passed! ===')
