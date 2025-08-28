#!/usr/bin/env python3
"""
配置自动迁移器
Configuration Auto-Migrator

将旧的aceflow-server和aceflow-enhanced-server配置迁移到统一配置格式
"""
import os
import json
import shutil
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
import uuid

from .config_detector import (
    ConfigurationDetector, ConfigDetectionResult, ConfigType, ConfigFormat
)

logger = logging.getLogger(__name__)

class MigrationStrategy(Enum):
    """迁移策略枚举"""
    REPLACE = "replace"  # 替换原配置
    BACKUP_AND_REPLACE = "backup_and_replace"  # 备份后替换
    CREATE_NEW = "create_new"  # 创建新配置文件
    MERGE = "merge"  # 合并到现有统一配置

class MigrationStatus(Enum):
    """迁移状态枚举"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"

@dataclass
class MigrationResult:
    """迁移结果数据结构"""
    migration_id: str
    source_file: str
    target_file: str
    source_type: ConfigType
    strategy: MigrationStrategy
    status: MigrationStatus
    
    # 迁移详情
    backup_file: Optional[str] = None
    changes_made: List[str] = None
    warnings: List[str] = None
    errors: List[str] = None
    
    # 验证结果
    validation_passed: bool = False
    validation_errors: List[str] = None
    
    # 时间戳
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.changes_made is None:
            self.changes_made = []
        if self.warnings is None:
            self.warnings = []
        if self.errors is None:
            self.errors = []
        if self.validation_errors is None:
            self.validation_errors = []

class ConfigurationMigrator:
    """配置自动迁移器"""
    
    def __init__(self, detector: Optional[ConfigurationDetector] = None):
        self.detector = detector or ConfigurationDetector()
        self.migration_history = []
        
        # 迁移模板
        self.unified_config_template = self._create_unified_config_template()
        
    def _create_unified_config_template(self) -> Dict[str, Any]:
        """创建统一配置模板"""
        return {
            "version": "2.0",
            "config_type": "aceflow_unified",
            "unified_mode": True,
            "mcpServers": {},
            "module_config": {
                "core": {
                    "enabled": True,
                    "tools": ["aceflow_init", "aceflow_stage", "aceflow_validate"]
                },
                "collaboration": {
                    "enabled": False,
                    "tools": ["aceflow_respond", "aceflow_collaboration_status", "aceflow_task_execute"]
                },
                "intelligence": {
                    "enabled": False,
                    "tools": ["aceflow_intent_analyze", "aceflow_recommend"]
                }
            },
            "feature_flags": {
                "caching": True,
                "monitoring": True,
                "resource_routing": True,
                "intelligent_recommendations": False
            },
            "performance_config": {
                "cache_ttl": 300,
                "max_concurrent_requests": 100,
                "request_timeout": 30
            },
            "migration_info": {
                "migrated_at": None,
                "source_configs": [],
                "migration_version": "1.0"
            }
        }
    
    def migrate_configuration(self, source_file: str, 
                            strategy: MigrationStrategy = MigrationStrategy.BACKUP_AND_REPLACE,
                            target_file: Optional[str] = None) -> MigrationResult:
        """迁移单个配置文件"""
        migration_id = str(uuid.uuid4())
        
        # 创建迁移结果对象
        result = MigrationResult(
            migration_id=migration_id,
            source_file=source_file,
            target_file=target_file or self._generate_target_filename(source_file),
            source_type=ConfigType.UNKNOWN,
            strategy=strategy,
            status=MigrationStatus.PENDING,
            started_at=datetime.now()
        )
        
        try:
            logger.info(f"Starting migration {migration_id} for {source_file}")
            result.status = MigrationStatus.IN_PROGRESS
            
            # 1. 检测源配置
            detection_results = self.detector.detect_configurations([source_file])
            if not detection_results:
                raise ValueError(f"Could not detect configuration in {source_file}")
            
            detection_result = detection_results[0]
            result.source_type = detection_result.config_type
            
            if not detection_result.migration_required:
                result.warnings.append("Configuration may not require migration")
            
            # 2. 加载源配置
            source_config = self._load_source_config(source_file, detection_result.config_format)
            if not source_config:
                raise ValueError(f"Could not load source configuration from {source_file}")
            
            # 3. 执行备份（如果需要）
            if strategy in [MigrationStrategy.BACKUP_AND_REPLACE, MigrationStrategy.REPLACE]:
                result.backup_file = self._create_backup(source_file)
                result.changes_made.append(f"Created backup: {result.backup_file}")
            
            # 4. 转换配置
            unified_config = self._convert_to_unified_config(source_config, detection_result)
            result.changes_made.extend(self._get_conversion_changes(source_config, unified_config))
            
            # 5. 保存新配置
            self._save_unified_config(unified_config, result.target_file)
            result.changes_made.append(f"Created unified config: {result.target_file}")
            
            # 6. 验证迁移结果
            validation_passed, validation_errors = self._validate_migrated_config(result.target_file)
            result.validation_passed = validation_passed
            result.validation_errors = validation_errors
            
            if not validation_passed:
                result.warnings.append("Migrated configuration has validation issues")
            
            # 7. 完成迁移
            result.status = MigrationStatus.COMPLETED
            result.completed_at = datetime.now()
            
            logger.info(f"Migration {migration_id} completed successfully")
            
        except Exception as e:
            result.status = MigrationStatus.FAILED
            result.errors.append(str(e))
            result.completed_at = datetime.now()
            logger.error(f"Migration {migration_id} failed: {e}")
        
        # 记录迁移历史
        self.migration_history.append(result)
        return result
    
    def migrate_multiple_configurations(self, source_files: List[str],
                                      strategy: MigrationStrategy = MigrationStrategy.BACKUP_AND_REPLACE,
                                      merge_into_single: bool = True) -> List[MigrationResult]:
        """迁移多个配置文件"""
        results = []
        
        if merge_into_single and len(source_files) > 1:
            # 合并多个配置到单个统一配置
            result = self._merge_multiple_configs(source_files, strategy)
            results.append(result)
        else:
            # 分别迁移每个配置
            for source_file in source_files:
                result = self.migrate_configuration(source_file, strategy)
                results.append(result)
        
        return results
    
    def _merge_multiple_configs(self, source_files: List[str], 
                               strategy: MigrationStrategy) -> MigrationResult:
        """合并多个配置文件"""
        migration_id = str(uuid.uuid4())
        
        result = MigrationResult(
            migration_id=migration_id,
            source_file=", ".join(source_files),
            target_file="aceflow-unified-config.json",
            source_type=ConfigType.UNKNOWN,
            strategy=MigrationStrategy.MERGE,
            status=MigrationStatus.IN_PROGRESS,
            started_at=datetime.now()
        )
        
        try:
            # 创建基础统一配置
            unified_config = self.unified_config_template.copy()
            unified_config["migration_info"]["source_configs"] = source_files
            unified_config["migration_info"]["migrated_at"] = datetime.now().isoformat()
            
            # 处理每个源配置
            for source_file in source_files:
                try:
                    # 检测配置类型
                    detection_results = self.detector.detect_configurations([source_file])
                    if not detection_results:
                        result.warnings.append(f"Could not detect configuration in {source_file}")
                        continue
                    
                    detection_result = detection_results[0]
                    source_config = self._load_source_config(source_file, detection_result.config_format)
                    
                    if not source_config:
                        result.warnings.append(f"Could not load configuration from {source_file}")
                        continue
                    
                    # 合并配置
                    self._merge_config_into_unified(source_config, detection_result, unified_config)
                    result.changes_made.append(f"Merged configuration from {source_file}")
                    
                    # 创建备份
                    if strategy == MigrationStrategy.BACKUP_AND_REPLACE:
                        backup_file = self._create_backup(source_file)
                        result.changes_made.append(f"Created backup: {backup_file}")
                    
                except Exception as e:
                    result.warnings.append(f"Failed to process {source_file}: {e}")
            
            # 保存合并后的配置
            self._save_unified_config(unified_config, result.target_file)
            result.changes_made.append(f"Created merged unified config: {result.target_file}")
            
            # 验证结果
            validation_passed, validation_errors = self._validate_migrated_config(result.target_file)
            result.validation_passed = validation_passed
            result.validation_errors = validation_errors
            
            result.status = MigrationStatus.COMPLETED
            result.completed_at = datetime.now()
            
        except Exception as e:
            result.status = MigrationStatus.FAILED
            result.errors.append(str(e))
            result.completed_at = datetime.now()
        
        return result
    
    def _load_source_config(self, source_file: str, config_format: ConfigFormat) -> Optional[Dict[str, Any]]:
        """加载源配置文件"""
        try:
            source_path = Path(source_file)
            if not source_path.exists():
                return None
            
            content = source_path.read_text(encoding='utf-8')
            
            if config_format == ConfigFormat.JSON:
                return json.loads(content)
            elif config_format == ConfigFormat.YAML:
                try:
                    import yaml
                    return yaml.safe_load(content)
                except ImportError:
                    logger.warning("PyYAML not available for YAML config")
                    return None
            else:
                # 尝试JSON解析
                return json.loads(content)
                
        except Exception as e:
            logger.error(f"Failed to load source config {source_file}: {e}")
            return None
    
    def _convert_to_unified_config(self, source_config: Dict[str, Any], 
                                 detection_result: ConfigDetectionResult) -> Dict[str, Any]:
        """转换为统一配置格式"""
        unified_config = self.unified_config_template.copy()
        
        # 设置迁移信息
        unified_config["migration_info"]["migrated_at"] = datetime.now().isoformat()
        unified_config["migration_info"]["source_configs"] = [detection_result.file_path]
        unified_config["migration_info"]["source_type"] = detection_result.config_type.value
        
        # 根据源配置类型进行转换
        if detection_result.config_type == ConfigType.ACEFLOW_BASIC:
            self._convert_basic_config(source_config, unified_config)
        elif detection_result.config_type == ConfigType.ACEFLOW_ENHANCED:
            self._convert_enhanced_config(source_config, unified_config)
        elif detection_result.config_type == ConfigType.ACEFLOW_UNIFIED:
            # 已经是统一配置，只需要更新版本
            unified_config.update(source_config)
            unified_config["version"] = "2.0"
        
        # 保留原有的mcpServers配置
        if "mcpServers" in source_config:
            unified_config["mcpServers"] = source_config["mcpServers"]
        
        return unified_config
    
    def _convert_basic_config(self, source_config: Dict[str, Any], unified_config: Dict[str, Any]):
        """转换基础配置"""
        # 启用核心模块
        unified_config["module_config"]["core"]["enabled"] = True
        
        # 检查环境变量中的功能标志
        mcp_servers = source_config.get("mcpServers", {})
        for server_config in mcp_servers.values():
            env = server_config.get("env", {})
            
            # 检查缓存设置
            if env.get("ENABLE_CACHING") == "true":
                unified_config["feature_flags"]["caching"] = True
            
            # 检查监控设置
            if env.get("ENABLE_MONITORING") == "true":
                unified_config["feature_flags"]["monitoring"] = True
    
    def _convert_enhanced_config(self, source_config: Dict[str, Any], unified_config: Dict[str, Any]):
        """转换增强配置"""
        # 启用所有模块
        unified_config["module_config"]["core"]["enabled"] = True
        unified_config["module_config"]["collaboration"]["enabled"] = True
        unified_config["module_config"]["intelligence"]["enabled"] = True
        
        # 启用高级功能
        unified_config["feature_flags"]["intelligent_recommendations"] = True
        
        # 检查环境变量
        mcp_servers = source_config.get("mcpServers", {})
        for server_config in mcp_servers.values():
            env = server_config.get("env", {})
            
            # 根据环境变量调整模块配置
            if env.get("ENABLE_COLLABORATION") == "false":
                unified_config["module_config"]["collaboration"]["enabled"] = False
            
            if env.get("ENABLE_INTELLIGENCE") == "false":
                unified_config["module_config"]["intelligence"]["enabled"] = False
    
    def _merge_config_into_unified(self, source_config: Dict[str, Any], 
                                 detection_result: ConfigDetectionResult,
                                 unified_config: Dict[str, Any]):
        """将源配置合并到统一配置中"""
        # 合并mcpServers
        source_servers = source_config.get("mcpServers", {})
        unified_servers = unified_config.get("mcpServers", {})
        
        for server_name, server_config in source_servers.items():
            # 重命名服务器以避免冲突
            if server_name in unified_servers:
                server_name = f"{server_name}_{detection_result.config_type.value}"
            
            unified_servers[server_name] = server_config
        
        # 根据配置类型启用相应模块
        if detection_result.config_type == ConfigType.ACEFLOW_ENHANCED:
            unified_config["module_config"]["collaboration"]["enabled"] = True
            unified_config["module_config"]["intelligence"]["enabled"] = True
    
    def _get_conversion_changes(self, source_config: Dict[str, Any], 
                              unified_config: Dict[str, Any]) -> List[str]:
        """获取转换过程中的变更列表"""
        changes = []
        
        # 检查新增的字段
        new_fields = set(unified_config.keys()) - set(source_config.keys())
        for field in new_fields:
            changes.append(f"Added field: {field}")
        
        # 检查模块配置
        if "module_config" in unified_config:
            changes.append("Added module configuration")
        
        # 检查功能标志
        if "feature_flags" in unified_config:
            changes.append("Added feature flags configuration")
        
        # 检查性能配置
        if "performance_config" in unified_config:
            changes.append("Added performance configuration")
        
        return changes
    
    def _generate_target_filename(self, source_file: str) -> str:
        """生成目标文件名"""
        source_path = Path(source_file)
        parent_dir = source_path.parent
        
        # 生成统一配置文件名
        target_name = "aceflow-unified-config.json"
        target_path = parent_dir / target_name
        
        # 如果文件已存在，添加时间戳
        if target_path.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            target_name = f"aceflow-unified-config_{timestamp}.json"
            target_path = parent_dir / target_name
        
        return str(target_path)
    
    def _create_backup(self, source_file: str) -> str:
        """创建配置文件备份"""
        source_path = Path(source_file)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{source_path.stem}_backup_{timestamp}{source_path.suffix}"
        backup_path = source_path.parent / backup_name
        
        shutil.copy2(source_file, backup_path)
        logger.info(f"Created backup: {backup_path}")
        
        return str(backup_path)
    
    def _save_unified_config(self, unified_config: Dict[str, Any], target_file: str):
        """保存统一配置文件"""
        target_path = Path(target_file)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(target_path, 'w', encoding='utf-8') as f:
            json.dump(unified_config, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved unified config: {target_path}")
    
    def _validate_migrated_config(self, target_file: str) -> Tuple[bool, List[str]]:
        """验证迁移后的配置"""
        try:
            # 使用检测器验证新配置
            detection_results = self.detector.detect_configurations([target_file])
            
            if not detection_results:
                return False, ["Could not validate migrated configuration"]
            
            result = detection_results[0]
            return result.is_valid, result.validation_errors
            
        except Exception as e:
            return False, [f"Validation failed: {e}"]
    
    def rollback_migration(self, migration_id: str) -> bool:
        """回滚迁移"""
        # 查找迁移记录
        migration_result = None
        for result in self.migration_history:
            if result.migration_id == migration_id:
                migration_result = result
                break
        
        if not migration_result:
            logger.error(f"Migration {migration_id} not found")
            return False
        
        if migration_result.status != MigrationStatus.COMPLETED:
            logger.error(f"Migration {migration_id} is not in completed state")
            return False
        
        try:
            # 删除目标文件
            if Path(migration_result.target_file).exists():
                Path(migration_result.target_file).unlink()
                logger.info(f"Removed migrated config: {migration_result.target_file}")
            
            # 恢复备份文件
            if migration_result.backup_file and Path(migration_result.backup_file).exists():
                shutil.copy2(migration_result.backup_file, migration_result.source_file)
                logger.info(f"Restored backup: {migration_result.backup_file}")
            
            # 更新状态
            migration_result.status = MigrationStatus.ROLLED_BACK
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to rollback migration {migration_id}: {e}")
            return False
    
    def get_migration_report(self) -> Dict[str, Any]:
        """获取迁移报告"""
        if not self.migration_history:
            return {
                "summary": "No migrations performed",
                "total_migrations": 0
            }
        
        total_migrations = len(self.migration_history)
        completed_migrations = len([r for r in self.migration_history if r.status == MigrationStatus.COMPLETED])
        failed_migrations = len([r for r in self.migration_history if r.status == MigrationStatus.FAILED])
        
        return {
            "summary": f"Performed {total_migrations} migration(s)",
            "total_migrations": total_migrations,
            "completed_migrations": completed_migrations,
            "failed_migrations": failed_migrations,
            "success_rate": completed_migrations / total_migrations if total_migrations > 0 else 0,
            "migrations": [
                {
                    "migration_id": r.migration_id,
                    "source_file": r.source_file,
                    "target_file": r.target_file,
                    "source_type": r.source_type.value,
                    "strategy": r.strategy.value,
                    "status": r.status.value,
                    "validation_passed": r.validation_passed,
                    "changes_count": len(r.changes_made),
                    "warnings_count": len(r.warnings),
                    "errors_count": len(r.errors),
                    "started_at": r.started_at.isoformat() if r.started_at else None,
                    "completed_at": r.completed_at.isoformat() if r.completed_at else None
                }
                for r in self.migration_history
            ]
        }

# 便利函数
def migrate_aceflow_config(source_file: str, 
                          strategy: MigrationStrategy = MigrationStrategy.BACKUP_AND_REPLACE,
                          target_file: Optional[str] = None) -> MigrationResult:
    """迁移AceFlow配置的便利函数"""
    migrator = ConfigurationMigrator()
    return migrator.migrate_configuration(source_file, strategy, target_file)

def migrate_multiple_aceflow_configs(source_files: List[str],
                                   strategy: MigrationStrategy = MigrationStrategy.BACKUP_AND_REPLACE,
                                   merge_into_single: bool = True) -> List[MigrationResult]:
    """迁移多个AceFlow配置的便利函数"""
    migrator = ConfigurationMigrator()
    return migrator.migrate_multiple_configurations(source_files, strategy, merge_into_single)

def auto_discover_and_migrate(search_paths: List[str] = None,
                            strategy: MigrationStrategy = MigrationStrategy.BACKUP_AND_REPLACE) -> Dict[str, Any]:
    """自动发现并迁移配置的便利函数"""
    detector = ConfigurationDetector()
    migrator = ConfigurationMigrator(detector)
    
    # 发现需要迁移的配置
    detection_results = detector.detect_configurations(search_paths)
    migration_needed = [r for r in detection_results if r.migration_required]
    
    if not migration_needed:
        return {
            "message": "No configurations require migration",
            "total_found": len(detection_results),
            "migration_needed": 0
        }
    
    # 执行迁移
    source_files = [r.file_path for r in migration_needed]
    migration_results = migrator.migrate_multiple_configurations(source_files, strategy, merge_into_single=True)
    
    # 生成报告
    report = migrator.get_migration_report()
    report["auto_discovery"] = {
        "total_configs_found": len(detection_results),
        "configs_needing_migration": len(migration_needed),
        "migration_performed": len(migration_results) > 0
    }
    
    return report