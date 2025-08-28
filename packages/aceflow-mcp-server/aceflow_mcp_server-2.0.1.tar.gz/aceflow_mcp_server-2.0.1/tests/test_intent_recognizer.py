"""
意图识别模块的单元测试
Unit tests for Intent Recognition Module
"""

import pytest
from aceflow_mcp_server.core.intent_recognizer import (
    IntentRecognizer, IntentType, WorkflowMode, IntentResult,
    recognize_user_intent, create_intent_recognizer
)


class TestIntentRecognizer:
    """意图识别器测试类"""
    
    def setup_method(self):
        """测试前的设置"""
        self.recognizer = IntentRecognizer()
    
    def test_detect_prd_document_intent(self):
        """测试PRD文档意图识别"""
        test_cases = [
            {
                "input": "这是PRD文档，开始开发",
                "expected_intent": IntentType.START_WORKFLOW,
                "expected_mode": WorkflowMode.STANDARD
            },
            {
                "input": "我有一个产品需求文档，需要启动完整的开发流程",
                "expected_intent": IntentType.START_WORKFLOW,
                "expected_mode": WorkflowMode.COMPLETE
            },
            {
                "input": "Here's the product requirement document, start development",
                "expected_intent": IntentType.START_WORKFLOW,
                "expected_mode": WorkflowMode.STANDARD
            },
            {
                "input": "简单的需求文档，快速原型开发",
                "expected_intent": IntentType.START_WORKFLOW,
                "expected_mode": WorkflowMode.MINIMAL
            }
        ]
        
        for case in test_cases:
            result = self.recognizer.recognize_intent(case["input"])
            assert result.intent_type == case["expected_intent"]
            assert result.parameters["suggested_mode"] == case["expected_mode"].value
            assert result.confidence >= 0.5
    
    def test_detect_task_execution_intent(self):
        """测试任务执行意图识别"""
        test_cases = [
            "开始编码实现用户登录功能",
            "实现数据库连接模块",
            "继续开发API接口",
            "implement user authentication feature",
            "start coding the database module"
        ]
        
        context = {"current_stage": "S5_implementation"}
        
        for input_text in test_cases:
            result = self.recognizer.recognize_intent(input_text, context)
            assert result.intent_type == IntentType.EXECUTE_TASK
            assert result.confidence >= 0.4
            assert "aceflow_stage(action='execute')" in result.suggested_action
    
    def test_detect_status_query_intent(self):
        """测试状态查询意图识别"""
        test_cases = [
            "当前项目进度如何？",
            "现在处于什么阶段？",
            "项目状态怎么样？",
            "what's the current status?",
            "how is the progress?",
            "current stage?"
        ]
        
        for input_text in test_cases:
            result = self.recognizer.recognize_intent(input_text)
            assert result.intent_type == IntentType.CHECK_STATUS
            assert result.confidence >= 0.3
            assert "aceflow_stage(action='status')" in result.suggested_action
    
    def test_detect_continue_intent(self):
        """测试继续意图识别"""
        test_cases = [
            "继续",
            "下一步",
            "下一阶段",
            "是的",
            "好的",
            "确认",
            "yes",
            "ok",
            "continue",
            "next"
        ]
        
        for input_text in test_cases:
            result = self.recognizer.recognize_intent(input_text)
            assert result.intent_type == IntentType.CONTINUE_STAGE
            assert result.confidence >= 0.4
            assert "aceflow_stage(action='next')" in result.suggested_action
    
    def test_detect_pause_intent(self):
        """测试暂停意图识别"""
        test_cases = [
            "暂停",
            "停止",
            "等等",
            "不",
            "否",
            "不要",
            "取消",
            "pause",
            "stop",
            "no"
        ]
        
        for input_text in test_cases:
            result = self.recognizer.recognize_intent(input_text)
            assert result.intent_type == IntentType.PAUSE_WORKFLOW
            assert result.confidence >= 0.4
            assert "save_current_state()" in result.suggested_action
    
    def test_unknown_intent(self):
        """测试未知意图识别"""
        test_cases = [
            "今天天气怎么样？",
            "我想吃饭",
            "random text here",
            "这是什么意思？"
        ]
        
        for input_text in test_cases:
            result = self.recognizer.recognize_intent(input_text)
            assert result.intent_type == IntentType.UNKNOWN
            assert result.confidence <= 0.2
            assert "request_clarification()" in result.suggested_action
    
    def test_workflow_mode_suggestion(self):
        """测试工作流模式建议"""
        test_cases = [
            {
                "input": "企业级完整开发流程",
                "expected_mode": WorkflowMode.COMPLETE
            },
            {
                "input": "智能AI辅助开发",
                "expected_mode": WorkflowMode.SMART
            },
            {
                "input": "简单快速原型",
                "expected_mode": WorkflowMode.MINIMAL
            },
            {
                "input": "标准开发流程",
                "expected_mode": WorkflowMode.STANDARD
            }
        ]
        
        for case in test_cases:
            mode = self.recognizer._suggest_workflow_mode(case["input"], {})
            assert mode == case["expected_mode"]
    
    def test_task_description_extraction(self):
        """测试任务描述提取"""
        test_cases = [
            {
                "input": "实现用户登录功能",
                "expected": "用户登录"
            },
            {
                "input": "创建数据库连接模块",
                "expected": "数据库连接"
            },
            {
                "input": "implement user authentication",
                "expected": "user authentication"
            },
            {
                "input": "write API documentation",
                "expected": "API documentation"
            }
        ]
        
        for case in test_cases:
            result = self.recognizer._extract_task_description(case["input"])
            assert case["expected"] in result
    
    def test_conversation_history(self):
        """测试对话历史管理"""
        # 测试历史记录添加
        self.recognizer.recognize_intent("测试输入1")
        self.recognizer.recognize_intent("测试输入2")
        
        history = self.recognizer.get_conversation_context()
        assert len(history) == 2
        assert history[0]["input"] == "测试输入1"
        assert history[1]["input"] == "测试输入2"
        
        # 测试历史记录清除
        self.recognizer.clear_conversation_history()
        history = self.recognizer.get_conversation_context()
        assert len(history) == 0
    
    def test_context_influence(self):
        """测试上下文对意图识别的影响"""
        # 测试当前阶段对任务执行意图的影响
        context_with_impl_stage = {"current_stage": "S5_implementation"}
        result = self.recognizer.recognize_intent("开始编码", context_with_impl_stage)
        
        context_without_stage = {}
        result_no_context = self.recognizer.recognize_intent("开始编码", context_without_stage)
        
        # 有实现阶段上下文的置信度应该更高
        assert result.confidence >= result_no_context.confidence
    
    def test_confidence_scores(self):
        """测试置信度评分"""
        # 高置信度案例
        high_confidence_cases = [
            "这是PRD文档，开始完整开发流程",
            "继续下一阶段",
            "当前项目状态如何？"
        ]
        
        for case in high_confidence_cases:
            result = self.recognizer.recognize_intent(case)
            assert result.confidence >= 0.5
        
        # 低置信度案例
        low_confidence_cases = [
            "可能需要开发",
            "也许继续",
            "不太确定状态"
        ]
        
        for case in low_confidence_cases:
            result = self.recognizer.recognize_intent(case)
            assert result.confidence <= 0.6  # 允许一定的模糊性


