from __future__ import annotations

from typing import Callable, Optional

__doc__: str
__version__: str

def activate(product: str, code: str, cluster_type: int = 0) -> bool:
    """
    激活GAXMath产品
    """
    ...

def set_license_server(url: str) -> bool:
    """
    设置许可证服务器地址
    """
    ...

def start_license_server() -> bool:
    """
    启动许可证服务器
    """
    ...

def client_main() -> int:
    """
    GAXKey客户端入口函数
    """
    ...

def server_main() -> int:
    """
    GAXKey服务器入口函数
    """
    ... 