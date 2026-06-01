"""
文件名: bridge.py
创建日期: 2026-06-01
功能描述: pywebview JS 桥接层，将 NFC 服务方法包装为 JSON 安全的 API 供前端调用。
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from nfc_writer.nfc.service import NFCService


class NFCBridge:
    """暴露给 pywebview 前端的 JSON 安全 API 接口。"""

    def __init__(self, service: NFCService) -> None:
        """初始化桥接层。

        参数:
            service: NFC 服务实例。
        """
        self._service = service

    def ping(self) -> dict[str, Any]:
        """健康检查接口。"""
        return {"ok": True, "data": {"service": "nfc-writer"}}

    def status(self) -> dict[str, Any]:
        """获取当前 NFC 服务状态。"""
        return self._safe(self._service.status)

    def list_readers(self) -> dict[str, Any]:
        """列出所有可用的 NFC 读写器。"""
        return self._safe(self._service.list_readers)

    def connect(self, reader_id: str) -> dict[str, Any]:
        """连接到指定的 NFC 读写器。

        参数:
            reader_id: 目标读写器的标识符。
        """
        return self._safe(lambda: self._service.connect(reader_id))

    def disconnect(self) -> dict[str, Any]:
        """断开当前 NFC 读写器连接。"""
        return self._safe(self._service.disconnect)

    def read_tag(self) -> dict[str, Any]:
        """读取当前 NFC 标签数据。"""
        return self._safe(self._service.read_tag)

    def write_text(self, text: str) -> dict[str, Any]:
        """向当前 NFC 标签写入文本记录。

        参数:
            text: 要写入的文本内容。
        """
        return self._safe(lambda: self._service.write_text(text))

    @staticmethod
    def _safe(action: Callable[[], Any]) -> dict[str, Any]:
        """安全执行操作，捕获异常并统一返回格式。

        参数:
            action: 要执行的回调函数。

        返回:
            包含 ok 状态和 data 或 error 的字典。
        """
        try:
            return {"ok": True, "data": action()}
        except Exception as exc:
            return {"ok": False, "error": str(exc), "errorType": exc.__class__.__name__}
