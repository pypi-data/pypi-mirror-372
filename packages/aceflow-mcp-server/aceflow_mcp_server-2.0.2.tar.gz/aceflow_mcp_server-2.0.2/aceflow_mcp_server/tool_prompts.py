#!/usr/bin/env python3
"""
AceFlow MCP 工具提示词定义
为大模型提供清晰、详细的工具使用指导
"""

from typing import Dict, Any

class AceFlowToolPrompts:
    """AceFlow 工具提示词管理类"""
    
    @staticmethod
    def get_tool_definitions() -> Dict[str, Dict[str, Any]]:
        """获取所有工具的详细定义和提示词"""
        return {
            "aceflow_init": {
                "name": "aceflow_init",
                "description": "🚀 初始化 AceFlow 项目 - 创建AI驱动的软件开发工作流项目结构",
                "detailed_description": """
这个工具用于初始化一个新的 AceFlow 项目，建立标准化的AI辅助软件开发工作流。

🎯 **使用场景**:
- 开始一个新的软件项目时
- 需要建立标准化开发流程时
- 想要使用AI辅助的项目管理时

📋 **工作流模式说明**:
- **minimal**: 快速原型模式 - 适合概念验证和快速迭代
- **standard**: 标准开发模式 - 适合大多数软件项目
- **complete**: 企业级模式 - 适合大型项目和团队协作
- **smart**: AI增强模式 - 集成智能分析和自适应流程

💡 **最佳实践**:
- 新手建议使用 'standard' 模式
- 快速原型使用 'minimal' 模式
- 企业项目使用 'complete' 模式
- AI项目使用 'smart' 模式
                """,
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "mode": {
                            "type": "string",
                            "description": "项目工作流模式 - 决定项目的复杂度和功能范围",
                            "enum": ["minimal", "standard", "complete", "smart"],
                            "enum_descriptions": {
                                "minimal": "快速原型模式 - 3个阶段，适合概念验证和快速迭代",
                                "standard": "标准开发模式 - 8个阶段，适合大多数软件项目 (推荐)",
                                "complete": "企业级模式 - 12个阶段，适合大型项目和团队协作",
                                "smart": "AI增强模式 - 10个阶段，集成智能分析和自适应流程"
                            },
                            "examples": ["standard", "minimal"],
                            "default": "standard"
                        },
                        "project_name": {
                            "type": "string",
                            "description": "项目名称 - 用于创建项目目录和配置文件 (可选)",
                            "examples": ["my-web-app", "ai-chatbot", "data-pipeline"]
                        },
                        "directory": {
                            "type": "string",
                            "description": "项目目录路径 - 指定项目创建位置 (可选，默认当前目录)",
                            "examples": ["./projects/my-app", "/home/user/workspace"]
                        }
                    },
                    "required": ["mode"]
                },
                "usage_examples": [
                    {
                        "scenario": "创建标准Web应用项目",
                        "parameters": {
                            "mode": "standard",
                            "project_name": "my-web-app"
                        }
                    },
                    {
                        "scenario": "快速原型开发",
                        "parameters": {
                            "mode": "minimal",
                            "project_name": "prototype"
                        }
                    }
                ]
            },
            
            "aceflow_stage": {
                "name": "aceflow_stage",
                "description": "📊 管理项目阶段和工作流 - 跟踪和控制项目开发进度",
                "detailed_description": """
这个工具用于管理 AceFlow 项目的开发阶段，提供项目进度跟踪和工作流控制。

🎯 **使用场景**:
- 查看项目当前进度和状态
- 了解项目的工作流阶段
- 推进项目到下一个阶段
- 重置项目状态

📋 **可用操作**:
- **list**: 列出所有可用的工作流阶段
- **status**: 查看当前项目状态和进度
- **next**: 推进到下一个阶段
- **reset**: 重置项目状态到初始阶段
- **set_analysis**: 设置AI分析数据 (AI Agent → MCP)
- **save_output**: 保存阶段输出数据 (AI Agent → MCP)
- **prepare_data**: 准备下阶段数据包 (MCP → AI Agent)
- **validate**: 验证当前阶段数据完整性

🔄 **标准工作流阶段**:
1. user_stories - 用户故事分析
2. task_breakdown - 任务分解
3. test_design - 测试用例设计
4. implementation - 功能实现
5. unit_test - 单元测试
6. integration_test - 集成测试
7. code_review - 代码审查
8. demo - 功能演示

💡 **最佳实践**:
- 定期检查项目状态
- 按顺序完成各个阶段
- 在推进前确保当前阶段完成
                """,
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "description": "要执行的操作类型 - 支持双向AI-MCP协作",
                            "enum": ["list", "status", "next", "reset", "set_analysis", "save_output", "prepare_data", "validate"],
                            "enum_descriptions": {
                                "list": "列出所有可用阶段",
                                "status": "查看当前状态",
                                "next": "推进到下一阶段",
                                "reset": "重置项目状态",
                                "set_analysis": "AI Agent提供分析数据",
                                "save_output": "AI Agent保存阶段输出",
                                "prepare_data": "MCP准备数据包",
                                "validate": "验证数据完整性"
                            },
                            "examples": ["status", "list", "set_analysis"]
                        },
                        "stage": {
                            "type": "string",
                            "description": "特定阶段名称 (某些操作需要，如跳转到指定阶段)",
                            "examples": ["implementation", "test_design"]
                        },
                        "data": {
                            "type": "object",
                            "description": "AI Agent提供的数据 - 用于双向协作(set_analysis, save_output操作时使用)",
                            "properties": {
                                "content": {
                                    "type": "object",
                                    "description": "主要内容数据"
                                },
                                "metadata": {
                                    "type": "object", 
                                    "description": "元数据信息"
                                }
                            },
                            "examples": [
                                {
                                    "project_info": {"name": "web-app", "version": "1.0.0"},
                                    "code_metrics": {"complexity": "medium", "coverage": 85}
                                }
                            ]
                        }
                    },
                    "required": ["action"]
                },
                "usage_examples": [
                    {
                        "scenario": "查看项目当前状态",
                        "parameters": {
                            "action": "status"
                        }
                    },
                    {
                        "scenario": "列出所有工作流阶段",
                        "parameters": {
                            "action": "list"
                        }
                    },
                    {
                        "scenario": "推进到下一阶段",
                        "parameters": {
                            "action": "next"
                        }
                    },
                    {
                        "scenario": "AI Agent提供分析数据",
                        "parameters": {
                            "action": "set_analysis",
                            "stage": "analysis",
                            "data": {
                                "project_info": {"name": "web-app", "version": "1.0.0"},
                                "code_metrics": {"complexity": "medium", "coverage": 85},
                                "test_metrics": {"test_count": 120, "pass_rate": 98.5}
                            }
                        }
                    },
                    {
                        "scenario": "AI Agent保存设计阶段输出",
                        "parameters": {
                            "action": "save_output",
                            "stage": "design",
                            "data": {
                                "content": {
                                    "architecture": "microservices",
                                    "components": ["api", "database", "cache"]
                                },
                                "metadata": {"author": "AI Agent", "timestamp": "2025-08-26"}
                            }
                        }
                    },
                    {
                        "scenario": "MCP准备实现阶段数据包",
                        "parameters": {
                            "action": "prepare_data",
                            "stage": "implementation"
                        }
                    }
                ]
            },
            
            "aceflow_validate": {
                "name": "aceflow_validate",
                "description": "✅ 验证项目合规性和质量 - 检查项目是否符合AceFlow标准和最佳实践",
                "detailed_description": """
这个工具用于验证 AceFlow 项目的质量和合规性，确保项目符合标准和最佳实践。

🎯 **使用场景**:
- 检查项目配置是否正确
- 验证代码质量和结构
- 确保项目符合标准
- 生成质量报告

📋 **验证模式**:
- **basic**: 基础验证 - 检查核心配置和结构
- **detailed**: 详细验证 - 深度分析代码质量和最佳实践

🔧 **验证内容**:
- 项目结构完整性
- 配置文件正确性
- 代码质量标准
- 文档完整性
- 测试覆盖率
- 安全性检查

💡 **最佳实践**:
- 定期运行验证检查
- 在提交代码前验证
- 使用详细模式进行深度检查
- 启用自动修复功能
                """,
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "mode": {
                            "type": "string",
                            "description": "验证模式 - 决定检查的深度和范围",
                            "enum": ["basic", "detailed"],
                            "default": "basic",
                            "examples": ["basic", "detailed"]
                        },
                        "fix": {
                            "type": "boolean",
                            "description": "是否自动修复发现的问题",
                            "default": False,
                            "examples": [True, False]
                        },
                        "report": {
                            "type": "boolean",
                            "description": "是否生成详细的验证报告",
                            "default": False,
                            "examples": [True, False]
                        }
                    }
                },
                "usage_examples": [
                    {
                        "scenario": "基础项目验证",
                        "parameters": {
                            "mode": "basic"
                        }
                    },
                    {
                        "scenario": "详细验证并生成报告",
                        "parameters": {
                            "mode": "detailed",
                            "report": True
                        }
                    },
                    {
                        "scenario": "验证并自动修复问题",
                        "parameters": {
                            "mode": "basic",
                            "fix": True
                        }
                    }
                ]
            },
            
            "aceflow_template": {
                "name": "aceflow_template",
                "description": "📋 管理工作流模板 - 查看和应用不同的项目模板配置",
                "detailed_description": """
这个工具用于管理 AceFlow 的工作流模板，提供不同复杂度的项目模板选择。

🎯 **使用场景**:
- 查看可用的项目模板
- 应用特定模板到项目
- 验证模板配置
- 切换项目模板

📋 **可用模板**:
- **minimal**: 最小化模板 - 3个阶段，适合快速原型
- **standard**: 标准模板 - 8个阶段，适合常规项目
- **complete**: 完整模板 - 12个阶段，适合企业级项目
- **smart**: 智能模板 - 10个阶段，AI增强功能

🔧 **可用操作**:
- **list**: 列出所有可用模板
- **apply**: 应用指定模板到当前项目
- **validate**: 验证模板配置

💡 **最佳实践**:
- 根据项目复杂度选择合适模板
- 在项目初期确定模板类型
- 定期验证模板配置
                """,
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "description": "要执行的模板操作",
                            "enum": ["list", "apply", "validate"],
                            "examples": ["list", "apply"]
                        },
                        "template": {
                            "type": "string",
                            "description": "模板名称 (apply和validate操作需要)",
                            "enum": ["minimal", "standard", "complete", "smart"],
                            "examples": ["standard", "minimal"]
                        }
                    },
                    "required": ["action"]
                },
                "usage_examples": [
                    {
                        "scenario": "查看所有可用模板",
                        "parameters": {
                            "action": "list"
                        }
                    },
                    {
                        "scenario": "应用标准模板",
                        "parameters": {
                            "action": "apply",
                            "template": "standard"
                        }
                    },
                    {
                        "scenario": "验证智能模板配置",
                        "parameters": {
                            "action": "validate",
                            "template": "smart"
                        }
                    }
                ]
            }
        }
    
    @staticmethod
    def get_tool_description(tool_name: str) -> str:
        """获取工具的详细描述"""
        definitions = AceFlowToolPrompts.get_tool_definitions()
        if tool_name in definitions:
            return definitions[tool_name]["detailed_description"]
        return f"未找到工具 {tool_name} 的描述"
    
    @staticmethod
    def get_usage_examples(tool_name: str) -> list:
        """获取工具的使用示例"""
        definitions = AceFlowToolPrompts.get_tool_definitions()
        if tool_name in definitions:
            return definitions[tool_name].get("usage_examples", [])
        return []
    
    @staticmethod
    def get_enhanced_tool_schema(tool_name: str) -> Dict[str, Any]:
        """获取增强的工具架构定义"""
        definitions = AceFlowToolPrompts.get_tool_definitions()
        if tool_name in definitions:
            tool_def = definitions[tool_name]
            return {
                "name": tool_def["name"],
                "description": tool_def["description"],
                "inputSchema": tool_def["inputSchema"]
            }
        return {}