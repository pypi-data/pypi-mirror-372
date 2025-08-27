"""
Enhanced Pattern Expander for strataregula MVP v0.1

Extends the existing pattern compilation with:
- Regional and prefecture hierarchies
- Stream processing support
- Memory-efficient expansion
- Template-based output generation
- Backward compatibility with existing compiler.py
"""

import re
import json
import logging
from typing import Dict, List, Any, Optional, Tuple, Iterator, Union
from dataclasses import dataclass, field
from pathlib import Path
from functools import lru_cache

from .compiler import PatternCompiler, PatternCache

logger = logging.getLogger(__name__)


@dataclass
class ExpansionRule:
    """Enhanced rule for pattern expansion."""
    data_source: str
    template: str
    description: str = ""
    priority: int = 0
    conditions: Dict[str, Any] = field(default_factory=dict)
    transforms: List[str] = field(default_factory=list)


@dataclass  
class RegionHierarchy:
    """Regional hierarchy configuration."""
    regions: List[str] = field(default_factory=list)
    prefectures: Dict[str, str] = field(default_factory=dict)  # prefecture -> region
    cities: Dict[str, str] = field(default_factory=dict)  # city -> prefecture
    services: List[str] = field(default_factory=list)
    roles: List[str] = field(default_factory=list)


def _safe_async_trigger(plugin_manager, hook_name: str, **kwargs) -> None:
    """Safely trigger async hooks without warnings."""
    if not plugin_manager or not hasattr(plugin_manager.hooks, 'trigger'):
        return
    
    try:
        import asyncio
        try:
            # Only create task if we're in an async context
            loop = asyncio.get_running_loop()
            loop.create_task(plugin_manager.hooks.trigger(hook_name, **kwargs))
        except RuntimeError:
            # No async context, skip async hooks gracefully
            pass
    except Exception:
        # Graceful degradation if hooks fail
        pass


