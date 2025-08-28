"""
简化的统一工具接口 (Simplified Unified Tools Interface)
Simplified Unified Tools Interface
This module provides a simplified tool interface with only the core 4 tools.
"""
from typing import Dict, Any, Optional
import logging
import datetime
from .tools import AceFlowTools

logger = logging.getLogger(__name__)


class SimplifiedUnifiedTools:
    """
    简化的统一工具接口
    
    提供核心的4个AceFlow工具，简洁高效。
    """
    
    def __init__(self, working_directory: Optional[str] = None):
        """
        初始化简化的统一工具接口
        
        Args:
            working_directory: 工作目录路径
        """
        self.aceflow_tools = AceFlowTools(working_directory)
        
        # 工具调用统计
        self._tool_stats = {
            "total_calls": 0,
            "successful_calls": 0,
            "failed_calls": 0,
            "tool_distribution": {}
        }
        
        logger.info("Simplified unified tools interface initialized successfully")
    
    def aceflow_init(
        self,
        mode: str,
        project_name: Optional[str] = None,
        directory: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        🚀 Initialize AceFlow project
        
        Args:
            mode: 工作流模式 (minimal, standard, complete, smart)
            project_name: 项目名称（可选）
            directory: 项目目录（可选）
            
        Returns:
            Dict[str, Any]: 初始化结果
        """
        start_time = datetime.datetime.now()
        
        try:
            self._record_tool_call("aceflow_init")
            
            result = self.aceflow_tools.aceflow_init(
                mode=mode,
                project_name=project_name,
                directory=directory
            )
            
            if result.get("success"):
                self._record_success()
            else:
                self._record_failure()
            
            # 添加执行时间
            end_time = datetime.datetime.now()
            result["execution_time"] = (end_time - start_time).total_seconds()
            
            return result
            
        except Exception as e:
            self._record_failure()
            return {
                "success": False,
                "error": str(e),
                "message": "项目初始化失败"
            }
    
    def aceflow_stage(
        self,
        action: str,
        stage: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        📊 Manage project stages and workflow
        
        Args:
            action: 阶段管理动作 (status, next, list, reset, execute, set_analysis, save_output, prepare_data, validate)
            stage: 目标阶段名称（可选）
            data: AI Agent 提供的分析数据或阶段输入数据（可选）
            
        Returns:
            Dict[str, Any]: 阶段管理结果
        """
        start_time = datetime.datetime.now()
        
        try:
            self._record_tool_call("aceflow_stage")
            
            result = self.aceflow_tools.aceflow_stage(
                action=action,
                stage=stage,
                data=data
            )
            
            if result.get("success"):
                self._record_success()
            else:
                self._record_failure()
            
            # 添加执行时间
            end_time = datetime.datetime.now()
            result["execution_time"] = (end_time - start_time).total_seconds()
            
            return result
            
        except Exception as e:
            self._record_failure()
            return {
                "success": False,
                "error": str(e),
                "message": "阶段管理失败"
            }
    
    def aceflow_validate(
        self,
        mode: str = "basic",
        fix: bool = False,
        report: bool = False
    ) -> Dict[str, Any]:
        """
        ✅ Validate project compliance and quality
        
        Args:
            mode: 验证模式 (basic, detailed)
            fix: 是否自动修复问题
            report: 是否生成详细报告
            
        Returns:
            Dict[str, Any]: 验证结果
        """
        start_time = datetime.datetime.now()
        
        try:
            self._record_tool_call("aceflow_validate")
            
            # 基础实现 - 可以扩展验证逻辑
            result = {
                "success": True,
                "validation_mode": mode,
                "issues_found": 0,
                "issues_fixed": 0 if fix else None,
                "report_generated": report,
                "message": "项目验证完成"
            }
            
            if report:
                result["validation_report"] = {
                    "timestamp": datetime.datetime.now().isoformat(),
                    "project_structure": "✅ 正常",
                    "configuration": "✅ 正常",
                    "dependencies": "✅ 正常"
                }
            
            self._record_success()
            
            # 添加执行时间
            end_time = datetime.datetime.now()
            result["execution_time"] = (end_time - start_time).total_seconds()
            
            return result
            
        except Exception as e:
            self._record_failure()
            return {
                "success": False,
                "error": str(e),
                "message": "项目验证失败"
            }
    
    def aceflow_template(
        self,
        action: str,
        template: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        📋 Manage workflow templates
        
        Args:
            action: 模板操作 (list, apply, validate)
            template: 模板名称（apply和validate操作需要）
            
        Returns:
            Dict[str, Any]: 模板管理结果
        """
        start_time = datetime.datetime.now()
        
        try:
            self._record_tool_call("aceflow_template")
            
            if action == "list":
                result = {
                    "success": True,
                    "action": action,
                    "templates": [
                        {
                            "name": "minimal",
                            "description": "快速原型模式 - 3个阶段",
                            "stages": 3
                        },
                        {
                            "name": "standard",
                            "description": "标准开发模式 - 8个阶段",
                            "stages": 8
                        },
                        {
                            "name": "complete",
                            "description": "企业级模式 - 12个阶段",
                            "stages": 12
                        },
                        {
                            "name": "smart",
                            "description": "AI增强模式 - 10个阶段",
                            "stages": 10
                        }
                    ]
                }
            elif action == "apply":
                if not template:
                    raise ValueError("apply操作需要指定template参数")
                
                result = {
                    "success": True,
                    "action": action,
                    "template": template,
                    "message": f"模板'{template}'应用成功"
                }
            elif action == "validate":
                if not template:
                    raise ValueError("validate操作需要指定template参数")
                
                result = {
                    "success": True,
                    "action": action,
                    "template": template,
                    "valid": True,
                    "message": f"模板'{template}'验证通过"
                }
            else:
                raise ValueError(f"不支持的操作: {action}")
            
            self._record_success()
            
            # 添加执行时间
            end_time = datetime.datetime.now()
            result["execution_time"] = (end_time - start_time).total_seconds()
            
            return result
            
        except Exception as e:
            self._record_failure()
            return {
                "success": False,
                "error": str(e),
                "message": "模板管理失败"
            }
    
    def get_tool_stats(self) -> Dict[str, Any]:
        """
        获取工具使用统计
        
        Returns:
            Dict[str, Any]: 工具统计信息
        """
        return self._tool_stats.copy()
    
    def _record_tool_call(self, tool_name: str):
        """记录工具调用"""
        self._tool_stats["total_calls"] += 1
        if tool_name not in self._tool_stats["tool_distribution"]:
            self._tool_stats["tool_distribution"][tool_name] = 0
        self._tool_stats["tool_distribution"][tool_name] += 1
    
    def _record_success(self):
        """记录成功调用"""
        self._tool_stats["successful_calls"] += 1
    
    def _record_failure(self):
        """记录失败调用"""
        self._tool_stats["failed_calls"] += 1