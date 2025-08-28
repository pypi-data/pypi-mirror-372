"""Document Generator for AceFlow stage outputs."""

from typing import Dict, Any, List, Optional
from pathlib import Path
from dataclasses import dataclass
from jinja2 import Environment, FileSystemLoader, Template, TemplateNotFound
import re
import yaml
import os

from ..config.template_config import template_config


@dataclass
class DocumentResult:
    """Result of document generation."""
    success: bool
    content: str = ""
    quality_score: float = 0.0
    errors: List[str] = None
    warnings: List[str] = None
    
    @classmethod
    def success_result(cls, content: str, quality_score: float = 1.0):
        return cls(
            success=True,
            content=content,
            quality_score=quality_score,
            errors=[],
            warnings=[]
        )
    
    @classmethod
    def failed_result(cls, errors: List[str]):
        return cls(
            success=False,
            errors=errors or [],
            warnings=[]
        )


class DocumentGenerator:
    """Generates documents based on templates and input data."""
    
    def __init__(self, clinerules_dir: Path):
        """Initialize the document generator."""
        self.clinerules_dir = clinerules_dir
        self.template_config = template_config
        
        # 使用配置管理的模板目录
        self.main_templates_dir = self.template_config.main_templates_dir
        self.local_templates_dir = clinerules_dir / "templates"
        
        # 选择可用的模板目录
        self.templates_dir = self.main_templates_dir or self.local_templates_dir
        
        # Initialize Jinja2 environment
        if self.templates_dir and self.templates_dir.exists():
            self.jinja_env = Environment(
                loader=FileSystemLoader(str(self.templates_dir)),
                trim_blocks=True,
                lstrip_blocks=True
            )
        else:
            self.jinja_env = None
    
    def generate_stage_document(self, stage_def, input_data: Dict[str, Any]) -> DocumentResult:
        """Generate document for a specific stage."""
        try:
            # 尝试使用主项目模板生成文档
            if self.main_templates_dir:
                content = self._generate_from_main_templates(stage_def, input_data)
                if content:
                    return DocumentResult.success_result(content, 0.9)
            
            # 回退到简化文档生成
            content = self._generate_fallback_document(stage_def, input_data)
            warnings = []
            if not self.main_templates_dir:
                warnings.append("未找到主项目模板目录，使用简化模板")
            
            result = DocumentResult.success_result(content, 0.7)
            result.warnings = warnings
            return result
            
        except Exception as e:
            return DocumentResult.failed_result([f"Document generation error: {str(e)}"])
    
    def _generate_from_main_templates(self, stage_def, input_data: Dict[str, Any]) -> Optional[str]:
        """使用主项目模板生成文档."""
        try:
            # 使用配置获取模板路径
            template_path = self.template_config.get_template_path(stage_def.id)
            if not template_path:
                return None
            
            # 读取模板内容
            template_content = template_path.read_text(encoding='utf-8')
            
            # 应用模板变量替换
            content = self._apply_template_variables(template_content, stage_def, input_data)
            
            return content
            
        except Exception as e:
            # 如果模板处理失败，返回None让系统使用回退方案
            return None
    
    def _apply_template_variables(self, template_content: str, stage_def, input_data: Dict[str, Any]) -> str:
        """应用模板变量替换."""
        # 基本变量替换
        replacements = {
            '{storyTitle}': input_data.get('project', {}).get('name', 'Unknown Project'),
            '{{序号}}': '001',
            '[角色]': '用户',
            '[功能描述]': stage_def.description,
            '[实现的核心业务价值]': '提升用户体验和系统效率',
        }
        
        content = template_content
        for placeholder, value in replacements.items():
            content = content.replace(placeholder, value)
        
        # 添加项目信息头部
        project_header = f"""# {stage_def.name}

**项目**: {input_data.get('project', {}).get('name', 'Unknown Project')}
**阶段**: {stage_def.id} - {stage_def.name}
**创建时间**: {input_data.get('current_date', 'Unknown Date')}

---

"""
        
        # 如果模板没有项目头部，添加它
        if not content.startswith('#'):
            content = project_header + content
        
        return content
    
    def _generate_fallback_document(self, stage_def, input_data: Dict[str, Any]) -> str:
        """Generate a fallback document when template is not available."""
        content = f"""# {stage_def.name}

**项目**: {input_data.get('project', {}).get('name', 'Unknown Project')}
**阶段**: {stage_def.id} - {stage_def.name}
**创建时间**: {input_data.get('current_date', 'Unknown Date')}

## 概述

{stage_def.description}

## 详细内容

基于以下输入进行分析：

"""
        
        # Add input information
        for input_name in stage_def.inputs:
            input_key = input_name.lower().replace(" ", "_").replace("文档", "")
            if input_key in input_data:
                content += f"### {input_name}\n\n"
                input_content = input_data[input_key]
                if isinstance(input_content, str) and len(input_content) > 500:
                    content += f"{input_content[:500]}...\n\n"
                else:
                    content += f"{input_content}\n\n"
        
        content += """## 分析结果

基于输入信息，本阶段的主要工作内容包括：

1. 分析现有输入材料
2. 提取关键信息和需求
3. 制定相应的解决方案
4. 为下一阶段提供输入

## 下一步工作

基于本阶段的分析结果，下一阶段将进行更详细的工作。

"""
        
        return content