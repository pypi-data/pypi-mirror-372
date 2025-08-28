"""AceFlow MCP Resources implementation."""

from typing import Dict, Any
import json
from pathlib import Path
import os


class AceFlowResources:
    """AceFlow MCP Resources collection."""
    
    def __init__(self):
        """Initialize resources."""
        pass
    
    @staticmethod
    def _get_current_directory() -> Path:
        """Get current working directory."""
        return Path.cwd()
    
    @staticmethod
    def _find_aceflow_project_root(start_path: Path = None) -> Path:
        """Find the AceFlow project root directory."""
        if start_path is None:
            start_path = AceFlowResources._get_current_directory()
        
        current = start_path.resolve()
        
        # Look for AceFlow indicators
        while current != current.parent:
            if (current / ".aceflow").exists() or (current / ".clinerules").exists():
                return current
            current = current.parent
        
        # If not found, return current directory
        return start_path
    
    @staticmethod
    def project_state(project_id: str = "current") -> str:
        """Get current project state."""
        try:
            project_root = AceFlowResources._find_aceflow_project_root()
            state_file = project_root / ".aceflow" / "current_state.json"
            
            if state_file.exists():
                with open(state_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                return json.dumps(state, indent=2, ensure_ascii=False)
            else:
                # Return default state if no project found
                default_state = {
                    "project": {
                        "name": "unknown",
                        "mode": "UNKNOWN",
                        "status": "not_initialized"
                    },
                    "flow": {
                        "current_stage": "unknown",
                        "completed_stages": [],
                        "progress_percentage": 0
                    },
                    "metadata": {
                        "message": "No AceFlow project found in current directory",
                        "suggestion": "Use aceflow_init tool to initialize a project"
                    }
                }
                return json.dumps(default_state, indent=2, ensure_ascii=False)
                
        except Exception as e:
            error_state = {
                "error": str(e),
                "message": "Failed to get project state",
                "suggestion": "Check if you're in an AceFlow project directory"
            }
            return json.dumps(error_state, indent=2, ensure_ascii=False)
    
    @staticmethod
    def workflow_config(config_id: str = "default") -> str:
        """Get workflow configuration."""
        try:
            project_root = AceFlowResources._find_aceflow_project_root()
            template_file = project_root / ".aceflow" / "template.yaml"
            
            if template_file.exists():
                with open(template_file, 'r', encoding='utf-8') as f:
                    config_content = f.read()
                
                # Also include some parsed information
                config_info = {
                    "template_file": str(template_file),
                    "project_root": str(project_root),
                    "template_content": config_content,
                    "status": "found"
                }
                return json.dumps(config_info, indent=2, ensure_ascii=False)
            else:
                default_config = {
                    "message": "No workflow configuration found",
                    "template_file": str(project_root / ".aceflow" / "template.yaml"),
                    "status": "not_found",
                    "suggestion": "Initialize project with aceflow_init tool"
                }
                return json.dumps(default_config, indent=2, ensure_ascii=False)
                
        except Exception as e:
            error_config = {
                "error": str(e),
                "message": "Failed to get workflow config",
                "suggestion": "Check if you're in an AceFlow project directory"
            }
            return json.dumps(error_config, indent=2, ensure_ascii=False)
    
    @staticmethod
    def stage_guide(stage: str) -> str:
        """Get stage-specific guidance."""
        try:
            # Stage guides based on common AceFlow stages
            stage_guides = {
                "user_stories": """# 用户故事分析阶段指南

## 目标
分析和定义用户需求，创建清晰的用户故事。

## 主要任务
1. **用户角色识别**
   - 确定主要用户群体
   - 分析用户特征和需求
   - 创建用户画像

2. **用户故事编写**
   - 使用标准格式：作为[用户角色]，我希望[功能]，以便[价值]
   - 确保故事具体、可测试、有价值
   - 添加验收标准

3. **优先级排序**
   - 评估商业价值
   - 考虑技术实现难度
   - 确定开发顺序

## 输出要求
- 用户故事列表 (aceflow_result/user_stories.md)
- 用户画像文档 (aceflow_result/user_personas.md)
- 需求优先级矩阵 (aceflow_result/priority_matrix.md)

## 质量标准
- 每个用户故事包含明确的验收标准
- 故事之间逻辑清晰，无重叠
- 覆盖主要业务场景

## 下一阶段
完成后进入"任务分解"阶段，将用户故事转化为具体开发任务。""",

                "task_breakdown": """# 任务分解阶段指南

## 目标
将用户故事分解为可执行的开发任务。

## 主要任务
1. **技术分析**
   - 确定技术实现方案
   - 识别技术依赖和风险
   - 评估开发工作量

2. **任务创建**
   - 将用户故事分解为具体任务
   - 确保任务颗粒度适中（1-3天完成）
   - 定义任务之间的依赖关系

3. **资源规划**
   - 评估所需技能和人力
   - 安排开发时间线
   - 识别潜在瓶颈

## 输出要求
- 任务分解文档 (aceflow_result/task_breakdown.md)
- 技术实现方案 (aceflow_result/technical_approach.md)
- 开发计划 (aceflow_result/development_plan.md)

## 质量标准
- 任务定义明确，可量化完成
- 工作量估算合理
- 依赖关系清晰

## 下一阶段
完成后进入"测试用例设计"阶段。""",

                "test_design": """# 测试用例设计阶段指南

## 目标
设计全面的测试用例，确保质量保证。

## 主要任务
1. **测试策略制定**
   - 确定测试类型和范围
   - 制定测试环境要求
   - 定义通过标准

2. **测试用例编写**
   - 基于用户故事创建功能测试用例
   - 设计边界条件和异常场景测试
   - 编写自动化测试脚本

3. **测试数据准备**
   - 准备测试数据集
   - 设计数据验证方案
   - 确保数据安全性

## 输出要求
- 测试计划 (aceflow_result/test_plan.md)
- 测试用例文档 (aceflow_result/test_cases.md)
- 自动化测试脚本 (aceflow_result/automated_tests/)

## 质量标准
- 测试覆盖率达到设计要求
- 测试用例具体可执行
- 自动化程度符合项目需求

## 下一阶段
完成后进入"功能实现"阶段。""",

                "implementation": """# 功能实现阶段指南

## 目标
根据设计和任务分解实现核心功能。

## 主要任务
1. **代码开发**
   - 按照任务分解进行编码
   - 遵循代码规范和最佳实践
   - 实现核心业务逻辑

2. **代码质量**
   - 编写清晰的注释和文档
   - 进行代码自检和重构
   - 确保代码可维护性

3. **集成开发**
   - 模块间接口对接
   - 处理系统集成问题
   - 确保整体功能一致性

## 输出要求
- 源代码 (aceflow_result/src/)
- 技术文档 (aceflow_result/technical_docs/)
- API文档 (aceflow_result/api_docs/)

## 质量标准
- 代码符合规范，注释完整
- 核心功能正常工作
- 模块间接口稳定

## 下一阶段
完成后进入"单元测试"阶段。""",

                "unit_test": """# 单元测试阶段指南

## 目标
对实现的功能进行单元测试验证。

## 主要任务
1. **测试执行**
   - 运行设计的测试用例
   - 执行自动化测试脚本
   - 验证功能正确性

2. **问题修复**
   - 记录和分析测试失败
   - 修复发现的缺陷
   - 重新测试验证修复

3. **覆盖率分析**
   - 统计测试覆盖率
   - 补充遗漏的测试场景
   - 确保质量标准达成

## 输出要求
- 测试执行报告 (aceflow_result/test_report.md)
- 缺陷修复记录 (aceflow_result/bug_fixes.md)
- 测试覆盖率报告 (aceflow_result/coverage_report.md)

## 质量标准
- 主要功能测试通过
- 测试覆盖率达到要求
- 关键缺陷已修复

## 下一阶段
完成后进入"集成测试"阶段。""",

                "integration_test": """# 集成测试阶段指南

## 目标
验证系统各部分的集成和整体功能。

## 主要任务
1. **系统集成**
   - 验证模块间集成
   - 测试端到端流程
   - 检查数据流转

2. **环境测试**
   - 在目标环境中测试
   - 验证部署配置
   - 检查性能表现

3. **用户验收**
   - 基于用户故事验收
   - 收集用户反馈
   - 确认业务价值实现

## 输出要求
- 集成测试报告 (aceflow_result/integration_report.md)
- 性能测试结果 (aceflow_result/performance_report.md)
- 用户验收记录 (aceflow_result/acceptance_record.md)

## 质量标准
- 集成功能正常工作
- 性能指标达到要求
- 用户验收通过

## 下一阶段
完成后进入"代码审查"阶段。""",

                "code_review": """# 代码审查阶段指南

## 目标
全面审查代码质量和设计合理性。

## 主要任务
1. **代码质量审查**
   - 检查代码规范遵循
   - 评估代码可读性
   - 验证最佳实践应用

2. **架构设计审查**
   - 评估设计合理性
   - 检查扩展性和维护性
   - 确认安全性考虑

3. **文档完整性**
   - 检查技术文档完整性
   - 验证API文档准确性
   - 确保注释清晰有用

## 输出要求
- 代码审查报告 (aceflow_result/code_review.md)
- 改进建议 (aceflow_result/improvement_suggestions.md)
- 最终代码版本 (aceflow_result/final_code/)

## 质量标准
- 代码质量达到团队标准
- 设计问题已解决
- 文档完整准确

## 下一阶段
完成后进入"功能演示"阶段。""",

                "demo": """# 功能演示阶段指南

## 目标
准备和执行项目功能演示。

## 主要任务
1. **演示准备**
   - 准备演示脚本和数据
   - 设置演示环境
   - 预演和优化流程

2. **功能展示**
   - 演示核心功能
   - 突出项目价值
   - 收集反馈意见

3. **项目总结**
   - 整理项目成果
   - 总结经验教训
   - 制定后续计划

## 输出要求
- 演示脚本 (aceflow_result/demo_script.md)
- 演示录制/截图 (aceflow_result/demo_materials/)
- 项目总结报告 (aceflow_result/project_summary.md)

## 质量标准
- 演示流程顺畅
- 功能展示完整
- 项目价值清晰

## 项目完成
这是标准工作流的最后阶段，项目完成！"""
            }
            
            guide = stage_guides.get(stage.lower())
            if guide:
                return guide
            else:
                return f"""# {stage.title()} 阶段指南

## 说明
暂未找到阶段 '{stage}' 的详细指南。

## 可用阶段指南
- user_stories (用户故事分析)
- task_breakdown (任务分解)
- test_design (测试用例设计)
- implementation (功能实现)
- unit_test (单元测试)
- integration_test (集成测试)
- code_review (代码审查)
- demo (功能演示)

## 建议
请使用正确的阶段名称，或联系管理员添加新的阶段指南。"""
                
        except Exception as e:
            return f"""# 错误

获取阶段 '{stage}' 指南时发生错误: {str(e)}

请检查阶段名称是否正确，或重试操作。"""