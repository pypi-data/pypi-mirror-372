"""
基础转换器类 - 提供转换器的通用接口和功能
"""

import tempfile
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional


class BaseConverter(ABC):
    """基础转换器抽象类"""
    
    def __init__(self):
        self.temp_files = []  # 跟踪临时文件以便清理
    
    @abstractmethod
    def convert(self, filepath: str, **kwargs) -> Dict[str, Any]:
        """
        转换文件的抽象方法
        
        Args:
            filepath: 输入文件路径
            **kwargs: 转换选项
            
        Returns:
            转换结果字典，包含状态和内容信息
        """
        pass
    
    def validate_file(self, filepath: str, valid_extensions: list) -> None:
        """
        验证文件是否存在且格式正确
        
        Args:
            filepath: 文件路径
            valid_extensions: 有效的文件扩展名列表
            
        Raises:
            FileNotFoundError: 文件不存在
            ValueError: 文件格式不支持
        """
        file_path = Path(filepath)
        
        # 检查文件是否存在
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {filepath}")
        
        # 检查文件扩展名
        if file_path.suffix.lower() not in valid_extensions:
            raise ValueError(f"文件格式不支持: {file_path.suffix} (支持: {', '.join(valid_extensions)})")
    
    def create_temp_file(self, content: str, suffix: str = '.md', encoding: str = 'utf-8') -> str:
        """
        创建临时文件并写入内容
        
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
            temp_path = temp_file.name
            self.temp_files.append(temp_path)  # 记录临时文件
            return temp_path
    
    def cleanup_temp_files(self):
        """清理临时文件"""
        for temp_file in self.temp_files:
            try:
                Path(temp_file).unlink()
            except (OSError, FileNotFoundError):
                pass  # 忽略清理失败
        self.temp_files.clear()
    
    def get_file_size(self, filepath: str) -> int:
        """获取文件大小（字节）"""
        return Path(filepath).stat().st_size
    
    def format_file_size(self, size_bytes: int) -> str:
        """格式化文件大小显示"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"