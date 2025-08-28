#!/usr/bin/env python3
"""
配置自动检测器
Configuration Auto-Detector

检测现有MCP配置文件，识别aceflow-server和aceflow-enhanced-server配置
"""
import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass
import re

logger = logging.getLogger(__name__)

class ConfigType(Enum):
    """配置类型枚举"""
    ACEFLOW_BASIC = "aceflow_basic"
    ACEFLOW_ENHANCED = "aceflow_enhanced"
    ACEFLOW_UNIFIED = "aceflow_unified"
    UNKNOWN = "unknown"
    INVALID = "invalid"

class ConfigFormat(Enum):
    """配置格式枚举"""
    JSON = "json"
    YAML = "yaml"
    TOML = "toml"
    ENV = "env"

@dataclass
class ConfigDetectionResult:
    """配置检测结果"""
    file_path: str
    config_type: ConfigType
    config_format: ConfigFormat
    version: Optional[str]
    is_valid: bool
    validation_errors: List[str]
    detected_features: List[str]
    migration_required: bool
    confidence_score: float  # 0.0 - 1.0

class ConfigurationDetector:
    """配置自动检测器"""
    
    def __init__(self):
        self.detection_patterns = self._initialize_detection_patterns()
        self.validation_rules = self._initialize_validation_rules()
        
    def _initialize_detection_patterns(self) -> Dict[str, Any]:
        """初始化检测模式"""
        return {
            "aceflow_basic": {
                "server_names": ["aceflow-server", "aceflow_server"],
                "required_fields": ["mcpServers"],
                "tool_patterns": [
                    r"aceflow[_-]?init",
                    r"aceflow[_-]?stage", 
                    r"aceflow[_-]?validate"
                ],
                "resource_patterns": [
                    r"project[_-]?state",
                    r"workflow[_-]?config",
                    r"stage[_-]?guide"
                ]
            },
            "aceflow_enhanced": {
                "server_names": ["aceflow-enhanced-server", "aceflow_enhanced_server"],
                "required_fields": ["mcpServers"],
                "tool_patterns": [
                    r"aceflow[_-]?respond",
                    r"aceflow[_-]?collaboration[_-]?status",
                    r"aceflow[_-]?task[_-]?execute",
                    r"aceflow[_-]?intent[_-]?analyze",
                    r"aceflow[_-]?recommend"
                ],
                "resource_patterns": [
                    r"intelligent[_-]?project[_-]?state",
                    r"collaboration[_-]?insights",
                    r"usage[_-]?stats"
                ]
            },
            "aceflow_unified": {
                "server_names": ["aceflow-unified-server", "aceflow_unified_server"],
                "required_fields": ["mcpServers"],
                "unified_indicators": [
                    "unified_mode",
                    "module_config",
                    "feature_flags"
                ]
            }
        }
    
    def _initialize_validation_rules(self) -> Dict[str, Any]:
        """初始化验证规则"""
        return {
            "required_structure": {
                "mcpServers": dict,
                "server_config": dict
            },
            "server_config_fields": [
                "command",
                "args"
            ],
            "optional_fields": [
                "env",
                "disabled",
                "autoApprove"
            ]
        }
    
    def detect_configurations(self, search_paths: List[str] = None) -> List[ConfigDetectionResult]:
        """检测配置文件"""
        if search_paths is None:
            search_paths = self._get_default_search_paths()
        
        results = []
        
        for search_path in search_paths:
            path = Path(search_path)
            if not path.exists():
                continue
                
            # 查找配置文件
            config_files = self._find_config_files(path)
            
            for config_file in config_files:
                try:
                    result = self._analyze_config_file(config_file)
                    if result:
                        results.append(result)
                except Exception as e:
                    logger.error(f"Error analyzing config file {config_file}: {e}")
                    results.append(ConfigDetectionResult(
                        file_path=str(config_file),
                        config_type=ConfigType.INVALID,
                        config_format=self._detect_format(config_file),
                        version=None,
                        is_valid=False,
                        validation_errors=[str(e)],
                        detected_features=[],
                        migration_required=False,
                        confidence_score=0.0
                    ))
        
        return results
    
    def _get_default_search_paths(self) -> List[str]:
        """获取默认搜索路径"""
        paths = []
        
        # 当前目录
        paths.append(".")
        
        # 用户配置目录
        home = Path.home()
        paths.extend([
            str(home / ".kiro" / "settings"),
            str(home / ".config" / "kiro"),
            str(home / ".aceflow")
        ])
        
        # 项目配置目录
        paths.extend([
            ".kiro/settings",
            ".aceflow",
            "config"
        ])
        
        return paths
    
    def _find_config_files(self, path: Path) -> List[Path]:
        """查找配置文件"""
        config_files = set()  # 使用set避免重复
        
        if path.is_file():
            # 如果是文件，检查是否是配置文件
            if self._is_config_file(path):
                config_files.add(path)
        else:
            # 如果是目录，查找所有可能的配置文件
            for file_path in path.rglob("*.json"):
                if self._is_config_file(file_path):
                    config_files.add(file_path)
            
            for file_path in path.rglob("*.yaml"):
                if self._is_config_file(file_path):
                    config_files.add(file_path)
            
            for file_path in path.rglob("*.yml"):
                if self._is_config_file(file_path):
                    config_files.add(file_path)
        
        return list(config_files)
    
    def _is_config_file(self, file_path: Path) -> bool:
        """判断是否是配置文件"""
        filename = file_path.name.lower()
        
        # 检查文件名模式
        config_patterns = [
            "mcp.json", "mcp.yaml", "mcp.yml",
            "aceflow", ".aceflow"
        ]
        
        return any(pattern in filename for pattern in config_patterns)
    
    def _analyze_config_file(self, config_file: Path) -> Optional[ConfigDetectionResult]:
        """分析配置文件"""
        try:
            # 检测格式
            config_format = self._detect_format(config_file)
            
            # 加载配置
            config_data = self._load_config(config_file, config_format)
            if not config_data:
                return None
            
            # 检测配置类型
            config_type, confidence = self._detect_config_type(config_data, config_file)
            
            # 提取版本信息
            version = self._extract_version(config_data)
            
            # 验证配置
            is_valid, validation_errors = self._validate_config(config_data, config_type)
            
            # 检测功能特性
            detected_features = self._detect_features(config_data, config_type)
            
            # 判断是否需要迁移
            migration_required = self._requires_migration(config_type, version)
            
            return ConfigDetectionResult(
                file_path=str(config_file),
                config_type=config_type,
                config_format=config_format,
                version=version,
                is_valid=is_valid,
                validation_errors=validation_errors,
                detected_features=detected_features,
                migration_required=migration_required,
                confidence_score=confidence
            )
            
        except Exception as e:
            logger.error(f"Failed to analyze config file {config_file}: {e}")
            return None
    
    def _detect_format(self, config_file: Path) -> ConfigFormat:
        """检测配置格式"""
        suffix = config_file.suffix.lower()
        
        if suffix in ['.json']:
            return ConfigFormat.JSON
        elif suffix in ['.yaml', '.yml']:
            return ConfigFormat.YAML
        elif suffix in ['.toml']:
            return ConfigFormat.TOML
        elif suffix in ['.env']:
            return ConfigFormat.ENV
        else:
            # 尝试从内容检测
            try:
                content = config_file.read_text(encoding='utf-8')
                if content.strip().startswith('{'):
                    return ConfigFormat.JSON
                elif '=' in content and not content.strip().startswith('['):
                    return ConfigFormat.ENV
                else:
                    return ConfigFormat.YAML
            except:
                return ConfigFormat.JSON  # 默认
    
    def _load_config(self, config_file: Path, config_format: ConfigFormat) -> Optional[Dict[str, Any]]:
        """加载配置文件"""
        try:
            content = config_file.read_text(encoding='utf-8')
            
            if config_format == ConfigFormat.JSON:
                return json.loads(content)
            elif config_format == ConfigFormat.YAML:
                try:
                    import yaml
                    return yaml.safe_load(content)
                except ImportError:
                    logger.warning("PyYAML not available, cannot parse YAML config")
                    return None
            elif config_format == ConfigFormat.TOML:
                try:
                    import tomli
                    return tomli.loads(content)
                except ImportError:
                    logger.warning("tomli not available, cannot parse TOML config")
                    return None
            elif config_format == ConfigFormat.ENV:
                # 简单的环境变量解析
                config = {}
                for line in content.split('\n'):
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        config[key.strip()] = value.strip().strip('"\'')
                return config
            
        except Exception as e:
            logger.error(f"Failed to load config file {config_file}: {e}")
            return None
    
    def _detect_config_type(self, config_data: Dict[str, Any], config_file: Path) -> Tuple[ConfigType, float]:
        """检测配置类型"""
        scores = {
            ConfigType.ACEFLOW_BASIC: 0.0,
            ConfigType.ACEFLOW_ENHANCED: 0.0,
            ConfigType.ACEFLOW_UNIFIED: 0.0
        }
        
        # 检查文件名
        filename = config_file.name.lower()
        if 'enhanced' in filename:
            scores[ConfigType.ACEFLOW_ENHANCED] += 0.3
        elif 'unified' in filename:
            scores[ConfigType.ACEFLOW_UNIFIED] += 0.3
        elif 'aceflow' in filename:
            scores[ConfigType.ACEFLOW_BASIC] += 0.2
        
        # 检查mcpServers配置
        mcp_servers = config_data.get('mcpServers', {})
        
        for server_name, server_config in mcp_servers.items():
            server_name_lower = server_name.lower()
            
            # 检查服务器名称
            for config_type, patterns in self.detection_patterns.items():
                if config_type == 'aceflow_unified':
                    continue
                    
                server_names = patterns.get('server_names', [])
                for name in server_names:
                    if name.lower() in server_name_lower:
                        if config_type == 'aceflow_basic':
                            scores[ConfigType.ACEFLOW_BASIC] += 0.4
                        elif config_type == 'aceflow_enhanced':
                            scores[ConfigType.ACEFLOW_ENHANCED] += 0.4
            
            # 检查命令和参数
            command = server_config.get('command', '')
            args = server_config.get('args', [])
            
            command_str = f"{command} {' '.join(args)}".lower()
            
            # 检查工具模式
            for config_type, patterns in self.detection_patterns.items():
                if config_type == 'aceflow_unified':
                    continue
                    
                tool_patterns = patterns.get('tool_patterns', [])
                for pattern in tool_patterns:
                    if re.search(pattern, command_str):
                        if config_type == 'aceflow_basic':
                            scores[ConfigType.ACEFLOW_BASIC] += 0.1
                        elif config_type == 'aceflow_enhanced':
                            scores[ConfigType.ACEFLOW_ENHANCED] += 0.1
        
        # 检查统一配置指示器
        unified_patterns = self.detection_patterns['aceflow_unified']
        unified_indicators = unified_patterns.get('unified_indicators', [])
        
        for indicator in unified_indicators:
            if indicator in config_data:
                scores[ConfigType.ACEFLOW_UNIFIED] += 0.3
        
        # 检查特殊配置字段
        if 'module_config' in config_data or 'unified_mode' in config_data:
            scores[ConfigType.ACEFLOW_UNIFIED] += 0.4
        
        # 确定最高分数的类型
        max_score = max(scores.values())
        if max_score < 0.3:
            return ConfigType.UNKNOWN, max_score
        
        for config_type, score in scores.items():
            if score == max_score:
                return config_type, score
        
        return ConfigType.UNKNOWN, 0.0
    
    def _extract_version(self, config_data: Dict[str, Any]) -> Optional[str]:
        """提取版本信息"""
        # 检查常见的版本字段
        version_fields = ['version', 'config_version', 'aceflow_version']
        
        for field in version_fields:
            if field in config_data:
                return str(config_data[field])
        
        # 检查mcpServers中的版本信息
        mcp_servers = config_data.get('mcpServers', {})
        for server_config in mcp_servers.values():
            if 'version' in server_config:
                return str(server_config['version'])
        
        return None
    
    def _validate_config(self, config_data: Dict[str, Any], config_type: ConfigType) -> Tuple[bool, List[str]]:
        """验证配置"""
        errors = []
        
        # 基本结构验证
        if 'mcpServers' not in config_data:
            errors.append("Missing required field: mcpServers")
        elif not isinstance(config_data['mcpServers'], dict):
            errors.append("mcpServers must be a dictionary")
        else:
            # 验证每个服务器配置
            mcp_servers = config_data['mcpServers']
            for server_name, server_config in mcp_servers.items():
                if not isinstance(server_config, dict):
                    errors.append(f"Server config for '{server_name}' must be a dictionary")
                    continue
                
                # 检查必需字段
                required_fields = self.validation_rules['server_config_fields']
                for field in required_fields:
                    if field not in server_config:
                        errors.append(f"Server '{server_name}' missing required field: {field}")
                
                # 验证命令字段
                if 'command' in server_config:
                    command = server_config['command']
                    if not isinstance(command, str) or not command.strip():
                        errors.append(f"Server '{server_name}' command must be a non-empty string")
                
                # 验证参数字段
                if 'args' in server_config:
                    args = server_config['args']
                    if not isinstance(args, list):
                        errors.append(f"Server '{server_name}' args must be a list")
        
        # 类型特定验证
        if config_type == ConfigType.ACEFLOW_UNIFIED:
            # 统一配置的特殊验证
            if 'module_config' in config_data:
                module_config = config_data['module_config']
                if not isinstance(module_config, dict):
                    errors.append("module_config must be a dictionary")
        
        return len(errors) == 0, errors
    
    def _detect_features(self, config_data: Dict[str, Any], config_type: ConfigType) -> List[str]:
        """检测功能特性"""
        features = []
        
        # 基于配置类型添加基础功能
        if config_type == ConfigType.ACEFLOW_BASIC:
            features.extend(['basic_tools', 'core_resources'])
        elif config_type == ConfigType.ACEFLOW_ENHANCED:
            features.extend(['enhanced_tools', 'collaboration', 'intelligence'])
        elif config_type == ConfigType.ACEFLOW_UNIFIED:
            features.extend(['unified_architecture', 'modular_design'])
        
        # 检查特定功能指示器
        mcp_servers = config_data.get('mcpServers', {})
        
        for server_config in mcp_servers.values():
            # 检查环境变量中的功能标志
            env = server_config.get('env', {})
            
            if 'ENABLE_COLLABORATION' in env:
                features.append('collaboration')
            if 'ENABLE_INTELLIGENCE' in env:
                features.append('intelligence')
            if 'ENABLE_MONITORING' in env:
                features.append('usage_monitoring')
            if 'ENABLE_CACHING' in env:
                features.append('caching')
        
        # 检查顶级功能配置
        if 'feature_flags' in config_data:
            feature_flags = config_data['feature_flags']
            if isinstance(feature_flags, dict):
                for flag, enabled in feature_flags.items():
                    if enabled:
                        features.append(flag)
        
        return list(set(features))  # 去重
    
    def _requires_migration(self, config_type: ConfigType, version: Optional[str]) -> bool:
        """判断是否需要迁移"""
        # 基础和增强配置都需要迁移到统一配置
        if config_type in [ConfigType.ACEFLOW_BASIC, ConfigType.ACEFLOW_ENHANCED]:
            return True
        
        # 统一配置检查版本
        if config_type == ConfigType.ACEFLOW_UNIFIED and version:
            try:
                # 假设当前版本是2.0，低于此版本需要迁移
                version_parts = version.split('.')
                major = int(version_parts[0])
                if major < 2:
                    return True
            except (ValueError, IndexError):
                # 版本格式不正确，建议迁移
                return True
        
        return False
    
    def generate_detection_report(self, results: List[ConfigDetectionResult]) -> Dict[str, Any]:
        """生成检测报告"""
        if not results:
            return {
                "summary": "No configuration files found",
                "total_configs": 0,
                "recommendations": ["Create a new unified configuration"]
            }
        
        # 统计信息
        total_configs = len(results)
        valid_configs = len([r for r in results if r.is_valid])
        migration_needed = len([r for r in results if r.migration_required])
        
        # 按类型分组
        by_type = {}
        for result in results:
            config_type = result.config_type.value
            if config_type not in by_type:
                by_type[config_type] = []
            by_type[config_type].append(result)
        
        # 生成建议
        recommendations = []
        
        if migration_needed > 0:
            recommendations.append(f"Migrate {migration_needed} configuration(s) to unified format")
        
        if valid_configs < total_configs:
            invalid_count = total_configs - valid_configs
            recommendations.append(f"Fix {invalid_count} invalid configuration(s)")
        
        if ConfigType.ACEFLOW_UNIFIED.value not in by_type:
            recommendations.append("Consider upgrading to unified configuration for better features")
        
        return {
            "summary": f"Found {total_configs} configuration file(s)",
            "total_configs": total_configs,
            "valid_configs": valid_configs,
            "migration_needed": migration_needed,
            "by_type": {k: len(v) for k, v in by_type.items()},
            "configurations": [
                {
                    "file_path": r.file_path,
                    "type": r.config_type.value,
                    "format": r.config_format.value,
                    "version": r.version,
                    "is_valid": r.is_valid,
                    "features": r.detected_features,
                    "migration_required": r.migration_required,
                    "confidence": r.confidence_score,
                    "errors": r.validation_errors
                }
                for r in results
            ],
            "recommendations": recommendations
        }

# 便利函数
def detect_aceflow_configurations(search_paths: List[str] = None) -> Dict[str, Any]:
    """检测AceFlow配置的便利函数"""
    detector = ConfigurationDetector()
    results = detector.detect_configurations(search_paths)
    return detector.generate_detection_report(results)

def is_migration_needed(config_file_path: str) -> bool:
    """检查特定配置文件是否需要迁移"""
    detector = ConfigurationDetector()
    results = detector.detect_configurations([config_file_path])
    
    if results:
        return results[0].migration_required
    
    return False