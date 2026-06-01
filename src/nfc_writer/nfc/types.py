"""
文件名: types.py
创建日期: 2026-06-01
功能描述: NFC 领域数据类型定义，包括读写器和标签的数据结构。
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class NFCReader:
    """NFC 读写器数据结构。

    属性:
        id: 读写器唯一标识符。
        name: 读写器显示名称。
        connected: 是否已连接。
    """

    id: str
    name: str
    connected: bool


@dataclass(frozen=True)
class NFCTag:
    """NFC 标签数据结构。

    属性:
        uid: 标签唯一标识符。
        records: 标签中存储的记录列表。
    """

    uid: str
    records: list[str]
