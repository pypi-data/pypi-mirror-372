#!/usr/bin/env python3
"""
Markdown格式转换 MCP服务器入口文件
"""

import asyncio
from .server import main


def run() -> None:
    """运行MCP服务器的同步入口点"""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("MCP服务器已停止")
    except Exception as e:
        print(f"MCP服务器启动失败: {e}")
        raise


if __name__ == "__main__":
    run()

