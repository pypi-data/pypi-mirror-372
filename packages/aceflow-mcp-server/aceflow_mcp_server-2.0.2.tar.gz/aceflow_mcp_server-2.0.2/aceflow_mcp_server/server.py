"""AceFlow MCP Server implementation using FastMCP framework."""

import click
from fastmcp import FastMCP
from typing import Dict, Any, Optional

# Create global FastMCP instance
mcp = FastMCP("AceFlow")

# Initialize components (import after mcp creation to avoid circular imports)
def get_tools():
    from .tools import AceFlowTools
    return AceFlowTools()

def get_resources():
    from .resources import AceFlowResources
    return AceFlowResources()

def get_prompts():
    from .prompts import AceFlowPrompts
    return AceFlowPrompts()

# Register tools with decorators
@mcp.tool
def aceflow_init(
    mode: str,
    project_name: Optional[str] = None,
    directory: Optional[str] = None
) -> Dict[str, Any]:
    """🚀 Initialize and create a new AceFlow project with AI-driven workflow management.
    
    This tool sets up a complete AceFlow project structure with configuration files,
    workflow templates, and development guidelines. Perfect for starting new software
    projects with structured development processes.
    
    Use this tool when users want to:
    - Initialize a new project / 初始化新项目 / 创建项目
    - Set up AceFlow workflow / 设置工作流 / 配置开发流程  
    - Create project structure / 创建项目结构 / 搭建项目框架
    - Start a new development project / 开始新的开发项目
    - Bootstrap project with templates / 使用模板引导项目
    
    Parameters:
    - mode: Project complexity ('minimal', 'standard', 'complete', 'smart')
    - project_name: Optional custom project name
    - directory: Optional target directory (defaults to current)
    
    Examples:
    - "Initialize AceFlow project" → aceflow_init(mode="standard")
    - "Create minimal project setup" → aceflow_init(mode="minimal")
    - "Set up complete workflow" → aceflow_init(mode="complete")
    """
    tools = get_tools()
    return tools.aceflow_init(mode, project_name, directory)

@mcp.tool
def aceflow_stage(
    action: str,
    stage: Optional[str] = None
) -> Dict[str, Any]:
    """📊 Manage project development stages and workflow progression.
    
    This tool controls the project's development lifecycle, allowing you to check
    current status, advance to next stages, list available stages, or reset progress.
    Essential for tracking and managing development workflow.
    
    Use this tool when users want to:
    - Check project status / 检查项目状态 / 查看进度
    - Move to next stage / 进入下一阶段 / 推进流程
    - List all stages / 列出所有阶段 / 查看工作流
    - Reset project progress / 重置项目进度 / 重新开始
    - Get current workflow state / 获取当前工作流状态
    
    Parameters:
    - action: 'status', 'next', 'list', 'reset'
    - stage: Optional specific stage name for targeted operations
    
    Examples:
    - "What's the current status?" → aceflow_stage(action="status")
    - "Move to next stage" → aceflow_stage(action="next")
    - "Show all workflow stages" → aceflow_stage(action="list")
    """
    tools = get_tools()
    return tools.aceflow_stage(action, stage)

@mcp.tool
def aceflow_validate(
    mode: str = "basic",
    fix: bool = False,
    report: bool = False
) -> Dict[str, Any]:
    """✅ Validate project compliance, quality, and AceFlow standards.
    
    This tool performs comprehensive project validation, checking code quality,
    structure compliance, and AceFlow workflow adherence. Can automatically
    fix issues and generate detailed reports.
    
    Use this tool when users want to:
    - Check project quality / 检查项目质量 / 验证代码
    - Validate compliance / 验证合规性 / 检查标准
    - Fix project issues / 修复项目问题 / 自动修复
    - Generate quality report / 生成质量报告 / 创建报告
    - Ensure best practices / 确保最佳实践 / 质量保证
    
    Parameters:
    - mode: Validation depth ('basic', 'detailed')
    - fix: Whether to automatically fix found issues
    - report: Whether to generate detailed validation report
    
    Examples:
    - "Validate my project" → aceflow_validate(mode="basic")
    - "Check and fix issues" → aceflow_validate(mode="detailed", fix=True)
    - "Generate quality report" → aceflow_validate(report=True)
    """
    tools = get_tools()
    return tools.aceflow_validate(mode, fix, report)

