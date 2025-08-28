"""
测试 fs_k8s_fastapi_helper.service 模块
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from fs_k8s_fastapi_helper import install_k8s_health_probes


@pytest.fixture
def app():
    """创建测试用的FastAPI应用"""
    app = FastAPI()
    return app


@pytest.fixture
def client(app):
    """创建测试客户端"""
    return TestClient(app)


class TestInstallK8sHealthProbes:
    """测试 install_k8s_health_probes 函数"""

    def test_install_probes_without_custom_readiness_path(self, app, client):
        """测试不设置custom_readiness_path的情况"""
        install_k8s_health_probes(app)

        # 测试启动探针
        response = client.get("/k8s-helper/startup")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

        # 测试存活探针
        response = client.get("/k8s-helper/liveness")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

        # 测试就绪探针
        response = client.get("/k8s-helper/readiness")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_install_probes_with_custom_readiness_path_success(self, app, client):
        """测试设置custom_readiness_path且目标路径正常的情况"""

        # 添加一个健康的端点
        @app.get("/health")
        def health():
            return {"status": "healthy"}

        install_k8s_health_probes(app, custom_readiness_path="/health")

        # 测试启动探针
        response = client.get("/k8s-helper/startup")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

        # 测试存活探针
        response = client.get("/k8s-helper/liveness")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

        # 测试就绪探针
        response = client.get("/k8s-helper/readiness")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_install_probes_with_custom_readiness_path_failure(self, app, client):
        """测试设置custom_readiness_path但目标路径失败的情况"""

        # 添加一个返回错误的端点
        @app.get("/error")
        def error():
            from fastapi import HTTPException

            raise HTTPException(status_code=503, detail="service unavailable")

        install_k8s_health_probes(app, custom_readiness_path="/error")

        # 测试启动探针
        response = client.get("/k8s-helper/startup")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

        # 测试存活探针
        response = client.get("/k8s-helper/liveness")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

        # 测试就绪探针 - 应该返回503
        response = client.get("/k8s-helper/readiness")
        assert response.status_code == 503
        assert response.json() == {"status": "degraded", "target_status": 503}

    def test_install_probes_with_nonexistent_custom_readiness_path(self, app, client):
        """测试设置custom_readiness_path但目标路径不存在的情况"""
        install_k8s_health_probes(app, custom_readiness_path="/nonexistent")

        # 测试启动探针
        response = client.get("/k8s-helper/startup")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

        # 测试存活探针
        response = client.get("/k8s-helper/liveness")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

        # 测试就绪探针 - 应该返回503
        response = client.get("/k8s-helper/readiness")
        assert response.status_code == 503
        assert response.json() == {"status": "degraded", "target_status": 404}

    def test_lifespan_compatibility(self, app):
        """测试lifespan兼容性"""
        # 记录原始的lifespan
        original_lifespan = app.router.lifespan_context

        install_k8s_health_probes(app)

        # 验证lifespan仍然存在
        assert app.router.lifespan_context is not None
        assert app.router.lifespan_context != original_lifespan

    @pytest.mark.asyncio
    async def test_lifespan_execution(self, app):
        """测试lifespan执行"""
        install_k8s_health_probes(app)

        # 执行lifespan
        async with app.router.lifespan_context(app):
            # 在lifespan上下文中执行一些操作
            pass


class TestProbeEndpoints:
    """测试探针端点"""

    def test_startup_endpoint(self, app, client):
        """测试启动探针端点"""
        install_k8s_health_probes(app)

        response = client.get("/k8s-helper/startup")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_liveness_endpoint(self, app, client):
        """测试存活探针端点"""
        install_k8s_health_probes(app)

        response = client.get("/k8s-helper/liveness")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_readiness_endpoint(self, app, client):
        """测试就绪探针端点"""
        install_k8s_health_probes(app)

        response = client.get("/k8s-helper/readiness")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_probe_endpoints_not_duplicated(self, app, client):
        """测试探针端点不会重复注册"""
        install_k8s_health_probes(app)
        install_k8s_health_probes(app)  # 再次调用

        # 应该只有一个启动探针端点
        response = client.get("/k8s-helper/startup")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

        # 应该只有一个存活探针端点
        response = client.get("/k8s-helper/liveness")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

        # 应该只有一个就绪探针端点
        response = client.get("/k8s-helper/readiness")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_all_probe_endpoints_exist(self, app, client):
        """测试所有探针端点都存在且正常工作"""
        install_k8s_health_probes(app)

        # 测试所有探针端点
        probe_endpoints = [
            "/k8s-helper/startup",
            "/k8s-helper/liveness",
            "/k8s-helper/readiness",
        ]

        for endpoint in probe_endpoints:
            response = client.get(endpoint)
            assert response.status_code == 200
            assert response.json() == {"status": "ok"}
