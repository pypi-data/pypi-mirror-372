#!/usr/bin/env python3
"""
Markdown格式转换 MCP服务器

统一的文档格式转换服务器，支持多种格式与Markdown之间的相互转换：
- Excel → Markdown
- PDF → Markdown  
- PPT → Markdown
- Word → Markdown
- Markdown → Word (支持模板)
"""

import asyncio
import os
from typing import Any, Dict, List

from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool, Resource

# 导入转换器
from .converters import (
    ExcelToMarkdownConverter,
    PDFToMarkdownConverter,
    PPTToMarkdownConverter,
    WordToMarkdownConverter,
    MarkdownToWordConverter
)
from .utils import FileUtils, ValidationUtils

# 创建MCP服务器
app = Server("markdown-format-converter")

# 全局配置
CONFIG = {
    "default_output_dir": "./output",
    "max_file_size": 50 * 1024 * 1024,  # 50MB
    "default_word_template": "product_manual_black.docx",
    "supported_formats": {
        "excel": [".xlsx", ".xls"],
        "pdf": [".pdf"],
        "ppt": [".pptx", ".ppt"],
        "word": [".docx", ".doc"],
        "markdown": [".md", ".markdown", ".txt"]
    }
}

# 初始化转换器
converters = {
    "excel_to_md": ExcelToMarkdownConverter(),
    "pdf_to_md": PDFToMarkdownConverter(),
    "ppt_to_md": PPTToMarkdownConverter(),
    "word_to_md": WordToMarkdownConverter(),
    "md_to_word": MarkdownToWordConverter()
}


@app.list_tools()
async def handle_list_tools() -> List[Tool]:
    """列出所有可用的转换工具"""
    return [
        Tool(
            name="excel_to_markdown",
            description="将Excel文件(.xlsx, .xls)转换为Markdown表格格式，支持多工作表",
            inputSchema={
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "要转换的Excel文件的绝对路径"
                    },
                    "sheet_name": {
                        "type": "string",
                        "description": "指定要转换的工作表名称（可选）"
                    }
                },
                "required": ["filepath"]
            }
        ),
        Tool(
            name="pdf_to_markdown",
            description="将PDF文件转换为Markdown格式，提取文本内容和结构",
            inputSchema={
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "要转换的PDF文件的绝对路径"
                    }
                },
                "required": ["filepath"]
            }
        ),
        Tool(
            name="ppt_to_markdown",
            description="将PowerPoint文件(.pptx, .ppt)转换为Markdown格式，保持幻灯片结构",
            inputSchema={
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "要转换的PowerPoint文件的绝对路径"
                    },
                    "include_slides": {
                        "type": "boolean",
                        "description": "是否包含幻灯片编号信息（默认: true）",
                        "default": True
                    }
                },
                "required": ["filepath"]
            }
        ),
        Tool(
            name="word_to_markdown",
            description="将Word文件(.docx, .doc)转换为Markdown格式，保持文档结构和格式",
            inputSchema={
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "要转换的Word文件的绝对路径"
                    },
                    "preserve_format": {
                        "type": "boolean",
                        "description": "是否尽量保持原文档格式（默认: true）",
                        "default": True
                    },
                    "extract_images": {
                        "type": "boolean",
                        "description": "是否提取图片信息（默认: true）",
                        "default": True
                    }
                },
                "required": ["filepath"]
            }
        ),
        Tool(
            name="markdown_to_word",
            description="将Markdown文件转换为Word文档，支持自定义模板和样式",
            inputSchema={
                "type": "object",
                "properties": {
                    "input_file": {
                        "type": "string",
                        "description": "输入的Markdown文件路径"
                    },
                    "output_file": {
                        "type": "string",
                        "description": "输出的Word文件路径（可选）",
                        "default": "output.docx"
                    },
                    "template": {
                        "type": "string",
                        "description": "Word模板文件路径（可选）"
                    },
                    "title": {
                        "type": "string",
                        "description": "文档标题（可选）"
                    },
                    "author": {
                        "type": "string",
                        "description": "文档作者（可选）"
                    }
                },
                "required": ["input_file"]
            }
        )
    ]


