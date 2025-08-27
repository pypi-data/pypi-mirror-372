"""
JSONPath Processor - JSONPath query processing for strataregula.
"""

import json
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from pathlib import Path
import logging

try:
    from jsonpath_ng import parse as jsonpath_parse
    from jsonpath_ng.ext import parse as jsonpath_ext_parse
    JSONPATH_AVAILABLE = True
except ImportError:
    JSONPATH_AVAILABLE = False
    jsonpath_parse = None
    jsonpath_ext_parse = None

logger = logging.getLogger(__name__)


@dataclass
class JSONPathResult:
    """JSONPath処理の結果"""
    success: bool
    data: Any = None
    matches: List[Any] = None
    count: int = 0
    path: Optional[str] = None
    error: Optional[str] = None
    
    def __post_init__(self):
        if self.matches is None:
            self.matches = []
        self.count = len(self.matches)


class JSONPathProcessor:
    """JSONPathクエリ処理クラス"""
    
    def __init__(self):
        self.compiled_expressions = {}
        if not JSONPATH_AVAILABLE:
            logger.warning("jsonpath-ng not available, JSONPath functionality disabled")
    
    def query(self, data: Any, path: str, extended: bool = True) -> JSONPathResult:
        """JSONPathクエリを実行"""
        if not JSONPATH_AVAILABLE:
            return JSONPathResult(
                success=False,
                error="jsonpath-ng not available",
                path=path
            )
        
        try:
            # 式をコンパイル（キャッシュ）
            if path not in self.compiled_expressions:
                if extended:
                    self.compiled_expressions[path] = jsonpath_ext_parse(path)
                else:
                    self.compiled_expressions[path] = jsonpath_parse(path)
            
            expression = self.compiled_expressions[path]
            
            # クエリ実行
            matches = expression.find(data)
            values = [match.value for match in matches]
            
            logger.debug(f"JSONPath query '{path}' found {len(values)} matches")
            
            return JSONPathResult(
                success=True,
                data=data,
                matches=values,
                path=path
            )
            
        except Exception as e:
            logger.error(f"JSONPath query error: {e}")
            return JSONPathResult(
                success=False,
                error=str(e),
                path=path
            )
    
    def query_first(self, data: Any, path: str, default: Any = None, extended: bool = True) -> Any:
        """JSONPathクエリの最初の結果を取得"""
        result = self.query(data, path, extended)
        if result.success and result.matches:
            return result.matches[0]
        return default
    
    def query_all(self, data: Any, path: str, extended: bool = True) -> List[Any]:
        """JSONPathクエリのすべての結果を取得"""
        result = self.query(data, path, extended)
        if result.success:
            return result.matches
        return []
    
    def exists(self, data: Any, path: str, extended: bool = True) -> bool:
        """JSONPathが存在するかチェック"""
        result = self.query(data, path, extended)
        return result.success and len(result.matches) > 0
    
    def count(self, data: Any, path: str, extended: bool = True) -> int:
        """JSONPathのマッチ数を取得"""
        result = self.query(data, path, extended)
        return result.count if result.success else 0
    
    def update(self, data: Any, path: str, value: Any, extended: bool = True) -> JSONPathResult:
        """JSONPathで指定された場所の値を更新"""
        if not JSONPATH_AVAILABLE:
            return JSONPathResult(
                success=False,
                error="jsonpath-ng not available",
                path=path
            )
        
        try:
            # 式をコンパイル
            if path not in self.compiled_expressions:
                if extended:
                    self.compiled_expressions[path] = jsonpath_ext_parse(path)
                else:
                    self.compiled_expressions[path] = jsonpath_parse(path)
            
            expression = self.compiled_expressions[path]
            
            # 更新実行
            matches = expression.find(data)
            updated_count = 0
            
            for match in matches:
                match.full_path.update(data, value)
                updated_count += 1
            
            logger.debug(f"JSONPath update '{path}' updated {updated_count} items")
            
            return JSONPathResult(
                success=True,
                data=data,
                count=updated_count,
                path=path
            )
            
        except Exception as e:
            logger.error(f"JSONPath update error: {e}")
            return JSONPathResult(
                success=False,
                error=str(e),
                path=path
            )
    
    def delete(self, data: Any, path: str, extended: bool = True) -> JSONPathResult:
        """JSONPathで指定された場所の値を削除"""
        if not JSONPATH_AVAILABLE:
            return JSONPathResult(
                success=False,
                error="jsonpath-ng not available",
                path=path
            )
        
        try:
            # 式をコンパイル
            if path not in self.compiled_expressions:
                if extended:
                    self.compiled_expressions[path] = jsonpath_ext_parse(path)
                else:
                    self.compiled_expressions[path] = jsonpath_parse(path)
            
            expression = self.compiled_expressions[path]
            
            # 削除実行
            matches = expression.find(data)
            deleted_count = 0
            
            # 逆順で削除（インデックスの変更を避けるため）
            for match in reversed(matches):
                try:
                    if hasattr(match.context, 'value') and isinstance(match.context.value, dict):
                        del match.context.value[match.path.fields[0]]
                        deleted_count += 1
                    elif hasattr(match.context, 'value') and isinstance(match.context.value, list):
                        if isinstance(match.path.fields[0], int):
                            del match.context.value[match.path.fields[0]]
                            deleted_count += 1
                except Exception as del_error:
                    logger.warning(f"Could not delete item: {del_error}")
            
            logger.debug(f"JSONPath delete '{path}' deleted {deleted_count} items")
            
            return JSONPathResult(
                success=True,
                data=data,
                count=deleted_count,
                path=path
            )
            
        except Exception as e:
            logger.error(f"JSONPath delete error: {e}")
            return JSONPathResult(
                success=False,
                error=str(e),
                path=path
            )
    
    def filter_data(self, data: Any, filter_path: str, extended: bool = True) -> Any:
        """JSONPathフィルターでデータをフィルタリング"""
        result = self.query(data, filter_path, extended)
        if result.success and result.matches:
            return result.matches
        return data
    
    def aggregate(self, data: Any, path: str, operation: str = "sum", extended: bool = True) -> Any:
        """JSONPathで取得したデータを集約"""
        values = self.query_all(data, path, extended)
        
        if not values:
            return None
        
        try:
            if operation == "sum":
                return sum(v for v in values if isinstance(v, (int, float)))
            elif operation == "avg" or operation == "average":
                numeric_values = [v for v in values if isinstance(v, (int, float))]
                return sum(numeric_values) / len(numeric_values) if numeric_values else None
            elif operation == "min":
                return min(values)
            elif operation == "max":
                return max(values)
            elif operation == "count":
                return len(values)
            elif operation == "first":
                return values[0]
            elif operation == "last":
                return values[-1]
            else:
                logger.warning(f"Unknown aggregation operation: {operation}")
                return values
        except Exception as e:
            logger.error(f"Aggregation error: {e}")
            return None
    
    def clear_cache(self):
        """コンパイル済み式のキャッシュをクリア"""
        self.compiled_expressions.clear()
        logger.debug("Cleared JSONPath expression cache")
    
    def get_cache_size(self) -> int:
        """キャッシュサイズを取得"""
        return len(self.compiled_expressions)
    
    def validate_path(self, path: str, extended: bool = True) -> bool:
        """JSONPathの構文をチェック"""
        if not JSONPATH_AVAILABLE:
            return False
        
        try:
            if extended:
                jsonpath_ext_parse(path)
            else:
                jsonpath_parse(path)
            return True
        except Exception:
            return False
