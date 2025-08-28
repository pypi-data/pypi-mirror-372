#!/usr/bin/env python3
"""
智能提示词生成器 - AceFlow MCP Server
基于AI决策思维和2025年MCP最佳实践的动态提示词生成系统
"""

import os
import json
from typing import Dict, Any, Optional, List
from pathlib import Path
from dataclasses import dataclass
from enum import Enum


class UserIntentType(Enum):
    """用户意图类型枚举"""
    PROJECT_INIT = "project_init"          # 项目初始化
    STATUS_CHECK = "status_check"          # 状态查看
    PROGRESS_ADVANCE = "progress_advance"  # 进度推进
    VALIDATION = "validation"              # 项目验证
    TEMPLATE_MANAGE = "template_manage"    # 模板管理
    HELP_GUIDANCE = "help_guidance"        # 帮助指导


class ProjectComplexity(Enum):
    """项目复杂度枚举"""
    SIMPLE = "simple"      # 简单项目
    STANDARD = "standard"  # 标准项目
    COMPLEX = "complex"    # 复杂项目
    UNKNOWN = "unknown"    # 未知复杂度


@dataclass
class ProjectContext:
    """项目上下文信息"""
    is_initialized: bool = False
    current_stage: Optional[str] = None
    progress_percentage: int = 0
    mode: Optional[str] = None
    project_name: Optional[str] = None
    has_errors: bool = False
    last_action: Optional[str] = None
    complexity: ProjectComplexity = ProjectComplexity.UNKNOWN


@dataclass
class UserIntent:
    """用户意图分析结果"""
    intent_type: UserIntentType
    confidence: float  # 0-1之间的置信度
    keywords: List[str]
    context_hints: List[str]


class ProjectContextAnalyzer:
    """项目上下文分析器"""
    
    def __init__(self):
        self.aceflow_indicators = [
            ".aceflow/current_state.json",
            ".clinerules",
            "aceflow_result/",
            "README_ACEFLOW.md"
        ]
    
    def analyze_current_directory(self, directory: str = None) -> ProjectContext:
        """分析当前目录的项目上下文"""
        if directory is None:
            directory = os.getcwd()
        
        project_path = Path(directory)
        context = ProjectContext()
        
        # 检查是否已初始化AceFlow
        aceflow_dir = project_path / ".aceflow"
        if aceflow_dir.exists():
            context.is_initialized = True
            
            # 读取项目状态
            state_file = aceflow_dir / "current_state.json"
            if state_file.exists():
                try:
                    with open(state_file, 'r', encoding='utf-8') as f:
                        state_data = json.load(f)
                    
                    context.current_stage = state_data.get("flow", {}).get("current_stage")
                    context.progress_percentage = state_data.get("flow", {}).get("progress_percentage", 0)
                    context.mode = state_data.get("project", {}).get("mode", "").lower()
                    context.project_name = state_data.get("project", {}).get("name")
                    
                    # 分析项目复杂度
                    if context.mode == "minimal":
                        context.complexity = ProjectComplexity.SIMPLE
                    elif context.mode in ["standard", "smart"]:
                        context.complexity = ProjectComplexity.STANDARD
                    elif context.mode == "complete":
                        context.complexity = ProjectComplexity.COMPLEX
                        
                except Exception:
                    context.has_errors = True
        
        return context
    
    def detect_project_type(self, directory: str = None) -> str:
        """检测项目类型"""
        if directory is None:
            directory = os.getcwd()
        
        project_path = Path(directory)
        
        # 检测常见项目类型的指示文件
        indicators = {
            "web": ["package.json", "yarn.lock", "webpack.config.js", "vite.config.js"],
            "python": ["requirements.txt", "setup.py", "pyproject.toml", "Pipfile"],
            "java": ["pom.xml", "build.gradle", "src/main/java"],
            "mobile": ["ios/", "android/", "lib/", "pubspec.yaml"],
            "data": ["requirements.txt", "jupyter/", "notebooks/", "data/"],
            "ai": ["model/", "training/", "inference/", "requirements.txt"]
        }
        
        for project_type, files in indicators.items():
            if any((project_path / file).exists() for file in files):
                return project_type
        
        return "general"


