"""
示例应用：展示如何使用 fs-k8s-fastapi-helper

这个文件演示了如何在FastAPI应用中集成Kubernetes健康检查探针。
"""

from fastapi import FastAPI

from fs_k8s_fastapi_helper import install_k8s_health_probes

# 创建FastAPI应用
app = FastAPI(
    title="FS K8s Python Helper Demo",
    description="演示如何使用 fs-k8s-fastapi-helper 添加健康检查探针",
    version="1.0.0",
)

# 安装Kubernetes健康检查探针
install_k8s_health_probes(app, custom_readiness_path="/health")  # 自定义健康检查路径


# 示例路由
@app.get("/")
def index():
    """根路径 - 返回欢迎信息"""
    return {
        "message": "Welcome to FS K8s Python Helper Demo",
        "description": "This app demonstrates Kubernetes health check probes",
    }


@app.get("/health")
def ping():
    """自定义健康检查端点"""
    return {"status": "healthy", "service": "demo-app", "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
