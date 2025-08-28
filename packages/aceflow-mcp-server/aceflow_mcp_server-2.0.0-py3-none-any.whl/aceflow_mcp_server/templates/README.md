# AceFlow v3.0 模板库

## 📚 模板结构说明

```
templates/
├── README.md                 # 本文档
├── 
├── 模式模板/
│   ├── minimal/              # 轻量级模式 (3阶段: P-D-R)
│   │   ├── template.yaml     # 模式配置
│   │   ├── README.md         # 使用说明
│   │   ├── requirements.md   # 需求模板
│   │   ├── tasks.md          # 任务模板
│   │   ├── review.md         # 评审模板
│   │   └── summary.md        # 总结模板
│   │   
│   ├── standard/             # 标准模式 (5阶段: P1-P2-D1-D2-R1)
│   │   ├── template.yaml     # 模式配置
│   │   └── ...               # 对应模板文件
│   │   
│   ├── complete/             # 完整模式 (8阶段: S1-S8)
│   │   ├── template.yaml     # 模式配置
│   │   └── ...               # 待创建
│   │   
│   └── smart/                # 智能模式 (动态阶段)
│       ├── template.yaml     # 模式配置
│       └── ...               # 待创建
│
├── AceFlow标准阶段模板/
│   ├── s1_user_story.md      # S1: 用户故事模板
│   ├── s2_tasks_group.md     # S2: 任务分组模板
│   ├── s2_tasks_main.md      # S2: 主要任务模板
│   ├── s3_testcases.md       # S3: 测试用例模板
│   ├── s3_testcases_main.md  # S3: 主要测试用例模板
│   ├── s4_implementation.md  # S4: 实现模板
│   ├── s4_implementation_report.md # S4: 实现报告模板
│   ├── s5_test_report.md     # S5: 测试报告模板
│   ├── s6_codereview.md      # S6: 代码评审模板
│   ├── s7_demo_script.md     # S7: 演示脚本模板
│   ├── s8_learning_summary.md # S8: 学习总结模板
│   └── s8_summary_report.md  # S8: 总结报告模板
│
├── 辅助模板/
│   ├── document_templates/   # 文档模板
│   │   ├── config_guide.md   # 配置指南
│   │   └── process_spec.md   # 流程规范
│   └── task-status-table.md  # 任务状态表模板
│
└── 工作流模板/
    └── minimal/workflows/     # 轻量级工作流
        ├── bug_fix.md        # 错误修复流程
        ├── feature_quick.md  # 快速功能开发
        └── prototype.md      # 原型开发流程
```

## 🎯 使用指南

### 选择合适的模式

| 模式 | 适用场景 | 团队规模 | 项目周期 | 特点 |
|------|----------|----------|----------|------|
| **minimal** | 快速原型、小功能 | 1-3人 | 2-7天 | 轻量灵活，3个核心阶段 |
| **standard** | 常规项目开发 | 3-8人 | 1-4周 | 平衡完整，5个标准阶段 |
| **complete** | 大型项目、严格流程 | 5-20人 | 2-12周 | 完整规范，8个详细阶段 |
| **smart** | AI辅助项目 | 任意 | 动态 | 智能决策，自适应流程 |

### 模板变量说明

模板中使用的占位符：
- `{{序号}}` - 自增序号，如 001, 002
- `{storyTitle}` - 用户故事标题
- `{taskName}` - 任务名称
- `{taskDescription}` - 任务描述
- `{completionTime}` - 完成时间
- `{actualHours}` - 实际工时

## 🔧 自定义模板

1. 复制现有模式目录
2. 修改 `template.yaml` 配置
3. 调整具体模板文件
4. 使用 `aceflow-templates.sh validate` 验证

## 📖 相关文档

- [AceFlow v3.0 规范](../aceflow-spec_v3.0.md)
- [集成指南](.clinerules/aceflow_integration.md)
- [使用教程](../docs/tutorial.md)