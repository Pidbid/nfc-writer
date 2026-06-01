"""
文件名: test_service.py
创建日期: 2026-06-01
功能描述: NFCService 业务服务层单元测试，覆盖适配器选择和读写器操作流程。
"""

from __future__ import annotations

import pytest

from nfc_writer.nfc.service import NFCService


class TestNFCService:
    """NFC 服务层测试类。"""

    def test_from_environment_defaults_to_mock(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """测试未设置环境变量时默认使用 mock 适配器。"""
        monkeypatch.delenv("NFC_WRITER_ADAPTER", raising=False)

        service = NFCService.from_environment()

        assert service.status()["adapter"] == "mock"

    def test_from_environment_mock(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """测试显式设置 mock 适配器环境变量。"""
        monkeypatch.setenv("NFC_WRITER_ADAPTER", "mock")

        service = NFCService.from_environment()

        assert service.status()["adapter"] == "mock"

    def test_from_environment_unknown_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """测试设置未知适配器名称时抛出异常。"""
        monkeypatch.setenv("NFC_WRITER_ADAPTER", "unknown")

        with pytest.raises(ValueError, match="Unsupported NFC adapter"):
            NFCService.from_environment()

    def test_list_readers(self, service: NFCService) -> None:
        """测试列出读写器返回正确的数据结构。"""
        readers = service.list_readers()

        assert len(readers) == 1
        assert readers[0]["id"] == "mock-reader-1"

    def test_connect_and_status(self, service: NFCService) -> None:
        """测试连接读写器后状态正确更新。"""
        result = service.connect("mock-reader-1")

        assert result["connected"] is True
        assert service.status()["connectedReaderId"] == "mock-reader-1"

    def test_disconnect_clears_state(self, service: NFCService) -> None:
        """测试断开连接后状态正确清除。"""
        service.connect("mock-reader-1")

        status = service.disconnect()

        assert status["connectedReaderId"] is None

    def test_read_tag_requires_connection(self, service: NFCService) -> None:
        """测试未连接时读取标签抛出异常。"""
        with pytest.raises(RuntimeError):
            service.read_tag()

    def test_read_tag_after_connect(self, service: NFCService) -> None:
        """测试连接后读取标签返回包含 uid 和 records 的字典。"""
        service.connect("mock-reader-1")

        tag = service.read_tag()

        assert "uid" in tag
        assert "records" in tag

    def test_write_text(self, service: NFCService) -> None:
        """测试写入文本后返回更新后的标签数据。"""
        service.connect("mock-reader-1")

        tag = service.write_text("Test payload")

        assert tag["records"] == ["Test payload"]
