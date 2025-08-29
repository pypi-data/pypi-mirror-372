"""
Word文档表格编辑MCP服务主程序

提供Word文档表格编辑功能的MCP服务器
"""

import os
import sys
# 设置FastMCP所需的环境变量
os.environ.setdefault('FASTMCP_LOG_LEVEL', 'INFO')

from fastmcp import FastMCP
from .tools import (
    format_table,
    set_table_cell_shading,
    apply_table_alternating_rows,
    highlight_table_header,
    merge_table_cells,
    merge_table_cells_horizontal,
    merge_table_cells_vertical,
    set_table_cell_alignment,
    set_table_alignment_all,
    format_table_cell_text,
    set_table_cell_padding,
    set_table_column_width,
    set_table_column_widths,
    set_table_width,
    auto_fit_table_columns
)

# 初始化FastMCP服务器
mcp = FastMCP("Word文档表格编辑")


def register_tools():
    """使用FastMCP装饰器注册所有工具"""

    @mcp.tool()
    async def format_table_tool(filename: str, table_index: int, has_header_row: str = "",
                         border_style: str = "", shading: list = []):
        """格式化表格的边框、阴影和结构

        参数说明:
        - has_header_row: "true" 表示有标题行，"false" 表示无标题行，""表示不设置
        - border_style: 边框样式名称，""表示不设置
        - shading: 阴影颜色列表，[]表示不设置
        """
        # Convert parameters
        has_header_param = None
        if has_header_row.lower() == "true":
            has_header_param = True
        elif has_header_row.lower() == "false":
            has_header_param = False

        border_style_param = border_style if border_style and border_style.strip() else None
        shading_param = shading if shading else None

        return await format_table(filename, table_index, has_header_param, border_style_param, shading_param)

    @mcp.tool()
    async def set_table_cell_shading_tool(filename: str, table_index: int, row_index: int,
                                   col_index: int, fill_color: str, pattern: str = "clear"):
        """为特定表格单元格应用阴影/填充"""
        return await set_table_cell_shading(filename, table_index, row_index, col_index, fill_color, pattern)

    @mcp.tool()
    async def apply_table_alternating_rows_tool(filename: str, table_index: int,
                                        color1: str = "FFFFFF", color2: str = "F2F2F2"):
        """为表格应用交替行颜色以提高可读性"""
        return await apply_table_alternating_rows(filename, table_index, color1, color2)

    @mcp.tool()
    async def highlight_table_header_tool(filename: str, table_index: int,
                                   header_color: str = "4472C4", text_color: str = "FFFFFF"):
        """为表格标题行应用特殊高亮"""
        return await highlight_table_header(filename, table_index, header_color, text_color)

    @mcp.tool()
    async def merge_table_cells_tool(filename: str, table_index: int, start_row: int, start_col: int,
                              end_row: int, end_col: int):
        """合并表格中矩形区域的单元格"""
        return await merge_table_cells(filename, table_index, start_row, start_col, end_row, end_col)

    @mcp.tool()
    async def merge_table_cells_horizontal_tool(filename: str, table_index: int, row_index: int,
                                         start_col: int, end_col: int):
        """水平合并单行中的单元格"""
        return await merge_table_cells_horizontal(filename, table_index, row_index, start_col, end_col)

    @mcp.tool()
    async def merge_table_cells_vertical_tool(filename: str, table_index: int, col_index: int,
                                       start_row: int, end_row: int):
        """垂直合并单列中的单元格"""
        return await merge_table_cells_vertical(filename, table_index, col_index, start_row, end_row)

    @mcp.tool()
    async def set_table_cell_alignment_tool(filename: str, table_index: int, row_index: int, col_index: int,
                                     horizontal: str = "left", vertical: str = "top"):
        """设置特定表格单元格的文本对齐方式"""
        return await set_table_cell_alignment(filename, table_index, row_index, col_index, horizontal, vertical)

    @mcp.tool()
    async def set_table_alignment_all_tool(filename: str, table_index: int,
                                    horizontal: str = "left", vertical: str = "top"):
        """设置表格中所有单元格的文本对齐方式"""
        return await set_table_alignment_all(filename, table_index, horizontal, vertical)

    @mcp.tool()
    async def format_table_cell_text_tool(filename: str, table_index: int, row_index: int, col_index: int,
                                   text_content: str = "", bold: str = "", italic: str = "",
                                   underline: str = "", color: str = "", font_size: int = 0,
                                   font_name: str = ""):
        """格式化特定表格单元格内的文本

        参数说明:
        - text_content: 单元格文本内容，""表示不修改
        - bold: "true" 表示粗体，"false" 表示非粗体，""表示不改变
        - italic: "true" 表示斜体，"false" 表示非斜体，""表示不改变
        - underline: "true" 表示下划线，"false" 表示无下划线，""表示不改变
        - color: 文本颜色，""表示不改变
        - font_size: 字体大小（磅），0表示不改变
        - font_name: 字体名称，""表示不改变
        """
        # Convert parameters
        text_content_param = text_content if text_content and text_content.strip() else None

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

        return await format_table_cell_text(filename, table_index, row_index, col_index,
                                                text_content_param, bold_param, italic_param,
                                                underline_param, color_param, font_size_param, font_name_param)

    @mcp.tool()
    async def set_table_cell_padding_tool(filename: str, table_index: int, row_index: int, col_index: int,
                                   top: float = 0.0, bottom: float = 0.0, left: float = 0.0,
                                   right: float = 0.0, unit: str = "points"):
        """设置特定表格单元格的内边距/边距

        参数说明:
        - top, bottom, left, right: 内边距值，0.0表示不设置
        - unit: 单位（"points", "inches", "cm"等）
        """
        # Convert parameters
        top_param = top if top > 0 else None
        bottom_param = bottom if bottom > 0 else None
        left_param = left if left > 0 else None
        right_param = right if right > 0 else None

        return await set_table_cell_padding(filename, table_index, row_index, col_index,
                                                top_param, bottom_param, left_param, right_param, unit)

    @mcp.tool()
    async def set_table_column_width_tool(filename: str, table_index: int, col_index: int,
                                   width: float, width_type: str = "points"):
        """设置特定表格列的宽度"""
        return await set_table_column_width(filename, table_index, col_index, width, width_type)

    @mcp.tool()
    async def set_table_column_widths_tool(filename: str, table_index: int, widths: list,
                                    width_type: str = "points"):
        """设置多个表格列的宽度"""
        return await set_table_column_widths(filename, table_index, widths, width_type)

    @mcp.tool()
    async def set_table_width_tool(filename: str, table_index: int, width: float,
                            width_type: str = "points"):
        """设置表格的整体宽度"""
        return await set_table_width(filename, table_index, width, width_type)

    @mcp.tool()
    async def auto_fit_table_columns_tool(filename: str, table_index: int):
        """设置表格列根据内容自动调整宽度"""
        return await auto_fit_table_columns(filename, table_index)


