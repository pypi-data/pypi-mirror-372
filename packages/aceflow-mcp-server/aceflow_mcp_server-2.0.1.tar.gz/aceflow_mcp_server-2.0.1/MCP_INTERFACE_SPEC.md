# AceFlow MCP工具接口规范

**版本**: 2.0  
**创建时间**: 2025-08-25  
**配套文档**: ARCHITECTURE_DESIGN.md  

## 🔌 核心接口定义

### aceflow_stage 主接口

```python
def aceflow_stage(
    action: str,                    # 必需：操作类型
    stage: Optional[str] = None,    # 可选：目标阶段ID  
    data: Optional[Dict] = None     # 可选：数据载荷
) -> Dict[str, Any]                 # 返回：标准响应格式
```

## 📋 操作类型详细规范

### 1. set_analysis - 设置项目分析数据

**用途**: AI Agent向MCP工具提供项目分析结果

**调用格式**:
```python
aceflow_stage(action="set_analysis", data={
    "project_info": {
        "name": str,
        "tech_stack": List[str],
        "file_count": int,
        "directory_structure": Dict,
        "dependencies": List[str]
    },
    "code_metrics": {
        "total_lines": int,
        "code_lines": int, 
        "comment_lines": int,
        "blank_lines": int,
        "complexity_score": float,
        "maintainability_index": float
    },
    "test_metrics": {
        "test_files_count": int,
        "total_tests": int,
        "test_coverage_percent": float,
        "test_types": List[str]  # ["unit", "integration", "e2e"]
    },
    "build_info": {
        "build_tool": str,      # "npm", "pip", "maven", etc.
        "scripts": Dict[str, str],
        "environment": str       # "development", "production"
    }
})
```

**返回格式**:
```python
{
    "success": bool,
    "message": str,
    "data_stored": {
        "analysis_id": str,
        "timestamp": str,
        "categories": List[str]
    }
}
```

### 2. save_output - 保存阶段输出

**用途**: AI Agent保存生成的阶段内容供后续阶段使用

**调用格式**:
```python
aceflow_stage(action="save_output", stage="s1_user_story", data={
    "content": str,                 # 完整的阶段输出内容
    "metadata": {
        "word_count": int,
        "sections_count": int,
        "completion_time": str,
        "ai_confidence": float      # 0.0-1.0
    },
    "artifacts": {
        "primary_output": str,      # 主要输出文件路径
        "supporting_files": List[str]
    }
})
```

**返回格式**:
```python
{
    "success": bool,
    "stage_id": str,
    "saved_to": str,               # 保存路径
    "next_stage_unlocked": bool,   # 是否解锁下一阶段
    "message": str
}
```

### 3. prepare_data - 准备执行数据包

**用途**: AI Agent请求完整的阶段执行数据包

**调用格式**:
```python
aceflow_stage(action="prepare_data", stage="s5_test_report")
```

**返回格式**:
```python
{
    "success": bool,
    "stage_id": str,
    "data_package": {
        "template": {
            "content": str,           # 模板文件内容
            "format": "markdown",
            "source_file": str,       # templates/s5_test_report.md
            "placeholders": List[str], # 模板中的占位符列表
            "sections": List[str]     # 主要章节列表
        },
        "previous_outputs": {
            # 前置阶段的输出内容
            "s4_implementation": {
                "content": str,
                "metadata": Dict,
                "key_points": List[str]
            }
        },
        "analysis_data": {
            # AI之前提供的分析数据
            "project_info": Dict,
            "code_metrics": Dict,
            "test_metrics": Dict
        },
        "project_context": {
            "name": str,
            "mode": str,
            "current_stage": str,
            "progress_percentage": int,
            "created_at": str
        },
        "stage_dependencies": {
            "required_inputs": List[str],     # 必需的输入
            "optional_inputs": List[str],     # 可选的输入
            "expected_outputs": List[str]     # 预期的输出
        }
    },
    "instructions": {
        "task_description": str,
        "output_format": "markdown",
        "output_location": str,           # aceflow_result/stage.md
        "quality_requirements": List[str],
        "success_criteria": List[str]
    }
}
```

### 4. status - 查询项目状态

