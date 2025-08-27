"""
JSON Processing Commands - Commands for JSON manipulation and processing.
"""

import asyncio
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
import json
import logging

from ..pipe.commands import BaseCommand
from .validator import JSONValidator, ValidationResult
from .jsonpath import JSONPathProcessor, JSONPathResult
from .converter import FormatConverter, ConversionResult

logger = logging.getLogger(__name__)


class JSONTransformCommand(BaseCommand):
    """JSON変換コマンド"""
    
    name = 'json_transform'
    description = 'Transform JSON data using JSONPath expressions'
    category = 'json'
    input_types = ['dict', 'list', 'str']
    output_types = ['dict', 'list', 'str']
    
    def __init__(self):
        super().__init__()
        self.processor = JSONPathProcessor()
    
    async def execute(self, data: Any, *args, **kwargs) -> Any:
        """JSON変換を実行"""
        transformations = kwargs.get('transformations', [])
        output_format = kwargs.get('output_format', 'dict')
        
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON input: {e}")
        
        result_data = data
        
        # 変換を順次実行
        for transform in transformations:
            if isinstance(transform, dict):
                path = transform.get('path')
                operation = transform.get('operation', 'query')
                value = transform.get('value')
                
                if not path:
                    continue
                
                if operation == 'query':
                    result_data = self.processor.query_all(result_data, path)
                elif operation == 'update':
                    self.processor.update(result_data, path, value)
                elif operation == 'delete':
                    self.processor.delete(result_data, path)
                elif operation == 'filter':
                    result_data = self.processor.filter_data(result_data, path)
                elif operation in ['sum', 'avg', 'min', 'max', 'count']:
                    result_data = self.processor.aggregate(result_data, path, operation)
        
        # 出力形式に応じて変換
        if output_format == 'json':
            return json.dumps(result_data, indent=2, ensure_ascii=False)
        elif output_format == 'str':
            return str(result_data)
        else:
            return result_data


class JSONPathCommand(BaseCommand):
    """JSONPathクエリコマンド"""
    
    name = 'jsonpath'
    description = 'Query JSON data using JSONPath expressions'
    category = 'json'
    input_types = ['dict', 'list', 'str']
    output_types = ['any']
    
    def __init__(self):
        super().__init__()
        self.processor = JSONPathProcessor()
    
    async def execute(self, data: Any, *args, **kwargs) -> Any:
        """JSONPathクエリを実行"""
        path = kwargs.get('path')
        operation = kwargs.get('operation', 'query')
        default = kwargs.get('default')
        extended = kwargs.get('extended', True)
        
        if not path:
            raise ValueError("JSONPath expression is required")
        
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON input: {e}")
        
        if operation == 'query':
            return self.processor.query_all(data, path, extended)
        elif operation == 'first':
            return self.processor.query_first(data, path, default, extended)
        elif operation == 'exists':
            return self.processor.exists(data, path, extended)
        elif operation == 'count':
            return self.processor.count(data, path, extended)
        else:
            raise ValueError(f"Unknown operation: {operation}")


class ValidateJSONCommand(BaseCommand):
    """JSON検証コマンド"""
    
    name = 'validate_json'
    description = 'Validate JSON data against schema'
    category = 'json'
    input_types = ['dict', 'list', 'str']
    output_types = ['dict']
    
    def __init__(self):
        super().__init__()
        self.validator = JSONValidator()
    
    async def execute(self, data: Any, *args, **kwargs) -> Any:
        """JSON検証を実行"""
        schema_name = kwargs.get('schema', 'basic')
        schema_file = kwargs.get('schema_file')
        schema_data = kwargs.get('schema_data')
        return_data = kwargs.get('return_data', False)
        
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON input: {e}")
        
        # スキーマを動的に追加
        if schema_file:
            self.validator.add_schema_from_file(schema_name, schema_file)
        elif schema_data:
            self.validator.add_schema(schema_name, schema_data)
        
        # 検証実行
        result = self.validator.validate(data, schema_name)
        
        # 結果を辞書形式で返す
        result_dict = {
            'valid': result.valid,
            'message': result.message,
            'errors': result.errors,
            'path': result.path,
            'schema_name': result.schema_name
        }
        
        if return_data:
            result_dict['data'] = data
        
        return result_dict


