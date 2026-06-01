"""
文件名: service.py
创建日期: 2026-06-01
功能描述: NFC 业务逻辑服务层，封装读写器操作并适配不同的硬件适配器。
"""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from nfc_writer.nfc.adapters.base import NFCAdapter

def _get_pyscard_adapter():
    from nfc_writer.nfc.adapters.pyscard_adapter import PyscardNFCAdapter

    return PyscardNFCAdapter()


def _get_xinheng_adapter():
    from nfc_writer.nfc.adapters.xinheng_adapter import XinhengNFCAdapter

    return XinhengNFCAdapter()


# 延迟加载的适配器工厂
_ADAPTER_FACTORIES: dict[str, type | callable] = {
    "pyscard": _get_pyscard_adapter,
    "xinheng": _get_xinheng_adapter,
}

# 适配器显示名称
_ADAPTER_NAMES: dict[str, str] = {
    "pyscard": "标准 PC/SC",
    "xinheng": "莘航 RFID",
}


class NFCService:
    """NFC 核心服务类，提供读写器管理和标签读写功能。"""

    def __init__(self, adapter: NFCAdapter, adapter_name: str = "mock") -> None:
        self._adapter = adapter
        self._adapter_name = adapter_name
        self._connected_reader_id: str | None = None

    @classmethod
    def from_environment(cls) -> NFCService:
        """根据环境变量创建 NFC 服务实例。"""
        import os

        adapter_name = os.getenv("NFC_WRITER_ADAPTER", "pyscard").strip().lower()
        return cls._create_with_adapter(adapter_name)

    @classmethod
    def _create_with_adapter(cls, adapter_name: str) -> NFCService:
        """使用指定适配器创建服务实例。"""
        factory = _ADAPTER_FACTORIES.get(adapter_name)
        if factory is None:
            available = ", ".join(_ADAPTER_FACTORIES.keys())
            raise ValueError(f"不支持的适配器: {adapter_name}，可用: {available}")

        if callable(factory) and not isinstance(factory, type):
            adapter = factory()
        else:
            adapter = factory()

        return cls(adapter, adapter_name)

    def list_adapters(self) -> list[dict[str, Any]]:
        """列出所有可用的适配器。"""
        return [
            {
                "id": adapter_id,
                "name": _ADAPTER_NAMES.get(adapter_id, adapter_id),
                "active": adapter_id == self._adapter_name,
            }
            for adapter_id in _ADAPTER_FACTORIES
        ]

    def set_adapter(self, adapter_name: str) -> dict[str, Any]:
        """切换适配器。

        参数:
            adapter_name: 目标适配器名称。

        返回:
            切换后的服务状态。
        """
        if adapter_name == self._adapter_name:
            return self.status()

        # 断开当前连接
        if self._connected_reader_id is not None:
            try:
                self._adapter.disconnect()
            except Exception:
                pass
            self._connected_reader_id = None

        # 创建新适配器
        factory = _ADAPTER_FACTORIES.get(adapter_name)
        if factory is None:
            available = ", ".join(_ADAPTER_FACTORIES.keys())
            raise ValueError(f"不支持的适配器: {adapter_name}，可用: {available}")

        if callable(factory) and not isinstance(factory, type):
            self._adapter = factory()
        else:
            self._adapter = factory()

        self._adapter_name = adapter_name
        return self.status()

    def status(self) -> dict[str, Any]:
        """获取当前服务状态。"""
        return {
            "adapter": self._adapter_name,
            "adapterName": _ADAPTER_NAMES.get(self._adapter_name, self._adapter_name),
            "connectedReaderId": self._connected_reader_id,
        }

    def list_readers(self) -> list[dict[str, Any]]:
        """列出所有可用的 NFC 读写器。"""
        return [asdict(reader) for reader in self._adapter.list_readers()]

    def connect(self, reader_id: str) -> dict[str, Any]:
        """连接到指定的 NFC 读写器。"""
        reader = self._adapter.connect(reader_id)
        self._connected_reader_id = reader.id
        return asdict(reader)

    def disconnect(self) -> dict[str, Any]:
        """断开当前 NFC 读写器连接。"""
        try:
            self._adapter.disconnect()
        finally:
            self._connected_reader_id = None
        return self.status()

    def read_tag(self) -> dict[str, Any]:
        """读取当前 NFC 标签数据。"""
        return asdict(self._adapter.read_tag())

    def write_text(self, text: str) -> dict[str, Any]:
        """向当前 NFC 标签写入文本记录。"""
        return asdict(self._adapter.write_text(text))

    def write_uri(self, uri: str) -> dict[str, Any]:
        """向当前 NFC 标签写入 URI 记录。"""
        return asdict(self._adapter.write_uri(uri))
