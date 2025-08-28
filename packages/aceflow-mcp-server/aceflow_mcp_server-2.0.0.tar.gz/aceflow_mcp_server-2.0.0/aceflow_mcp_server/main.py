#!/usr/bin/env python3
"""
AceFlow MCP Server 主入口点
支持多种运行模式和配置选项
"""

import argparse
import logging
import os
import sys
from typing import Optional

from .mcp_stdio_server import MCPStdioServer


def setup_logging(log_level: str, log_file: Optional[str] = None):
    """设置日志配置"""
    level = getattr(logging, log_level.upper(), logging.INFO)
    
    # 配置日志格式
    formatter = logging.Formatter(
        '[%(asctime)s] %(name)s - %(levelname)s - %(message)s'
    )
    
    # 配置stderr处理器（用于调试）
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setFormatter(formatter)
    
    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(stderr_handler)
    
    # 如果指定了日志文件，添加文件处理器
    if log_file:
        try:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
        except Exception as e:
            logging.error(f"无法创建日志文件 {log_file}: {e}")


def create_parser() -> argparse.ArgumentParser:
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        description='AceFlow MCP Server - AI驱动的工作流管理系统',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 启动stdio模式服务器（默认）
  python -m aceflow_mcp_server.main
  
  # 启动调试模式
  python -m aceflow_mcp_server.main --debug
  
  # 指定日志级别和文件
  python -m aceflow_mcp_server.main --log-level DEBUG --log-file mcp.log
  
  # 开发模式
  python -m aceflow_mcp_server.main --mode dev --debug
        """
    )
    
    parser.add_argument(
        '--mode',
        choices=['stdio', 'dev'],
        default='stdio',
        help='运行模式 (默认: stdio)'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='WARNING',
        help='日志级别 (默认: WARNING)'
    )
    
    parser.add_argument(
        '--log-file',
        type=str,
        help='日志文件路径 (可选)'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='启用调试模式'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='AceFlow MCP Server 1.0.4'
    )
    
    return parser


def main():
    """主函数"""
    parser = create_parser()
    args = parser.parse_args()
    
    # 设置环境变量
    if args.debug:
        os.environ['MCP_DEBUG'] = 'true'
        if args.log_level == 'WARNING':  # 如果没有明确指定日志级别，调试模式下使用DEBUG
            args.log_level = 'DEBUG'
    
    # 设置日志
    setup_logging(args.log_level, args.log_file)
    
    logger = logging.getLogger(__name__)
    logger.info(f"启动 AceFlow MCP Server - 模式: {args.mode}")
    
    try:
        if args.mode == 'stdio':
            # stdio模式 - 标准MCP服务器
            server = MCPStdioServer()
            import asyncio
            asyncio.run(server.run())
        elif args.mode == 'dev':
            # 开发模式 - 可以添加额外的开发工具
            logger.info("开发模式启动")
            server = MCPStdioServer()
            import asyncio
            asyncio.run(server.run())
        else:
            logger.error(f"不支持的模式: {args.mode}")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("收到键盘中断，正在关闭服务器...")
    except Exception as e:
        logger.error(f"服务器运行错误: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()