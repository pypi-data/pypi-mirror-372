"""Word to Text MCP Server Package

一个基于FastMCP的Word文档转文本分析服务器包。
提供Word文档处理、文本提取和内容分析功能。
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"
__description__ = "FastMCP Word文档转文本分析服务器"

# 导入主要功能
from .server import (
    convert_word_to_text,
    process_word_document,
    analyze_document_content,
    create_mcp_server
)

# 定义包的公共接口
__all__ = [
    "convert_word_to_text",
    "process_word_document", 
    "analyze_document_content",
    "create_mcp_server",
    "__version__"
]