class TestConvenienceFunctions:
    """便捷函数测试类"""
    
    def test_create_intent_recognizer(self):
        """测试创建意图识别器"""
        recognizer = create_intent_recognizer()
        assert isinstance(recognizer, IntentRecognizer)
    
    def test_recognize_user_intent(self):
        """测试便捷意图识别函数"""
        result = recognize_user_intent("这是PRD文档，开始开发")
        assert isinstance(result, IntentResult)
        assert result.intent_type == IntentType.START_WORKFLOW
    
    def test_recognize_user_intent_with_context(self):
        """测试带上下文的便捷意图识别函数"""
        context = {"current_stage": "S1_user_stories"}
        result = recognize_user_intent("继续下一阶段", context)
        assert isinstance(result, IntentResult)
        assert result.intent_type == IntentType.CONTINUE_STAGE


class TestEdgeCases:
    """边界情况测试类"""
    
    def setup_method(self):
        """测试前的设置"""
        self.recognizer = IntentRecognizer()
    
    def test_empty_input(self):
        """测试空输入"""
        result = self.recognizer.recognize_intent("")
        assert result.intent_type == IntentType.UNKNOWN
    
    def test_whitespace_input(self):
        """测试空白字符输入"""
        result = self.recognizer.recognize_intent("   \n\t   ")
        assert result.intent_type == IntentType.UNKNOWN
    
    def test_very_long_input(self):
        """测试超长输入"""
        long_input = "这是一个非常长的输入" * 100 + "PRD文档开始开发"
        result = self.recognizer.recognize_intent(long_input)
        assert result.intent_type == IntentType.START_WORKFLOW
    
    def test_mixed_language_input(self):
        """测试中英文混合输入"""
        mixed_inputs = [
            "这是PRD document，start development",
            "implement 用户登录 feature",
            "current 项目状态 how?"
        ]
        
        for input_text in mixed_inputs:
            result = self.recognizer.recognize_intent(input_text)
            assert result.intent_type != IntentType.UNKNOWN
    
    def test_special_characters(self):
        """测试特殊字符输入"""
        special_inputs = [
            "PRD文档！！！开始开发@#$%",
            "继续>>>下一阶段",
            "状态？？？进度如何？？？"
        ]
        
        for input_text in special_inputs:
            result = self.recognizer.recognize_intent(input_text)
            assert result.intent_type != IntentType.UNKNOWN


if __name__ == "__main__":
    pytest.main([__file__])