"""
Word文档内容添加工具的辅助函数

提供文件处理和验证相关的辅助功能
"""

import os
import stat


def ensure_docx_extension(filename: str) -> str:
    """确保文件名有.docx扩展名
    
    Args:
        filename: 原始文件名
        
    Returns:
        带有.docx扩展名的文件名
    """
    if not filename.lower().endswith('.docx'):
        return filename + '.docx'
    return filename


def check_file_writeable(filename: str) -> tuple[bool, str]:
    """检查文件是否可写
    
    Args:
        filename: 文件路径
        
    Returns:
        (是否可写, 错误信息)
    """
    try:
        # 检查文件是否存在
        if not os.path.exists(filename):
            return False, "File does not exist"
        
        # 检查文件权限
        if not os.access(filename, os.W_OK):
            return False, "File is not writable (permission denied)"
        
        # 检查文件是否被其他程序锁定
        try:
            # 尝试以写入模式打开文件
            with open(filename, 'r+b') as f:
                pass
        except PermissionError:
            return False, "File is currently open in another application"
        except IOError as e:
            return False, f"File access error: {str(e)}"
        
        return True, ""
    
    except Exception as e:
        return False, f"Error checking file: {str(e)}"


def validate_image_file(image_path: str) -> tuple[bool, str]:
    """验证图片文件是否有效
    
    Args:
        image_path: 图片文件路径
        
    Returns:
        (是否有效, 错误信息)
    """
    # 支持的图片格式
    supported_formats = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif'}
    
    try:
        # 检查文件是否存在
        if not os.path.exists(image_path):
            return False, f"Image file does not exist: {image_path}"
        
        # 检查文件扩展名
        _, ext = os.path.splitext(image_path.lower())
        if ext not in supported_formats:
            return False, f"Unsupported image format: {ext}. Supported formats: {', '.join(supported_formats)}"
        
        # 检查文件是否可读
        if not os.access(image_path, os.R_OK):
            return False, "Image file is not readable (permission denied)"
        
        # 检查文件大小
        file_size = os.path.getsize(image_path)
        if file_size == 0:
            return False, "Image file is empty"
        
        # 可选：检查文件是否真的是图片（需要PIL/Pillow）
        try:
            from PIL import Image
            with Image.open(image_path) as img:
                img.verify()  # 验证图片完整性
        except ImportError:
            # 如果没有安装PIL，跳过图片验证
            pass
        except Exception as e:
            return False, f"Invalid image file: {str(e)}"
        
        return True, ""
    
    except Exception as e:
        return False, f"Error validating image: {str(e)}"


def format_file_size(size_bytes: int) -> str:
    """格式化文件大小显示
    
    Args:
        size_bytes: 文件大小（字节）
        
    Returns:
        格式化的文件大小字符串
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size = float(size_bytes)
    
    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1
    
    return f"{size:.1f} {size_names[i]}"


def get_file_info(filename: str) -> dict:
    """获取文件基本信息
    
    Args:
        filename: 文件路径
        
    Returns:
        包含文件信息的字典
    """
    try:
        if not os.path.exists(filename):
            return {"error": "File does not exist"}
        
        stat_info = os.stat(filename)
        
        return {
            "filename": os.path.basename(filename),
            "full_path": os.path.abspath(filename),
            "size": stat_info.st_size,
            "size_formatted": format_file_size(stat_info.st_size),
            "created": stat_info.st_ctime,
            "modified": stat_info.st_mtime,
            "is_readable": os.access(filename, os.R_OK),
            "is_writable": os.access(filename, os.W_OK),
        }
    
    except Exception as e:
        return {"error": f"Error getting file info: {str(e)}"}


def create_backup_filename(filename: str) -> str:
    """创建备份文件名
    
    Args:
        filename: 原始文件名
        
    Returns:
        备份文件名
    """
    base, ext = os.path.splitext(filename)
    counter = 1
    
    while True:
        backup_name = f"{base}_backup_{counter}{ext}"
        if not os.path.exists(backup_name):
            return backup_name
        counter += 1
