"""
Plugin Error Handling and Fallback Mechanisms.
"""

import logging
import time
import traceback
from typing import Dict, Any, List, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import asyncio
from contextlib import contextmanager
import threading

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories for classification."""
    LOAD_ERROR = "load_error"
    RUNTIME_ERROR = "runtime_error"
    TIMEOUT_ERROR = "timeout_error"
    DEPENDENCY_ERROR = "dependency_error"
    VALIDATION_ERROR = "validation_error"
    PERMISSION_ERROR = "permission_error"
    NETWORK_ERROR = "network_error"
    RESOURCE_ERROR = "resource_error"


@dataclass
class PluginError:
    """Represents a plugin error."""
    plugin_name: str
    category: ErrorCategory
    severity: ErrorSeverity
    message: str
    exception: Optional[Exception] = None
    timestamp: float = field(default_factory=time.time)
    context: Dict[str, Any] = field(default_factory=dict)
    stack_trace: Optional[str] = None
    
    def __post_init__(self):
        if self.exception and self.stack_trace is None:
            self.stack_trace = traceback.format_exception(
                type(self.exception), self.exception, self.exception.__traceback__
            )


class ErrorRecoveryStrategy:
    """Base class for error recovery strategies."""
    
    def __init__(self, max_retries: int = 3, backoff_factor: float = 2.0):
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.retry_counts: Dict[str, int] = {}
        self.last_attempt: Dict[str, float] = {}
    
    def should_retry(self, plugin_name: str, error: PluginError) -> bool:
        """Determine if operation should be retried."""
        current_retries = self.retry_counts.get(plugin_name, 0)
        
        # Check retry limit
        if current_retries >= self.max_retries:
            return False
        
        # Check error severity (don't retry critical errors)
        if error.severity == ErrorSeverity.CRITICAL:
            return False
        
        # Check cooldown period
        last_attempt = self.last_attempt.get(plugin_name, 0)
        cooldown_period = self.backoff_factor ** current_retries
        if time.time() - last_attempt < cooldown_period:
            return False
        
        return True
    
    def record_attempt(self, plugin_name: str) -> None:
        """Record a retry attempt."""
        self.retry_counts[plugin_name] = self.retry_counts.get(plugin_name, 0) + 1
        self.last_attempt[plugin_name] = time.time()
    
    def reset_attempts(self, plugin_name: str) -> None:
        """Reset retry attempts after successful operation."""
        self.retry_counts.pop(plugin_name, None)
        self.last_attempt.pop(plugin_name, None)


class CircuitBreaker:
    """Circuit breaker pattern implementation for plugins."""
    
    def __init__(self, failure_threshold: int = 5, timeout: float = 60.0):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_counts: Dict[str, int] = {}
        self.last_failure: Dict[str, float] = {}
        self.states: Dict[str, str] = {}  # closed, open, half-open
        self._lock = threading.Lock()
    
    def is_open(self, plugin_name: str) -> bool:
        """Check if circuit breaker is open for a plugin."""
        with self._lock:
            state = self.states.get(plugin_name, 'closed')
            
            if state == 'open':
                # Check if timeout has passed
                last_failure = self.last_failure.get(plugin_name, 0)
                if time.time() - last_failure >= self.timeout:
                    self.states[plugin_name] = 'half-open'
                    return False
                return True
            
            return False
    
    def record_success(self, plugin_name: str) -> None:
        """Record successful operation."""
        with self._lock:
            self.failure_counts[plugin_name] = 0
            self.states[plugin_name] = 'closed'
    
    def record_failure(self, plugin_name: str) -> None:
        """Record failed operation."""
        with self._lock:
            count = self.failure_counts.get(plugin_name, 0) + 1
            self.failure_counts[plugin_name] = count
            self.last_failure[plugin_name] = time.time()
            
            if count >= self.failure_threshold:
                self.states[plugin_name] = 'open'
                logger.warning(f"Circuit breaker opened for plugin: {plugin_name}")


class FallbackHandler:
    """Handles fallback mechanisms for plugin operations."""
    
    def __init__(self):
        self.fallback_strategies: Dict[str, List[Callable]] = {}
        self.default_fallbacks: List[Callable] = []
    
    def register_fallback(self, plugin_name: str, fallback_func: Callable) -> None:
        """Register a fallback function for a specific plugin."""
        if plugin_name not in self.fallback_strategies:
            self.fallback_strategies[plugin_name] = []
        self.fallback_strategies[plugin_name].append(fallback_func)
    
    def register_default_fallback(self, fallback_func: Callable) -> None:
        """Register a default fallback function."""
        self.default_fallbacks.append(fallback_func)
    
    def execute_fallback(self, plugin_name: str, pattern: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute fallback for a failed plugin operation."""
        # Try plugin-specific fallbacks first
        fallbacks = self.fallback_strategies.get(plugin_name, [])
        fallbacks.extend(self.default_fallbacks)
        
        for fallback_func in fallbacks:
            try:
                result = fallback_func(pattern, context, plugin_name)
                if result is not None:
                    logger.info(f"Fallback successful for plugin {plugin_name}")
                    return result
            except Exception as e:
                logger.warning(f"Fallback function failed: {e}")
        
        # Ultimate fallback - basic pattern expansion
        return {pattern: context.get('value', None)}