class JSONFormatCommand(BaseCommand):
    """JSON形式変換コマンド"""
    
    name = 'json_format'
    description = 'Convert between JSON, YAML, XML, CSV formats'
    category = 'json'
    input_types = ['dict', 'list', 'str']
    output_types = ['str']
    
    def __init__(self):
        super().__init__()
        self.converter = FormatConverter()
    
    async def execute(self, data: Any, *args, **kwargs) -> Any:
        """形式変換を実行"""
        to_format = kwargs.get('to_format', 'json')
        from_format = kwargs.get('from_format', 'auto')
        options = kwargs.get('options', {})
        
        # 入力データが文字列の場合、形式を自動検出
        if isinstance(data, str) and from_format == 'auto':
            from_format = self.converter.detect_format(data) or 'json'
        elif not isinstance(data, str):
            # Python オブジェクトの場合はJSONとして扱う
            data = json.dumps(data, ensure_ascii=False)
            from_format = 'json'
        
        # 変換実行
        result = self.converter.convert(data, from_format, to_format, **options)
        
        if result.success:
            return result.data
        else:
            raise ValueError(f"Conversion failed: {result.error}")


class JSONMergeCommand(BaseCommand):
    """JSON統合コマンド"""
    
    name = 'json_merge'
    description = 'Merge multiple JSON objects'
    category = 'json'
    input_types = ['dict', 'list']
    output_types = ['dict', 'list']
    
    async def execute(self, data: Any, *args, **kwargs) -> Any:
        """JSON統合を実行"""
        merge_data = kwargs.get('merge_with', [])
        strategy = kwargs.get('strategy', 'deep')
        
        if not isinstance(merge_data, list):
            merge_data = [merge_data]
        
        result = data
        
        for item in merge_data:
            if isinstance(item, str):
                try:
                    item = json.loads(item)
                except json.JSONDecodeError:
                    continue
            
            if strategy == 'deep':
                result = self._deep_merge(result, item)
            elif strategy == 'shallow':
                if isinstance(result, dict) and isinstance(item, dict):
                    result.update(item)
                elif isinstance(result, list) and isinstance(item, list):
                    result.extend(item)
            elif strategy == 'replace':
                result = item
        
        return result
    
    def _deep_merge(self, base: Any, override: Any) -> Any:
        """ディープマージ"""
        if isinstance(base, dict) and isinstance(override, dict):
            result = base.copy()
            for key, value in override.items():
                if key in result:
                    result[key] = self._deep_merge(result[key], value)
                else:
                    result[key] = value
            return result
        elif isinstance(base, list) and isinstance(override, list):
            return base + override
        else:
            return override


class JSONFilterCommand(BaseCommand):
    """JSONフィルターコマンド"""
    
    name = 'json_filter'
    description = 'Filter JSON data based on conditions'
    category = 'json'
    input_types = ['dict', 'list']
    output_types = ['dict', 'list']
    
    def __init__(self):
        super().__init__()
        self.processor = JSONPathProcessor()
    
    async def execute(self, data: Any, *args, **kwargs) -> Any:
        """JSONフィルターを実行"""
        filters = kwargs.get('filters', [])
        operation = kwargs.get('operation', 'and')  # 'and' or 'or'
        
        if not filters:
            return data
        
        if isinstance(data, list):
            return self._filter_list(data, filters, operation)
        elif isinstance(data, dict):
            return self._filter_dict(data, filters, operation)
        else:
            return data
    
    def _filter_list(self, data: List[Any], filters: List[Dict], operation: str) -> List[Any]:
        """リストをフィルター"""
        result = []
        
        for item in data:
            if self._matches_filters(item, filters, operation):
                result.append(item)
        
        return result
    
    def _filter_dict(self, data: Dict[str, Any], filters: List[Dict], operation: str) -> Dict[str, Any]:
        """辞書をフィルター"""
        if self._matches_filters(data, filters, operation):
            return data
        else:
            return {}
    
    def _matches_filters(self, item: Any, filters: List[Dict], operation: str) -> bool:
        """フィルター条件にマッチするかチェック"""
        results = []
        
        for filter_def in filters:
            path = filter_def.get('path', '$')
            operator = filter_def.get('operator', 'eq')
            value = filter_def.get('value')
            
            # JSONPathで値を取得
            item_value = self.processor.query_first(item, path)
            
            # 条件チェック
            if operator == 'eq':
                results.append(item_value == value)
            elif operator == 'ne':
                results.append(item_value != value)
            elif operator == 'gt':
                results.append(item_value > value if item_value is not None else False)
            elif operator == 'gte':
                results.append(item_value >= value if item_value is not None else False)
            elif operator == 'lt':
                results.append(item_value < value if item_value is not None else False)
            elif operator == 'lte':
                results.append(item_value <= value if item_value is not None else False)
            elif operator == 'in':
                results.append(item_value in value if isinstance(value, (list, tuple)) else False)
            elif operator == 'contains':
                results.append(value in item_value if isinstance(item_value, (str, list)) else False)
            elif operator == 'exists':
                results.append(item_value is not None)
            else:
                results.append(False)
        
        # 結果を統合
        if operation == 'and':
            return all(results)
        elif operation == 'or':
            return any(results)
        else:
            return False


