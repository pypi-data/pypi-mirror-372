"""
CLI Command for Configuration Compilation

Provides the 'sr compile' command that replaces config_compiler.py
with enhanced features and backward compatibility.
"""

import click
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List
import logging
import json
import yaml

from ..core.config_compiler import ConfigCompiler, CompilationConfig
from ..core.pattern_expander import EnhancedPatternExpander, ExpansionRule

logger = logging.getLogger(__name__)


@click.command()
@click.option('--traffic', 
              type=click.Path(exists=True, path_type=Path),
              required=True,
              help='Traffic/service configuration file (YAML or JSON)')
@click.option('--prefectures', 
              type=click.Path(exists=True, path_type=Path),
              help='Prefecture/region configuration file (YAML or JSON)')
@click.option('--out', '--output',
              type=click.Path(path_type=Path),
              help='Output file path (default: stdout)')
@click.option('--format', 'output_format',
              type=click.Choice(['python', 'json', 'yaml']),
              default='python',
              help='Output format (default: python)')
@click.option('--template',
              type=click.Path(exists=True, path_type=Path),
              help='Custom template file for output generation')
@click.option('--chunk-size',
              type=int,
              default=1024,
              help='Chunk size for memory-efficient processing (default: 1024)')
@click.option('--max-memory',
              type=int,
              default=200,
              help='Maximum memory usage in MB (default: 200)')
@click.option('--no-metadata',
              is_flag=True,
              help='Exclude metadata from output')
@click.option('--no-provenance',
              is_flag=True,
              help='Exclude provenance tracking from output')
@click.option('--no-optimize',
              is_flag=True,
              help='Disable lookup optimizations')
@click.option('--verbose', '-v',
              is_flag=True,
              help='Verbose output')
@click.option('--plan',
              is_flag=True,
              help='Show compilation plan without executing')
@click.option('--stats',
              is_flag=True,
              help='Show detailed compilation statistics')
@click.option('--validate-only',
              is_flag=True,
              help='Validate input files without compilation')
@click.option('--dump-compiled-config',
              type=click.Path(path_type=Path),
              help='Dump compiled configuration for inspection (file path or use - for stdout)')
@click.option('--dump-format',
              type=click.Choice(['yaml', 'json', 'python', 'table', 'tree']),
              default='yaml',
              help='Format for dumped configuration (default: yaml)')
