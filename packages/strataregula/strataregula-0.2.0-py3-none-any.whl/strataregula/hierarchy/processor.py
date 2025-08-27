"""
Hierarchy Processor - High-level hierarchy management and processing.
"""

import yaml
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
import logging
import copy

from .merger import HierarchyMerger, MergeStrategy

logger = logging.getLogger(__name__)


class HierarchyProcessor:
    """階層処理の専門クラス"""
    
    def __init__(self, default_strategy: MergeStrategy = MergeStrategy.SMART):
        self.merger = HierarchyMerger(default_strategy)
        self.environment_configs: Dict[str, Dict] = {}
        self.base_config: Optional[Dict] = None
        logger.info(f"Initialized HierarchyProcessor with strategy: {default_strategy.value}")
    
    def load_base_config(self, config_path: Union[str, Path]) -> bool:
        """基本設定を読み込み"""
        try:
            config_path = Path(config_path)
            if not config_path.exists():
                logger.error(f"Base config file not found: {config_path}")
                return False
            
            with open(config_path, 'r', encoding='utf-8') as f:
                self.base_config = yaml.safe_load(f)
            
            logger.info(f"Loaded base config from: {config_path}")
            return True
        except Exception as e:
            logger.error(f"Error loading base config: {e}")
            return False
    
    def load_environment_config(self, env_name: str, config_path: Union[str, Path]) -> bool:
        """環境別設定を読み込み"""
        try:
            config_path = Path(config_path)
            if not config_path.exists():
                logger.error(f"Environment config file not found: {config_path}")
                return False
            
            with open(config_path, 'r', encoding='utf-8') as f:
                env_config = yaml.safe_load(f)
            
            # 環境名を設定に追加
            env_config['environment'] = env_name
            self.environment_configs[env_name] = env_config
            
            logger.info(f"Loaded environment config for '{env_name}' from: {config_path}")
            return True
        except Exception as e:
            logger.error(f"Error loading environment config for '{env_name}': {e}")
            return False
    
    def load_multiple_configs(self, config_paths: List[Union[str, Path]]) -> bool:
        """複数の設定ファイルを読み込み"""
        if not config_paths:
            logger.warning("No config paths provided")
            return False
        
        configs = []
        
        for config_path in config_paths:
            try:
                config_path = Path(config_path)
                if not config_path.exists():
                    logger.warning(f"Config file not found, skipping: {config_path}")
                    continue
                
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                
                configs.append(config)
                logger.debug(f"Loaded config from: {config_path}")
                
            except Exception as e:
                logger.error(f"Error loading config from {config_path}: {e}")
                continue
        
        if configs:
            # 最初の設定を基本設定として使用
            self.base_config = configs[0]
            # 残りを環境設定として処理
            for i, config in enumerate(configs[1:], 1):
                env_name = config.get('environment', f'config_{i}')
                self.environment_configs[env_name] = config
            
            logger.info(f"Loaded {len(configs)} configuration files")
            return True
        
        return False
    
    def get_merged_config(self, target_env: str = None, strategy: MergeStrategy = None) -> Optional[Dict]:
        """マージされた設定を取得"""
        if not self.base_config:
            logger.error("No base config loaded")
            return None
        
        # 戦略を設定
        if strategy:
            self.merger.strategy = strategy
        
        result = copy.deepcopy(self.base_config)
        
        if target_env and target_env in self.environment_configs:
            # 特定の環境設定をマージ
            logger.info(f"Merging environment config for: {target_env}")
            result = self.merger.merge_with_environment(result, self.environment_configs[target_env], target_env)
        else:
            # すべての環境設定をマージ
            logger.info("Merging all environment configs")
            for env_name, env_config in self.environment_configs.items():
                result = self.merger.merge_with_environment(result, env_config, env_name)
        
        return result
    
    def merge_configs(self, configs: List[Dict], strategy: MergeStrategy = None) -> Optional[Dict]:
        """複数の設定をマージ"""
        if not configs:
            logger.error("No configs provided for merging")
            return None
        
        # 戦略を設定
        if strategy:
            self.merger.strategy = strategy
        
        logger.info(f"Merging {len(configs)} configurations")
        return self.merger.merge_multiple(configs)
    
    def resolve_config_conflicts(self, base: Dict, conflicts: List[Dict], 
                               priority_order: List[str] = None) -> Dict:
        """設定の競合を解決"""
        logger.info(f"Resolving conflicts for {len(conflicts)} configurations")
        return self.merger.resolve_conflicts(base, conflicts, priority_order)
    
    def save_merged_config(self, config: Dict, output_path: Union[str, Path], 
                          format: str = 'yaml') -> bool:
        """マージされた設定を保存"""
        try:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            if format.lower() == 'yaml':
                with open(output_path, 'w', encoding='utf-8') as f:
                    yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
            elif format.lower() == 'json':
                import json
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
            else:
                logger.error(f"Unsupported format: {format}")
                return False
            
            logger.info(f"Saved merged config to: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving merged config: {e}")
            return False
    
    def get_available_environments(self) -> List[str]:
        """利用可能な環境の一覧を取得"""
        return list(self.environment_configs.keys())
    
    def get_config_summary(self) -> Dict[str, Any]:
        """設定の概要を取得"""
        summary = {
            'base_config_loaded': self.base_config is not None,
            'base_config_keys': list(self.base_config.keys()) if self.base_config else [],
            'environments': self.get_available_environments(),
            'total_configs': 1 + len(self.environment_configs)
        }
        
        if self.base_config:
            summary['base_config_size'] = len(str(self.base_config))
        
        return summary
    
    def validate_configs(self) -> Dict[str, bool]:
        """設定の妥当性を検証"""
        validation_results = {}
        
        # 基本設定の検証
        if self.base_config:
            validation_results['base_config'] = self._validate_single_config(self.base_config)
        
        # 環境設定の検証
        for env_name, env_config in self.environment_configs.items():
            validation_results[f'env_{env_name}'] = self._validate_single_config(env_config)
        
        return validation_results
    
    def _validate_single_config(self, config: Dict) -> bool:
        """単一設定の妥当性を検証"""
        try:
            # 基本的な検証（必須フィールドの存在など）
            if not isinstance(config, dict):
                return False
            
            # 環境設定の場合は環境名が含まれているかチェック
            if 'environment' in config:
                env_name = config['environment']
                if not isinstance(env_name, str) or not env_name:
                    return False
            
            return True
        except Exception:
            return False
    
    def clear_configs(self):
        """すべての設定をクリア"""
        self.base_config = None
        self.environment_configs.clear()
        logger.info("Cleared all configurations")
