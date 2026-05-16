# -*- coding: utf-8 -*-
"""
向 nbcmd 的 SQLite 数据库预置 20 条 Windows 11 最常用命令。
运行: python tests/ai_codes/insert_win11_commands.py
"""
import os
import sqlite3

DB_DIR = os.path.join(os.path.expanduser('~'), '.nb_cmd')
DB_PATH = os.path.join(DB_DIR, 'nb_cmd_web.db')

WIN11_COMMANDS = [
    ("查看网络配置", "exec ipconfig /all"),
    ("查看端口占用", "exec netstat -ano"),
    ("查看进程列表", "exec tasklist"),
    ("查看系统信息", "exec systeminfo"),
    ("系统文件修复", "exec sfc /scannow"),
    ("修复系统映像", "exec DISM /Online /Cleanup-Image /RestoreHealth"),
    ("查看磁盘空间", "exec wmic logicaldisk get size,freespace,caption"),
    ("查看WiFi密码", 'exec netsh wlan show profile name="WiFi名称" key=clear'),
    ("查看已保存WiFi", "exec netsh wlan show profiles"),
    ("刷新DNS缓存", "exec ipconfig /flushdns"),
    ("查看路由表", "exec route print"),
    ("测试网络连通", "exec ping -n 4 8.8.8.8"),
    ("追踪路由", "exec tracert 8.8.8.8"),
    ("查看环境变量", "exec set"),
    ("清理临时文件", r"exec del /q/f/s %TEMP%\*"),
    ("查看已安装程序", "exec wmic product get name,version"),
    ("强制结束进程", "exec taskkill /F /IM 进程名.exe"),
    ("查看开机启动项", "exec wmic startup get caption,command"),
    ("查看共享目录", "exec net share"),
    ("快速关机重启", "exec shutdown /r /t 0"),
]


def main():
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        'CREATE TABLE IF NOT EXISTS saved_commands '
        '(id INTEGER PRIMARY KEY AUTOINCREMENT, '
        'command TEXT UNIQUE NOT NULL, '
        'alias TEXT DEFAULT NULL, '
        'created_at TEXT DEFAULT CURRENT_TIMESTAMP)')
    try:
        conn.execute('ALTER TABLE saved_commands ADD COLUMN alias TEXT DEFAULT NULL')
    except Exception:
        pass

    inserted = 0
    skipped = 0
    for alias, cmd in WIN11_COMMANDS:
        try:
            conn.execute(
                'INSERT OR IGNORE INTO saved_commands (command, alias) VALUES (?, ?)',
                (cmd, alias))
            if conn.total_changes > inserted + skipped:
                inserted += 1
            else:
                skipped += 1
        except Exception as e:
            print(f"  跳过: {alias} -> {e}")
            skipped += 1

    conn.commit()

    total = conn.execute('SELECT COUNT(*) FROM saved_commands').fetchone()[0]
    conn.close()

    print(f"数据库路径: {DB_PATH}")
    print(f"新插入: {inserted} 条")
    print(f"已存在(跳过): {skipped} 条")
    print(f"收藏夹总计: {total} 条")


if __name__ == '__main__':
    main()
