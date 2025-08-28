"""
AceFlow MCP Server - Simplified
Simplified MCP Server for AI-driven software development workflows
"""

__version__ = "1.0.8"
__author__ = "AceFlow Team"
__description__ = "Simplified MCP Server with 4 core tools for AI-driven workflows"

# Core tools export
from .tools import AceFlowTools
from .unified_tools import SimplifiedUnifiedTools

# MCP Server (optional, may fail if dependencies missing)
try:
    from .mcp_stdio_server import MCPStdioServer
    MCP_AVAILABLE = True
except ImportError:
    MCPStdioServer = None
    MCP_AVAILABLE = False

__all__ = [
    "AceFlowTools",
    "SimplifiedUnifiedTools", 
    "MCPStdioServer",
    "MCP_AVAILABLE",
    "__version__"
]