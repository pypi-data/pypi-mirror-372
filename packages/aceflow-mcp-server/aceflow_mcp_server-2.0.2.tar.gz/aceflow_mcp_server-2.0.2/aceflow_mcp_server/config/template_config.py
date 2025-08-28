"""Template configuration for AceFlow MCP Server."""

from pathlib import Path
from typing import Optional, Dict
import os


class TemplateConfig:
    """管理模板配置和路径."""
    
    def __init__(self):
        self.main_templates_dir = self._find_main_templates_dir()
        self.stage_template_mapping = self._get_stage_template_mapping()
    
    def _find_main_templates_dir(self) -> Optional[Path]:
        """查找模板目录，优先使用内置模板."""
        current_dir = Path(__file__).parent
        
        # 优先使用内置的同步模板
        builtin_templates = current_dir.parent / "templates"
        if builtin_templates.exists() and (builtin_templates / "s1_user_story.md").exists():
            return builtin_templates
        
        # 开发环境下，尝试查找主项目模板目录
        possible_paths = [
            # 相对于MCP服务器的路径
            current_dir / "../../../aceflow/templates",
            current_dir / "../../../../aceflow/templates", 
            # 从工作目录查找
            Path.cwd() / "aceflow/templates",
            Path.cwd().parent / "aceflow/templates",
            # 环境变量指定的路径
            Path(os.environ.get('ACEFLOW_TEMPLATES_DIR', '')) if os.environ.get('ACEFLOW_TEMPLATES_DIR') else None,
        ]
        
        for path in possible_paths:
            if path is None:
                continue
                
            try:
                resolved_path = path.resolve()
                if resolved_path.exists() and resolved_path.is_dir():
                    # 验证这是正确的模板目录
                    if (resolved_path / "s1_user_story.md").exists():
                        return resolved_path
            except (OSError, ValueError):
                continue
        
        return None
    
    def _get_stage_template_mapping(self) -> Dict[str, str]:
        """获取阶段到模板文件的映射."""
        return {
            # Standard模式映射
            "S1_user_stories": "s1_user_story.md",
            "S2_task_breakdown": "s2_tasks_main.md",
            "S3_test_design": "s3_testcases_main.md", 
            "S4_implementation": "s4_implementation.md",
            "S5_unit_test": "s5_test_report.md",
            "S6_integration_test": "s5_test_report.md",
            "S7_code_review": "s6_codereview.md",
            "S8_demo": "s7_demo_script.md",
            
            # Complete模式映射
            "S1_requirement_analysis": "s1_user_story.md",
            "S2_architecture_design": "s2_tasks_main.md",
            "S3_user_stories": "s1_user_story.md",
            "S4_task_breakdown": "s2_tasks_main.md",
            "S5_test_design": "s3_testcases_main.md",
            "S6_implementation": "s4_implementation.md",
            "S7_unit_test": "s5_test_report.md",
            "S8_integration_test": "s5_test_report.md",
            "S9_performance_test": "s5_test_report.md",
            "S10_security_review": "s6_codereview.md",
            "S11_code_review": "s6_codereview.md",
            "S12_demo": "s7_demo_script.md",
            
            # Minimal模式映射
            "S1_implementation": "s4_implementation.md",
            "S2_test": "s5_test_report.md",
            "S3_demo": "s7_demo_script.md",
            
            # Smart模式映射
            "S1_project_analysis": "s1_user_story.md",
            "S2_adaptive_planning": "s2_tasks_main.md",
            "S3_user_stories": "s1_user_story.md",
            "S4_smart_breakdown": "s2_tasks_main.md",
            "S5_test_generation": "s3_testcases_main.md",
            "S6_implementation": "s4_implementation.md",
            "S7_automated_test": "s5_test_report.md",
            "S8_quality_assessment": "s6_codereview.md",
            "S9_optimization": "s4_implementation.md",
            "S10_demo": "s7_demo_script.md",
        }
    
    def get_template_path(self, stage_id: str) -> Optional[Path]:
        """获取指定阶段的模板路径."""
        if not self.main_templates_dir:
            return None
            
        template_file = self.stage_template_mapping.get(stage_id)
        if not template_file:
            return None
            
        template_path = self.main_templates_dir / template_file
        return template_path if template_path.exists() else None
    
    def is_main_templates_available(self) -> bool:
        """检查主项目模板是否可用."""
        return self.main_templates_dir is not None
    
    def get_template_info(self) -> Dict[str, any]:
        """获取模板配置信息."""
        return {
            "main_templates_dir": str(self.main_templates_dir) if self.main_templates_dir else None,
            "templates_available": self.is_main_templates_available(),
            "supported_stages": list(self.stage_template_mapping.keys()),
            "template_files": list(set(self.stage_template_mapping.values())),
        }


# 全局配置实例
template_config = TemplateConfig()