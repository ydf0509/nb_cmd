# -*- coding: utf-8 -*-
"""
参数持久化模块 —— 自动保存/恢复上一次执行的参数。
"""
import json
import os


class ConfigManager(object):
    """管理参数持久化到 JSON 文件"""

    def __init__(self, config_file=None):
        if config_file:
            self.config_file = os.path.expanduser(config_file)
        else:
            self.config_file = None
        self._data = {}
        if self.config_file:
            self._load()

    def _load(self):
        if self.config_file and os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self._data = json.load(f)
            except Exception:
                self._data = {}

    def save_args(self, command, kwargs):
        """保存命令的参数"""
        if not self.config_file:
            return
        serializable = {}
        for k, v in kwargs.items():
            try:
                json.dumps(v)
                serializable[k] = v
            except (TypeError, ValueError):
                serializable[k] = str(v)
        self._data[command] = serializable
        self._write()

    def load_args(self, command):
        """加载命令上次保存的参数"""
        return self._data.get(command, {})

    def _write(self):
        if not self.config_file:
            return
        dir_path = os.path.dirname(self.config_file)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass
