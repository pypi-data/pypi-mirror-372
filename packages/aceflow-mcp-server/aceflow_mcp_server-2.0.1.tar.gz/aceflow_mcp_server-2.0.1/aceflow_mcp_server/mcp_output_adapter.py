#!/usr/bin/env python3
"""
MCP输出适配器
负责将AceFlow工具的输出转换为MCP标准JSON格式

设计原则：
- 保留所有emoji、markdown、中文字符
- 转换为MCP标准的content数组格式
- 提供统一的错误处理机制
"""

import json
import logging
from typing import Any, Dict, List, Union

logger = logging.getLogger(__name__)


class MCPOutputAdapter:
    """MCP输出适配器类"""
    
    def __init__(self):
        self.version = '1.0.0'
    
    def convert_to_mcp_format(self, input_data: Any) -> Dict[str, Any]:
        """
        将CLI输出转换为MCP标准格式
        
        Args:
            input_data: CLI输出（可能是字符串、对象等）
            
        Returns:
            MCP标准格式的响应
        """
        try:
            text = self.normalize_input(input_data)
            sanitized_text = self.sanitize_text(text)
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": sanitized_text
                    }
                ]
            }
        except Exception as error:
            return self.handle_error(error)
    
    def normalize_input(self, input_data: Any) -> str:
        """
        标准化输入，将各种类型转换为字符串
        
        Args:
            input_data: 输入数据
            
        Returns:
            标准化后的字符串
        """
        # 处理None
        if input_data is None:
            return 'null'
        
        # 处理字符串
        if isinstance(input_data, str):
            return input_data
        
        # 处理有__str__方法的对象
        if hasattr(input_data, '__str__') and not isinstance(input_data, (dict, list)):
            try:
                str_result = str(input_data)
                # 避免使用默认的object.__str__
                if not str_result.startswith('<') or not str_result.endswith('>'):
                    return str_result
            except Exception:
                pass
        
        # 处理字典和列表
        if isinstance(input_data, (dict, list)):
            return json.dumps(input_data, indent=2, ensure_ascii=False)
        
        # 其他类型直接转换
        return str(input_data)
    
    def sanitize_text(self, text: str) -> str:
        """
        清理文本，确保JSON兼容性但保留所有格式
        
        Args:
            text: 输入文本
            
        Returns:
            清理后的文本
        """
        # 对于MCP协议，我们实际上不需要做任何转义
        # emoji、中文字符、markdown都应该保留
        # MCP的content格式本身就支持UTF-8字符
        return text
    
    def handle_error(self, error: Union[Exception, str]) -> Dict[str, Any]:
        """
        统一的错误处理
        
        Args:
            error: 错误对象或错误信息
            
        Returns:
            MCP格式的错误响应
        """
        if isinstance(error, Exception):
            error_message = str(error)
            logger.error(f"MCP输出适配器错误: {error_message}", exc_info=True)
        else:
            error_message = str(error)
            logger.error(f"MCP输出适配器错误: {error_message}")
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"❌ 执行失败: {error_message}"
                }
            ],
            "isError": True
        }
    
    def validate_mcp_format(self, output: Any) -> bool:
        """
        验证输出格式是否符合MCP标准
        
        Args:
            output: 要验证的输出
            
        Returns:
            是否符合标准
        """
        if not isinstance(output, dict):
            return False
        
        if 'content' not in output:
            return False
        
        if not isinstance(output['content'], list):
            return False
        
        return all(
            isinstance(item, dict) and
            item.get('type') == 'text' and
            isinstance(item.get('text'), str)
            for item in output['content']
        )
    
    def create_success_response(self, text: str) -> Dict[str, Any]:
        """
        创建成功响应的快捷方法
        
        Args:
            text: 响应文本
            
        Returns:
            MCP格式响应
        """
        return self.convert_to_mcp_format(text)
    
    def create_error_response(self, message: str) -> Dict[str, Any]:
        """
        创建错误响应的快捷方法
        
        Args:
            message: 错误消息
            
        Returns:
            MCP格式错误响应
        """
        return self.handle_error(message)
    
    def create_json_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建JSON格式响应的快捷方法
        
        Args:
            data: 要转换的数据
            
        Returns:
            MCP格式响应
        """
        json_text = json.dumps(data, indent=2, ensure_ascii=False)
        return self.convert_to_mcp_format(json_text)