class JSONStatsCommand(BaseCommand):
    """JSON統計コマンド"""
    
    name = 'json_stats'
    description = 'Generate statistics for JSON data'
    category = 'json'
    input_types = ['dict', 'list']
    output_types = ['dict']
    
    def __init__(self):
        super().__init__()
        self.processor = JSONPathProcessor()
    
    async def execute(self, data: Any, *args, **kwargs) -> Any:
        """JSON統計を生成"""
        paths = kwargs.get('paths', [])
        include_structure = kwargs.get('include_structure', True)
        
        stats = {}
        
        # 基本統計
        stats['type'] = type(data).__name__
        stats['size'] = len(str(data))
        
        if isinstance(data, dict):
            stats['key_count'] = len(data)
            stats['keys'] = list(data.keys())
        elif isinstance(data, list):
            stats['item_count'] = len(data)
            if data:
                stats['item_types'] = list(set(type(item).__name__ for item in data))
        
        # 構造分析
        if include_structure:
            stats['structure'] = self._analyze_structure(data)
        
        # 指定されたパスの統計
        if paths:
            stats['path_stats'] = {}
            for path in paths:
                values = self.processor.query_all(data, path)
                if values:
                    stats['path_stats'][path] = self._calculate_stats(values)
        
        return stats
    
    def _analyze_structure(self, data: Any, max_depth: int = 10, current_depth: int = 0) -> Dict[str, Any]:
        """データ構造を分析"""
        if current_depth > max_depth:
            return {'type': 'max_depth_reached'}
        
        if isinstance(data, dict):
            return {
                'type': 'object',
                'keys': len(data),
                'children': {
                    key: self._analyze_structure(value, max_depth, current_depth + 1)
                    for key, value in list(data.items())[:5]  # 最初の5つのキーのみ
                }
            }
        elif isinstance(data, list):
            return {
                'type': 'array',
                'length': len(data),
                'item_types': list(set(type(item).__name__ for item in data[:10])),  # 最初の10個のみ
                'sample': self._analyze_structure(data[0], max_depth, current_depth + 1) if data else None
            }
        else:
            return {
                'type': type(data).__name__,
                'value': str(data)[:100]  # 最初の100文字のみ
            }
    
    def _calculate_stats(self, values: List[Any]) -> Dict[str, Any]:
        """値の統計を計算"""
        stats = {
            'count': len(values),
            'types': list(set(type(v).__name__ for v in values))
        }
        
        # 数値統計
        numeric_values = [v for v in values if isinstance(v, (int, float))]
        if numeric_values:
            stats['numeric'] = {
                'count': len(numeric_values),
                'sum': sum(numeric_values),
                'avg': sum(numeric_values) / len(numeric_values),
                'min': min(numeric_values),
                'max': max(numeric_values)
            }
        
        # 文字列統計
        string_values = [v for v in values if isinstance(v, str)]
        if string_values:
            stats['string'] = {
                'count': len(string_values),
                'avg_length': sum(len(s) for s in string_values) / len(string_values),
                'min_length': min(len(s) for s in string_values),
                'max_length': max(len(s) for s in string_values)
            }
        
        return stats
