# -*- coding: utf-8 -*-
"""全面测试 exec 在所有模式下的行为"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from nb_cmd import NbCmd
from nb_cmd.core.discovery import discover_commands
from nb_cmd.core.parser import build_parser, reassign_positionals


class TestApp(NbCmd):
    class Meta:
        enable_exec = True


def test_cli_exec():
    """测试 CLI 模式下 exec 的三种写法"""
    app = TestApp()
    commands = discover_commands(app, NbCmd, enable_exec=True)
    meta = app.Meta

    print("=" * 60)
    print("CLI 模式: exec 三种写法")
    print("=" * 60)

    tests = [
        ("位置传参", ['exec', 'echo hello']),
        ("长 flag", ['exec', '--cmd', 'echo hello']),
        ("短 flag", ['exec', '-c', 'echo hello']),
        ("位置传参(多词)", ['exec', 'ipconfig /all']),
        ("长 flag(多词)", ['exec', '--cmd', 'ipconfig /all']),
        ("短 flag(多词)", ['exec', '-c', 'ipconfig /all']),
    ]

    all_pass = True
    for desc, args in tests:
        parser = build_parser(app, commands, meta, base_cls=NbCmd)
        try:
            parsed = parser.parse_args(args)
            reassign_positionals(parsed)
            cmd_val = getattr(parsed, 'cmd', None)
            expected = args[-1] if '--cmd' in args or '-c' in args else args[1]
            ok = cmd_val == expected
            status = "PASS" if ok else "FAIL"
            print(f"  [{status}] {desc}: args={args} -> cmd='{cmd_val}' (expect '{expected}')")
            if not ok:
                all_pass = False
        except Exception as e:
            print(f"  [FAIL] {desc}: args={args} -> ERROR: {e}")
            all_pass = False

    return all_pass


def test_cli_exec_real():
    """实际执行 exec（用 echo 测试安全命令）"""
    import subprocess

    print("\n" + "=" * 60)
    print("CLI 模式: exec 实际执行测试")
    print("=" * 60)

    script = os.path.join(os.path.dirname(__file__), '..', '..', 'examples', 'five_in_one_demo.py')
    python = sys.executable

    tests = [
        ("位置", [python, script, 'exec', 'echo test_positional']),
        ("--cmd", [python, script, 'exec', '--cmd', 'echo test_flag']),
        ("-c", [python, script, 'exec', '-c', 'echo test_short']),
    ]

    all_pass = True
    for desc, cmd in tests:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            output = result.stdout.strip()
            expected = cmd[-1].replace('echo ', '')
            ok = expected in output
            status = "PASS" if ok else "FAIL"
            print(f"  [{status}] {desc}: output='{output}' (expect '{expected}')")
            if not ok:
                all_pass = False
                print(f"    stderr: {result.stderr.strip()}")
        except Exception as e:
            print(f"  [FAIL] {desc}: ERROR: {e}")
            all_pass = False

    return all_pass


def test_tui_parser():
    """测试 TUI 解析逻辑（模拟 _parse_cli_text 的核心部分）"""
    import inspect
    import shlex
    from nb_cmd.core.type_utils import convert_value

    print("\n" + "=" * 60)
    print("TUI 模式: 解析逻辑测试")
    print("=" * 60)

    app = TestApp()
    commands = discover_commands(app, NbCmd, enable_exec=True)

    def simulate_tui_parse(text):
        """模拟 TUI 的 _parse_cli_text 逻辑"""
        try:
            tokens = shlex.split(text)
        except ValueError:
            tokens = text.split()
        if not tokens:
            return None

        path_parts = []
        current_cmds = commands
        i = 0
        cmd_info = None
        while i < len(tokens):
            token = tokens[i]
            if token.startswith('-'):
                break
            py_name = token.replace('-', '_')
            if py_name not in current_cmds:
                break
            info = current_cmds[py_name]
            path_parts.append(py_name)
            if not info.get('is_group'):
                cmd_info = info
                i += 1
                break
            i += 1

        if not path_parts or cmd_info is None:
            return None
        cmd_path = '/'.join(path_parts)

        arg_tokens = tokens[i:]
        raw_kwargs = {}
        positional_tokens = []
        j = 0
        while j < len(arg_tokens):
            tok = arg_tokens[j]
            if tok.startswith('--'):
                key = tok[2:].replace('-', '_')
                if j + 1 < len(arg_tokens) and not arg_tokens[j + 1].startswith('-'):
                    raw_kwargs[key] = arg_tokens[j + 1]
                    j += 2
                else:
                    raw_kwargs[key] = True
                    j += 1
            elif tok.startswith('-') and len(tok) == 2:
                alias_map = cmd_info.get('arg_meta', {})
                matched = None
                for pn, am in alias_map.items():
                    if am and tok in am.aliases:
                        matched = pn
                        break
                key = matched or tok[1:]
                if j + 1 < len(arg_tokens) and not arg_tokens[j + 1].startswith('-'):
                    raw_kwargs[key] = arg_tokens[j + 1]
                    j += 2
                else:
                    raw_kwargs[key] = True
                    j += 1
            else:
                positional_tokens.append(tok)
                j += 1

        sig = cmd_info.get('signature')
        if sig and positional_tokens:
            pos_idx = 0
            for pname, param in sig.parameters.items():
                if pname == 'self' or pname in raw_kwargs:
                    continue
                if param.default is not inspect.Parameter.empty:
                    continue
                if pos_idx < len(positional_tokens):
                    raw_kwargs[pname] = positional_tokens[pos_idx]
                    pos_idx += 1
            if pos_idx < len(positional_tokens):
                last_required = None
                for pname, param in sig.parameters.items():
                    if pname == 'self':
                        continue
                    if param.default is inspect.Parameter.empty:
                        last_required = pname
                if last_required and last_required in raw_kwargs:
                    remaining = positional_tokens[pos_idx:]
                    raw_kwargs[last_required] = raw_kwargs[last_required] + ' ' + ' '.join(remaining)

        return cmd_path, raw_kwargs

    tests = [
        ('exec "echo hello"', 'echo hello'),
        ('exec --cmd "echo hello"', 'echo hello'),
        ('-c flag', None),
        ('exec ipconfig /all', 'ipconfig /all'),
        ('exec --cmd "ipconfig /all"', 'ipconfig /all'),
        ('exec -c "ipconfig /all"', 'ipconfig /all'),
        ('exec echo test', 'echo test'),
        ('exec --cmd "docker run --rm alpine"', 'docker run --rm alpine'),
    ]

    all_pass = True
    for text, expected in tests:
        if expected is None:
            continue
        result = simulate_tui_parse(text)
        if result is None:
            print(f"  [FAIL] '{text}' -> parse returned None")
            all_pass = False
            continue
        cmd_path, kwargs = result
        cmd_val = kwargs.get('cmd', '')
        ok = cmd_val == expected
        status = "PASS" if ok else "FAIL"
        print(f"  [{status}] '{text}' -> cmd='{cmd_val}' (expect '{expected}')")
        if not ok:
            all_pass = False

    # Test -c short alias specifically
    result = simulate_tui_parse('exec -c "ipconfig /all"')
    if result:
        cmd_path, kwargs = result
        cmd_val = kwargs.get('cmd', '')
        ok = cmd_val == 'ipconfig /all'
        print(f"  [{'PASS' if ok else 'FAIL'}] 'exec -c \"ipconfig /all\"' -> cmd='{cmd_val}' (expect 'ipconfig /all')")
        if not ok:
            all_pass = False

    return all_pass


if __name__ == '__main__':
    pass1 = test_cli_exec()
    pass2 = test_cli_exec_real()
    pass3 = test_tui_parser()

    print("\n" + "=" * 60)
    if pass1 and pass2 and pass3:
        print("全部测试通过!")
    else:
        print("有测试失败!")
        sys.exit(1)
