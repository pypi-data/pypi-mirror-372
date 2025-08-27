"""
Configuration Compiler for strataregula MVP v0.1

Generates static Python modules for runtime O(1) config lookups.
Replaces config_compiler.py with enhanced features:
- Template-based code generation
- Multiple output formats
- Provenance tracking
- Memory-efficient compilation
"""

import json
import yaml
import time
import hashlib
from typing import Dict, List, Any, Optional, Union, TextIO
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime, timezone

from .pattern_expander import EnhancedPatternExpander, RegionHierarchy, StreamingPatternProcessor

import logging

logger = logging.getLogger(__name__)


def _safe_trigger_hook(plugin_manager, hook_name: str, **kwargs) -> None:
    """Safely trigger plugin hooks, handling both sync and async contexts."""
    if not plugin_manager or not hasattr(plugin_manager, 'hooks'):
        return
    
    try:
        # For sync contexts, we skip async hooks to avoid warnings
        # This is a simplified approach for the MVP
        logger.debug(f"Hook {hook_name} triggered with args: {kwargs}")
    except Exception as e:
        logger.debug(f"Hook {hook_name} failed: {e}")


@dataclass
class CompilationConfig:
    """Configuration for the compilation process."""
    input_format: str = "yaml"  # yaml, json
    output_format: str = "python"  # python, json, yaml
    template_path: Optional[Path] = None
    include_metadata: bool = True
    include_provenance: bool = True
    optimize_lookups: bool = True
    chunk_size: int = 1024
    max_memory_mb: int = 200


@dataclass
class ProvenanceInfo:
    """Compilation provenance information."""
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    version: str = "0.1.0"
    input_files: List[str] = field(default_factory=list)
    compilation_config: Dict[str, Any] = field(default_factory=dict)
    execution_fingerprint: str = ""
    performance_stats: Dict[str, Any] = field(default_factory=dict)


class TemplateEngine:
    """Template engine for code generation."""
    
    def __init__(self):
        self.templates = {
            'python': self._get_python_template(),
            'json': self._get_json_template(),
            'yaml': self._get_yaml_template()
        }
    
    def render(self, template_name: str, context: Dict[str, Any]) -> str:
        """Render template with given context."""
        if template_name not in self.templates:
            raise ValueError(f"Unknown template: {template_name}")
        
        template = self.templates[template_name]
        return template.format(**context)
    
    def _get_python_template(self) -> str:
        """Get Python module template."""
        return '''"""
Generated configuration module for strataregula.

This module provides O(1) lookup performance for compiled patterns.
Generated at: {timestamp}
Input files: {input_files}
Compilation fingerprint: {fingerprint}
"""

from typing import Dict, Any, List
import re

# Direct mapping for simple lookups
DIRECT_MAPPING = {direct_mapping_code}

# Component mapping for hierarchical lookups  
COMPONENT_MAPPING = {component_mapping_code}

# Metadata and provenance
METADATA = {metadata_code}

# Performance-optimized lookup functions
def get_service_time(service_name: str, default: float = 0.0) -> float:
    """Get service time with O(1) lookup."""
    # Try direct mapping first
    if service_name in DIRECT_MAPPING:
        return DIRECT_MAPPING[service_name]
    
    # Try component mapping
    if service_name in COMPONENT_MAPPING:
        return COMPONENT_MAPPING[service_name]
    
    return default

def get_service_info(service_name: str) -> Dict[str, Any]:
    """Get comprehensive service information."""
    service_time = get_service_time(service_name)
    
    return {{
        "service_name": service_name,
        "service_time": service_time,
        "found_in": "direct" if service_name in DIRECT_MAPPING else "component" if service_name in COMPONENT_MAPPING else "default",
        "metadata": METADATA
    }}

def list_all_services() -> List[str]:
    """List all available service names."""
    return sorted(set(list(DIRECT_MAPPING.keys()) + list(COMPONENT_MAPPING.keys())))

def get_services_by_pattern(pattern: str) -> Dict[str, float]:
    """Get services matching a pattern."""
    regex_pattern = pattern.replace('.', r'\\.').replace('*', r'[^.]*')
    compiled_regex = re.compile(f"^{{regex_pattern}}$")
    
    result = {{}}
    
    # Search direct mapping
    for service, time_val in DIRECT_MAPPING.items():
        if compiled_regex.match(service):
            result[service] = time_val
    
    # Search component mapping
    for service, time_val in COMPONENT_MAPPING.items():
        if compiled_regex.match(service):
            result[service] = time_val
    
    return result

# Regional and hierarchical lookup functions
{hierarchical_functions}

# Statistics and introspection
def get_compilation_stats() -> Dict[str, Any]:
    """Get compilation statistics."""
    return {{
        "total_services": len(DIRECT_MAPPING) + len(COMPONENT_MAPPING),
        "direct_mappings": len(DIRECT_MAPPING),
        "component_mappings": len(COMPONENT_MAPPING),
        "compilation_time": METADATA.get("performance_stats", {{}}).get("compilation_time_seconds", 0),
        "memory_usage_mb": METADATA.get("performance_stats", {{}}).get("peak_memory_mb", 0),
        "input_files": METADATA.get("provenance", {{}}).get("input_files", []),
        "fingerprint": METADATA.get("provenance", {{}}).get("execution_fingerprint", "")
    }}
'''

    def _get_json_template(self) -> str:
        """Get JSON template."""
        return '''{{
  "direct_mapping": {direct_mapping},
  "component_mapping": {component_mapping},
  "metadata": {metadata},
  "generated_at": "{timestamp}",
  "fingerprint": "{fingerprint}"
}}'''

    def _get_yaml_template(self) -> str:
        """Get YAML template."""
        return '''# Generated configuration for strataregula
# Generated at: {timestamp}
# Fingerprint: {fingerprint}

direct_mapping:
{direct_mapping_yaml}

component_mapping:
{component_mapping_yaml}

metadata:
{metadata_yaml}
'''


