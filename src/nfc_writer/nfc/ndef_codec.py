"""
文件名: ndef_codec.py
创建日期: 2026-06-01
功能描述: NDEF (NFC Data Exchange Format) 记录编解码器，支持文本和 URI 记录的序列化与反序列化。
"""

from __future__ import annotations

import struct


def encode_text_record(text: str, language: str = "en") -> bytes:
    """将文本编码为 NDEF 文本记录的 payload（不含 record header）。

    NDEF Text Record payload 格式:
    [status_byte] [language_code] [text]

    status_byte:
      - bit 7: 0 = UTF-8, 1 = UTF-16
      - bit 5-0: language code length

    参数:
        text: 要编码的文本。
        language: 语言代码（如 "en", "zh"），最长 63 字节。

    返回:
        NDEF Text Record 的 payload 字节。
    """
    lang_bytes = language.encode("ascii")[:63]
    text_bytes = text.encode("utf-8")
    status_byte = len(lang_bytes)  # UTF-8, bit7=0
    return bytes([status_byte]) + lang_bytes + text_bytes


def encode_ndef_message(records: list[tuple[str, bytes]]) -> bytes:
    """将多条 NDEF 记录编码为完整的 NDEF 消息。

    参数:
        records: (类型, payload) 元组列表。
            类型: "T" (文本), "U" (URI) 等。

    返回:
        完整的 NDEF 消息字节。
    """
    if not records:
        raise ValueError("至少需要一条 NDEF 记录")

    message = bytearray()
    for i, (record_type, payload) in enumerate(records):
        is_first = i == 0
        is_last = i == len(records) - 1

        # 构建 record header
        header = 0x00
        if is_first:
            header |= 0x80  # MB: Message Begin
        if is_last:
            header |= 0x40  # ME: Message End

        # TNF (Type Name Format): 0x01 = NFC Forum well-known type
        header |= 0x01

        type_bytes = record_type.encode("ascii")

        # 构建 record
        record = bytearray()
        record.append(header)
        record.append(len(type_bytes))
        record.append(len(payload))
        record.extend(type_bytes)
        record.extend(payload)

        message.extend(record)

    return bytes(message)


def encode_text_ndef_message(text: str, language: str = "en") -> bytes:
    """将文本编码为完整的 NDEF 消息。

    参数:
        text: 要编码的文本。
        language: 语言代码。

    返回:
        完整的 NDEF 消息字节。
    """
    payload = encode_text_record(text, language)
    return encode_ndef_message([("T", payload)])


def encode_uri_ndef_message(uri: str) -> bytes:
    """将 URI 编码为完整的 NDEF 消息。

    参数:
        uri: 要编码的 URI。

    返回:
        完整的 NDEF 消息字节。
    """
    # URI prefix code: 0x00 = no abbreviation
    prefix_code = 0x00
    uri_bytes = uri.encode("ascii")
    payload = bytes([prefix_code]) + uri_bytes
    return encode_ndef_message([("U", payload)])


def decode_ndef_message(data: bytes) -> list[dict]:
    """解码 NDEF 消息，返回记录列表。

    参数:
        data: NDEF 消息字节。

    返回:
        记录字典列表，每个包含 type, tnf, payload 字段。
    """
    records = []
    offset = 0

    while offset < len(data):
        if offset >= len(data):
            break

        header = data[offset]
        offset += 1

        mb = bool(header & 0x80)  # Message Begin
        me = bool(header & 0x40)  # Message End
        cf = bool(header & 0x20)  # Chunk Flag
        sr = bool(header & 0x10)  # Short Record
        il = bool(header & 0x08)  # ID Length present
        tnf = header & 0x07       # Type Name Format

        # Type length
        type_length = data[offset] if offset < len(data) else 0
        offset += 1

        # Payload length
        if sr:
            payload_length = data[offset] if offset < len(data) else 0
            offset += 1
        else:
            if offset + 4 <= len(data):
                payload_length = struct.unpack(">I", data[offset : offset + 4])[0]
                offset += 4
            else:
                break

        # ID length (if present)
        id_length = 0
        if il:
            id_length = data[offset] if offset < len(data) else 0
            offset += 1

        # Type
        record_type = data[offset : offset + type_length]
        offset += type_length

        # ID (if present)
        record_id = data[offset : offset + id_length]
        offset += id_length

        # Payload
        payload = data[offset : offset + payload_length]
        offset += payload_length

        records.append(
            {
                "type": record_type,
                "tnf": tnf,
                "payload": payload,
                "id": record_id,
            }
        )

        if me:
            break

    return records


def decode_text_record(payload: bytes) -> str:
    """解码 NDEF Text Record 的 payload 为文本。

    参数:
        payload: Text Record 的 payload 字节。

    返回:
        解码后的文本。
    """
    if len(payload) < 2:
        raise ValueError("Text record payload too short")

    status_byte = payload[0]
    is_utf16 = bool(status_byte & 0x80)
    lang_length = status_byte & 0x3F

    if len(payload) < 1 + lang_length:
        raise ValueError("Text record payload too short for language code")

    text_bytes = payload[1 + lang_length :]
    if is_utf16:
        return text_bytes.decode("utf-16")
    return text_bytes.decode("utf-8")


def decode_uri_record(payload: bytes) -> str:
    """解码 NDEF URI Record 的 payload 为 URI 字符串。

    参数:
        payload: URI Record 的 payload 字节。

    返回:
        解码后的 URI。
    """
    if len(payload) < 2:
        raise ValueError("URI record payload too short")

    prefix_code = payload[0]
    uri_bytes = payload[1:]

    # 常见 URI 前缀
    prefixes = {
        0x00: "",
        0x01: "http://www.",
        0x02: "https://www.",
        0x03: "http://",
        0x04: "https://",
        0x05: "tel:",
        0x06: "mailto:",
        0x07: "ftp://anonymous:anonymous@",
        0x08: "ftp://ftp.",
        0x09: "ftps://",
        0x0A: "sftp://",
        0x0B: "smb://",
        0x0C: "nfs://",
        0x0D: "ftp://",
        0x0E: "dav://",
        0x0F: "news:",
        0x10: "telnet://",
        0x11: "imap:",
        0x12: "rtsp://",
        0x13: "urn:",
        0x14: "pop:",
        0x15: "sip:",
        0x16: "sips:",
        0x17: "tftp:",
        0x18: "btspp://",
        0x19: "btl2cap://",
        0x1A: "btgoep://",
        0x1B: "tcpobex://",
        0x1C: "irdaobex://",
        0x1D: "file://",
        0x1E: "urn:epc:id:",
        0x1F: "urn:epc:tag:",
        0x20: "urn:epc:pat:",
        0x21: "urn:epc:raw:",
        0x22: "urn:epc:",
        0x23: "urn:nfc:",
    }

    prefix = prefixes.get(prefix_code, "")
    return prefix + uri_bytes.decode("utf-8")
