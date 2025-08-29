"""
文件处理工具 - 提供文件操作相关的工具函数
"""

import os
import tempfile
from pathlib import Path
from typing import Dict, Any, List


class FileUtils:
    """文件处理工具类"""
    
    @staticmethod
    def validate_file_path(filepath: str) -> bool:
        """
        验证文件路径是否有效
        
        Args:
            filepath: 文件路径
            
        Returns:
            文件是否存在且可读
        """
        if not filepath:
            return False
        
        file_path = Path(filepath)
        return file_path.exists() and file_path.is_file()
    
    @staticmethod
    def get_file_info(filepath: str) -> Dict[str, Any]:
        """
        获取文件信息
        
        Args:
            filepath: 文件路径
            
        Returns:
            文件信息字典
        """
        if not FileUtils.validate_file_path(filepath):
            return {"error": "文件不存在或不可访问"}
        
        file_path = Path(filepath)
        stat = file_path.stat()
        
        return {
            "name": file_path.name,
            "size": stat.st_size,
            "extension": file_path.suffix.lower(),
            "absolute_path": str(file_path.resolve()),
            "parent_dir": str(file_path.parent),
            "modified_time": stat.st_mtime
        }
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """
        格式化文件大小显示
        
        Args:
            size_bytes: 文件大小（字节）
            
        Returns:
            格式化的文件大小字符串
        """
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
    
    @staticmethod
    def create_temp_file(content: str, suffix: str = '.tmp', encoding: str = 'utf-8') -> str:
        """
        创建临时文件
        
        Args:
            content: 文件内容
            suffix: 文件后缀
            encoding: 文件编码
            
        Returns:
            临时文件路径
        """
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix=suffix,
            delete=False,
            encoding=encoding
        ) as temp_file:
            temp_file.write(content)
            return temp_file.name
    
    @staticmethod
    def cleanup_temp_file(filepath: str) -> bool:
        """
        清理临时文件
        
        Args:
            filepath: 文件路径
            
        Returns:
            清理是否成功
        """
        try:
            Path(filepath).unlink()
            return True
        except (OSError, FileNotFoundError):
            return False
    
    @staticmethod
    def ensure_dir_exists(dirpath: str) -> bool:
        """
        确保目录存在，不存在则创建
        
        Args:
            dirpath: 目录路径
            
        Returns:
            操作是否成功
        """
        try:
            os.makedirs(dirpath, exist_ok=True)
            return True
        except OSError:
            return False
    
    @staticmethod
    def list_files_by_extension(directory: str, extensions: List[str]) -> List[str]:
        """
        按扩展名列出目录中的文件
        
        Args:
            directory: 目录路径
            extensions: 文件扩展名列表
            
        Returns:
            匹配的文件路径列表
        """
        if not os.path.isdir(directory):
            return []
        
        files = []
        for file in os.listdir(directory):
            file_path = os.path.join(directory, file)
            if os.path.isfile(file_path):
                file_ext = Path(file).suffix.lower()
                if file_ext in extensions:
                    files.append(file_path)
        
        return sorted(files)