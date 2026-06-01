"""
文件名: test_mock_adapter.py
创建日期: 2026-06-01
功能描述: MockNFCAdapter 模拟适配器单元测试，覆盖读写器管理和标签读写操作。
"""

from __future__ import annotations

import pytest

from nfc_writer.nfc.adapters.mock import MockNFCAdapter


class TestMockNFCAdapter:
    """模拟 NFC 适配器测试类。"""

    def test_list_readers_returns_mock(self) -> None:
        """测试列出读写器返回模拟读写器。"""
        adapter = MockNFCAdapter()

        readers = adapter.list_readers()

        assert len(readers) == 1
        assert readers[0].id == "mock-reader-1"
        assert readers[0].connected is False

    def test_connect_marks_reader_connected(self) -> None:
        """测试连接后读写器状态变为已连接。"""
        adapter = MockNFCAdapter()

        reader = adapter.connect("mock-reader-1")

        assert reader.connected is True
        assert adapter.list_readers()[0].connected is True

    def test_connect_unknown_reader_raises(self) -> None:
        """测试连接不存在的读写器时抛出异常。"""
        adapter = MockNFCAdapter()

        with pytest.raises(ValueError, match="Reader not found"):
            adapter.connect("nonexistent")

    def test_disconnect_clears_connection(self) -> None:
        """测试断开连接后读写器状态恢复为未连接。"""
        adapter = MockNFCAdapter()
        adapter.connect("mock-reader-1")

        adapter.disconnect()

        assert adapter.list_readers()[0].connected is False

    def test_read_tag_requires_connection(self) -> None:
        """测试未连接时读取标签抛出异常。"""
        adapter = MockNFCAdapter()

        with pytest.raises(RuntimeError, match="No NFC reader is connected"):
            adapter.read_tag()

    def test_read_tag_returns_uid_and_records(self) -> None:
        """测试已连接时读取标签返回正确的 uid 和记录。"""
        adapter = MockNFCAdapter()
        adapter.connect("mock-reader-1")

        tag = adapter.read_tag()

        assert tag.uid == "04:A2:19:8F:2B:61:80"
        assert len(tag.records) == 1

    def test_write_text_updates_records(self) -> None:
        """测试写入文本后标签记录被正确更新。"""
        adapter = MockNFCAdapter()
        adapter.connect("mock-reader-1")

        tag = adapter.write_text("Hello NFC")

        assert tag.records == ["Hello NFC"]

    def test_write_empty_text_raises(self) -> None:
        """测试写入空文本时抛出异常。"""
        adapter = MockNFCAdapter()
        adapter.connect("mock-reader-1")

        with pytest.raises(ValueError, match="cannot be empty"):
            adapter.write_text("   ")

    def test_write_text_requires_connection(self) -> None:
        """测试未连接时写入文本抛出异常。"""
        adapter = MockNFCAdapter()

        with pytest.raises(RuntimeError, match="No NFC reader is connected"):
            adapter.write_text("test")
