#!/usr/bin/env python3
"""使用标准 MCP SDK 的 AceFlow 服务器"""

import asyncio
import logging
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from typing import Any, Sequence

from .tools import AceFlowTools

# 创建服务器实例
server = Server("AceFlow")

# 创建工具实例
tools_instance = AceFlowTools()

@server.list_tools()
async def list_tools() -> list[Tool]:
    """列出可用工具"""
    return [
        Tool(
            name="aceflow_init",
            description="Initialize AceFlow project with specified mode",
            inputSchema={
                "type": "object",
                "properties": {
                    "mode": {
                        "type": "string",
                        "description": "Project mode (minimal, standard, complete, smart)"
                    },
                    "project_name": {
                        "type": "string",
                        "description": "Project name (optional)"
                    },
                    "directory": {
                        "type": "string", 
                        "description": "Project directory (optional)"
                    }
                },
                "required": ["mode"]
            }
        ),
        Tool(
            name="aceflow_stage",
            description="Manage project stages and workflow",
            inputSchema={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "description": "Action to perform (list, status, next, reset)"
                    },
                    "stage": {
                        "type": "string",
                        "description": "Stage name (optional)"
                    }
                },
                "required": ["action"]
            }
        ),
        Tool(
            name="aceflow_validate",
            description="Validate project compliance and quality",
            inputSchema={
                "type": "object",
                "properties": {
                    "mode": {
                        "type": "string",
                        "description": "Validation mode (basic, detailed)",
                        "default": "basic"
                    },
                    "fix": {
                        "type": "boolean",
                        "description": "Auto-fix issues",
                        "default": False
                    },
                    "report": {
                        "type": "boolean", 
                        "description": "Generate report",
                        "default": False
                    }
                }
            }
        ),
        Tool(
            name="aceflow_template",
            description="Manage workflow templates",
            inputSchema={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "description": "Action to perform (list, apply, validate)"
                    },
                    "template": {
                        "type": "string",
                        "description": "Template name (optional)"
                    }
                },
                "required": ["action"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> Sequence[TextContent]:
    """调用工具"""
    try:
        if name == "aceflow_init":
            result = tools_instance.aceflow_init(
                mode=arguments["mode"],
                project_name=arguments.get("project_name"),
                directory=arguments.get("directory")
            )
        elif name == "aceflow_stage":
            result = tools_instance.aceflow_stage(
                action=arguments["action"],
                stage=arguments.get("stage")
            )
        elif name == "aceflow_validate":
            result = tools_instance.aceflow_validate(
                mode=arguments.get("mode", "basic"),
                fix=arguments.get("fix", False),
                report=arguments.get("report", False)
            )
        elif name == "aceflow_template":
            result = tools_instance.aceflow_template(
                action=arguments["action"],
                template=arguments.get("template")
            )
        else:
            raise ValueError(f"Unknown tool: {name}")
        
        # 将结果转换为 JSON 字符串
        import json
        result_text = json.dumps(result, indent=2, ensure_ascii=False)
        
        return [TextContent(type="text", text=result_text)]
        
    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "tool": name,
            "arguments": arguments
        }
        import json
        error_text = json.dumps(error_result, indent=2, ensure_ascii=False)
        return [TextContent(type="text", text=error_text)]

async def run_server():
    """运行服务器"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

def main():
    """主函数"""
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_server())

if __name__ == "__main__":
    main()