"""
Simple, high-performance YAML configuration compiler.
Extracted from fast_compiler.py and optimizations.py for simplicity.
"""

import yaml
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)


class PatternCache:
    """Simple LRU-style cache for pattern expansion results."""
    
    def __init__(self, max_size: int = 10000):
        self._cache: Dict[str, Any] = {}
        self.max_size = max_size
    
    def get(self, key: str) -> Optional[Any]:
        return self._cache.get(key)
    
    def set(self, key: str, value: Any) -> None:
        if len(self._cache) >= self.max_size:
            # Clear half the cache when full
            items = list(self._cache.items())
            self._cache = dict(items[len(items)//2:])
        self._cache[key] = value
    
    def clear(self) -> None:
        self._cache.clear()


class PatternCompiler:
    """High-performance pattern compiler with caching."""
    
    def __init__(self):
        self.data_sources: Dict[str, List[str]] = {}
        self.pattern_rules: Dict[str, Any] = {}
        self._pattern_cache = PatternCache()
        self._split_cache = PatternCache(max_size=5000)
    
    def load_config(self, config_path: Path) -> None:
        """Load YAML configuration file."""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            if not isinstance(config, dict):
                raise ValueError("Configuration must be a dictionary")
            
            self.data_sources = config.get('data_sources', {})
            self.pattern_rules = config.get('pattern_rules', {})
            
            # Basic validation
            if not self.data_sources:
                logger.warning("No data sources found in configuration")
            if not self.pattern_rules:
                logger.warning("No pattern rules found in configuration")
                
        except Exception as e:
            raise ValueError(f"Failed to load configuration: {e}")
    
    def set_data_sources(self, data_sources: Dict[str, List[str]]) -> None:
        """Set data sources programmatically."""
        self.data_sources = data_sources.copy()
        self._pattern_cache.clear()
    
    def set_pattern_rules(self, pattern_rules: Dict[str, Any]) -> None:
        """Set pattern rules programmatically."""
        self.pattern_rules = pattern_rules.copy()
        self._pattern_cache.clear()
    
    def compile_patterns(self, patterns: Dict[str, Any]) -> Dict[str, Any]:
        """Compile patterns into expanded mappings."""
        result = {}
        
        for pattern, value in patterns.items():
            # Check cache first
            cache_key = f"{pattern}:{hash(str(value))}"
            cached_result = self._pattern_cache.get(cache_key)
            
            if cached_result is not None:
                result.update(cached_result)
                continue
            
            # Expand pattern
            expanded = self._expand_pattern(pattern, value)
            result.update(expanded)
            
            # Cache result
            self._pattern_cache.set(cache_key, expanded)
        
        return result
    
    def _expand_pattern(self, pattern: str, value: Any) -> Dict[str, Any]:
        """Expand a single pattern with wildcards."""
        if '*' not in pattern:
            return {pattern: value}
        
        # Get pattern rule if it exists
        rule = self._find_matching_rule(pattern)
        if not rule:
            logger.debug(f"No expansion rule found for pattern: {pattern}")
            return {pattern: value}  # No expansion
        
        # Get data source
        data_source_name = rule.get('data_source')
        if not data_source_name or data_source_name not in self.data_sources:
            logger.warning(f"Data source '{data_source_name}' not found for pattern '{pattern}'")
            return {pattern: value}
        
        data_items = self.data_sources[data_source_name]
        template = rule.get('template', pattern)
        
        return self._expand_with_template(pattern, template, data_items, value)
    
    def _find_matching_rule(self, pattern: str) -> Optional[Dict[str, Any]]:
        """Find the best matching rule for a pattern."""
        # Exact match first
        if pattern in self.pattern_rules:
            return self.pattern_rules[pattern]
        
        # Pattern matching
        for rule_pattern, rule in self.pattern_rules.items():
            if self._patterns_match(pattern, rule_pattern):
                return rule
        
        return None
    
    def _patterns_match(self, pattern: str, rule_pattern: str) -> bool:
        """Check if pattern matches rule pattern."""
        if pattern == rule_pattern:
            return True
        
        # Convert wildcard pattern to regex
        regex_pattern = rule_pattern.replace('.', r'\.').replace('*', r'.*')
        regex_pattern = f"^{regex_pattern}$"
        
        try:
            return bool(re.match(regex_pattern, pattern))
        except re.error as e:
            logger.warning(f"Invalid regex pattern '{regex_pattern}' for rule pattern '{rule_pattern}': {e}")
            return False
    
    def _expand_with_template(self, pattern: str, template: str, data_items: List[str], value: Any) -> Dict[str, Any]:
        """Expand pattern using template and data items."""
        result = {}
        
        # Parse pattern to find wildcard positions
        pattern_parts = pattern.split('.')
        template_parts = template.split('.')
        
        # Find wildcard indices
        wildcard_indices = []
        for i, part in enumerate(pattern_parts):
            if part == '*':
                wildcard_indices.append(i)
        
        if not wildcard_indices:
            return {pattern: value}
        
        # Generate combinations for multi-wildcard patterns
        if len(wildcard_indices) == 1:
            # Single wildcard - simple case
            wildcard_idx = wildcard_indices[0]
            for item in data_items:
                expanded_parts = pattern_parts.copy()
                expanded_parts[wildcard_idx] = item
                expanded_key = '.'.join(expanded_parts)
                result[expanded_key] = value
        else:
            # Multiple wildcards - generate all combinations
            import itertools
            for combination in itertools.product(data_items, repeat=len(wildcard_indices)):
                expanded_parts = pattern_parts.copy()
                for i, item in zip(wildcard_indices, combination):
                    expanded_parts[i] = item
                expanded_key = '.'.join(expanded_parts)
                result[expanded_key] = value
        
        return result
    
    @lru_cache(maxsize=1000)
    def _split_pattern_cached(self, pattern: str) -> Tuple[str, ...]:
        """Cached pattern splitting."""
        return tuple(pattern.split('.'))
