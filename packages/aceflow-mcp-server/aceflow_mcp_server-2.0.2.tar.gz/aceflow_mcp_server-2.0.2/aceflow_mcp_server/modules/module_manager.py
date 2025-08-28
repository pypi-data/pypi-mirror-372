"""
模块管理器
Module Manager

This module provides centralized management for all functional modules
in the AceFlow MCP Server, including dependency resolution, lifecycle
management, and lazy loading.
"""

from typing import Dict, List, Set, Optional, Type, Any
import logging
from collections import defaultdict, deque
import time

from .base_module import BaseModule, ModuleState, ModuleError, ModuleMetadata

logger = logging.getLogger(__name__)


class DependencyError(Exception):
    """依赖错误异常"""
    pass


class ModuleManager:
    """
    模块管理器
    
    负责管理所有功能模块的生命周期，包括：
    - 模块注册和发现
    - 依赖解析和管理
    - 懒加载和按需初始化
    - 健康检查和监控
    - 优雅关闭
    """
    
    def __init__(self):
        # 模块注册表
        self._modules: Dict[str, BaseModule] = {}
        self._module_classes: Dict[str, Type[BaseModule]] = {}
        self._module_configs: Dict[str, Any] = {}
        
        # 依赖图
        self._dependency_graph: Dict[str, Set[str]] = defaultdict(set)
        self._reverse_dependency_graph: Dict[str, Set[str]] = defaultdict(set)
        
        # 初始化顺序
        self._initialization_order: List[str] = []
        self._shutdown_order: List[str] = []
        
        # 状态跟踪
        self._initialized_modules: Set[str] = set()
        self._failed_modules: Set[str] = set()
        
        logger.info("Module manager initialized")
    
    def register_module_class(
        self, 
        name: str, 
        module_class: Type[BaseModule], 
        config: Any,
        metadata: Optional[ModuleMetadata] = None
    ):
        """
        注册模块类
        
        Args:
            name: 模块名称
            module_class: 模块类
            config: 模块配置
            metadata: 模块元数据
        """
        if name in self._module_classes:
            logger.warning(f"Module class '{name}' already registered, overwriting")
        
        self._module_classes[name] = module_class
        self._module_configs[name] = config
        
        # 如果提供了元数据，构建依赖图
        if metadata:
            self._dependency_graph[name] = set(metadata.dependencies)
            for dep in metadata.dependencies:
                self._reverse_dependency_graph[dep].add(name)
        
        logger.info(f"Registered module class: {name}")
    
    def register_module_instance(self, module: BaseModule):
        """
        注册模块实例
        
        Args:
            module: 模块实例
        """
        name = module.get_module_name()
        
        if name in self._modules:
            logger.warning(f"Module instance '{name}' already registered, overwriting")
        
        self._modules[name] = module
        
        # 构建依赖图
        dependencies = module.get_required_dependencies()
        self._dependency_graph[name] = dependencies
        for dep in dependencies:
            self._reverse_dependency_graph[dep].add(name)
        
        logger.info(f"Registered module instance: {name}")
    
    def get_module(self, name: str) -> Optional[BaseModule]:
        """
        获取模块实例（懒加载）
        
        Args:
            name: 模块名称
            
        Returns:
            模块实例或None
        """
        # 如果模块已存在，直接返回
        if name in self._modules:
            return self._modules[name]
        
        # 如果有注册的模块类，创建实例
        if name in self._module_classes:
            try:
                module_class = self._module_classes[name]
                config = self._module_configs[name]
                
                # 创建模块实例
                module = module_class(config)
                self._modules[name] = module
                
                logger.info(f"Created module instance: {name}")
                return module
                
            except Exception as e:
                logger.error(f"Failed to create module instance '{name}': {e}")
                self._failed_modules.add(name)
                return None
        
        logger.warning(f"Module '{name}' not found")
        return None
    
    def initialize_module(self, name: str, force: bool = False) -> bool:
        """
        初始化模块
        
        Args:
            name: 模块名称
            force: 是否强制重新初始化
            
        Returns:
            初始化是否成功
        """
        if name in self._initialized_modules and not force:
            logger.debug(f"Module '{name}' already initialized")
            return True
        
        if name in self._failed_modules and not force:
            logger.warning(f"Module '{name}' previously failed, skipping")
            return False
        
        # 获取模块实例
        module = self.get_module(name)
        if not module:
            logger.error(f"Cannot initialize module '{name}': module not found")
            self._failed_modules.add(name)
            return False
        
        # 检查并初始化依赖
        dependencies = module.get_required_dependencies()
        for dep in dependencies:
            if not self.initialize_module(dep):
                logger.error(f"Cannot initialize module '{name}': dependency '{dep}' failed")
                self._failed_modules.add(name)
                return False
            
            # 标记依赖已解决
            module.mark_dependency_resolved(dep)
        
        # 初始化模块
        try:
            success = module.initialize()
            if success:
                self._initialized_modules.add(name)
                logger.info(f"Module '{name}' initialized successfully")
                return True
            else:
                self._failed_modules.add(name)
                logger.error(f"Module '{name}' initialization failed")
                return False
                
        except Exception as e:
            self._failed_modules.add(name)
            logger.error(f"Module '{name}' initialization error: {e}")
            return False
    
    def initialize_all_modules(self) -> bool:
        """
        初始化所有模块
        
        Returns:
            是否所有模块都初始化成功
        """
        logger.info("Initializing all modules...")
        
        # 计算初始化顺序
        self._calculate_initialization_order()
        
        success = True
        for module_name in self._initialization_order:
            if not self.initialize_module(module_name):
                success = False
        
        # 初始化剩余的模块（没有依赖关系的）
        for module_name in self._module_classes.keys():
            if module_name not in self._initialized_modules:
                if not self.initialize_module(module_name):
                    success = False
        
        logger.info(f"Module initialization complete. Success: {success}")
        return success
    
    def shutdown_module(self, name: str):
        """
        关闭模块
        
        Args:
            name: 模块名称
        """
        if name not in self._modules:
            logger.warning(f"Module '{name}' not found for shutdown")
            return
        
        # 先关闭依赖此模块的其他模块
        dependents = self._reverse_dependency_graph.get(name, set())
        for dependent in dependents:
            if dependent in self._initialized_modules:
                self.shutdown_module(dependent)
        
        # 关闭模块
        module = self._modules[name]
        try:
            module.cleanup()
            self._initialized_modules.discard(name)
            logger.info(f"Module '{name}' shut down successfully")
        except Exception as e:
            logger.error(f"Module '{name}' shutdown error: {e}")
    
    def shutdown_all_modules(self):
        """关闭所有模块"""
        logger.info("Shutting down all modules...")
        
        # 计算关闭顺序（初始化顺序的逆序）
        self._calculate_shutdown_order()
        
        for module_name in self._shutdown_order:
            if module_name in self._initialized_modules:
                self.shutdown_module(module_name)
        
        logger.info("All modules shut down")
    
    def get_module_status(self, name: str) -> Dict[str, Any]:
        """
        获取模块状态
        
        Args:
            name: 模块名称
            
        Returns:
            模块状态信息
        """
        if name not in self._modules:
            return {
                "name": name,
                "status": "not_found",
                "registered": name in self._module_classes
            }
        
        module = self._modules[name]
        return module.get_module_info()
    
    def get_all_modules_status(self) -> Dict[str, Dict[str, Any]]:
        """获取所有模块状态"""
        status = {}
        
        # 已注册的模块类
        for name in self._module_classes.keys():
            status[name] = self.get_module_status(name)
        
        # 直接注册的模块实例
        for name in self._modules.keys():
            if name not in status:
                status[name] = self.get_module_status(name)
        
        return status
    
    def health_check(self) -> Dict[str, Any]:
        """
        执行健康检查
        
        Returns:
            健康检查结果
        """
        logger.debug("Performing health check...")
        
        healthy_modules = []
        unhealthy_modules = []
        disabled_modules = []
        
        for name, module in self._modules.items():
            if not module.enabled:
                disabled_modules.append(name)
            elif module.is_healthy():
                healthy_modules.append(name)
            else:
                unhealthy_modules.append(name)
        
        overall_health = len(unhealthy_modules) == 0
        
        return {
            "overall_healthy": overall_health,
            "healthy_modules": healthy_modules,
            "unhealthy_modules": unhealthy_modules,
            "disabled_modules": disabled_modules,
            "total_modules": len(self._modules),
            "initialized_modules": len(self._initialized_modules),
            "failed_modules": len(self._failed_modules),
            "timestamp": time.time()
        }
    
    def reload_module(self, name: str) -> bool:
        """
        重新加载模块
        
        Args:
            name: 模块名称
            
        Returns:
            重新加载是否成功
        """
        logger.info(f"Reloading module: {name}")
        
        # 关闭模块
        if name in self._initialized_modules:
            self.shutdown_module(name)
        
        # 清除失败状态
        self._failed_modules.discard(name)
        
        # 重新初始化
        return self.initialize_module(name, force=True)
    
    def update_module_config(self, name: str, new_config: Any) -> bool:
        """
        更新模块配置
        
        Args:
            name: 模块名称
            new_config: 新配置
            
        Returns:
            更新是否成功
        """
        # 更新配置存储
        self._module_configs[name] = new_config
        
        # 如果模块已存在，更新其配置
        if name in self._modules:
            module = self._modules[name]
            return module.update_config(new_config)
        
        return True
    
    def _calculate_initialization_order(self):
        """计算模块初始化顺序（拓扑排序）"""
        # 使用Kahn算法进行拓扑排序
        in_degree = defaultdict(int)
        
        # 计算入度
        for module in self._dependency_graph:
            for dep in self._dependency_graph[module]:
                in_degree[module] += 1
        
        # 找到入度为0的节点
        queue = deque([module for module in self._module_classes.keys() if in_degree[module] == 0])
        order = []
        
        while queue:
            current = queue.popleft()
            order.append(current)
            
            # 减少依赖此模块的其他模块的入度
            for dependent in self._reverse_dependency_graph.get(current, set()):
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)
        
        # 检查是否有循环依赖
        if len(order) != len(self._module_classes):
            remaining = set(self._module_classes.keys()) - set(order)
            logger.warning(f"Circular dependency detected among modules: {remaining}")
            # 将剩余模块添加到顺序中
            order.extend(remaining)
        
        self._initialization_order = order
        logger.debug(f"Module initialization order: {order}")
    
    def _calculate_shutdown_order(self):
        """计算模块关闭顺序（初始化顺序的逆序）"""
        if not self._initialization_order:
            self._calculate_initialization_order()
        
        self._shutdown_order = list(reversed(self._initialization_order))
        logger.debug(f"Module shutdown order: {self._shutdown_order}")
    
    def get_dependency_graph(self) -> Dict[str, Set[str]]:
        """获取依赖图"""
        return dict(self._dependency_graph)
    
    def get_initialization_order(self) -> List[str]:
        """获取初始化顺序"""
        if not self._initialization_order:
            self._calculate_initialization_order()
        return self._initialization_order.copy()
    
    def list_modules(self) -> List[str]:
        """列出所有模块名称"""
        all_modules = set(self._module_classes.keys())
        all_modules.update(self._modules.keys())
        return sorted(all_modules)
    
    def is_module_available(self, name: str) -> bool:
        """检查模块是否可用"""
        module = self.get_module(name)
        return module is not None and module.is_available()
    
    def get_available_modules(self) -> List[str]:
        """获取所有可用模块"""
        available = []
        for name in self.list_modules():
            if self.is_module_available(name):
                available.append(name)
        return available
    
    def __repr__(self) -> str:
        return f"ModuleManager(modules={len(self._modules)}, initialized={len(self._initialized_modules)}, failed={len(self._failed_modules)})"