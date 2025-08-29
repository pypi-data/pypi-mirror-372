"""
Word文档内容添加MCP服务主程序

提供Word文档内容添加功能的MCP服务器
"""

import os
import sys
# 设置FastMCP所需的环境变量
os.environ.setdefault('FASTMCP_LOG_LEVEL', 'INFO')

from fastmcp import FastMCP
from .tools import (
    add_heading,
    add_paragraph,
    add_table,
    add_picture,
    add_page_break
)

# 初始化FastMCP服务器
mcp = FastMCP("Word文档内容添加")


def register_tools():
    """使用FastMCP装饰器注册所有工具"""

    @mcp.tool()
    async def add_heading_tool(filename: str, text: str, level: int = 1):
        """向Word文档添加标题"""
        return await add_heading(filename, text, level)

    @mcp.tool()
    async def add_paragraph_tool(filename: str, text: str, style: str = ""):
        """向Word文档添加段落"""
        # Convert empty string to None for the actual function
        style_param = style if style and style.strip() else None
        return await add_paragraph(filename, text, style_param)

    @mcp.tool()
    async def add_table_tool(filename: str, rows: int, cols: int, data: list = []):
        """向Word文档添加表格"""
        # Convert empty list to None for the actual function
        data_param = data if data else None
        return await add_table(filename, rows, cols, data_param)

    @mcp.tool()
    async def add_picture_tool(filename: str, image_path: str, width: float = 0.0):
        """向Word文档添加图片"""
        # Convert 0.0 to None for the actual function
        width_param = width if width > 0 else None
        return await add_picture(filename, image_path, width_param)

    @mcp.tool()
    async def add_page_break_tool(filename: str):
        """向Word文档添加分页符"""
        return await add_page_break(filename)


def main():
    """服务器的主入口点 - 只支持stdio传输"""
    # 注册所有工具
    register_tools()

    print("启动Word文档内容添加MCP服务器...")
    print("提供以下功能:")
    print("- add_heading_tool: 添加标题")
    print("- add_paragraph_tool: 添加段落")
    print("- add_table_tool: 添加表格")
    print("- add_picture_tool: 添加图片")
    print("- add_page_break_tool: 添加分页符")

    try:
        # 只使用stdio传输运行
        mcp.run(transport='stdio')
    except KeyboardInterrupt:
        print("\n正在关闭Word文档内容添加服务器...")
    except Exception as e:
        print(f"启动服务器时出错: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
