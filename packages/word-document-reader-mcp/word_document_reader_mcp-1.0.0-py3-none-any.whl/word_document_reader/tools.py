"""
Word文档内容读取工具函数

提供五个核心的文档读取功能
"""

import os
import json
from .utils import (
    ensure_docx_extension,
    get_document_properties,
    extract_document_text,
    get_document_structure,
    get_paragraph_text,
    find_text
)


async def get_document_info(filename: str) -> str:
    """获取Word文档的信息
    
    Args:
        filename: Word文档的路径
        
    Returns:
        JSON格式的文档信息字符串
    """
    filename = ensure_docx_extension(filename)
    
    if not os.path.exists(filename):
        raise FileNotFoundError(f"Document {filename} does not exist")
    
    try:
        properties = get_document_properties(filename)
        return json.dumps(properties, indent=2, ensure_ascii=False)
    except Exception as e:
        return f"Failed to get document info: {str(e)}"


async def get_document_text(filename: str) -> str:
    """提取Word文档中的所有文本
    
    Args:
        filename: Word文档的路径
        
    Returns:
        文档的文本内容
    """
    filename = ensure_docx_extension(filename)
    
    return extract_document_text(filename)


async def get_document_outline(filename: str) -> str:
    """获取Word文档的结构大纲
    
    Args:
        filename: Word文档的路径
        
    Returns:
        JSON格式的文档结构字符串
    """
    filename = ensure_docx_extension(filename)
    
    structure = get_document_structure(filename)
    return json.dumps(structure, indent=2, ensure_ascii=False)


async def get_paragraph_text_from_document(filename: str, paragraph_index: int) -> str:
    """从Word文档中获取指定段落的文本
    
    Args:
        filename: Word文档的路径
        paragraph_index: 段落索引（从0开始）
        
    Returns:
        JSON格式的段落信息字符串
    """
    filename = ensure_docx_extension(filename)
    
    if not os.path.exists(filename):
        raise FileNotFoundError(f"Document {filename} does not exist")

    if paragraph_index < 0:
        raise ValueError("Invalid parameter: paragraph_index must be a non-negative integer")
    
    try:
        result = get_paragraph_text(filename, paragraph_index)
        return json.dumps(result, indent=2, ensure_ascii=False)
    except Exception as e:
        return f"Failed to get paragraph text: {str(e)}"


async def find_text_in_document(filename: str, text_to_find: str, match_case: bool = True, whole_word: bool = False) -> str:
    """在Word文档中查找指定文本
    
    Args:
        filename: Word文档的路径
        text_to_find: 要查找的文本
        match_case: 是否区分大小写（True）或忽略大小写（False）
        whole_word: 是否只匹配完整单词（True）或匹配子字符串（False）
        
    Returns:
        JSON格式的搜索结果字符串
    """
    filename = ensure_docx_extension(filename)
    
    if not os.path.exists(filename):
        raise FileNotFoundError(f"Document {filename} does not exist")

    if not text_to_find:
        raise ValueError("Search text cannot be empty")
    
    try:
        result = find_text(filename, text_to_find, match_case, whole_word)
        return json.dumps(result, indent=2, ensure_ascii=False)
    except Exception as e:
        return f"Failed to find text: {str(e)}"
