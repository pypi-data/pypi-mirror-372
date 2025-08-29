"""
Word文档评论提取MCP服务主程序

提供Word文档评论提取功能的MCP服务器
"""

import os
import sys
# 设置FastMCP所需的环境变量
os.environ.setdefault('FASTMCP_LOG_LEVEL', 'INFO')

from fastmcp import FastMCP
from .tools import (
    get_all_comments,
    get_comments_by_author,
    get_comments_for_paragraph
)

# 初始化FastMCP服务器
mcp = FastMCP("Word文档评论提取")


def register_tools():
    """使用FastMCP装饰器注册所有工具"""

    @mcp.tool()
    async def get_all_comments_tool(filename: str):
        """提取Word文档中的所有评论"""
        return await get_all_comments(filename)

    @mcp.tool()
    async def get_comments_by_author_tool(filename: str, author: str):
        """提取指定作者的评论"""
        return await get_comments_by_author(filename, author)

    @mcp.tool()
    async def get_comments_for_paragraph_tool(filename: str, paragraph_index: int):
        """提取指定段落的评论"""
        return await get_comments_for_paragraph(filename, paragraph_index)


def main():
    """服务器的主入口点 - 只支持stdio传输"""
    # 注册所有工具
    register_tools()

    print("启动Word文档评论提取MCP服务器...")
    print("提供以下功能:")
    print("- get_all_comments_tool: 提取所有评论")
    print("- get_comments_by_author_tool: 按作者提取评论")
    print("- get_comments_for_paragraph_tool: 按段落提取评论")

    try:
        # 只使用stdio传输运行
        mcp.run(transport='stdio')
    except KeyboardInterrupt:
        print("\n正在关闭Word文档评论提取服务器...")
    except Exception as e:
        print(f"启动服务器时出错: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
