"""
基础模块类和接口
Base Module Classes and Interfaces

This module defines the base classes and interfaces for all functional modules
in the AceFlow MCP Server unified architecture.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Set
from enum import Enum
import logging
import time
from pathlib import Path

logger = logging.getLogger(__name__)


class ModuleState(Enum):
    """模块状态枚举"""
    UNINITIALIZED = "uninitialized"
    INITIALIZING = "initializing"
    READY = "ready"
    RUNNING = "running"
    ERROR = "error"
    DISABLED = "disabled"
    SHUTTING_DOWN = "shutting_down"
    SHUTDOWN = "shutdown"


class ModuleError(Exception):
    """模块错误异常"""
    def __init__(self, module_name: str, message: str, cause: Optional[Exception] = None):
        self.module_name = module_name
        self.message = message
        self.cause = cause
        super().__init__(f"Module '{module_name}': {message}")


@dataclass
class ModuleMetadata:
    """模块元数据"""
    name: str
    version: str = "1.0.0"
    description: str = ""
    dependencies: List[str] = field(default_factory=list)
    optional_dependencies: List[str] = field(default_factory=list)
    provides: List[str] = field(default_factory=list)
    tags: Set[str] = field(default_factory=set)


@dataclass
class ModuleStats:
    """模块统计信息"""
    initialization_time: float = 0.0
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    last_call_time: Optional[float] = None
    average_call_duration: float = 0.0
    memory_usage_mb: float = 0.0


class BaseModule(ABC):
    """
    基础模块抽象类
    
    所有功能模块都必须继承此类并实现抽象方法。
    提供模块生命周期管理、状态跟踪、错误处理等基础功能。
    """
    
    def __init__(self, config: Any, metadata: Optional[ModuleMetadata] = None):
        """
        初始化基础模块
        
        Args:
            config: 模块配置对象
            metadata: 模块元数据
        """
        self.config = config
        self.metadata = metadata or ModuleMetadata(name=self.__class__.__name__)
        
        # 状态管理
        self._state = ModuleState.UNINITIALIZED
        self._enabled = getattr(config, 'enabled', True)
        self._initialized = False
        self._last_error: Optional[Exception] = None
        
        # 统计信息
        self.stats = ModuleStats()
        
        # 依赖管理
        self._dependencies: Set[str] = set(self.metadata.dependencies)
        self._optional_dependencies: Set[str] = set(self.metadata.optional_dependencies)
        self._resolved_dependencies: Set[str] = set()
        
        # 生命周期钩子
        self._initialization_hooks: List[callable] = []
        self._shutdown_hooks: List[callable] = []
        
        logger.debug(f"Created module: {self.get_module_name()}")
    
    @property
    def state(self) -> ModuleState:
        """获取模块状态"""
        return self._state
    
    @property
    def enabled(self) -> bool:
        """检查模块是否启用"""
        return self._enabled
    
    @property
    def initialized(self) -> bool:
        """检查模块是否已初始化"""
        return self._initialized
    
    @property
    def last_error(self) -> Optional[Exception]:
        """获取最后一次错误"""
        return self._last_error
    
    # 抽象方法 - 子类必须实现
    
    @abstractmethod
    def get_module_name(self) -> str:
        """获取模块名称"""
        pass
    
    @abstractmethod
    def _do_initialize(self) -> bool:
        """执行模块初始化逻辑"""
        pass
    
    @abstractmethod
    def _do_cleanup(self):
        """执行模块清理逻辑"""
        pass
    
    @abstractmethod
    def get_health_status(self) -> Dict[str, Any]:
        """获取模块健康状态"""
        pass
    
    # 生命周期管理方法
    
    def initialize(self) -> bool:
        """
        初始化模块
        
        Returns:
            bool: 初始化是否成功
        """
        if not self._enabled:
            logger.info(f"Module {self.get_module_name()} is disabled, skipping initialization")
            self._state = ModuleState.DISABLED
            return True
        
        if self._initialized:
            logger.debug(f"Module {self.get_module_name()} already initialized")
            return True
        
        logger.info(f"Initializing module: {self.get_module_name()}")
        self._state = ModuleState.INITIALIZING
        
        try:
            start_time = time.time()
            
            # 执行初始化钩子
            for hook in self._initialization_hooks:
                try:
                    hook()
                except Exception as e:
                    logger.warning(f"Initialization hook failed: {e}")
            
            # 执行具体的初始化逻辑
            success = self._do_initialize()
            
            if success:
                self._initialized = True
                self._state = ModuleState.READY
                self.stats.initialization_time = time.time() - start_time
                logger.info(f"Module {self.get_module_name()} initialized successfully in {self.stats.initialization_time:.3f}s")
                return True
            else:
                self._state = ModuleState.ERROR
                logger.error(f"Module {self.get_module_name()} initialization failed")
                return False
                
        except Exception as e:
            self._last_error = e
            self._state = ModuleState.ERROR
            logger.error(f"Module {self.get_module_name()} initialization error: {e}")
            return False
    
    def cleanup(self):
        """清理模块资源"""
        if self._state == ModuleState.SHUTDOWN:
            return
        
        logger.info(f"Cleaning up module: {self.get_module_name()}")
        self._state = ModuleState.SHUTTING_DOWN
        
        try:
            # 执行清理钩子
            for hook in self._shutdown_hooks:
                try:
                    hook()
                except Exception as e:
                    logger.warning(f"Shutdown hook failed: {e}")
            
            # 执行具体的清理逻辑
            self._do_cleanup()
            
            self._state = ModuleState.SHUTDOWN
            self._initialized = False
            logger.info(f"Module {self.get_module_name()} cleaned up successfully")
            
        except Exception as e:
            self._last_error = e
            self._state = ModuleState.ERROR
            logger.error(f"Module {self.get_module_name()} cleanup error: {e}")
    
    def ensure_initialized(self) -> bool:
        """确保模块已初始化"""
        if not self._initialized and self._enabled:
            return self.initialize()
        return self._initialized or not self._enabled
    
    def is_available(self) -> bool:
        """检查模块是否可用"""
        return (
            self._enabled and 
            self._initialized and 
            self._state in [ModuleState.READY, ModuleState.RUNNING]
        )
    
    def is_healthy(self) -> bool:
        """检查模块是否健康"""
        if not self.is_available():
            return False
        
        try:
            health_status = self.get_health_status()
            return health_status.get('healthy', False)
        except Exception as e:
            logger.error(f"Health check failed for module {self.get_module_name()}: {e}")
            return False
    
    # 依赖管理
    
    def add_dependency(self, dependency: str, optional: bool = False):
        """添加依赖"""
        if optional:
            self._optional_dependencies.add(dependency)
        else:
            self._dependencies.add(dependency)
    
    def remove_dependency(self, dependency: str):
        """移除依赖"""
        self._dependencies.discard(dependency)
        self._optional_dependencies.discard(dependency)
    
    def get_dependencies(self) -> Set[str]:
        """获取所有依赖"""
        return self._dependencies.union(self._optional_dependencies)
    
    def get_required_dependencies(self) -> Set[str]:
        """获取必需依赖"""
        return self._dependencies.copy()
    
    def get_optional_dependencies(self) -> Set[str]:
        """获取可选依赖"""
        return self._optional_dependencies.copy()
    
    def mark_dependency_resolved(self, dependency: str):
        """标记依赖已解决"""
        self._resolved_dependencies.add(dependency)
    
    def are_dependencies_resolved(self) -> bool:
        """检查依赖是否已解决"""
        return self._dependencies.issubset(self._resolved_dependencies)
    
    # 生命周期钩子
    
    def add_initialization_hook(self, hook: callable):
        """添加初始化钩子"""
        self._initialization_hooks.append(hook)
    
    def add_shutdown_hook(self, hook: callable):
        """添加关闭钩子"""
        self._shutdown_hooks.append(hook)
    
    # 统计和监控
    
    def record_call(self, success: bool = True, duration: float = 0.0):
        """记录调用统计"""
        self.stats.total_calls += 1
        self.stats.last_call_time = time.time()
        
        if success:
            self.stats.successful_calls += 1
        else:
            self.stats.failed_calls += 1
        
        # 更新平均调用时间
        if duration > 0:
            total_duration = self.stats.average_call_duration * (self.stats.total_calls - 1) + duration
            self.stats.average_call_duration = total_duration / self.stats.total_calls
    
    def get_success_rate(self) -> float:
        """获取成功率"""
        if self.stats.total_calls == 0:
            return 0.0
        return self.stats.successful_calls / self.stats.total_calls
    
    def reset_stats(self):
        """重置统计信息"""
        self.stats = ModuleStats()
    
    # 配置管理
    
    def update_config(self, new_config: Any) -> bool:
        """更新配置"""
        try:
            old_enabled = self._enabled
            self.config = new_config
            self._enabled = getattr(new_config, 'enabled', True)
            
            # 如果启用状态改变，需要重新初始化
            if old_enabled != self._enabled:
                if self._enabled and not self._initialized:
                    return self.initialize()
                elif not self._enabled and self._initialized:
                    self.cleanup()
            
            logger.info(f"Module {self.get_module_name()} configuration updated")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update configuration for module {self.get_module_name()}: {e}")
            return False
    
    # 调试和诊断
    
    def get_module_info(self) -> Dict[str, Any]:
        """获取模块信息"""
        return {
            "name": self.get_module_name(),
            "metadata": {
                "version": self.metadata.version,
                "description": self.metadata.description,
                "dependencies": list(self.metadata.dependencies),
                "optional_dependencies": list(self.metadata.optional_dependencies),
                "provides": list(self.metadata.provides),
                "tags": list(self.metadata.tags)
            },
            "state": self._state.value,
            "enabled": self._enabled,
            "initialized": self._initialized,
            "available": self.is_available(),
            "healthy": self.is_healthy(),
            "dependencies_resolved": self.are_dependencies_resolved(),
            "stats": {
                "initialization_time": self.stats.initialization_time,
                "total_calls": self.stats.total_calls,
                "successful_calls": self.stats.successful_calls,
                "failed_calls": self.stats.failed_calls,
                "success_rate": self.get_success_rate(),
                "average_call_duration": self.stats.average_call_duration,
                "last_call_time": self.stats.last_call_time,
                "memory_usage_mb": self.stats.memory_usage_mb
            },
            "last_error": str(self._last_error) if self._last_error else None
        }
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.get_module_name()}', state='{self._state.value}', enabled={self._enabled})"