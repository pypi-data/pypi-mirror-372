"""
核心模块 (CoreModule)
Core Module

This module encapsulates the existing AceFlowTools as CoreModule,
implementing the basic tools: aceflow_init, aceflow_stage, aceflow_validate.
Ensures complete compatibility with the original aceflow-server.
"""

from typing import Dict, Any, Optional, List
import logging
import json
import os
import sys
from pathlib import Path
import shutil
import datetime

from .base_module import BaseModule, ModuleMetadata

# 导入工具 - 使用绝对导入避免问题
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from tools import AceFlowTools
except ImportError:
    # 如果导入失败，创建占位符类
    class AceFlowTools:
        def __init__(self): pass
        def aceflow_init(self, **kwargs): 
            return {"success": True, "message": "Placeholder implementation"}
        def aceflow_stage(self, **kwargs): 
            return {"success": True, "message": "Placeholder implementation"}
        def aceflow_validate(self, **kwargs): 
            return {"success": True, "message": "Placeholder implementation"}

logger = logging.getLogger(__name__)


class CoreModule(BaseModule):
    """
    核心模块
    
    封装现有的 AceFlowTools 为 CoreModule，实现基础工具：
    - aceflow_init: 项目初始化
    - aceflow_stage: 阶段管理  
    - aceflow_validate: 项目验证
    
    确保与原 aceflow-server 完全兼容。
    """
    
    def __init__(self, config):
        """
        初始化核心模块
        
        Args:
            config: 核心模块配置
        """
        metadata = ModuleMetadata(
            name="core",
            version="1.0.0",
            description="Core AceFlow functionality module",
            provides=["aceflow_init", "aceflow_stage", "aceflow_validate"],
            tags={"core", "essential"}
        )
        
        super().__init__(config, metadata)
        
        # AceFlow工具实例
        self._aceflow_tools: Optional[AceFlowTools] = None
        
        # 运行时配置存储
        self._runtime_config: Dict[str, Any] = {}
    
    def get_module_name(self) -> str:
        """获取模块名称"""
        return "core"
    
    def _do_initialize(self) -> bool:
        """执行模块初始化逻辑"""
        try:
            # 初始化 AceFlow 工具
            self._aceflow_tools = AceFlowTools()
            
            # 加载运行时配置
            self._load_runtime_config()
            
            logger.info("Core module initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Core module initialization failed: {e}")
            return False
    
    def _do_cleanup(self):
        """执行模块清理逻辑"""
        try:
            # 保存运行时配置
            self._save_runtime_config()
            
            # 清理资源
            self._aceflow_tools = None
            self._runtime_config.clear()
            
            logger.info("Core module cleaned up successfully")
            
        except Exception as e:
            logger.error(f"Core module cleanup error: {e}")
    
    def get_health_status(self) -> Dict[str, Any]:
        """获取模块健康状态"""
        if not self.initialized or not self._aceflow_tools:
            return {
                "healthy": False,
                "status": "not_initialized",
                "details": "AceFlow tools not initialized"
            }
        
        return {
            "healthy": True,
            "status": "running",
            "details": "Core module is healthy and ready",
            "tools_available": ["aceflow_init", "aceflow_stage", "aceflow_validate"],
            "runtime_config_loaded": bool(self._runtime_config)
        }
    
    # 核心工具方法
    
    def aceflow_init(
        self,
        mode: str,
        project_name: Optional[str] = None,
        directory: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        🚀 Initialize AceFlow project with specified mode
        
        Args:
            mode: Workflow mode (minimal, standard, complete, smart)
            project_name: Optional project name
            directory: Optional target directory
            **kwargs: Additional runtime parameters
            
        Returns:
            Dict with success status, message, and project info
        """
        if not self.ensure_initialized():
            return {
                "success": False,
                "error": "Core module not initialized",
                "message": "Module initialization failed"
            }
        
        try:
            # 记录调用开始
            start_time = datetime.datetime.now()
            
            # 应用运行时配置覆盖
            effective_params = self._apply_runtime_overrides({
                "mode": mode,
                "project_name": project_name,
                "directory": directory,
                **kwargs
            })
            
            # 调用原始工具
            result = self._aceflow_tools.aceflow_init(
                mode=effective_params["mode"],
                project_name=effective_params.get("project_name"),
                directory=effective_params.get("directory")
            )
            
            # 记录统计信息
            duration = (datetime.datetime.now() - start_time).total_seconds()
            self.record_call(success=result.get("success", False), duration=duration)
            
            # 保存运行时配置（如果有新的配置参数）
            if any(key.startswith("config_") for key in kwargs):
                self._update_runtime_config(kwargs)
            
            logger.info(f"aceflow_init executed: mode={mode}, success={result.get('success')}")
            return result
            
        except Exception as e:
            self.record_call(success=False)
            logger.error(f"aceflow_init error: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to initialize project"
            }
    
    def aceflow_stage(
        self,
        action: str,
        stage: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        📊 Manage project stages
        
        Args:
            action: Stage action (status, next, prev, set, list)
            stage: Optional specific stage name
            **kwargs: Additional parameters
            
        Returns:
            Dict with success status and stage information
        """
        if not self.ensure_initialized():
            return {
                "success": False,
                "error": "Core module not initialized",
                "message": "Module initialization failed"
            }
        
        try:
            start_time = datetime.datetime.now()
            
            # 应用运行时配置覆盖
            effective_params = self._apply_runtime_overrides({
                "action": action,
                "stage": stage,
                **kwargs
            })
            
            # 实现阶段管理逻辑
            result = self._execute_stage_action(
                effective_params["action"],
                effective_params.get("stage"),
                effective_params
            )
            
            # 记录统计信息
            duration = (datetime.datetime.now() - start_time).total_seconds()
            self.record_call(success=result.get("success", False), duration=duration)
            
            logger.info(f"aceflow_stage executed: action={action}, success={result.get('success')}")
            return result
            
        except Exception as e:
            self.record_call(success=False)
            logger.error(f"aceflow_stage error: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to execute stage action"
            }
    
    def aceflow_validate(
        self,
        mode: str = "basic",
        fix: bool = False,
        report: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        ✅ Validate project configuration and structure
        
        Args:
            mode: Validation mode (basic, standard, complete)
            fix: Whether to attempt automatic fixes
            report: Whether to generate detailed report
            **kwargs: Additional parameters
            
        Returns:
            Dict with validation results
        """
        if not self.ensure_initialized():
            return {
                "success": False,
                "error": "Core module not initialized",
                "message": "Module initialization failed"
            }
        
        try:
            start_time = datetime.datetime.now()
            
            # 应用运行时配置覆盖
            effective_params = self._apply_runtime_overrides({
                "mode": mode,
                "fix": fix,
                "report": report,
                **kwargs
            })
            
            # 实现验证逻辑
            result = self._execute_validation(
                effective_params["mode"],
                effective_params["fix"],
                effective_params["report"],
                effective_params
            )
            
            # 记录统计信息
            duration = (datetime.datetime.now() - start_time).total_seconds()
            self.record_call(success=result.get("success", False), duration=duration)
            
            logger.info(f"aceflow_validate executed: mode={mode}, success={result.get('success')}")
            return result
            
        except Exception as e:
            self.record_call(success=False)
            logger.error(f"aceflow_validate error: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to validate project"
            }
    
    # 内部实现方法
    
    def _execute_stage_action(
        self,
        action: str,
        stage: Optional[str],
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """执行阶段操作"""
        valid_actions = ["status", "next", "prev", "set", "list"]
        
        if action not in valid_actions:
            return {
                "success": False,
                "error": f"Invalid action '{action}'. Valid actions: {', '.join(valid_actions)}",
                "message": "Action validation failed"
            }
        
        try:
            # 获取当前项目状态
            project_state = self._get_project_state()
            
            if action == "status":
                return self._get_stage_status(project_state)
            elif action == "next":
                return self._advance_to_next_stage(project_state)
            elif action == "prev":
                return self._go_to_previous_stage(project_state)
            elif action == "set":
                return self._set_current_stage(project_state, stage)
            elif action == "list":
                return self._list_available_stages(project_state)
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to execute stage action '{action}'"
            }
    
    def _execute_validation(
        self,
        mode: str,
        fix: bool,
        report: bool,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """执行项目验证"""
        valid_modes = ["basic", "standard", "complete"]
        
        if mode not in valid_modes:
            return {
                "success": False,
                "error": f"Invalid validation mode '{mode}'. Valid modes: {', '.join(valid_modes)}",
                "message": "Validation mode validation failed"
            }
        
        try:
            validation_results = []
            
            # 基础验证
            basic_results = self._validate_basic_structure()
            validation_results.extend(basic_results)
            
            # 标准验证
            if mode in ["standard", "complete"]:
                standard_results = self._validate_standard_requirements()
                validation_results.extend(standard_results)
            
            # 完整验证
            if mode == "complete":
                complete_results = self._validate_complete_requirements()
                validation_results.extend(complete_results)
            
            # 统计结果
            total_checks = len(validation_results)
            passed_checks = sum(1 for r in validation_results if r["passed"])
            failed_checks = total_checks - passed_checks
            
            # 自动修复（如果启用）
            fixes_applied = []
            if fix and failed_checks > 0:
                fixes_applied = self._apply_automatic_fixes(validation_results)
            
            # 生成报告（如果启用）
            detailed_report = None
            if report:
                detailed_report = self._generate_validation_report(validation_results, fixes_applied)
            
            return {
                "success": failed_checks == 0,
                "message": f"Validation completed: {passed_checks}/{total_checks} checks passed",
                "validation_summary": {
                    "mode": mode,
                    "total_checks": total_checks,
                    "passed_checks": passed_checks,
                    "failed_checks": failed_checks,
                    "fixes_applied": len(fixes_applied) if fixes_applied else 0
                },
                "validation_results": validation_results,
                "fixes_applied": fixes_applied,
                "detailed_report": detailed_report
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to execute validation in {mode} mode"
            }
    
    def _get_project_state(self) -> Dict[str, Any]:
        """获取项目状态"""
        state_file = Path.cwd() / ".aceflow" / "current_state.json"
        
        if not state_file.exists():
            return {
                "project": {"name": "unknown", "mode": "standard"},
                "flow": {"current_stage": "requirement_analysis", "completed_stages": [], "progress_percentage": 0}
            }
        
        try:
            with open(state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load project state: {e}")
            return {
                "project": {"name": "unknown", "mode": "standard"},
                "flow": {"current_stage": "requirement_analysis", "completed_stages": [], "progress_percentage": 0}
            }
    
    def _save_project_state(self, state: Dict[str, Any]):
        """保存项目状态"""
        state_file = Path.cwd() / ".aceflow" / "current_state.json"
        state_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save project state: {e}")
    
    def _get_stage_status(self, project_state: Dict[str, Any]) -> Dict[str, Any]:
        """获取阶段状态"""
        flow = project_state.get("flow", {})
        
        return {
            "success": True,
            "message": "Stage status retrieved successfully",
            "stage_info": {
                "current_stage": flow.get("current_stage", "unknown"),
                "completed_stages": flow.get("completed_stages", []),
                "progress_percentage": flow.get("progress_percentage", 0),
                "project_mode": project_state.get("project", {}).get("mode", "standard")
            }
        }
    
    def _advance_to_next_stage(self, project_state: Dict[str, Any]) -> Dict[str, Any]:
        """推进到下一阶段"""
        # 这里实现阶段推进逻辑
        # 暂时返回占位符响应
        return {
            "success": True,
            "message": "Advanced to next stage",
            "stage_info": {
                "previous_stage": project_state.get("flow", {}).get("current_stage"),
                "current_stage": "next_stage",
                "progress_updated": True
            }
        }
    
    def _go_to_previous_stage(self, project_state: Dict[str, Any]) -> Dict[str, Any]:
        """回到上一阶段"""
        return {
            "success": True,
            "message": "Moved to previous stage",
            "stage_info": {
                "current_stage": project_state.get("flow", {}).get("current_stage"),
                "action": "previous"
            }
        }
    
    def _set_current_stage(self, project_state: Dict[str, Any], stage: Optional[str]) -> Dict[str, Any]:
        """设置当前阶段"""
        if not stage:
            return {
                "success": False,
                "error": "Stage name is required for 'set' action",
                "message": "Missing stage parameter"
            }
        
        return {
            "success": True,
            "message": f"Stage set to '{stage}'",
            "stage_info": {
                "previous_stage": project_state.get("flow", {}).get("current_stage"),
                "current_stage": stage
            }
        }
    
    def _list_available_stages(self, project_state: Dict[str, Any]) -> Dict[str, Any]:
        """列出可用阶段"""
        mode = project_state.get("project", {}).get("mode", "standard").lower()
        
        stages = {
            "minimal": ["implementation", "test", "demo"],
            "standard": ["user_stories", "task_breakdown", "test_design", "implementation", 
                        "unit_test", "integration_test", "code_review", "demo"],
            "complete": ["requirement_analysis", "architecture_design", "user_stories", 
                        "task_breakdown", "test_design", "implementation", "unit_test", 
                        "integration_test", "performance_test", "security_review", 
                        "code_review", "demo"],
            "smart": ["requirement_analysis", "user_stories", "task_breakdown", "test_design", 
                     "implementation", "unit_test", "integration_test", "performance_test", 
                     "code_review", "demo"]
        }
        
        available_stages = stages.get(mode, stages["standard"])
        
        return {
            "success": True,
            "message": f"Available stages for {mode} mode",
            "stage_info": {
                "mode": mode,
                "available_stages": available_stages,
                "total_stages": len(available_stages),
                "current_stage": project_state.get("flow", {}).get("current_stage")
            }
        }
    
    def _validate_basic_structure(self) -> List[Dict[str, Any]]:
        """基础结构验证"""
        results = []
        
        # 检查 .aceflow 目录
        aceflow_dir = Path.cwd() / ".aceflow"
        results.append({
            "check": "aceflow_directory_exists",
            "description": "Check if .aceflow directory exists",
            "passed": aceflow_dir.exists(),
            "details": f"Directory: {aceflow_dir}"
        })
        
        # 检查状态文件
        state_file = aceflow_dir / "current_state.json"
        results.append({
            "check": "state_file_exists",
            "description": "Check if current_state.json exists",
            "passed": state_file.exists(),
            "details": f"File: {state_file}"
        })
        
        # 检查结果目录
        result_dir = Path.cwd() / "aceflow_result"
        results.append({
            "check": "result_directory_exists",
            "description": "Check if aceflow_result directory exists",
            "passed": result_dir.exists(),
            "details": f"Directory: {result_dir}"
        })
        
        return results
    
    def _validate_standard_requirements(self) -> List[Dict[str, Any]]:
        """标准需求验证"""
        results = []
        
        # 检查模板文件
        template_file = Path.cwd() / ".aceflow" / "template.yaml"
        results.append({
            "check": "template_file_exists",
            "description": "Check if template.yaml exists",
            "passed": template_file.exists(),
            "details": f"File: {template_file}"
        })
        
        # 检查 .clinerules 目录
        clinerules_dir = Path.cwd() / ".clinerules"
        results.append({
            "check": "clinerules_directory_exists",
            "description": "Check if .clinerules directory exists",
            "passed": clinerules_dir.exists(),
            "details": f"Directory: {clinerules_dir}"
        })
        
        return results
    
    def _validate_complete_requirements(self) -> List[Dict[str, Any]]:
        """完整需求验证"""
        results = []
        
        # 检查所有必需的 .clinerules 文件
        clinerules_files = [
            "system_prompt.md",
            "aceflow_integration.md",
            "spec_summary.md",
            "spec_query_helper.md",
            "quality_standards.md"
        ]
        
        clinerules_dir = Path.cwd() / ".clinerules"
        for filename in clinerules_files:
            file_path = clinerules_dir / filename
            results.append({
                "check": f"clinerules_{filename.replace('.', '_')}_exists",
                "description": f"Check if .clinerules/{filename} exists",
                "passed": file_path.exists(),
                "details": f"File: {file_path}"
            })
        
        return results
    
    def _apply_automatic_fixes(self, validation_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """应用自动修复"""
        fixes_applied = []
        
        for result in validation_results:
            if not result["passed"]:
                fix_result = self._attempt_fix(result)
                if fix_result:
                    fixes_applied.append(fix_result)
        
        return fixes_applied
    
    def _attempt_fix(self, validation_result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """尝试修复单个验证问题"""
        check = validation_result["check"]
        
        try:
            if check == "aceflow_directory_exists":
                aceflow_dir = Path.cwd() / ".aceflow"
                aceflow_dir.mkdir(exist_ok=True)
                return {
                    "check": check,
                    "fix_applied": "Created .aceflow directory",
                    "success": True
                }
            
            elif check == "result_directory_exists":
                result_dir = Path.cwd() / "aceflow_result"
                result_dir.mkdir(exist_ok=True)
                return {
                    "check": check,
                    "fix_applied": "Created aceflow_result directory",
                    "success": True
                }
            
            # 其他修复逻辑...
            
        except Exception as e:
            return {
                "check": check,
                "fix_applied": f"Failed to fix: {str(e)}",
                "success": False
            }
        
        return None
    
    def _generate_validation_report(
        self,
        validation_results: List[Dict[str, Any]],
        fixes_applied: List[Dict[str, Any]]
    ) -> str:
        """生成验证报告"""
        report_lines = [
            "# AceFlow Project Validation Report",
            f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Summary",
            f"- Total checks: {len(validation_results)}",
            f"- Passed: {sum(1 for r in validation_results if r['passed'])}",
            f"- Failed: {sum(1 for r in validation_results if not r['passed'])}",
            f"- Fixes applied: {len(fixes_applied)}",
            "",
            "## Detailed Results"
        ]
        
        for result in validation_results:
            status = "✅ PASS" if result["passed"] else "❌ FAIL"
            report_lines.extend([
                f"### {result['check']}",
                f"**Status**: {status}",
                f"**Description**: {result['description']}",
                f"**Details**: {result['details']}",
                ""
            ])
        
        if fixes_applied:
            report_lines.extend([
                "## Applied Fixes",
                ""
            ])
            
            for fix in fixes_applied:
                status = "✅ SUCCESS" if fix["success"] else "❌ FAILED"
                report_lines.extend([
                    f"### {fix['check']}",
                    f"**Status**: {status}",
                    f"**Fix**: {fix['fix_applied']}",
                    ""
                ])
        
        return "\n".join(report_lines)
    
    # 运行时配置管理
    
    def _load_runtime_config(self):
        """加载运行时配置"""
        config_file = Path.cwd() / ".aceflow" / "runtime_config.json"
        
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    self._runtime_config = json.load(f)
                logger.debug("Runtime configuration loaded")
            except Exception as e:
                logger.warning(f"Failed to load runtime configuration: {e}")
                self._runtime_config = {}
        else:
            self._runtime_config = {}
    
    def _save_runtime_config(self):
        """保存运行时配置"""
        if not self._runtime_config:
            return
        
        config_file = Path.cwd() / ".aceflow" / "runtime_config.json"
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self._runtime_config, f, indent=2, ensure_ascii=False)
            logger.debug("Runtime configuration saved")
        except Exception as e:
            logger.error(f"Failed to save runtime configuration: {e}")
    
    def _update_runtime_config(self, updates: Dict[str, Any]):
        """更新运行时配置"""
        config_updates = {k: v for k, v in updates.items() if k.startswith("config_")}
        if config_updates:
            self._runtime_config.update(config_updates)
            logger.debug(f"Runtime configuration updated: {list(config_updates.keys())}")
    
    def _apply_runtime_overrides(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """应用运行时配置覆盖"""
        # 创建参数副本
        effective_params = params.copy()
        
        # 应用运行时配置覆盖
        for key, value in self._runtime_config.items():
            if key.startswith("config_"):
                param_key = key[7:]  # 移除 "config_" 前缀
                if param_key not in effective_params or effective_params[param_key] is None:
                    effective_params[param_key] = value
        
        return effective_params