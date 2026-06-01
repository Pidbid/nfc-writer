"""
文件名: conftest.py
创建日期: 2026-06-01
功能描述: pytest 共享夹具定义，为测试提供通用的模拟适配器和服务实例。
"""

from __future__ import annotations

import pytest

from nfc_writer.nfc.adapters.mock import MockNFCAdapter
from nfc_writer.nfc.service import NFCService


@pytest.fixture()
def mock_adapter() -> MockNFCAdapter:
    """创建模拟 NFC 适配器实例。"""
    return MockNFCAdapter()


@pytest.fixture()
def service(mock_adapter: MockNFCAdapter) -> NFCService:
    """创建使用模拟适配器的 NFC 服务实例。"""
    return NFCService(mock_adapter)