class UserIntentMapper:
    """用户意图映射器"""
    
    def __init__(self):
        self.intent_keywords = {
            UserIntentType.PROJECT_INIT: [
                "初始化", "创建", "开始", "新建", "setup", "init", "initialize", 
                "project", "项目", "开发", "搭建"
            ],
            UserIntentType.STATUS_CHECK: [
                "状态", "进度", "当前", "查看", "显示", "status", "progress", 
                "current", "show", "check", "情况"
            ],
            UserIntentType.PROGRESS_ADVANCE: [
                "下一步", "继续", "推进", "advance", "next", "proceed", 
                "forward", "完成", "move", "进入"
            ],
            UserIntentType.VALIDATION: [
                "验证", "检查", "测试", "validate", "check", "test", 
                "review", "audit", "质量", "错误"
            ],
            UserIntentType.TEMPLATE_MANAGE: [
                "模板", "template", "切换", "管理", "配置", "设置", 
                "更改", "选择"
            ],
            UserIntentType.HELP_GUIDANCE: [
                "帮助", "指导", "教程", "help", "guide", "tutorial", 
                "how", "什么", "如何", "怎么"
            ]
        }
    
    def analyze_user_query(self, query: str) -> UserIntent:
        """分析用户查询意图"""
        query_lower = query.lower()
        
        # 计算每种意图的匹配分数
        intent_scores = {}
        matched_keywords = {}
        
        for intent_type, keywords in self.intent_keywords.items():
            score = 0
            matches = []
            
            for keyword in keywords:
                if keyword in query_lower:
                    score += 1
                    matches.append(keyword)
            
            if score > 0:
                intent_scores[intent_type] = score / len(keywords)
                matched_keywords[intent_type] = matches
        
        # 选择得分最高的意图
        if intent_scores:
            best_intent = max(intent_scores.keys(), key=lambda k: intent_scores[k])
            confidence = intent_scores[best_intent]
            keywords = matched_keywords[best_intent]
        else:
            best_intent = UserIntentType.HELP_GUIDANCE
            confidence = 0.5
            keywords = []
        
        # 生成上下文提示
        context_hints = self._generate_context_hints(best_intent, query)
        
        return UserIntent(
            intent_type=best_intent,
            confidence=confidence,
            keywords=keywords,
            context_hints=context_hints
        )
    
    def _generate_context_hints(self, intent_type: UserIntentType, query: str) -> List[str]:
        """生成上下文提示"""
        hints = []
        
        if intent_type == UserIntentType.PROJECT_INIT:
            if "快速" in query or "简单" in query or "原型" in query:
                hints.append("建议使用minimal模式进行快速原型开发")
            elif "企业" in query or "团队" in query or "完整" in query:
                hints.append("建议使用complete模式进行企业级开发")
            elif "AI" in query or "智能" in query or "机器学习" in query:
                hints.append("建议使用smart模式进行AI项目开发")
            else:
                hints.append("建议使用standard模式进行标准项目开发")
        
        elif intent_type == UserIntentType.PROGRESS_ADVANCE:
            hints.append("确保当前阶段已完成所有必要任务")
            hints.append("建议先运行验证确保质量")
        
        elif intent_type == UserIntentType.VALIDATION:
            hints.append("可选择basic或complete验证模式")
            hints.append("验证将检查项目结构和质量标准")
        
        return hints


