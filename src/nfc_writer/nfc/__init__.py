"""
文件名: __init__.py
创建日期: 2026-06-01
功能描述: nfc 子包初始化模块，导出 NFCService 供外部使用。
"""

from nfc_writer.nfc.service import NFCService

__all__ = ["NFCService"]
