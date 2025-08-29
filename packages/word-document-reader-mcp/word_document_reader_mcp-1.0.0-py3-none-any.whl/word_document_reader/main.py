"""
Word文档内容读取MCP服务主程序

提供Word文档内容读取功能的MCP服务器
"""

import os
import sys
# 设置FastMCP所需的环境变量
os.environ.setdefault('FASTMCP_LOG_LEVEL', 'INFO')

from fastmcp import FastMCP
from .tools import (
    get_document_info,
    get_document_text,
    get_document_outline,
    get_paragraph_text_from_document,
    find_text_in_document
)

# 初始化FastMCP服务器
mcp = FastMCP("Word文档内容读取")


def register_tools():
    """使用FastMCP装饰器注册所有工具"""

    @mcp.tool()
    async def get_document_info_tool(filename: str):
        """获取Word文档的信息"""
        return await get_document_info(filename)

    @mcp.tool()
    async def get_document_text_tool(filename: str):
        """提取Word文档的所有文本内容"""
        return await get_document_text(filename)

    @mcp.tool()
    async def get_document_outline_tool(filename: str):
        """获取Word文档的大纲结构"""
        return await get_document_outline(filename)

    @mcp.tool()
    async def get_paragraph_text_from_document_tool(filename: str, paragraph_index: int):
        """从Word文档中获取指定段落的文本"""
        return await get_paragraph_text_from_document(filename, paragraph_index)

    @mcp.tool()
    async def find_text_in_document_tool(filename: str, text_to_find: str, match_case: bool = True, whole_word: bool = False):
        """在Word文档中查找指定文本"""
        return await find_text_in_document(filename, text_to_find, match_case, whole_word)


def main():
    """服务器的主入口点 - 只支持stdio传输"""
    # 注册所有工具
    register_tools()

    print("启动Word文档内容读取MCP服务器...")
    print("提供以下功能:")
    print("- get_document_info_tool: 获取文档信息")
    print("- get_document_text_tool: 提取文档文本")
    print("- get_document_outline_tool: 获取文档大纲")
    print("- get_paragraph_text_from_document_tool: 获取段落文本")
    print("- find_text_in_document_tool: 查找文档文本")

    try:
        # 只使用stdio传输运行
        mcp.run(transport='stdio')
    except KeyboardInterrupt:
        print("\n正在关闭Word文档内容读取服务器...")
    except Exception as e:
        print(f"启动服务器时出错: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
