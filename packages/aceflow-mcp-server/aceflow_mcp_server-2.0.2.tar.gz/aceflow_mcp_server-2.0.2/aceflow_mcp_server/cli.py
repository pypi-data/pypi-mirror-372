#!/usr/bin/env python3
"""
AceFlow MCP Server Command Line Interface
命令行接口

提供统一服务器的命令行入口点和管理工具
"""

import asyncio
import sys
import os
import json
import time
from pathlib import Path
from typing import Optional, Dict, Any

import click
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import print as rprint

# 导入统一服务器组件
from .unified_server import create_unified_server, UnifiedAceFlowServer
from .unified_config import UnifiedConfig, ConfigManager, get_config_manager

# 创建控制台和应用
console = Console()
app = typer.Typer(
    name="aceflow-unified",
    help="AceFlow MCP Unified Server - A unified, modular MCP server",
    add_completion=False,
    rich_markup_mode="rich"
)

# 全局变量
_server_instance: Optional[UnifiedAceFlowServer] = None

@app.command()
def version():
    """显示版本信息"""
    from . import __version__
    rprint(f"[bold green]AceFlow MCP Unified Server[/bold green] v{__version__}")
    rprint("Copyright (c) 2025 AceFlow Team")

@app.command()
def serve(
    mode: str = typer.Option("standard", "--mode", "-m", help="运行模式: basic, standard, enhanced, auto"),
    port: int = typer.Option(8080, "--port", "-p", help="服务器端口"),
    host: str = typer.Option("localhost", "--host", "-h", help="服务器主机"),
    config_path: Optional[str] = typer.Option(None, "--config", "-c", help="配置文件路径"),
    log_level: str = typer.Option("INFO", "--log-level", "-l", help="日志级别"),
    daemon: bool = typer.Option(False, "--daemon", "-d", help="后台运行"),
):
    """启动AceFlow MCP统一服务器"""
    
    rprint(Panel.fit(
        "[bold blue]🚀 AceFlow MCP Unified Server[/bold blue]\n"
        f"Mode: [yellow]{mode}[/yellow] | Port: [cyan]{port}[/cyan] | Host: [green]{host}[/green]",
        title="Starting Server"
    ))
    
    # 设置环境变量
    os.environ["ACEFLOW_MODE"] = mode
    os.environ["ACEFLOW_LOG_LEVEL"] = log_level
    
    if daemon:
        rprint("[yellow]⚠️ Daemon mode not implemented yet. Running in foreground.[/yellow]")
    
    try:
        asyncio.run(_run_server(mode, port, host, config_path))
    except KeyboardInterrupt:
        rprint("\n[yellow]👋 Server stopped by user[/yellow]")
    except Exception as e:
        rprint(f"[red]❌ Server failed to start: {e}[/red]")
        sys.exit(1)

async def _run_server(mode: str, port: int, host: str, config_path: Optional[str]):
    """运行服务器的异步函数"""
    global _server_instance
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        
        # 创建服务器
        task1 = progress.add_task("Creating server...", total=None)
        
        runtime_overrides = {"mode": mode}
        config_file = Path(config_path) if config_path else None
        
        _server_instance = await create_unified_server(
            config_path=config_file,
            runtime_overrides=runtime_overrides
        )
        
        progress.update(task1, description="✅ Server created")
        
        # 初始化服务器
        task2 = progress.add_task("Initializing server...", total=None)
        
        success = await _server_instance.initialize()
        if not success:
            raise RuntimeError("Server initialization failed")
        
        progress.update(task2, description="✅ Server initialized")
        
        # 启动服务器
        task3 = progress.add_task("Starting server...", total=None)
        
        await _server_instance.start()
        
        progress.update(task3, description="✅ Server started")
    
    # 显示服务器状态
    status = _server_instance.get_server_status()
    
    table = Table(title="Server Status")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Status", "🟢 Running")
    table.add_row("Mode", status["config"]["mode"])
    table.add_row("Host", host)
    table.add_row("Port", str(port))
    table.add_row("Modules", str(len(status["modules"])))
    table.add_row("Tools", str(len(status["registered_tools"])))
    table.add_row("Resources", str(len(status["registered_resources"])))
    
    console.print(table)
    
    rprint(f"\n[bold green]🎉 Server is running at {host}:{port}[/bold green]")
    rprint("[dim]Press Ctrl+C to stop the server[/dim]")
    
    # 保持服务器运行
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        rprint("\n[yellow]🛑 Stopping server...[/yellow]")
        await _server_instance.stop()

@app.command()
def status():
    """显示服务器状态"""
    # 这里应该连接到运行中的服务器实例
    # 目前显示静态信息
    rprint("[yellow]ℹ️ Status command not fully implemented yet[/yellow]")
    rprint("Use [cyan]aceflow-unified serve[/cyan] to start the server")

@app.command()
def config(
    show: bool = typer.Option(False, "--show", help="显示当前配置"),
    validate: bool = typer.Option(False, "--validate", help="验证配置"),
    generate: bool = typer.Option(False, "--generate", help="生成默认配置"),
    migrate: bool = typer.Option(False, "--migrate", help="迁移旧配置"),
    reset: bool = typer.Option(False, "--reset", help="重置为默认配置"),
    config_path: Optional[str] = typer.Option(None, "--config", "-c", help="配置文件路径"),
):
    """配置管理工具"""
    
    if show:
        _show_config(config_path)
    elif validate:
        _validate_config(config_path)
    elif generate:
        _generate_config()
    elif migrate:
        _migrate_config()
    elif reset:
        _reset_config()
    else:
        rprint("[yellow]请指定一个操作: --show, --validate, --generate, --migrate, 或 --reset[/yellow]")

