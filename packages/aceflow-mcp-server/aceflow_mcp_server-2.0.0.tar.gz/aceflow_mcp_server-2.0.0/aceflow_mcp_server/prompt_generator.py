#!/usr/bin/env python3
"""
AceFlow MCP 智能提示词生成器
为大模型生成上下文相关的工具使用提示
"""

from typing import Dict, List, Any, Optional
from .tool_prompts import AceFlowToolPrompts


class AceFlowPromptGenerator:
    """AceFlow 智能提示词生成器"""
    
    def __init__(self):
        self.tool_prompts = AceFlowToolPrompts()
    
    def generate_context_prompt(self, context: str = "general") -> str:
        """
        根据上下文生成智能提示词
        
        Args:
            context: 上下文类型 (general, project_start, development, debugging)
            
        Returns:
            生成的提示词
        """
        base_prompt = """
# AceFlow MCP 工具使用助手

我是 AceFlow MCP 工具的智能助手，可以帮助你使用AI驱动的软件开发工作流工具。

## 🚀 可用工具概览

"""
        
        # 添加工具列表
        tool_definitions = self.tool_prompts.get_tool_definitions()
        for tool_name, tool_def in tool_definitions.items():
            base_prompt += f"### {tool_def['name']}\n"
            base_prompt += f"{tool_def['description']}\n\n"
        
        # 根据上下文添加特定建议
        context_prompts = {
            "project_start": self._get_project_start_prompt(),
            "development": self._get_development_prompt(),
            "debugging": self._get_debugging_prompt(),
            "general": self._get_general_prompt()
        }
        
        base_prompt += context_prompts.get(context, context_prompts["general"])
        
        return base_prompt
    
    def _get_project_start_prompt(self) -> str:
        """项目启动阶段的提示词"""
        return """
## 🎯 项目启动建议

当你开始一个新项目时，建议按以下顺序使用工具：

1. **初始化项目**: 使用 `aceflow_init` 创建项目结构
   - 新手推荐使用 `standard` 模式
   - 快速原型使用 `minimal` 模式
   - 企业项目使用 `complete` 模式

2. **查看工作流**: 使用 `aceflow_stage` 了解项目阶段
   - 先执行 `{"action": "list"}` 查看所有阶段
   - 再执行 `{"action": "status"}` 查看当前状态

3. **验证配置**: 使用 `aceflow_validate` 确保项目配置正确
   - 执行 `{"mode": "basic"}` 进行基础验证

### 示例工作流
```
1. aceflow_init({"mode": "standard", "project_name": "my-project"})
2. aceflow_stage({"action": "status"})
3. aceflow_validate({"mode": "basic"})
```
"""
    
    def _get_development_prompt(self) -> str:
        """开发阶段的提示词"""
        return """
## 🔧 开发阶段建议

在开发过程中，建议定期使用以下工具：

1. **跟踪进度**: 定期使用 `aceflow_stage` 查看项目状态
   - `{"action": "status"}` - 查看当前进度
   - `{"action": "next"}` - 推进到下一阶段

2. **质量检查**: 使用 `aceflow_validate` 确保代码质量
   - `{"mode": "basic"}` - 日常检查
   - `{"mode": "detailed", "report": true}` - 详细分析

3. **模板管理**: 根据需要调整工作流模板
   - `{"action": "list"}` - 查看可用模板
   - `{"action": "apply", "template": "xxx"}` - 应用新模板

### 开发最佳实践
- 完成每个阶段后进行验证
- 定期检查项目状态
- 根据项目复杂度调整模板
"""
    
    def _get_debugging_prompt(self) -> str:
        """调试阶段的提示词"""
        return """
## 🐛 问题排查建议

当遇到问题时，按以下步骤排查：

1. **检查项目状态**: 
   ```json
   aceflow_stage({"action": "status"})
   ```

2. **验证项目配置**:
   ```json
   aceflow_validate({"mode": "detailed", "report": true})
   ```

3. **查看模板配置**:
   ```json
   aceflow_template({"action": "list"})
   ```

### 常见问题解决
- **项目未初始化**: 使用 `aceflow_init` 重新初始化
- **阶段推进失败**: 检查当前阶段是否完成
- **验证失败**: 查看详细报告并修复问题
"""
    
    def _get_general_prompt(self) -> str:
        """通用提示词"""
        return """
## 💡 使用建议

### 工具选择指南
- **项目管理**: 使用 `aceflow_stage` 跟踪进度
- **质量保证**: 使用 `aceflow_validate` 检查质量
- **配置管理**: 使用 `aceflow_template` 管理模板
- **项目初始化**: 使用 `aceflow_init` 创建新项目

### 参数使用技巧
- 所有工具都返回 JSON 格式的结果
- 必需参数必须提供，可选参数可以省略
- 使用枚举值时请严格按照定义使用
- 查看工具描述了解详细用法

### 最佳实践
1. 按顺序完成工作流阶段
2. 定期进行质量验证
3. 根据项目需求选择合适模板
4. 保持项目配置的一致性
"""
    
    def generate_tool_specific_prompt(self, tool_name: str) -> str:
        """
        为特定工具生成详细提示词
        
        Args:
            tool_name: 工具名称
            
        Returns:
            工具特定的提示词
        """
        tool_definitions = self.tool_prompts.get_tool_definitions()
        
        if tool_name not in tool_definitions:
            return f"未找到工具 {tool_name} 的定义"
        
        tool_def = tool_definitions[tool_name]
        
        prompt = f"""
# {tool_def['name']} 工具详细指南

## 📋 工具描述
{tool_def['description']}

## 📖 详细说明
{tool_def['detailed_description']}

## 🔧 参数说明
"""
        
        # 添加参数详细说明
        schema = tool_def['inputSchema']
        if 'properties' in schema:
            for param_name, param_def in schema['properties'].items():
                prompt += f"### {param_name}\n"
                prompt += f"- **类型**: {param_def.get('type', 'unknown')}\n"
                prompt += f"- **描述**: {param_def.get('description', '无描述')}\n"
                
                if 'enum' in param_def:
                    prompt += f"- **可选值**: {', '.join(param_def['enum'])}\n"
                
                if 'default' in param_def:
                    prompt += f"- **默认值**: {param_def['default']}\n"
                
                if 'examples' in param_def:
                    prompt += f"- **示例**: {', '.join(map(str, param_def['examples']))}\n"
                
                prompt += "\n"
        
        # 添加使用示例
        if 'usage_examples' in tool_def:
            prompt += "## 💡 使用示例\n\n"
            for i, example in enumerate(tool_def['usage_examples'], 1):
                prompt += f"### 示例 {i}: {example['scenario']}\n"
                prompt += "```json\n"
                prompt += str(example['parameters']).replace("'", '"')
                prompt += "\n```\n\n"
        
        return prompt
    
    def generate_workflow_prompt(self, current_stage: Optional[str] = None) -> str:
        """
        根据当前阶段生成工作流提示词
        
        Args:
            current_stage: 当前项目阶段
            
        Returns:
            工作流相关的提示词
        """
        stages = [
            "user_stories", "task_breakdown", "test_design", "implementation",
            "unit_test", "integration_test", "code_review", "demo"
        ]
        
        prompt = "# AceFlow 工作流指导\n\n"
        
        if current_stage:
            if current_stage in stages:
                current_index = stages.index(current_stage)
                prompt += f"## 🎯 当前阶段: {current_stage}\n\n"
                
                if current_index > 0:
                    prompt += f"✅ 已完成: {', '.join(stages[:current_index])}\n\n"
                
                prompt += f"🔄 当前工作: {current_stage}\n\n"
                
                if current_index < len(stages) - 1:
                    prompt += f"⏭️ 下一阶段: {stages[current_index + 1]}\n\n"
                    prompt += f"📋 剩余阶段: {', '.join(stages[current_index + 1:])}\n\n"
            else:
                prompt += f"⚠️ 未知阶段: {current_stage}\n\n"
        
        prompt += "## 📊 完整工作流阶段\n\n"
        for i, stage in enumerate(stages, 1):
            status = "✅" if current_stage and stages.index(current_stage) >= i-1 else "⏳"
            prompt += f"{i}. {status} **{stage}** - {self._get_stage_description(stage)}\n"
        
        prompt += "\n## 🔧 推荐操作\n\n"
        if current_stage:
            prompt += f"- 使用 `aceflow_validate` 验证当前阶段完成情况\n"
            prompt += f"- 使用 `aceflow_stage({{\"action\": \"next\"}})` 推进到下一阶段\n"
        else:
            prompt += f"- 使用 `aceflow_stage({{\"action\": \"status\"}})` 查看当前状态\n"
            prompt += f"- 使用 `aceflow_init` 初始化项目（如果尚未初始化）\n"
        
        return prompt
    
    def _get_stage_description(self, stage: str) -> str:
        """获取阶段描述"""
        descriptions = {
            "user_stories": "分析用户需求，编写用户故事",
            "task_breakdown": "将用户故事分解为具体任务",
            "test_design": "设计测试用例和测试策略",
            "implementation": "实现核心功能和业务逻辑",
            "unit_test": "编写和执行单元测试",
            "integration_test": "执行集成测试和系统测试",
            "code_review": "进行代码审查和质量检查",
            "demo": "准备功能演示和文档"
        }
        return descriptions.get(stage, "未知阶段")