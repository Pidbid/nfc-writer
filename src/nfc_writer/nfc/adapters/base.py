"""
文件名: base.py
创建日期: 2026-06-01
功能描述: NFC 适配器协议定义，规定所有硬件适配器必须实现的接口。
"""

from __future__ import annotations

from typing import Protocol

from nfc_writer.nfc.types import NFCReader, NFCTag


class NFCAdapter(Protocol):
    """NFC 硬件适配器协议，定义读写器和标签操作的边界接口。"""

    def list_readers(self) -> list[NFCReader]:
        """列出所有可用的 NFC 读写器。"""

    def connect(self, reader_id: str) -> NFCReader:
        """连接到指定读写器并返回该读写器信息。

        参数:
            reader_id: 目标读写器的标识符。
        """

    def disconnect(self) -> None:
        """关闭当前活动的读写器连接。"""

    def read_tag(self) -> NFCTag:
        """读取当前放置的 NFC 标签。"""

    def write_text(self, text: str) -> NFCTag:
        """向当前 NFC 标签写入文本并返回更新后的标签状态。

        参数:
            text: 要写入的文本内容。
        """