@mcp.tool
def aceflow_template(
    action: str,
    template: Optional[str] = None
) -> Dict[str, Any]:
    """📋 Manage and apply AceFlow workflow templates.
    
    This tool handles workflow templates, allowing you to list available templates,
    apply specific templates to projects, or validate current template usage.
    Templates provide pre-configured workflows for different project types.
    
    Use this tool when users want to:
    - List available templates / 列出可用模板 / 查看模板
    - Apply workflow template / 应用工作流模板 / 使用模板
    - Change project template / 更改项目模板 / 切换模板
    - Validate template usage / 验证模板使用 / 检查模板
    - Get template information / 获取模板信息 / 了解模板
    
    Parameters:
    - action: 'list', 'apply', 'validate'
    - template: Template name when applying ('minimal', 'standard', 'complete', 'smart')
    
    Examples:
    - "Show available templates" → aceflow_template(action="list")
    - "Apply standard template" → aceflow_template(action="apply", template="standard")
    - "Validate current template" → aceflow_template(action="validate")
    """
    tools = get_tools()
    return tools.aceflow_template(action, template)

# Register resources with decorators
@mcp.resource("aceflow://project/state/{project_id}")
def project_state(project_id: str = "current") -> str:
    """Get current project state."""
    resources = get_resources()
    return resources.project_state(project_id)

@mcp.resource("aceflow://workflow/config/{config_id}")
def workflow_config(config_id: str = "default") -> str:
    """Get workflow configuration."""
    resources = get_resources()
    return resources.workflow_config(config_id)

@mcp.resource("aceflow://stage/guide/{stage}")
def stage_guide(stage: str) -> str:
    """Get stage-specific guidance."""
    resources = get_resources()
    return resources.stage_guide(stage)

# Register prompts with decorators
@mcp.prompt
def workflow_assistant(
    task: Optional[str] = None,
    context: Optional[str] = None
) -> str:
    """Generate workflow assistance prompt."""
    prompts = get_prompts()
    return prompts.workflow_assistant(task, context)

@mcp.prompt
def stage_guide_prompt(stage: str) -> str:
    """Generate stage-specific guidance prompt."""
    prompts = get_prompts()
    return prompts.stage_guide(stage)


class AceFlowMCPServer:
    """Main AceFlow MCP Server class."""
    
    def __init__(self):
        """Initialize the MCP server."""
        self.mcp = mcp
    
    def run(self, host: str = "localhost", port: int = 8000, log_level: str = "INFO"):
        """Start the MCP server."""
        self.mcp.run(host=host, port=port, log_level=log_level)


@click.command()
@click.option('--host', default=None, help='Host to bind to (for HTTP mode)')
@click.option('--port', default=None, type=int, help='Port to bind to (for HTTP mode)')
@click.option('--transport', default='stdio', help='Transport mode: stdio, sse, or streamable-http')
@click.option('--log-level', default='INFO', help='Log level')
@click.version_option(version="1.1.0")
def main(host: str, port: int, transport: str, log_level: str):
    """Start AceFlow MCP Server."""
    import os
    import logging
    
    # Set up logging
    logging.basicConfig(level=getattr(logging, log_level.upper()))
    
    # For stdio mode, run directly with FastMCP
    if transport == 'stdio':
        mcp.run(transport='stdio')
    else:
        # For HTTP modes, use host and port
        if host and port:
            mcp.run(transport=transport, host=host, port=port)
        else:
            mcp.run(transport=transport)


if __name__ == "__main__":
    main()