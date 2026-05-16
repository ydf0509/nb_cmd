# -*- coding: utf-8 -*-
"""修正收藏命令格式: exec --cmd "xxx" -> exec xxx"""
import sqlite3
import os
import re

DB_PATH = os.path.expanduser('~/.nb_cmd/nb_cmd_web.db')
conn = sqlite3.connect(DB_PATH)

rows = conn.execute('SELECT id, command, alias FROM saved_commands').fetchall()
updated = 0
for row_id, cmd, alias in rows:
    m = re.match(r'^exec\s+--cmd\s+"(.+)"$', cmd)
    if not m:
        m = re.match(r"^exec\s+--cmd\s+'(.+)'$", cmd)
    if m:
        raw_cmd = m.group(1)
        new_cmd = f'exec {raw_cmd}'
        conn.execute('UPDATE saved_commands SET command = ? WHERE id = ?', (new_cmd, row_id))
        updated += 1
        print(f'  [{alias}] {cmd}  ->  {new_cmd}')

conn.commit()
print(f'\n已更新 {updated} 条')

print('\n--- 最终结果 ---')
rows2 = conn.execute('SELECT alias, command FROM saved_commands ORDER BY id').fetchall()
for alias, cmd in rows2:
    print(f'  [{alias}] {cmd}')

conn.close()
