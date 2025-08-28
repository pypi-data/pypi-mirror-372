"""
AceFlow MCP数据管理模块
负责管理AI Agent分析数据、阶段输出和项目状态
优化版本：支持缓存、并发和批处理
"""

import json
import os
import asyncio
import threading
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
import uuid
from concurrent.futures import ThreadPoolExecutor
import hashlib


class DataManager:
    """AceFlow项目数据管理器 (性能优化版)
    
    职责：
    1. 管理AI Agent提供的分析数据
    2. 管理阶段输出数据
    3. 维护项目状态一致性
    4. 提供数据验证和缓存功能
    5. 支持并发操作和批处理
    """
    
    def __init__(self, working_directory: str = "."):
        self.working_dir = Path(working_directory)
        self.aceflow_dir = self.working_dir / ".aceflow"
        
        # 数据文件路径
        self.state_file = self.aceflow_dir / "current_state.json"
        self.analysis_file = self.aceflow_dir / "analysis_data.json"
        self.outputs_dir = self.aceflow_dir / "stage_outputs"
        self.cache_dir = self.aceflow_dir / "cache"
        
        # 性能优化组件
        self._memory_cache = {}  # 内存缓存
        self._cache_ttl = {}     # 缓存TTL
        self._lock = threading.RLock()  # 线程安全锁
        self._executor = ThreadPoolExecutor(max_workers=4)  # 线程池
        self._batch_operations = []  # 批处理队列
        
        # 缓存配置
        self.cache_timeout = 300  # 5分钟缓存过期
        self.batch_size = 10      # 批处理大小
        
        # 确保目录存在
        self._ensure_directories()
    
    def _ensure_directories(self):
        """确保所有必需的目录存在"""
        self.aceflow_dir.mkdir(exist_ok=True)
        self.outputs_dir.mkdir(exist_ok=True)
        self.cache_dir.mkdir(exist_ok=True)
        (self.cache_dir / "templates").mkdir(exist_ok=True)
        (self.cache_dir / "computed").mkdir(exist_ok=True)
    
    # ========== 分析数据管理 ==========
    
    def save_analysis_data(self, data: Dict[str, Any]) -> bool:
        """保存AI Agent提供的分析数据
        
        Args:
            data: 分析数据字典，包含project_info, code_metrics, test_metrics等
            
        Returns:
            bool: 保存是否成功
        """
        try:
            # 验证数据格式
            if not self._validate_analysis_data(data):
                return False
            
            # 加载现有数据或创建新数据
            existing_data = self.load_analysis_data() or {}
            
            # 合并数据（增量更新）
            merged_data = self._merge_analysis_data(existing_data, data)
            
            # 添加元数据
            merged_data["_metadata"] = {
                "last_updated": datetime.now().isoformat(),
                "update_id": str(uuid.uuid4())[:8],
                "version": "2.0"
            }
            
            # 保存到文件
            with open(self.analysis_file, 'w', encoding='utf-8') as f:
                json.dump(merged_data, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"[ERROR] 保存分析数据失败: {e}")
            return False
    
    def load_analysis_data(self) -> Optional[Dict[str, Any]]:
        """加载分析数据"""
        try:
            if not self.analysis_file.exists():
                return None
                
            with open(self.analysis_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data
                
        except Exception as e:
            print(f"[ERROR] 加载分析数据失败: {e}")
            return None
    
    def _validate_analysis_data(self, data: Dict[str, Any]) -> bool:
        """验证分析数据格式"""
        required_sections = ["project_info", "code_metrics", "test_metrics"]
        
        for section in required_sections:
            if section not in data:
                print(f"[WARN] 缺少必需的数据section: {section}")
                # 不强制要求，允许部分数据
        
        return True
    
    def _merge_analysis_data(self, existing: Dict, new: Dict) -> Dict:
        """智能合并分析数据"""
        result = existing.copy()
        
        for key, value in new.items():
            if isinstance(value, dict) and key in result and isinstance(result[key], dict):
                # 递归合并字典
                result[key] = {**result[key], **value}
            else:
                # 直接覆盖或新增
                result[key] = value
        
        return result
    
    # ========== 阶段输出管理 ==========
    
    def save_stage_output(self, stage: str, data: Dict[str, Any]) -> bool:
        """保存阶段输出数据
        
        Args:
            stage: 阶段ID，如 's1_user_story'
            data: 阶段输出数据，包含content和metadata
            
        Returns:
            bool: 保存是否成功
        """
        try:
            # 验证数据格式
            if not self._validate_stage_output(data):
                return False
            
            # 添加元数据
            output_data = {
                **data,
                "_metadata": {
                    "stage_id": stage,
                    "saved_at": datetime.now().isoformat(),
                    "save_id": str(uuid.uuid4())[:8]
                }
            }
            
            # 保存到文件
            output_file = self.outputs_dir / f"{stage}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            # 更新项目状态
            self._update_stage_completion(stage)
            
            return True
            
        except Exception as e:
            print(f"[ERROR] 保存阶段输出失败: {e}")
            return False
    
    def load_stage_output(self, stage: str) -> Optional[Dict[str, Any]]:
        """加载指定阶段的输出数据"""
        try:
            output_file = self.outputs_dir / f"{stage}.json"
            if not output_file.exists():
                return None
                
            with open(output_file, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        except Exception as e:
            print(f"[ERROR] 加载阶段输出失败 {stage}: {e}")
            return None
    
    def get_previous_outputs(self, current_stage: str) -> Dict[str, Dict[str, Any]]:
        """获取当前阶段的前置阶段输出
        
        Args:
            current_stage: 当前阶段ID
            
        Returns:
            Dict: {stage_id: output_data} 格式的前置输出数据
        """
        try:
            # 定义阶段顺序和依赖关系
            stage_dependencies = self._get_stage_dependencies()
            
            # 获取当前阶段的依赖
            dependencies = stage_dependencies.get(current_stage, [])
            
            # 收集依赖阶段的输出
            previous_outputs = {}
            for dep_stage in dependencies:
                output_data = self.load_stage_output(dep_stage)
                if output_data:
                    # 只返回内容部分，过滤元数据
                    previous_outputs[dep_stage] = {
                        "content": output_data.get("content", ""),
                        "metadata": output_data.get("metadata", {}),
                        "key_points": self._extract_key_points(output_data.get("content", ""))
                    }
            
            return previous_outputs
            
        except Exception as e:
            print(f"[ERROR] 获取前置输出失败: {e}")
            return {}
    
    def _validate_stage_output(self, data: Dict[str, Any]) -> bool:
        """验证阶段输出数据格式"""
        if "content" not in data:
            print("[ERROR] 阶段输出缺少content字段")
            return False
        
        return True
    
    def _extract_key_points(self, content: str) -> List[str]:
        """从内容中提取关键点（简单实现）"""
        if not content:
            return []
        
        # 简单提取：找到列表项或标题
        lines = content.split('\n')
        key_points = []
        
        for line in lines:
            line = line.strip()
            if line.startswith('- ') or line.startswith('* '):
                key_points.append(line[2:])
            elif line.startswith('## '):
                key_points.append(line[3:])
            
            # 限制数量
            if len(key_points) >= 10:
                break
        
        return key_points
    
    # ========== 项目状态管理 ==========
    
    def load_project_state(self) -> Optional[Dict[str, Any]]:
        """加载项目状态"""
        try:
            if not self.state_file.exists():
                return None
                
            with open(self.state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        except Exception as e:
            print(f"[ERROR] 加载项目状态失败: {e}")
            return None
    
    def save_project_state(self, state: Dict[str, Any]) -> bool:
        """保存项目状态"""
        try:
            # 添加更新时间
            state.setdefault("project", {})["last_updated"] = datetime.now().isoformat()
            
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
                
            return True
            
        except Exception as e:
            print(f"[ERROR] 保存项目状态失败: {e}")
            return False
    
    def _update_stage_completion(self, stage: str):
        """更新阶段完成状态"""
        try:
            state = self.load_project_state()
            if not state:
                return
            
            # 更新完成的阶段列表
            completed_stages = state.get("flow", {}).get("completed_stages", [])
            if stage not in completed_stages:
                completed_stages.append(stage)
                state["flow"]["completed_stages"] = completed_stages
            
            # 更新进度百分比
            mode = state.get("project", {}).get("mode", "standard")
            total_stages = self._get_stage_count(mode)
            progress = int((len(completed_stages) / total_stages) * 100)
            state["flow"]["progress_percentage"] = progress
            
            # 保存状态
            self.save_project_state(state)
            
        except Exception as e:
            print(f"[ERROR] 更新阶段完成状态失败: {e}")
    
    # ========== 辅助方法 ==========
    
    def _get_stage_dependencies(self) -> Dict[str, List[str]]:
        """定义阶段依赖关系"""
        return {
            "s2_tasks_group": ["s1_user_story"],
            "s3_testcases": ["s1_user_story", "s2_tasks_group"],
            "s4_implementation": ["s2_tasks_group", "s3_testcases"],
            "s5_test_report": ["s4_implementation"],
            "s6_codereview": ["s4_implementation", "s5_test_report"],
            "s7_demo_script": ["s4_implementation"],
            "s8_summary_report": ["s5_test_report", "s6_codereview"]
        }
    
    def _get_stage_count(self, mode: str) -> int:
        """获取模式对应的总阶段数"""
        stage_counts = {
            "minimal": 3,
            "standard": 6,
            "complete": 8,
            "smart": 10
        }
        return stage_counts.get(mode, 8)
    
    # ========== 数据清理和维护 ==========
    
    def cleanup_old_data(self, days: int = 30):
        """清理旧数据"""
        try:
            import time
            cutoff_time = time.time() - (days * 24 * 60 * 60)
            
            # 清理旧的输出文件
            for file_path in self.outputs_dir.glob("*.json"):
                if file_path.stat().st_mtime < cutoff_time:
                    file_path.unlink()
                    
            # 清理缓存
            for file_path in self.cache_dir.rglob("*"):
                if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                    file_path.unlink()
                    
        except Exception as e:
            print(f"[ERROR] 清理旧数据失败: {e}")
    
    def get_storage_info(self) -> Dict[str, Any]:
        """获取存储信息统计"""
        try:
            def get_dir_size(path: Path) -> int:
                return sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
            
            return {
                "total_size_mb": round(get_dir_size(self.aceflow_dir) / 1024 / 1024, 2),
                "analysis_data_size_kb": round(self.analysis_file.stat().st_size / 1024, 2) if self.analysis_file.exists() else 0,
                "stage_outputs_count": len(list(self.outputs_dir.glob("*.json"))),
                "cache_size_mb": round(get_dir_size(self.cache_dir) / 1024 / 1024, 2)
            }
            
        except Exception as e:
            print(f"[ERROR] 获取存储信息失败: {e}")
            return {"error": str(e)}
    
    # ========== 性能优化方法 ==========
    
    def _get_cache_key(self, key: str, data: Any = None) -> str:
        """生成缓存键"""
        if data:
            # 对数据进行哈希以生成唯一键
            data_str = json.dumps(data, sort_keys=True, ensure_ascii=False)
            hash_key = hashlib.md5(data_str.encode()).hexdigest()[:8]
            return f"{key}_{hash_key}"
        return key
    
    def _is_cache_valid(self, key: str) -> bool:
        """检查缓存是否有效"""
        if key not in self._cache_ttl:
            return False
        return datetime.now() < self._cache_ttl[key]
    
    def _get_from_cache(self, key: str) -> Optional[Any]:
        """从内存缓存获取数据"""
        with self._lock:
            if key in self._memory_cache and self._is_cache_valid(key):
                return self._memory_cache[key]
        return None
    
    def _set_cache(self, key: str, value: Any, ttl_seconds: int = None):
        """设置内存缓存"""
        ttl_seconds = ttl_seconds or self.cache_timeout
        with self._lock:
            self._memory_cache[key] = value
            self._cache_ttl[key] = datetime.now() + timedelta(seconds=ttl_seconds)
    
    def _clear_expired_cache(self):
        """清理过期缓存"""
        with self._lock:
            now = datetime.now()
            expired_keys = [k for k, v in self._cache_ttl.items() if now >= v]
            for key in expired_keys:
                self._memory_cache.pop(key, None)
                self._cache_ttl.pop(key, None)
    
    async def save_analysis_data_async(self, data: Dict[str, Any]) -> bool:
        """异步保存分析数据"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self._executor, self.save_analysis_data, data)
    
    async def save_stage_output_async(self, stage: str, data: Dict[str, Any]) -> bool:
        """异步保存阶段输出"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self._executor, self.save_stage_output, stage, data)
    
    def add_to_batch(self, operation: str, *args, **kwargs):
        """添加操作到批处理队列"""
        with self._lock:
            self._batch_operations.append({
                'operation': operation,
                'args': args,
                'kwargs': kwargs,
                'timestamp': datetime.now()
            })
            
            # 达到批处理大小时自动执行
            if len(self._batch_operations) >= self.batch_size:
                self._execute_batch()
    
    def _execute_batch(self):
        """执行批处理操作"""
        if not self._batch_operations:
            return
            
        operations = self._batch_operations.copy()
        self._batch_operations.clear()
        
        # 并发执行批处理操作
        futures = []
        for op in operations:
            if op['operation'] == 'save_analysis':
                future = self._executor.submit(self.save_analysis_data, *op['args'], **op['kwargs'])
            elif op['operation'] == 'save_output':
                future = self._executor.submit(self.save_stage_output, *op['args'], **op['kwargs'])
            else:
                continue
            futures.append(future)
        
        # 等待所有操作完成
        for future in futures:
            try:
                future.result(timeout=30)  # 30秒超时
            except Exception as e:
                print(f"[ERROR] 批处理操作失败: {e}")
    
    def flush_batch(self):
        """强制执行所有待处理的批操作"""
        with self._lock:
            if self._batch_operations:
                self._execute_batch()
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """获取性能指标"""
        with self._lock:
            return {
                "cache_size": len(self._memory_cache),
                "cache_hit_ratio": getattr(self, '_cache_hits', 0) / max(getattr(self, '_cache_requests', 1), 1),
                "batch_queue_size": len(self._batch_operations),
                "thread_pool_active": self._executor._threads and len([t for t in self._executor._threads if t.is_alive()]),
                "memory_cache_keys": list(self._memory_cache.keys()),
                "expired_cache_count": len([k for k, v in self._cache_ttl.items() if datetime.now() >= v])
            }
    
    def __del__(self):
        """清理资源"""
        if hasattr(self, '_executor'):
            self._executor.shutdown(wait=False)