def main():
    """服务器的主入口点 - 只支持stdio传输"""
    # 注册所有工具
    register_tools()

    print("启动Word文档表格编辑MCP服务器...")
    print("提供以下功能:")
    print("- format_table_tool: 格式化表格")
    print("- set_table_cell_shading_tool: 设置单元格阴影")
    print("- apply_table_alternating_rows_tool: 应用交替行颜色")
    print("- highlight_table_header_tool: 高亮表格标题")
    print("- merge_table_cells_tool: 合并单元格")
    print("- merge_table_cells_horizontal_tool: 水平合并单元格")
    print("- merge_table_cells_vertical_tool: 垂直合并单元格")
    print("- set_table_cell_alignment_tool: 设置单元格对齐")
    print("- set_table_alignment_all_tool: 设置表格整体对齐")
    print("- format_table_cell_text_tool: 格式化单元格文本")
    print("- set_table_cell_padding_tool: 设置单元格内边距")
    print("- set_table_column_width_tool: 设置列宽度")
    print("- set_table_column_widths_tool: 设置多列宽度")
    print("- set_table_width_tool: 设置表格宽度")
    print("- auto_fit_table_columns_tool: 自动调整列宽")

    try:
        # 只使用stdio传输运行
        mcp.run(transport='stdio')
    except KeyboardInterrupt:
        print("\n正在关闭Word文档表格编辑服务器...")
    except Exception as e:
        print(f"启动服务器时出错: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
