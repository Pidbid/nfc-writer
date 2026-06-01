"""
文件名: service.py
创建日期: 2026-06-01
功能描述: NFC 业务逻辑服务层，封装读写器操作并适配不同的硬件适配器。
"""

from __future__ import annotations

import os
from dataclasses import asdict
from typing import Any

from nfc_writer.nfc.adapters.base import NFCAdapter
from nfc_writer.nfc.adapters.mock import MockNFCAdapter


class NFCService:
    """NFC 核心服务类，提供读写器管理和标签读写功能。"""

    def __init__(self, adapter: NFCAdapter) -> None:
        """初始化 NFC 服务。

        参数:
            adapter: NFC 硬件适配器实例。
        """
        self._adapter = adapter
        self._connected_reader_id: str | None = None

    @classmethod
    def from_environment(cls) -> NFCService:
        """根据环境变量创建 NFC 服务实例。

        读取 NFC_WRITER_ADAPTER 环境变量选择适配器：
        - mock: 开发用模拟适配器（默认）
        - pyscard: 真实 PC/SC 硬件适配器

        返回:
            配置好的 NFCService 实例。

        异常:
            ValueError: 不支持的适配器名称时抛出。
        """
        adapter_name = os.getenv("NFC_WRITER_ADAPTER", "mock").strip().lower()
        if adapter_name == "mock":
            return cls(MockNFCAdapter())
        if adapter_name == "pyscard":
            from nfc_writer.nfc.adapters.pyscard_adapter import PyscardNFCAdapter

            return cls(PyscardNFCAdapter())
        raise ValueError(f"Unsupported NFC adapter: {adapter_name}")

    def status(self) -> dict[str, Any]:
        """获取当前服务状态。

        返回:
            包含适配器名称和已连接读写器 ID 的字典。
        """
        return {
            "adapter": os.getenv("NFC_WRITER_ADAPTER", "mock").strip().lower(),
            "connectedReaderId": self._connected_reader_id,
        }

    def list_readers(self) -> list[dict[str, Any]]:
        """列出所有可用的 NFC 读写器。

        返回:
            读写器信息字典列表。
        """
        return [asdict(reader) for reader in self._adapter.list_readers()]

    def connect(self, reader_id: str) -> dict[str, Any]:
        """连接到指定的 NFC 读写器。

        参数:
            reader_id: 目标读写器的标识符。

        返回:
            已连接读写器的信息字典。
        """
        reader = self._adapter.connect(reader_id)
        self._connected_reader_id = reader.id
        return asdict(reader)

    def disconnect(self) -> dict[str, Any]:
        """断开当前 NFC 读写器连接。

        使用 try/finally 确保即使适配器断开失败也能清除内部状态。

        返回:
            断开后的服务状态字典。
        """
        try:
            self._adapter.disconnect()
        finally:
            self._connected_reader_id = None
        return self.status()

    def read_tag(self) -> dict[str, Any]:
        """读取当前 NFC 标签数据。

        返回:
            标签信息字典，包含 uid 和 records。

        异常:
            RuntimeError: 未连接读写器时抛出。
        """
        return asdict(self._adapter.read_tag())

    def write_text(self, text: str) -> dict[str, Any]:
        """向当前 NFC 标签写入文本记录。

        参数:
            text: 要写入的文本内容。

        返回:
            写入后的标签信息字典。
        """
        return asdict(self._adapter.write_text(text))
