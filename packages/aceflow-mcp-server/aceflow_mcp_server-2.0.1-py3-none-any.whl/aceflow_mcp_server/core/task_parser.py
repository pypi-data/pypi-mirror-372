"""
任务分解解析器 - AceFlow AI-人协同工作流
Task Parser for AceFlow AI-Human Collaborative Workflow
"""

from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import re
import json
from pathlib import Path
from datetime import datetime


class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    """任务优先级"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class TaskItem:
    """任务项"""
    task_id: str
    name: str
    description: str
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM
    estimated_hours: float = 0.0
    dependencies: List[str] = field(default_factory=list)
    output_files: List[str] = field(default_factory=list)
    requirements: List[str] = field(default_factory=list)
    acceptance_criteria: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    assigned_to: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TaskQueue:
    """任务队列"""
    project_id: str
    stage_id: str
    tasks: List[TaskItem] = field(default_factory=list)
    total_estimated_hours: float = 0.0
    completed_tasks: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


class TaskParser:
    """任务分解解析器"""
    
    def __init__(self, workspace_dir: Optional[Path] = None):
        """
        初始化任务解析器
        
        Args:
            workspace_dir: 工作空间目录
        """
        self.workspace_dir = workspace_dir or Path.cwd()
        self.aceflow_result_dir = self.workspace_dir / "aceflow_result"
        
        # 任务解析模式
        self.task_patterns = [
            # 标准任务格式: - [ ] 任务名称
            r'^-\s*\[\s*\]\s*(.+)$',
            # 编号任务格式: 1. 任务名称
            r'^\d+\.\s*(.+)$',
            # 子任务格式: - 子任务名称
            r'^-\s*(.+)$',
            # 带优先级的任务: [高] 任务名称
            r'^\[([^\]]+)\]\s*(.+)$'
        ]
        
        # 优先级关键词映射
        self.priority_keywords = {
            'critical': TaskPriority.CRITICAL,
            'high': TaskPriority.HIGH,
            'medium': TaskPriority.MEDIUM,
            'low': TaskPriority.LOW,
            '紧急': TaskPriority.CRITICAL,
            '高': TaskPriority.HIGH,
            '中': TaskPriority.MEDIUM,
            '低': TaskPriority.LOW
        }
        
        # 时间估算关键词
        self.time_patterns = [
            r'(\d+(?:\.\d+)?)\s*小时',
            r'(\d+(?:\.\d+)?)\s*hours?',
            r'(\d+(?:\.\d+)?)\s*h',
            r'(\d+(?:\.\d+)?)\s*天',
            r'(\d+(?:\.\d+)?)\s*days?',
            r'(\d+(?:\.\d+)?)\s*d'
        ]
    
    def parse_task_breakdown_document(
        self,
        document_path: Path,
        project_id: str,
        stage_id: str = "S2_task_breakdown"
    ) -> TaskQueue:
        """
        解析任务分解文档
        
        Args:
            document_path: 文档路径
            project_id: 项目ID
            stage_id: 阶段ID
            
        Returns:
            TaskQueue: 解析后的任务队列
        """
        if not document_path.exists():
            raise FileNotFoundError(f"Task breakdown document not found: {document_path}")
        
        # 读取文档内容
        with open(document_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 解析任务
        tasks = self._parse_tasks_from_content(content)
        
        # 创建任务队列
        task_queue = TaskQueue(
            project_id=project_id,
            stage_id=stage_id,
            tasks=tasks,
            total_estimated_hours=sum(task.estimated_hours for task in tasks)
        )
        
        # 解析依赖关系
        self._resolve_task_dependencies(task_queue)
        
        return task_queue
    
    def parse_task_from_text(
        self,
        task_text: str,
        task_id: Optional[str] = None
    ) -> TaskItem:
        """
        从文本解析单个任务
        
        Args:
            task_text: 任务文本
            task_id: 任务ID，如果为None则自动生成
            
        Returns:
            TaskItem: 解析后的任务项
        """
        if task_id is None:
            task_id = self._generate_task_id()
        
        # 清理文本
        cleaned_text = task_text.strip()
        
        # 提取任务名称
        task_name = self._extract_task_name(cleaned_text)
        
        # 提取任务描述
        task_description = self._extract_task_description(cleaned_text)
        
        # 提取优先级
        priority = self._extract_priority(cleaned_text)
        
        # 提取时间估算
        estimated_hours = self._extract_time_estimate(cleaned_text)
        
        # 提取依赖关系
        dependencies = self._extract_dependencies(cleaned_text)
        
        # 提取输出文件
        output_files = self._extract_output_files(cleaned_text)
        
        # 提取需求引用
        requirements = self._extract_requirements(cleaned_text)
        
        # 提取验收标准
        acceptance_criteria = self._extract_acceptance_criteria(cleaned_text)
        
        # 提取标签
        tags = self._extract_tags(cleaned_text)
        
        return TaskItem(
            task_id=task_id,
            name=task_name,
            description=task_description,
            priority=priority,
            estimated_hours=estimated_hours,
            dependencies=dependencies,
            output_files=output_files,
            requirements=requirements,
            acceptance_criteria=acceptance_criteria,
            tags=tags
        )
    
    def update_task_status(
        self,
        task_queue: TaskQueue,
        task_id: str,
        new_status: TaskStatus,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        更新任务状态
        
        Args:
            task_queue: 任务队列
            task_id: 任务ID
            new_status: 新状态
            metadata: 额外元数据
            
        Returns:
            bool: 是否成功更新
        """
        for task in task_queue.tasks:
            if task.task_id == task_id:
                old_status = task.status
                task.status = new_status
                task.updated_at = datetime.now()
                
                if metadata:
                    task.metadata.update(metadata)
                
                # 更新队列统计
                if old_status != TaskStatus.COMPLETED and new_status == TaskStatus.COMPLETED:
                    task_queue.completed_tasks += 1
                elif old_status == TaskStatus.COMPLETED and new_status != TaskStatus.COMPLETED:
                    task_queue.completed_tasks -= 1
                
                task_queue.updated_at = datetime.now()
                return True
        
        return False
    
    def get_next_executable_tasks(self, task_queue: TaskQueue) -> List[TaskItem]:
        """
        获取下一个可执行的任务
        
        Args:
            task_queue: 任务队列
            
        Returns:
            List[TaskItem]: 可执行的任务列表
        """
        executable_tasks = []
        completed_task_ids = {
            task.task_id for task in task_queue.tasks 
            if task.status == TaskStatus.COMPLETED
        }
        
        for task in task_queue.tasks:
            if task.status == TaskStatus.PENDING:
                # 检查依赖是否都已完成
                dependencies_met = all(
                    dep_id in completed_task_ids 
                    for dep_id in task.dependencies
                )
                
                if dependencies_met:
                    executable_tasks.append(task)
        
        # 按优先级排序
        priority_order = {
            TaskPriority.CRITICAL: 0,
            TaskPriority.HIGH: 1,
            TaskPriority.MEDIUM: 2,
            TaskPriority.LOW: 3
        }
        
        executable_tasks.sort(key=lambda t: priority_order[t.priority])
        
        return executable_tasks
    
    def get_task_progress(self, task_queue: TaskQueue) -> Dict[str, Any]:
        """
        获取任务进度信息
        
        Args:
            task_queue: 任务队列
            
        Returns:
            Dict[str, Any]: 进度信息
        """
        total_tasks = len(task_queue.tasks)
        completed_tasks = task_queue.completed_tasks
        in_progress_tasks = len([
            task for task in task_queue.tasks 
            if task.status == TaskStatus.IN_PROGRESS
        ])
        blocked_tasks = len([
            task for task in task_queue.tasks 
            if task.status == TaskStatus.BLOCKED
        ])
        
        progress_percentage = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "in_progress_tasks": in_progress_tasks,
            "blocked_tasks": blocked_tasks,
            "pending_tasks": total_tasks - completed_tasks - in_progress_tasks - blocked_tasks,
            "progress_percentage": round(progress_percentage, 2),
            "total_estimated_hours": task_queue.total_estimated_hours,
            "completed_hours": sum(
                task.estimated_hours for task in task_queue.tasks 
                if task.status == TaskStatus.COMPLETED
            )
        }
    
    def save_task_queue(self, task_queue: TaskQueue, filename: Optional[str] = None) -> Path:
        """
        保存任务队列到文件
        
        Args:
            task_queue: 任务队列
            filename: 文件名，如果为None则自动生成
            
        Returns:
            Path: 保存的文件路径
        """
        if filename is None:
            filename = f"task_queue_{task_queue.project_id}_{task_queue.stage_id}.json"
        
        save_path = self.aceflow_result_dir / filename
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 序列化任务队列
        queue_data = {
            "project_id": task_queue.project_id,
            "stage_id": task_queue.stage_id,
            "total_estimated_hours": task_queue.total_estimated_hours,
            "completed_tasks": task_queue.completed_tasks,
            "created_at": task_queue.created_at.isoformat(),
            "updated_at": task_queue.updated_at.isoformat(),
            "tasks": [
                {
                    "task_id": task.task_id,
                    "name": task.name,
                    "description": task.description,
                    "status": task.status.value,
                    "priority": task.priority.value,
                    "estimated_hours": task.estimated_hours,
                    "dependencies": task.dependencies,
                    "output_files": task.output_files,
                    "requirements": task.requirements,
                    "acceptance_criteria": task.acceptance_criteria,
                    "tags": task.tags,
                    "assigned_to": task.assigned_to,
                    "created_at": task.created_at.isoformat(),
                    "updated_at": task.updated_at.isoformat(),
                    "metadata": task.metadata
                }
                for task in task_queue.tasks
            ]
        }
        
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(queue_data, f, indent=2, ensure_ascii=False)
        
        return save_path
    
    def load_task_queue(self, file_path: Path) -> TaskQueue:
        """
        从文件加载任务队列
        
        Args:
            file_path: 文件路径
            
        Returns:
            TaskQueue: 加载的任务队列
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            queue_data = json.load(f)
        
        # 反序列化任务
        tasks = []
        for task_data in queue_data["tasks"]:
            task = TaskItem(
                task_id=task_data["task_id"],
                name=task_data["name"],
                description=task_data["description"],
                status=TaskStatus(task_data["status"]),
                priority=TaskPriority(task_data["priority"]),
                estimated_hours=task_data["estimated_hours"],
                dependencies=task_data["dependencies"],
                output_files=task_data["output_files"],
                requirements=task_data["requirements"],
                acceptance_criteria=task_data["acceptance_criteria"],
                tags=task_data["tags"],
                assigned_to=task_data["assigned_to"],
                created_at=datetime.fromisoformat(task_data["created_at"]),
                updated_at=datetime.fromisoformat(task_data["updated_at"]),
                metadata=task_data["metadata"]
            )
            tasks.append(task)
        
        # 创建任务队列
        task_queue = TaskQueue(
            project_id=queue_data["project_id"],
            stage_id=queue_data["stage_id"],
            tasks=tasks,
            total_estimated_hours=queue_data["total_estimated_hours"],
            completed_tasks=queue_data["completed_tasks"],
            created_at=datetime.fromisoformat(queue_data["created_at"]),
            updated_at=datetime.fromisoformat(queue_data["updated_at"])
        )
        
        return task_queue
    
    def _parse_tasks_from_content(self, content: str) -> List[TaskItem]:
        """从内容解析任务列表"""
        tasks = []
        lines = content.split('\n')
        current_task = None
        task_counter = 1
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 检查是否是任务行
            task_match = self._match_task_line(line)
            if task_match:
                # 保存前一个任务
                if current_task:
                    tasks.append(current_task)
                
                # 创建新任务
                task_id = f"T{task_counter:03d}"
                current_task = self.parse_task_from_text(task_match, task_id)
                task_counter += 1
            
            elif current_task and line.startswith('-'):
                # 子任务或详细信息
                self._parse_task_details(current_task, line)
        
        # 添加最后一个任务
        if current_task:
            tasks.append(current_task)
        
        return tasks
    
    def _match_task_line(self, line: str) -> Optional[str]:
        """匹配任务行"""
        for pattern in self.task_patterns:
            match = re.match(pattern, line)
            if match:
                return match.group(1) if len(match.groups()) == 1 else match.group(2)
        return None
    
    def _parse_task_details(self, task: TaskItem, detail_line: str):
        """解析任务详细信息"""
        detail = detail_line.lstrip('- ').strip()
        
        # 检查是否是需求引用
        if detail.startswith('_需求:') or detail.startswith('_Requirements:'):
            req_text = detail.split(':', 1)[1].strip()
            requirements = [req.strip() for req in req_text.split(',')]
            task.requirements.extend(requirements)
        
        # 检查是否是输出文件
        elif detail.startswith('输出:') or detail.startswith('Output:'):
            output_text = detail.split(':', 1)[1].strip()
            outputs = [out.strip() for out in output_text.split(',')]
            task.output_files.extend(outputs)
        
        # 检查是否是验收标准
        elif detail.startswith('验收:') or detail.startswith('Acceptance:'):
            criteria_text = detail.split(':', 1)[1].strip()
            task.acceptance_criteria.append(criteria_text)
        
        # 其他情况作为描述的一部分
        else:
            if task.description:
                task.description += f"\n- {detail}"
            else:
                task.description = detail
    
    def _extract_task_name(self, text: str) -> str:
        """提取任务名称"""
        # 移除标记符号和优先级标记
        cleaned = re.sub(r'^\[.*?\]\s*', '', text)
        cleaned = re.sub(r'^-\s*\[\s*\]\s*', '', cleaned)
        cleaned = re.sub(r'^\d+\.\s*', '', cleaned)
        
        # 提取第一行作为任务名称
        first_line = cleaned.split('\n')[0].strip()
        return first_line
    
    def _extract_task_description(self, text: str) -> str:
        """提取任务描述"""
        lines = text.split('\n')
        if len(lines) > 1:
            return '\n'.join(lines[1:]).strip()
        return ""
    
    def _extract_priority(self, text: str) -> TaskPriority:
        """提取优先级"""
        priority_match = re.search(r'\[([^\]]+)\]', text)
        if priority_match:
            priority_text = priority_match.group(1).lower()
            return self.priority_keywords.get(priority_text, TaskPriority.MEDIUM)
        return TaskPriority.MEDIUM
    
    def _extract_time_estimate(self, text: str) -> float:
        """提取时间估算"""
        for pattern in self.time_patterns:
            match = re.search(pattern, text)
            if match:
                hours = float(match.group(1))
                # 如果是天数，转换为小时
                if '天' in match.group(0) or 'day' in match.group(0) or 'd' in match.group(0):
                    hours *= 8  # 假设一天8小时
                return hours
        return 0.0
    
    def _extract_dependencies(self, text: str) -> List[str]:
        """提取依赖关系"""
        dependencies = []
        dep_patterns = [
            r'依赖[：:]\s*([^，,\n]+)',
            r'depends?\s+on[：:]\s*([^，,\n]+)',
            r'需要[：:]\s*([^，,\n]+)'
        ]
        
        for pattern in dep_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                deps = [dep.strip() for dep in match.split(',')]
                dependencies.extend(deps)
        
        return dependencies
    
    def _extract_output_files(self, text: str) -> List[str]:
        """提取输出文件"""
        output_files = []
        output_patterns = [
            r'输出[：:]\s*([^，,\n]+)',
            r'output[：:]\s*([^，,\n]+)',
            r'生成[：:]\s*([^，,\n]+)'
        ]
        
        for pattern in output_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                files = [file.strip() for file in match.split(',')]
                output_files.extend(files)
        
        return output_files
    
    def _extract_requirements(self, text: str) -> List[str]:
        """提取需求引用"""
        requirements = []
        req_patterns = [
            r'_需求[：:]\s*([^_\n]+)_',
            r'_Requirements[：:]\s*([^_\n]+)_',
            r'需求[：:]\s*([^，,\n]+)'
        ]
        
        for pattern in req_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                reqs = [req.strip() for req in match.split(',')]
                requirements.extend(reqs)
        
        return requirements
    
    def _extract_acceptance_criteria(self, text: str) -> List[str]:
        """提取验收标准"""
        criteria = []
        criteria_patterns = [
            r'验收[：:]\s*([^\n]+)',
            r'acceptance[：:]\s*([^\n]+)',
            r'标准[：:]\s*([^\n]+)'
        ]
        
        for pattern in criteria_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            criteria.extend(matches)
        
        return criteria
    
    def _extract_tags(self, text: str) -> List[str]:
        """提取标签"""
        tags = []
        tag_patterns = [
            r'#(\w+)',
            r'标签[：:]\s*([^，,\n]+)',
            r'tags[：:]\s*([^，,\n]+)'
        ]
        
        for pattern in tag_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if ',' in match:
                    tag_list = [tag.strip() for tag in match.split(',')]
                    tags.extend(tag_list)
                else:
                    tags.append(match.strip())
        
        return tags
    
    def _resolve_task_dependencies(self, task_queue: TaskQueue):
        """解析任务依赖关系"""
        task_name_to_id = {task.name: task.task_id for task in task_queue.tasks}
        
        for task in task_queue.tasks:
            resolved_deps = []
            for dep in task.dependencies:
                if dep in task_name_to_id:
                    resolved_deps.append(task_name_to_id[dep])
                else:
                    # 尝试模糊匹配
                    for name, task_id in task_name_to_id.items():
                        if dep.lower() in name.lower():
                            resolved_deps.append(task_id)
                            break
            
            task.dependencies = resolved_deps
    
    def _generate_task_id(self) -> str:
        """生成任务ID"""
        timestamp = int(datetime.now().timestamp() * 1000)
        return f"T{timestamp}"


# 工厂函数
def create_task_parser(workspace_dir: Optional[Path] = None) -> TaskParser:
    """创建任务解析器实例"""
    return TaskParser(workspace_dir)


# 便捷函数
def parse_task_breakdown(
    document_path: Path,
    project_id: str,
    stage_id: str = "S2_task_breakdown"
) -> TaskQueue:
    """
    便捷的任务分解解析函数
    
    Args:
        document_path: 文档路径
        project_id: 项目ID
        stage_id: 阶段ID
        
    Returns:
        TaskQueue: 解析后的任务队列
    """
    parser = create_task_parser()
    return parser.parse_task_breakdown_document(document_path, project_id, stage_id)