**调用格式**:
```python
aceflow_stage(action="status")
```

**返回格式**:
```python
{
    "success": bool,
    "project": {
        "name": str,
        "mode": str,
        "created_at": str,
        "last_updated": str
    },
    "flow": {
        "current_stage": str,
        "current_stage_status": str,    # "pending", "in_progress", "completed"
        "completed_stages": List[str],
        "next_stage": Optional[str],
        "progress_percentage": int,
        "estimated_remaining_time": Optional[str]
    },
    "data_status": {
        "analysis_data_available": bool,
        "previous_outputs_count": int,
        "missing_dependencies": List[str]
    }
}
```

### 5. next - 推进到下一阶段

**调用格式**:
```python
aceflow_stage(action="next")
```

**返回格式**:
```python
{
    "success": bool,
    "transition": {
        "from_stage": str,
        "to_stage": str,
        "progress_update": int
    },
    "message": str,
    "next_actions": List[str]         # 建议的下一步操作
}
```

### 6. goto - 跳转到指定阶段

**调用格式**:
```python
aceflow_stage(action="goto", stage="s3_testcases")
```

### 7. validate - 验证当前阶段完整性

**调用格式**:
```python
aceflow_stage(action="validate", stage="s2_tasks_group")
```

**返回格式**:
```python
{
    "success": bool,
    "validation_result": {
        "is_valid": bool,
        "completeness_score": float,    # 0.0-1.0
        "missing_elements": List[str],
        "quality_issues": List[str],
        "suggestions": List[str]
    }
}
```

## 🔄 标准错误处理

### 错误响应格式
```python
{
    "success": False,
    "error_code": str,              # "MISSING_STAGE", "INVALID_DATA", etc.
    "error_message": str,           # 用户友好的错误描述
    "error_details": Dict,          # 详细的错误信息
    "suggested_actions": List[str]  # 建议的修复操作
}
```

### 常见错误代码
- `MISSING_STAGE`: 指定的阶段不存在
- `INVALID_DATA`: 提供的数据格式不正确
- `DEPENDENCY_MISSING`: 缺少必需的前置阶段
- `TEMPLATE_NOT_FOUND`: 找不到对应的模板文件
- `ANALYSIS_DATA_MISSING`: 缺少必需的分析数据

## 📊 数据验证规则

### 项目信息验证
```python
project_info_schema = {
    "name": {"type": "string", "minLength": 1, "maxLength": 100},
    "tech_stack": {"type": "array", "items": {"type": "string"}},
    "file_count": {"type": "integer", "minimum": 0}
}
```

### 代码指标验证
```python
code_metrics_schema = {
    "total_lines": {"type": "integer", "minimum": 0},
    "complexity_score": {"type": "number", "minimum": 0, "maximum": 20},
    "test_coverage_percent": {"type": "number", "minimum": 0, "maximum": 100}
}
```

## 🚀 使用示例

### 完整的阶段执行流程示例

```python
# 1. AI Agent分析项目后设置分析数据
response1 = aceflow_stage(action="set_analysis", data={
    "project_info": {
        "name": "TaskManager",
        "tech_stack": ["Python", "FastAPI", "Vue3"],
        "file_count": 42
    },
    "test_metrics": {
        "total_tests": 25,
        "test_coverage_percent": 87.5
    }
})

# 2. 请求S5阶段的数据包
response2 = aceflow_stage(action="prepare_data", stage="s5_test_report")

# 3. AI基于数据包生成内容后保存输出
response3 = aceflow_stage(action="save_output", stage="s5_test_report", data={
    "content": "完整的测试报告内容...",
    "metadata": {"word_count": 1500}
})

# 4. 推进到下一阶段
response4 = aceflow_stage(action="next")
```

## ⚡ 性能考虑

### 缓存策略
- 模板文件缓存到内存，避免重复读取
- 分析数据增量更新，不完全覆盖
- 项目状态变更时触发缓存刷新

### 数据大小限制
- 单次分析数据不超过10MB
- 阶段输出内容不超过5MB
- 模板文件不超过1MB

---
*接口规范版本: 2.0*  
*最后更新: 2025-08-25*