@app.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """处理工具调用"""
    try:
        if name == "excel_to_markdown":
            return await handle_excel_to_markdown(arguments)
        elif name == "pdf_to_markdown":
            return await handle_pdf_to_markdown(arguments)
        elif name == "ppt_to_markdown":
            return await handle_ppt_to_markdown(arguments)
        elif name == "word_to_markdown":
            return await handle_word_to_markdown(arguments)
        elif name == "markdown_to_word":
            return await handle_markdown_to_word(arguments)
        else:
            raise ValueError(f"未知工具: {name}")
            
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"❌ 错误: {str(e)}"
        )]


async def handle_excel_to_markdown(arguments: Dict[str, Any]) -> List[TextContent]:
    """处理Excel转Markdown"""
    filepath = arguments.get("filepath")
    sheet_name = arguments.get("sheet_name")
    
    if not filepath:
        raise ValueError("缺少必需参数: filepath")
    
    # 验证文件
    validation = ValidationUtils.validate_file_format(filepath, 'excel')
    if not validation['valid']:
        raise ValueError(validation['error'])
    
    size_validation = ValidationUtils.validate_file_size(filepath)
    if not size_validation['valid']:
        raise ValueError(size_validation['error'])
    
    # 执行转换
    result = converters["excel_to_md"].convert(filepath, sheet_name=sheet_name)
    
    return [
        TextContent(
            type="text",
            text=f"✅ {result['message']}\n\n" +
                 f"📁 输入文件: {result['input_file']}\n" +
                 f"📄 输出文件: {result['output_file']}\n" +
                 f"📊 输入大小: {result['input_size']}\n" +
                 f"📊 输出大小: {result['output_size']}"
        ),
        TextContent(
            type="text",
            text="📋 转换后的Markdown内容:"
        ),
        TextContent(
            type="text",
            text=result['content']
        )
    ]


async def handle_pdf_to_markdown(arguments: Dict[str, Any]) -> List[TextContent]:
    """处理PDF转Markdown"""
    filepath = arguments.get("filepath")
    
    if not filepath:
        raise ValueError("缺少必需参数: filepath")
    
    # 验证文件
    validation = ValidationUtils.validate_file_format(filepath, 'pdf')
    if not validation['valid']:
        raise ValueError(validation['error'])
    
    size_validation = ValidationUtils.validate_file_size(filepath)
    if not size_validation['valid']:
        raise ValueError(size_validation['error'])
    
    # 执行转换
    result = converters["pdf_to_md"].convert(filepath)
    
    return [
        TextContent(
            type="text",
            text=f"✅ {result['message']}\n\n" +
                 f"📁 输入文件: {result['input_file']}\n" +
                 f"📄 输出文件: {result['output_file']}\n" +
                 f"📊 输入大小: {result['input_size']}\n" +
                 f"📊 输出大小: {result['output_size']}"
        ),
        TextContent(
            type="text",
            text="📋 转换后的Markdown内容:"
        ),
        TextContent(
            type="text",
            text=result['content']
        )
    ]


async def handle_ppt_to_markdown(arguments: Dict[str, Any]) -> List[TextContent]:
    """处理PPT转Markdown"""
    filepath = arguments.get("filepath")
    include_slides = arguments.get("include_slides", True)
    
    if not filepath:
        raise ValueError("缺少必需参数: filepath")
    
    # 验证文件
    validation = ValidationUtils.validate_file_format(filepath, 'ppt')
    if not validation['valid']:
        raise ValueError(validation['error'])
    
    size_validation = ValidationUtils.validate_file_size(filepath)
    if not size_validation['valid']:
        raise ValueError(size_validation['error'])
    
    # 执行转换
    result = converters["ppt_to_md"].convert(filepath, include_slides=include_slides)
    
    return [
        TextContent(
            type="text",
            text=f"✅ {result['message']}\n\n" +
                 f"📁 输入文件: {result['input_file']}\n" +
                 f"📄 输出文件: {result['output_file']}\n" +
                 f"📊 输入大小: {result['input_size']}\n" +
                 f"📊 输出大小: {result['output_size']}"
        ),
        TextContent(
            type="text",
            text="📋 转换后的Markdown内容:"
        ),
        TextContent(
            type="text",
            text=result['content']
        )
    ]


