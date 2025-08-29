"""
Word转Markdown转换器
"""

from typing import Any, Dict
from markitdown import MarkItDown
from .base_converter import BaseConverter


class WordToMarkdownConverter(BaseConverter):
    """Word文件转换为Markdown格式的转换器"""
    
    def __init__(self):
        super().__init__()
        self.markitdown = MarkItDown()
        self.valid_extensions = ['.docx', '.doc']
    
    def convert(self, filepath: str, preserve_format: bool = True, extract_images: bool = True, **kwargs) -> Dict[str, Any]:
        """
        转换Word文件为Markdown格式
        
        Args:
            filepath: Word文件路径
            preserve_format: 是否尽量保持原文档格式
            extract_images: 是否提取图片信息
            **kwargs: 其他转换参数
            
        Returns:
            转换结果字典
        """
        # 验证文件
        self.validate_file(filepath, self.valid_extensions)
        
        # 执行转换
        result = self.markitdown.convert(filepath)
        
        # 创建临时输出文件
        temp_path = self.create_temp_file(result.text_content, suffix='.md')
        
        # 准备结果
        file_size = self.get_file_size(filepath)
        output_size = len(result.text_content.encode('utf-8'))
        
        # 构建选项描述
        options = []
        if preserve_format:
            options.append("保持格式")
        if extract_images:
            options.append("提取图片")
        
        options_text = f" ({', '.join(options)})" if options else ""
        
        conversion_result = {
            'success': True,
            'input_file': filepath,
            'output_file': temp_path,
            'preserve_format': preserve_format,
            'extract_images': extract_images,
            'content': result.text_content,
            'input_size': self.format_file_size(file_size),
            'output_size': self.format_file_size(output_size),
            'message': f"Word文档转换成功！{options_text}"
        }
        
        return conversion_result