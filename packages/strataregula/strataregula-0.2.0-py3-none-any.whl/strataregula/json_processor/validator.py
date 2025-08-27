"""
JSON Schema Validation - Comprehensive JSON validation for strataregula.
"""

import json
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from pathlib import Path
import logging

try:
    import jsonschema
    from jsonschema import ValidationError
    JSONSCHEMA_AVAILABLE = True
except ImportError:
    JSONSCHEMA_AVAILABLE = False
    ValidationError = Exception

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """JSON検証の結果"""
    valid: bool
    message: str
    errors: List[str] = None
    path: Optional[str] = None
    schema_name: Optional[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []


class JSONValidator:
    """JSONスキーマ検証クラス"""
    
    def __init__(self):
        self.schemas: Dict[str, dict] = {}
        self._load_default_schemas()
    
    def _load_default_schemas(self):
        """デフォルトスキーマを読み込み"""
        if not JSONSCHEMA_AVAILABLE:
            logger.warning("jsonschema not available, validation disabled")
            return
        
        # 基本的なJSONスキーマ
        basic_schema = {
            "type": "object",
            "properties": {},
            "additionalProperties": True
        }
        
        self.add_schema("basic", basic_schema)
        
        # 設定ファイル用スキーマ
        config_schema = {
            "type": "object",
            "properties": {
                "version": {"type": "string"},
                "settings": {"type": "object"},
                "data": {"type": "array"}
            },
            "required": ["version"]
        }
        
        self.add_schema("config", config_schema)
    
    def add_schema(self, name: str, schema: dict) -> bool:
        """スキーマを追加"""
        if not JSONSCHEMA_AVAILABLE:
            logger.warning("Cannot add schema: jsonschema not available")
            return False
        
        try:
            # スキーマの妥当性をチェック
            jsonschema.validators.validator_for(schema)
            self.schemas[name] = schema
            logger.debug(f"Added schema: {name}")
            return True
        except Exception as e:
            logger.error(f"Invalid schema '{name}': {e}")
            return False
    
    def add_schema_from_file(self, name: str, file_path: Union[str, Path]) -> bool:
        """ファイルからスキーマを読み込み"""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                logger.error(f"Schema file not found: {file_path}")
                return False
            
            with open(file_path, 'r', encoding='utf-8') as f:
                schema = json.load(f)
            
            return self.add_schema(name, schema)
        except Exception as e:
            logger.error(f"Error loading schema from file: {e}")
            return False
    
    def add_schema_from_string(self, name: str, schema_str: str) -> bool:
        """文字列からスキーマを読み込み"""
        try:
            schema = json.loads(schema_str)
            return self.add_schema(name, schema)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in schema string: {e}")
            return False
    
    def validate(self, data: Any, schema_name: str = None) -> ValidationResult:
        """データをスキーマで検証"""
        if not JSONSCHEMA_AVAILABLE:
            return ValidationResult(
                valid=True,
                message="Validation skipped: jsonschema not available"
            )
        
        # スキーマ名が指定されていない場合は基本スキーマを使用
        if schema_name is None:
            schema_name = "basic"
        
        if schema_name not in self.schemas:
            return ValidationResult(
                valid=False,
                message=f"Schema '{schema_name}' not found",
                schema_name=schema_name
            )
        
        try:
            jsonschema.validate(data, self.schemas[schema_name])
            return ValidationResult(
                valid=True,
                message="Validation passed",
                schema_name=schema_name
            )
        except ValidationError as e:
            errors = [str(e)]
            return ValidationResult(
                valid=False,
                message="Validation failed",
                errors=errors,
                path=str(e.path),
                schema_name=schema_name
            )
        except Exception as e:
            return ValidationResult(
                valid=False,
                message=f"Validation error: {e}",
                schema_name=schema_name
            )
    
    def validate_file(self, file_path: Union[str, Path], schema_name: str = None) -> ValidationResult:
        """ファイルの内容を検証"""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                return ValidationResult(
                    valid=False,
                    message=f"File not found: {file_path}"
                )
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return self.validate(data, schema_name)
        except json.JSONDecodeError as e:
            return ValidationResult(
                valid=False,
                message=f"Invalid JSON in file: {e}"
            )
        except Exception as e:
            return ValidationResult(
                valid=False,
                message=f"Error reading file: {e}"
            )
    
    def list_schemas(self) -> List[str]:
        """利用可能なスキーマの一覧を取得"""
        return list(self.schemas.keys())
    
    def get_schema(self, name: str) -> Optional[dict]:
        """スキーマを取得"""
        return self.schemas.get(name)
    
    def remove_schema(self, name: str) -> bool:
        """スキーマを削除"""
        if name in self.schemas:
            del self.schemas[name]
            logger.debug(f"Removed schema: {name}")
            return True
        return False
    
    def clear_schemas(self):
        """すべてのスキーマをクリア"""
        self.schemas.clear()
        self._load_default_schemas()
        logger.debug("Cleared all schemas")
