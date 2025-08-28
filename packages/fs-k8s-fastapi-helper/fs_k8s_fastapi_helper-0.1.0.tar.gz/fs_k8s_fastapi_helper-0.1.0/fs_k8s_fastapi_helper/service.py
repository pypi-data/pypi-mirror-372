"""
Kubernetes健康检查探针服务模块

提供FastAPI应用的Kubernetes健康检查探针集成功能。
"""

from contextlib import asynccontextmanager
from typing import Optional

from fastapi import APIRouter, FastAPI, Response
from starlette.testclient import TestClient

# 常量定义
STARTUP_PATH = "/k8s-helper/startup"
LIVENESS_PATH = "/k8s-helper/liveness"
READINESS_PATH = "/k8s-helper/readiness"


def install_k8s_health_probes(
    app: FastAPI,
    *,
    custom_readiness_path: Optional[str] = None,
) -> None:
    """
    为FastAPI应用安装Kubernetes健康检查探针

    Args:
        app: FastAPI应用实例
        custom_readiness_path: 可选的就绪检查目标路径。如果提供，就绪探针会检查该路径的响应状态

    Returns:
        None

    Example:
        ```python
        from fastapi import FastAPI
        from fs_k8s_fastapi_helper import install_k8s_health_probes

        app = FastAPI()
        install_k8s_health_probes(app, custom_readiness_path="/health")
        ```
    """
    router = APIRouter()

    @router.get(STARTUP_PATH)
    async def startup() -> dict[str, str]:
        """
        启动探针端点
        """
        return {"status": "ok"}

    @router.get(LIVENESS_PATH)
    async def liveness() -> dict[str, str]:
        """
        存活探针端点
        """
        return {"status": "ok"}

    @router.get(READINESS_PATH)
    def readiness(response: Response) -> dict[str, str | int]:
        """
        就绪探针端点

        如果设置了custom_readiness_path，会检查目标路径的响应状态。
        如果目标路径返回4xx或5xx状态码，就绪探针会返回503状态。

        Args:
            response: FastAPI响应对象
        """
        if not custom_readiness_path:
            return {"status": "ok"}  # 仅验证应用路由是否注册

        # 使用 TestClient 在内部发起请求
        with TestClient(app) as client:
            try:
                r = client.get(custom_readiness_path)
                if r.status_code >= 400:
                    response.status_code = 503
                    return {"status": "degraded", "target_status": r.status_code}
                return {"status": "ok"}
            except Exception as e:
                response.status_code = 503
                return {"status": "degraded", "error": type(e).__name__}

    app.include_router(router)

    # 保留 lifespan 兼容
    main_lifespan = app.router.lifespan_context

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        """应用生命周期管理器"""
        async with main_lifespan(app):
            yield

    app.router.lifespan_context = lifespan