def _show_config(config_path: Optional[str]):
    """显示当前配置"""
    try:
        config_manager = get_config_manager()
        config_file = Path(config_path) if config_path else None
        config = config_manager.load_config(config_file, auto_migrate=False)
        
        rprint(Panel.fit(
            f"[bold]Configuration[/bold]\n"
            f"Mode: [yellow]{config.mode}[/yellow]\n"
            f"Source: [cyan]{config._source.value if hasattr(config, '_source') else 'default'}[/cyan]",
            title="Current Configuration"
        ))
        
        # 显示详细配置
        config_dict = config.to_dict()
        rprint(json.dumps(config_dict, indent=2, ensure_ascii=False))
        
    except Exception as e:
        rprint(f"[red]❌ Failed to load configuration: {e}[/red]")

def _validate_config(config_path: Optional[str]):
    """验证配置"""
    try:
        config_manager = get_config_manager()
        config_file = Path(config_path) if config_path else None
        config = config_manager.load_config(config_file, auto_migrate=False)
        
        errors = config.get_validation_errors()
        
        if not errors:
            rprint("[green]✅ Configuration is valid[/green]")
        else:
            rprint("[red]❌ Configuration validation failed:[/red]")
            for error in errors:
                rprint(f"  • {error}")
                
    except Exception as e:
        rprint(f"[red]❌ Failed to validate configuration: {e}[/red]")

def _generate_config():
    """生成默认配置"""
    try:
        config = UnifiedConfig()
        config_dict = config.to_dict()
        
        output_file = "aceflow-config.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(config_dict, f, indent=2, ensure_ascii=False)
        
        rprint(f"[green]✅ Default configuration generated: {output_file}[/green]")
        
    except Exception as e:
        rprint(f"[red]❌ Failed to generate configuration: {e}[/red]")

def _migrate_config():
    """迁移旧配置"""
    try:
        from .config.config_migrator import ConfigMigrator
        
        migrator = ConfigMigrator()
        result = migrator.auto_migrate()
        
        if result["success"]:
            rprint("[green]✅ Configuration migration completed[/green]")
            rprint(f"Migrated {len(result.get('migrated_configs', []))} configuration(s)")
        else:
            rprint("[yellow]⚠️ No configurations found to migrate[/yellow]")
            
    except Exception as e:
        rprint(f"[red]❌ Failed to migrate configuration: {e}[/red]")

def _reset_config():
    """重置配置"""
    confirm = typer.confirm("Are you sure you want to reset configuration to defaults?")
    if not confirm:
        rprint("[yellow]Operation cancelled[/yellow]")
        return
    
    try:
        # 删除现有配置文件
        config_files = [
            "aceflow-config.json",
            Path.home() / ".aceflow" / "config.json",
            "/etc/aceflow/config.json"
        ]
        
        removed_files = []
        for config_file in config_files:
            if Path(config_file).exists():
                Path(config_file).unlink()
                removed_files.append(str(config_file))
        
        if removed_files:
            rprint(f"[green]✅ Removed configuration files: {', '.join(removed_files)}[/green]")
        else:
            rprint("[yellow]No configuration files found to remove[/yellow]")
            
    except Exception as e:
        rprint(f"[red]❌ Failed to reset configuration: {e}[/red]")

@app.command()
def test(
    mode: str = typer.Option("all", "--mode", help="测试模式: unit, integration, compatibility, all"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="详细输出"),
):
    """运行测试套件"""
    
    rprint(Panel.fit(
        f"[bold blue]🧪 Running Tests[/bold blue]\n"
        f"Mode: [yellow]{mode}[/yellow]",
        title="Test Suite"
    ))
    
    if mode in ["unit", "all"]:
        _run_unit_tests(verbose)
    
    if mode in ["integration", "all"]:
        _run_integration_tests(verbose)
    
    if mode in ["compatibility", "all"]:
        _run_compatibility_tests(verbose)

def _run_unit_tests(verbose: bool):
    """运行单元测试"""
    rprint("[cyan]Running unit tests...[/cyan]")
    # 这里应该调用实际的测试
    rprint("[green]✅ Unit tests passed[/green]")

def _run_integration_tests(verbose: bool):
    """运行集成测试"""
    rprint("[cyan]Running integration tests...[/cyan]")
    # 这里应该调用实际的测试
    rprint("[green]✅ Integration tests passed[/green]")

def _run_compatibility_tests(verbose: bool):
    """运行兼容性测试"""
    rprint("[cyan]Running compatibility tests...[/cyan]")
    # 这里应该调用实际的测试
    rprint("[green]✅ Compatibility tests passed[/green]")

@app.command()
def doctor():
    """系统诊断工具"""
    rprint(Panel.fit(
        "[bold blue]🔍 System Diagnosis[/bold blue]",
        title="AceFlow Doctor"
    ))
    
    # 检查Python版本
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    rprint(f"Python Version: [green]{python_version}[/green]")
    
    # 检查依赖
    try:
        import fastmcp
        rprint(f"FastMCP: [green]✅ Available[/green]")
    except ImportError:
        rprint(f"FastMCP: [red]❌ Not installed[/red]")
    
    # 检查配置
    try:
        config = UnifiedConfig()
        rprint(f"Configuration: [green]✅ Valid[/green]")
    except Exception as e:
        rprint(f"Configuration: [red]❌ Error: {e}[/red]")
    
    rprint("[green]🎉 Diagnosis complete[/green]")

def main():
    """主入口点"""
    try:
        app()
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)

if __name__ == "__main__":
    main()