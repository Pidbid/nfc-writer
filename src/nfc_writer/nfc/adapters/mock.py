"""
文件名: mock.py
创建日期: 2026-06-01
功能描述: NFC 模拟适配器，用于开发和测试环境，无需真实硬件即可运行。
"""

from __future__ import annotations

from dataclasses import replace

from nfc_writer.nfc.types import NFCReader, NFCTag


class MockNFCAdapter:
    """模拟 NFC 适配器，提供内存中的假读写器和标签数据。"""

    def __init__(self) -> None:
        """初始化模拟适配器，创建一个假读写器和默认标签。"""
        self._readers = [
            NFCReader(id="mock-reader-1", name="Mock NFC Reader", connected=False),
        ]
        self._connected_reader: NFCReader | None = None
        self._tag = NFCTag(uid="04:A2:19:8F:2B:61:80", records=["NFC Writer ready"])

    def list_readers(self) -> list[NFCReader]:
        """列出所有模拟读写器，根据连接状态更新 connected 标志。"""
        return [
            replace(
                reader,
                connected=self._connected_reader is not None
                and reader.id == self._connected_reader.id,
            )
            for reader in self._readers
        ]

    def connect(self, reader_id: str) -> NFCReader:
        """连接到指定的模拟读写器。

        参数:
            reader_id: 目标读写器的标识符。

        返回:
            已连接状态的读写器信息。

        异常:
            ValueError: 读写器不存在时抛出。
        """
        reader = next((item for item in self._readers if item.id == reader_id), None)
        if reader is None:
            raise ValueError(f"Reader not found: {reader_id}")
        self._connected_reader = replace(reader, connected=True)
        return self._connected_reader

    def disconnect(self) -> None:
        """断开当前模拟读写器连接。"""
        self._connected_reader = None

    def read_tag(self) -> NFCTag:
        """读取当前模拟标签数据。

        返回:
            模拟标签的 uid 和记录。

        异常:
            RuntimeError: 未连接读写器时抛出。
        """
        self._require_connection()
        return self._tag

    def write_text(self, text: str) -> NFCTag:
        """向模拟标签写入文本记录。

        参数:
            text: 要写入的文本内容。

        返回:
            写入后的标签数据。

        异常:
            ValueError: 文本为空时抛出。
            RuntimeError: 未连接读写器时抛出。
        """
        self._require_connection()
        normalized = text.strip()
        if not normalized:
            raise ValueError("Text payload cannot be empty.")
        self._tag = replace(self._tag, records=[normalized])
        return self._tag

    def _require_connection(self) -> None:
        """检查是否已连接读写器，未连接时抛出异常。

        异常:
            RuntimeError: 未连接读写器时抛出。
        """
        if self._connected_reader is None:
            raise RuntimeError("No NFC reader is connected.")
