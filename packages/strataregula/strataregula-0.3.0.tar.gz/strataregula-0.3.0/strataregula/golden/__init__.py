"""
Golden Metrics Guard System for StrataRegula

This package provides performance regression detection through:
- Historical metrics collection and analysis
- Fixed and adaptive threshold calculation
- CI/CD integration for automated quality gates
- Trend analysis and anomaly detection

Usage:
    # Fixed threshold mode (v0.3.0)
    from strataregula.golden.history import collect_and_store_metrics
    collect_and_store_metrics(reports_dir, current_metrics)
    
    # Adaptive threshold mode (v0.4.0+)  
    from strataregula.golden.adaptive import calculate_adaptive_thresholds_for_config
    thresholds = calculate_adaptive_thresholds_for_config(reports_dir, config)
"""

from .history import (
    HistoryManager,
    MetricsSnapshot,
    StatisticalAnalyzer,
    initialize_history,
    collect_and_store_metrics
)

from .adaptive import (
    AdaptiveThresholdCalculator,
    AdaptiveThreshold,
    ThresholdStrategy,
    SensitivityLevel,
    create_adaptive_calculator,
    calculate_adaptive_thresholds_for_config
)

__all__ = [
    # History management
    'HistoryManager',
    'MetricsSnapshot', 
    'StatisticalAnalyzer',
    'initialize_history',
    'collect_and_store_metrics',
    
    # Adaptive thresholds
    'AdaptiveThresholdCalculator',
    'AdaptiveThreshold',
    'ThresholdStrategy', 
    'SensitivityLevel',
    'create_adaptive_calculator',
    'calculate_adaptive_thresholds_for_config',
]

# Version info
__version__ = "0.4.0"
GOLDEN_METRICS_VERSION = "2.0.0"  # Internal version for compatibility