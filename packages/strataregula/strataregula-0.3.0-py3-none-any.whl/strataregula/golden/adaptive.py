"""
Adaptive Threshold Calculator for StrataRegula Golden Metrics v0.4.0+

This module provides intelligent threshold calculation based on historical data,
replacing fixed thresholds with statistically-derived bounds.

Features:
- Multiple threshold calculation strategies
- Trend-aware threshold adjustment
- Confidence interval-based bounds
- Anomaly detection and filtering
- Configurable sensitivity levels
"""

import logging
import math
import statistics
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path

from .history import HistoryManager, StatisticalAnalyzer

logger = logging.getLogger(__name__)


class ThresholdStrategy(Enum):
    """Available threshold calculation strategies."""
    CONFIDENCE_INTERVAL = "confidence_interval"  # Statistical CI bounds
    PERCENTILE = "percentile"                    # Percentile-based bounds
    MOVING_AVERAGE = "moving_average"            # Moving average ± std dev
    TREND_ADJUSTED = "trend_adjusted"            # Trend-aware thresholds


class SensitivityLevel(Enum):
    """Threshold sensitivity levels."""
    STRICT = "strict"        # Low tolerance (99% confidence)
    NORMAL = "normal"        # Medium tolerance (95% confidence) 
    RELAXED = "relaxed"      # High tolerance (90% confidence)


@dataclass
class AdaptiveThreshold:
    """Calculated adaptive threshold with metadata."""
    metric_name: str
    threshold_value: float
    strategy: ThresholdStrategy
    confidence_level: float
    samples_used: int
    trend_info: Dict[str, Any]
    calculation_metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        result = asdict(self)
        result['strategy'] = self.strategy.value
        return result


