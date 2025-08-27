"""
Format Converter - Convert between JSON, YAML, XML, CSV and other formats.
"""

import json
import csv
import io
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from pathlib import Path
import logging

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

try:
    import defusedxml.ElementTree as ET
    import defusedxml.minidom as minidom
    XML_AVAILABLE = True
except ImportError:
    try:
        import xml.etree.ElementTree as ET
        import xml.dom.minidom as minidom
        XML_AVAILABLE = True
    except ImportError:
        XML_AVAILABLE = False
        ET = None
        minidom = None

try:
    import orjson
    ORJSON_AVAILABLE = True
except ImportError:
    ORJSON_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class ConversionResult:
    """変換結果"""
    success: bool
    data: Any = None
    format: Optional[str] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class FormatConverter:
    """形式変換クラス"""
    
    def __init__(self):
        self.supported_formats = ['json', 'yaml', 'yml', 'xml', 'csv', 'tsv']
        if ORJSON_AVAILABLE:
            self.supported_formats.append('orjson')
        logger.debug(f"Initialized FormatConverter with formats: {self.supported_formats}")
    
    def convert(self, data: Any, from_format: str, to_format: str, **options) -> ConversionResult:
        """データを指定された形式に変換"""
        try:
            # 入力形式から Python オブジェクトに変換
            if isinstance(data, str):
                parsed_data = self._parse_from_string(data, from_format, **options)
            else:
                parsed_data = data
            
            # Python オブジェクトから出力形式に変換
            converted_data = self._format_to_string(parsed_data, to_format, **options)
            
            return ConversionResult(
                success=True,
                data=converted_data,
                format=to_format,
                metadata={
                    'from_format': from_format,
                    'to_format': to_format,
                    'options': options
                }
            )
            
        except Exception as e:
            logger.error(f"Conversion error from {from_format} to {to_format}: {e}")
            return ConversionResult(
                success=False,
                error=str(e),
                metadata={
                    'from_format': from_format,
                    'to_format': to_format
                }
            )
    
    def _parse_from_string(self, data: str, format: str, **options) -> Any:
        """文字列から Python オブジェクトに解析"""
        format = format.lower()
        
        if format == 'json':
            return json.loads(data)
        elif format == 'orjson' and ORJSON_AVAILABLE:
            return orjson.loads(data)
        elif format in ['yaml', 'yml']:
            if not YAML_AVAILABLE:
                raise ValueError("PyYAML not available for YAML parsing")
            return yaml.safe_load(data)
        elif format == 'xml':
            return self._parse_xml(data, **options)
        elif format in ['csv', 'tsv']:
            return self._parse_csv(data, format, **options)
        else:
            raise ValueError(f"Unsupported input format: {format}")
    
    def _format_to_string(self, data: Any, format: str, **options) -> str:
        """Python オブジェクトから文字列に変換"""
        format = format.lower()
        
        if format == 'json':
            indent = options.get('indent', 2)
            ensure_ascii = options.get('ensure_ascii', False)
            return json.dumps(data, indent=indent, ensure_ascii=ensure_ascii)
        elif format == 'orjson' and ORJSON_AVAILABLE:
            option = orjson.OPT_INDENT_2
            if not options.get('ensure_ascii', True):
                option |= orjson.OPT_NON_STR_KEYS
            return orjson.dumps(data, option=option).decode('utf-8')
        elif format in ['yaml', 'yml']:
            if not YAML_AVAILABLE:
                raise ValueError("PyYAML not available for YAML formatting")
            return yaml.dump(data, default_flow_style=False, allow_unicode=True, **options)
        elif format == 'xml':
            return self._format_xml(data, **options)
        elif format in ['csv', 'tsv']:
            return self._format_csv(data, format, **options)
        else:
            raise ValueError(f"Unsupported output format: {format}")
    
    def _parse_xml(self, xml_string: str, **options) -> Dict[str, Any]:
        """XMLを辞書に変換"""
        if not XML_AVAILABLE:
            raise ValueError("XML support not available")
        
        try:
            root = ET.fromstring(xml_string)
            return self._xml_element_to_dict(root)
        except ET.ParseError as e:
            raise ValueError(f"Invalid XML: {e}")
    
    def _xml_element_to_dict(self, element) -> Dict[str, Any]:
        """XML要素を辞書に変換"""
        result = {}
        
        # 属性を追加
        if element.attrib:
            result['@attributes'] = element.attrib
        
        # テキストコンテンツを追加
        if element.text and element.text.strip():
            if len(element) == 0:  # 子要素がない場合
                return element.text.strip()
            else:
                result['#text'] = element.text.strip()
        
        # 子要素を処理
        children = {}
        for child in element:
            child_data = self._xml_element_to_dict(child)
            if child.tag in children:
                if not isinstance(children[child.tag], list):
                    children[child.tag] = [children[child.tag]]
                children[child.tag].append(child_data)
            else:
                children[child.tag] = child_data
        
        result.update(children)
        
        # ルート要素の場合はタグ名をキーにする
        if not hasattr(self, '_in_recursion'):
            self._in_recursion = True
            result = {element.tag: result}
            del self._in_recursion
        
        return result
    
    def _format_xml(self, data: Any, **options) -> str:
        """辞書をXMLに変換"""
        if not XML_AVAILABLE or ET is None:
            raise ValueError("XML support not available")
        
        root_name = options.get('root', 'root')
        
        if isinstance(data, dict) and len(data) == 1:
            # 単一のルート要素がある場合
            root_name = list(data.keys())[0]
            data = data[root_name]
        
        root = ET.Element(root_name)
        self._dict_to_xml_element(root, data)
        
        # 整形
        rough_string = ET.tostring(root, encoding='unicode')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ").strip()
    
    def _dict_to_xml_element(self, parent, data: Any):
        """辞書をXML要素に変換"""
        if isinstance(data, dict):
            for key, value in data.items():
                if key == '@attributes':
                    parent.attrib.update(value)
                elif key == '#text':
                    parent.text = str(value)
                else:
                    if isinstance(value, list):
                        for item in value:
                            child = ET.SubElement(parent, key)
                            self._dict_to_xml_element(child, item)
                    else:
                        child = ET.SubElement(parent, key)
                        self._dict_to_xml_element(child, value)
        elif isinstance(data, list):
            for item in data:
                child = ET.SubElement(parent, 'item')
                self._dict_to_xml_element(child, item)
        else:
            parent.text = str(data)
    
    def _parse_csv(self, csv_string: str, format: str, **options) -> List[Dict[str, Any]]:
        """CSVを辞書のリストに変換"""
        delimiter = '\t' if format == 'tsv' else options.get('delimiter', ',')
        has_header = options.get('has_header', True)
        
        reader = csv.reader(io.StringIO(csv_string), delimiter=delimiter)
        rows = list(reader)
        
        if not rows:
            return []
        
        if has_header:
            headers = rows[0]
            data_rows = rows[1:]
            return [dict(zip(headers, row)) for row in data_rows]
        else:
            # ヘッダーがない場合は列番号をキーにする
            return [dict(enumerate(row)) for row in rows]
    
    def _format_csv(self, data: Any, format: str, **options) -> str:
        """辞書のリストをCSVに変換"""
        if not isinstance(data, list):
            raise ValueError("CSV format requires a list of dictionaries")
        
        if not data:
            return ""
        
        delimiter = '\t' if format == 'tsv' else options.get('delimiter', ',')
        include_header = options.get('include_header', True)
        
        output = io.StringIO()
        
        if isinstance(data[0], dict):
            fieldnames = list(data[0].keys())
            writer = csv.DictWriter(output, fieldnames=fieldnames, delimiter=delimiter)
            
            if include_header:
                writer.writeheader()
            
            for row in data:
                writer.writerow(row)
        else:
            writer = csv.writer(output, delimiter=delimiter)
            for row in data:
                if isinstance(row, (list, tuple)):
                    writer.writerow(row)
                else:
                    writer.writerow([row])
        
        return output.getvalue()
    
    def convert_file(self, input_file: Union[str, Path], output_file: Union[str, Path],
                    from_format: Optional[str] = None, to_format: Optional[str] = None,
                    **options) -> ConversionResult:
        """ファイル間の形式変換"""
        input_file = Path(input_file)
        output_file = Path(output_file)
        
        # 形式を自動検出
        if from_format is None:
            from_format = input_file.suffix[1:].lower()
        if to_format is None:
            to_format = output_file.suffix[1:].lower()
        
        try:
            # 入力ファイルを読み込み
            with open(input_file, 'r', encoding='utf-8') as f:
                input_data = f.read()
            
            # 変換実行
            result = self.convert(input_data, from_format, to_format, **options)
            
            if result.success:
                # 出力ファイルに書き込み
                output_file.parent.mkdir(parents=True, exist_ok=True)
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(result.data)
                
                result.metadata['input_file'] = str(input_file)
                result.metadata['output_file'] = str(output_file)
                logger.info(f"Converted {input_file} to {output_file}")
            
            return result
            
        except Exception as e:
            logger.error(f"File conversion error: {e}")
            return ConversionResult(
                success=False,
                error=str(e),
                metadata={
                    'input_file': str(input_file),
                    'output_file': str(output_file),
                    'from_format': from_format,
                    'to_format': to_format
                }
            )
    
    def detect_format(self, data: str) -> Optional[str]:
        """データの形式を自動検出"""
        data = data.strip()
        
        if not data:
            return None
        
        # JSON検出
        if (data.startswith('{') and data.endswith('}')) or \
           (data.startswith('[') and data.endswith(']')):
            try:
                json.loads(data)
                return 'json'
            except json.JSONDecodeError:
                pass
        
        # XML検出
        if data.startswith('<') and data.endswith('>'):
            try:
                if XML_AVAILABLE:
                    ET.fromstring(data)
                    return 'xml'
            except ET.ParseError:
                pass
        
        # YAML検出（JSONでもXMLでもない場合）
        if YAML_AVAILABLE:
            try:
                yaml.safe_load(data)
                return 'yaml'
            except yaml.YAMLError:
                pass
        
        # CSV検出（カンマまたはタブ区切り）
        lines = data.split('\n')
        if len(lines) > 1:
            first_line = lines[0]
            if ',' in first_line:
                return 'csv'
            elif '\t' in first_line:
                return 'tsv'
        
        return None
    
    def get_supported_formats(self) -> List[str]:
        """サポートされている形式の一覧を取得"""
        return self.supported_formats.copy()
    
    def is_format_supported(self, format: str) -> bool:
        """指定された形式がサポートされているかチェック"""
        return format.lower() in self.supported_formats