class PluginErrorHandler:
    """Comprehensive plugin error handling system."""
    
    def __init__(self):
        self.recovery_strategy = ErrorRecoveryStrategy()
        self.circuit_breaker = CircuitBreaker()
        self.fallback_handler = FallbackHandler()
        self.error_history: List[PluginError] = []
        self.error_callbacks: Dict[ErrorCategory, List[Callable]] = {
            category: [] for category in ErrorCategory
        }
        self._lock = threading.Lock()
    
    def handle_error(self, error: PluginError) -> Dict[str, Any]:
        """Handle a plugin error and return appropriate response."""
        with self._lock:
            # Record error in history
            self.error_history.append(error)
            
            # Limit history size
            if len(self.error_history) > 1000:
                self.error_history = self.error_history[-500:]
            
            # Update circuit breaker
            self.circuit_breaker.record_failure(error.plugin_name)
            
            # Execute error callbacks
            self._execute_error_callbacks(error)
            
            # Log error appropriately
            self._log_error(error)
            
            # Determine response strategy
            return self._determine_response(error)
    
    def handle_success(self, plugin_name: str) -> None:
        """Handle successful plugin operation."""
        self.recovery_strategy.reset_attempts(plugin_name)
        self.circuit_breaker.record_success(plugin_name)
    
    def should_attempt_operation(self, plugin_name: str) -> bool:
        """Check if operation should be attempted for a plugin."""
        return not self.circuit_breaker.is_open(plugin_name)
    
    def can_retry_operation(self, plugin_name: str, error: PluginError) -> bool:
        """Check if operation can be retried."""
        return self.recovery_strategy.should_retry(plugin_name, error)
    
    @contextmanager
    def error_context(self, plugin_name: str, operation: str, context: Optional[Dict[str, Any]] = None):
        """Context manager for plugin operations with error handling."""
        start_time = time.time()
        operation_context = context or {}
        
        try:
            yield
            # Success - record it
            self.handle_success(plugin_name)
            
        except Exception as e:
            # Categorize the error
            category = self._categorize_exception(e)
            severity = self._determine_severity(e, category)
            
            error = PluginError(
                plugin_name=plugin_name,
                category=category,
                severity=severity,
                message=f"Error in {operation}: {str(e)}",
                exception=e,
                context={
                    'operation': operation,
                    'duration': time.time() - start_time,
                    **operation_context
                }
            )
            
            # Handle the error
            self.handle_error(error)
            raise
    
    def register_error_callback(self, category: ErrorCategory, callback: Callable[[PluginError], None]) -> None:
        """Register callback for specific error categories."""
        self.error_callbacks[category].append(callback)
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics."""
        with self._lock:
            if not self.error_history:
                return {"total_errors": 0}
            
            # Count by plugin
            plugin_errors = {}
            category_counts = {}
            severity_counts = {}
            
            for error in self.error_history:
                # Plugin counts
                plugin_errors[error.plugin_name] = plugin_errors.get(error.plugin_name, 0) + 1
                
                # Category counts
                category_counts[error.category.value] = category_counts.get(error.category.value, 0) + 1
                
                # Severity counts
                severity_counts[error.severity.value] = severity_counts.get(error.severity.value, 0) + 1
            
            return {
                "total_errors": len(self.error_history),
                "by_plugin": plugin_errors,
                "by_category": category_counts,
                "by_severity": severity_counts,
                "circuit_breaker_states": dict(self.circuit_breaker.states),
                "retry_counts": dict(self.recovery_strategy.retry_counts)
            }
    
    def get_recent_errors(self, count: int = 10) -> List[PluginError]:
        """Get most recent errors."""
        with self._lock:
            return self.error_history[-count:]
    
    def clear_error_history(self) -> None:
        """Clear error history."""
        with self._lock:
            self.error_history.clear()
            logger.info("Plugin error history cleared")
    
    def _categorize_exception(self, exception: Exception) -> ErrorCategory:
        """Categorize exception by type."""
        if isinstance(exception, ImportError):
            return ErrorCategory.LOAD_ERROR
        elif isinstance(exception, PermissionError):
            return ErrorCategory.PERMISSION_ERROR
        elif isinstance(exception, TimeoutError):
            return ErrorCategory.TIMEOUT_ERROR
        elif isinstance(exception, (ConnectionError, OSError)):
            return ErrorCategory.NETWORK_ERROR
        elif isinstance(exception, (MemoryError, OSError)):
            return ErrorCategory.RESOURCE_ERROR
        elif isinstance(exception, (ValueError, TypeError)):
            return ErrorCategory.VALIDATION_ERROR
        else:
            return ErrorCategory.RUNTIME_ERROR
    
    def _determine_severity(self, exception: Exception, category: ErrorCategory) -> ErrorSeverity:
        """Determine error severity."""
        # Critical errors
        if isinstance(exception, (MemoryError, SystemExit)):
            return ErrorSeverity.CRITICAL
        
        # High severity errors
        if category in [ErrorCategory.LOAD_ERROR, ErrorCategory.DEPENDENCY_ERROR]:
            return ErrorSeverity.HIGH
        
        # Medium severity errors
        if category in [ErrorCategory.TIMEOUT_ERROR, ErrorCategory.NETWORK_ERROR]:
            return ErrorSeverity.MEDIUM
        
        # Default to low severity
        return ErrorSeverity.LOW
    
    def _execute_error_callbacks(self, error: PluginError) -> None:
        """Execute registered error callbacks."""
        callbacks = self.error_callbacks.get(error.category, [])
        
        for callback in callbacks:
            try:
                callback(error)
            except Exception as e:
                logger.error(f"Error in error callback: {e}")
    
    def _log_error(self, error: PluginError) -> None:
        """Log error with appropriate level."""
        log_msg = f"Plugin {error.plugin_name} - {error.category.value}: {error.message}"
        
        if error.severity == ErrorSeverity.CRITICAL:
            logger.critical(log_msg)
        elif error.severity == ErrorSeverity.HIGH:
            logger.error(log_msg)
        elif error.severity == ErrorSeverity.MEDIUM:
            logger.warning(log_msg)
        else:
            logger.info(log_msg)
        
        # Log stack trace for high/critical errors
        if error.severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL] and error.stack_trace:
            logger.debug(f"Stack trace for {error.plugin_name}: {''.join(error.stack_trace)}")
    
    def _determine_response(self, error: PluginError) -> Dict[str, Any]:
        """Determine appropriate response to error."""
        response = {
            'error': True,
            'plugin_name': error.plugin_name,
            'category': error.category.value,
            'severity': error.severity.value,
            'message': error.message,
            'timestamp': error.timestamp
        }
        
        # Add retry information
        if self.can_retry_operation(error.plugin_name, error):
            response['can_retry'] = True
            response['retry_count'] = self.recovery_strategy.retry_counts.get(error.plugin_name, 0)
        else:
            response['can_retry'] = False
        
        # Add circuit breaker status
        response['circuit_open'] = self.circuit_breaker.is_open(error.plugin_name)
        
        return response


# Default fallback functions
def basic_pattern_fallback(pattern: str, context: Dict[str, Any], plugin_name: str) -> Dict[str, Any]:
    """Basic fallback that returns pattern with value."""
    logger.info(f"Using basic fallback for pattern '{pattern}' (failed plugin: {plugin_name})")
    return {pattern: context.get('value', None)}


def hierarchical_fallback(pattern: str, context: Dict[str, Any], plugin_name: str) -> Dict[str, Any]:
    """Fallback that attempts simple hierarchical expansion."""
    logger.info(f"Using hierarchical fallback for pattern '{pattern}' (failed plugin: {plugin_name})")
    
    result = {}
    if '*' in pattern and 'value' in context:
        # Simple wildcard expansion
        base_pattern = pattern.replace('*', '')
        if 'data_sources' in context:
            for key in context['data_sources']:
                result[f"{base_pattern}{key}"] = context['value']
        else:
            result[pattern.replace('*', 'default')] = context['value']
    else:
        result[pattern] = context.get('value', None)
    
    return result