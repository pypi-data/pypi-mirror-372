"""
Hierarchy Processing Commands - CLI commands for hierarchy management.
"""

import asyncio
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
import yaml
import json

from ..pipe.commands import BaseCommand
from .processor import HierarchyProcessor
from .merger import MergeStrategy

import copy


class MergeCommand(BaseCommand):
    """設定マージコマンド"""
    
    name = 'merge'
    description = 'Merge configurations with deep copy for same hierarchies'
    category = 'configuration'
    input_types = ['dict', 'list']
    output_types = ['dict', 'list']
    
    async def execute(self, data: Any, *args, **kwargs) -> Any:
        """設定をマージ"""
        merge_data = kwargs.get('with')
        strategy_name = kwargs.get('strategy', 'smart')
        
        if merge_data is None:
            return data
        
        # 戦略を設定
        try:
            strategy = MergeStrategy(strategy_name)
        except ValueError:
            # 無効な戦略の場合はデフォルトを使用
            strategy = MergeStrategy.SMART
        
        # マージ処理
        processor = HierarchyProcessor(default_strategy=strategy)
        
        if isinstance(merge_data, str):
            # ファイルパスの場合
            if Path(merge_data).exists():
                processor.load_base_config(merge_data)
                merge_data = processor.base_config
            else:
                # YAML文字列として解析
                try:
                    merge_data = yaml.safe_load(merge_data)
                except yaml.YAMLError:
                    raise ValueError(f"Invalid YAML string: {merge_data}")
        
        # マージ実行
        result = processor.merge_configs([data, merge_data], strategy)
        return result


class EnvironmentMergeCommand(BaseCommand):
    """環境別設定マージコマンド"""
    
    name = 'env_merge'
    description = 'Merge environment-specific configurations'
    category = 'configuration'
    input_types = ['dict']
    output_types = ['dict']
    
    async def execute(self, data: Any, *args, **kwargs) -> Any:
        """環境別設定をマージ"""
        env_name = kwargs.get('environment')
        config_dir = kwargs.get('config_dir', '.')
        strategy_name = kwargs.get('strategy', 'smart')
        
        if not env_name:
            raise ValueError("Environment name must be specified")
        
        # 戦略を設定
        try:
            strategy = MergeStrategy(strategy_name)
        except ValueError:
            strategy = MergeStrategy.SMART
        
        # 環境設定ファイルを検索
        config_dir = Path(config_dir)
        env_config_files = []
        
        # 環境設定ファイルのパターン
        patterns = [
            f"{env_name}.yaml",
            f"{env_name}.yml",
            f"config.{env_name}.yaml",
            f"config.{env_name}.yml"
        ]
        
        for pattern in patterns:
            config_file = config_dir / pattern
            if config_file.exists():
                env_config_files.append(config_file)
                break
        
        if not env_config_files:
            # 環境設定ファイルが見つからない場合は基本データを返す
            return copy.deepcopy(data)
        
        # 環境設定を読み込み
        processor = HierarchyProcessor(default_strategy=strategy)
        processor.load_base_config(env_config_files[0])
        
        # マージ実行
        result = processor.get_merged_config(target_env=env_name, strategy=strategy)
        return result


class ConfigMergeCommand(BaseCommand):
    """複数設定ファイルマージコマンド"""
    
    name = 'config_merge'
    description = 'Merge multiple configuration files'
    category = 'configuration'
    input_types = ['dict']
    output_types = ['dict']
    
    async def execute(self, data: Any, *args, **kwargs) -> Any:
        """複数設定ファイルをマージ"""
        config_files = kwargs.get('files', [])
        strategy_name = kwargs.get('strategy', 'smart')
        output_file = kwargs.get('output')
        output_format = kwargs.get('format', 'yaml')
        
        if not config_files:
            return data
        
        # 戦略を設定
        try:
            strategy = MergeStrategy(strategy_name)
        except ValueError:
            strategy = MergeStrategy.SMART
        
        # 設定ファイルを読み込み
        processor = HierarchyProcessor(default_strategy=strategy)
        
        # 基本設定として現在のデータを使用
        configs = [data]
        
        # 追加の設定ファイルを読み込み
        for config_file in config_files:
            if Path(config_file).exists():
                processor.load_base_config(config_file)
                if processor.base_config:
                    configs.append(processor.base_config)
        
        # マージ実行
        result = processor.merge_configs(configs, strategy)
        
        # 結果を保存
        if output_file:
            processor.save_merged_config(result, output_file, output_format)
        
        return result


class HierarchyInfoCommand(BaseCommand):
    """階層情報表示コマンド"""
    
    name = 'hierarchy_info'
    description = 'Display hierarchy information and merge strategy'
    category = 'information'
    input_types = ['any']
    output_types = ['dict']
    
    async def execute(self, data: Any, *args, **kwargs) -> Any:
        """階層情報を表示"""
        strategy_name = kwargs.get('strategy', 'smart')
        
        try:
            strategy = MergeStrategy(strategy_name)
        except ValueError:
            strategy = MergeStrategy.SMART
        
        # データの階層構造を分析
        hierarchy_info = self._analyze_hierarchy(data)
        
        info = {
            'strategy': strategy.value,
            'data_type': type(data).__name__,
            'hierarchy_depth': hierarchy_info['depth'],
            'total_keys': hierarchy_info['total_keys'],
            'structure': hierarchy_info['structure'],
            'merge_recommendation': self._get_merge_recommendation(data, strategy)
        }
        
        return info
    
    def _analyze_hierarchy(self, data: Any, depth: int = 0, max_depth: int = 10) -> Dict:
        """階層構造を分析"""
        if depth > max_depth:
            return {'depth': depth, 'total_keys': 0, 'structure': 'max_depth_reached'}
        
        if isinstance(data, dict):
            total_keys = len(data)
            structure = 'dict'
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    child_info = self._analyze_hierarchy(value, depth + 1, max_depth)
                    total_keys += child_info['total_keys']
        elif isinstance(data, list):
            total_keys = len(data)
            structure = 'list'
            for item in data:
                if isinstance(item, (dict, list)):
                    child_info = self._analyze_hierarchy(item, depth + 1, max_depth)
                    total_keys += child_info['total_keys']
        else:
            total_keys = 1
            structure = type(data).__name__
        
        return {
            'depth': depth,
            'total_keys': total_keys,
            'structure': structure
        }
    
    def _get_merge_recommendation(self, data: Any, strategy: MergeStrategy) -> str:
        """マージ戦略の推奨事項を取得"""
        if strategy == MergeStrategy.SMART:
            if isinstance(data, dict):
                return "Smart merge will analyze data structure and choose optimal strategy"
            elif isinstance(data, list):
                return "Smart merge will analyze list contents and choose between replace/merge/append"
            else:
                return "Smart merge will use deep copy for basic types"
        elif strategy == MergeStrategy.DEEP_COPY:
            return "Deep copy will completely replace all hierarchies"
        elif strategy == MergeStrategy.MERGE:
            return "Merge will combine hierarchies while preserving existing structure"
        elif strategy == MergeStrategy.APPEND:
            return "Append will add new items to existing lists"
        else:
            return "Unknown strategy"
