"""
文件名: xinheng_adapter.py
创建日期: 2026-06-01
功能描述: 基于莘航 XH_RFID_DLL.dll 的 NFC 适配器，通过串口与莘航 RFID 高频读写器通信。
"""

from __future__ import annotations

import sys
from pathlib import Path

from nfc_writer.nfc.types import NFCReader, NFCTag

# DLL 所在目录
_DLL_DIR = Path(__file__).parent / "dll"
_DLL_PATH = _DLL_DIR / "XH_RFID_DLL.dll"

# 默认读写器地址
_DEFAULT_ADDR = 0x00

# 默认波特率
_DEFAULT_BAUDRATE = 9600


def _load_dll():
    """加载莘航 RFID DLL，返回 (XH_Rfid, Cmd, Beep) 类型。"""
    import clr  # type: ignore[import-untyped]

    dll_dir_str = str(_DLL_DIR)
    if dll_dir_str not in sys.path:
        sys.path.insert(0, dll_dir_str)

    clr.AddReference(str(_DLL_PATH.with_suffix("")))
    from XH_RFID_DLL import XH_Rfid, Cmd, Beep  # type: ignore[import-untyped]

    return XH_Rfid, Cmd, Beep


class XinhengNFCAdapter:
    """基于莘航 XH_RFID_DLL.dll 的真实 NFC 硬件适配器。"""

    def __init__(self) -> None:
        self._reader = None
        self._reader_class = None
        self._cmd = None
        self._beep = None
        self._connected_port: str | None = None

    def _ensure_dll(self):
        """确保 DLL 已加载。"""
        if self._reader_class is None:
            self._reader_class, self._cmd, self._beep = _load_dll()
            self._reader = self._reader_class()

    def _get_reader(self):
        self._ensure_dll()
        return self._reader

    def list_readers(self) -> list[NFCReader]:
        """列出可用的串口读写器。"""
        import serial.tools.list_ports  # type: ignore[import-untyped]

        ports = serial.tools.list_ports.comports()
        return [
            NFCReader(
                id=port.device,
                name=f"{port.description} ({port.device})",
                connected=port.device == self._connected_port,
            )
            for port in ports
        ]

    def connect(self, reader_id: str) -> NFCReader:
        """连接到指定串口的读写器。"""
        if self._connected_port is not None:
            self.disconnect()

        reader = self._get_reader()
        result = reader.Connect(reader_id, _DEFAULT_BAUDRATE)
        if not result:
            raise ValueError(f"无法打开串口 {reader_id}，请检查设备连接。")

        self._connected_port = reader_id
        return NFCReader(
            id=reader_id,
            name=f"莘航 RFID 读写器 ({reader_id})",
            connected=True,
        )

    def disconnect(self) -> None:
        """断开当前串口连接。"""
        if self._reader is not None and self._connected_port is not None:
            try:
                self._reader.DisConnect()
            except Exception:
                pass
        self._connected_port = None

    def read_tag(self) -> NFCTag:
        """读取当前标签的卡号。"""
        self._require_connection()
        reader = self._get_reader()

        reader.Cmd = self._cmd.M1_ReadId
        reader.Addr = _DEFAULT_ADDR
        reader.Beep = self._beep.On

        status = reader.M1_Operation()
        if status != 1:
            raise RuntimeError(f"读卡号失败，错误码: {status}")

        uid = ":".join(f"{reader.RxBuffer[i + 2]:02X}" for i in range(4))
        return NFCTag(uid=uid, records=[])

    def read_block(self, block: int) -> bytes:
        """读取指定数据块的 16 字节数据。"""
        self._require_connection()
        reader = self._get_reader()

        reader.Cmd = self._cmd.M1_ReadBlock
        reader.Addr = _DEFAULT_ADDR
        reader.M1Block = block
        reader.Beep = self._beep.Off

        status = reader.M1_Operation()
        if status != 1:
            raise RuntimeError(f"读块数据失败，块号: {block}，错误码: {status}")

        return bytes(reader.RxBuffer[:16])

    def write_block(self, block: int, data: bytes) -> None:
        """向指定数据块写入 16 字节数据。"""
        self._require_connection()
        if len(data) != 16:
            raise ValueError(f"数据长度必须为 16 字节，当前: {len(data)} 字节")

        reader = self._get_reader()

        reader.Cmd = self._cmd.M1_WriteBlock
        reader.Addr = _DEFAULT_ADDR
        reader.M1Block = block
        reader.Beep = self._beep.Off

        for i in range(16):
            reader.TxBuffer[i] = data[i]

        status = reader.M1_Operation()
        if status != 1:
            raise RuntimeError(f"写块数据失败，块号: {block}，错误码: {status}")

    def write_text(self, text: str) -> NFCTag:
        """向标签写入文本数据。"""
        self._require_connection()
        normalized = text.strip()
        if not normalized:
            raise ValueError("文本内容不能为空")

        payload = normalized.encode("utf-8")
        max_len = 16 * 4
        if len(payload) > max_len:
            raise ValueError(f"文本过长，最大 {max_len} 字节，当前: {len(payload)} 字节")

        padded = payload.ljust(((len(payload) + 15) // 16) * 16, b"\x00")

        tag = self.read_tag()

        for i in range(0, len(padded), 16):
            block_num = 4 + (i // 16)
            self.write_block(block_num, padded[i : i + 16])

        return NFCTag(uid=tag.uid, records=[normalized])

    def write_uri(self, uri: str) -> NFCTag:
        """向标签写入 URI 数据。"""
        return self.write_text(uri)

    def _require_connection(self) -> None:
        if self._connected_port is None:
            raise RuntimeError("未连接读写器，请先连接串口。")
