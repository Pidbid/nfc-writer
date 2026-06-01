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
        self._service = service

    def ping(self) -> dict[str, Any]:
        return {"ok": True, "data": {"service": "nfc-writer"}}

    def status(self) -> dict[str, Any]:
        return self._safe(self._service.status)

    def list_adapters(self) -> dict[str, Any]:
        return self._safe(self._service.list_adapters)

    def set_adapter(self, adapter_name: str) -> dict[str, Any]:
        return self._safe(lambda: self._service.set_adapter(adapter_name))

    def list_readers(self) -> dict[str, Any]:
        return self._safe(self._service.list_readers)

    def connect(self, reader_id: str) -> dict[str, Any]:
        return self._safe(lambda: self._service.connect(reader_id))

    def disconnect(self) -> dict[str, Any]:
        return self._safe(self._service.disconnect)

    def read_tag(self) -> dict[str, Any]:
        return self._safe(self._service.read_tag)

    def write_text(self, text: str) -> dict[str, Any]:
        return self._safe(lambda: self._service.write_text(text))

    def write_uri(self, uri: str) -> dict[str, Any]:
        return self._safe(lambda: self._service.write_uri(uri))

    @staticmethod
    def _safe(action: Callable[[], Any]) -> dict[str, Any]:
        try:
            return {"ok": True, "data": action()}
        except Exception as exc:
            return {"ok": False, "error": str(exc), "errorType": exc.__class__.__name__}
