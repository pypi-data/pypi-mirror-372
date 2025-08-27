"""
Hierarchy Merger - Core functionality for merging configurations with deep copy.
"""

import copy
from typing import Any, Dict, List, Union
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class MergeStrategy(Enum):
    """マージ戦略の定義"""
    DEEP_COPY = "deep_copy"      # 同名階層は完全に置き換え
    MERGE = "merge"              # 同名階層は統合
    APPEND = "append"            # リストは末尾に追加
    SMART = "smart"              # データ型に応じて自動選択


class HierarchyMerger:
    """同名階層のディープコピーとマージ処理"""
    
    def __init__(self, strategy: MergeStrategy = MergeStrategy.SMART):
        self.strategy = strategy
        logger.debug(f"Initialized HierarchyMerger with strategy: {strategy.value}")
    
    def merge(self, base: Any, override: Any) -> Any:
        """階層をマージ（同名の場合はディープコピー）"""
        logger.debug(f"Merging with strategy: {self.strategy.value}")
        
        if isinstance(base, dict) and isinstance(override, dict):
            return self._merge_dicts(base, override)
        elif isinstance(base, list) and isinstance(override, list):
            return self._merge_lists(base, override)
        else:
            # 基本型の場合はオーバーライド（ディープコピー）
            logger.debug("Basic type override with deep copy")
            return copy.deepcopy(override)
    
    def _merge_dicts(self, base: Dict, override: Dict) -> Dict:
        """辞書の階層マージ"""
        result = copy.deepcopy(base)
        
        for key, value in override.items():
            if key in result and isinstance(result[key], (dict, list)):
                # 同名の階層がある場合は再帰的にマージ
                logger.debug(f"Recursive merge for key: {key}")
                result[key] = self.merge(result[key], value)
            else:
                # 新しいキーまたは基本型の場合はディープコピー
                logger.debug(f"Deep copy for key: {key}")
                result[key] = copy.deepcopy(value)
        
        return result
    
    def _merge_lists(self, base: List, override: List) -> List:
        """リストの階層マージ"""
        if self.strategy == MergeStrategy.DEEP_COPY:
            # ディープコピーで完全置き換え
            logger.debug("List deep copy replacement")
            return copy.deepcopy(override)
        elif self.strategy == MergeStrategy.APPEND:
            # 末尾に追加
            logger.debug("List append merge")
            result = copy.deepcopy(base)
            result.extend(copy.deepcopy(override))
            return result
        elif self.strategy == MergeStrategy.MERGE:
            # インデックスでマージ
            logger.debug("List index-based merge")
            return self._merge_lists_by_index(base, override)
        elif self.strategy == MergeStrategy.SMART:
            # データ型に応じて自動選択
            return self._smart_list_merge(base, override)
        else:
            return copy.deepcopy(override)
    
    def _merge_lists_by_index(self, base: List, override: List) -> List:
        """インデックスベースでリストをマージ"""
        result = copy.deepcopy(base)
        
        for i, item in enumerate(override):
            if i < len(result):
                # 既存のインデックスがある場合はマージ
                if isinstance(result[i], (dict, list)):
                    result[i] = self.merge(result[i], item)
                else:
                    result[i] = copy.deepcopy(item)
            else:
                # 新しいインデックスの場合は追加
                result.append(copy.deepcopy(item))
        
        return result
    
    def _smart_list_merge(self, base: List, override: List) -> List:
        """スマートなリストマージ（データ型に応じて自動選択）"""
        # リストの内容を分析して最適な戦略を選択
        if self._are_simple_types(base) and self._are_simple_types(override):
            # 基本型のリストの場合は置き換え
            logger.debug("Smart merge: simple types -> replace")
            return copy.deepcopy(override)
        elif self._are_config_objects(base) and self._are_config_objects(override):
            # 設定オブジェクトの場合は統合
            logger.debug("Smart merge: config objects -> merge")
            return self._merge_lists_by_index(base, override)
        else:
            # デフォルトは追加
            logger.debug("Smart merge: mixed types -> append")
            result = copy.deepcopy(base)
            result.extend(copy.deepcopy(override))
            return result
    
    def _are_simple_types(self, items: List) -> bool:
        """リストが基本型のみで構成されているかチェック"""
        return all(isinstance(item, (str, int, float, bool, type(None))) for item in items)
    
    def _are_config_objects(self, items: List) -> bool:
        """リストが設定オブジェクト（辞書）で構成されているかチェック"""
        return all(isinstance(item, dict) for item in items)
    
    def merge_multiple(self, configs: List[Dict]) -> Dict:
        """複数の設定を順次マージ"""
        if not configs:
            return {}
        
        result = copy.deepcopy(configs[0])
        logger.debug(f"Starting merge of {len(configs)} configurations")
        
        for i, config in enumerate(configs[1:], 1):
            logger.debug(f"Merging configuration {i+1}/{len(configs)}")
            result = self.merge(result, config)
        
        return result
    
    def merge_with_environment(self, base: Dict, env_config: Dict, target_env: str) -> Dict:
        """環境別設定をマージ"""
        if env_config.get('environment') == target_env:
            logger.debug(f"Environment match found for: {target_env}")
            return self.merge(base, env_config)
        else:
            logger.debug(f"Environment mismatch, skipping: {env_config.get('environment')} != {target_env}")
            return copy.deepcopy(base)
    
    def resolve_conflicts(self, base: Dict, conflicts: List[Dict], priority_order: List[str] = None) -> Dict:
        """競合する設定を解決"""
        if not conflicts:
            return copy.deepcopy(base)
        
        result = copy.deepcopy(base)
        
        # 優先順位に基づいて競合を解決
        if priority_order:
            sorted_conflicts = self._sort_by_priority(conflicts, priority_order)
        else:
            sorted_conflicts = conflicts
        
        for conflict in sorted_conflicts:
            logger.debug(f"Resolving conflict with priority: {conflict.get('priority', 'default')}")
            result = self.merge(result, conflict)
        
        return result
    
    def _sort_by_priority(self, conflicts: List[Dict], priority_order: List[str]) -> List[Dict]:
        """優先順位に基づいて競合設定をソート"""
        def get_priority(config):
            priority = config.get('priority', 'default')
            try:
                return priority_order.index(priority)
            except ValueError:
                return len(priority_order)  # 優先順位が定義されていない場合は最後
        
        return sorted(conflicts, key=get_priority)
