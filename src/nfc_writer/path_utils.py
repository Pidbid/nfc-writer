"""
文件名: path_utils.py
创建日期: 2026-06-01
功能描述: 路径管理工具模块，提供开发环境和 Nuitka/PyInstaller 打包环境下的资源定位功能。
"""

from __future__ import annotations

import sys
from pathlib import Path


def resource_path(relative_path: str) -> Path:
    """获取资源的绝对路径，兼容开发环境和打包环境。

    在 Nuitka --onefile 模式下，sys._MEIPASS 指向临时解压目录；
    在开发环境下，基于项目根目录定位资源。

    参数:
        relative_path: 相对于项目根目录的资源路径。

    返回:
        资源的绝对路径。
    """
    if hasattr(sys, "_MEIPASS"):
        # Nuitka/PyInstaller 打包环境：使用临时解压目录
        base_path = Path(sys._MEIPASS)
    else:
        # 开发环境：从当前文件向上定位到项目根目录（src/nfc_writer 的上两级）
        base_path = Path(__file__).resolve().parents[2]
    return base_path / relative_path


def resolve_frontend_entry(dev_server: str | None = None) -> str:
    """解析前端入口地址。

    参数:
        dev_server: 开发服务器 URL，为 None 时使用本地构建产物。

    返回:
        前端入口页面的 URL 或本地文件路径。

    异常:
        FileNotFoundError: 本地构建产物不存在时抛出。
        ValueError: dev_server URL 格式不合法时抛出。
    """
    if dev_server:
        _validate_dev_server_url(dev_server)
        return dev_server

    index_file = resource_path("frontend/dist/index.html")
    if not index_file.exists():
        raise FileNotFoundError(
            "Built frontend not found. Run `pnpm build` in the frontend directory "
            "or start with --dev-server."
        )
    return str(index_file)


def _validate_dev_server_url(url: str) -> None:
    """校验开发服务器 URL 的合法性，拒绝 file:// 和 javascript: 等危险 scheme。

    参数:
        url: 要校验的 URL 字符串。

    异常:
        ValueError: URL scheme 不是 http 或 https 时抛出。
    """
    allowed_schemes = ("http://", "https://")
    if not url.lower().startswith(allowed_schemes):
        raise ValueError(
            f"dev_server URL 必须以 http:// 或 https:// 开头，收到: {url}"
        )
