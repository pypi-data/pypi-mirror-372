"""
智能意图识别模块 - AceFlow AI-人协同工作流
Intent Recognition Module for AceFlow AI-Human Collaborative Workflow
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import re
import json
from pathlib import Path


class IntentType(Enum):
    """意图类型枚举"""
    START_WORKFLOW = "start_workflow"
    EXECUTE_TASK = "execute_task"
    CHECK_STATUS = "check_status"
    CONTINUE_STAGE = "continue_stage"
    PAUSE_WORKFLOW = "pause_workflow"
    SOLVE_PROBLEM = "solve_problem"
    UNKNOWN = "unknown"


class WorkflowMode(Enum):
    """工作流模式枚举"""
    MINIMAL = "minimal"
    STANDARD = "standard"
    COMPLETE = "complete"
    SMART = "smart"


@dataclass
class IntentResult:
    """意图识别结果"""
    intent_type: IntentType
    confidence: float
    parameters: Dict[str, Any]
    context: Dict[str, Any]
    suggested_action: str
    reasoning: str


class IntentRecognizer:
    """智能意图识别器"""
    
    def __init__(self):
        """初始化意图识别器"""
        self.prd_keywords = [
            "prd", "产品需求", "需求文档", "product requirement", 
            "requirements document", "功能需求", "业务需求"
        ]
        
        self.task_keywords = [
            "开始编码", "实现功能", "继续开发", "执行任务", 
            "start coding", "implement", "continue development"
        ]
        
        self.status_keywords = [
            "进度", "状态", "完成情况", "progress", "status", 
            "current stage", "当前阶段"
        ]
        
        self.continue_keywords = [
            "继续", "下一步", "下一阶段", "continue", "next", 
            "proceed", "move forward"
        ]
        
        self.pause_keywords = [
            "暂停", "停止", "等等", "pause", "stop", "wait"
        ]
        
        # 上下文历史记录
        self.conversation_history: List[Dict[str, Any]] = []
        
    def recognize_intent(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> IntentResult:
        """
        识别用户意图
        
        Args:
            user_input: 用户输入文本
            context: 上下文信息
            
        Returns:
            IntentResult: 意图识别结果
        """
        if context is None:
            context = {}
            
        # 更新对话历史
        self._update_conversation_history(user_input, context)
        
        # 预处理输入
        processed_input = self._preprocess_input(user_input)
        
        # 检测PRD文档
        prd_detection = self._detect_prd_document(processed_input, context)
        if prd_detection["detected"]:
            return self._create_start_workflow_intent(prd_detection, context)
        
        # 检测任务执行请求
        task_detection = self._detect_task_execution(processed_input, context)
        if task_detection["detected"]:
            return self._create_execute_task_intent(task_detection, context)
        
        # 检测状态查询
        status_detection = self._detect_status_query(processed_input, context)
        if status_detection["detected"]:
            return self._create_check_status_intent(status_detection, context)
        
        # 检测继续请求
        continue_detection = self._detect_continue_request(processed_input, context)
        if continue_detection["detected"]:
            return self._create_continue_stage_intent(continue_detection, context)
        
        # 检测暂停请求
        pause_detection = self._detect_pause_request(processed_input, context)
        if pause_detection["detected"]:
            return self._create_pause_workflow_intent(pause_detection, context)
        
        # 默认返回未知意图
        return self._create_unknown_intent(processed_input, context)
    
    def _preprocess_input(self, user_input: str) -> str:
        """预处理用户输入"""
        # 转换为小写
        processed = user_input.lower().strip()
        
        # 移除多余的空白字符
        processed = re.sub(r'\s+', ' ', processed)
        
        return processed
    
    def _detect_prd_document(self, processed_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """检测PRD文档相关的意图"""
        detection_score = 0.0
        detected_keywords = []
        
        # 检查PRD关键词
        for keyword in self.prd_keywords:
            if keyword.lower() in processed_input:
                detection_score += 0.3
                detected_keywords.append(keyword)
        
        # 检查文档格式指示
        doc_patterns = [
            r'\.md\b', r'\.docx?\b', r'\.pdf\b',
            r'文档', r'document', r'需求'
        ]
        
        for pattern in doc_patterns:
            if re.search(pattern, processed_input):
                detection_score += 0.2
        
        # 检查开发启动意图
        start_patterns = [
            r'开始开发', r'启动.*流程', r'start.*development',
            r'begin.*project', r'initialize'
        ]
        
        for pattern in start_patterns:
            if re.search(pattern, processed_input):
                detection_score += 0.4
        
        # 检查上下文中是否有文档内容
        if context.get('has_document_content', False):
            detection_score += 0.3
        
        return {
            "detected": detection_score >= 0.5,
            "confidence": min(detection_score, 1.0),
            "keywords": detected_keywords,
            "suggested_mode": self._suggest_workflow_mode(processed_input, context)
        }
    
    def _detect_task_execution(self, processed_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """检测任务执行请求"""
        detection_score = 0.0
        detected_keywords = []
        
        # 检查任务执行关键词
        for keyword in self.task_keywords:
            if keyword.lower() in processed_input:
                detection_score += 0.4
                detected_keywords.append(keyword)
        
        # 检查具体任务描述
        task_patterns = [
            r'实现.*功能', r'编写.*代码', r'创建.*模块',
            r'implement.*feature', r'write.*code', r'create.*module'
        ]
        
        for pattern in task_patterns:
            if re.search(pattern, processed_input):
                detection_score += 0.3
        
        # 检查当前是否在实现阶段
        current_stage = context.get('current_stage', '')
        if 'implementation' in current_stage.lower():
            detection_score += 0.2
        
        return {
            "detected": detection_score >= 0.4,
            "confidence": min(detection_score, 1.0),
            "keywords": detected_keywords,
            "task_description": self._extract_task_description(processed_input)
        }
    
    def _detect_status_query(self, processed_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """检测状态查询请求"""
        detection_score = 0.0
        detected_keywords = []
        
        # 检查状态查询关键词
        for keyword in self.status_keywords:
            if keyword.lower() in processed_input:
                detection_score += 0.4
                detected_keywords.append(keyword)
        
        # 检查疑问句模式
        question_patterns = [
            r'什么.*状态', r'如何.*进度', r'现在.*阶段',
            r'what.*status', r'how.*progress', r'current.*stage'
        ]
        
        for pattern in question_patterns:
            if re.search(pattern, processed_input):
                detection_score += 0.4
        
        return {
            "detected": detection_score >= 0.3,
            "confidence": min(detection_score, 1.0),
            "keywords": detected_keywords
        }
    
    def _detect_continue_request(self, processed_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """检测继续请求"""
        detection_score = 0.0
        detected_keywords = []
        
        # 检查继续关键词
        for keyword in self.continue_keywords:
            if keyword.lower() in processed_input:
                detection_score += 0.4
                detected_keywords.append(keyword)
        
        # 检查确认模式
        confirm_patterns = [
            r'^是的?$', r'^好的?$', r'^确认$', r'^yes$', r'^ok$', r'^确定$'
        ]
        
        for pattern in confirm_patterns:
            if re.search(pattern, processed_input):
                detection_score += 0.5
        
        return {
            "detected": detection_score >= 0.4,
            "confidence": min(detection_score, 1.0),
            "keywords": detected_keywords
        }
    
    def _detect_pause_request(self, processed_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """检测暂停请求"""
        detection_score = 0.0
        detected_keywords = []
        
        # 检查暂停关键词
        for keyword in self.pause_keywords:
            if keyword.lower() in processed_input:
                detection_score += 0.4
                detected_keywords.append(keyword)
        
        # 检查否定模式
        negative_patterns = [
            r'^不$', r'^否$', r'^no$', r'^不要$', r'^取消$'
        ]
        
        for pattern in negative_patterns:
            if re.search(pattern, processed_input):
                detection_score += 0.5
        
        return {
            "detected": detection_score >= 0.4,
            "confidence": min(detection_score, 1.0),
            "keywords": detected_keywords
        }
    
    def _suggest_workflow_mode(self, processed_input: str, context: Dict[str, Any]) -> WorkflowMode:
        """根据输入建议工作流模式"""
        # 检查复杂度指示词
        if any(word in processed_input for word in ['企业级', '完整', '全面', 'enterprise', 'complete', 'comprehensive']):
            return WorkflowMode.COMPLETE
        
        if any(word in processed_input for word in ['智能', 'ai', 'smart', '自适应', 'adaptive']):
            return WorkflowMode.SMART
        
        if any(word in processed_input for word in ['简单', '快速', '原型', 'simple', 'quick', 'prototype']):
            return WorkflowMode.MINIMAL
        
        # 默认推荐标准模式
        return WorkflowMode.STANDARD
    
    def _extract_task_description(self, processed_input: str) -> str:
        """提取任务描述"""
        # 简单的任务描述提取
        task_patterns = [
            r'实现(.+?)功能',
            r'创建(.+?)模块',
            r'编写(.+?)代码',
            r'implement\s+(.+?)(?:\s+feature|\s*$)',
            r'create\s+(.+?)(?:\s+module|\s*$)',
            r'write\s+(.+?)(?:\s+code|\s*$)'
        ]
        
        for pattern in task_patterns:
            match = re.search(pattern, processed_input)
            if match:
                return match.group(1).strip()
        
        return processed_input
    
    def _create_start_workflow_intent(self, detection: Dict[str, Any], context: Dict[str, Any]) -> IntentResult:
        """创建启动工作流意图结果"""
        return IntentResult(
            intent_type=IntentType.START_WORKFLOW,
            confidence=detection["confidence"],
            parameters={
                "suggested_mode": detection["suggested_mode"].value,
                "detected_keywords": detection["keywords"]
            },
            context=context,
            suggested_action=f"aceflow_init(mode='{detection['suggested_mode'].value}')",
            reasoning=f"检测到PRD文档相关内容，建议启动{detection['suggested_mode'].value}模式工作流"
        )
    
    def _create_execute_task_intent(self, detection: Dict[str, Any], context: Dict[str, Any]) -> IntentResult:
        """创建执行任务意图结果"""
        return IntentResult(
            intent_type=IntentType.EXECUTE_TASK,
            confidence=detection["confidence"],
            parameters={
                "task_description": detection["task_description"],
                "detected_keywords": detection["keywords"]
            },
            context=context,
            suggested_action="aceflow_stage(action='execute')",
            reasoning="检测到任务执行请求，建议执行当前阶段任务"
        )
    
    def _create_check_status_intent(self, detection: Dict[str, Any], context: Dict[str, Any]) -> IntentResult:
        """创建检查状态意图结果"""
        return IntentResult(
            intent_type=IntentType.CHECK_STATUS,
            confidence=detection["confidence"],
            parameters={
                "detected_keywords": detection["keywords"]
            },
            context=context,
            suggested_action="aceflow_stage(action='status')",
            reasoning="检测到状态查询请求，建议获取项目当前状态"
        )
    
    def _create_continue_stage_intent(self, detection: Dict[str, Any], context: Dict[str, Any]) -> IntentResult:
        """创建继续阶段意图结果"""
        return IntentResult(
            intent_type=IntentType.CONTINUE_STAGE,
            confidence=detection["confidence"],
            parameters={
                "detected_keywords": detection["keywords"]
            },
            context=context,
            suggested_action="aceflow_stage(action='next')",
            reasoning="检测到继续请求，建议推进到下一阶段"
        )
    
    def _create_pause_workflow_intent(self, detection: Dict[str, Any], context: Dict[str, Any]) -> IntentResult:
        """创建暂停工作流意图结果"""
        return IntentResult(
            intent_type=IntentType.PAUSE_WORKFLOW,
            confidence=detection["confidence"],
            parameters={
                "detected_keywords": detection["keywords"]
            },
            context=context,
            suggested_action="save_current_state()",
            reasoning="检测到暂停请求，建议保存当前状态并暂停工作流"
        )
    
    def _create_unknown_intent(self, processed_input: str, context: Dict[str, Any]) -> IntentResult:
        """创建未知意图结果"""
        return IntentResult(
            intent_type=IntentType.UNKNOWN,
            confidence=0.1,
            parameters={
                "original_input": processed_input
            },
            context=context,
            suggested_action="request_clarification()",
            reasoning="无法识别明确意图，建议请求用户澄清"
        )
    
    def _update_conversation_history(self, user_input: str, context: Dict[str, Any]):
        """更新对话历史"""
        self.conversation_history.append({
            "input": user_input,
            "context": context,
            "timestamp": context.get("timestamp", "unknown")
        })
        
        # 保持历史记录在合理范围内
        if len(self.conversation_history) > 10:
            self.conversation_history = self.conversation_history[-10:]
    
    def get_conversation_context(self) -> List[Dict[str, Any]]:
        """获取对话上下文"""
        return self.conversation_history.copy()
    
    def clear_conversation_history(self):
        """清除对话历史"""
        self.conversation_history.clear()


# 工厂函数
def create_intent_recognizer() -> IntentRecognizer:
    """创建意图识别器实例"""
    return IntentRecognizer()


# 便捷函数
def recognize_user_intent(user_input: str, context: Optional[Dict[str, Any]] = None) -> IntentResult:
    """
    便捷的意图识别函数
    
    Args:
        user_input: 用户输入
        context: 上下文信息
        
    Returns:
        IntentResult: 意图识别结果
    """
    recognizer = create_intent_recognizer()
    return recognizer.recognize_intent(user_input, context)