"""
验证引擎 - AceFlow AI-人协同工作流的输入输出验证
Validation Engine for AceFlow AI-Human Collaborative Workflow
"""

from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import re
import json
from pathlib import Path
from datetime import datetime


class ValidationLevel(Enum):
    """验证级别"""
    BASIC = "basic"
    STANDARD = "standard"
    STRICT = "strict"


class ValidationResult(Enum):
    """验证结果"""
    PASS = "pass"
    WARNING = "warning"
    FAIL = "fail"


@dataclass
class ValidationIssue:
    """验证问题"""
    level: ValidationResult
    category: str
    message: str
    suggestion: Optional[str] = None
    location: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationReport:
    """验证报告"""
    success: bool
    overall_score: float
    issues: List[ValidationIssue] = field(default_factory=list)
    summary: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


class InputValidator:
    """输入验证器"""
    
    def __init__(self, validation_level: ValidationLevel = ValidationLevel.STANDARD):
        """
        初始化输入验证器
        
        Args:
            validation_level: 验证级别
        """
        self.validation_level = validation_level
        
        # 阶段输入要求定义
        self.stage_input_requirements = {
            "S1_user_stories": {
                "required_files": ["prd.md", "requirements.md"],
                "optional_files": ["business_context.md"],
                "content_requirements": {
                    "min_length": 100,
                    "required_sections": ["概述", "功能需求"],
                    "required_keywords": ["用户", "功能", "需求"]
                }
            },
            "S2_task_breakdown": {
                "required_files": ["S1_user_stories.md"],
                "content_requirements": {
                    "min_length": 200,
                    "required_sections": ["用户故事", "验收标准"],
                    "user_story_format": True
                }
            },
            "S3_test_design": {
                "required_files": ["S2_task_breakdown.md"],
                "content_requirements": {
                    "min_length": 150,
                    "required_sections": ["任务列表", "开发计划"],
                    "task_format": True
                }
            },
            "S4_implementation": {
                "required_files": ["S2_task_breakdown.md", "S3_test_design.md"],
                "content_requirements": {
                    "test_cases_defined": True,
                    "test_strategy_present": True
                }
            }
        }
    
    def validate_stage_input(
        self,
        stage_id: str,
        input_data: Dict[str, Any],
        workspace_dir: Optional[Path] = None
    ) -> ValidationReport:
        """
        验证阶段输入
        
        Args:
            stage_id: 阶段ID
            input_data: 输入数据
            workspace_dir: 工作空间目录
            
        Returns:
            ValidationReport: 验证报告
        """
        issues = []
        workspace_dir = workspace_dir or Path.cwd()
        
        # 获取阶段要求
        requirements = self.stage_input_requirements.get(stage_id, {})
        
        if not requirements:
            issues.append(ValidationIssue(
                level=ValidationResult.WARNING,
                category="stage_definition",
                message=f"No input requirements defined for stage {stage_id}",
                suggestion="Define input requirements for this stage"
            ))
        else:
            # 验证必需文件
            issues.extend(self._validate_required_files(
                requirements.get("required_files", []),
                workspace_dir,
                stage_id
            ))
            
            # 验证内容要求
            content_requirements = requirements.get("content_requirements", {})
            if content_requirements:
                issues.extend(self._validate_content_requirements(
                    content_requirements,
                    input_data,
                    workspace_dir,
                    stage_id
                ))
        
        # 验证项目状态一致性
        issues.extend(self._validate_project_state_consistency(input_data, stage_id))
        
        # 生成验证报告
        return self._generate_validation_report(issues, "input", stage_id)
    
    def validate_user_input(
        self,
        user_input: str,
        expected_type: str = "general",
        context: Optional[Dict[str, Any]] = None
    ) -> ValidationReport:
        """
        验证用户输入
        
        Args:
            user_input: 用户输入
            expected_type: 期望的输入类型
            context: 上下文信息
            
        Returns:
            ValidationReport: 验证报告
        """
        issues = []
        
        # 基础验证
        if not user_input or not user_input.strip():
            issues.append(ValidationIssue(
                level=ValidationResult.FAIL,
                category="input_format",
                message="User input is empty",
                suggestion="Please provide valid input"
            ))
            return self._generate_validation_report(issues, "user_input", expected_type)
        
        # 长度验证
        if len(user_input.strip()) < 3:
            issues.append(ValidationIssue(
                level=ValidationResult.WARNING,
                category="input_length",
                message="User input is very short",
                suggestion="Consider providing more detailed input"
            ))
        
        # 类型特定验证
        if expected_type == "prd_document":
            issues.extend(self._validate_prd_document(user_input))
        elif expected_type == "task_description":
            issues.extend(self._validate_task_description(user_input))
        elif expected_type == "confirmation":
            issues.extend(self._validate_confirmation_input(user_input))
        
        return self._generate_validation_report(issues, "user_input", expected_type)
    
    def _validate_required_files(
        self,
        required_files: List[str],
        workspace_dir: Path,
        stage_id: str
    ) -> List[ValidationIssue]:
        """验证必需文件"""
        issues = []
        aceflow_result_dir = workspace_dir / "aceflow_result"
        
        for file_name in required_files:
            file_path = aceflow_result_dir / file_name
            
            if not file_path.exists():
                issues.append(ValidationIssue(
                    level=ValidationResult.FAIL,
                    category="missing_file",
                    message=f"Required file {file_name} not found",
                    suggestion=f"Complete the previous stage to generate {file_name}",
                    location=str(file_path)
                ))
            else:
                # 验证文件内容不为空
                try:
                    content = file_path.read_text(encoding='utf-8')
                    if len(content.strip()) < 50:
                        issues.append(ValidationIssue(
                            level=ValidationResult.WARNING,
                            category="file_content",
                            message=f"File {file_name} appears to be empty or too short",
                            suggestion="Ensure the file contains meaningful content",
                            location=str(file_path)
                        ))
                except Exception as e:
                    issues.append(ValidationIssue(
                        level=ValidationResult.FAIL,
                        category="file_access",
                        message=f"Cannot read file {file_name}: {str(e)}",
                        location=str(file_path)
                    ))
        
        return issues
    
    def _validate_content_requirements(
        self,
        requirements: Dict[str, Any],
        input_data: Dict[str, Any],
        workspace_dir: Path,
        stage_id: str
    ) -> List[ValidationIssue]:
        """验证内容要求"""
        issues = []
        
        # 验证最小长度
        min_length = requirements.get("min_length", 0)
        if min_length > 0:
            # 检查输入数据中的文本内容
            total_content_length = 0
            for key, value in input_data.items():
                if isinstance(value, str):
                    total_content_length += len(value)
            
            if total_content_length < min_length:
                issues.append(ValidationIssue(
                    level=ValidationResult.WARNING,
                    category="content_length",
                    message=f"Content length ({total_content_length}) is below minimum requirement ({min_length})",
                    suggestion="Provide more detailed content"
                ))
        
        # 验证必需章节
        required_sections = requirements.get("required_sections", [])
        if required_sections:
            issues.extend(self._validate_required_sections(
                required_sections, input_data, workspace_dir, stage_id
            ))
        
        # 验证用户故事格式
        if requirements.get("user_story_format"):
            issues.extend(self._validate_user_story_format(input_data, workspace_dir))
        
        # 验证任务格式
        if requirements.get("task_format"):
            issues.extend(self._validate_task_format(input_data, workspace_dir))
        
        return issues
    
    def _validate_required_sections(
        self,
        required_sections: List[str],
        input_data: Dict[str, Any],
        workspace_dir: Path,
        stage_id: str
    ) -> List[ValidationIssue]:
        """验证必需章节"""
        issues = []
        
        # 从相关文件中检查章节
        aceflow_result_dir = workspace_dir / "aceflow_result"
        
        for section in required_sections:
            section_found = False
            
            # 在输入数据中查找
            for key, value in input_data.items():
                if isinstance(value, str) and section.lower() in value.lower():
                    section_found = True
                    break
            
            # 在相关文件中查找
            if not section_found:
                for file_path in aceflow_result_dir.glob("*.md"):
                    try:
                        content = file_path.read_text(encoding='utf-8')
                        if section.lower() in content.lower():
                            section_found = True
                            break
                    except Exception:
                        continue
            
            if not section_found:
                issues.append(ValidationIssue(
                    level=ValidationResult.WARNING,
                    category="missing_section",
                    message=f"Required section '{section}' not found",
                    suggestion=f"Add a '{section}' section to the document"
                ))
        
        return issues
    
    def _validate_user_story_format(
        self,
        input_data: Dict[str, Any],
        workspace_dir: Path
    ) -> List[ValidationIssue]:
        """验证用户故事格式"""
        issues = []
        
        # 查找用户故事文件
        user_stories_file = workspace_dir / "aceflow_result" / "S1_user_stories.md"
        
        if user_stories_file.exists():
            try:
                content = user_stories_file.read_text(encoding='utf-8')
                
                # 检查用户故事格式: "作为...，我希望...，这样..."
                user_story_pattern = r'作为.*?，我希望.*?，这样.*?'
                user_stories = re.findall(user_story_pattern, content)
                
                if len(user_stories) == 0:
                    issues.append(ValidationIssue(
                        level=ValidationResult.WARNING,
                        category="user_story_format",
                        message="No properly formatted user stories found",
                        suggestion="Use format: '作为[角色]，我希望[功能]，这样[价值]'"
                    ))
                
            except Exception as e:
                issues.append(ValidationIssue(
                    level=ValidationResult.WARNING,
                    category="file_parsing",
                    message=f"Cannot parse user stories file: {str(e)}"
                ))
        
        return issues
    
    def _validate_task_format(
        self,
        input_data: Dict[str, Any],
        workspace_dir: Path
    ) -> List[ValidationIssue]:
        """验证任务格式"""
        issues = []
        
        # 查找任务分解文件
        task_file = workspace_dir / "aceflow_result" / "S2_task_breakdown.md"
        
        if task_file.exists():
            try:
                content = task_file.read_text(encoding='utf-8')
                
                # 检查任务格式: "- [ ] 任务名称"
                task_pattern = r'- \[ \] .+'
                tasks = re.findall(task_pattern, content)
                
                if len(tasks) == 0:
                    issues.append(ValidationIssue(
                        level=ValidationResult.WARNING,
                        category="task_format",
                        message="No properly formatted tasks found",
                        suggestion="Use format: '- [ ] Task name'"
                    ))
                elif len(tasks) < 3:
                    issues.append(ValidationIssue(
                        level=ValidationResult.WARNING,
                        category="task_count",
                        message=f"Only {len(tasks)} tasks found, consider adding more detailed tasks",
                        suggestion="Break down complex tasks into smaller, manageable tasks"
                    ))
                
            except Exception as e:
                issues.append(ValidationIssue(
                    level=ValidationResult.WARNING,
                    category="file_parsing",
                    message=f"Cannot parse task breakdown file: {str(e)}"
                ))
        
        return issues
    
    def _validate_project_state_consistency(
        self,
        input_data: Dict[str, Any],
        stage_id: str
    ) -> List[ValidationIssue]:
        """验证项目状态一致性"""
        issues = []
        
        # 检查项目状态文件
        state_file = Path(".aceflow/current_state.json")
        
        if state_file.exists():
            try:
                with open(state_file, 'r', encoding='utf-8') as f:
                    state_data = json.load(f)
                
                current_stage = state_data.get("flow", {}).get("current_stage", "")
                
                # 检查阶段一致性
                if current_stage != stage_id:
                    issues.append(ValidationIssue(
                        level=ValidationResult.WARNING,
                        category="stage_consistency",
                        message=f"Current stage ({current_stage}) doesn't match target stage ({stage_id})",
                        suggestion="Ensure you're executing the correct stage"
                    ))
                
            except Exception as e:
                issues.append(ValidationIssue(
                    level=ValidationResult.WARNING,
                    category="state_validation",
                    message=f"Cannot validate project state: {str(e)}"
                ))
        
        return issues
    
    def _validate_prd_document(self, content: str) -> List[ValidationIssue]:
        """验证PRD文档"""
        issues = []
        
        # 检查PRD关键要素
        required_elements = {
            "产品概述": ["概述", "overview", "产品介绍"],
            "功能需求": ["功能", "feature", "需求", "requirement"],
            "用户群体": ["用户", "user", "目标用户", "target user"]
        }
        
        content_lower = content.lower()
        
        for element, keywords in required_elements.items():
            if not any(keyword in content_lower for keyword in keywords):
                issues.append(ValidationIssue(
                    level=ValidationResult.WARNING,
                    category="prd_completeness",
                    message=f"PRD document may be missing '{element}' section",
                    suggestion=f"Consider adding information about {element}"
                ))
        
        return issues
    
    def _validate_task_description(self, content: str) -> List[ValidationIssue]:
        """验证任务描述"""
        issues = []
        
        # 检查任务描述的完整性
        if len(content.strip()) < 10:
            issues.append(ValidationIssue(
                level=ValidationResult.WARNING,
                category="task_detail",
                message="Task description is too brief",
                suggestion="Provide more detailed task description"
            ))
        
        # 检查是否包含动作词
        action_words = ["实现", "创建", "开发", "设计", "测试", "implement", "create", "develop", "design", "test"]
        if not any(word in content.lower() for word in action_words):
            issues.append(ValidationIssue(
                level=ValidationResult.WARNING,
                category="task_clarity",
                message="Task description may lack clear action",
                suggestion="Use action words like '实现', '创建', '开发' etc."
            ))
        
        return issues
    
    def _validate_confirmation_input(self, content: str) -> List[ValidationIssue]:
        """验证确认输入"""
        issues = []
        
        content_lower = content.lower().strip()
        
        # 检查是否是有效的确认响应
        valid_yes = ["yes", "y", "是", "是的", "好", "好的", "确认", "继续", "同意"]
        valid_no = ["no", "n", "否", "不", "不是", "取消", "停止", "暂停"]
        
        if content_lower not in valid_yes + valid_no:
            issues.append(ValidationIssue(
                level=ValidationResult.WARNING,
                category="confirmation_format",
                message="Confirmation response may be ambiguous",
                suggestion="Use clear responses like 'yes/no' or '是/否'"
            ))
        
        return issues
    
    def _generate_validation_report(
        self,
        issues: List[ValidationIssue],
        validation_type: str,
        target: str
    ) -> ValidationReport:
        """生成验证报告"""
        # 计算总体评分
        total_issues = len(issues)
        fail_count = len([i for i in issues if i.level == ValidationResult.FAIL])
        warning_count = len([i for i in issues if i.level == ValidationResult.WARNING])
        
        # 评分逻辑：失败问题严重扣分，警告问题轻微扣分
        base_score = 100.0
        score_deduction = (fail_count * 20) + (warning_count * 5)
        overall_score = max(0.0, base_score - score_deduction)
        
        # 判断是否成功
        success = fail_count == 0 and overall_score >= 60.0
        
        # 生成摘要
        summary = {
            "validation_type": validation_type,
            "target": target,
            "total_issues": total_issues,
            "fail_count": fail_count,
            "warning_count": warning_count,
            "pass_count": 0 if total_issues > 0 else 1
        }
        
        # 生成建议
        recommendations = []
        if fail_count > 0:
            recommendations.append("修复所有失败项以继续流程")
        if warning_count > 0:
            recommendations.append("考虑解决警告项以提高质量")
        if success:
            recommendations.append("验证通过，可以继续下一步")
        
        return ValidationReport(
            success=success,
            overall_score=overall_score,
            issues=issues,
            summary=summary,
            recommendations=recommendations
        )


