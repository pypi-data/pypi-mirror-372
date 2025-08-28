"""
统一 AceFlow MCP 服务器
Unified AceFlow MCP Server

This module implements the unified server entry point that integrates
all functional modules and provides a single MCP server interface.
"""

from typing import Dict, Any, Optional, List
import logging
import asyncio
from pathlib import Path

# FastMCP imports
from fastmcp import FastMCP

# Internal imports
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from unified_config import UnifiedConfig, ConfigManager, get_config_manager
from .modules import BaseModule, ModuleManager

logger = logging.getLogger(__name__)


class UnifiedAceFlowServer:
    """
    统一的 AceFlow MCP 服务器
    
    这是整个系统的主入口点，负责：
    - 配置管理和加载
    - 模块生命周期管理
    - MCP 协议处理
    - 工具和资源注册
    - 服务器生命周期管理
    """
    
    def __init__(self, config: Optional[UnifiedConfig] = None):
        """
        初始化统一服务器
        
        Args:
            config: 统一配置对象，如果为None则自动加载
        """
        # 配置管理
        self.config_manager = get_config_manager()
        if config:
            self.config_manager._config = config
        self.config = self.config_manager.get_config()
        
        # MCP 服务器实例
        self.mcp = FastMCP("AceFlow-Unified")
        
        # 模块管理
        self.module_manager = ModuleManager()
        
        # 服务器状态
        self._initialized = False
        self._running = False
        
        # 注册的工具和资源
        self._registered_tools: Dict[str, Any] = {}
        self._registered_resources: Dict[str, Any] = {}
        
        logger.info("Unified AceFlow Server created")
    
    async def initialize(self) -> bool:
        """
        初始化服务器
        
        Returns:
            初始化是否成功
        """
        if self._initialized:
            logger.debug("Server already initialized")
            return True
        
        logger.info("Initializing Unified AceFlow Server...")
        
        try:
            # 1. 注册核心模块
            await self._register_core_modules()
            
            # 2. 根据配置注册可选模块
            await self._register_optional_modules()
            
            # 3. 初始化所有模块
            success = self.module_manager.initialize_all_modules()
            if not success:
                logger.error("Failed to initialize all modules")
                return False
            
            # 4. 注册 MCP 工具和资源
            await self._register_mcp_interfaces()
            
            self._initialized = True
            logger.info("Unified AceFlow Server initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Server initialization failed: {e}")
            return False
    
    async def start(self) -> bool:
        """
        启动服务器
        
        Returns:
            启动是否成功
        """
        if not self._initialized:
            success = await self.initialize()
            if not success:
                return False
        
        if self._running:
            logger.debug("Server already running")
            return True
        
        logger.info("Starting Unified AceFlow Server...")
        
        try:
            # 启动 MCP 服务器
            # 注意：FastMCP 的启动方式可能需要根据实际API调整
            self._running = True
            logger.info("Unified AceFlow Server started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Server start failed: {e}")
            return False
    
    async def stop(self):
        """停止服务器"""
        if not self._running:
            logger.debug("Server not running")
            return
        
        logger.info("Stopping Unified AceFlow Server...")
        
        try:
            # 关闭所有模块
            self.module_manager.shutdown_all_modules()
            
            # 停止 MCP 服务器
            self._running = False
            
            logger.info("Unified AceFlow Server stopped successfully")
            
        except Exception as e:
            logger.error(f"Server stop error: {e}")
    
    async def _register_core_modules(self):
        """注册核心模块"""
        logger.debug("Registering core modules...")
        
        # 导入并注册核心模块
        from modules.core_module import CoreModule
        self.module_manager.register_module_class(
            "core", CoreModule, self.config.core
        )
        
        logger.debug("Core modules registered")
    
    async def _register_optional_modules(self):
        """根据配置注册可选模块"""
        logger.debug("Registering optional modules...")
        
        # 协作模块
        if self.config.collaboration.enabled:
            logger.debug("Registering collaboration module...")
            try:
                from modules.collaboration_module import CollaborationModule
                self.module_manager.register_module_class(
                    "collaboration", CollaborationModule, self.config.collaboration
                )
                logger.debug("Collaboration module registered successfully")
            except ImportError as e:
                logger.warning(f"Failed to import collaboration module: {e}")
        
        # 智能模块
        if self.config.intelligence.enabled:
            logger.debug("Registering intelligence module...")
            try:
                from modules.intelligence_module import IntelligenceModule
                self.module_manager.register_module_class(
                    "intelligence", IntelligenceModule, self.config.intelligence
                )
                logger.debug("Intelligence module registered successfully")
            except ImportError as e:
                logger.warning(f"Failed to import intelligence module: {e}")
        
        # 监控模块
        if self.config.monitoring.enabled:
            logger.debug("Registering monitoring module...")
            try:
                # 监控模块可能不存在，所以我们跳过它
                logger.debug("Monitoring module skipped (not implemented yet)")
            except ImportError as e:
                logger.warning(f"Failed to import monitoring module: {e}")
        
        logger.debug("Optional modules registered")
    
    async def _register_mcp_interfaces(self):
        """注册 MCP 工具和资源"""
        logger.debug("Registering MCP interfaces...")
        
        # 注册统一工具
        await self._register_unified_tools()
        
        # 注册专用工具
        await self._register_specialized_tools()
        
        # 注册资源
        await self._register_resources()
        
        logger.debug("MCP interfaces registered")
    
    async def _register_unified_tools(self):
        """注册统一工具"""
        # 这些是所有模式都提供的核心工具
        
        @self.mcp.tool
        async def aceflow_init(
            mode: str,
            project_name: Optional[str] = None,
            directory: Optional[str] = None,
            # 新增统一配置参数
            collaboration_enabled: Optional[bool] = None,
            intelligence_enabled: Optional[bool] = None
        ) -> Dict[str, Any]:
            """🚀 Initialize AceFlow project with unified configuration."""
            # 实现统一的初始化逻辑
            return await self._execute_unified_tool(
                "aceflow_init",
                {
                    "mode": mode,
                    "project_name": project_name,
                    "directory": directory,
                    "collaboration_enabled": collaboration_enabled,
                    "intelligence_enabled": intelligence_enabled
                }
            )
        
        @self.mcp.tool
        async def aceflow_stage(
            action: str,
            stage: Optional[str] = None,
            # 协作参数
            user_input: Optional[str] = None,
            auto_confirm: Optional[bool] = None,
            collaboration_mode: Optional[str] = None
        ) -> Dict[str, Any]:
            """📊 Unified stage management with optional collaboration."""
            return await self._execute_unified_tool(
                "aceflow_stage",
                {
                    "action": action,
                    "stage": stage,
                    "user_input": user_input,
                    "auto_confirm": auto_confirm,
                    "collaboration_mode": collaboration_mode
                }
            )
        
        @self.mcp.tool
        async def aceflow_validate(
            mode: str = "basic",
            fix: bool = False,
            report: bool = False,
            # 智能验证参数
            validation_level: Optional[str] = None,
            generate_report: Optional[bool] = None
        ) -> Dict[str, Any]:
            """✅ Unified project validation with enhanced quality checks."""
            return await self._execute_unified_tool(
                "aceflow_validate",
                {
                    "mode": mode,
                    "fix": fix,
                    "report": report,
                    "validation_level": validation_level,
                    "generate_report": generate_report
                }
            )
        
        self._registered_tools.update({
            "aceflow_init": aceflow_init,
            "aceflow_stage": aceflow_stage,
            "aceflow_validate": aceflow_validate
        })
    
    async def _register_specialized_tools(self):
        """注册专用工具"""
        # 协作专用工具
        if self.config.collaboration.enabled:
            @self.mcp.tool
            async def aceflow_respond(
                request_id: str,
                response: str,
                user_id: str = "user"
            ) -> Dict[str, Any]:
                """💬 Respond to collaboration requests."""
                return await self._execute_module_tool(
                    "collaboration", "aceflow_respond",
                    {"request_id": request_id, "response": response, "user_id": user_id}
                )
            
            @self.mcp.tool
            async def aceflow_collaboration_status(
                project_id: Optional[str] = None
            ) -> Dict[str, Any]:
                """📊 Get collaboration status and insights."""
                return await self._execute_module_tool(
                    "collaboration", "aceflow_collaboration_status",
                    {"project_id": project_id}
                )
            
            @self.mcp.tool
            async def aceflow_task_execute(
                task_id: Optional[str] = None,
                auto_confirm: bool = False
            ) -> Dict[str, Any]:
                """📋 Execute tasks with collaborative confirmation."""
                return await self._execute_module_tool(
                    "collaboration", "aceflow_task_execute",
                    {"task_id": task_id, "auto_confirm": auto_confirm}
                )
            
            self._registered_tools.update({
                "aceflow_respond": aceflow_respond,
                "aceflow_collaboration_status": aceflow_collaboration_status,
                "aceflow_task_execute": aceflow_task_execute
            })
        
        # 智能专用工具
        if self.config.intelligence.enabled:
            @self.mcp.tool
            async def aceflow_intent_analyze(
                user_input: str,
                context: Optional[Dict[str, Any]] = None
            ) -> Dict[str, Any]:
                """🧠 Analyze user intent and suggest actions."""
                return await self._execute_module_tool(
                    "intelligence", "aceflow_intent_analyze",
                    {"user_input": user_input, "context": context}
                )
            
            @self.mcp.tool
            async def aceflow_recommend(
                context: Optional[Dict[str, Any]] = None
            ) -> Dict[str, Any]:
                """💡 Get intelligent recommendations for next actions."""
                return await self._execute_module_tool(
                    "intelligence", "aceflow_recommend",
                    {"context": context}
                )
            
            self._registered_tools.update({
                "aceflow_intent_analyze": aceflow_intent_analyze,
                "aceflow_recommend": aceflow_recommend
            })
    
    async def _register_resources(self):
        """注册资源"""
        # 核心资源
        @self.mcp.resource("aceflow://project/state/{project_id}")
        async def project_state(project_id: str = "current") -> str:
            """Get current project state."""
            return await self._get_resource("project_state", {"project_id": project_id})
        
        @self.mcp.resource("aceflow://workflow/config/{config_id}")
        async def workflow_config(config_id: str = "default") -> str:
            """Get workflow configuration."""
            return await self._get_resource("workflow_config", {"config_id": config_id})
        
        @self.mcp.resource("aceflow://stage/guide/{stage}")
        async def stage_guide(stage: str) -> str:
            """Get stage-specific guidance."""
            return await self._get_resource("stage_guide", {"stage": stage})
        
        self._registered_resources.update({
            "project_state": project_state,
            "workflow_config": workflow_config,
            "stage_guide": stage_guide
        })
        
        # 增强资源
        if self.config.intelligence.enabled:
            @self.mcp.resource("aceflow://project/intelligent-state/{project_id}")
            async def intelligent_project_state(project_id: str = "current") -> str:
                """Get intelligent project state with recommendations."""
                return await self._get_resource("intelligent_project_state", {"project_id": project_id})
            
            self._registered_resources["intelligent_project_state"] = intelligent_project_state
        
        if self.config.collaboration.enabled:
            @self.mcp.resource("aceflow://collaboration/insights/{project_id}")
            async def collaboration_insights(project_id: str = "current") -> str:
                """Get collaboration insights and analytics."""
                return await self._get_resource("collaboration_insights", {"project_id": project_id})
            
            self._registered_resources["collaboration_insights"] = collaboration_insights
        
        if self.config.monitoring.enabled:
            @self.mcp.resource("aceflow://monitoring/usage-stats")
            async def usage_stats() -> str:
                """Get usage statistics and recommendations."""
                return await self._get_resource("usage_stats", {})
            
            self._registered_resources["usage_stats"] = usage_stats
    
    async def _execute_unified_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """执行统一工具"""
        try:
            # 获取核心模块
            core_module = self.module_manager.get_module("core")
            if not core_module or not core_module.is_available():
                return {
                    "success": False,
                    "error": "Core module not available",
                    "tool": tool_name
                }
            
            # 根据工具名称调用相应的方法
            if tool_name == "aceflow_init":
                return core_module.aceflow_init(**params)
            elif tool_name == "aceflow_stage":
                return core_module.aceflow_stage(**params)
            elif tool_name == "aceflow_validate":
                return core_module.aceflow_validate(**params)
            else:
                return {
                    "success": False,
                    "error": f"Unknown unified tool: {tool_name}",
                    "tool": tool_name
                }
                
        except Exception as e:
            logger.error(f"Unified tool execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "tool": tool_name,
                "message": "Tool execution failed"
            }
    
    async def _execute_module_tool(self, module_name: str, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """执行模块专用工具"""
        module = self.module_manager.get_module(module_name)
        if not module or not module.is_available():
            return {
                "success": False,
                "error": f"Module '{module_name}' not available",
                "tool": tool_name
            }
        
        # 这里会调用模块的具体方法
        # 暂时返回占位符响应
        return {
            "success": True,
            "message": f"Module tool '{tool_name}' executed",
            "module": module_name,
            "params": params
        }
    
    async def _get_resource(self, resource_name: str, params: Dict[str, Any]) -> str:
        """获取资源"""
        # 这里会实现资源获取逻辑
        # 暂时返回占位符响应
        return f"Resource '{resource_name}' with params: {params}"
    
    # 状态和监控方法
    
    def get_server_status(self) -> Dict[str, Any]:
        """获取服务器状态"""
        return {
            "initialized": self._initialized,
            "running": self._running,
            "config": self.config_manager.get_config_summary(),
            "modules": self.module_manager.get_all_modules_status(),
            "registered_tools": list(self._registered_tools.keys()),
            "registered_resources": list(self._registered_resources.keys())
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """获取健康状态"""
        module_health = self.module_manager.health_check()
        
        return {
            "server_healthy": self._initialized and self._running,
            "modules_healthy": module_health["overall_healthy"],
            "server_status": {
                "initialized": self._initialized,
                "running": self._running
            },
            "module_status": module_health,
            "timestamp": module_health["timestamp"]
        }
    
    def reload_config(self) -> bool:
        """重新加载配置"""
        try:
            old_config = self.config
            new_config = self.config_manager.reload_config()
            
            # 检查配置变化
            if old_config.mode != new_config.mode:
                logger.info(f"Server mode changed from {old_config.mode} to {new_config.mode}")
                # 这里可以实现模式切换逻辑
            
            if old_config.collaboration.enabled != new_config.collaboration.enabled:
                logger.info(f"Collaboration module enabled changed to {new_config.collaboration.enabled}")
                # 这里可以实现模块启用/禁用逻辑
            
            if old_config.intelligence.enabled != new_config.intelligence.enabled:
                logger.info(f"Intelligence module enabled changed to {new_config.intelligence.enabled}")
                # 这里可以实现模块启用/禁用逻辑
            
            self.config = new_config
            logger.info("Configuration reloaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to reload configuration: {e}")
            return False
    
    def get_mcp_server(self) -> FastMCP:
        """获取 MCP 服务器实例"""
        return self.mcp
    
    def __repr__(self) -> str:
        return f"UnifiedAceFlowServer(initialized={self._initialized}, running={self._running}, mode={self.config.mode})"


# 便捷函数

async def create_unified_server(
    config_path: Optional[Path] = None,
    runtime_overrides: Optional[Dict[str, Any]] = None
) -> UnifiedAceFlowServer:
    """
    创建统一服务器实例
    
    Args:
        config_path: 配置文件路径
        runtime_overrides: 运行时配置覆盖
        
    Returns:
        统一服务器实例
    """
    # 加载配置
    config_manager = get_config_manager()
    config = config_manager.load_config(config_path, runtime_overrides)
    
    # 创建服务器
    server = UnifiedAceFlowServer(config)
    
    return server


async def run_unified_server(
    config_path: Optional[Path] = None,
    runtime_overrides: Optional[Dict[str, Any]] = None
) -> UnifiedAceFlowServer:
    """
    运行统一服务器
    
    Args:
        config_path: 配置文件路径
        runtime_overrides: 运行时配置覆盖
        
    Returns:
        运行中的统一服务器实例
    """
    server = await create_unified_server(config_path, runtime_overrides)
    
    success = await server.start()
    if not success:
        raise RuntimeError("Failed to start unified server")
    
    return server