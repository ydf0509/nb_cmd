---
noteId: "54b5d5a05ca811f1b0e849262af76e51"
tags: []

---



## 现在nbcmd 这个包能一次编写，生成多种用途，例如 命令行 web api tui markdown  python本地调用，

因为现在ai编程很火爆，尤其是skills

你参考cursor里面的skilsl的写法
C:\Users\ydf19\.cursor\skills-cursor

你要学习 agentskills.io 这个国际协议的最佳实践

生成的skill必须包含题头， 例如
---
name: shell
description: >-
  Runs the rest of a /shell request as a literal shell command. Use only when
  the user explicitly invokes /shell and wants the following text executed
  directly in the terminal.
---

生成的skill是个文件夹，你生成的文件夹名字和skill题头的名字必须一致


## ai 可以参考 CmdGen 这个类的实现，来生成skill文件夹




需要修改的
g = SkillGen(MyApp, output_dir='./skills/my-app', generate_scripts=True)

中的output_dir不应该让用户选，用户只能指定skill的名称，skill的文件夹名字就是skill的名称

SkillGen 去掉以下参数

去掉以下功能，只生成skill.md既可
 include_tui_guide : bool, optional
        是否在 SKILL.md 中包含 TUI 使用指南（默认 False）
    generate_scripts : bool, optional
        是否生成 scripts/ 辅助脚本（默认 False）
    generate_references : bool, optional
        是否生成 references/ 参考文档（默认 False）
    max_skill_md_lines : int, optional
        SKILL.md 最大行数（默认 500），超过则分流到 references/

修改include_python_examples的默认值为false
    include_python_examples : bool, optional
        是否在 SKILL.md 中包含 Python 调用示例（默认 True）

增加一个入参，user_highest_priority_skill_prompt
用户可以灵活指定一个最高优先级的提示语，这个要放在skill.md 的显要位置

例如用户可以告诉ai，如果是linux线上服务器，用什么python解释器，本地用什么python解释器，
nbcmd脚本位置在不同环境时候脚本在哪里 ，例如告诉ai运行脚本前要设置 PYTHONPATH 环境变量等等

这个作为最高优先级的skill提示，放在题头下面的显要位置






- Boolean flags default to `False`; add the flag to set it to `True`.
- Subcommand groups are accessed via space or dot, e.g., `<group> <command>` or `<group>.<command>`.

这里是不是有幻觉 <group>.<command> 不支持. 吧？
然后需要加上 ，命令行有NbCmd三方包开发实现，继承NbCmd的类中的实例方法就是命令，如果ai不确定命令对应的具体逻辑，可以去看命令行实现的方法源码
