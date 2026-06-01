"""
文件名: main.py
创建日期: 2026-06-01
功能描述: 应用程序入口模块，负责解析命令行参数并启动桌面窗口。
"""

from __future__ import annotations

import argparse
import logging
import os

from nfc_writer.app import launch_app


def build_parser() -> argparse.ArgumentParser:
    """构建命令行参数解析器。

    返回:
        配置好参数选项的 ArgumentParser 实例。
    """
    parser = argparse.ArgumentParser(description="Start the NFC Writer desktop app.")
    parser.add_argument(
        "--dev-server",
        default=os.getenv("NFC_WRITER_DEV_SERVER"),
        help="Vue dev server URL. When omitted, the built frontend is loaded.",
    )
    parser.add_argument("--debug", action="store_true", help="Enable pywebview debug mode.")
    return parser


def main() -> None:
    """应用程序主入口函数。解析参数、配置日志并启动桌面窗口。"""
    args = build_parser().parse_args()
    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    launch_app(dev_server=args.dev_server, debug=args.debug)


if __name__ == "__main__":
    main()
