"""
文件名: test_bridge.py
创建日期: 2026-06-01
功能描述: NFCBridge 桥接层单元测试，验证 JSON 安全包装和异常处理。
"""

from nfc_writer.bridge import NFCBridge
from nfc_writer.nfc.service import NFCService


def test_bridge_wraps_successful_calls() -> None:
    """测试桥接层正确包装成功调用的返回结果。"""
    bridge = NFCBridge(NFCService.from_environment())

    response = bridge.list_readers()

    assert response["ok"] is True
    assert response["data"][0]["id"] == "mock-reader-1"


def test_bridge_wraps_errors() -> None:
    """测试桥接层正确捕获异常并返回错误信息。"""
    bridge = NFCBridge(NFCService.from_environment())

    response = bridge.read_tag()

    assert response["ok"] is False
    assert response["errorType"] == "RuntimeError"