class ToolDecisionEngine:
    """工具决策引擎"""
    
    def __init__(self):
        self.tool_mappings = {
            UserIntentType.PROJECT_INIT: ["aceflow_init"],
            UserIntentType.STATUS_CHECK: ["aceflow_stage"],
            UserIntentType.PROGRESS_ADVANCE: ["aceflow_stage", "aceflow_validate"],
            UserIntentType.VALIDATION: ["aceflow_validate"],
            UserIntentType.TEMPLATE_MANAGE: ["aceflow_template"],
            UserIntentType.HELP_GUIDANCE: ["aceflow_stage", "aceflow_template"]
        }
    
    def recommend_tool(self, intent: UserIntent, context: ProjectContext) -> Dict[str, Any]:
        """基于意图和上下文推荐工具"""
        # 基础工具推荐
        candidate_tools = self.tool_mappings.get(intent.intent_type, [])
        
        # 上下文过滤和优化
        if not context.is_initialized and intent.intent_type != UserIntentType.PROJECT_INIT:
            return {
                "recommended_tool": "aceflow_init",
                "reason": "项目尚未初始化，需要先创建AceFlow项目结构",
                "suggested_parameters": self._suggest_init_parameters(intent, context),
                "confidence": 0.9
            }
        
        if context.is_initialized and intent.intent_type == UserIntentType.PROJECT_INIT:
            return {
                "recommended_tool": "aceflow_stage",
                "action": "status",
                "reason": "项目已初始化，建议查看当前状态而非重新初始化",
                "confidence": 0.8
            }
        
        # 选择最佳工具
        if candidate_tools:
            best_tool = candidate_tools[0]  # 简化版本，后续可以增加更复杂的选择逻辑
            
            return {
                "recommended_tool": best_tool,
                "reason": f"基于意图分析，{best_tool}最适合当前需求",
                "suggested_parameters": self._suggest_parameters(best_tool, intent, context),
                "confidence": intent.confidence
            }
        
        return {
            "recommended_tool": "aceflow_stage",
            "action": "status",
            "reason": "未能明确识别意图，建议查看项目状态",
            "confidence": 0.3
        }
    
    def _suggest_init_parameters(self, intent: UserIntent, context: ProjectContext) -> Dict[str, Any]:
        """建议初始化参数"""
        params = {}
        
        # 基于意图提示选择模式
        if "快速" in " ".join(intent.context_hints) or "原型" in " ".join(intent.context_hints):
            params["mode"] = "minimal"
        elif "企业" in " ".join(intent.context_hints) or "完整" in " ".join(intent.context_hints):
            params["mode"] = "complete"
        elif "AI" in " ".join(intent.context_hints) or "智能" in " ".join(intent.context_hints):
            params["mode"] = "smart"
        else:
            params["mode"] = "standard"
        
        return params
    
    def _suggest_parameters(self, tool_name: str, intent: UserIntent, context: ProjectContext) -> Dict[str, Any]:
        """建议工具参数"""
        params = {}
        
        if tool_name == "aceflow_stage":
            if intent.intent_type == UserIntentType.STATUS_CHECK:
                params["action"] = "status"
            elif intent.intent_type == UserIntentType.PROGRESS_ADVANCE:
                params["action"] = "next"
            else:
                params["action"] = "list"
        
        elif tool_name == "aceflow_validate":
            if context.complexity == ProjectComplexity.COMPLEX:
                params["mode"] = "complete"
            else:
                params["mode"] = "basic"
        
        return params


