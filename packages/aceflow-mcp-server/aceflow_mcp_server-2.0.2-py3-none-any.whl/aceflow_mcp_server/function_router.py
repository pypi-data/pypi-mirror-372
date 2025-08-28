"""
功能路由器 (FunctionRouter)
Function Router
This module provides intelligent routing for function calls based on parameters,
configuration, and context to determine the optimal execution path.
"""
from typing import Dict, Any, Optional, List
import logging
import datetime
from enum import Enum
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

class ExecutionMode(Enum):
    """执行模式枚举"""
    CORE_ONLY = "core_only"
    CORE_WITH_COLLABORATION = "core_with_collaboration"
    CORE_WITH_INTELLIGENCE = "core_with_intelligence"
    FULL_ENHANCED = "full_enhanced"

@dataclass
class ParameterFeatures:
    """参数特征分析结果"""
    has_user_input: bool = False
    requests_collaboration: bool = False
    requests_intelligence: bool = False
    auto_confirm: bool = False
    validation_level: str = "basic"
    complexity_score: float = 0.0
    interaction_required: bool = False
    enhancement_hints: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """计算复杂度分数"""
        score = 0.0
        if self.has_user_input:
            score += 0.3
        if self.requests_collaboration:
            score += 0.4
        if self.requests_intelligence:
            score += 0.3
        if self.interaction_required:
            score += 0.2
        if self.validation_level in ["enhanced", "comprehensive"]:
            score += 0.2
        self.complexity_score = min(score, 1.0)

@dataclass
class ExecutionPlan:
    """执行计划"""
    mode: ExecutionMode
    primary_module: str
    enhancement_modules: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    fallback_plan: Optional['ExecutionPlan'] = None
    created_at: str = field(default_factory=lambda: datetime.datetime.now().isoformat())
    
    def get_all_modules(self) -> List[str]:
        """获取所有涉及的模块"""
        modules = [self.primary_module]
        modules.extend(self.enhancement_modules)
        return list(set(modules))
    
    def requires_module(self, module_name: str) -> bool:
        """检查是否需要特定模块"""
        return module_name in self.get_all_modules()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "mode": self.mode.value,
            "primary_module": self.primary_module,
            "enhancement_modules": self.enhancement_modules,
            "parameters": self.parameters,
            "metadata": self.metadata,
            "confidence": self.confidence,
            "created_at": self.created_at
        }