class OutputValidator:
    """输出验证器"""
    
    def __init__(self, validation_level: ValidationLevel = ValidationLevel.STANDARD):
        """
        初始化输出验证器
        
        Args:
            validation_level: 验证级别
        """
        self.validation_level = validation_level
        
        # 阶段输出要求定义
        self.stage_output_requirements = {
            "S1_user_stories": {
                "required_sections": ["概述", "用户故事", "验收标准"],
                "min_user_stories": 3,
                "format_requirements": {
                    "user_story_format": True,
                    "acceptance_criteria": True
                }
            },
            "S2_task_breakdown": {
                "required_sections": ["任务列表", "开发计划"],
                "min_tasks": 5,
                "format_requirements": {
                    "task_format": True,
                    "time_estimates": True
                }
            },
            "S3_test_design": {
                "required_sections": ["测试策略", "测试用例"],
                "min_test_cases": 10,
                "format_requirements": {
                    "test_case_format": True,
                    "coverage_plan": True
                }
            }
        }
    
    def validate_stage_output(
        self,
        stage_id: str,
        output_path: Path,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ValidationReport:
        """
        验证阶段输出
        
        Args:
            stage_id: 阶段ID
            output_path: 输出文件路径
            metadata: 元数据
            
        Returns:
            ValidationReport: 验证报告
        """
        issues = []
        
        # 检查文件是否存在
        if not output_path.exists():
            issues.append(ValidationIssue(
                level=ValidationResult.FAIL,
                category="missing_output",
                message=f"Output file {output_path} does not exist",
                location=str(output_path)
            ))
            return self._generate_validation_report(issues, "output", stage_id)
        
        # 读取文件内容
        try:
            content = output_path.read_text(encoding='utf-8')
        except Exception as e:
            issues.append(ValidationIssue(
                level=ValidationResult.FAIL,
                category="file_access",
                message=f"Cannot read output file: {str(e)}",
                location=str(output_path)
            ))
            return self._generate_validation_report(issues, "output", stage_id)
        
        # 获取阶段要求
        requirements = self.stage_output_requirements.get(stage_id, {})
        
        if requirements:
            # 验证必需章节
            required_sections = requirements.get("required_sections", [])
            issues.extend(self._validate_output_sections(content, required_sections))
            
            # 验证格式要求
            format_requirements = requirements.get("format_requirements", {})
            issues.extend(self._validate_output_format(content, format_requirements, stage_id))
            
            # 验证数量要求
            issues.extend(self._validate_output_quantities(content, requirements, stage_id))
        
        # 验证通用质量要求
        issues.extend(self._validate_output_quality(content, stage_id))
        
        return self._generate_validation_report(issues, "output", stage_id)
    
    def _validate_output_sections(
        self,
        content: str,
        required_sections: List[str]
    ) -> List[ValidationIssue]:
        """验证输出章节"""
        issues = []
        
        for section in required_sections:
            # 检查章节标题
            section_patterns = [
                f"# {section}",
                f"## {section}",
                f"### {section}",
                section.lower()
            ]
            
            section_found = any(pattern in content.lower() for pattern in section_patterns)
            
            if not section_found:
                issues.append(ValidationIssue(
                    level=ValidationResult.WARNING,
                    category="missing_section",
                    message=f"Required section '{section}' not found in output",
                    suggestion=f"Add '{section}' section to the document"
                ))
        
        return issues
    
    def _validate_output_format(
        self,
        content: str,
        format_requirements: Dict[str, bool],
        stage_id: str
    ) -> List[ValidationIssue]:
        """验证输出格式"""
        issues = []
        
        if format_requirements.get("user_story_format"):
            user_story_pattern = r'作为.*?，我希望.*?，这样.*?'
            user_stories = re.findall(user_story_pattern, content)
            
            if len(user_stories) == 0:
                issues.append(ValidationIssue(
                    level=ValidationResult.WARNING,
                    category="format_validation",
                    message="No properly formatted user stories found",
                    suggestion="Use format: '作为[角色]，我希望[功能]，这样[价值]'"
                ))
        
        if format_requirements.get("task_format"):
            task_pattern = r'- \[ \] .+'
            tasks = re.findall(task_pattern, content)
            
            if len(tasks) == 0:
                issues.append(ValidationIssue(
                    level=ValidationResult.WARNING,
                    category="format_validation",
                    message="No properly formatted tasks found",
                    suggestion="Use format: '- [ ] Task name'"
                ))
        
        if format_requirements.get("acceptance_criteria"):
            criteria_patterns = [
                r'验收标准',
                r'acceptance criteria',
                r'WHEN.*THEN.*SHALL'
            ]
            
            criteria_found = any(re.search(pattern, content, re.IGNORECASE) for pattern in criteria_patterns)
            
            if not criteria_found:
                issues.append(ValidationIssue(
                    level=ValidationResult.WARNING,
                    category="format_validation",
                    message="No acceptance criteria found",
                    suggestion="Add acceptance criteria for user stories"
                ))
        
        return issues
    
    def _validate_output_quantities(
        self,
        content: str,
        requirements: Dict[str, Any],
        stage_id: str
    ) -> List[ValidationIssue]:
        """验证输出数量"""
        issues = []
        
        # 验证用户故事数量
        if "min_user_stories" in requirements:
            min_count = requirements["min_user_stories"]
            user_story_pattern = r'作为.*?，我希望.*?，这样.*?'
            actual_count = len(re.findall(user_story_pattern, content))
            
            if actual_count < min_count:
                issues.append(ValidationIssue(
                    level=ValidationResult.WARNING,
                    category="quantity_validation",
                    message=f"Found {actual_count} user stories, minimum required: {min_count}",
                    suggestion="Add more detailed user stories"
                ))
        
        # 验证任务数量
        if "min_tasks" in requirements:
            min_count = requirements["min_tasks"]
            task_pattern = r'- \[ \] .+'
            actual_count = len(re.findall(task_pattern, content))
            
            if actual_count < min_count:
                issues.append(ValidationIssue(
                    level=ValidationResult.WARNING,
                    category="quantity_validation",
                    message=f"Found {actual_count} tasks, minimum required: {min_count}",
                    suggestion="Break down work into more detailed tasks"
                ))
        
        # 验证测试用例数量
        if "min_test_cases" in requirements:
            min_count = requirements["min_test_cases"]
            test_case_patterns = [
                r'测试用例\s*\d+',
                r'test case\s*\d+',
                r'TC\d+'
            ]
            
            actual_count = 0
            for pattern in test_case_patterns:
                actual_count += len(re.findall(pattern, content, re.IGNORECASE))
            
            if actual_count < min_count:
                issues.append(ValidationIssue(
                    level=ValidationResult.WARNING,
                    category="quantity_validation",
                    message=f"Found {actual_count} test cases, minimum required: {min_count}",
                    suggestion="Add more comprehensive test cases"
                ))
        
        return issues
    
    def _validate_output_quality(
        self,
        content: str,
        stage_id: str
    ) -> List[ValidationIssue]:
        """验证输出质量"""
        issues = []
        
        # 检查内容长度
        if len(content.strip()) < 200:
            issues.append(ValidationIssue(
                level=ValidationResult.WARNING,
                category="content_quality",
                message="Output content appears to be too brief",
                suggestion="Provide more detailed content"
            ))
        
        # 检查是否有占位符文本
        placeholder_patterns = [
            r'\[.*?\]',
            r'TODO',
            r'FIXME',
            r'待完成',
            r'待填写'
        ]
        
        for pattern in placeholder_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                issues.append(ValidationIssue(
                    level=ValidationResult.WARNING,
                    category="content_quality",
                    message=f"Found placeholder text: {matches[:3]}",
                    suggestion="Replace placeholder text with actual content"
                ))
                break
        
        # 检查Markdown格式
        if not re.search(r'^#+ ', content, re.MULTILINE):
            issues.append(ValidationIssue(
                level=ValidationResult.WARNING,
                category="format_quality",
                message="No Markdown headers found",
                suggestion="Use proper Markdown formatting with headers"
            ))
        
        return issues
    
    def _generate_validation_report(
        self,
        issues: List[ValidationIssue],
        validation_type: str,
        target: str
    ) -> ValidationReport:
        """生成验证报告"""
        # 计算总体评分
        total_issues = len(issues)
        fail_count = len([i for i in issues if i.level == ValidationResult.FAIL])
        warning_count = len([i for i in issues if i.level == ValidationResult.WARNING])
        
        # 评分逻辑
        base_score = 100.0
        score_deduction = (fail_count * 25) + (warning_count * 10)
        overall_score = max(0.0, base_score - score_deduction)
        
        # 判断是否成功
        success = fail_count == 0 and overall_score >= 70.0
        
        # 生成摘要
        summary = {
            "validation_type": validation_type,
            "target": target,
            "total_issues": total_issues,
            "fail_count": fail_count,
            "warning_count": warning_count,
            "pass_count": 0 if total_issues > 0 else 1
        }
        
        # 生成建议
        recommendations = []
        if fail_count > 0:
            recommendations.append("修复所有失败项以达到质量标准")
        if warning_count > 0:
            recommendations.append("解决警告项以提高输出质量")
        if success:
            recommendations.append("输出质量良好，符合标准")
        
        return ValidationReport(
            success=success,
            overall_score=overall_score,
            issues=issues,
            summary=summary,
            recommendations=recommendations
        )


class ValidationEngine:
    """验证引擎 - 统一的输入输出验证管理"""
    
    def __init__(self, validation_level: ValidationLevel = ValidationLevel.STANDARD):
        """
        初始化验证引擎
        
        Args:
            validation_level: 验证级别
        """
        self.validation_level = validation_level
        self.input_validator = InputValidator(validation_level)
        self.output_validator = OutputValidator(validation_level)
    
    def validate_stage_transition(
        self,
        from_stage: str,
        to_stage: str,
        workspace_dir: Optional[Path] = None
    ) -> ValidationReport:
        """
        验证阶段转换
        
        Args:
            from_stage: 源阶段
            to_stage: 目标阶段
            workspace_dir: 工作空间目录
            
        Returns:
            ValidationReport: 验证报告
        """
        issues = []
        workspace_dir = workspace_dir or Path.cwd()
        
        # 验证源阶段输出
        from_stage_output = workspace_dir / "aceflow_result" / f"{from_stage}.md"
        if from_stage_output.exists():
            output_report = self.output_validator.validate_stage_output(from_stage, from_stage_output)
            if not output_report.success:
                issues.extend(output_report.issues)
        else:
            issues.append(ValidationIssue(
                level=ValidationResult.FAIL,
                category="stage_transition",
                message=f"Source stage {from_stage} output not found",
                suggestion=f"Complete stage {from_stage} before proceeding to {to_stage}"
            ))
        
        # 验证目标阶段输入要求
        input_report = self.input_validator.validate_stage_input(to_stage, {}, workspace_dir)
        if not input_report.success:
            issues.extend(input_report.issues)
        
        return ValidationReport(
            success=len([i for i in issues if i.level == ValidationResult.FAIL]) == 0,
            overall_score=max(0, 100 - len(issues) * 10),
            issues=issues,
            summary={
                "transition": f"{from_stage} -> {to_stage}",
                "validation_type": "stage_transition"
            },
            recommendations=["Fix all issues before proceeding with stage transition"] if issues else ["Stage transition validated successfully"]
        )
    
    def generate_quality_report(
        self,
        project_dir: Optional[Path] = None
    ) -> Dict[str, Any]:
        """
        生成项目质量报告
        
        Args:
            project_dir: 项目目录
            
        Returns:
            Dict: 质量报告
        """
        project_dir = project_dir or Path.cwd()
        aceflow_result_dir = project_dir / "aceflow_result"
        
        if not aceflow_result_dir.exists():
            return {
                "success": False,
                "error": "No aceflow_result directory found",
                "message": "Project has not been initialized or no stages completed"
            }
        
        stage_reports = {}
        overall_issues = []
        total_score = 0
        stage_count = 0
        
        # 验证所有阶段输出
        for output_file in aceflow_result_dir.glob("S*_*.md"):
            stage_id = output_file.stem
            report = self.output_validator.validate_stage_output(stage_id, output_file)
            
            stage_reports[stage_id] = {
                "success": report.success,
                "score": report.overall_score,
                "issues": len(report.issues),
                "recommendations": report.recommendations
            }
            
            overall_issues.extend(report.issues)
            total_score += report.overall_score
            stage_count += 1
        
        # 计算总体质量评分
        average_score = total_score / stage_count if stage_count > 0 else 0
        
        return {
            "success": True,
            "overall_quality_score": average_score,
            "total_stages_validated": stage_count,
            "total_issues": len(overall_issues),
            "stage_reports": stage_reports,
            "quality_level": self._get_quality_level(average_score),
            "recommendations": self._generate_overall_recommendations(overall_issues, average_score),
            "timestamp": datetime.now().isoformat()
        }
    
    def _get_quality_level(self, score: float) -> str:
        """获取质量等级"""
        if score >= 90:
            return "Excellent"
        elif score >= 80:
            return "Good"
        elif score >= 70:
            return "Acceptable"
        elif score >= 60:
            return "Needs Improvement"
        else:
            return "Poor"
    
    def _generate_overall_recommendations(
        self,
        issues: List[ValidationIssue],
        average_score: float
    ) -> List[str]:
        """生成总体建议"""
        recommendations = []
        
        fail_count = len([i for i in issues if i.level == ValidationResult.FAIL])
        warning_count = len([i for i in issues if i.level == ValidationResult.WARNING])
        
        if fail_count > 0:
            recommendations.append(f"修复 {fail_count} 个严重问题")
        
        if warning_count > 0:
            recommendations.append(f"解决 {warning_count} 个警告问题")
        
        if average_score < 70:
            recommendations.append("整体质量需要改进，建议重新审查所有阶段输出")
        elif average_score >= 90:
            recommendations.append("质量优秀，继续保持高标准")
        
        return recommendations


# 工厂函数
def create_validation_engine(validation_level: ValidationLevel = ValidationLevel.STANDARD) -> ValidationEngine:
    """创建验证引擎实例"""
    return ValidationEngine(validation_level)


# 便捷函数
def validate_stage_input(stage_id: str, input_data: Dict[str, Any]) -> ValidationReport:
    """便捷的阶段输入验证函数"""
    validator = InputValidator()
    return validator.validate_stage_input(stage_id, input_data)


def validate_stage_output(stage_id: str, output_path: Path) -> ValidationReport:
    """便捷的阶段输出验证函数"""
    validator = OutputValidator()
    return validator.validate_stage_output(stage_id, output_path)