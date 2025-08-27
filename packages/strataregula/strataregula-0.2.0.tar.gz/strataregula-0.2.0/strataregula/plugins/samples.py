"""
Sample Plugin Implementations for Strataregula.

These plugins demonstrate practical usage patterns and serve as templates
for custom plugin development.
"""

import datetime
import os
import re
from typing import Dict, Any
from .base import PatternPlugin, PluginInfo


class TimestampPlugin(PatternPlugin):
    """Plugin that expands @timestamp patterns with current timestamp."""
    
    @property
    def info(self) -> PluginInfo:
        return PluginInfo(
            name="timestamp-plugin",
            version="1.0.0",
            description="Expands @timestamp patterns with configurable formats"
        )
    
    def can_handle(self, pattern: str) -> bool:
        """Handle patterns containing @timestamp."""
        return '@timestamp' in pattern
    
    def expand(self, pattern: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Expand @timestamp with current timestamp."""
        try:
            # Get timestamp format from plugin settings or use default
            plugin_settings = context.get('plugin_settings', {})
            timestamp_format = plugin_settings.get('timestamp_format', '%Y%m%d_%H%M%S')
            timezone = plugin_settings.get('timezone', 'local')
            
            # Generate timestamp
            if timezone.lower() == 'utc':
                current_time = datetime.datetime.utcnow()
            else:
                current_time = datetime.datetime.now()
            
            timestamp_str = current_time.strftime(timestamp_format)
            
            # Replace @timestamp in pattern
            expanded_pattern = pattern.replace('@timestamp', timestamp_str)
            
            return {expanded_pattern: context.get('value')}
            
        except Exception as e:
            # Fallback on error
            fallback_time = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            expanded_pattern = pattern.replace('@timestamp', fallback_time)
            return {expanded_pattern: context.get('value')}


class EnvironmentPlugin(PatternPlugin):
    """Plugin that expands environment variable patterns."""
    
    @property
    def info(self) -> PluginInfo:
        return PluginInfo(
            name="environment-plugin",
            version="1.0.0", 
            description="Expands $ENV_VAR patterns with environment variables"
        )
    
    def can_handle(self, pattern: str) -> bool:
        """Handle patterns starting with $ (environment variables)."""
        return bool(re.search(r'\$[A-Z_][A-Z0-9_]*', pattern))
    
    def expand(self, pattern: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Expand environment variables in pattern."""
        try:
            # Find all environment variable references
            env_vars = re.findall(r'\$([A-Z_][A-Z0-9_]*)', pattern)
            
            expanded_pattern = pattern
            for env_var in env_vars:
                # Get environment variable value
                env_value = os.getenv(env_var)
                
                if env_value is not None:
                    expanded_pattern = expanded_pattern.replace(f'${env_var}', env_value)
                else:
                    # Handle missing environment variables
                    plugin_settings = context.get('plugin_settings', {})
                    default_value = plugin_settings.get('missing_env_default', f'MISSING_{env_var}')
                    expanded_pattern = expanded_pattern.replace(f'${env_var}', default_value)
            
            return {expanded_pattern: context.get('value')}
            
        except Exception as e:
            # Return original pattern on error
            return {pattern: context.get('value')}


class ConditionalPlugin(PatternPlugin):
    """Plugin that handles conditional pattern expansion."""
    
    @property
    def info(self) -> PluginInfo:
        return PluginInfo(
            name="conditional-plugin",
            version="1.0.0",
            description="Expands patterns based on conditions"
        )
    
    def can_handle(self, pattern: str) -> bool:
        """Handle patterns with @if() conditional syntax."""
        return '@if(' in pattern and ')' in pattern
    
    def expand(self, pattern: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Expand conditional patterns."""
        try:
            # Extract condition from @if(condition) syntax
            match = re.search(r'@if\(([^)]+)\)', pattern)
            if not match:
                return {pattern: context.get('value')}
            
            condition = match.group(1)
            
            # Evaluate condition
            if self._evaluate_condition(condition, context):
                # Remove the conditional part and expand
                expanded_pattern = re.sub(r'@if\([^)]+\)', '', pattern)
                return {expanded_pattern.strip(): context.get('value')}
            else:
                # Condition failed, don't expand this pattern
                return {}
                
        except Exception as e:
            # Return original pattern on error
            return {pattern: context.get('value')}
    
    def _evaluate_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """Evaluate a simple condition."""
        try:
            # Simple condition evaluation
            # Supports: env.VAR_NAME, context.key, "literal" == "literal"
            
            if '==' in condition:
                left, right = condition.split('==', 1)
                left = left.strip().strip('"\'')
                right = right.strip().strip('"\'')
                
                # Handle environment variables
                if left.startswith('env.'):
                    env_var = left[4:]  # Remove 'env.' prefix
                    left_value = os.getenv(env_var, '')
                elif left.startswith('context.'):
                    context_key = left[8:]  # Remove 'context.' prefix
                    left_value = context.get(context_key, '')
                else:
                    left_value = left
                
                return str(left_value) == str(right)
            
            # Default to True for simple existence checks
            return True
            
        except Exception:
            return False


class PrefixPlugin(PatternPlugin):
    """Plugin that adds configurable prefixes to patterns."""
    
    @property
    def info(self) -> PluginInfo:
        return PluginInfo(
            name="prefix-plugin",
            version="1.0.0",
            description="Adds configurable prefixes to patterns"
        )
    
    def can_handle(self, pattern: str) -> bool:
        """Handle patterns starting with @prefix:"""
        return pattern.startswith('@prefix:')
    
    def expand(self, pattern: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Add prefix to pattern."""
        try:
            # Remove @prefix: marker
            base_pattern = pattern[8:]  # Remove '@prefix:' (8 chars)
            
            # Get prefix from settings
            plugin_settings = context.get('plugin_settings', {})
            prefix = plugin_settings.get('prefix', 'default')
            
            # Create expanded pattern
            expanded_pattern = f"{prefix}.{base_pattern}"
            
            return {expanded_pattern: context.get('value')}
            
        except Exception as e:
            # Return original without @prefix: marker
            base_pattern = pattern[8:] if pattern.startswith('@prefix:') else pattern
            return {base_pattern: context.get('value')}


class MultiplicatorPlugin(PatternPlugin):
    """Plugin that creates multiple expanded patterns."""
    
    @property
    def info(self) -> PluginInfo:
        return PluginInfo(
            name="multiplicator-plugin", 
            version="1.0.0",
            description="Expands patterns to multiple variations"
        )
    
    def can_handle(self, pattern: str) -> bool:
        """Handle patterns with @multi() syntax."""
        return '@multi(' in pattern and ')' in pattern
    
    def expand(self, pattern: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Expand pattern to multiple variations."""
        try:
            # Extract multiplier list from @multi(item1,item2,item3) syntax
            match = re.search(r'@multi\(([^)]+)\)', pattern)
            if not match:
                return {pattern: context.get('value')}
            
            items_str = match.group(1)
            items = [item.strip() for item in items_str.split(',')]
            
            # Create multiple expanded patterns
            results = {}
            base_pattern = re.sub(r'@multi\([^)]+\)', '{}', pattern)
            
            for item in items:
                expanded_pattern = base_pattern.format(item)
                results[expanded_pattern] = context.get('value')
            
            return results
            
        except Exception as e:
            # Return original pattern on error
            return {pattern: context.get('value')}


class ValidationPlugin(PatternPlugin):
    """Plugin that validates patterns and adds validation metadata."""
    
    @property
    def info(self) -> PluginInfo:
        return PluginInfo(
            name="validation-plugin",
            version="1.0.0",
            description="Validates patterns and adds validation metadata"
        )
    
    def can_handle(self, pattern: str) -> bool:
        """Handle all patterns for validation."""
        # This plugin can validate any pattern, but should have low priority
        return True
    
    def expand(self, pattern: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate pattern and add metadata."""
        try:
            # Perform validation checks
            validation_result = self._validate_pattern(pattern, context)
            
            # Add validation metadata to context
            value = context.get('value')
            if isinstance(value, dict):
                value['_validation'] = validation_result
            else:
                # Wrap simple values with validation info
                value = {
                    'value': value,
                    '_validation': validation_result
                }
            
            return {pattern: value}
            
        except Exception as e:
            # Don't break expansion on validation errors
            return {pattern: context.get('value')}
    
    def _validate_pattern(self, pattern: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform pattern validation checks."""
        validation = {
            'valid': True,
            'warnings': [],
            'timestamp': datetime.datetime.now().isoformat()
        }
        
        # Check for common issues
        if len(pattern) > 200:
            validation['warnings'].append('Pattern is very long (>200 chars)')
        
        if pattern.count('*') > 5:
            validation['warnings'].append('Pattern has many wildcards (>5)')
        
        if not pattern.replace('*', '').replace('.', '').replace('-', '').replace('_', '').isalnum():
            validation['warnings'].append('Pattern contains special characters')
        
        # Mark as invalid if critical issues found
        if len(validation['warnings']) > 3:
            validation['valid'] = False
        
        return validation


# Plugin registration helper
def register_sample_plugins(plugin_manager):
    """Register all sample plugins with a plugin manager."""
    sample_plugins = [
        TimestampPlugin(),
        EnvironmentPlugin(), 
        ConditionalPlugin(),
        PrefixPlugin(),
        MultiplicatorPlugin(),
        ValidationPlugin()
    ]
    
    for plugin in sample_plugins:
        try:
            plugin_manager.load_plugin(plugin.info.name)
            plugin_manager.activate_plugin(plugin.info.name)
        except Exception as e:
            print(f"Failed to register sample plugin {plugin.info.name}: {e}")


# Export sample plugins
__all__ = [
    'TimestampPlugin',
    'EnvironmentPlugin', 
    'ConditionalPlugin',
    'PrefixPlugin',
    'MultiplicatorPlugin',
    'ValidationPlugin',
    'register_sample_plugins'
]