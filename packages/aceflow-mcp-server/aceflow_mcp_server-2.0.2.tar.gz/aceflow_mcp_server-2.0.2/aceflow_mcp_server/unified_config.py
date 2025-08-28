"""
统一配置管理模块
Unified Configuration Management Module

This module provides a comprehensive configuration management system for the
AceFlow MCP Server, supporting multiple configuration sources with proper
priority handling and validation.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Union
import json
from pathlib import Path
import os
import logging
from enum import Enum

logger = logging.getLogger(__name__)


class ConfigurationError(Exception):
    """配置错误异常"""
    pass


class ConfigSource(Enum):
    """配置源枚举"""
    DEFAULT = "default"
    FILE = "file"
    ENVIRONMENT = "environment"
    RUNTIME = "runtime"


@dataclass
class CoreConfig:
    """核心模块配置"""
    enabled: bool = True
    default_mode: str = "standard"
    auto_advance: bool = False
    quality_threshold: float = 0.8


@dataclass
class CollaborationConfig:
    """协作模块配置"""
    enabled: bool = False
    confirmation_timeout: int = 300
    auto_confirm: bool = False
    interaction_level: str = "standard"  # minimal, standard, full


@dataclass
class IntelligenceConfig:
    """智能模块配置"""
    enabled: bool = False
    intent_recognition: bool = True
    adaptive_guidance: bool = True
    learning_enabled: bool = False


@dataclass
class MonitoringConfig:
    """监控配置"""
    enabled: bool = True
    usage_tracking: bool = True
    performance_tracking: bool = True
    data_retention_days: int = 30


@dataclass
class UnifiedConfig:
    """统一配置"""
    mode: str = "standard"  # basic, standard, enhanced, auto
    core: CoreConfig = field(default_factory=CoreConfig)
    collaboration: CollaborationConfig = field(default_factory=CollaborationConfig)
    intelligence: IntelligenceConfig = field(default_factory=IntelligenceConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    
    # 配置元数据
    _source: ConfigSource = field(default=ConfigSource.DEFAULT, init=False)
    _config_path: Optional[Path] = field(default=None, init=False)
    _validation_errors: List[str] = field(default_factory=list, init=False)
    
    def validate(self) -> bool:
        """验证配置有效性"""
        self._validation_errors.clear()
        
        # 验证模式
        valid_modes = ["basic", "standard", "enhanced", "auto"]
        if self.mode not in valid_modes:
            self._validation_errors.append(f"Invalid mode '{self.mode}'. Must be one of: {valid_modes}")
        
        # 验证质量阈值
        if not 0.0 <= self.core.quality_threshold <= 1.0:
            self._validation_errors.append("Quality threshold must be between 0.0 and 1.0")
        
        # 验证超时时间
        if self.collaboration.confirmation_timeout <= 0:
            self._validation_errors.append("Confirmation timeout must be positive")
        
        # 验证数据保留天数
        if self.monitoring.data_retention_days <= 0:
            self._validation_errors.append("Data retention days must be positive")
        
        # 验证交互级别
        valid_levels = ["minimal", "standard", "full"]
        if self.collaboration.interaction_level not in valid_levels:
            self._validation_errors.append(f"Invalid interaction level '{self.collaboration.interaction_level}'. Must be one of: {valid_levels}")
        
        return len(self._validation_errors) == 0
    
    def get_validation_errors(self) -> List[str]:
        """获取验证错误"""
        return self._validation_errors.copy()
    
    @classmethod
    def load_default(cls) -> 'UnifiedConfig':
        """加载默认配置"""
        config = cls()
        config._source = ConfigSource.DEFAULT
        return config
    
    @classmethod
    def load_from_file(cls, config_path: Path) -> 'UnifiedConfig':
        """从文件加载配置"""
        if not config_path.exists():
            logger.warning(f"Config file {config_path} not found, using default config")
            return cls.load_default()
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            config = cls.from_dict(config_data)
            config._source = ConfigSource.FILE
            config._config_path = config_path
            
            # 验证配置
            if not config.validate():
                logger.warning(f"Configuration validation failed: {config.get_validation_errors()}")
                logger.warning("Using default configuration instead")
                return cls.load_default()
            
            logger.info(f"Successfully loaded configuration from {config_path}")
            return config
            
        except Exception as e:
            logger.error(f"Failed to load config from {config_path}: {e}")
            return cls.load_default()
    
    @classmethod
    def load_from_env(cls, base_config: Optional['UnifiedConfig'] = None) -> 'UnifiedConfig':
        """从环境变量加载配置"""
        config = base_config or cls.load_default()
        
        # 从环境变量覆盖配置
        env_overrides = {}
        
        if os.getenv('ACEFLOW_MODE'):
            config.mode = os.getenv('ACEFLOW_MODE')
            env_overrides['mode'] = config.mode
        
        if os.getenv('ACEFLOW_COLLABORATION_ENABLED'):
            config.collaboration.enabled = os.getenv('ACEFLOW_COLLABORATION_ENABLED').lower() == 'true'
            env_overrides['collaboration.enabled'] = config.collaboration.enabled
        
        if os.getenv('ACEFLOW_INTELLIGENCE_ENABLED'):
            config.intelligence.enabled = os.getenv('ACEFLOW_INTELLIGENCE_ENABLED').lower() == 'true'
            env_overrides['intelligence.enabled'] = config.intelligence.enabled
        
        if os.getenv('ACEFLOW_AUTO_ADVANCE'):
            config.core.auto_advance = os.getenv('ACEFLOW_AUTO_ADVANCE').lower() == 'true'
            env_overrides['core.auto_advance'] = config.core.auto_advance
        
        if os.getenv('ACEFLOW_QUALITY_THRESHOLD'):
            try:
                config.core.quality_threshold = float(os.getenv('ACEFLOW_QUALITY_THRESHOLD'))
                env_overrides['core.quality_threshold'] = config.core.quality_threshold
            except ValueError:
                logger.warning("Invalid ACEFLOW_QUALITY_THRESHOLD value, ignoring")
        
        if os.getenv('ACEFLOW_CONFIRMATION_TIMEOUT'):
            try:
                config.collaboration.confirmation_timeout = int(os.getenv('ACEFLOW_CONFIRMATION_TIMEOUT'))
                env_overrides['collaboration.confirmation_timeout'] = config.collaboration.confirmation_timeout
            except ValueError:
                logger.warning("Invalid ACEFLOW_CONFIRMATION_TIMEOUT value, ignoring")
        
        if env_overrides:
            config._source = ConfigSource.ENVIRONMENT
            logger.info(f"Applied environment variable overrides: {env_overrides}")
        
        # 验证配置
        if not config.validate():
            logger.error(f"Environment configuration validation failed: {config.get_validation_errors()}")
            raise ConfigurationError("Invalid environment configuration")
        
        return config
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UnifiedConfig':
        """从字典创建配置"""
        # 智能模式映射
        mode = data.get('mode', 'standard')
        
        if mode == 'basic':
            collaboration_enabled = False
            intelligence_enabled = False
        elif mode == 'enhanced':
            collaboration_enabled = True
            intelligence_enabled = True
        elif mode == 'auto':
            # 自动模式：根据使用情况动态启用
            collaboration_enabled = data.get('collaboration', {}).get('enabled', False)
            intelligence_enabled = data.get('intelligence', {}).get('enabled', False)
        else:  # standard
            collaboration_enabled = data.get('collaboration', {}).get('enabled', False)
            intelligence_enabled = data.get('intelligence', {}).get('enabled', False)
        
        # 处理协作配置
        collab_data = data.get('collaboration', {})
        if 'enabled' not in collab_data:
            collab_data['enabled'] = collaboration_enabled
        
        # 处理智能配置
        intel_data = data.get('intelligence', {})
        if 'enabled' not in intel_data:
            intel_data['enabled'] = intelligence_enabled
        
        return cls(
            mode=mode,
            core=CoreConfig(**data.get('core', {})),
            collaboration=CollaborationConfig(**collab_data),
            intelligence=IntelligenceConfig(**intel_data),
            monitoring=MonitoringConfig(**data.get('monitoring', {}))
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'mode': self.mode,
            'core': {
                'enabled': self.core.enabled,
                'default_mode': self.core.default_mode,
                'auto_advance': self.core.auto_advance,
                'quality_threshold': self.core.quality_threshold
            },
            'collaboration': {
                'enabled': self.collaboration.enabled,
                'confirmation_timeout': self.collaboration.confirmation_timeout,
                'auto_confirm': self.collaboration.auto_confirm,
                'interaction_level': self.collaboration.interaction_level
            },
            'intelligence': {
                'enabled': self.intelligence.enabled,
                'intent_recognition': self.intelligence.intent_recognition,
                'adaptive_guidance': self.intelligence.adaptive_guidance,
                'learning_enabled': self.intelligence.learning_enabled
            },
            'monitoring': {
                'enabled': self.monitoring.enabled,
                'usage_tracking': self.monitoring.usage_tracking,
                'performance_tracking': self.monitoring.performance_tracking,
                'data_retention_days': self.monitoring.data_retention_days
            }
        }
    
    def save_to_file(self, config_path: Path):
        """保存到文件"""
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
    
    def create_runtime_config(
        self,
        collaboration_enabled: Optional[bool] = None,
        intelligence_enabled: Optional[bool] = None
    ) -> 'UnifiedConfig':
        """创建运行时配置副本"""
        config = UnifiedConfig(
            mode=self.mode,
            core=CoreConfig(
                enabled=self.core.enabled,
                default_mode=self.core.default_mode,
                auto_advance=self.core.auto_advance,
                quality_threshold=self.core.quality_threshold
            ),
            collaboration=CollaborationConfig(
                enabled=collaboration_enabled if collaboration_enabled is not None else self.collaboration.enabled,
                confirmation_timeout=self.collaboration.confirmation_timeout,
                auto_confirm=self.collaboration.auto_confirm,
                interaction_level=self.collaboration.interaction_level
            ),
            intelligence=IntelligenceConfig(
                enabled=intelligence_enabled if intelligence_enabled is not None else self.intelligence.enabled,
                intent_recognition=self.intelligence.intent_recognition,
                adaptive_guidance=self.intelligence.adaptive_guidance,
                learning_enabled=self.intelligence.learning_enabled
            ),
            monitoring=MonitoringConfig(
                enabled=self.monitoring.enabled,
                usage_tracking=self.monitoring.usage_tracking,
                performance_tracking=self.monitoring.performance_tracking,
                data_retention_days=self.monitoring.data_retention_days
            )
        )
        return config


def load_unified_config(
    config_path: Optional[Path] = None,
    runtime_overrides: Optional[Dict[str, Any]] = None
) -> UnifiedConfig:
    """
    加载统一配置的便捷函数
    
    优先级（从高到低）：
    1. 运行时参数 (runtime_overrides)
    2. 环境变量
    3. 指定的配置文件
    4. 默认配置文件位置
    5. 默认配置
    """
    logger.info("Loading unified configuration...")
    
    # 1. 从配置文件加载基础配置
    config = None
    
    if config_path and config_path.exists():
        # 使用指定的配置文件
        config = UnifiedConfig.load_from_file(config_path)
        logger.info(f"Loaded configuration from specified path: {config_path}")
    else:
        # 尝试默认配置文件位置
        default_config_paths = [
            Path(".aceflow/config.json"),
            Path("aceflow.config.json"),
            Path.home() / ".aceflow" / "config.json"
        ]
        
        for default_path in default_config_paths:
            if default_path.exists():
                config = UnifiedConfig.load_from_file(default_path)
                logger.info(f"Loaded configuration from default path: {default_path}")
                break
    
    if config is None:
        config = UnifiedConfig.load_default()
        logger.info("Using default configuration")
    
    # 2. 应用环境变量覆盖
    try:
        config = UnifiedConfig.load_from_env(config)
    except ConfigurationError as e:
        logger.error(f"Environment configuration error: {e}")
        # 继续使用文件配置，但记录错误
    
    # 3. 应用运行时覆盖
    if runtime_overrides:
        config = apply_runtime_overrides(config, runtime_overrides)
        config._source = ConfigSource.RUNTIME
        logger.info(f"Applied runtime overrides: {runtime_overrides}")
    
    # 4. 最终验证
    if not config.validate():
        logger.error(f"Final configuration validation failed: {config.get_validation_errors()}")
        logger.warning("Falling back to default configuration")
        config = UnifiedConfig.load_default()
    
    logger.info(f"Configuration loaded successfully (source: {config._source.value})")
    return config


def apply_runtime_overrides(config: UnifiedConfig, overrides: Dict[str, Any]) -> UnifiedConfig:
    """应用运行时配置覆盖"""
    # 创建配置副本
    new_config = UnifiedConfig(
        mode=config.mode,
        core=CoreConfig(
            enabled=config.core.enabled,
            default_mode=config.core.default_mode,
            auto_advance=config.core.auto_advance,
            quality_threshold=config.core.quality_threshold
        ),
        collaboration=CollaborationConfig(
            enabled=config.collaboration.enabled,
            confirmation_timeout=config.collaboration.confirmation_timeout,
            auto_confirm=config.collaboration.auto_confirm,
            interaction_level=config.collaboration.interaction_level
        ),
        intelligence=IntelligenceConfig(
            enabled=config.intelligence.enabled,
            intent_recognition=config.intelligence.intent_recognition,
            adaptive_guidance=config.intelligence.adaptive_guidance,
            learning_enabled=config.intelligence.learning_enabled
        ),
        monitoring=MonitoringConfig(
            enabled=config.monitoring.enabled,
            usage_tracking=config.monitoring.usage_tracking,
            performance_tracking=config.monitoring.performance_tracking,
            data_retention_days=config.monitoring.data_retention_days
        )
    )
    
    # 应用覆盖
    for key, value in overrides.items():
        if key == 'mode':
            new_config.mode = value
            # 当模式改变时，自动调整功能启用状态
            if value == 'basic':
                new_config.collaboration.enabled = False
                new_config.intelligence.enabled = False
            elif value == 'enhanced':
                new_config.collaboration.enabled = True
                new_config.intelligence.enabled = True
            elif value == 'standard':
                # 标准模式保持当前设置或使用默认值
                pass
        elif key == 'collaboration_enabled':
            new_config.collaboration.enabled = value
        elif key == 'intelligence_enabled':
            new_config.intelligence.enabled = value
        elif key == 'auto_advance':
            new_config.core.auto_advance = value
        elif key == 'quality_threshold':
            new_config.core.quality_threshold = value
        elif key == 'confirmation_timeout':
            new_config.collaboration.confirmation_timeout = value
        elif key == 'auto_confirm':
            new_config.collaboration.auto_confirm = value
        elif key == 'interaction_level':
            new_config.collaboration.interaction_level = value
        elif key == 'intent_recognition':
            new_config.intelligence.intent_recognition = value
        elif key == 'adaptive_guidance':
            new_config.intelligence.adaptive_guidance = value
        elif key == 'learning_enabled':
            new_config.intelligence.learning_enabled = value
        elif key == 'usage_tracking':
            new_config.monitoring.usage_tracking = value
        elif key == 'performance_tracking':
            new_config.monitoring.performance_tracking = value
        elif key == 'data_retention_days':
            new_config.monitoring.data_retention_days = value
        else:
            logger.warning(f"Unknown runtime override key: {key}")
    
    return new_config


def detect_legacy_config() -> Dict[str, Any]:
    """检测现有配置类型和详细信息"""
    legacy_info = {
        "type": "standard",
        "found": False,
        "config_path": None,
        "server_config": None
    }
    
    # 检查 MCP 配置文件
    mcp_config_paths = [
        Path("mcp.json"),
        Path(".cursor/mcp.json"),
        Path(".kiro/settings/mcp.json"),
        Path.home() / ".cursor" / "mcp.json",
        Path.home() / ".kiro" / "settings" / "mcp.json"
    ]
    
    for config_path in mcp_config_paths:
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                servers = config.get("mcpServers", {})
                
                # 检查 aceflow-enhanced-server
                if "aceflow-enhanced" in servers:
                    legacy_info.update({
                        "type": "enhanced",
                        "found": True,
                        "config_path": config_path,
                        "server_config": servers["aceflow-enhanced"]
                    })
                    logger.info(f"Detected legacy enhanced server config at {config_path}")
                    return legacy_info
                
                # 检查 aceflow-server
                elif "aceflow" in servers:
                    legacy_info.update({
                        "type": "basic",
                        "found": True,
                        "config_path": config_path,
                        "server_config": servers["aceflow"]
                    })
                    logger.info(f"Detected legacy basic server config at {config_path}")
                    return legacy_info
                
                # 检查统一服务器配置
                elif "aceflow-unified" in servers:
                    legacy_info.update({
                        "type": "unified",
                        "found": True,
                        "config_path": config_path,
                        "server_config": servers["aceflow-unified"]
                    })
                    logger.info(f"Detected unified server config at {config_path}")
                    return legacy_info
                    
            except Exception as e:
                logger.warning(f"Failed to parse MCP config at {config_path}: {e}")
                continue
    
    logger.info("No legacy configuration detected")
    return legacy_info


def migrate_legacy_config(legacy_info: Dict[str, Any]) -> UnifiedConfig:
    """迁移旧配置"""
    legacy_type = legacy_info.get("type", "standard")
    server_config = legacy_info.get("server_config", {})
    
    logger.info(f"Migrating legacy configuration of type: {legacy_type}")
    
    if legacy_type == "enhanced":
        config = UnifiedConfig(
            mode="enhanced",
            collaboration=CollaborationConfig(enabled=True),
            intelligence=IntelligenceConfig(enabled=True)
        )
        
        # 尝试从服务器配置中提取参数
        env_vars = server_config.get("env", {})
        if "ACEFLOW_AUTO_ADVANCE" in env_vars:
            config.core.auto_advance = env_vars["ACEFLOW_AUTO_ADVANCE"].lower() == "true"
        
        logger.info("Migrated to enhanced mode configuration")
        return config
        
    elif legacy_type == "basic":
        config = UnifiedConfig(
            mode="basic",
            collaboration=CollaborationConfig(enabled=False),
            intelligence=IntelligenceConfig(enabled=False)
        )
        
        # 尝试从服务器配置中提取参数
        env_vars = server_config.get("env", {})
        if "ACEFLOW_AUTO_ADVANCE" in env_vars:
            config.core.auto_advance = env_vars["ACEFLOW_AUTO_ADVANCE"].lower() == "true"
        
        logger.info("Migrated to basic mode configuration")
        return config
        
    elif legacy_type == "unified":
        # 已经是统一配置，尝试解析现有参数
        env_vars = server_config.get("env", {})
        mode = env_vars.get("ACEFLOW_MODE", "standard")
        
        config = UnifiedConfig(mode=mode)
        
        if "ACEFLOW_COLLABORATION_ENABLED" in env_vars:
            config.collaboration.enabled = env_vars["ACEFLOW_COLLABORATION_ENABLED"].lower() == "true"
        
        if "ACEFLOW_INTELLIGENCE_ENABLED" in env_vars:
            config.intelligence.enabled = env_vars["ACEFLOW_INTELLIGENCE_ENABLED"].lower() == "true"
        
        if "ACEFLOW_AUTO_ADVANCE" in env_vars:
            config.core.auto_advance = env_vars["ACEFLOW_AUTO_ADVANCE"].lower() == "true"
        
        logger.info("Migrated existing unified configuration")
        return config
    
    else:
        logger.info("Using default configuration (no migration needed)")
        return UnifiedConfig.load_default()


def backup_config(config_path: Path) -> bool:
    """备份配置文件"""
    if not config_path.exists():
        return True
    
    backup_path = config_path.with_suffix(f"{config_path.suffix}.backup")
    try:
        import shutil
        shutil.copy2(config_path, backup_path)
        logger.info(f"Configuration backed up to {backup_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to backup configuration: {e}")
        return False


def auto_migrate_config() -> UnifiedConfig:
    """自动检测并迁移配置"""
    logger.info("Starting automatic configuration migration...")
    
    # 1. 检测现有配置
    legacy_info = detect_legacy_config()
    
    # 2. 如果找到旧配置，进行迁移
    if legacy_info["found"]:
        config = migrate_legacy_config(legacy_info)
        
        # 3. 保存迁移后的配置
        unified_config_path = Path(".aceflow/config.json")
        
        # 备份原配置（如果存在）
        if unified_config_path.exists():
            backup_config(unified_config_path)
        
        # 保存新配置
        try:
            config.save_to_file(unified_config_path)
            logger.info(f"Migrated configuration saved to {unified_config_path}")
        except Exception as e:
            logger.error(f"Failed to save migrated configuration: {e}")
        
        return config
    
    # 4. 没有找到旧配置，使用标准加载流程
    return load_unified_config()


class ConfigManager:
    """配置管理器 - 统一管理所有配置操作"""
    
    def __init__(self):
        self._config: Optional[UnifiedConfig] = None
        self._config_path: Optional[Path] = None
    
    def load_config(
        self,
        config_path: Optional[Path] = None,
        runtime_overrides: Optional[Dict[str, Any]] = None,
        auto_migrate: bool = True
    ) -> UnifiedConfig:
        """加载配置"""
        if auto_migrate and runtime_overrides is None:
            # 只有在没有运行时覆盖时才使用自动迁移
            self._config = auto_migrate_config()
        else:
            # 有运行时覆盖时，使用完整的配置加载流程
            self._config = load_unified_config(config_path, runtime_overrides)
        
        self._config_path = config_path
        return self._config
    
    def get_config(self) -> UnifiedConfig:
        """获取当前配置"""
        if self._config is None:
            self._config = self.load_config()
        return self._config
    
    def reload_config(self) -> UnifiedConfig:
        """重新加载配置"""
        self._config = None
        return self.load_config(self._config_path)
    
    def save_config(self, config_path: Optional[Path] = None) -> bool:
        """保存配置"""
        if self._config is None:
            logger.error("No configuration to save")
            return False
        
        save_path = config_path or self._config_path or Path(".aceflow/config.json")
        
        try:
            # 备份现有配置
            if save_path.exists():
                backup_config(save_path)
            
            # 保存配置
            self._config.save_to_file(save_path)
            self._config_path = save_path
            logger.info(f"Configuration saved to {save_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            return False
    
    def update_config(self, updates: Dict[str, Any]) -> bool:
        """更新配置"""
        if self._config is None:
            self._config = self.load_config()
        
        try:
            # 应用更新
            updated_config = apply_runtime_overrides(self._config, updates)
            
            # 验证更新后的配置
            if not updated_config.validate():
                logger.error(f"Configuration update validation failed: {updated_config.get_validation_errors()}")
                return False
            
            self._config = updated_config
            logger.info(f"Configuration updated: {updates}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update configuration: {e}")
            return False
    
    def get_effective_mode(self) -> str:
        """获取有效的运行模式"""
        config = self.get_config()
        
        if config.mode == "auto":
            # 自动模式：根据启用的功能决定实际模式
            if config.collaboration.enabled and config.intelligence.enabled:
                return "enhanced"
            elif config.collaboration.enabled or config.intelligence.enabled:
                return "standard"
            else:
                return "basic"
        
        return config.mode
    
    def is_feature_enabled(self, feature: str) -> bool:
        """检查功能是否启用"""
        config = self.get_config()
        
        if feature == "collaboration":
            return config.collaboration.enabled
        elif feature == "intelligence":
            return config.intelligence.enabled
        elif feature == "monitoring":
            return config.monitoring.enabled
        elif feature == "core":
            return config.core.enabled
        else:
            logger.warning(f"Unknown feature: {feature}")
            return False
    
    def get_config_summary(self) -> Dict[str, Any]:
        """获取配置摘要"""
        config = self.get_config()
        
        return {
            "mode": config.mode,
            "effective_mode": self.get_effective_mode(),
            "source": config._source.value,
            "config_path": str(self._config_path) if self._config_path else None,
            "features": {
                "core": config.core.enabled,
                "collaboration": config.collaboration.enabled,
                "intelligence": config.intelligence.enabled,
                "monitoring": config.monitoring.enabled
            },
            "validation_status": "valid" if config.validate() else "invalid",
            "validation_errors": config.get_validation_errors()
        }


# 全局配置管理器实例
_config_manager = ConfigManager()


def get_config_manager() -> ConfigManager:
    """获取全局配置管理器实例"""
    return _config_manager