class EnhancedPatternExpander:
    """Enhanced pattern expander with hierarchical support."""
    
    def __init__(self, chunk_size: int = 1024, plugin_manager=None):
        self.base_compiler = PatternCompiler()
        self.hierarchy = RegionHierarchy()
        self.expansion_rules: Dict[str, ExpansionRule] = {}
        self.chunk_size = chunk_size
        self._expansion_cache = PatternCache(max_size=50000)
        self.plugin_manager = plugin_manager
        
        # Default Japanese prefectures and regions
        self._initialize_default_hierarchy()
    
    def _initialize_default_hierarchy(self) -> None:
        """Initialize default Japanese regional hierarchy."""
        # Standard Japanese prefectures
        default_prefectures = [
            'hokkaido', 'aomori', 'iwate', 'miyagi', 'akita', 'yamagata', 'fukushima',
            'ibaraki', 'tochigi', 'gunma', 'saitama', 'chiba', 'tokyo', 'kanagawa',
            'niigata', 'toyama', 'ishikawa', 'fukui', 'yamanashi', 'nagano',
            'gifu', 'shizuoka', 'aichi', 'mie', 'shiga', 'kyoto', 'osaka',
            'hyogo', 'nara', 'wakayama', 'tottori', 'shimane', 'okayama', 'hiroshima',
            'yamaguchi', 'tokushima', 'kagawa', 'ehime', 'kochi', 'fukuoka',
            'saga', 'nagasaki', 'kumamoto', 'oita', 'miyazaki', 'kagoshima', 'okinawa'
        ]
        
        # Regional groupings
        prefecture_to_region = {
            'tokyo': 'kanto', 'kanagawa': 'kanto', 'saitama': 'kanto', 'chiba': 'kanto',
            'ibaraki': 'kanto', 'tochigi': 'kanto', 'gunma': 'kanto',
            'osaka': 'kansai', 'kyoto': 'kansai', 'hyogo': 'kansai', 'nara': 'kansai',
            'wakayama': 'kansai', 'shiga': 'kansai',
            'aichi': 'chubu', 'gifu': 'chubu', 'shizuoka': 'chubu', 'yamanashi': 'chubu',
            'nagano': 'chubu', 'niigata': 'chubu', 'toyama': 'chubu', 'ishikawa': 'chubu', 'fukui': 'chubu',
            'hokkaido': 'hokkaido',
            'fukuoka': 'kyushu', 'saga': 'kyushu', 'nagasaki': 'kyushu', 'kumamoto': 'kyushu',
            'oita': 'kyushu', 'miyazaki': 'kyushu', 'kagoshima': 'kyushu', 'okinawa': 'kyushu'
        }
        
        # Fill remaining prefectures with 'other' region
        for pref in default_prefectures:
            if pref not in prefecture_to_region:
                prefecture_to_region[pref] = 'other'
        
        self.hierarchy.prefectures = prefecture_to_region
        self.hierarchy.regions = list(set(prefecture_to_region.values()))
        self.hierarchy.services = ['edge', 'service-hub', 'corebrain', 'gateway', 'api', 'web']
        self.hierarchy.roles = ['gateway', 'processor', 'worker', 'storage', 'monitor']
        
        # Update base compiler data sources
        self.base_compiler.set_data_sources({
            'regions': self.hierarchy.regions,
            'prefectures': list(self.hierarchy.prefectures.keys()),
            'services': self.hierarchy.services,
            'roles': self.hierarchy.roles
        })
        
        # Set up default pattern rules for common patterns
        self._setup_default_rules()
    
    def set_hierarchy(self, hierarchy: RegionHierarchy) -> None:
        """Set custom regional hierarchy."""
        self.hierarchy = hierarchy
        
        # Update base compiler
        self.base_compiler.set_data_sources({
            'regions': hierarchy.regions,
            'prefectures': list(hierarchy.prefectures.keys()) if hierarchy.prefectures else [],
            'services': hierarchy.services,
            'roles': hierarchy.roles,
            'cities': list(hierarchy.cities.keys()) if hierarchy.cities else []
        })
        
        # Clear caches
        self._expansion_cache.clear()
        
        # Setup default rules for new hierarchy
        self._setup_default_rules()
    
    def _setup_default_rules(self) -> None:
        """Setup default expansion rules for common patterns."""
        default_rules = {
            # Edge services use prefectures
            'edge.*.gateway': ExpansionRule(
                data_source='prefectures',
                template='edge.{prefecture}.gateway',
                description='Edge gateways by prefecture',
                priority=100
            ),
            'edge.*.api': ExpansionRule(
                data_source='prefectures', 
                template='edge.{prefecture}.api',
                description='Edge APIs by prefecture',
                priority=100
            ),
            'edge.*.web': ExpansionRule(
                data_source='prefectures',
                template='edge.{prefecture}.web', 
                description='Edge web services by prefecture',
                priority=100
            ),
            # Service hubs use regions
            'service-hub.*': ExpansionRule(
                data_source='regions',
                template='service-hub.{region}',
                description='Service hubs by region',
                priority=80
            ),
            'service-hub.*.*': ExpansionRule(
                data_source='regions',
                template='service-hub.{region}.{service}',
                description='Service hub services by region', 
                priority=90
            ),
            # Core brain services use regions
            'corebrain.*.*': ExpansionRule(
                data_source='regions',
                template='corebrain.{region}.{service}',
                description='Core brain services by region',
                priority=85
            )
        }
        
        for pattern, rule in default_rules.items():
            self.expansion_rules[pattern] = rule
            
            # Also add to base compiler for compatibility
            self.base_compiler.set_pattern_rules({
                **self.base_compiler.pattern_rules,
                pattern: {
                    'data_source': rule.data_source,
                    'template': rule.template,
                    'description': rule.description,
                    'priority': rule.priority
                }
            })
    
    def add_expansion_rule(self, pattern: str, rule: ExpansionRule) -> None:
        """Add or update an expansion rule."""
        self.expansion_rules[pattern] = rule
        
        # Also update base compiler pattern rules for backward compatibility
        self.base_compiler.set_pattern_rules({
            **self.base_compiler.pattern_rules,
            pattern: {
                'data_source': rule.data_source,
                'template': rule.template,
                'description': rule.description,
                'priority': rule.priority
            }
        })
        
        self._expansion_cache.clear()
    
    def load_rules_from_config(self, config_path: Path) -> None:
        """Load expansion rules from YAML configuration."""
        self.base_compiler.load_config(config_path)
        
        # Convert base compiler rules to enhanced rules
        for pattern, rule_data in self.base_compiler.pattern_rules.items():
            if isinstance(rule_data, dict):
                enhanced_rule = ExpansionRule(
                    data_source=rule_data.get('data_source', 'regions'),
                    template=rule_data.get('template', pattern),
                    description=rule_data.get('description', ''),
                    priority=rule_data.get('priority', 0)
                )
                self.expansion_rules[pattern] = enhanced_rule
    
    def expand_pattern_stream(self, patterns: Dict[str, Any]) -> Iterator[Tuple[str, Any]]:
        """Stream-based pattern expansion for memory efficiency."""
        # Hook point: Pre-compilation
        if self.plugin_manager:
            _safe_async_trigger(
                self.plugin_manager,
                'pre_compilation',
                patterns=patterns,
                expander=self
            )
        
        # Sort patterns by priority for consistent expansion order
        sorted_patterns = sorted(patterns.items(), key=lambda x: self._get_pattern_priority(x[0]))
        
        for pattern, value in sorted_patterns:
            # Hook point: Pre-expand
            if self.plugin_manager:
                try:
                    # Check if any plugin can handle this pattern
                    plugin_result = self.plugin_manager.expand_pattern(
                        pattern, 
                        {'value': value, 'hierarchy': self.hierarchy}
                    )
                    if plugin_result != {pattern: value}:  # Plugin handled it
                        for expanded_key, expanded_value in plugin_result.items():
                            yield expanded_key, expanded_value
                        continue
                except:
                    pass  # Fall through to default expansion
            
            cache_key = f"{pattern}:{hash(str(value))}"
            cached_result = self._expansion_cache.get(cache_key)
            
            if cached_result is not None:
                for expanded_key, expanded_value in cached_result.items():
                    yield expanded_key, expanded_value
                continue
            
            # Hook point: Pre-expand (for default expansion)
            if self.plugin_manager:
                _safe_async_trigger(
                    self.plugin_manager,
                    'pre_expand',
                    pattern=pattern,
                    value=value,
                    expander=self
                )
            
            # Expand pattern
            expanded = self._expand_pattern_enhanced(pattern, value)
            
            # Hook point: Post-expand
            if self.plugin_manager:
                _safe_async_trigger(
                    self.plugin_manager,
                    'post_expand',
                    pattern=pattern,
                    value=value,
                    result=expanded,
                    expander=self
                )
            
            # Cache result
            self._expansion_cache.set(cache_key, expanded)
            
            # Yield results
            for expanded_key, expanded_value in expanded.items():
                yield expanded_key, expanded_value
        
        # Hook point: Compilation complete
        if self.plugin_manager:
            _safe_async_trigger(
                self.plugin_manager,
                'compilation_complete',
                total_patterns=len(patterns),
                expander=self
            )
    
    def _get_pattern_priority(self, pattern: str) -> int:
        """Get priority for pattern sorting."""
        if pattern in self.expansion_rules:
            return self.expansion_rules[pattern].priority
        
        # Default priority based on specificity (more specific = higher priority)
        wildcard_count = pattern.count('*')
        specificity = len(pattern.split('.')) - wildcard_count
        return specificity * 100  # Higher specificity = higher priority
    
    def _expand_pattern_enhanced(self, pattern: str, value: Any) -> Dict[str, Any]:
        """Enhanced pattern expansion with hierarchical support."""
        if '*' not in pattern:
            return {pattern: value}
        
        # Use enhanced rules if available
        if pattern in self.expansion_rules:
            return self._expand_with_enhanced_rule(pattern, value, self.expansion_rules[pattern])
        
        # Check if base compiler has matching rules
        matching_rule = self.base_compiler._find_matching_rule(pattern)
        if matching_rule:
            # Fall back to base compiler
            return self.base_compiler._expand_pattern(pattern, value)
        
        # No rule found - return as-is
        return {pattern: value}
    
    def _expand_with_enhanced_rule(self, pattern: str, value: Any, rule: ExpansionRule) -> Dict[str, Any]:
        """Expand pattern using enhanced rule with hierarchical support."""
        data_source = rule.data_source
        template = rule.template
        
        # Get data items based on data source
        data_items = self._get_data_items(data_source)
        if not data_items:
            logger.warning(f"No data found for source '{data_source}' in pattern '{pattern}'")
            return {pattern: value}
        
        # Apply conditions if specified
        if rule.conditions:
            data_items = self._apply_conditions(data_items, rule.conditions)
        
        # Expand with template
        result = {}
        pattern_parts = pattern.split('.')
        
        # Find wildcard positions
        wildcard_indices = [i for i, part in enumerate(pattern_parts) if part == '*']
        
        if len(wildcard_indices) == 1:
            # Single wildcard expansion
            wildcard_idx = wildcard_indices[0]
            for item in data_items:
                expanded_parts = pattern_parts.copy()
                expanded_parts[wildcard_idx] = item
                expanded_key = '.'.join(expanded_parts)
                
                # Apply transforms if specified
                final_value = self._apply_transforms(value, rule.transforms, item)
                result[expanded_key] = final_value
        else:
            # Multiple wildcard expansion - need different data sources for each wildcard
            import itertools
            
            # For multiple wildcards, we need to handle data source mapping
            # For now, use the same data source for all wildcards (can be enhanced later)
            data_source_for_wildcards = []
            for wildcard_idx in wildcard_indices:
                # Could be enhanced to use different sources based on position
                if rule.data_source == 'roles' and len(data_source_for_wildcards) == 1:
                    # Second wildcard gets roles when first is prefectures
                    data_source_for_wildcards.append(self._get_data_items('roles'))
                else:
                    data_source_for_wildcards.append(data_items)
            
            # Generate combinations
            for combination in itertools.product(*data_source_for_wildcards):
                expanded_parts = pattern_parts.copy()
                for i, item in zip(wildcard_indices, combination):
                    expanded_parts[i] = item
                expanded_key = '.'.join(expanded_parts)
                
                # Apply transforms with all combination items
                final_value = self._apply_transforms(value, rule.transforms, combination)
                result[expanded_key] = final_value
        
        return result
    
    def _get_data_items(self, data_source: str) -> List[str]:
        """Get data items for specified source with hierarchical support."""
        if data_source == 'regions':
            return self.hierarchy.regions
        elif data_source == 'prefectures':
            return list(self.hierarchy.prefectures.keys())
        elif data_source == 'cities':
            return list(self.hierarchy.cities.keys())
        elif data_source == 'services':
            return self.hierarchy.services
        elif data_source == 'roles':
            return self.hierarchy.roles
        elif data_source in self.base_compiler.data_sources:
            return self.base_compiler.data_sources[data_source]
        else:
            return []
    
    def _apply_conditions(self, data_items: List[str], conditions: Dict[str, Any]) -> List[str]:
        """Apply filtering conditions to data items."""
        filtered = data_items.copy()
        
        # Include/exclude conditions
        if 'include' in conditions:
            include_patterns = conditions['include']
            if isinstance(include_patterns, str):
                include_patterns = [include_patterns]
            
            filtered = [item for item in filtered 
                       if any(re.match(pattern, item) for pattern in include_patterns)]
        
        if 'exclude' in conditions:
            exclude_patterns = conditions['exclude']
            if isinstance(exclude_patterns, str):
                exclude_patterns = [exclude_patterns]
            
            filtered = [item for item in filtered 
                       if not any(re.match(pattern, item) for pattern in exclude_patterns)]
        
        # Regional conditions
        if 'region' in conditions:
            target_region = conditions['region']
            filtered = [item for item in filtered 
                       if self.hierarchy.prefectures.get(item) == target_region]
        
        return filtered
    
    def _apply_transforms(self, value: Any, transforms: List[str], context: Union[str, Tuple[str, ...]]) -> Any:
        """Apply value transforms based on context."""
        if not transforms:
            return value
        
        result = value
        context_str = context if isinstance(context, str) else str(context)
        
        for transform in transforms:
            if transform == 'scale_by_region':
                # Scale value based on regional importance
                region = self.hierarchy.prefectures.get(context_str, 'other')
                scale_factors = {
                    'kanto': 1.5,    # Tokyo area - high traffic
                    'kansai': 1.3,   # Osaka area - high traffic
                    'chubu': 1.1,    # Nagoya area - medium traffic
                    'kyushu': 0.9,   # Southern Japan - lower traffic
                    'hokkaido': 0.8, # Northern Japan - lower traffic
                    'other': 1.0     # Default
                }
                result = float(result) * scale_factors.get(region, 1.0)
            
            elif transform == 'add_latency_factor':
                # Add latency factor based on distance from Tokyo
                if isinstance(result, (int, float)):
                    latency_factors = {
                        'tokyo': 0.001, 'kanagawa': 0.002, 'saitama': 0.002,
                        'osaka': 0.010, 'kyoto': 0.012,
                        'fukuoka': 0.020, 'okinawa': 0.030,
                        'hokkaido': 0.025
                    }
                    result += latency_factors.get(context_str, 0.015)
        
        return result
    
    def compile_to_static_mapping(self, patterns: Dict[str, Any]) -> Dict[str, Any]:
        """Compile patterns to static mapping for runtime performance."""
        direct_mapping = {}
        component_mapping = {}
        
        for key, value in self.expand_pattern_stream(patterns):
            # All mappings go to component_mapping for now
            # This matches the original config_compiler.py behavior
            # where most patterns become component mappings
            if key in patterns:
                # Original patterns that didn't get expanded (no wildcards) could be direct
                component_mapping[key] = value
            else:
                # Expanded patterns go to component mapping
                component_mapping[key] = value
        
        return {
            "direct_mapping": direct_mapping,
            "component_mapping": component_mapping,
            "metadata": {
                "expansion_rules_count": len(self.expansion_rules),
                "total_patterns": len(direct_mapping) + len(component_mapping),
                "cache_size": len(self._expansion_cache._cache),
                "hierarchy": {
                    "regions": len(self.hierarchy.regions),
                    "prefectures": len(self.hierarchy.prefectures),
                    "cities": len(self.hierarchy.cities),
                    "services": len(self.hierarchy.services),
                    "roles": len(self.hierarchy.roles)
                }
            }
        }
    
    def get_expansion_stats(self) -> Dict[str, Any]:
        """Get expansion statistics for monitoring."""
        return {
            "rules_count": len(self.expansion_rules),
            "cache_size": len(self._expansion_cache._cache),
            "cache_max_size": self._expansion_cache.max_size,
            "hierarchy_stats": {
                "regions": len(self.hierarchy.regions),
                "prefectures": len(self.hierarchy.prefectures),
                "cities": len(self.hierarchy.cities),
                "services": len(self.hierarchy.services),
                "roles": len(self.hierarchy.roles)
            },
            "data_sources": list(self.base_compiler.data_sources.keys())
        }


