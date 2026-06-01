"""
文件名: pyscard_adapter.py
创建日期: 2026-06-01
功能描述: 基于 pyscard 的真实 NFC 适配器，通过 PC/SC 接口与物理读写器通信。
"""

from __future__ import annotations

from smartcard.System import readers as pcsc_readers
from smartcard.util import toHexString

from nfc_writer.nfc.types import NFCReader, NFCTag

# 获取标签 UID 的 APDU 指令
_GET_UID_APDU = [0xFF, 0xCA, 0x00, 0x00, 0x00]

# UPDATE BINARY APDU 的 Lc 字段为单字节，最大有效载荷为 255 字节
_MAX_PAYLOAD_BYTES = 255


class PyscardNFCAdapter:
    """基于 pyscard / PC/SC 的真实 NFC 硬件适配器。"""

    def __init__(self) -> None:
        """初始化适配器，连接状态为空。"""
        self._connection = None
        self._connected_reader_name: str | None = None

    def list_readers(self) -> list[NFCReader]:
        """列出系统中所有可用的 PC/SC NFC 读写器。

        返回:
            读写器信息列表，仅当前连接的读写器标记为 connected=True。
        """
        return [
            NFCReader(
                id=str(reader),
                name=str(reader),
                connected=str(reader) == self._connected_reader_name,
            )
            for reader in pcsc_readers()
        ]

    def connect(self, reader_id: str) -> NFCReader:
        """连接到指定的 PC/SC 读写器。

        若已有连接，先断开再连接新读写器，避免资源泄漏。

        参数:
            reader_id: 目标读写器的字符串标识符。

        返回:
            已连接状态的读写器信息。

        异常:
            ValueError: 指定的读写器不存在时抛出。
        """
        if self._connection is not None:
            self.disconnect()

        available = pcsc_readers()
        target = next((r for r in available if str(r) == reader_id), None)
        if target is None:
            raise ValueError(f"Reader not found: {reader_id}")

        connection = target.createConnection()
        connection.connect()
        self._connection = connection
        self._connected_reader_name = str(target)
        return NFCReader(id=str(target), name=str(target), connected=True)

    def disconnect(self) -> None:
        """断开当前 PC/SC 读写器连接。

        使用 try/finally 确保即使底层断开失败也能清除内部状态，
        避免适配器进入僵尸状态。
        """
        if self._connection is not None:
            try:
                self._connection.disconnect()
            finally:
                self._connection = None
                self._connected_reader_name = None

    def read_tag(self) -> NFCTag:
        """通过 APDU 指令读取当前标签的 UID。

        返回:
            包含 uid 和空记录列表的标签数据。

        异常:
            RuntimeError: 未连接读写器或读取失败时抛出。
        """
        self._require_connection()
        uid_bytes, sw1, sw2 = self._connection.transmit(_GET_UID_APDU)
        if (sw1, sw2) != (0x90, 0x00):
            raise RuntimeError(f"Failed to read UID: SW={sw1:02X}{sw2:02X}")
        uid = toHexString(uid_bytes)
        return NFCTag(uid=uid, records=[])

    def write_text(self, text: str) -> NFCTag:
        """通过 APDU 指令向标签写入文本数据。

        注意: 当前实现写入原始 UTF-8 字节，未封装 NDEF 记录格式。
        写入的数据对标准 NFC 读写器和手机不可见。

        参数:
            text: 要写入的文本内容。

        返回:
            写入后重新读取的标签数据。

        异常:
            ValueError: 文本为空或编码后超过 255 字节时抛出。
            RuntimeError: 未连接读写器或写入失败时抛出。
        """
        self._require_connection()
        normalized = text.strip()
        if not normalized:
            raise ValueError("Text payload cannot be empty.")
        payload = list(normalized.encode("utf-8"))
        if len(payload) > _MAX_PAYLOAD_BYTES:
            raise ValueError(
                f"编码后 payload 为 {len(payload)} 字节，"
                f"超过 APDU 单帧上限 {_MAX_PAYLOAD_BYTES} 字节。"
            )
        apdu = [0xFF, 0xD6, 0x00, 0x04, len(payload)] + payload
        sw1, sw2 = self._connection.transmit(apdu)[1:]
        if (sw1, sw2) != (0x90, 0x00):
            raise RuntimeError(f"Write failed: SW={sw1:02X}{sw2:02X}")
        return self.read_tag()

    def _require_connection(self) -> None:
        """检查是否已连接读写器，未连接时抛出异常。

        异常:
            RuntimeError: 未连接读写器时抛出。
        """
        if self._connection is None:
            raise RuntimeError("No NFC reader is connected.")
