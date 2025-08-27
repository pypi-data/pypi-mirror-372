"""
LiblibAI AI图片生成MCP工具

基于LiblibAI API的AI图片生成服务，支持各种风格的图片创作
通过MCP协议与Claude Desktop等AI客户端集成

主要功能：
- create_image: 根据提示词生成AI图片
- check_image_status: 查询图片生成状态
- generate_and_wait: 一站式生成并等待完成
- health_check: 系统健康检查
"""

__version__ = "1.0.0"
__author__ = "LiblibAI MCP Developer"
__email__ = "developer@example.com"
__description__ = "LiblibAI AI图片生成MCP工具"

from .main import main

__all__ = ["main"]