class AdaptiveThresholdCalculator:
    """Calculates adaptive thresholds based on historical metrics."""
    
    def __init__(self, 
                 history_manager: HistoryManager,
                 default_window_size: int = 20,
                 min_samples_required: int = 5):
        """Initialize calculator.
        
        Args:
            history_manager: History manager instance
            default_window_size: Default number of samples for analysis
            min_samples_required: Minimum samples needed for calculation
        """
        self.history = history_manager
        self.analyzer = StatisticalAnalyzer(history_manager)
        self.default_window_size = default_window_size
        self.min_samples_required = min_samples_required
    
    def calculate_threshold(self,
                          metric_name: str,
                          threshold_type: str,  # 'upper' or 'lower'
                          strategy: ThresholdStrategy = ThresholdStrategy.CONFIDENCE_INTERVAL,
                          sensitivity: SensitivityLevel = SensitivityLevel.NORMAL,
                          window_size: Optional[int] = None) -> Optional[AdaptiveThreshold]:
        """Calculate adaptive threshold for a metric.
        
        Args:
            metric_name: Name of metric
            threshold_type: 'upper' for regression detection, 'lower' for minimum bounds
            strategy: Calculation strategy to use
            sensitivity: Sensitivity level
            window_size: Number of samples to analyze
            
        Returns:
            Calculated threshold or None if insufficient data
        """
        window_size = window_size or self.default_window_size
        
        # Get historical data
        values = self.history.get_metric_series(metric_name, window_size)
        
        if len(values) < self.min_samples_required:
            logger.warning(f"Insufficient data for {metric_name}: {len(values)} < {self.min_samples_required}")
            return None
        
        # Get confidence level from sensitivity
        confidence_levels = {
            SensitivityLevel.STRICT: 0.99,
            SensitivityLevel.NORMAL: 0.95,
            SensitivityLevel.RELAXED: 0.90
        }
        confidence = confidence_levels[sensitivity]
        
        # Calculate threshold using selected strategy
        threshold_value = None
        calculation_metadata = {}
        
        if strategy == ThresholdStrategy.CONFIDENCE_INTERVAL:
            threshold_value, calculation_metadata = self._calculate_ci_threshold(
                values, threshold_type, confidence
            )
        elif strategy == ThresholdStrategy.PERCENTILE:
            threshold_value, calculation_metadata = self._calculate_percentile_threshold(
                values, threshold_type, sensitivity
            )
        elif strategy == ThresholdStrategy.MOVING_AVERAGE:
            threshold_value, calculation_metadata = self._calculate_ma_threshold(
                values, threshold_type, confidence
            )
        elif strategy == ThresholdStrategy.TREND_ADJUSTED:
            threshold_value, calculation_metadata = self._calculate_trend_adjusted_threshold(
                metric_name, values, threshold_type, confidence, window_size
            )
        else:
            raise ValueError(f"Unknown strategy: {strategy}")
        
        if threshold_value is None:
            return None
        
        # Get trend analysis
        trend_info = self.analyzer.get_trend_analysis(metric_name, window_size)
        
        return AdaptiveThreshold(
            metric_name=metric_name,
            threshold_value=threshold_value,
            strategy=strategy,
            confidence_level=confidence,
            samples_used=len(values),
            trend_info=trend_info,
            calculation_metadata=calculation_metadata
        )
    
    def _calculate_ci_threshold(self, 
                              values: List[float],
                              threshold_type: str,
                              confidence: float) -> Tuple[Optional[float], Dict[str, Any]]:
        """Calculate threshold using confidence interval."""
        # Remove outliers
        clean_values = self.analyzer._remove_outliers(values)
        
        if len(clean_values) < 2:
            return None, {"error": "insufficient_clean_data"}
        
        lower_bound, upper_bound = self.analyzer.calculate_confidence_interval(
            clean_values, confidence
        )
        
        threshold_value = upper_bound if threshold_type == 'upper' else lower_bound
        
        metadata = {
            "mean": statistics.mean(clean_values),
            "std_dev": statistics.stdev(clean_values) if len(clean_values) > 1 else 0,
            "lower_bound": lower_bound,
            "upper_bound": upper_bound,
            "outliers_removed": len(values) - len(clean_values)
        }
        
        return threshold_value, metadata
    
    def _calculate_percentile_threshold(self,
                                     values: List[float],
                                     threshold_type: str,
                                     sensitivity: SensitivityLevel) -> Tuple[Optional[float], Dict[str, Any]]:
        """Calculate threshold using percentiles."""
        # Remove outliers first
        clean_values = self.analyzer._remove_outliers(values)
        
        if len(clean_values) < 2:
            return None, {"error": "insufficient_clean_data"}
        
        # Select percentile based on sensitivity and threshold type
        if threshold_type == 'upper':
            percentiles = {
                SensitivityLevel.STRICT: 95,    # Very strict upper bound
                SensitivityLevel.NORMAL: 90,    # Normal upper bound
                SensitivityLevel.RELAXED: 85    # Relaxed upper bound
            }
        else:  # 'lower'
            percentiles = {
                SensitivityLevel.STRICT: 5,     # Very strict lower bound
                SensitivityLevel.NORMAL: 10,    # Normal lower bound
                SensitivityLevel.RELAXED: 15    # Relaxed lower bound
            }
        
        percentile = percentiles[sensitivity]
        threshold_value = statistics.quantiles(clean_values, n=100, method='inclusive')[percentile-1]
        
        metadata = {
            "percentile_used": percentile,
            "median": statistics.median(clean_values),
            "min_value": min(clean_values),
            "max_value": max(clean_values),
            "outliers_removed": len(values) - len(clean_values)
        }
        
        return threshold_value, metadata
    
    def _calculate_ma_threshold(self,
                              values: List[float],
                              threshold_type: str,
                              confidence: float) -> Tuple[Optional[float], Dict[str, Any]]:
        """Calculate threshold using moving average ± standard deviation."""
        if len(values) < 3:
            return None, {"error": "insufficient_data_for_ma"}
        
        # Calculate moving average (use all values as single window)
        ma = statistics.mean(values)
        std_dev = statistics.stdev(values)
        
        # Z-score for confidence level
        z_scores = {0.90: 1.645, 0.95: 1.96, 0.99: 2.576}
        z_score = z_scores.get(confidence, 1.96)
        
        if threshold_type == 'upper':
            threshold_value = ma + (z_score * std_dev)
        else:
            threshold_value = ma - (z_score * std_dev)
        
        metadata = {
            "moving_average": ma,
            "standard_deviation": std_dev,
            "z_score_used": z_score,
            "confidence_level": confidence
        }
        
        return threshold_value, metadata
    
    def _calculate_trend_adjusted_threshold(self,
                                          metric_name: str,
                                          values: List[float],
                                          threshold_type: str,
                                          confidence: float,
                                          window_size: int) -> Tuple[Optional[float], Dict[str, Any]]:
        """Calculate threshold adjusted for detected trends."""
        # First get base threshold using confidence interval
        base_threshold, base_metadata = self._calculate_ci_threshold(
            values, threshold_type, confidence
        )
        
        if base_threshold is None:
            return None, base_metadata
        
        # Get trend analysis
        trend_info = self.analyzer.get_trend_analysis(metric_name, window_size)
        
        # Adjust threshold based on trend
        adjustment_factor = 1.0
        
        if trend_info["trend"] == "increasing" and threshold_type == "upper":
            # If metric is trending up, be more lenient on upper bounds
            if trend_info["confidence"] == "high":
                adjustment_factor = 1.1  # 10% more lenient
            elif trend_info["confidence"] == "medium":
                adjustment_factor = 1.05  # 5% more lenient
        elif trend_info["trend"] == "decreasing" and threshold_type == "lower":
            # If metric is trending down, be more lenient on lower bounds  
            if trend_info["confidence"] == "high":
                adjustment_factor = 0.9  # 10% more lenient
            elif trend_info["confidence"] == "medium":
                adjustment_factor = 0.95  # 5% more lenient
        
        adjusted_threshold = base_threshold * adjustment_factor
        
        metadata = {
            **base_metadata,
            "base_threshold": base_threshold,
            "trend_adjustment_factor": adjustment_factor,
            "trend_direction": trend_info["trend"],
            "trend_confidence": trend_info["confidence"],
            "trend_slope": trend_info["slope"]
        }
        
        return adjusted_threshold, metadata
    
    def calculate_all_thresholds(self,
                               metric_configs: Dict[str, Dict[str, Any]],
                               sensitivity: SensitivityLevel = SensitivityLevel.NORMAL) -> Dict[str, AdaptiveThreshold]:
        """Calculate adaptive thresholds for multiple metrics.
        
        Args:
            metric_configs: Dict mapping metric names to config dicts containing
                          'threshold_type', 'strategy', etc.
            sensitivity: Default sensitivity level
            
        Returns:
            Dict mapping metric names to calculated thresholds
        """
        thresholds = {}
        
        for metric_name, config in metric_configs.items():
            threshold_type = config.get('threshold_type', 'upper')
            strategy = ThresholdStrategy(config.get('strategy', 'confidence_interval'))
            metric_sensitivity = SensitivityLevel(config.get('sensitivity', sensitivity.value))
            window_size = config.get('window_size')
            
            threshold = self.calculate_threshold(
                metric_name=metric_name,
                threshold_type=threshold_type,
                strategy=strategy,
                sensitivity=metric_sensitivity,
                window_size=window_size
            )
            
            if threshold:
                thresholds[metric_name] = threshold
            else:
                logger.warning(f"Could not calculate adaptive threshold for {metric_name}")
        
        return thresholds
    
    def export_thresholds(self, 
                         thresholds: Dict[str, AdaptiveThreshold],
                         output_path: Path) -> None:
        """Export calculated thresholds to JSON file.
        
        Args:
            thresholds: Calculated thresholds
            output_path: Path to save thresholds
        """
        import json
        from datetime import datetime, timezone
        
        export_data = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "version": "0.4.0",
            "thresholds": {
                name: threshold.to_dict() 
                for name, threshold in thresholds.items()
            }
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2)
        
        logger.info(f"Exported {len(thresholds)} adaptive thresholds to {output_path}")