class ConfigCompiler:
    """Main configuration compiler."""
    
    def __init__(self, config: CompilationConfig = None, use_plugins: bool = True):
        self.config = config or CompilationConfig()
        
        # Initialize plugin system if enabled
        self.use_plugins = use_plugins
        if self.use_plugins:
            from ..plugins.config import PluginConfigManager
            from ..plugins.manager import EnhancedPluginManager
            
            self.plugin_config = PluginConfigManager()
            self.plugin_manager = EnhancedPluginManager(
                config=self.plugin_config.get_global_config()
            )
            # Discover and activate plugins
            self.plugin_manager.discover_plugins()
        else:
            self.plugin_manager = None
            
        self.expander = EnhancedPatternExpander(
            chunk_size=self.config.chunk_size,
            plugin_manager=self.plugin_manager
        )
        self.streaming_processor = StreamingPatternProcessor(
            self.expander, 
            max_memory_mb=self.config.max_memory_mb
        )
        self.template_engine = TemplateEngine()
        
    def compile_traffic_config(self, 
                             traffic_file: Path,
                             prefectures_file: Optional[Path] = None,
                             output_file: Path = None) -> str:
        """Compile traffic configuration - main entry point matching config_compiler.py."""
        start_time = time.time()
        
        try:
            # Hook: Pre-compilation
            _safe_trigger_hook(self.plugin_manager, 'pre_compilation', 
                              traffic_file=traffic_file,
                              prefectures_file=prefectures_file,
                              output_file=output_file)
            
            # Load input files
            traffic_data = self._load_file(traffic_file)
            
            # Set up hierarchy if prefecture file provided
            if prefectures_file and prefectures_file.exists():
                prefectures_data = self._load_file(prefectures_file)
                self._setup_hierarchy_from_config(prefectures_data)
            
            # Extract service patterns
            service_patterns = self._extract_service_patterns(traffic_data)
            
            # Hook: Pattern discovered
            _safe_trigger_hook(self.plugin_manager, 'pattern_discovered', 
                              patterns=service_patterns)
            
            # Hook: Pre-expansion
            _safe_trigger_hook(self.plugin_manager, 'pre_expand', 
                              patterns=service_patterns)
            
            # Compile patterns
            compiled_mapping = self.expander.compile_to_static_mapping(service_patterns)
            
            # Hook: Post-expansion
            _safe_trigger_hook(self.plugin_manager, 'post_expand', 
                              compiled_mapping=compiled_mapping)
            
            # Generate provenance
            provenance = self._generate_provenance([traffic_file, prefectures_file], start_time)
            
            # Create output context
            context = self._create_output_context(compiled_mapping, provenance)
            
            # Generate output
            output_content = self.template_engine.render(self.config.output_format, context)
            
            # Save to file if specified
            if output_file:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(output_content)
                logger.info(f"Compiled configuration saved to {output_file}")
            
            # Hook: Compilation complete
            _safe_trigger_hook(self.plugin_manager, 'compilation_complete',
                              output_content=output_content,
                              output_file=output_file,
                              duration=time.time() - start_time)
            
            return output_content
            
        except Exception as e:
            logger.error(f"Compilation failed: {e}")
            raise
    
    def compile_large_config(self, 
                           input_file: Path, 
                           output_file: Path,
                           progress_callback: Optional[callable] = None) -> None:
        """Compile large configuration files with streaming."""
        start_time = time.time()
        
        try:
            # Load input data
            input_data = self._load_file(input_file)
            service_patterns = self._extract_service_patterns(input_data)
            
            # Stream processing for large datasets
            all_mappings = {'direct_mapping': {}, 'component_mapping': {}}
            
            processed_chunks = 0
            total_chunks = max(1, len(service_patterns) // self.config.chunk_size)
            
            for chunk_result in self.streaming_processor.process_large_patterns(service_patterns):
                # Merge chunk results
                for key, value in chunk_result.items():
                    if '.' in key:
                        all_mappings['component_mapping'][key] = value
                    else:
                        all_mappings['direct_mapping'][key] = value
                
                processed_chunks += 1
                if progress_callback:
                    progress_callback(processed_chunks, total_chunks)
            
            # Generate final output
            provenance = self._generate_provenance([input_file], start_time)
            context = self._create_output_context(all_mappings, provenance)
            output_content = self.template_engine.render(self.config.output_format, context)
            
            # Save output
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(output_content)
            
            logger.info(f"Large configuration compiled to {output_file}")
            
        except Exception as e:
            logger.error(f"Large compilation failed: {e}")
            raise
    
    def _load_file(self, file_path: Path) -> Dict[str, Any]:
        """Load YAML or JSON file."""
        if not file_path or not file_path.exists():
            return {}
        
        with open(file_path, 'r', encoding='utf-8') as f:
            if file_path.suffix.lower() in ['.yaml', '.yml']:
                return yaml.safe_load(f) or {}
            elif file_path.suffix.lower() == '.json':
                return json.load(f)
            else:
                # Try to detect format
                content = f.read()
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    return yaml.safe_load(content) or {}
    
    def _setup_hierarchy_from_config(self, config_data: Dict[str, Any]) -> None:
        """Set up hierarchy from configuration data."""
        hierarchy = RegionHierarchy()
        
        if 'prefectures' in config_data:
            if isinstance(config_data['prefectures'], list):
                # List of prefectures - use default region mapping
                hierarchy.prefectures = {pref: 'default' for pref in config_data['prefectures']}
            elif isinstance(config_data['prefectures'], dict):
                # Prefecture to region mapping
                hierarchy.prefectures = config_data['prefectures']
        
        if 'regions' in config_data:
            hierarchy.regions = config_data['regions']
        
        if 'services' in config_data:
            hierarchy.services = config_data['services']
        
        if 'roles' in config_data:
            hierarchy.roles = config_data['roles']
        
        self.expander.set_hierarchy(hierarchy)
    
    def _extract_service_patterns(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract service patterns from input data."""
        # Look for common pattern structures
        if 'service_times' in data:
            return data['service_times']
        elif 'patterns' in data:
            return data['patterns']
        elif 'services' in data:
            return data['services']
        elif 'traffic' in data:
            return data['traffic']
        else:
            # Assume the entire data is service patterns
            return data
    
    def _generate_provenance(self, input_files: List[Path], start_time: float) -> ProvenanceInfo:
        """Generate compilation provenance information."""
        end_time = time.time()
        compilation_time = end_time - start_time
        
        # Create fingerprint from input files and config
        fingerprint_data = {
            'input_files': [str(f) for f in input_files if f],
            'config': {
                'input_format': self.config.input_format,
                'output_format': self.config.output_format,
                'chunk_size': self.config.chunk_size,
                'max_memory_mb': self.config.max_memory_mb
            },
            'timestamp': time.time()
        }
        
        fingerprint = hashlib.md5(
            json.dumps(fingerprint_data, sort_keys=True).encode(),
            usedforsecurity=False
        ).hexdigest()
        
        # Memory monitoring removed for simplified dependencies
        peak_memory_mb = 0
        
        return ProvenanceInfo(
            input_files=[str(f) for f in input_files if f],
            compilation_config=fingerprint_data['config'],
            execution_fingerprint=fingerprint,
            performance_stats={
                'compilation_time_seconds': compilation_time,
                'peak_memory_mb': peak_memory_mb,
                'patterns_processed': len(self.expander._expansion_cache._cache),
                'cache_size': len(self.expander._expansion_cache._cache)
            }
        )
    
    def _create_output_context(self, compiled_mapping: Dict[str, Any], provenance: ProvenanceInfo) -> Dict[str, Any]:
        """Create template context for output generation."""
        direct_mapping = compiled_mapping.get('direct_mapping', {})
        component_mapping = compiled_mapping.get('component_mapping', {})
        metadata = compiled_mapping.get('metadata', {})
        
        # Add provenance to metadata
        metadata['provenance'] = {
            'timestamp': provenance.timestamp,
            'version': provenance.version,
            'input_files': provenance.input_files,
            'execution_fingerprint': provenance.execution_fingerprint,
            'performance_stats': provenance.performance_stats
        }
        
        # Format for different output types
        if self.config.output_format == 'python':
            return {
                'timestamp': provenance.timestamp,
                'input_files': ', '.join(f.replace('\\', '\\\\') for f in provenance.input_files),
                'fingerprint': provenance.execution_fingerprint,
                'direct_mapping_code': self._format_python_dict(direct_mapping),
                'component_mapping_code': self._format_python_dict(component_mapping),
                'metadata_code': self._format_python_dict(metadata),
                'hierarchical_functions': self._generate_hierarchical_functions()
            }
        elif self.config.output_format == 'json':
            return {
                'timestamp': provenance.timestamp,
                'fingerprint': provenance.execution_fingerprint,
                'direct_mapping': json.dumps(direct_mapping, indent=2),
                'component_mapping': json.dumps(component_mapping, indent=2),
                'metadata': json.dumps(metadata, indent=2)
            }
        else:  # yaml
            # Indent YAML content properly
            direct_yaml = yaml.dump(direct_mapping, default_flow_style=False)
            component_yaml = yaml.dump(component_mapping, default_flow_style=False)
            metadata_yaml = yaml.dump(metadata, default_flow_style=False)
            
            # Add proper indentation for nested YAML
            direct_yaml = '  ' + direct_yaml.replace('\n', '\n  ').rstrip()
            component_yaml = '  ' + component_yaml.replace('\n', '\n  ').rstrip()
            metadata_yaml = '  ' + metadata_yaml.replace('\n', '\n  ').rstrip()
            
            return {
                'timestamp': provenance.timestamp,
                'fingerprint': provenance.execution_fingerprint,
                'direct_mapping_yaml': direct_yaml,
                'component_mapping_yaml': component_yaml,
                'metadata_yaml': metadata_yaml
            }
    
    def _format_python_dict(self, data: Dict[str, Any], indent: int = 4) -> str:
        """Format dictionary as Python code."""
        if not data:
            return "{}"
        
        lines = ["{"]
        items = list(data.items())
        
        for i, (key, value) in enumerate(items):
            comma = "," if i < len(items) - 1 else ""
            if isinstance(value, str):
                lines.append(f'{" " * indent}"{key}": "{value}"{comma}')
            elif isinstance(value, (int, float)):
                lines.append(f'{" " * indent}"{key}": {value}{comma}')
            else:
                value_str = json.dumps(value)
                lines.append(f'{" " * indent}"{key}": {value_str}{comma}')
        
        lines.append("}")
        return "\n".join(lines)
    
    def _generate_hierarchical_functions(self) -> str:
        """Generate hierarchical lookup functions."""
        return '''
def get_services_by_region(region: str) -> Dict[str, float]:
    """Get all services in a specific region."""
    result = {}
    region_prefectures = {region_prefectures_map}
    
    for service, time_val in COMPONENT_MAPPING.items():
        parts = service.split('.')
        if len(parts) >= 2 and parts[1] in region_prefectures.get(region, []):
            result[service] = time_val
    
    return result

def get_services_by_prefecture(prefecture: str) -> Dict[str, float]:
    """Get all services in a specific prefecture."""
    result = {}
    
    for service, time_val in COMPONENT_MAPPING.items():
        if f'.{prefecture}.' in service:
            result[service] = time_val
    
    return result
'''.replace('{region_prefectures_map}', str(self._get_region_prefecture_map()))
    
    def _get_region_prefecture_map(self) -> Dict[str, List[str]]:
        """Get mapping of regions to prefectures."""
        region_to_prefs = {}
        for pref, region in self.expander.hierarchy.prefectures.items():
            if region not in region_to_prefs:
                region_to_prefs[region] = []
            region_to_prefs[region].append(pref)
        return region_to_prefs


# CLI compatibility functions
def compile_config(traffic_file: str, prefectures_file: str = None, output_file: str = None) -> str:
    """CLI-compatible config compilation function."""
    compiler = ConfigCompiler()
    
    traffic_path = Path(traffic_file)
    prefectures_path = Path(prefectures_file) if prefectures_file else None
    output_path = Path(output_file) if output_file else None
    
    return compiler.compile_traffic_config(traffic_path, prefectures_path, output_path)