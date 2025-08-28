"""
智能模块 (IntelligenceModule)
Intelligence Module

This module creates IntelligenceModule class,
implementing intelligence tools: aceflow_intent_analyze, aceflow_recommend.
Integrates intent recognition and intelligent recommendation functionality.
Implements enhanced validation functionality.
"""

from typing import Dict, Any, Optional, List
import logging
import json
import os
import sys
from pathlib import Path
import datetime
import uuid

from .base_module import BaseModule, ModuleMetadata

# 导入智能组件 - 使用绝对导入避免问题
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from core.intent_recognizer import IntentRecognizer, IntentType, IntentResult, recognize_user_intent
    from core.recommendation_engine import RecommendationEngine, RecommendationType
    from core.validation_engine import ValidationEngine, ValidationLevel
except ImportError:
    # 如果导入失败，创建占位符类
    class IntentRecognizer:
        def __init__(self): pass
        def recognize_intent(self, text, context=None):
            return {"intent": "unknown", "confidence": 0.5, "parameters": {}}
    
    class IntentType:
        START_WORKFLOW = "start_workflow"
        EXECUTE_TASK = "execute_task"
        CHECK_STATUS = "check_status"
        UNKNOWN = "unknown"
    
    class IntentResult:
        def __init__(self, intent_type, confidence, parameters, context, suggested_action, reasoning):
            self.intent_type = intent_type
            self.confidence = confidence
            self.parameters = parameters
            self.context = context
            self.suggested_action = suggested_action
            self.reasoning = reasoning
    
    def recognize_user_intent(text, context=None):
        return {"intent": "unknown", "confidence": 0.5, "entities": {}}
    
    class RecommendationEngine:
        def __init__(self): pass
        def generate_recommendations(self, context):
            return []
    
    class RecommendationType:
        NEXT_ACTION = "next_action"
        OPTIMIZATION = "optimization"
        BEST_PRACTICE = "best_practice"
    
    class ValidationEngine:
        def __init__(self, level): pass
        def validate_enhanced(self, project_path):
            return {"success": True, "issues": [], "recommendations": []}
    
    class ValidationLevel:
        BASIC = "basic"
        STANDARD = "standard"
        ENHANCED = "enhanced"

logger = logging.getLogger(__name__)


