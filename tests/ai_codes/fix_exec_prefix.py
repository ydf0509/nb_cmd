# -*- coding: utf-8 -*-
"""给已插入的收藏命令加上 exec --cmd 前缀"""
import sqlite3
import os

DB_PATH = os.path.expanduser('~/.nb_cmd/nb_cmd_web.db')
conn = sqlite3.connect(DB_PATH)

rows = conn.execute('SELECT id, command, alias FROM saved_commands').fetchall()
updated = 0
for row_id, cmd, alias in rows:
    if not cmd.startswith('exec '):
        new_cmd = f'exec --cmd "{cmd}"'
        conn.execute('UPDATE saved_commands SET command = ? WHERE id = ?', (new_cmd, row_id))
        updated += 1
        print(f'  [{alias}] {cmd}  ->  {new_cmd}')

conn.commit()
print(f'\n已更新 {updated} 条')

print('\n--- 验证 ---')
rows2 = conn.execute('SELECT alias, command FROM saved_commands ORDER BY id').fetchall()
for alias, cmd in rows2:
    print(f'  [{alias}] {cmd}')

conn.close()