class StreamingPatternProcessor:
    """Memory-efficient streaming processor for large pattern compilations."""
    
    def __init__(self, expander: EnhancedPatternExpander, max_memory_mb: int = 200):
        self.expander = expander
        self.max_memory_mb = max_memory_mb
        self._current_memory_usage = 0
        self._cache = {}
        
    def process_large_patterns(self, patterns: Dict[str, Any]) -> Iterator[Dict[str, Any]]:
        """Process large pattern sets with memory limits."""
        chunk_size = self._calculate_chunk_size(len(patterns))
        pattern_items = list(patterns.items())
        
        for i in range(0, len(pattern_items), chunk_size):
            chunk = dict(pattern_items[i:i + chunk_size])
            
            # Process chunk
            chunk_result = {}
            for key, value in self.expander.expand_pattern_stream(chunk):
                chunk_result[key] = value
            
            yield chunk_result
            
            # Force garbage collection if needed
            if self._should_cleanup_memory():
                import gc
                gc.collect()
    
    def _calculate_chunk_size(self, total_patterns: int) -> int:
        """Calculate optimal chunk size based on memory constraints."""
        # Estimate memory per pattern (rough heuristic)
        estimated_memory_per_pattern = 1024  # bytes
        max_patterns_in_memory = (self.max_memory_mb * 1024 * 1024) // estimated_memory_per_pattern
        
        return min(max_patterns_in_memory, max(1, total_patterns // 10))
    
    def _should_cleanup_memory(self) -> bool:
        """Check if memory cleanup is needed based on cache size."""
        # Simple cache-based cleanup - no external dependencies needed
        return len(self._cache) > 1000


# Backward compatibility with existing code
PatternExpander = EnhancedPatternExpander
RegionPrefectureResolver = EnhancedPatternExpander