def compile_cmd(traffic: Path,
                prefectures: Optional[Path],
                out: Optional[Path],
                output_format: str,
                template: Optional[Path],
                chunk_size: int,
                max_memory: int,
                no_metadata: bool,
                no_provenance: bool,
                no_optimize: bool,
                verbose: bool,
                plan: bool,
                stats: bool,
                validate_only: bool,
                dump_compiled_config: Optional[Path],
                dump_format: str):
    """
    Compile configuration patterns into optimized static mappings.
    
    This command replaces config_compiler.py with enhanced features:
    - Regional/prefecture hierarchy support
    - Memory-efficient processing for large files
    - Multiple output formats (Python, JSON, YAML)
    - Provenance tracking and fingerprinting
    - Runtime optimization for O(1) lookups
    
    Examples:
    
        # Basic compilation (config_compiler.py replacement)
        sr compile --traffic configs/traffic.yaml --prefectures configs/prefectures.yaml --out compiled_config.py
        
        # Compile large configuration with memory limit
        sr compile --traffic large_config.json --max-memory 100 --chunk-size 512 --out optimized.py
        
        # Generate JSON output with statistics
        sr compile --traffic traffic.yaml --format json --stats --out config.json
        
        # Preview compilation plan
        sr compile --traffic traffic.yaml --plan
        
        # Validate configuration files only
        sr compile --traffic traffic.yaml --prefectures prefectures.yaml --validate-only
        
        # Dump compiled configuration for inspection
        sr compile --traffic traffic.yaml --dump-compiled-config compiled_dump.yaml
        
        # Dump to stdout in JSON format  
        sr compile --traffic traffic.yaml --dump-compiled-config - --dump-format json
        
        # Dump in table format for easy viewing
        sr compile --traffic traffic.yaml --dump-compiled-config - --dump-format table
        
        # Dump in tree format for hierarchical visualization
        sr compile --traffic traffic.yaml --dump-compiled-config - --dump-format tree
    """
    
    # Set up logging
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=log_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    try:
        # Create compilation config
        config = CompilationConfig(
            output_format=output_format,
            template_path=template,
            include_metadata=not no_metadata,
            include_provenance=not no_provenance,
            optimize_lookups=not no_optimize,
            chunk_size=chunk_size,
            max_memory_mb=max_memory
        )
        
        # Validation mode
        if validate_only:
            return _validate_files(traffic, prefectures)
        
        # Plan mode
        if plan:
            return _show_compilation_plan(traffic, prefectures, config)
        
        # Create compiler
        compiler = ConfigCompiler(config)
        
        # Set up progress callback for large files
        def progress_callback(current: int, total: int):
            if verbose:
                percentage = (current / total) * 100 if total > 0 else 0
                click.echo(f"Processing: {current}/{total} chunks ({percentage:.1f}%)", err=True)
        
        # Compile configuration
        click.echo("Starting compilation...", err=True)
        
        if _is_large_file(traffic):
            # Use streaming compilation for large files
            if not out:
                click.echo("Error: Output file required for large file compilation", err=True)
                sys.exit(1)
            
            compiler.compile_large_config(traffic, out, progress_callback if verbose else None)
            compiled_content = ""  # Already written to file
            
        else:
            # Standard compilation
            compiled_content = compiler.compile_traffic_config(traffic, prefectures, out)
        
        # Output results
        if not out and compiled_content:
            click.echo(compiled_content)
        elif out:
            click.echo(f"Compilation successful. Output written to: {out}", err=True)
        
        # Dump compiled configuration if requested
        if dump_compiled_config:
            _dump_compiled_configuration(compiler, traffic, prefectures, dump_compiled_config, dump_format, verbose)
        
        # Show statistics if requested
        if stats:
            _show_compilation_stats(compiler)
        
        click.echo("Compilation completed successfully.", err=True)
        
    except Exception as e:
        click.echo(f"Compilation failed: {e}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def _validate_files(traffic_file: Path, prefectures_file: Optional[Path]) -> None:
    """Validate input configuration files."""
    click.echo("Validating configuration files...", err=True)
    
    errors = []
    
    # Validate traffic file
    try:
        compiler = ConfigCompiler()
        traffic_data = compiler._load_file(traffic_file)
        if not traffic_data:
            errors.append(f"Traffic file is empty or invalid: {traffic_file}")
        else:
            patterns = compiler._extract_service_patterns(traffic_data)
            if not patterns:
                errors.append(f"No service patterns found in traffic file: {traffic_file}")
            else:
                click.echo(f"✓ Traffic file valid: {len(patterns)} patterns found", err=True)
        
    except Exception as e:
        errors.append(f"Invalid traffic file {traffic_file}: {e}")
    
    # Validate prefectures file if provided
    if prefectures_file:
        try:
            compiler = ConfigCompiler()
            pref_data = compiler._load_file(prefectures_file)
            if not pref_data:
                errors.append(f"Prefectures file is empty or invalid: {prefectures_file}")
            else:
                click.echo(f"✓ Prefectures file valid", err=True)
                
                # Check for expected structure
                if 'prefectures' in pref_data:
                    pref_count = len(pref_data['prefectures'])
                    click.echo(f"  - {pref_count} prefectures configured", err=True)
                
                if 'regions' in pref_data:
                    region_count = len(pref_data['regions'])
                    click.echo(f"  - {region_count} regions configured", err=True)
        
        except Exception as e:
            errors.append(f"Invalid prefectures file {prefectures_file}: {e}")
    
    # Report validation results
    if errors:
        click.echo("Validation failed with errors:", err=True)
        for error in errors:
            click.echo(f"  ✗ {error}", err=True)
        sys.exit(1)
    else:
        click.echo("✓ All files validated successfully", err=True)


def _show_compilation_plan(traffic_file: Path, 
                          prefectures_file: Optional[Path], 
                          config: CompilationConfig) -> None:
    """Show compilation plan without executing."""
    click.echo("=== Compilation Plan ===", err=True)
    click.echo(f"Input files:", err=True)
    click.echo(f"  Traffic: {traffic_file}", err=True)
    click.echo(f"  Prefectures: {prefectures_file or 'Not provided'}", err=True)
    click.echo("", err=True)
    
    click.echo(f"Configuration:", err=True)
    click.echo(f"  Output format: {config.output_format}", err=True)
    click.echo(f"  Chunk size: {config.chunk_size}", err=True)
    click.echo(f"  Max memory: {config.max_memory_mb} MB", err=True)
    click.echo(f"  Include metadata: {config.include_metadata}", err=True)
    click.echo(f"  Include provenance: {config.include_provenance}", err=True)
    click.echo(f"  Optimize lookups: {config.optimize_lookups}", err=True)
    click.echo("", err=True)
    
    # Analyze input files
    try:
        compiler = ConfigCompiler(config)
        traffic_data = compiler._load_file(traffic_file)
        patterns = compiler._extract_service_patterns(traffic_data)
        
        click.echo(f"Analysis:", err=True)
        click.echo(f"  Service patterns: {len(patterns)}", err=True)
        
        # Estimate expansion
        expander = EnhancedPatternExpander()
        if prefectures_file:
            pref_data = compiler._load_file(prefectures_file)
            compiler._setup_hierarchy_from_config(pref_data)
            expander = compiler.expander
        
        # Sample expansion to estimate output size
        sample_patterns = dict(list(patterns.items())[:min(10, len(patterns))])
        sample_result = expander.compile_to_static_mapping(sample_patterns)
        
        estimated_direct = len(sample_result['direct_mapping'])
        estimated_component = len(sample_result['component_mapping'])
        expansion_ratio = (estimated_direct + estimated_component) / len(sample_patterns) if sample_patterns else 1
        
        total_estimated = int(len(patterns) * expansion_ratio)
        
        click.echo(f"  Estimated expanded mappings: {total_estimated}", err=True)
        click.echo(f"  Expected direct mappings: {int(total_estimated * 0.3)}", err=True)
        click.echo(f"  Expected component mappings: {int(total_estimated * 0.7)}", err=True)
        click.echo("", err=True)
        
        # Memory estimation
        estimated_memory_mb = (total_estimated * 64) / (1024 * 1024)  # Rough estimate
        use_streaming = estimated_memory_mb > config.max_memory_mb
        
        click.echo(f"Processing strategy:", err=True)
        click.echo(f"  Estimated memory usage: {estimated_memory_mb:.1f} MB", err=True)
        click.echo(f"  Use streaming: {use_streaming}", err=True)
        click.echo(f"  Estimated processing time: {_estimate_processing_time(len(patterns))} seconds", err=True)
        
    except Exception as e:
        click.echo(f"Unable to analyze input files: {e}", err=True)


def _show_compilation_stats(compiler: ConfigCompiler) -> None:
    """Show detailed compilation statistics."""
    click.echo("\n=== Compilation Statistics ===", err=True)
    
    try:
        # Get expansion stats
        expansion_stats = compiler.expander.get_expansion_stats()
        
        click.echo("Pattern Expansion:", err=True)
        click.echo(f"  Rules loaded: {expansion_stats['rules_count']}", err=True)
        click.echo(f"  Cache entries: {expansion_stats['cache_size']}", err=True)
        click.echo(f"  Cache max size: {expansion_stats['cache_max_size']}", err=True)
        
        click.echo("\nHierarchy Information:", err=True)
        hierarchy = expansion_stats['hierarchy_stats']
        for key, value in hierarchy.items():
            click.echo(f"  {key.capitalize()}: {value}", err=True)
        
        click.echo(f"\nData Sources: {', '.join(expansion_stats['data_sources'])}", err=True)
        
    except Exception as e:
        click.echo(f"Unable to gather statistics: {e}", err=True)


def _is_large_file(file_path: Path) -> bool:
    """Check if file is large and needs streaming processing."""
    try:
        size_mb = file_path.stat().st_size / (1024 * 1024)
        return size_mb > 10  # Files larger than 10MB use streaming
    except:
        return False


def _estimate_processing_time(pattern_count: int) -> float:
    """Estimate processing time based on pattern count."""
    # Very rough estimation: 1000 patterns per second base rate
    base_rate = 1000
    return max(1.0, pattern_count / base_rate)


def _dump_compiled_configuration(compiler: ConfigCompiler, 
                                traffic_file: Path,
                                prefectures_file: Optional[Path],
                                dump_path: Path,
                                dump_format: str,
                                verbose: bool) -> None:
    """Dump compiled configuration for inspection and debugging."""
    try:
        click.echo("Generating compiled configuration dump...", err=True)
        
        # Load and process the configuration
        traffic_data = compiler._load_file(traffic_file)
        patterns = compiler._extract_service_patterns(traffic_data)
        
        # Set up hierarchy if prefectures file provided
        if prefectures_file:
            pref_data = compiler._load_file(prefectures_file)
            compiler._setup_hierarchy_from_config(pref_data)
        
        # Generate compiled mapping
        compiled_result = compiler.expander.compile_to_static_mapping(patterns)
        
        # Create comprehensive dump data
        dump_data = {
            'metadata': {
                'source_files': {
                    'traffic': str(traffic_file),
                    'prefectures': str(prefectures_file) if prefectures_file else None
                },
                'compilation_timestamp': compiler.get_compilation_fingerprint() if hasattr(compiler, 'get_compilation_fingerprint') else 'unknown',
                'total_patterns': len(patterns),
                'total_direct_mappings': len(compiled_result['direct_mapping']),
                'total_component_mappings': len(compiled_result['component_mapping']),
                'expansion_ratio': (len(compiled_result['direct_mapping']) + len(compiled_result['component_mapping'])) / len(patterns) if patterns else 0
            },
            'original_patterns': patterns,
            'compiled_mappings': {
                'direct_mapping': compiled_result['direct_mapping'],
                'component_mapping': compiled_result['component_mapping']
            },
            'hierarchy_info': compiler.expander.get_expansion_stats()['hierarchy_stats'] if hasattr(compiler.expander, 'get_expansion_stats') else {},
            'pattern_analysis': _analyze_patterns(patterns, compiled_result)
        }
        
        # Format and output the dump
        formatted_output = _format_dump_output(dump_data, dump_format)
        
        # Output to file or stdout
        if str(dump_path) == '-':
            click.echo(formatted_output)
        else:
            with open(dump_path, 'w', encoding='utf-8') as f:
                f.write(formatted_output)
            
            file_size_kb = dump_path.stat().st_size / 1024
            click.echo(f"Configuration dump written to: {dump_path} ({file_size_kb:.1f} KB)", err=True)
        
        if verbose:
            click.echo(f"Dump contains {len(dump_data['compiled_mappings']['direct_mapping'])} direct mappings", err=True)
            click.echo(f"Dump contains {len(dump_data['compiled_mappings']['component_mapping'])} component mappings", err=True)
    
    except Exception as e:
        click.echo(f"Failed to dump compiled configuration: {e}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()


def _analyze_patterns(original_patterns: Dict[str, Any], compiled_result: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze patterns to provide insights in the dump."""
    analysis = {
        'pattern_types': {},
        'wildcard_usage': 0,
        'most_expanded_patterns': [],
        'complexity_metrics': {}
    }
    
    # Count pattern types
    for pattern in original_patterns:
        parts = pattern.split('.')
        pattern_type = f"{len(parts)}-part"
        analysis['pattern_types'][pattern_type] = analysis['pattern_types'].get(pattern_type, 0) + 1
        
        if '*' in pattern:
            analysis['wildcard_usage'] += 1
    
    # Find most expanded patterns
    direct_counts = {}
    component_counts = {}
    
    for key in compiled_result['direct_mapping']:
        root_pattern = _find_root_pattern(key, original_patterns)
        if root_pattern:
            direct_counts[root_pattern] = direct_counts.get(root_pattern, 0) + 1
    
    for key in compiled_result['component_mapping']:
        root_pattern = _find_root_pattern(key, original_patterns)
        if root_pattern:
            component_counts[root_pattern] = component_counts.get(root_pattern, 0) + 1
    
    # Get top 5 most expanded patterns
    all_counts = {}
    for pattern, count in direct_counts.items():
        all_counts[pattern] = count + component_counts.get(pattern, 0)
    
    analysis['most_expanded_patterns'] = [
        {'pattern': pattern, 'expansions': count} 
        for pattern, count in sorted(all_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    ]
    
    # Calculate complexity metrics
    total_original = len(original_patterns)
    total_compiled = len(compiled_result['direct_mapping']) + len(compiled_result['component_mapping'])
    
    analysis['complexity_metrics'] = {
        'expansion_factor': total_compiled / total_original if total_original > 0 else 0,
        'wildcard_percentage': (analysis['wildcard_usage'] / total_original * 100) if total_original > 0 else 0,
        'average_parts_per_pattern': sum(len(p.split('.')) for p in original_patterns) / total_original if total_original > 0 else 0
    }
    
    return analysis


def _find_root_pattern(expanded_key: str, original_patterns: Dict[str, Any]) -> Optional[str]:
    """Find which original pattern generated an expanded key."""
    # Simple heuristic: find the pattern that could have generated this key
    for pattern in original_patterns:
        if _pattern_matches(pattern, expanded_key):
            return pattern
    return None


def _pattern_matches(pattern: str, expanded_key: str) -> bool:
    """Check if a pattern could have generated an expanded key."""
    pattern_parts = pattern.split('.')
    key_parts = expanded_key.split('.')
    
    if len(pattern_parts) != len(key_parts):
        return False
    
    for pattern_part, key_part in zip(pattern_parts, key_parts):
        if pattern_part != '*' and pattern_part != key_part:
            return False
    
    return True


def _format_dump_output(dump_data: Dict[str, Any], format_type: str) -> str:
    """Format dump data according to specified format."""
    if format_type == 'json':
        return json.dumps(dump_data, indent=2, ensure_ascii=False, default=str)
    
    elif format_type == 'yaml':
        return yaml.dump(dump_data, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    elif format_type == 'python':
        return f"""# StrataRegula Compiled Configuration Dump
# Generated from: {dump_data['metadata']['source_files']['traffic']}

COMPILED_CONFIG = {repr(dump_data)}

# Quick Stats:
# - Original patterns: {dump_data['metadata']['total_patterns']}
# - Direct mappings: {dump_data['metadata']['total_direct_mappings']} 
# - Component mappings: {dump_data['metadata']['total_component_mappings']}
# - Expansion ratio: {dump_data['metadata']['expansion_ratio']:.2f}
"""
    
    elif format_type == 'table':
        return _format_table_output(dump_data)
    
    elif format_type == 'tree':
        return _format_tree_output(dump_data)
    
    else:
        return str(dump_data)


def _format_table_output(dump_data: Dict[str, Any]) -> str:
    """Format dump data as human-readable tables."""
    output = []
    
    # Header
    output.append("=" * 80)
    output.append("StrataRegula Compiled Configuration Dump")
    output.append("=" * 80)
    
    # Metadata
    metadata = dump_data['metadata']
    output.append(f"\nSource Files:")
    output.append(f"  Traffic: {metadata['source_files']['traffic']}")
    output.append(f"  Prefectures: {metadata['source_files']['prefectures'] or 'None'}")
    
    output.append(f"\nCompilation Summary:")
    output.append(f"  Original patterns: {metadata['total_patterns']}")
    output.append(f"  Direct mappings: {metadata['total_direct_mappings']}")
    output.append(f"  Component mappings: {metadata['total_component_mappings']}")
    output.append(f"  Expansion ratio: {metadata['expansion_ratio']:.2f}x")
    
    # Pattern Analysis
    analysis = dump_data['pattern_analysis']
    output.append(f"\nPattern Analysis:")
    output.append(f"  Wildcard usage: {analysis['wildcard_usage']} patterns ({analysis['complexity_metrics']['wildcard_percentage']:.1f}%)")
    output.append(f"  Average parts per pattern: {analysis['complexity_metrics']['average_parts_per_pattern']:.1f}")
    
    # Top expanded patterns
    if analysis['most_expanded_patterns']:
        output.append(f"\nMost Expanded Patterns:")
        for i, item in enumerate(analysis['most_expanded_patterns'], 1):
            output.append(f"  {i}. {item['pattern']} -> {item['expansions']} expansions")
    
    # Sample mappings (first 10)
    output.append(f"\nSample Direct Mappings (first 10):")
    direct_mappings = dump_data['compiled_mappings']['direct_mapping']
    for i, (key, value) in enumerate(list(direct_mappings.items())[:10]):
        output.append(f"  {key}: {value}")
    
    if len(direct_mappings) > 10:
        output.append(f"  ... and {len(direct_mappings) - 10} more direct mappings")
    
    # Sample component mappings
    output.append(f"\nSample Component Mappings (first 10):")
    component_mappings = dump_data['compiled_mappings']['component_mapping']
    for i, (key, components) in enumerate(list(component_mappings.items())[:10]):
        if isinstance(components, list) and len(components) > 0:
            first_component = components[0] if components else "N/A"
            count = len(components)
            output.append(f"  {key}: {first_component} (+{count-1} more)" if count > 1 else f"  {key}: {first_component}")
    
    if len(component_mappings) > 10:
        output.append(f"  ... and {len(component_mappings) - 10} more component mappings")
    
    output.append("=" * 80)
    
    return "\n".join(output)


def _format_tree_output(dump_data: Dict[str, Any]) -> str:
    """Format dump data as hierarchical tree structure."""
    output = []
    
    # Header
    output.append("TREE: StrataRegula Configuration Tree")
    output.append("=" * 50)
    
    metadata = dump_data['metadata']
    output.append(f"Source: {metadata['source_files']['traffic']}")
    output.append(f"Patterns: {metadata['total_patterns']} -> {metadata['total_direct_mappings'] + metadata['total_component_mappings']} mappings")
    output.append("")
    
    # Build tree structure from patterns
    tree_structure = _build_pattern_tree(dump_data)
    
    # Render tree
    output.append("Configuration Hierarchy:")
    output.extend(_render_tree_node(tree_structure, "", True))
    
    # Statistics
    analysis = dump_data['pattern_analysis']
    output.append("")
    output.append("Pattern Statistics:")
    output.append(f"|-- Wildcard Usage: {analysis['wildcard_usage']} patterns ({analysis['complexity_metrics']['wildcard_percentage']:.1f}%)")
    output.append(f"|-- Expansion Factor: {analysis['complexity_metrics']['expansion_factor']:.2f}x")
    output.append(f"`-- Avg Parts/Pattern: {analysis['complexity_metrics']['average_parts_per_pattern']:.1f}")
    
    return "\n".join(output)


def _build_pattern_tree(dump_data: Dict[str, Any]) -> Dict[str, Any]:
    """Build hierarchical tree structure from patterns."""
    tree = {}
    
    # Process both original patterns and compiled mappings
    all_mappings = {}
    all_mappings.update(dump_data['compiled_mappings']['direct_mapping'])
    all_mappings.update(dump_data['compiled_mappings']['component_mapping'])
    
    for pattern, value in all_mappings.items():
        parts = pattern.split('.')
        current = tree
        
        # Build path through tree
        for i, part in enumerate(parts):
            if part not in current:
                current[part] = {
                    '_children': {},
                    '_values': [],
                    '_type': _determine_part_type(part, i),
                    '_pattern_part': part
                }
            
            # Add value at leaf node
            if i == len(parts) - 1:
                current[part]['_values'].append({
                    'full_pattern': pattern,
                    'value': value,
                    'original': pattern in dump_data['original_patterns']
                })
            
            current = current[part]['_children']
    
    return tree


def _determine_part_type(part: str, position: int) -> str:
    """Determine the type of pattern part for tree visualization."""
    if part == '*':
        return 'wildcard'
    elif position == 0:
        return 'environment'
    elif position == 1:
        return 'service'
    elif position == 2:
        return 'config_type'
    else:
        return 'extended'


def _render_tree_node(node: Dict[str, Any], prefix: str = "", is_last: bool = True, level: int = 0) -> List[str]:
    """Recursively render tree nodes with proper tree formatting."""
    lines = []
    
    if level == 0:
        # Root level - just render children
        items = list(node.items())
        for i, (key, child) in enumerate(items):
            is_last_child = (i == len(items) - 1)
            lines.extend(_render_tree_node({key: child}, "", is_last_child, level + 1))
        return lines
    
    # Extract node items
    items = list(node.items())
    
    for i, (key, child) in enumerate(items):
        is_last_child = (i == len(items) - 1)
        
        # Determine tree symbols
        if is_last_child:
            current_prefix = prefix + "└── "
            child_prefix = prefix + "    "
        else:
            current_prefix = prefix + "├── "
            child_prefix = prefix + "│   "
        
        # Format current node
        node_info = child
        part_type = node_info.get('_type', 'unknown')
        values = node_info.get('_values', [])
        
        # Choose icon based on type
        icons = {
            'environment': '[ENV]',
            'service': '[SVC]',
            'config_type': '[CFG]',
            'wildcard': '[*]',
            'extended': '[EXT]'
        }
        icon = icons.get(part_type, '[?]')
        
        # Format the node line
        if values:
            # Leaf node with values
            value_summary = _format_tree_values(values)
            lines.append(f"{current_prefix}{icon} {key} {value_summary}")
        else:
            # Branch node
            lines.append(f"{current_prefix}{icon} {key}")
        
        # Recursively render children
        children = node_info.get('_children', {})
        if children:
            lines.extend(_render_tree_node(children, child_prefix, True, level + 1))
    
    return lines


def _format_tree_values(values: List[Dict[str, Any]]) -> str:
    """Format values for tree display."""
    if len(values) == 1:
        value = values[0]
        original_marker = "[ORIG]" if value['original'] else "[COMP]"
        return f"{original_marker} = {value['value']}"
    else:
        # Multiple values
        value_list = [str(v['value']) for v in values]
        original_count = sum(1 for v in values if v['original'])
        return f"[{len(values)} values: {', '.join(value_list[:2])}{'...' if len(values) > 2 else ''}] ({original_count} original)"


# Add to main CLI
def add_compile_command(cli_group):
    """Add compile command to the main CLI group."""
    cli_group.add_command(compile_cmd, name='compile')