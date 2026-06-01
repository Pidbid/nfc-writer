"""
文件名: __init__.py
创建日期: 2026-06-01
功能描述: NFC 适配器子包初始化模块，导出适配器类型并支持 pyscard 延迟加载。
"""

from nfc_writer.nfc.adapters.base import NFCAdapter
from nfc_writer.nfc.adapters.mock import MockNFCAdapter

__all__ = ["MockNFCAdapter", "NFCAdapter"]


def __getattr__(name: str):
    """模块级延迟导入，仅在访问 PyscardNFCAdapter 时才加载 pyscard 依赖。"""
    if name == "PyscardNFCAdapter":
        from nfc_writer.nfc.adapters.pyscard_adapter import PyscardNFCAdapter

        return PyscardNFCAdapter
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