class FunctionRouter:
    """智能功能路由器"""
    
    def __init__(self, config):
        """初始化功能路由器"""
        self.config = config
        self._execution_history: List[ExecutionPlan] = []
        self._routing_stats = {
            "total_routes": 0,
            "mode_distribution": {},
            "avg_confidence": 0.0,
            "fallback_usage": 0
        }
        logger.info("Function router initialized successfully")
    
    def plan_execution(self, tool_name: str, parameters: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> ExecutionPlan:
        """生成执行计划"""
        try:
            # 分析参数特征
            features = self._analyze_parameters(tool_name, parameters, context or {})
            
            # 决策执行模式
            mode = self._decide_execution_mode(tool_name, features)
            
            # 生成执行计划
            plan = self._generate_execution_plan(tool_name, mode, features, parameters, context or {})
            
            # 生成降级计划
            plan.fallback_plan = self._generate_fallback_plan(tool_name, plan, features)
            
            # 记录执行历史
            self._execution_history.append(plan)
            if len(self._execution_history) > 100:
                self._execution_history.pop(0)
            
            # 更新统计信息
            self._update_routing_stats(plan)
            
            logger.info(f"Execution plan generated: tool={tool_name}, mode={mode.value}, confidence={plan.confidence:.2f}")
            return plan
            
        except Exception as e:
            logger.error(f"Failed to generate execution plan for {tool_name}: {e}")
            return self._generate_basic_fallback_plan(tool_name, parameters)
    
    def _analyze_parameters(self, tool_name: str, parameters: Dict[str, Any], context: Dict[str, Any]) -> ParameterFeatures:
        """分析参数特征"""
        features = ParameterFeatures()
        
        # 检查用户输入
        user_input_fields = ['user_input', 'message', 'query', 'description', 'comment']
        for field in user_input_fields:
            if parameters.get(field):
                features.has_user_input = True
                break
        
        # 检查协作请求
        collab_indicators = [
            parameters.get('collaboration_mode') == 'enhanced',
            parameters.get('interactive', False),
            parameters.get('require_confirmation', False),
            not parameters.get('auto_confirm', True),
            parameters.get('collaboration_enabled', False)
        ]
        features.requests_collaboration = any(collab_indicators)
        
        # 检查智能功能请求
        intel_indicators = [
            features.has_user_input,
            parameters.get('intelligence_enabled', False),
            parameters.get('intent_analysis', False),
            parameters.get('smart_recommendations', False),
            tool_name in ['aceflow_intent_analyze', 'aceflow_recommend']
        ]
        features.requests_intelligence = any(intel_indicators)
        
        # 其他特征
        features.auto_confirm = parameters.get('auto_confirm', False)
        features.validation_level = parameters.get('validation_level', 'basic')
        
        interaction_indicators = [
            features.requests_collaboration,
            not features.auto_confirm,
            parameters.get('interactive', False),
            parameters.get('require_input', False)
        ]
        features.interaction_required = any(interaction_indicators)
        
        # 生成增强提示
        features.enhancement_hints = self._generate_enhancement_hints(tool_name, parameters, context)
        
        return features
    
    def _decide_execution_mode(self, tool_name: str, features: ParameterFeatures) -> ExecutionMode:
        """决策执行模式"""
        # 检查模块可用性
        collab_available = getattr(self.config.collaboration, 'enabled', False)
        intel_available = getattr(self.config.intelligence, 'enabled', False)
        
        # 如果没有增强模块可用，只能使用核心模式
        if not collab_available and not intel_available:
            return ExecutionMode.CORE_ONLY
        
        # 专用智能工具强制使用智能模式
        if tool_name in ['aceflow_intent_analyze', 'aceflow_recommend']:
            if intel_available:
                return ExecutionMode.CORE_WITH_INTELLIGENCE
            else:
                return ExecutionMode.CORE_ONLY
        
        # 专用协作工具强制使用协作模式
        if tool_name in ['aceflow_respond', 'aceflow_collaboration_status', 'aceflow_task_execute']:
            if collab_available:
                return ExecutionMode.CORE_WITH_COLLABORATION
            else:
                return ExecutionMode.CORE_ONLY
        
        # 基于特征决策
        needs_collab = collab_available and (
            features.requests_collaboration or
            (features.has_user_input and features.interaction_required) or
            features.complexity_score > 0.6
        )
        
        needs_intel = intel_available and (
            features.requests_intelligence or
            (features.has_user_input and getattr(self.config.intelligence, 'intent_recognition', False)) or
            features.validation_level in ['enhanced', 'comprehensive']
        )
        
        # 决策执行模式
        if needs_collab and needs_intel:
            return ExecutionMode.FULL_ENHANCED
        elif needs_collab:
            return ExecutionMode.CORE_WITH_COLLABORATION
        elif needs_intel:
            return ExecutionMode.CORE_WITH_INTELLIGENCE
        else:
            return ExecutionMode.CORE_ONLY
    
    def _generate_execution_plan(self, tool_name: str, mode: ExecutionMode, features: ParameterFeatures, parameters: Dict[str, Any], context: Dict[str, Any]) -> ExecutionPlan:
        """生成执行计划"""
        # 确定主模块
        primary_module = self._get_primary_module(tool_name, mode)
        
        # 确定增强模块
        enhancement_modules = self._get_enhancement_modules(mode, features)
        
        # 生成元数据
        metadata = self._generate_metadata(tool_name, mode, features, context)
        
        # 计算置信度
        confidence = self._calculate_confidence(mode, features, context)
        
        return ExecutionPlan(
            mode=mode,
            primary_module=primary_module,
            enhancement_modules=enhancement_modules,
            parameters=parameters,
            metadata=metadata,
            confidence=confidence
        )
    
    def _get_primary_module(self, tool_name: str, mode: ExecutionMode) -> str:
        """获取主模块"""
        tool_module_mapping = {
            'aceflow_intent_analyze': 'intelligence',
            'aceflow_recommend': 'intelligence',
            'aceflow_respond': 'collaboration',
            'aceflow_collaboration_status': 'collaboration',
            'aceflow_task_execute': 'collaboration'
        }
        
        if tool_name in tool_module_mapping:
            return tool_module_mapping[tool_name]
        
        return 'core'
    
    def _get_enhancement_modules(self, mode: ExecutionMode, features: ParameterFeatures) -> List[str]:
        """获取增强模块列表"""
        modules = []
        
        if mode == ExecutionMode.CORE_WITH_COLLABORATION:
            modules.append('collaboration')
        elif mode == ExecutionMode.CORE_WITH_INTELLIGENCE:
            modules.append('intelligence')
        elif mode == ExecutionMode.FULL_ENHANCED:
            modules.extend(['collaboration', 'intelligence'])
        
        return modules
    
    def _generate_metadata(self, tool_name: str, mode: ExecutionMode, features: ParameterFeatures, context: Dict[str, Any]) -> Dict[str, Any]:
        """生成执行计划元数据"""
        return {
            "tool_name": tool_name,
            "routing_version": "1.0.0",
            "features": {
                "has_user_input": features.has_user_input,
                "requests_collaboration": features.requests_collaboration,
                "requests_intelligence": features.requests_intelligence,
                "complexity_score": features.complexity_score,
                "enhancement_hints": features.enhancement_hints
            },
            "config_state": {
                "collaboration_enabled": getattr(self.config.collaboration, 'enabled', False),
                "intelligence_enabled": getattr(self.config.intelligence, 'enabled', False),
                "mode": getattr(self.config, 'mode', 'standard')
            },
            "context": {
                "has_project_state": bool(context.get('project_state')),
                "has_user_context": bool(context.get('user_id')),
                "timestamp": datetime.datetime.now().isoformat()
            }
        }
    
    def _calculate_confidence(self, mode: ExecutionMode, features: ParameterFeatures, context: Dict[str, Any]) -> float:
        """计算执行计划置信度"""
        confidence = 0.8
        
        mode_confidence = {
            ExecutionMode.CORE_ONLY: 0.9,
            ExecutionMode.CORE_WITH_COLLABORATION: 0.8,
            ExecutionMode.CORE_WITH_INTELLIGENCE: 0.8,
            ExecutionMode.FULL_ENHANCED: 0.7
        }
        confidence *= mode_confidence.get(mode, 0.8)
        
        if features.complexity_score > 0.8:
            confidence *= 0.9
        elif features.complexity_score < 0.3:
            confidence *= 1.1
        
        if context.get('project_state'):
            confidence *= 1.05
        
        if context.get('user_context'):
            confidence *= 1.03
        
        return min(confidence, 1.0)
    
    def _generate_fallback_plan(self, tool_name: str, primary_plan: ExecutionPlan, features: ParameterFeatures) -> Optional[ExecutionPlan]:
        """生成降级计划"""
        if primary_plan.mode == ExecutionMode.CORE_ONLY:
            return None
        
        return ExecutionPlan(
            mode=ExecutionMode.CORE_ONLY,
            primary_module='core',
            enhancement_modules=[],
            parameters=primary_plan.parameters,
            metadata={
                **primary_plan.metadata,
                "is_fallback": True,
                "original_mode": primary_plan.mode.value
            },
            confidence=0.6
        )
    
    def _generate_basic_fallback_plan(self, tool_name: str, parameters: Dict[str, Any]) -> ExecutionPlan:
        """生成基础降级计划"""
        return ExecutionPlan(
            mode=ExecutionMode.CORE_ONLY,
            primary_module='core',
            enhancement_modules=[],
            parameters=parameters,
            metadata={
                "tool_name": tool_name,
                "is_emergency_fallback": True,
                "error_recovery": True
            },
            confidence=0.5
        )
    
    def _generate_enhancement_hints(self, tool_name: str, parameters: Dict[str, Any], context: Dict[str, Any]) -> List[str]:
        """生成增强提示"""
        hints = []
        
        if tool_name == 'aceflow_init':
            if parameters.get('user_input'):
                hints.append("Consider using intent analysis for project setup")
            if not parameters.get('auto_confirm', True):
                hints.append("Interactive mode detected - collaboration module recommended")
        
        elif tool_name == 'aceflow_stage':
            if parameters.get('user_input'):
                hints.append("User input detected - intelligence module can provide guidance")
            if parameters.get('action') == 'next' and not parameters.get('auto_confirm', True):
                hints.append("Stage advancement with confirmation - collaboration recommended")
        
        elif tool_name == 'aceflow_validate':
            if parameters.get('validation_level') in ['enhanced', 'comprehensive']:
                hints.append("Enhanced validation requested - intelligence module recommended")
        
        if parameters.get('user_input') and not any('intent' in hint for hint in hints):
            hints.append("User input present - consider intent analysis")
        
        if not parameters.get('auto_confirm', True) and not any('collaboration' in hint for hint in hints):
            hints.append("Manual confirmation required - collaboration module helpful")
        
        return hints
    
    def _update_routing_stats(self, plan: ExecutionPlan):
        """更新路由统计信息"""
        self._routing_stats["total_routes"] += 1
        
        mode_key = plan.mode.value
        if mode_key not in self._routing_stats["mode_distribution"]:
            self._routing_stats["mode_distribution"][mode_key] = 0
        self._routing_stats["mode_distribution"][mode_key] += 1
        
        total_confidence = self._routing_stats["avg_confidence"] * (self._routing_stats["total_routes"] - 1)
        total_confidence += plan.confidence
        self._routing_stats["avg_confidence"] = total_confidence / self._routing_stats["total_routes"]
        
        if plan.fallback_plan:
            self._routing_stats["fallback_usage"] += 1
    
    def get_routing_stats(self) -> Dict[str, Any]:
        """获取路由统计信息"""
        return self._routing_stats.copy()
    
    def get_execution_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取执行历史"""
        recent_history = self._execution_history[-limit:] if limit > 0 else self._execution_history
        return [plan.to_dict() for plan in recent_history]
    
    def optimize_routing(self, feedback: Dict[str, Any]):
        """基于反馈优化路由决策"""
        logger.info(f"Routing optimization feedback received: {feedback}")
    
    def reset_stats(self):
        """重置统计信息"""
        self._routing_stats = {
            "total_routes": 0,
            "mode_distribution": {},
            "avg_confidence": 0.0,
            "fallback_usage": 0
        }
        self._execution_history.clear()
        logger.info("Routing statistics reset")