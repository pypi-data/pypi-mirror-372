"""
FS K8s Python Helper

A Kubernetes health check probe helper for FastAPI applications.
"""

__version__ = "0.1.0"
__author__ = "wuzh"
__email__ = "wuzh@fxiaoke.com"

from .service import install_k8s_health_probes

__all__ = ["install_k8s_health_probes"]