class IntelligentPromptGenerator:
    """智能提示词生成器主类"""
    
    def __init__(self):
        self.context_analyzer = ProjectContextAnalyzer()
        self.intent_mapper = UserIntentMapper()
        self.decision_engine = ToolDecisionEngine()
    
    def generate_enhanced_tool_description(
        self, 
        tool_name: str, 
        user_query: str = None,
        working_directory: str = None
    ) -> Dict[str, Any]:
        """生成增强的工具描述"""
        
        # 分析项目上下文
        context = self.context_analyzer.analyze_current_directory(working_directory)
        
        # 分析用户意图（如果提供了查询）
        intent = None
        if user_query:
            intent = self.intent_mapper.analyze_user_query(user_query)
        
        # 获取基础工具描述
        base_description = self._get_base_tool_description(tool_name)
        
        # 生成智能增强
        enhancement = self._generate_contextual_enhancement(tool_name, context, intent)
        
        # 组合最终描述
        enhanced_description = {
            **base_description,
            "contextual_guidance": enhancement["guidance"],
            "smart_recommendations": enhancement["recommendations"],
            "decision_factors": enhancement["decision_factors"],
            "success_indicators": enhancement["success_indicators"]
        }
        
        return enhanced_description
    
    def _get_base_tool_description(self, tool_name: str) -> Dict[str, Any]:
        """获取基础工具描述"""
        # 这里集成现有的tool_prompts.py内容
        descriptions = {
            "aceflow_init": {
                "name": "aceflow_init",
                "description": "🚀 智能初始化AceFlow项目 - 基于上下文分析的项目结构创建",
                "core_purpose": "为软件项目建立AI驱动的标准化开发工作流"
            },
            "aceflow_stage": {
                "name": "aceflow_stage", 
                "description": "📊 智能项目阶段管理 - 基于状态感知的工作流控制",
                "core_purpose": "跟踪、管理和推进项目开发阶段"
            },
            "aceflow_validate": {
                "name": "aceflow_validate",
                "description": "✅ 智能项目验证 - 基于项目复杂度的质量检查",
                "core_purpose": "确保项目质量和开发标准合规性"
            },
            "aceflow_template": {
                "name": "aceflow_template",
                "description": "🛠️ 智能模板管理 - 基于项目需求的模板操作",
                "core_purpose": "管理和应用项目工作流模板"
            }
        }
        
        return descriptions.get(tool_name, {})
    
    def _generate_contextual_enhancement(
        self, 
        tool_name: str, 
        context: ProjectContext, 
        intent: Optional[UserIntent]
    ) -> Dict[str, Any]:
        """生成上下文增强信息"""
        
        enhancement = {
            "guidance": [],
            "recommendations": [],
            "decision_factors": [],
            "success_indicators": []
        }
        
        # 基于项目状态的指导
        if tool_name == "aceflow_init":
            if context.is_initialized:
                enhancement["guidance"].append("⚠️ 项目已初始化，考虑使用aceflow_stage查看状态")
                enhancement["decision_factors"].append("当前目录已包含AceFlow配置")
            else:
                enhancement["guidance"].append("✨ 项目未初始化，这是开始的好时机")
                enhancement["recommendations"].append("建议先选择合适的工作流模式")
                
        elif tool_name == "aceflow_stage":
            if context.is_initialized:
                enhancement["guidance"].append(f"📍 当前阶段: {context.current_stage or '未知'}")
                enhancement["guidance"].append(f"📈 完成进度: {context.progress_percentage}%")
                if context.progress_percentage > 80:
                    enhancement["recommendations"].append("项目接近完成，建议进行最终验证")
            else:
                enhancement["guidance"].append("❌ 项目未初始化，请先使用aceflow_init")
                
        elif tool_name == "aceflow_validate":
            if context.is_initialized:
                if context.complexity == ProjectComplexity.COMPLEX:
                    enhancement["recommendations"].append("建议使用complete模式进行全面验证")
                else:
                    enhancement["recommendations"].append("建议使用basic模式进行快速验证")
            else:
                enhancement["guidance"].append("❌ 项目未初始化，无法执行验证")
        
        # 基于用户意图的增强
        if intent:
            enhancement["guidance"].extend(intent.context_hints)
            enhancement["decision_factors"].append(f"用户意图: {intent.intent_type.value}")
            enhancement["decision_factors"].append(f"意图置信度: {intent.confidence:.2f}")
        
        return enhancement


# 使用示例和测试
if __name__ == "__main__":
    generator = IntelligentPromptGenerator()
    
    # 测试场景1: 新项目初始化
    print("=== 测试场景1: 新项目初始化 ===")
    result = generator.generate_enhanced_tool_description(
        "aceflow_init", 
        "我想创建一个新的Web应用项目"
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    print("\n=== 测试场景2: 项目状态查看 ===")
    result = generator.generate_enhanced_tool_description(
        "aceflow_stage",
        "查看当前项目进度"
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))