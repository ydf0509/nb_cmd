# -*- coding: utf-8 -*-
"""
nb_cmd 继承覆写 demo —— 对应设计文档 5.2 和附录B

用法:
    python demo_inherit.py deploy web-01 --version v2.0
    python demo_inherit.py status
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from nb_cmd import NbCmd, cmdui


class BaseDeploy(NbCmd):
    """基础部署工具"""

    def deploy(self, host: str, version: str = "latest"):
        """部署服务到目标主机"""
        self._pre_deploy(host)
        self._do_deploy(host, version)
        self._post_deploy(host)
        cmdui.success('{}@{} 已部署到 {}'.format("app", version, host))

    def status(self):
        """查看部署状态"""
        cmdui.kv({
            "部署方式": self._deploy_type(),
            "最后部署": "2026-04-17 15:00",
            "状态": "运行中",
        })

    def _deploy_type(self):
        return "基础部署"

    def _pre_deploy(self, host):
        cmdui.info('部署前检查: {}'.format(host))

    def _do_deploy(self, host, version):
        cmdui.info('上传文件到 {} ...'.format(host))
        cmdui.info('重启服务 ...')

    def _post_deploy(self, host):
        cmdui.info('验证服务状态: OK')


class DockerDeploy(BaseDeploy):
    """Docker部署——只需覆写部署逻辑"""

    def _deploy_type(self):
        return "Docker"

    def _do_deploy(self, host, version):
        cmdui.info('docker pull app:{}'.format(version))
        cmdui.info('docker-compose up -d')


class K8sDeploy(BaseDeploy):
    """K8s部署——覆写部署逻辑，还新增了 scale 命令"""

    def _deploy_type(self):
        return "Kubernetes"

    def _do_deploy(self, host, version):
        cmdui.info('kubectl set image deployment/app app=app:{}'.format(version))
        cmdui.info('kubectl rollout status deployment/app')

    def scale(self, replicas: int = 3):
        """扩缩容（K8s特有命令）"""
        cmdui.info('kubectl scale deployment/app --replicas={}'.format(replicas))
        cmdui.success('app 已扩缩至 {} 个副本'.format(replicas))


if __name__ == '__main__':
    import sys as _sys
    ops_map = {'base': BaseDeploy, 'docker': DockerDeploy, 'k8s': K8sDeploy}
    if len(_sys.argv) > 1 and _sys.argv[1] in ops_map:
        mode = _sys.argv.pop(1)
        ops_map[mode]().run()
    else:
        BaseDeploy().run()