async def handle_word_to_markdown(arguments: Dict[str, Any]) -> List[TextContent]:
    """处理Word转Markdown"""
    filepath = arguments.get("filepath")
    preserve_format = arguments.get("preserve_format", True)
    extract_images = arguments.get("extract_images", True)
    
    if not filepath:
        raise ValueError("缺少必需参数: filepath")
    
    # 验证文件
    validation = ValidationUtils.validate_file_format(filepath, 'word')
    if not validation['valid']:
        raise ValueError(validation['error'])
    
    size_validation = ValidationUtils.validate_file_size(filepath)
    if not size_validation['valid']:
        raise ValueError(size_validation['error'])
    
    # 执行转换
    result = converters["word_to_md"].convert(
        filepath, 
        preserve_format=preserve_format,
        extract_images=extract_images
    )
    
    return [
        TextContent(
            type="text",
            text=f"✅ {result['message']}\n\n" +
                 f"📁 输入文件: {result['input_file']}\n" +
                 f"📄 输出文件: {result['output_file']}\n" +
                 f"📊 输入大小: {result['input_size']}\n" +
                 f"📊 输出大小: {result['output_size']}"
        ),
        TextContent(
            type="text",
            text="📋 转换后的Markdown内容:"
        ),
        TextContent(
            type="text",
            text=result['content']
        )
    ]


async def handle_markdown_to_word(arguments: Dict[str, Any]) -> List[TextContent]:
    """处理Markdown转Word"""
    input_file = arguments.get("input_file")
    output_file = arguments.get("output_file", "output.docx")
    template = arguments.get("template")
    title = arguments.get("title")
    author = arguments.get("author")
    
    if not input_file:
        raise ValueError("缺少必需参数: input_file")
    
    # 验证输入文件
    validation = ValidationUtils.validate_file_format(input_file, 'markdown')
    if not validation['valid']:
        raise ValueError(validation['error'])
    
    size_validation = ValidationUtils.validate_file_size(input_file)
    if not size_validation['valid']:
        raise ValueError(size_validation['error'])
    
    # 验证输出路径
    output_validation = ValidationUtils.validate_output_path(output_file)
    if not output_validation['valid']:
        raise ValueError(output_validation['error'])
    
    # 验证模板文件（如果提供）
    if template:
        template_validation = ValidationUtils.validate_template_file(template)
        if not template_validation['valid']:
            raise ValueError(template_validation['error'])
    
    # 执行转换
    result = converters["md_to_word"].convert(
        input_file=input_file,
        output_file=output_file,
        template_path=template,
        title=title,
        author=author
    )
    
    return [
        TextContent(
            type="text",
            text=f"✅ {result['message']}\n\n" +
                 f"📁 输入文件: {result['input_file']}\n" +
                 f"📄 输出文件: {result['output_file']}\n" +
                 f"📊 输入大小: {result['input_size']}\n" +
                 f"📊 输出大小: {result['output_size']}\n" +
                 f"🎨 使用模板: {result['template']}\n" +
                 f"⏱️ 处理时间: {result['processing_time']} 秒"
        )
    ]


async def main():
    """启动MCP服务器"""
    # 确保输出目录存在
    FileUtils.ensure_dir_exists(CONFIG["default_output_dir"])
    
    # 启动服务器
    async with stdio_server() as (read_stream, write_stream):
        capabilities = app.get_capabilities(
            notification_options=NotificationOptions(),
            experimental_capabilities={}
        )
        
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())