# Integration helpers
def create_adaptive_calculator(reports_dir: Path) -> AdaptiveThresholdCalculator:
    """Create adaptive threshold calculator for reports directory.
    
    Args:
        reports_dir: Reports directory path
        
    Returns:
        Configured calculator instance
    """
    from .history import initialize_history
    
    history = initialize_history(reports_dir)
    return AdaptiveThresholdCalculator(history)


def calculate_adaptive_thresholds_for_config(reports_dir: Path,
                                           config: Dict[str, Any]) -> Dict[str, AdaptiveThreshold]:
    """Calculate adaptive thresholds using pyproject.toml config.
    
    Args:
        reports_dir: Reports directory path
        config: Golden metrics configuration from pyproject.toml
        
    Returns:
        Calculated adaptive thresholds
    """
    calculator = create_adaptive_calculator(reports_dir)
    
    # Extract metric configurations from pyproject.toml format
    sensitivity_str = config.get('sensitivity', 'normal')
    sensitivity = SensitivityLevel(sensitivity_str)
    
    # Define metric configurations based on standard golden metrics
    metric_configs = {
        'latency_ms': {
            'threshold_type': 'upper',
            'strategy': 'trend_adjusted'
        },
        'throughput_rps': {
            'threshold_type': 'lower', 
            'strategy': 'confidence_interval'
        },
        'error_rate': {
            'threshold_type': 'upper',
            'strategy': 'percentile'
        },
        'memory_bytes': {
            'threshold_type': 'upper',
            'strategy': 'moving_average'
        },
        'hit_ratio': {
            'threshold_type': 'lower',
            'strategy': 'confidence_interval'
        }
    }
    
    return calculator.calculate_all_thresholds(metric_configs, sensitivity)