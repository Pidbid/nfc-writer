"""
文件名: app.py
创建日期: 2026-06-01
功能描述: pywebview 窗口创建与前端资源解析模块，负责组装桌面窗口并挂载 JS 桥接 API。
"""

from __future__ import annotations

import webview

from nfc_writer.bridge import NFCBridge
from nfc_writer.nfc.service import NFCService
from nfc_writer.path_utils import resolve_frontend_entry


def launch_app(dev_server: str | None = None, debug: bool = False) -> None:
    """启动 pywebview 桌面窗口。

    参数:
        dev_server: 开发服务器 URL，为 None 时加载本地构建产物。
        debug: 是否启用 pywebview 调试模式。
    """
    service = NFCService.from_environment()
    bridge = NFCBridge(service)
    webview.create_window(
        title="NFC Writer",
        url=resolve_frontend_entry(dev_server),
        js_api=bridge,
        width=1180,
        height=760,
        min_size=(960, 640),
        text_select=True,
    )
    webview.start(debug=debug)
