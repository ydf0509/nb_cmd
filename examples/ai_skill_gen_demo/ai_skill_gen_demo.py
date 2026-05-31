# -*- coding: utf-8 -*-
"""
AI Skill 自动生成演示 —— nb_cmd 第七种能力。

本示例演示如何将一个普通的 NbCmd 工具类，一键生成符合
agentskills.io 国际开放标准的 AI Skill 文件夹，让 Cursor、
Claude Code、Codex 等 AI Agent 能自动识别并正确使用你的工具。

功能:
    - 定义一个带全局参数 + 多级子命令组的 DevOps 工具
    - 一键生成 AI Skill 文件夹（仅 SKILL.md）
    - 演示 SkillGen 的各种配置选项

用法:
    # 1. 直接运行（Python 本地调用 + SkillGen 演示）
    python ai_skill_gen_demo.py

    # 2. CLI 模式
    python ai_skill_gen_demo.py --env staging deploy --version 2.1.0

    # 3. Web UI 模式
    python ai_skill_gen_demo.py --web --web-port 8086

    # 4. TUI 模式
    python ai_skill_gen_demo.py --tui
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from dataclasses import dataclass
from typing import Annotated
from nb_cmd import NbCmd, SkillGen


# ==================== 1. 全局上下文 ====================

@dataclass
class DevCtx:
    """DevOps 全局上下文"""
    env: str = 'prod'
    region: str = 'us-east'
    verbose: bool = False


# ==================== 2. 子命令组 ====================

class DbCmd(NbCmd):
    """数据库管理 (二级子命令组)"""
    nbctx: DevCtx

    def migrate(self,
                dry_run: Annotated[bool, '仅预览，不执行'] = False,
                target: Annotated[str, '目标迁移版本'] = 'latest'):
        """执行数据库迁移"""
        prefix = '[DRY-RUN]' if dry_run else '[EXEC]'
        print(f'{prefix} [{self.nbctx.env}/{self.nbctx.region}] 迁移到 {target}')

    def backup(self, compress: Annotated[bool, '启用压缩'] = True):
        """备份数据库"""
        fmt = 'tar.gz' if compress else 'sql'
        print(f'[{self.nbctx.env}] 备份数据库 → backup.{fmt}')

    def restore(self, file: Annotated[str, '备份文件路径']):
        """从备份恢复数据库"""
        print(f'[{self.nbctx.env}] 恢复数据库: {file}')


class DeployCmd(NbCmd):
    """部署管理 (二级子命令组)"""
    nbctx: DevCtx

    def rolling(self,
                version: Annotated[str, '部署版本号', 'v'],
                batch_size: Annotated[int, '每批实例数'] = 3,
                wait: Annotated[int, '每批等待秒数'] = 30):
        """滚动部署"""
        print(f'[{self.nbctx.env}] 滚动部署 v{version} (每批 {batch_size} 台, 等待 {wait}s)')

    def canary(self,
               version: Annotated[str, '部署版本号', 'v'],
               traffic: Annotated[float, '流量比例 0-1'] = 0.1):
        """金丝雀部署"""
        print(f'[{self.nbctx.env}] 金丝雀部署 v{version} (流量 {traffic*100:.0f}%)')

    def rollback(self, steps: Annotated[int, '回退步数'] = 1):
        """回滚到上一个版本"""
        print(f'[{self.nbctx.env}] 回滚 {steps} 个版本')


class MonitorCmd(NbCmd):
    """监控告警 (二级子命令组)"""
    nbctx: DevCtx

    def status(self, service: Annotated[str, '服务名'] = None):
        """查看服务状态"""
        target = service or 'all'
        print(f'[{self.nbctx.env}] 服务状态: {target}')

    def alert(self, rule: Annotated[str, '告警规则名'], threshold: Annotated[float, '阈值']):
        """配置告警规则"""
        print(f'[{self.nbctx.env}] 告警规则: {rule} > {threshold}')


# ==================== 3. 顶层工具类 ====================

class DevOpsTool(NbCmd):
    """
    DevOps 运维工具 —— AI Skill 自动生成演示。

    支持数据库管理、部署管理、监控告警三大模块。
    全局参数 env/region/verbose 自动穿透到所有子命令组。
    """
    nbctx: DevCtx

    class Meta:
        name = 'devops-tool'
        version = '1.0.0'
        description = 'DevOps 运维工具，支持数据库管理、部署、监控等操作。'
        enable_exec = False

    def __init__(self,
                 env: Annotated[str, '运行环境 prod/staging/dev'] = 'prod',
                 region: Annotated[str, '部署区域'] = 'us-east',
                 verbose: Annotated[bool, '输出详细信息'] = False):
        self.env = env
        self.region = region
        self.verbose = verbose

    def make_nbctx(self):
        return DevCtx(env=self.env, region=self.region, verbose=self.verbose)

    sub_commands = {
        'db': DbCmd,
        'deploy': DeployCmd,
        'monitor': MonitorCmd,
    }

    def health(self):
        """查看全局健康状态"""
        print(f'=== 全局健康检查 [{self.nbctx.env}/{self.nbctx.region}] ===')
        print('  Database: OK')
        print('  API:      OK')
        print('  Cache:    OK')

    def version(self):
        """查看工具版本"""
        return {'tool': 'devops-tool', 'version': '1.0.0', 'env': self.nbctx.env}


# ==================== 4. SkillGen 演示 ====================

def demo_basic():
    """演示 1: 最简用法 —— 一键生成 Skill"""
    print('\n' + '='*60)
    print('演示 1: SkillGen 最简用法')
    print('='*60)

    base_dir = os.path.join(os.path.dirname(__file__), 'skills')
    g = SkillGen(DevOpsTool, base_dir=base_dir, script='ai_skill_gen_demo.py')
    path = g.gen()
    print(f'\nSkill 已生成到: {path}')
    print(f'  SKILL.md -> {os.path.join(path, "SKILL.md")}')


def demo_full():
    """演示 2: 完整用法 —— 自定义元数据 + 环境提示"""
    print('\n' + '='*60)
    print('演示 2: SkillGen 完整用法（含环境提示 + 元数据）')
    print('='*60)

    base_dir = os.path.join(os.path.dirname(__file__), 'skills')
    priority_prompt = (
        '## 运行环境说明\n'
        '- 线上服务器：使用 `/usr/bin/python3`，脚本位于 `/opt/devops/ai_skill_gen_demo.py`\n'
        '- 本地开发：使用 `python`，脚本位于当前目录\n'
        '- 运行前请确保设置 `PYTHONPATH=/opt/devops`（线上）或项目根目录（本地）'
    )

    g = SkillGen(
        DevOpsTool,
        base_dir=base_dir,
        name='devops-tool-full',
        script='ai_skill_gen_demo.py',
        description='DevOps 运维工具 —— 数据库迁移/备份/恢复、滚动/金丝雀部署、服务监控。当需要执行运维操作时使用。',
        license='MIT',
        compatibility='Requires Python 3.8+ and nb_cmd >= 0.2.0',
        metadata={'author': 'ops-team', 'version': '1.0', 'category': 'devops'},
        user_highest_priority_skill_prompt=priority_prompt,
        include_python_examples=True,
    )
    path = g.gen()
    print(f'\nSkill 已生成到: {path}')
    print(f'  SKILL.md -> OK')


def demo_string_only():
    """演示 3: 仅生成 SKILL.md 内容字符串（不写入文件）"""
    print('\n' + '='*60)
    print('演示 3: 仅生成 SKILL.md 字符串')
    print('='*60)

    g = SkillGen(DevOpsTool, base_dir='/tmp', script='ai_skill_gen_demo.py')
    content = g.gen_skill_md()

    print(f'\nSKILL.md 内容长度: {len(content)} 字符, {len(content.splitlines())} 行')
    print('\n--- 前 20 行预览 ---')
    for i, line in enumerate(content.splitlines()[:20], 1):
        print(f'  {i:2}: {line}')
    print('  ...')


def demo_python_examples():
    """演示 4: 开启 Python 调用示例"""
    print('\n' + '='*60)
    print('演示 4: 开启 Python 调用示例')
    print('='*60)

    base_dir = os.path.join(os.path.dirname(__file__), 'skills')
    g = SkillGen(
        DevOpsTool,
        base_dir=base_dir,
        name='devops-tool-py',
        script='ai_skill_gen_demo.py',
        include_python_examples=True,
    )
    path = g.gen()
    print(f'\nSkill 已生成到: {path}')

    skill_md = os.path.join(path, 'SKILL.md')
    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()
    has_python = '```python' in content
    has_cli = '```bash' in content
    print(f'  包含 Python 示例: {has_python}')
    print(f'  包含 CLI 示例: {has_cli}')


def print_generated_skills():
    """打印生成的 Skill 文件夹结构"""
    print('\n' + '='*60)
    print('生成的 Skill 目录结构')
    print('='*60)

    skills_dir = os.path.join(os.path.dirname(__file__), 'skills')
    if not os.path.exists(skills_dir):
        print('(无)')
        return

    for root, dirs, files in os.walk(skills_dir):
        level = root.replace(skills_dir, '').count(os.sep)
        indent = '  ' * level
        print(f'{indent}{os.path.basename(root)}/')
        subindent = '  ' * (level + 1)
        for f in files:
            print(f'{subindent}{f}')


# ==================== 5. 入口 ====================

if __name__ == '__main__':
    import sys as _sys

    if len(_sys.argv) > 1:
        # CLI / Web / API / TUI 模式
        DevOpsTool().run()
    else:
        # 本地直接调用演示
        print('='*60)
        print('AI Skill 自动生成演示')
        print('='*60)

        # 先清理旧的生成结果
        skills_dir = os.path.join(os.path.dirname(__file__), 'skills')
        if os.path.exists(skills_dir):
            import shutil
            shutil.rmtree(skills_dir)
            print('\n已清理旧的 skills/ 目录')

        # 运行各种演示
        demo_basic()
        demo_full()
        demo_string_only()
        demo_python_examples()
        print_generated_skills()

        print('\n' + '='*60)
        print('所有演示完成！')
        print('='*60)
        print(f'\n查看生成的 Skill 文件:')
        print(f'  {skills_dir}')
        print('\n你也可以运行 CLI 模式测试:')
        print(f'  python ai_skill_gen_demo.py --env staging db migrate --dry-run')
