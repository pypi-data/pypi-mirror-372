"""
验证工具 - 提供文件和数据验证功能
"""

import os
import re
from pathlib import Path
from typing import Dict, Any, List, Optional


class ValidationUtils:
    """验证工具类"""
    
    # 支持的文件格式
    SUPPORTED_FORMATS = {
        'excel': ['.xlsx', '.xls'],
        'pdf': ['.pdf'],
        'ppt': ['.pptx', '.ppt'],
        'word': ['.docx', '.doc'],
        'markdown': ['.md', '.markdown', '.txt']
    }
    
    # 最大文件大小限制 (50MB)
    MAX_FILE_SIZE = 50 * 1024 * 1024
    
    @classmethod
    def validate_file_format(cls, filepath: str, format_type: str) -> Dict[str, Any]:
        """
        验证文件格式是否支持
        
        Args:
            filepath: 文件路径
            format_type: 格式类型 (excel, pdf, ppt, word, markdown)
            
        Returns:
            验证结果字典
        """
        if format_type not in cls.SUPPORTED_FORMATS:
            return {
                'valid': False,
                'error': f"不支持的格式类型: {format_type}"
            }
        
        if not os.path.exists(filepath):
            return {
                'valid': False,
                'error': f"文件不存在: {filepath}"
            }
        
        file_ext = Path(filepath).suffix.lower()
        supported_exts = cls.SUPPORTED_FORMATS[format_type]
        
        if file_ext not in supported_exts:
            return {
                'valid': False,
                'error': f"文件格式不支持: {file_ext} (支持: {', '.join(supported_exts)})"
            }
        
        return {'valid': True}
    
    @classmethod
    def validate_file_size(cls, filepath: str, max_size: Optional[int] = None) -> Dict[str, Any]:
        """
        验证文件大小
        
        Args:
            filepath: 文件路径
            max_size: 最大文件大小（字节），默认使用类变量
            
        Returns:
            验证结果字典
        """
        if not os.path.exists(filepath):
            return {
                'valid': False,
                'error': f"文件不存在: {filepath}"
            }
        
        file_size = os.path.getsize(filepath)
        limit = max_size or cls.MAX_FILE_SIZE
        
        if file_size > limit:
            return {
                'valid': False,
                'error': f"文件太大: {file_size} 字节 (限制: {limit} 字节)",
                'file_size': file_size,
                'size_limit': limit
            }
        
        return {
            'valid': True,
            'file_size': file_size
        }
    
    @classmethod
    def validate_output_path(cls, output_path: str) -> Dict[str, Any]:
        """
        验证输出路径是否有效
        
        Args:
            output_path: 输出文件路径
            
        Returns:
            验证结果字典
        """
        output_dir = os.path.dirname(output_path)
        
        # 检查目录是否存在，不存在则尝试创建
        if output_dir and not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir, exist_ok=True)
            except OSError as e:
                return {
                    'valid': False,
                    'error': f"无法创建输出目录: {e}"
                }
        
        # 检查目录写入权限
        test_dir = output_dir or '.'
        if not os.access(test_dir, os.W_OK):
            return {
                'valid': False,
                'error': f"输出目录没有写入权限: {test_dir}"
            }
        
        return {'valid': True}
    
    @classmethod
    def validate_markdown_content(cls, content: str) -> Dict[str, Any]:
        """
        验证Markdown内容的基本结构
        
        Args:
            content: Markdown内容
            
        Returns:
            验证结果字典
        """
        if not content or not content.strip():
            return {
                'valid': False,
                'error': "内容为空"
            }
        
        lines = content.splitlines()
        warnings = []
        
        # 检查是否有标题
        has_headers = any(line.strip().startswith('#') for line in lines)
        if not has_headers:
            warnings.append("没有发现标题标记 (#)")
        
        # 检查是否有过长的行
        long_lines = [i + 1 for i, line in enumerate(lines) if len(line) > 120]
        if long_lines:
            warnings.append(f"发现过长的行: {long_lines[:5]}{'...' if len(long_lines) > 5 else ''}")
        
        # 检查链接格式
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        broken_links = []
        for i, line in enumerate(lines):
            matches = re.findall(link_pattern, line)
            for text, url in matches:
                if not url.strip() or url.strip() in ['#', '']:
                    broken_links.append(f"行 {i + 1}: [{text}]({url})")
        
        if broken_links:
            warnings.append(f"发现疑似无效链接: {broken_links[:3]}{'...' if len(broken_links) > 3 else ''}")
        
        return {
            'valid': True,
            'warnings': warnings,
            'lines': len(lines),
            'characters': len(content)
        }
    
    @classmethod
    def validate_template_file(cls, template_path: str) -> Dict[str, Any]:
        """
        验证Word模板文件
        
        Args:
            template_path: 模板文件路径
            
        Returns:
            验证结果字典
        """
        if not os.path.exists(template_path):
            return {
                'valid': False,
                'error': f"模板文件不存在: {template_path}"
            }
        
        file_ext = Path(template_path).suffix.lower()
        valid_template_exts = ['.docx', '.dotx', '.doc', '.dot']
        
        if file_ext not in valid_template_exts:
            return {
                'valid': False,
                'error': f"模板格式不支持: {file_ext} (支持: {', '.join(valid_template_exts)})"
            }
        
        # 检查文件大小
        template_size = os.path.getsize(template_path)
        if template_size > 10 * 1024 * 1024:  # 10MB limit for templates
            return {
                'valid': False,
                'error': f"模板文件过大: {template_size} 字节 (限制: 10MB)"
            }
        
        return {
            'valid': True,
            'template_size': template_size,
            'template_format': file_ext
        }