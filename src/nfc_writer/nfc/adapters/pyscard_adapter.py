"""
文件名: pyscard_adapter.py
创建日期: 2026-06-01
功能描述: 基于 pyscard 的真实 NFC 适配器，通过 PC/SC 接口与物理读写器通信。
"""

from __future__ import annotations

from smartcard.System import readers as pcsc_readers
from smartcard.util import toHexString

from nfc_writer.nfc.ndef_codec import (
    decode_ndef_message,
    decode_text_record,
    decode_uri_record,
    encode_text_ndef_message,
    encode_uri_ndef_message,
)
from nfc_writer.nfc.types import NFCReader, NFCTag

# 获取标签 UID 的 APDU 指令
_GET_UID_APDU = [0xFF, 0xCA, 0x00, 0x00, 0x00]

# UPDATE BINARY APDU 的 Lc 字段为单字节，最大有效载荷为 255 字节
_MAX_PAYLOAD_BYTES = 255

# NDEF 消息在标签中的起始块（NTAG215: 块 4）
_NDEF_START_BLOCK = 4


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
        """断开当前 PC/SC 读写器连接。"""
        if self._connection is not None:
            try:
                self._connection.disconnect()
            finally:
                self._connection = None
                self._connected_reader_name = None

    def read_tag(self) -> NFCTag:
        """读取当前标签的 UID 和 NDEF 记录。

        返回:
            包含 uid 和解析后记录列表的标签数据。

        异常:
            RuntimeError: 未连接读写器或读取失败时抛出。
        """
        self._require_connection()

        # 读取 UID
        uid_bytes, sw1, sw2 = self._connection.transmit(_GET_UID_APDU)
        if (sw1, sw2) != (0x90, 0x00):
            raise RuntimeError(f"Failed to read UID: SW={sw1:02X}{sw2:02X}")
        uid = toHexString(uid_bytes)

        # 尝试读取 NDEF 数据
        records = []
        try:
            ndef_data = self._read_ndef_data()
            if ndef_data:
                decoded = decode_ndef_message(ndef_data)
                for rec in decoded:
                    try:
                        if rec["type"] == b"T":
                            records.append(decode_text_record(rec["payload"]))
                        elif rec["type"] == b"U":
                            records.append(decode_uri_record(rec["payload"]))
                        else:
                            records.append(rec["payload"].hex().upper())
                    except Exception:
                        records.append(rec["payload"].hex().upper())
        except Exception:
            pass  # 读取 NDEF 失败不影响卡号读取

        return NFCTag(uid=uid, records=records)

    def write_text(self, text: str) -> NFCTag:
        """通过 NDEF 格式向标签写入文本记录。

        将文本编码为 NDEF Text Record 后写入标签。

        参数:
            text: 要写入的文本内容。

        返回:
            写入后重新读取的标签数据。

        异常:
            ValueError: 文本为空或编码后超过标签容量时抛出。
            RuntimeError: 未连接读写器或写入失败时抛出。
        """
        self._require_connection()
        normalized = text.strip()
        if not normalized:
            raise ValueError("Text payload cannot be empty.")

        ndef_message = encode_text_ndef_message(normalized)
        self._write_ndef_data(ndef_message)
        return self.read_tag()

    def write_uri(self, uri: str) -> NFCTag:
        """通过 NDEF 格式向标签写入 URI 记录。

        参数:
            uri: 要写入的 URI。

        返回:
            写入后重新读取的标签数据。
        """
        self._require_connection()
        normalized = uri.strip()
        if not normalized:
            raise ValueError("URI cannot be empty.")

        ndef_message = encode_uri_ndef_message(normalized)
        self._write_ndef_data(ndef_message)
        return self.read_tag()

    def _read_ndef_data(self) -> bytes:
        """从标签读取 NDEF 消息数据。

        从 NDEF 起始块开始读取多个块，直到遇到 TLV terminator。

        返回:
            NDEF 消息字节。
        """
        self._require_connection()
        data = bytearray()

        for block in range(_NDEF_START_BLOCK, _NDEF_START_BLOCK + 20):
            try:
                block_data = self._read_block(block)
                data.extend(block_data)
            except RuntimeError:
                break

        # 解析 TLV (Tag-Length-Value) 格式
        # NDEF 消息被包装在 Type=0x03 的 TLV 中
        offset = 0
        while offset < len(data):
            tag_type = data[offset]
            if tag_type == 0x00:  # NULL TLV, skip
                offset += 1
                continue
            if tag_type == 0xFE:  # Terminator TLV
                break

            if offset + 1 >= len(data):
                break

            length = data[offset + 1]
            if length == 0xFF:  # 长格式
                if offset + 3 >= len(data):
                    break
                length = (data[offset + 2] << 8) | data[offset + 3]
                value_start = offset + 4
            else:
                value_start = offset + 2

            if tag_type == 0x03:  # NDEF Message TLV
                return bytes(data[value_start : value_start + length])

            offset = value_start + length

        return b""

    def _write_ndef_data(self, ndef_message: bytes) -> None:
        """将 NDEF 消息写入标签。

        将 NDEF 消息包装为 TLV 格式后写入标签的数据块。

        参数:
            ndef_message: NDEF 消息字节。

        异常:
            ValueError: NDEF 消息过长时抛出。
            RuntimeError: 写入失败时抛出。
        """
        self._require_connection()

        # 构建 TLV: [0x03] [length] [ndef_message] [0xFE]
        if len(ndef_message) <= 254:
            tlv = bytes([0x03, len(ndef_message)]) + ndef_message + bytes([0xFE])
        else:
            tlv = (
                bytes([0x03, 0xFF, len(ndef_message) >> 8, len(ndef_message) & 0xFF])
                + ndef_message
                + bytes([0xFE])
            )

        # 按 16 字节分块写入
        blocks_needed = (len(tlv) + 15) // 16
        max_blocks = 20  # 限制写入块数
        if blocks_needed > max_blocks:
            raise ValueError(
                f"NDEF 消息过长，需要 {blocks_needed} 块，最大支持 {max_blocks} 块"
            )

        # 填充到 16 字节的倍数
        padded = tlv.ljust(blocks_needed * 16, b"\x00")

        for i in range(blocks_needed):
            block_num = _NDEF_START_BLOCK + i
            block_data = list(padded[i * 16 : (i + 1) * 16])
            self._write_block(block_num, block_data)

    def _read_block(self, block: int) -> list[int]:
        """读取指定块的数据。

        参数:
            block: 块号。

        返回:
            16 字节的块数据列表。
        """
        self._require_connection()
        # READ BINARY APDU: FF B0 00 block 10
        apdu = [0xFF, 0xB0, 0x00, block, 0x10]
        data, sw1, sw2 = self._connection.transmit(apdu)
        if (sw1, sw2) != (0x90, 0x00):
            raise RuntimeError(f"Read block {block} failed: SW={sw1:02X}{sw2:02X}")
        return data

    def _write_block(self, block: int, data: list[int]) -> None:
        """写入指定块的数据。

        参数:
            block: 块号。
            data: 16 字节的数据列表。
        """
        self._require_connection()
        # UPDATE BINARY APDU: FF D6 00 block 10 data
        apdu = [0xFF, 0xD6, 0x00, block, 0x10] + data
        sw1, sw2 = self._connection.transmit(apdu)[1:]
        if (sw1, sw2) != (0x90, 0x00):
            raise RuntimeError(f"Write block {block} failed: SW={sw1:02X}{sw2:02X}")

    def _require_connection(self) -> None:
        """检查是否已连接读写器。"""
        if self._connection is None:
            raise RuntimeError("No NFC reader is connected.")
