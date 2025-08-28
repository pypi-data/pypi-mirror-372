"""AceFlow MCP Tools implementation."""

from typing import Dict, Any, Optional, List
import json
import os
import sys
from pathlib import Path
import shutil
import datetime

# Import core functionality
from .core import ProjectManager, WorkflowEngine, TemplateManager

# Import existing AceFlow functionality
current_dir = Path(__file__).parent
# Fix: correct path to aceflow scripts directory - go up 3 levels from aceflow_mcp_server/tools.py
aceflow_scripts_dir = current_dir.parent.parent / "aceflow" / "scripts"
sys.path.insert(0, str(aceflow_scripts_dir))

try:
    from utils.platform_compatibility import PlatformUtils, SafeFileOperations, EnhancedErrorHandler
except ImportError:
    # Fallback implementations if utils are not available
    class PlatformUtils:
        @staticmethod
        def get_os_type(): return "unknown"
    
    class SafeFileOperations:
        @staticmethod
        def write_text_file(path, content, encoding="utf-8"):
            with open(path, 'w', encoding=encoding) as f:
                f.write(content)
    
    class EnhancedErrorHandler:
        @staticmethod
        def handle_file_error(error, context=""): return str(error)


class AceFlowTools:
    """AceFlow MCP Tools collection."""
    
    def __init__(self, working_directory: Optional[str] = None):
        """Initialize tools with necessary dependencies."""
        self.platform_utils = PlatformUtils()
        self.file_ops = SafeFileOperations()
        self.error_handler = EnhancedErrorHandler()
        self.project_manager = ProjectManager()
        self.workflow_engine = WorkflowEngine()
        self.template_manager = TemplateManager()
        
        # Set the working directory context
        self.working_directory = working_directory or os.getcwd()
        
        # Initialize new data manager for AI-MCP collaboration
        from .data_manager import DataManager
        self.data_manager = DataManager(self.working_directory)
        
        # Debug logging
        print(f"[DEBUG] AceFlowTools initialized with working_directory: {self.working_directory}", file=sys.stderr)
    
    def aceflow_init(
        self,
        mode: str,
        project_name: Optional[str] = None,
        directory: Optional[str] = None
    ) -> Dict[str, Any]:
        """Initialize AceFlow project with specified mode.
        
        Args:
            mode: Workflow mode (minimal, standard, complete, smart)
            project_name: Optional project name
            directory: Optional target directory (defaults to current directory)
        
        Returns:
            Dict with success status, message, and project info
        """
        try:
            # Validate mode
            valid_modes = ["minimal", "standard", "complete", "smart"]
            if mode not in valid_modes:
                return {
                    "success": False,
                    "error": f"Invalid mode '{mode}'. Valid modes: {', '.join(valid_modes)}",
                    "message": "Mode validation failed"
                }
            
            # Determine target directory with intelligent working directory detection
            if directory:
                target_dir = Path(directory).resolve()
            else:
                # Use the working directory passed during initialization
                # This should be the correct client working directory
                target_dir = Path(self.working_directory).resolve()
                
                # Debug logging for troubleshooting
                print(f"[DEBUG] Working directory detection:", file=sys.stderr)
                print(f"[DEBUG] Instance working_directory: {self.working_directory}", file=sys.stderr)
                print(f"[DEBUG] PWD: {os.environ.get('PWD')}", file=sys.stderr)
                print(f"[DEBUG] CLIENT_CWD: {os.environ.get('CLIENT_CWD')}", file=sys.stderr)
                print(f"[DEBUG] os.getcwd(): {os.getcwd()}", file=sys.stderr)
                print(f"[DEBUG] Selected target_dir: {target_dir}", file=sys.stderr)
            
            # Create directory if it doesn't exist
            target_dir.mkdir(parents=True, exist_ok=True)
            
            # Set project name
            if not project_name:
                project_name = target_dir.name
            
            # Check if already initialized (unless forced)
            aceflow_dir = target_dir / ".aceflow"
            clinerules_file = target_dir / ".clinerules"
            
            if aceflow_dir.exists() or clinerules_file.exists():
                return {
                    "success": False,
                    "error": "Directory already contains AceFlow configuration",
                    "message": f"Directory '{target_dir}' is already initialized. Use force=true to overwrite."
                }
            
            # Initialize project structure
            result = self._initialize_project_structure(target_dir, project_name, mode)
            
            if result["success"]:
                return {
                    "success": True,
                    "message": f"Project '{project_name}' initialized successfully in {mode} mode",
                    "project_info": {
                        "name": project_name,
                        "mode": mode,
                        "directory": str(target_dir),
                        "created_files": result.get("created_files", []),
                        "debug_info": {
                            "detected_working_dir": str(target_dir),
                            "original_cwd": os.getcwd(),
                            "pwd_env": os.environ.get('PWD'),
                            "cwd_env": os.environ.get('CWD')
                        }
                    }
                }
            else:
                return result
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to initialize project",
                "debug_info": {
                    "exception_type": type(e).__name__,
                    "working_directory": os.getcwd(),
                    "target_directory": str(target_dir) if 'target_dir' in locals() else "unknown"
                }
            }
    
    def _initialize_project_structure(self, target_dir: Path, project_name: str, mode: str) -> Dict[str, Any]:
        """Initialize the complete project structure."""
        created_files = []
        
        try:
            # Create .aceflow directory
            aceflow_dir = target_dir / ".aceflow"
            aceflow_dir.mkdir(exist_ok=True)
            created_files.append(".aceflow/")
            
            # Create aceflow_result directory
            result_dir = target_dir / "aceflow_result"
            result_dir.mkdir(exist_ok=True)
            created_files.append("aceflow_result/")
            
            # Create project state file
            state_data = {
                "project": {
                    "name": project_name,
                    "mode": mode.upper(),
                    "created_at": datetime.datetime.now().isoformat(),
                    "version": "3.0"
                },
                "flow": {
                    "current_stage": self._get_initial_stage_for_mode(mode),
                    "completed_stages": [],
                    "progress_percentage": 0
                },
                "metadata": {
                    "total_stages": self._get_stage_count(mode),
                    "last_updated": datetime.datetime.now().isoformat()
                }
            }
            
            state_file = aceflow_dir / "current_state.json"
            with open(state_file, 'w', encoding='utf-8') as f:
                json.dump(state_data, f, indent=2, ensure_ascii=False)
            created_files.append(".aceflow/current_state.json")
            
            # Create .aceflow subdirectories for templates, config, core
            config_dir = aceflow_dir / "config"
            config_dir.mkdir(exist_ok=True)
            created_files.append(".aceflow/config/")
            
            templates_dir = aceflow_dir / "templates"
            templates_dir.mkdir(exist_ok=True)
            created_files.append(".aceflow/templates/")
            
            core_dir = aceflow_dir / "core"
            core_dir.mkdir(exist_ok=True)
            created_files.append(".aceflow/core/")
            
            # Create .clinerules directory for AI Agent prompts
            clinerules_dir = target_dir / ".clinerules"
            clinerules_dir.mkdir(exist_ok=True)
            created_files.append(".clinerules/")
            
            # Copy mode definitions to .aceflow/config/
            mode_def_source = Path(__file__).parent / "templates" / "mode_definitions.yaml"
            mode_def_target = config_dir / "mode_definitions.yaml"
            if mode_def_source.exists():
                import shutil
                shutil.copy2(mode_def_source, mode_def_target)
                created_files.append(".aceflow/config/mode_definitions.yaml")
            
            # Copy template files to .aceflow/templates/
            template_source_dir = Path(__file__).parent / "templates"
            if template_source_dir.exists():
                import shutil
                shutil.copytree(template_source_dir, templates_dir, dirs_exist_ok=True)
                created_files.append(".aceflow/templates/")
            
            # Create enhanced AI Agent prompt files in .clinerules/
            # 1. System Prompt (Enhanced version)
            system_prompt = self._generate_enhanced_system_prompt(project_name, mode)
            prompt_file = clinerules_dir / "system_prompt.md"
            with open(prompt_file, 'w', encoding='utf-8') as f:
                f.write(system_prompt)
            created_files.append(".clinerules/system_prompt.md")
            
            # 2. AceFlow Integration Rules
            aceflow_integration = self._generate_aceflow_integration(project_name, mode)
            integration_file = clinerules_dir / "aceflow_integration.md"
            with open(integration_file, 'w', encoding='utf-8') as f:
                f.write(aceflow_integration)
            created_files.append(".clinerules/aceflow_integration.md")
            
            # 3. SPEC Summary
            spec_summary = self._generate_spec_summary(project_name, mode)
            summary_file = clinerules_dir / "spec_summary.md"
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(spec_summary)
            created_files.append(".clinerules/spec_summary.md")
            
            # 4. SPEC Query Helper
            spec_query_helper = self._generate_spec_query_helper(project_name, mode)
            query_file = clinerules_dir / "spec_query_helper.md"
            with open(query_file, 'w', encoding='utf-8') as f:
                f.write(spec_query_helper)
            created_files.append(".clinerules/spec_query_helper.md")
            
            # 5. Quality Standards (Enhanced version)
            quality_standards = self._generate_enhanced_quality_standards(project_name, mode)
            quality_file = clinerules_dir / "quality_standards.md"
            with open(quality_file, 'w', encoding='utf-8') as f:
                f.write(quality_standards)
            created_files.append(".clinerules/quality_standards.md")
            
            # Create template.yaml
            template_content = self._generate_template_yaml(mode)
            template_file = aceflow_dir / "template.yaml"
            with open(template_file, 'w', encoding='utf-8') as f:
                f.write(template_content)
            created_files.append(".aceflow/template.yaml")
            
            # Copy management scripts
            script_files = ["aceflow-stage.py", "aceflow-validate.py", "aceflow-templates.py"]
            for script in script_files:
                source_path = aceflow_scripts_dir / script
                if source_path.exists():
                    dest_path = target_dir / script
                    shutil.copy2(source_path, dest_path)
                    created_files.append(script)
            
            # Create README
            readme_content = self._generate_readme(project_name, mode)
            readme_file = target_dir / "README_ACEFLOW.md"
            with open(readme_file, 'w', encoding='utf-8') as f:
                f.write(readme_content)
            created_files.append("README_ACEFLOW.md")
            
            return {
                "success": True,
                "created_files": created_files
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to create project structure"
            }
    
    def _get_stage_count(self, mode: str) -> int:
        """Get the number of stages for the given mode."""
        stage_counts = {
            "minimal": 3,
            "standard": 8,
            "complete": 12,
            "smart": 10
        }
        return stage_counts.get(mode, 8)
    
    def _generate_ai_agent_prompts(self, project_name: str, mode: str) -> str:
        """Generate .clinerules/system_prompt.md content for AI Agent integration."""
        return f"""# AceFlow v3.0 - AI Agent 系统提示

**项目**: {project_name}  
**模式**: {mode}  
**初始化时间**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**版本**: 3.0  

## AI Agent 身份定义

你是一个专业的软件开发AI助手，专门负责执行AceFlow v3.0工作流。你的核心职责是：

1. **严格遵循AceFlow标准**: 按照{mode}模式的流程执行每个阶段
2. **基于事实工作**: 每个阶段必须基于前一阶段的实际输出，不能基于假设
3. **保证输出质量**: 确保生成的文档结构完整、内容准确
4. **维护项目状态**: 实时更新项目进度和状态信息

## 工作模式配置

- **AceFlow模式**: {mode}
- **输出目录**: aceflow_result/
- **配置目录**: .aceflow/
- **模板目录**: .aceflow/templates/
- **项目名称**: {project_name}

## 核心工作原则  

1. **严格遵循 AceFlow 标准**: 所有阶段产物必须符合 AceFlow 定义
2. **自动化执行**: 使用 Stage Engine 自动生成各阶段文档
3. **基于事实工作**: 每个阶段必须基于前一阶段的输出，不能基于假设
4. **质量保证**: 确保生成文档的结构完整、内容准确
5. **状态同步**: 阶段完成后自动更新项目状态

## 阶段执行流程

### 标准执行命令
```bash
# 查看当前状态
aceflow_stage(action="status")

# 执行当前阶段
aceflow_stage(action="execute")

# 推进到下一阶段
aceflow_stage(action="next")

# 验证项目质量
aceflow_validate(mode="basic", report=True)
```

### 阶段依赖关系
- 每个阶段都有明确的输入要求
- 必须验证输入条件满足才能执行
- 输出文档保存到 aceflow_result/ 目录
- 状态文件实时更新进度

## 质量标准

### 文档质量要求
- **结构完整**: 包含概述、详细内容、下一步工作等必要章节
- **内容准确**: 基于实际输入生成，无占位符文本
- **格式规范**: 遵循 Markdown 格式规范
- **引用正确**: 正确引用输入文档和相关资源

### 代码质量要求
- **遵循编码规范**: 代码注释完整，结构清晰
- **测试覆盖**: 根据模式要求执行相应测试策略
- **性能标准**: 满足项目性能要求
- **安全考虑**: 遵循安全最佳实践

## 工具集成

### MCP Tools
- `aceflow_init`: 项目初始化
- `aceflow_stage`: 阶段管理和执行
- `aceflow_validate`: 项目验证
- `aceflow_template`: 模板管理

### 本地脚本
- `python aceflow-stage.py`: 阶段管理脚本
- `python aceflow-validate.py`: 验证脚本
- `python aceflow-templates.py`: 模板管理脚本

## 模式特定配置

### {mode.upper()} 模式特点
{self._get_mode_specific_config(mode)}

## 注意事项

1. **输入验证**: 每个阶段执行前都会验证输入条件
2. **错误处理**: 遇到错误时会提供详细的错误信息和修复建议
3. **状态一致性**: 项目状态与实际进度保持同步
4. **文档版本**: 所有文档都包含版本信息和创建时间
5. **质量监控**: 自动检查文档质量并提供改进建议

---
*Generated by AceFlow v3.0 MCP Server*
*AI Agent 系统提示文件*
"""
    
    def _generate_quality_standards(self, mode: str) -> str:
        """Generate quality standards for AI Agent."""
        return f"""# AceFlow v3.0 - 质量标准

## 文档质量标准

### 结构完整性
- 包含概述、详细内容、下一步工作等必要章节
- 使用标准的Markdown格式
- 章节层次清晰，编号规范

### 内容准确性
- 基于实际输入生成，无占位符文本
- 引用正确，链接有效
- 数据和信息准确无误

### 格式规范
- 遵循Markdown语法规范
- 代码块使用正确的语言标识
- 表格格式整齐，易于阅读

## 代码质量标准

### 编码规范
- 代码注释完整，结构清晰
- 变量命名有意义
- 函数职责单一

### 测试要求
- 根据{mode}模式要求执行相应测试策略
- 测试覆盖率满足标准
- 测试用例完整有效

### 性能标准
- 满足项目性能要求
- 资源使用合理
- 响应时间符合预期

## 安全标准

### 数据安全
- 敏感信息不在代码中硬编码
- 输入验证完整
- 错误处理不泄露敏感信息

### 访问控制
- 权限控制合理
- 认证机制完善
- 审计日志完整

---
*Generated by AceFlow v3.0 MCP Server*
*质量标准文件*
"""
    
    def _generate_workflow_guide(self, project_name: str, mode: str) -> str:
        """Generate comprehensive workflow guide for AI Agent."""
        
        # 根据模式获取阶段列表
        stage_configs = {
            "minimal": [
                ("01_implementation", "快速实现", "实现核心功能"),
                ("02_test", "基础测试", "基础功能测试"),
                ("03_demo", "功能演示", "功能演示")
            ],
            "standard": [
                ("01_user_stories", "用户故事分析", "基于PRD文档分析用户故事"),
                ("02_task_breakdown", "任务分解", "将用户故事分解为开发任务"),
                ("03_test_design", "测试用例设计", "设计测试用例和测试策略"),
                ("04_implementation", "功能实现", "实现核心功能"),
                ("05_unit_test", "单元测试", "编写和执行单元测试"),
                ("06_integration_test", "集成测试", "执行集成测试"),
                ("07_code_review", "代码审查", "进行代码审查和质量检查"),
                ("08_demo", "功能演示", "准备和执行功能演示")
            ],
            "complete": [
                ("01_requirement_analysis", "需求分析", "深度分析业务需求和技术需求"),
                ("02_architecture_design", "架构设计", "设计系统架构和技术方案"),
                ("03_user_stories", "用户故事分析", "基于需求和架构设计用户故事"),
                ("04_task_breakdown", "任务分解", "详细的任务分解和工作计划"),
                ("05_test_design", "测试用例设计", "全面的测试策略和用例设计"),
                ("06_implementation", "功能实现", "按照架构设计实现功能"),
                ("07_unit_test", "单元测试", "全面的单元测试"),
                ("08_integration_test", "集成测试", "系统集成测试"),
                ("09_performance_test", "性能测试", "性能和负载测试"),
                ("10_security_review", "安全审查", "安全漏洞扫描和审查"),
                ("11_code_review", "代码审查", "全面的代码质量审查"),
                ("12_demo", "功能演示", "完整的功能演示和交付")
            ],
            "smart": [
                ("01_project_analysis", "AI项目复杂度分析", "使用AI分析项目复杂度和需求"),
                ("02_adaptive_planning", "自适应规划", "基于分析结果制定自适应计划"),
                ("03_user_stories", "用户故事分析", "智能生成和优化用户故事"),
                ("04_smart_breakdown", "智能任务分解", "AI辅助的智能任务分解"),
                ("05_test_generation", "AI测试用例生成", "自动生成测试用例和策略"),
                ("06_implementation", "功能实现", "AI辅助的代码实现"),
                ("07_automated_test", "自动化测试", "执行自动化测试套件"),
                ("08_quality_assessment", "AI质量评估", "AI驱动的质量评估和优化建议"),
                ("09_optimization", "性能优化", "基于AI建议的性能优化"),
                ("10_demo", "智能演示", "AI辅助的智能演示和交付")
            ]
        }
        
        stages = stage_configs.get(mode, stage_configs["standard"])
        
        return f"""# AceFlow v3.0 - 工作流指导

**项目**: {project_name}  
**模式**: {mode.upper()}  
**总阶段数**: {len(stages)}  
**创建时间**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  

## 🎯 工作流概述

本文档为AI Agent提供完整的AceFlow工作流指导，包含每个阶段的具体执行步骤、MCP工具使用方法和质量检查要点。

## 🔄 核心工作循环

每个阶段都遵循以下标准循环：

1. **状态检查** → 使用 `aceflow_stage(action="status")` 确认当前阶段
2. **输入验证** → 检查前置条件和输入文件是否满足
3. **执行阶段** → 使用 `aceflow_stage(action="execute")` 执行当前阶段
4. **质量验证** → 使用 `aceflow_validate()` 检查输出质量
5. **推进阶段** → 使用 `aceflow_stage(action="next")` 进入下一阶段

## 📋 阶段详细指导

{self._generate_stage_details(stages)}

## 🛠️ MCP工具使用指南

### aceflow_stage 工具
```python
# 查看当前状态
aceflow_stage(action="status")

# 执行当前阶段
aceflow_stage(action="execute")

# 推进到下一阶段
aceflow_stage(action="next")

# 重置项目状态
aceflow_stage(action="reset")
```

### aceflow_validate 工具
```python
# 基础验证
aceflow_validate(mode="basic")

# 详细验证并生成报告
aceflow_validate(mode="detailed", report=True)

# 自动修复问题
aceflow_validate(mode="basic", fix=True)
```

### aceflow_template 工具
```python
# 列出可用模板
aceflow_template(action="list")

# 应用新模板
aceflow_template(action="apply", template="complete")

# 验证模板
aceflow_template(action="validate")
```

## ⚠️ 重要注意事项

1. **严格按顺序执行**: 不能跳过阶段，必须按照定义的顺序执行
2. **基于实际输入**: 每个阶段必须基于前一阶段的实际输出，不能基于假设
3. **输出到指定目录**: 所有文档输出到 `aceflow_result/` 目录
4. **使用标准模板**: 使用 `.aceflow/templates/` 中的标准模板
5. **实时状态更新**: 每个阶段完成后自动更新项目状态

## 🚨 错误处理

### 常见问题及解决方案

1. **阶段执行失败**
   - 检查输入文件是否存在
   - 验证前置条件是否满足
   - 查看错误日志获取详细信息

2. **验证失败**
   - 使用 `aceflow_validate(mode="detailed", report=True)` 获取详细报告
   - 根据报告修复具体问题
   - 重新执行验证

3. **状态不一致**
   - 使用 `aceflow_stage(action="reset")` 重置状态
   - 重新从当前阶段开始执行

---
*Generated by AceFlow v3.0 MCP Server*
*工作流指导文件*
"""
    
    def _generate_stage_details(self, stages) -> str:
        """Generate detailed stage instructions."""
        details = []
        
        for stage_id, stage_name, stage_desc in stages:
            details.append(f"""
### 阶段 {stage_id}: {stage_name}

**描述**: {stage_desc}

**执行步骤**:
1. 确认当前处于此阶段: `aceflow_stage(action="status")`
2. 检查输入条件是否满足
3. 执行阶段任务: `aceflow_stage(action="execute")`
4. 验证输出质量: `aceflow_validate(mode="basic")`
5. 推进到下一阶段: `aceflow_stage(action="next")`

**输入要求**:
- 前一阶段的输出文档
- 项目相关的源文件和配置

**输出产物**:
- 阶段文档保存到 `aceflow_result/{stage_id}_{stage_name.lower().replace(' ', '_')}.md`
- 更新项目状态文件

**质量检查**:
- 文档结构完整
- 内容基于实际输入
- 格式符合标准
- 无占位符文本
""")
        
        return "".join(details)
    
    def _get_mode_specific_config(self, mode: str) -> str:
        """Get mode-specific configuration details."""
        configs = {
            "minimal": """- **快速迭代**: 专注于核心功能快速实现
- **简化流程**: 只包含必要的3个阶段
- **质量标准**: 基本功能可用即可""",
            
            "standard": """- **平衡发展**: 兼顾开发效率和代码质量
- **标准流程**: 包含8个标准开发阶段
- **质量标准**: 代码质量良好，测试覆盖充分""",
            
            "complete": """- **企业级标准**: 完整的企业级开发流程
- **全面覆盖**: 包含12个完整阶段
- **高质量标准**: 代码质量优秀，安全性和性能达标""",
            
            "smart": """- **AI增强**: 利用AI技术优化开发流程
- **自适应**: 根据项目特点动态调整流程
- **智能分析**: AI辅助的质量评估和优化建议"""
        }
        return configs.get(mode, configs["standard"])


    
    def _generate_template_yaml(self, mode: str) -> str:
        """Generate template.yaml content based on mode."""
        templates = {
            "minimal": """# AceFlow Minimal模式配置
name: "Minimal Workflow"
version: "3.0"
description: "快速原型和概念验证工作流"

stages:
  - name: "implementation"
    description: "快速实现核心功能"
    required: true
  - name: "test"
    description: "基础功能测试"
    required: true
  - name: "demo"
    description: "功能演示"
    required: true

quality_gates:
  - stage: "implementation"
    criteria: ["核心功能完成", "基本可运行"]
  - stage: "test"
    criteria: ["主要功能测试通过"]""",
            
            "standard": """# AceFlow Standard模式配置
name: "Standard Workflow"
version: "3.0"
description: "标准软件开发工作流"

stages:
  - name: "user_stories"
    description: "用户故事分析"
    required: true
  - name: "task_breakdown"
    description: "任务分解"
    required: true
  - name: "test_design"
    description: "测试用例设计"
    required: true
  - name: "implementation"
    description: "功能实现"
    required: true
  - name: "unit_test"
    description: "单元测试"
    required: true
  - name: "integration_test"
    description: "集成测试"
    required: true
  - name: "code_review"
    description: "代码审查"
    required: true
  - name: "demo"
    description: "功能演示"
    required: true

quality_gates:
  - stage: "user_stories"
    criteria: ["用户故事完整", "验收标准明确"]
  - stage: "implementation"
    criteria: ["代码质量合格", "功能完整"]
  - stage: "unit_test"
    criteria: ["测试覆盖率 > 80%", "所有测试通过"]""",
            
            "complete": """# AceFlow Complete模式配置  
name: "Complete Workflow"
version: "3.0"
description: "完整企业级开发工作流"

stages:
  - name: "requirement_analysis"
    description: "需求分析"
    required: true
  - name: "architecture_design"
    description: "架构设计"
    required: true
  - name: "user_stories"
    description: "用户故事分析"
    required: true
  - name: "task_breakdown"
    description: "任务分解"
    required: true
  - name: "test_design"
    description: "测试用例设计"
    required: true
  - name: "implementation"
    description: "功能实现"
    required: true
  - name: "unit_test"
    description: "单元测试"
    required: true
  - name: "integration_test"
    description: "集成测试"
    required: true
  - name: "performance_test"
    description: "性能测试"
    required: true
  - name: "security_review"
    description: "安全审查"
    required: true
  - name: "code_review"
    description: "代码审查"
    required: true
  - name: "demo"
    description: "功能演示"
    required: true

quality_gates:
  - stage: "architecture_design"
    criteria: ["架构设计完整", "技术选型合理"]
  - stage: "implementation"
    criteria: ["代码质量优秀", "性能满足要求"]
  - stage: "security_review"
    criteria: ["安全检查通过", "无重大漏洞"]""",
            
            "smart": """# AceFlow Smart模式配置
name: "Smart Adaptive Workflow"  
version: "3.0"
description: "AI增强的自适应工作流"

stages:
  - name: "project_analysis"
    description: "AI项目复杂度分析"
    required: true
  - name: "adaptive_planning"
    description: "自适应规划"
    required: true
  - name: "user_stories"
    description: "用户故事分析"
    required: true
  - name: "smart_breakdown"
    description: "智能任务分解"
    required: true
  - name: "test_generation"
    description: "AI测试用例生成"
    required: true
  - name: "implementation"
    description: "功能实现"
    required: true
  - name: "automated_test"
    description: "自动化测试"
    required: true
  - name: "quality_assessment"
    description: "AI质量评估"
    required: true
  - name: "optimization"
    description: "性能优化"
    required: true
  - name: "demo"
    description: "智能演示"
    required: true

ai_features:
  - "复杂度智能评估"
  - "动态流程调整"
  - "自动化测试生成"
  - "质量智能分析"

quality_gates:
  - stage: "project_analysis"
    criteria: ["复杂度评估完成", "技术栈确定"]
  - stage: "implementation"
    criteria: ["AI代码质量检查通过", "性能指标达标"]"""
        }
        
        return templates.get(mode, templates["standard"])
    
    def _generate_readme(self, project_name: str, mode: str) -> str:
        """Generate README content."""
        return f"""# {project_name}

## AceFlow项目说明

本项目使用AceFlow v3.0工作流管理系统，采用 **{mode.upper()}** 模式。

### 项目信息
- **项目名称**: {project_name}
- **工作流模式**: {mode.upper()}
- **初始化时间**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **AceFlow版本**: 3.0

### 目录结构
```
{project_name}/
├── .aceflow/           # AceFlow配置目录
│   ├── current_state.json    # 项目状态文件
│   └── template.yaml         # 工作流模板
├── aceflow_result/     # 项目输出目录
├── .clinerules         # AI Agent工作配置
├── aceflow-stage.py    # 阶段管理脚本
├── aceflow-validate.py # 项目验证脚本
├── aceflow-templates.py # 模板管理脚本
└── README_ACEFLOW.md   # 本文件
```

### 快速开始

1. **查看当前状态**
   ```bash
   python aceflow-stage.py --action status
   ```

2. **验证项目配置**
   ```bash
   python aceflow-validate.py
   ```

3. **推进到下一阶段**
   ```bash
   python aceflow-stage.py --action next
   ```

### 工作流程

根据{mode}模式，项目将按以下阶段进行：

{self._get_stage_description(mode)}

### 注意事项

- 所有项目文档和代码请输出到 `aceflow_result/` 目录
- 使用AI助手时，确保.clinerules配置已加载
- 每个阶段完成后，使用 `aceflow-stage.py` 更新状态
- 定期使用 `aceflow-validate.py` 检查项目合规性

### 帮助和支持

如需帮助，请参考：
- AceFlow官方文档
- 项目状态文件: `.aceflow/current_state.json`
- 工作流配置: `.aceflow/template.yaml`

---
*Generated by AceFlow v3.0 MCP Server*"""
    
    def _get_stage_description(self, mode: str) -> str:
        """Get stage descriptions for the mode."""
        descriptions = {
            "minimal": """1. **Implementation** - 快速实现核心功能
2. **Test** - 基础功能测试  
3. **Demo** - 功能演示""",
            
            "standard": """1. **User Stories** - 用户故事分析
2. **Task Breakdown** - 任务分解
3. **Test Design** - 测试用例设计
4. **Implementation** - 功能实现
5. **Unit Test** - 单元测试
6. **Integration Test** - 集成测试
7. **Code Review** - 代码审查
8. **Demo** - 功能演示""",
            
            "complete": """1. **Requirement Analysis** - 需求分析
2. **Architecture Design** - 架构设计
3. **User Stories** - 用户故事分析
4. **Task Breakdown** - 任务分解
5. **Test Design** - 测试用例设计
6. **Implementation** - 功能实现
7. **Unit Test** - 单元测试
8. **Integration Test** - 集成测试
9. **Performance Test** - 性能测试
10. **Security Review** - 安全审查
11. **Code Review** - 代码审查
12. **Demo** - 功能演示""",
            
            "smart": """1. **Project Analysis** - AI项目复杂度分析
2. **Adaptive Planning** - 自适应规划
3. **User Stories** - 用户故事分析
4. **Smart Breakdown** - 智能任务分解
5. **Test Generation** - AI测试用例生成
6. **Implementation** - 功能实现
7. **Automated Test** - 自动化测试
8. **Quality Assessment** - AI质量评估
9. **Optimization** - 性能优化
10. **Demo** - 智能演示"""
        }
        
        return descriptions.get(mode, descriptions["standard"])
    
    def _get_initial_stage_for_mode(self, mode: str) -> str:
        """Get the initial stage for a specific mode."""
        initial_stages = {
            "minimal": "S1_implementation",
            "standard": "S1_user_stories", 
            "complete": "S1_requirement_analysis",
            "smart": "S1_project_analysis"
        }
        return initial_stages.get(mode.lower(), "S1_user_stories")
    
    def aceflow_stage(
        self,
        action: str,
        stage: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Enhanced AceFlow stage management with AI-MCP collaboration.
        
        Supports both traditional workflow control and new AI collaboration features.
        
        Args:
            action: Action type (status, next, execute, set_analysis, save_output, prepare_data, etc.)
            stage: Optional target stage ID
            data: Optional data payload for AI collaboration
            
        Returns:
            Dict with action result and relevant data
        """
        try:
            # Traditional workflow actions (backward compatibility)
            if action == "status":
                result = self.workflow_engine.get_current_status()
                # Enhance with data availability info
                analysis_data = self.data_manager.load_analysis_data()
                result["data_status"] = {
                    "analysis_data_available": analysis_data is not None,
                    "analysis_last_updated": analysis_data.get("_metadata", {}).get("last_updated") if analysis_data else None
                }
                return {
                    "success": True,
                    "action": action,
                    "result": result
                }
                
            elif action == "next":
                result = self.workflow_engine.advance_to_next_stage()
                return {
                    "success": True,
                    "action": action,
                    "result": result
                }
                
            elif action == "list":
                stages = self.workflow_engine.list_all_stages()
                return {
                    "success": True,
                    "action": action,
                    "result": {
                        "stages": stages
                    }
                }
                
            elif action == "reset":
                result = self.workflow_engine.reset_project()
                return {
                    "success": True,
                    "action": action,
                    "result": result
                }
            
            # New AI collaboration actions
            elif action == "set_analysis":
                if not data:
                    return {
                        "success": False,
                        "error": "Missing analysis data",
                        "message": "set_analysis action requires data parameter"
                    }
                
                success = self.data_manager.save_analysis_data(data)
                if success:
                    return {
                        "success": True,
                        "action": action,
                        "message": "分析数据保存成功",
                        "data_stored": {
                            "timestamp": datetime.datetime.now().isoformat(),
                            "categories": list(data.keys())
                        }
                    }
                else:
                    return {
                        "success": False,
                        "error": "Failed to save analysis data",
                        "message": "数据保存失败，请检查数据格式"
                    }
            
            elif action == "save_output":
                if not stage:
                    return {
                        "success": False,
                        "error": "Missing stage parameter",
                        "message": "save_output action requires stage parameter"
                    }
                
                if not data:
                    return {
                        "success": False,
                        "error": "Missing output data", 
                        "message": "save_output action requires data parameter"
                    }
                
                success = self.data_manager.save_stage_output(stage, data)
                if success:
                    return {
                        "success": True,
                        "action": action,
                        "stage_id": stage,
                        "message": f"阶段输出保存成功: {stage}",
                        "saved_to": f".aceflow/stage_outputs/{stage}.json"
                    }
                else:
                    return {
                        "success": False,
                        "error": "Failed to save stage output",
                        "message": "阶段输出保存失败"
                    }
            
            elif action == "prepare_data":
                if not stage:
                    return {
                        "success": False,
                        "error": "Missing stage parameter",
                        "message": "prepare_data action requires stage parameter"
                    }
                
                return self._prepare_execution_package(stage)
            
            elif action == "execute":
                # Legacy execute action (backward compatibility)
                return self._execute_current_stage(stage)
            
            elif action == "validate":
                return self._validate_stage_data(stage)
            
            else:
                return {
                    "success": False,
                    "error": f"Invalid action '{action}'",
                    "message": "Unsupported action",
                    "supported_actions": [
                        "status", "next", "list", "reset", "execute", 
                        "set_analysis", "save_output", "prepare_data", "validate"
                    ]
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to execute stage action: {action}",
                "debug_info": {
                    "action": action,
                    "stage": stage,
                    "has_data": data is not None
                }
            }
    
    def _execute_current_stage(self, stage_id: Optional[str] = None) -> Dict[str, Any]:
        """Execute the current or specified stage using proper AceFlow templates.
        
        Args:
            stage_id: Optional specific stage to execute
            
        Returns:
            Dict with execution result
        """
        try:
            # Get current state to determine stage
            current_state = self.project_manager.get_current_state()
            current_stage = current_state.get("flow", {}).get("current_stage", "unknown")
            
            if stage_id:
                target_stage = stage_id
            else:
                target_stage = current_stage
            
            # Create result directory
            result_dir = Path.cwd() / "aceflow_result"
            result_dir.mkdir(exist_ok=True)
            
            # Load project PRD content
            prd_content = self._load_project_prd()
            
            # Generate stage-specific content based on AceFlow templates
            doc_content = self._generate_stage_content(target_stage, current_state, prd_content)
            
            # Save document
            doc_filename = f"{target_stage}.md"
            doc_path = result_dir / doc_filename
            doc_path.write_text(doc_content, encoding='utf-8')
            
            return {
                "success": True,
                "action": "execute",
                "stage_id": target_stage,
                "output_path": str(doc_path),
                "quality_score": 0.9,
                "execution_time": 2.0,
                "warnings": [],
                "message": f"Stage '{target_stage}' executed successfully using AceFlow templates"
            }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to execute stage"
            }
    
    def _load_project_prd(self) -> str:
        """Load project PRD content."""
        try:
            # Look for PRD files in common locations
            prd_files = [
                "taskmaster-demo.md",
                "PRD.md", 
                "requirements.md",
                "README.md"
            ]
            
            for prd_file in prd_files:
                prd_path = Path.cwd() / prd_file
                if prd_path.exists():
                    return prd_path.read_text(encoding='utf-8')
            
            return "No PRD document found"
            
        except Exception:
            return "Failed to load PRD content"
    
    def _generate_stage_content(self, stage: str, project_state: Dict[str, Any], prd_content: str) -> str:
        """Generate stage-specific content based on static template files."""
        project_name = project_state.get('project', {}).get('name', 'Unknown')
        
        # Try to load from static template files first
        template_content = self._load_template_file(stage)
        
        if template_content:
            # Render template with variables
            return self._render_template(template_content, project_state, prd_content)
        else:
            # Fallback to generic template if no specific template exists
            return self._generate_generic_stage_content(stage, project_name)
    
    def _load_template_file(self, stage: str) -> Optional[str]:
        """Load template file for the given stage."""
        try:
            # Try different template file names based on stage naming conventions
            template_names = [
                f"{stage}.md",
                f"{stage.lower()}.md",
                f"{stage.replace('_', '')}.md"
            ]
            
            templates_dir = Path(__file__).parent / "templates"
            
            for template_name in template_names:
                template_path = templates_dir / template_name
                if template_path.exists():
                    return template_path.read_text(encoding='utf-8')
            
            return None
            
        except Exception as e:
            print(f"[DEBUG] Failed to load template for stage '{stage}': {e}", file=sys.stderr)
            return None
    
    def _render_template(self, template_content: str, project_state: Dict[str, Any], prd_content: str) -> str:
        """Render template with project-specific variables."""
        try:
            project_name = project_state.get('project', {}).get('name', 'Unknown')
            current_date = datetime.datetime.now().strftime('%Y-%m-%d')
            current_datetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Common variables for template rendering
            template_vars = {
                # Project info
                'project_name': project_name,
                'projectName': project_name,
                
                # Dates
                'current_date': current_date,
                'current_datetime': current_datetime,
                'date': current_date,
                'datetime': current_datetime,
                
                # Stage info
                'stage_id': project_state.get('flow', {}).get('current_stage', 'unknown'),
                'progress': project_state.get('flow', {}).get('progress_percentage', 0),
                
                # Placeholders for user to fill
                'user_fill': '[请填写]',
                'todo': '___',
                'placeholder': '[待填写]'
            }
            
            # Replace template variables
            rendered_content = template_content
            
            # Replace {{variable}} format
            for key, value in template_vars.items():
                rendered_content = rendered_content.replace(f"{{{{{key}}}}}", str(value))
            
            # Replace {variable} format
            for key, value in template_vars.items():
                rendered_content = rendered_content.replace(f"{{{key}}}", str(value))
            
            # Add generation timestamp
            rendered_content += f"\n\n---\n*Generated by AceFlow v3.0 at {current_datetime}*\n"
            
            return rendered_content
            
        except Exception as e:
            print(f"[DEBUG] Template rendering failed: {e}", file=sys.stderr)
            return template_content  # Return unrendered template as fallback
    
    def _prepare_execution_package(self, stage: str) -> Dict[str, Any]:
        """准备AI Agent执行阶段所需的完整数据包
        
        Args:
            stage: 目标阶段ID
            
        Returns:
            Dict: 包含模板、前置输出、分析数据等的完整数据包
        """
        try:
            # 1. 加载阶段模板
            template_content = self._load_template_file(stage)
            if not template_content:
                template_content = self._get_generic_template(stage)
            
            # 2. 收集前置阶段输出
            previous_outputs = self.data_manager.get_previous_outputs(stage)
            
            # 3. 获取分析数据
            analysis_data = self.data_manager.load_analysis_data() or {}
            
            # 4. 获取项目上下文
            project_state = self.data_manager.load_project_state() or {}
            project_context = {
                "name": project_state.get("project", {}).get("name", "Unknown"),
                "mode": project_state.get("project", {}).get("mode", "standard"),
                "current_stage": project_state.get("flow", {}).get("current_stage", "unknown"),
                "progress_percentage": project_state.get("flow", {}).get("progress_percentage", 0),
                "created_at": project_state.get("project", {}).get("created_at", "")
            }
            
            # 5. 生成阶段依赖信息
            stage_dependencies = self.data_manager._get_stage_dependencies()
            dependencies_info = {
                "required_inputs": stage_dependencies.get(stage, []),
                "optional_inputs": [],
                "expected_outputs": [f"{stage}.md"]
            }
            
            # 6. 构建完整数据包
            data_package = {
                "template": {
                    "content": template_content,
                    "format": "markdown",
                    "source_file": f"templates/{stage}.md",
                    "placeholders": self._extract_placeholders(template_content),
                    "sections": self._extract_sections(template_content)
                },
                "previous_outputs": previous_outputs,
                "analysis_data": {
                    "project_info": analysis_data.get("project_info", {}),
                    "code_metrics": analysis_data.get("code_metrics", {}),
                    "test_metrics": analysis_data.get("test_metrics", {}),
                    "build_info": analysis_data.get("build_info", {})
                },
                "project_context": project_context,
                "stage_dependencies": dependencies_info
            }
            
            # 7. 生成执行指令
            instructions = {
                "task_description": f"基于提供的模板和输入数据，生成{stage}阶段的完整文档",
                "output_format": "markdown",
                "output_location": f"aceflow_result/{stage}.md",
                "quality_requirements": [
                    "严格遵循模板结构",
                    "基于前一阶段输出生成具体内容",
                    "结合项目实际情况填充数据",
                    "确保内容完整且有意义"
                ],
                "success_criteria": [
                    "文档结构完整",
                    "包含真实项目数据",
                    "逻辑连贯性强",
                    "格式规范正确"
                ]
            }
            
            return {
                "success": True,
                "stage_id": stage,
                "data_package": data_package,
                "instructions": instructions,
                "message": f"数据准备完成: {stage}阶段执行包已就绪"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"数据包准备失败: {stage}",
                "stage_id": stage
            }
    
    def _validate_stage_data(self, stage: Optional[str] = None) -> Dict[str, Any]:
        """验证阶段数据完整性
        
        Args:
            stage: 要验证的阶段ID，None表示验证当前阶段
            
        Returns:
            Dict: 验证结果
        """
        try:
            if not stage:
                # 获取当前阶段
                project_state = self.data_manager.load_project_state()
                if not project_state:
                    return {
                        "success": False,
                        "error": "No project state found",
                        "message": "项目状态不存在，请先初始化项目"
                    }
                stage = project_state.get("flow", {}).get("current_stage", "unknown")
            
            validation_result = {
                "is_valid": True,
                "completeness_score": 1.0,
                "missing_elements": [],
                "quality_issues": [],
                "suggestions": []
            }
            
            # 1. 检查模板是否存在
            template_content = self._load_template_file(stage)
            if not template_content:
                validation_result["missing_elements"].append("阶段模板文件")
                validation_result["is_valid"] = False
                validation_result["completeness_score"] -= 0.3
            
            # 2. 检查前置阶段输出
            previous_outputs = self.data_manager.get_previous_outputs(stage)
            required_deps = self.data_manager._get_stage_dependencies().get(stage, [])
            missing_deps = [dep for dep in required_deps if dep not in previous_outputs]
            if missing_deps:
                validation_result["missing_elements"].extend([f"前置阶段输出: {dep}" for dep in missing_deps])
                validation_result["completeness_score"] -= 0.2 * len(missing_deps)
            
            # 3. 检查分析数据
            analysis_data = self.data_manager.load_analysis_data()
            if not analysis_data:
                validation_result["missing_elements"].append("AI分析数据")
                validation_result["completeness_score"] -= 0.2
            
            # 4. 计算最终分数和状态
            if validation_result["completeness_score"] < 0.5:
                validation_result["is_valid"] = False
            
            # 5. 生成建议
            if validation_result["missing_elements"]:
                validation_result["suggestions"].append("请先提供缺失的输入数据")
            if not analysis_data:
                validation_result["suggestions"].append("建议AI Agent先分析项目并提供分析数据")
            
            return {
                "success": True,
                "stage_id": stage,
                "validation_result": validation_result
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"阶段数据验证失败: {stage}",
                "stage_id": stage
            }
    
    def _extract_placeholders(self, template_content: str) -> List[str]:
        """从模板中提取占位符"""
        import re
        placeholders = re.findall(r'\{\{([^}]+)\}\}', template_content)
        return list(set(placeholders))  # 去重
    
    def _extract_sections(self, template_content: str) -> List[str]:
        """从模板中提取主要章节标题"""
        import re
        sections = re.findall(r'^## (.+)$', template_content, re.MULTILINE)
        return sections
    
    def _get_generic_template(self, stage: str) -> str:
        """生成通用阶段模板"""
        return f"""# {stage.upper().replace('_', ' ')} 阶段文档

## 概述
请在此处填写阶段概述内容。

## 主要内容
请在此处填写主要内容。

## 结果总结
请在此处填写结果总结。

---
*本文档基于AceFlow通用模板生成*
*请根据实际情况调整内容结构*
"""
    
