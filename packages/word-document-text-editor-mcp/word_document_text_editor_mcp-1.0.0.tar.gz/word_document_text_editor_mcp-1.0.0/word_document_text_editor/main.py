"""
Word文档文本编辑MCP服务主程序

提供Word文档文本编辑功能的MCP服务器
"""

import os
import sys
# 设置FastMCP所需的环境变量
os.environ.setdefault('FASTMCP_LOG_LEVEL', 'INFO')

from fastmcp import FastMCP
from .tools import (
    format_text,
    search_and_replace,
    delete_paragraph,
    create_custom_style
)

# 初始化FastMCP服务器
mcp = FastMCP("Word文档文本编辑")


def register_tools():
    """使用FastMCP装饰器注册所有工具"""

    @mcp.tool()
    async def format_text_tool(filename: str, paragraph_index: int, start_pos: int, end_pos: int,
                        bold: str = "", italic: str = "", underline: str = "",
                        color: str = "", font_size: int = 0, font_name: str = ""):
        """格式化Word文档中指定段落的文本范围

        参数说明:
        - bold: "true" 表示粗体，"false" 表示非粗体，空字符串表示不改变
        - italic: "true" 表示斜体，"false" 表示非斜体，空字符串表示不改变
        - underline: "true" 表示下划线，"false" 表示无下划线，空字符串表示不改变
        - color: 颜色名称（如 "red", "blue"），空字符串表示不改变
        - font_size: 字体大小（磅），0表示不改变
        - font_name: 字体名称，空字符串表示不改变
        """
        # Convert string parameters to appropriate types for the actual function
        bold_param = None
        if bold.lower() == "true":
            bold_param = True
        elif bold.lower() == "false":
            bold_param = False

        italic_param = None
        if italic.lower() == "true":
            italic_param = True
        elif italic.lower() == "false":
            italic_param = False

        underline_param = None
        if underline.lower() == "true":
            underline_param = True
        elif underline.lower() == "false":
            underline_param = False

        color_param = color if color and color.strip() else None
        font_size_param = font_size if font_size > 0 else None
        font_name_param = font_name if font_name and font_name.strip() else None

        return await format_text(filename, paragraph_index, start_pos, end_pos,
                                     bold_param, italic_param, underline_param,
                                     color_param, font_size_param, font_name_param)

    @mcp.tool()
    async def search_and_replace_tool(filename: str, find_text: str, replace_text: str):
        """在Word文档中查找并替换文本"""
        return await search_and_replace(filename, find_text, replace_text)

    @mcp.tool()
    async def delete_paragraph_tool(filename: str, paragraph_index: int):
        """删除Word文档中的指定段落"""
        return await delete_paragraph(filename, paragraph_index)

    @mcp.tool()
    async def create_custom_style_tool(filename: str, style_name: str, bold: str = "",
                                italic: str = "", font_size: int = 0,
                                font_name: str = "", color: str = "",
                                base_style: str = ""):
        """在Word文档中创建自定义样式

        参数说明:
        - bold: "true" 表示粗体，"false" 表示非粗体，空字符串表示不设置
        - italic: "true" 表示斜体，"false" 表示非斜体，空字符串表示不设置
        - font_size: 字体大小（磅），0表示不设置
        - font_name: 字体名称，空字符串表示不设置
        - color: 颜色名称，空字符串表示不设置
        - base_style: 基础样式名称，空字符串表示不设置
        """
        # Convert string parameters to appropriate types for the actual function
        bold_param = None
        if bold.lower() == "true":
            bold_param = True
        elif bold.lower() == "false":
            bold_param = False

        italic_param = None
        if italic.lower() == "true":
            italic_param = True
        elif italic.lower() == "false":
            italic_param = False

        font_size_param = font_size if font_size > 0 else None
        font_name_param = font_name if font_name and font_name.strip() else None
        color_param = color if color and color.strip() else None
        base_style_param = base_style if base_style and base_style.strip() else None

        return await create_custom_style(filename, style_name, bold_param, italic_param,
                                             font_size_param, font_name_param, color_param, base_style_param)


def main():
    """服务器的主入口点 - 只支持stdio传输"""
    # 注册所有工具
    register_tools()

    print("启动Word文档文本编辑MCP服务器...")
    print("提供以下功能:")
    print("- format_text_tool: 格式化文本范围")
    print("- search_and_replace_tool: 查找替换文本")
    print("- delete_paragraph_tool: 删除段落")
    print("- create_custom_style_tool: 创建自定义样式")

    try:
        # 只使用stdio传输运行
        mcp.run(transport='stdio')
    except KeyboardInterrupt:
        print("\n正在关闭Word文档文本编辑服务器...")
    except Exception as e:
        print(f"启动服务器时出错: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