class IntelligenceModule(BaseModule):
    """
    智能模块
    
    创建 IntelligenceModule 类，实现智能工具：
    - aceflow_intent_analyze: 分析用户意图并建议操作
    - aceflow_recommend: 获取智能推荐
    
    集成意图识别和智能推荐功能，实现增强验证功能。
    """    
    
    def __init__(self, config):
        """
        初始化智能模块
        
        Args:
            config: 智能模块配置
        """
        metadata = ModuleMetadata(
            name="intelligence",
            version="1.0.0",
            description="AI intelligence and recommendation functionality module",
            dependencies=["core"],
            optional_dependencies=["collaboration"],
            provides=["aceflow_intent_analyze", "aceflow_recommend"],
            tags={"intelligence", "ai", "enhanced"}
        )
        
        super().__init__(config, metadata)
        
        # 智能组件
        self._intent_recognizer: Optional[IntentRecognizer] = None
        self._recommendation_engine: Optional[RecommendationEngine] = None
        self._validation_engine: Optional[ValidationEngine] = None
        
        # 智能状态
        self._intent_history: List[Dict[str, Any]] = []
        self._recommendation_cache: Dict[str, Any] = {}
        
        # 配置参数
        self._intent_recognition = getattr(config, 'intent_recognition', True)
        self._adaptive_guidance = getattr(config, 'adaptive_guidance', True)
        self._learning_enabled = getattr(config, 'learning_enabled', False)
    
    def get_module_name(self) -> str:
        """获取模块名称"""
        return "intelligence"
    
    def _do_initialize(self) -> bool:
        """执行模块初始化逻辑"""
        try:
            # 初始化智能组件
            self._intent_recognizer = IntentRecognizer()
            self._recommendation_engine = RecommendationEngine()
            self._validation_engine = ValidationEngine(ValidationLevel.ENHANCED)
            
            # 加载意图历史
            self._load_intent_history()
            
            logger.info("Intelligence module initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Intelligence module initialization failed: {e}")
            return False
    
    def _do_cleanup(self):
        """执行模块清理逻辑"""
        try:
            # 保存意图历史
            self._save_intent_history()
            
            # 清理缓存
            self._recommendation_cache.clear()
            
            # 清理资源
            self._intent_recognizer = None
            self._recommendation_engine = None
            self._validation_engine = None
            
            logger.info("Intelligence module cleaned up successfully")
            
        except Exception as e:
            logger.error(f"Intelligence module cleanup error: {e}")
    
    def get_health_status(self) -> Dict[str, Any]:
        """获取模块健康状态"""
        if not self.initialized or not self._intent_recognizer:
            return {
                "healthy": False,
                "status": "not_initialized",
                "details": "Intelligence components not initialized"
            }
        
        return {
            "healthy": True,
            "status": "running",
            "details": "Intelligence module is healthy and ready",
            "tools_available": ["aceflow_intent_analyze", "aceflow_recommend"],
            "intent_history_size": len(self._intent_history),
            "recommendation_cache_size": len(self._recommendation_cache),
            "configuration": {
                "intent_recognition": self._intent_recognition,
                "adaptive_guidance": self._adaptive_guidance,
                "learning_enabled": self._learning_enabled
            }
        }    
 
   # 智能工具方法
    
    def aceflow_intent_analyze(
        self,
        user_input: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        🧠 Analyze user intent and suggest actions
        
        Args:
            user_input: 用户输入文本
            context: 可选的上下文信息
            
        Returns:
            Dict with intent analysis results and suggested actions
        """
        if not self.ensure_initialized():
            return {
                "success": False,
                "error": "Intelligence module not initialized",
                "message": "Module initialization failed"
            }
        
        try:
            start_time = datetime.datetime.now()
            
            # 准备上下文
            if context is None:
                context = {}
            
            # 添加项目上下文
            context.update(self._get_project_context())
            
            # 执行意图分析
            intent_result = self._analyze_user_intent(user_input, context)
            
            # 生成建议操作
            suggested_actions = self._generate_suggested_actions(intent_result, context)
            
            # 记录意图历史
            self._record_intent_analysis(user_input, intent_result, context)
            
            # 记录统计信息
            duration = (datetime.datetime.now() - start_time).total_seconds()
            self.record_call(success=True, duration=duration)
            
            logger.info(f"aceflow_intent_analyze executed: intent={intent_result.get('intent', 'unknown')}")
            
            return {
                "success": True,
                "message": "Intent analysis completed successfully",
                "user_input": user_input,
                "intent_analysis": intent_result,
                "suggested_actions": suggested_actions,
                "context_used": context,
                "analysis_timestamp": datetime.datetime.now().isoformat()
            }
            
        except Exception as e:
            self.record_call(success=False)
            logger.error(f"aceflow_intent_analyze error: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to analyze user intent"
            }
    
    def aceflow_recommend(
        self,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        💡 Get intelligent recommendations for next actions
        
        Args:
            context: 可选的上下文信息
            
        Returns:
            Dict with intelligent recommendations
        """
        if not self.ensure_initialized():
            return {
                "success": False,
                "error": "Intelligence module not initialized",
                "message": "Module initialization failed"
            }
        
        try:
            start_time = datetime.datetime.now()
            
            # 准备上下文
            if context is None:
                context = {}
            
            # 添加项目上下文
            context.update(self._get_project_context())
            
            # 生成推荐
            recommendations = self._generate_recommendations(context)
            
            # 缓存推荐结果
            cache_key = self._generate_cache_key(context)
            self._recommendation_cache[cache_key] = {
                "recommendations": recommendations,
                "timestamp": datetime.datetime.now().isoformat(),
                "context_hash": hash(str(context))
            }
            
            # 记录统计信息
            duration = (datetime.datetime.now() - start_time).total_seconds()
            self.record_call(success=True, duration=duration)
            
            logger.info(f"aceflow_recommend executed: {len(recommendations)} recommendations generated")
            
            return {
                "success": True,
                "message": "Recommendations generated successfully",
                "recommendations": recommendations,
                "context_used": context,
                "recommendation_timestamp": datetime.datetime.now().isoformat(),
                "cache_info": {
                    "cached": False,
                    "cache_key": cache_key
                }
            }
            
        except Exception as e:
            self.record_call(success=False)
            logger.error(f"aceflow_recommend error: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to generate recommendations"
            }    

    # 内部实现方法
    
    def _analyze_user_intent(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """分析用户意图"""
        try:
            if self._intent_recognizer and self._intent_recognition:
                # 使用意图识别器
                if hasattr(self._intent_recognizer, 'recognize_intent'):
                    result = self._intent_recognizer.recognize_intent(user_input, context)
                    
                    # 处理不同类型的返回值
                    if isinstance(result, dict):
                        return {
                            "intent": result.get("intent", "unknown"),
                            "confidence": result.get("confidence", 0.0),
                            "parameters": result.get("parameters", {}),
                            "reasoning": result.get("reasoning", "Intent recognized using pattern matching"),
                            "suggested_action": result.get("suggested_action", "No specific action suggested")
                        }
                    elif hasattr(result, 'intent_type'):
                        # IntentResult 对象
                        return {
                            "intent": result.intent_type.value if hasattr(result.intent_type, 'value') else str(result.intent_type),
                            "confidence": result.confidence,
                            "parameters": result.parameters,
                            "reasoning": result.reasoning,
                            "suggested_action": result.suggested_action
                        }
                else:
                    # 使用全局函数
                    result = recognize_user_intent(user_input, context)
                    return {
                        "intent": result.get("intent", "unknown"),
                        "confidence": result.get("confidence", 0.0),
                        "parameters": result.get("entities", {}),
                        "reasoning": "Intent recognized using global function",
                        "suggested_action": self._infer_action_from_intent(result.get("intent", "unknown"))
                    }
            
            # 简单的基于规则的意图分析
            return self._simple_intent_analysis(user_input, context)
            
        except Exception as e:
            logger.warning(f"Intent analysis failed: {e}")
            return self._simple_intent_analysis(user_input, context)
    
    def _simple_intent_analysis(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """简单的意图分析"""
        user_input_lower = user_input.lower().strip()
        
        # 基于关键词的简单分类
        if any(keyword in user_input_lower for keyword in ["start", "begin", "init", "create", "开始", "创建"]):
            intent = "start_workflow"
            confidence = 0.7
            suggested_action = "Initialize a new project or workflow"
        elif any(keyword in user_input_lower for keyword in ["status", "progress", "check", "状态", "进度"]):
            intent = "check_status"
            confidence = 0.8
            suggested_action = "Check current project status and progress"
        elif any(keyword in user_input_lower for keyword in ["continue", "next", "proceed", "继续", "下一步"]):
            intent = "continue_workflow"
            confidence = 0.7
            suggested_action = "Continue to the next stage of the workflow"
        elif any(keyword in user_input_lower for keyword in ["help", "recommend", "suggest", "帮助", "建议"]):
            intent = "request_help"
            confidence = 0.6
            suggested_action = "Provide recommendations and guidance"
        else:
            intent = "unknown"
            confidence = 0.3
            suggested_action = "Clarify the request or provide more context"
        
        return {
            "intent": intent,
            "confidence": confidence,
            "parameters": {"raw_input": user_input},
            "reasoning": f"Simple keyword-based analysis identified intent as '{intent}'",
            "suggested_action": suggested_action
        }
    
    def _infer_action_from_intent(self, intent: str) -> str:
        """从意图推断建议操作"""
        action_map = {
            "start_workflow": "Initialize a new AceFlow project",
            "execute_task": "Execute the specified task",
            "check_status": "Check current project status",
            "continue_stage": "Continue to the next workflow stage",
            "pause_workflow": "Pause the current workflow",
            "solve_problem": "Analyze and solve the identified problem",
            "unknown": "Provide more context or clarify the request"
        }
        
        return action_map.get(intent, "No specific action available for this intent")
    
    def _generate_suggested_actions(self, intent_result: Dict[str, Any], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成建议操作"""
        actions = []
        intent = intent_result.get("intent", "unknown")
        confidence = intent_result.get("confidence", 0.0)
        
        # 基于意图生成操作
        if intent == "start_workflow":
            actions.append({
                "action": "aceflow_init",
                "description": "Initialize a new AceFlow project",
                "parameters": {"mode": "standard"},
                "priority": "high",
                "confidence": confidence
            })
        elif intent == "check_status":
            actions.append({
                "action": "aceflow_stage",
                "description": "Check current workflow stage",
                "parameters": {"action": "status"},
                "priority": "medium",
                "confidence": confidence
            })
        elif intent == "continue_workflow":
            actions.append({
                "action": "aceflow_stage",
                "description": "Advance to next workflow stage",
                "parameters": {"action": "next"},
                "priority": "high",
                "confidence": confidence
            })
        
        # 添加通用推荐
        if confidence < 0.6:
            actions.append({
                "action": "clarify_intent",
                "description": "Request more specific information about the desired action",
                "parameters": {},
                "priority": "low",
                "confidence": 0.9
            })
        
        return actions
    
    def _generate_recommendations(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成智能推荐"""
        recommendations = []
        
        try:
            # 获取项目状态
            project_state = self._get_project_state()
            
            # 基于项目状态生成推荐
            if project_state:
                current_stage = project_state.get("flow", {}).get("current_stage", "unknown")
                completed_stages = project_state.get("flow", {}).get("completed_stages", [])
                progress = project_state.get("flow", {}).get("progress_percentage", 0)
                
                # 进度相关推荐
                if progress < 25:
                    recommendations.append({
                        "type": "progress",
                        "title": "Project Getting Started",
                        "description": "Your project is in the early stages. Consider setting up the basic structure and requirements.",
                        "priority": "high",
                        "actions": ["aceflow_init", "aceflow_stage"],
                        "confidence": 0.8
                    })
                elif progress < 75:
                    recommendations.append({
                        "type": "progress",
                        "title": "Development in Progress",
                        "description": "Good progress! Continue with implementation and testing phases.",
                        "priority": "medium",
                        "actions": ["aceflow_stage", "aceflow_validate"],
                        "confidence": 0.7
                    })
                else:
                    recommendations.append({
                        "type": "progress",
                        "title": "Project Near Completion",
                        "description": "Excellent progress! Focus on final validation and documentation.",
                        "priority": "medium",
                        "actions": ["aceflow_validate", "aceflow_stage"],
                        "confidence": 0.9
                    })
                
                # 阶段相关推荐
                stage_recommendations = self._get_stage_recommendations(current_stage, completed_stages)
                recommendations.extend(stage_recommendations)
            
            # 基于意图历史生成推荐
            history_recommendations = self._get_history_based_recommendations()
            recommendations.extend(history_recommendations)
            
            # 通用最佳实践推荐
            best_practice_recommendations = self._get_best_practice_recommendations(context)
            recommendations.extend(best_practice_recommendations)
            
        except Exception as e:
            logger.warning(f"Failed to generate some recommendations: {e}")
            # 添加基本推荐
            recommendations.append({
                "type": "general",
                "title": "Check Project Status",
                "description": "Review your current project status and progress",
                "priority": "low",
                "actions": ["aceflow_stage"],
                "confidence": 0.5
            })
        
        # 限制推荐数量并按优先级排序
        recommendations = sorted(recommendations, key=lambda x: (
            {"high": 3, "medium": 2, "low": 1}.get(x.get("priority", "low"), 1),
            x.get("confidence", 0.0)
        ), reverse=True)
        
        return recommendations[:5]  # 最多返回5个推荐
    
    def _get_stage_recommendations(self, current_stage: str, completed_stages: List[str]) -> List[Dict[str, Any]]:
        """获取阶段相关推荐"""
        recommendations = []
        
        stage_advice = {
            "requirement_analysis": {
                "title": "Requirements Analysis Phase",
                "description": "Focus on gathering and documenting detailed requirements",
                "actions": ["aceflow_stage", "aceflow_validate"]
            },
            "implementation": {
                "title": "Implementation Phase",
                "description": "Time to code! Implement the core functionality",
                "actions": ["aceflow_stage", "aceflow_validate"]
            },
            "testing": {
                "title": "Testing Phase",
                "description": "Ensure quality through comprehensive testing",
                "actions": ["aceflow_validate", "aceflow_stage"]
            }
        }
        
        if current_stage in stage_advice:
            advice = stage_advice[current_stage]
            recommendations.append({
                "type": "stage_guidance",
                "title": advice["title"],
                "description": advice["description"],
                "priority": "high",
                "actions": advice["actions"],
                "confidence": 0.8
            })
        
        return recommendations
    
    def _get_history_based_recommendations(self) -> List[Dict[str, Any]]:
        """基于历史记录生成推荐"""
        recommendations = []
        
        if len(self._intent_history) > 0:
            # 分析最近的意图模式
            recent_intents = [entry.get("intent", {}).get("intent", "unknown") 
                            for entry in self._intent_history[-5:]]
            
            # 如果用户经常查询状态，推荐设置自动更新
            if recent_intents.count("check_status") >= 2:
                recommendations.append({
                    "type": "pattern_based",
                    "title": "Frequent Status Checks Detected",
                    "description": "Consider enabling auto-advance mode to reduce manual status checking",
                    "priority": "low",
                    "actions": ["configure_auto_advance"],
                    "confidence": 0.6
                })
        
        return recommendations
    
    def _get_best_practice_recommendations(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """获取最佳实践推荐"""
        recommendations = []
        
        # 验证相关推荐
        recommendations.append({
            "type": "best_practice",
            "title": "Regular Validation",
            "description": "Run project validation regularly to catch issues early",
            "priority": "medium",
            "actions": ["aceflow_validate"],
            "confidence": 0.7
        })
        
        return recommendations    
 
   # 辅助方法
    
    def _get_project_context(self) -> Dict[str, Any]:
        """获取项目上下文"""
        context = {}
        
        try:
            # 获取项目状态
            project_state = self._get_project_state()
            if project_state:
                context["project_state"] = project_state
                context["current_stage"] = project_state.get("flow", {}).get("current_stage")
                context["progress"] = project_state.get("flow", {}).get("progress_percentage", 0)
            
            # 获取项目文件信息
            context["project_files"] = self._get_project_files_info()
            
            # 获取最近的意图历史
            if self._intent_history:
                context["recent_intents"] = self._intent_history[-3:]
            
        except Exception as e:
            logger.warning(f"Failed to get project context: {e}")
        
        return context
    
    def _get_project_state(self) -> Optional[Dict[str, Any]]:
        """获取项目状态"""
        state_file = Path.cwd() / ".aceflow" / "current_state.json"
        
        if not state_file.exists():
            return None
        
        try:
            with open(state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load project state: {e}")
            return None
    
    def _get_project_files_info(self) -> Dict[str, Any]:
        """获取项目文件信息"""
        info = {
            "has_aceflow_config": False,
            "has_result_dir": False,
            "has_clinerules": False,
            "file_count": 0
        }
        
        try:
            cwd = Path.cwd()
            
            # 检查关键目录和文件
            info["has_aceflow_config"] = (cwd / ".aceflow").exists()
            info["has_result_dir"] = (cwd / "aceflow_result").exists()
            info["has_clinerules"] = (cwd / ".clinerules").exists()
            
            # 统计文件数量
            info["file_count"] = len(list(cwd.glob("*")))
            
        except Exception as e:
            logger.warning(f"Failed to get project files info: {e}")
        
        return info
    
    def _record_intent_analysis(self, user_input: str, intent_result: Dict[str, Any], context: Dict[str, Any]):
        """记录意图分析"""
        record = {
            "timestamp": datetime.datetime.now().isoformat(),
            "user_input": user_input,
            "intent": intent_result,
            "context": context,
            "session_id": self._get_session_id()
        }
        
        self._intent_history.append(record)
        
        # 限制历史记录大小
        if len(self._intent_history) > 100:
            self._intent_history = self._intent_history[-50:]
    
    def _get_session_id(self) -> str:
        """获取会话ID"""
        # 简单的会话ID生成
        return f"session_{datetime.datetime.now().strftime('%Y%m%d_%H')}"
    
    def _generate_cache_key(self, context: Dict[str, Any]) -> str:
        """生成缓存键"""
        # 基于上下文生成缓存键
        key_parts = [
            context.get("current_stage", "unknown"),
            str(context.get("progress", 0)),
            str(len(self._intent_history))
        ]
        
        return "_".join(key_parts)
    
    def _load_intent_history(self):
        """加载意图历史"""
        history_file = Path.cwd() / ".aceflow" / "intent_history.json"
        if history_file.exists():
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    self._intent_history = json.load(f)
                logger.debug("Intent history loaded")
            except Exception as e:
                logger.warning(f"Failed to load intent history: {e}")
                self._intent_history = []
        else:
            self._intent_history = []
    
    def _save_intent_history(self):
        """保存意图历史"""
        history_file = Path.cwd() / ".aceflow" / "intent_history.json"
        history_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # 只保留最近的50条记录
            recent_history = self._intent_history[-50:]
            
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(recent_history, f, indent=2, ensure_ascii=False)
            logger.debug("Intent history saved")
        except Exception as e:
            logger.error(f"Failed to save intent history: {e}")
    
    # 增强验证功能
    
    def enhanced_validate(self, project_path: Optional[str] = None) -> Dict[str, Any]:
        """
        执行增强验证
        
        Args:
            project_path: 项目路径，默认为当前目录
            
        Returns:
            增强验证结果
        """
        if not self.ensure_initialized():
            return {
                "success": False,
                "error": "Intelligence module not initialized",
                "message": "Module initialization failed"
            }
        
        try:
            if project_path is None:
                project_path = str(Path.cwd())
            
            # 使用验证引擎进行增强验证
            if self._validation_engine:
                result = self._validation_engine.validate_enhanced(project_path)
            else:
                result = self._basic_enhanced_validation(project_path)
            
            # 添加智能推荐
            if result.get("success", False):
                recommendations = self._generate_validation_recommendations(result)
                result["intelligent_recommendations"] = recommendations
            
            return result
            
        except Exception as e:
            logger.error(f"Enhanced validation error: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Enhanced validation failed"
            }
    
    def _basic_enhanced_validation(self, project_path: str) -> Dict[str, Any]:
        """基础增强验证"""
        issues = []
        recommendations = []
        
        project_dir = Path(project_path)
        
        # 检查项目结构
        if not (project_dir / ".aceflow").exists():
            issues.append("Missing .aceflow directory")
            recommendations.append("Initialize AceFlow project structure")
        
        if not (project_dir / "aceflow_result").exists():
            issues.append("Missing aceflow_result directory")
            recommendations.append("Create result directory for project outputs")
        
        # 检查配置文件
        if not (project_dir / ".aceflow" / "current_state.json").exists():
            issues.append("Missing project state file")
            recommendations.append("Initialize project state tracking")
        
        return {
            "success": len(issues) == 0,
            "issues": issues,
            "recommendations": recommendations,
            "validation_level": "enhanced",
            "timestamp": datetime.datetime.now().isoformat()
        }
    
    def _generate_validation_recommendations(self, validation_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成验证推荐"""
        recommendations = []
        
        issues = validation_result.get("issues", [])
        
        for issue in issues:
            if "missing" in issue.lower():
                recommendations.append({
                    "type": "fix_missing",
                    "title": f"Fix: {issue}",
                    "description": f"Address the missing component: {issue}",
                    "priority": "high",
                    "confidence": 0.9
                })
        
        return recommendations