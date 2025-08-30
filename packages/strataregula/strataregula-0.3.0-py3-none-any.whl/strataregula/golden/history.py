"""
Golden Metrics History Management for StrataRegula v0.4.0+

This module handles collection, storage, and analysis of historical
performance metrics for adaptive threshold calculation.

Features:
- JSONL-based metrics storage for efficiency
- Statistical analysis of historical data
- Trend detection and anomaly filtering
- Configurable retention and window sizes
"""

import json
import math
import statistics
from dataclasses import dataclass, asdict
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Iterator
import logging

logger = logging.getLogger(__name__)


@dataclass
class MetricsSnapshot:
    """Single metrics snapshot with metadata."""
    timestamp: str
    version: str
    commit_hash: Optional[str]
    branch: str
    metrics: Dict[str, float]
    environment: Dict[str, str]
    
    @classmethod
    def create(cls, metrics: Dict[str, float], 
               version: str = "0.3.0",
               branch: str = "main") -> "MetricsSnapshot":
        """Create new snapshot with current timestamp."""
        import subprocess
        
        # Try to get git commit hash
        commit_hash = None
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"], 
                capture_output=True, text=True, check=True
            )
            commit_hash = result.stdout.strip()[:8]
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
        
        return cls(
            timestamp=datetime.now(timezone.utc).isoformat(),
            version=version,
            commit_hash=commit_hash,
            branch=branch,
            metrics=metrics,
            environment={
                "python_version": f"{__import__('sys').version_info.major}.{__import__('sys').version_info.minor}",
                "platform": __import__('platform').system(),
            }
        )
    
    def to_jsonl(self) -> str:
        """Convert to JSONL format."""
        return json.dumps(asdict(self), separators=(',', ':'))
    
    @classmethod
    def from_jsonl(cls, line: str) -> "MetricsSnapshot":
        """Create from JSONL line."""
        data = json.loads(line)
        return cls(**data)


class HistoryManager:
    """Manages collection and analysis of historical metrics."""
    
    def __init__(self, history_dir: Path):
        """Initialize history manager.
        
        Args:
            history_dir: Directory to store history files
        """
        self.history_dir = Path(history_dir)
        self.history_file = self.history_dir / "metrics.jsonl"
        self.history_dir.mkdir(parents=True, exist_ok=True)
    
    def append(self, snapshot: MetricsSnapshot) -> None:
        """Append metrics snapshot to history."""
        with open(self.history_file, "a", encoding="utf-8") as f:
            f.write(snapshot.to_jsonl() + "\n")
        
        logger.debug(f"Appended metrics snapshot: {snapshot.timestamp}")
    
    def collect_current_and_append(self, metrics: Dict[str, float]) -> MetricsSnapshot:
        """Collect current metrics and append to history.
        
        Args:
            metrics: Current metrics to record
            
        Returns:
            Created snapshot
        """
        snapshot = MetricsSnapshot.create(metrics)
        self.append(snapshot)
        return snapshot
    
    def load_history(self, limit: Optional[int] = None) -> List[MetricsSnapshot]:
        """Load historical snapshots.
        
        Args:
            limit: Maximum number of recent snapshots to load
            
        Returns:
            List of snapshots, most recent first
        """
        if not self.history_file.exists():
            return []
        
        snapshots = []
        with open(self.history_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        snapshots.append(MetricsSnapshot.from_jsonl(line))
                    except json.JSONDecodeError as e:
                        logger.warning(f"Skipped invalid JSONL line: {e}")
        
        # Return most recent first
        snapshots.reverse()
        
        if limit:
            snapshots = snapshots[:limit]
        
        return snapshots
    
    def get_metric_series(self, metric_name: str, window_size: int = 10) -> List[float]:
        """Get time series data for a specific metric.
        
        Args:
            metric_name: Name of metric to extract
            window_size: Number of recent data points
            
        Returns:
            List of metric values, most recent first
        """
        snapshots = self.load_history(limit=window_size)
        values = []
        
        for snapshot in snapshots:
            if metric_name in snapshot.metrics:
                values.append(snapshot.metrics[metric_name])
        
        return values
    
    def cleanup_old_entries(self, retain_days: int = 90) -> int:
        """Remove entries older than specified days.
        
        Args:
            retain_days: Number of days to retain
            
        Returns:
            Number of entries removed
        """
        if not self.history_file.exists():
            return 0
        
        cutoff = datetime.now(timezone.utc) - timedelta(days=retain_days)
        
        temp_file = self.history_file.with_suffix('.tmp')
        removed_count = 0
        kept_count = 0
        
        with open(self.history_file, "r", encoding="utf-8") as infile, \
             open(temp_file, "w", encoding="utf-8") as outfile:
            
            for line in infile:
                line = line.strip()
                if not line:
                    continue
                    
                try:
                    snapshot = MetricsSnapshot.from_jsonl(line)
                    snapshot_time = datetime.fromisoformat(snapshot.timestamp.replace('Z', '+00:00'))
                    
                    if snapshot_time >= cutoff:
                        outfile.write(line + "\n")
                        kept_count += 1
                    else:
                        removed_count += 1
                        
                except (json.JSONDecodeError, ValueError) as e:
                    logger.warning(f"Skipped invalid entry during cleanup: {e}")
                    removed_count += 1
        
        # Replace original with cleaned file
        temp_file.replace(self.history_file)
        
        logger.info(f"Cleaned history: kept {kept_count}, removed {removed_count} entries")
        return removed_count
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics about stored history.
        
        Returns:
            Dictionary with history statistics
        """
        snapshots = self.load_history()
        
        if not snapshots:
            return {
                "total_entries": 0,
                "date_range": None,
                "metrics_tracked": [],
                "branches": [],
                "versions": []
            }
        
        # Extract unique values
        all_metrics = set()
        branches = set()
        versions = set()
        
        for snapshot in snapshots:
            all_metrics.update(snapshot.metrics.keys())
            branches.add(snapshot.branch)
            versions.add(snapshot.version)
        
        return {
            "total_entries": len(snapshots),
            "date_range": {
                "earliest": snapshots[-1].timestamp,  # Last in reversed list
                "latest": snapshots[0].timestamp      # First in reversed list
            },
            "metrics_tracked": sorted(all_metrics),
            "branches": sorted(branches),
            "versions": sorted(versions),
            "file_size_bytes": self.history_file.stat().st_size if self.history_file.exists() else 0
        }


class StatisticalAnalyzer:
    """Analyzes historical metrics for adaptive threshold calculation."""
    
    def __init__(self, history_manager: HistoryManager):
        """Initialize analyzer.
        
        Args:
            history_manager: History manager instance
        """
        self.history = history_manager
    
    def calculate_confidence_interval(self, 
                                    values: List[float], 
                                    confidence: float = 0.95) -> Tuple[float, float]:
        """Calculate confidence interval for values.
        
        Args:
            values: List of metric values
            confidence: Confidence level (0-1)
            
        Returns:
            Tuple of (lower_bound, upper_bound)
        """
        if len(values) < 2:
            return (0.0, float('inf'))
        
        mean = statistics.mean(values)
        stdev = statistics.stdev(values)
        
        # Use t-distribution for small samples
        if len(values) < 30:
            # Approximation for t-distribution critical value
            if confidence == 0.95:
                t_critical = 2.262  # t(0.025, df=9) for small samples
            else:
                t_critical = 2.576  # 99% confidence approximation
        else:
            # Normal distribution for large samples
            if confidence == 0.95:
                t_critical = 1.96
            else:
                t_critical = 2.576
        
        margin = t_critical * (stdev / math.sqrt(len(values)))
        
        return (mean - margin, mean + margin)
    
    def calculate_adaptive_threshold(self, 
                                   metric_name: str,
                                   threshold_type: str,
                                   window_size: int = 10,
                                   confidence: float = 0.95) -> Optional[float]:
        """Calculate adaptive threshold for a metric.
        
        Args:
            metric_name: Name of metric
            threshold_type: 'upper' for max allowed, 'lower' for min allowed
            window_size: Number of recent samples to analyze
            confidence: Statistical confidence level
            
        Returns:
            Calculated threshold value or None if insufficient data
        """
        values = self.history.get_metric_series(metric_name, window_size)
        
        if len(values) < 3:
            logger.warning(f"Insufficient data for {metric_name}: {len(values)} samples")
            return None
        
        # Remove outliers using IQR method
        values = self._remove_outliers(values)
        
        if len(values) < 2:
            logger.warning(f"Too few samples after outlier removal for {metric_name}")
            return None
        
        lower_bound, upper_bound = self.calculate_confidence_interval(values, confidence)
        
        if threshold_type == 'upper':
            return upper_bound
        elif threshold_type == 'lower':
            return lower_bound
        else:
            raise ValueError(f"Invalid threshold_type: {threshold_type}")
    
    def _remove_outliers(self, values: List[float]) -> List[float]:
        """Remove statistical outliers using IQR method.
        
        Args:
            values: List of values
            
        Returns:
            Values with outliers removed
        """
        if len(values) < 4:
            return values
        
        # Sort for quartile calculation
        sorted_values = sorted(values)
        n = len(sorted_values)
        
        # Calculate quartiles
        q1_idx = n // 4
        q3_idx = 3 * n // 4
        
        q1 = sorted_values[q1_idx]
        q3 = sorted_values[q3_idx]
        iqr = q3 - q1
        
        # Calculate outlier bounds
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        # Filter outliers
        filtered = [v for v in values if lower_bound <= v <= upper_bound]
        
        if len(filtered) < len(values):
            logger.debug(f"Removed {len(values) - len(filtered)} outliers from {len(values)} values")
        
        return filtered if filtered else values  # Return original if all were outliers
    
    def get_trend_analysis(self, metric_name: str, window_size: int = 20) -> Dict[str, Any]:
        """Analyze trend for a metric.
        
        Args:
            metric_name: Name of metric to analyze
            window_size: Number of recent samples for trend analysis
            
        Returns:
            Dictionary with trend information
        """
        values = self.history.get_metric_series(metric_name, window_size)
        
        if len(values) < 5:
            return {
                "trend": "insufficient_data",
                "samples": len(values),
                "slope": None,
                "r_squared": None
            }
        
        # Simple linear regression for trend
        # Note: values are in reverse chronological order (newest first)
        # For trend analysis, we need chronological order (oldest first)
        x = list(range(len(values)))
        y = list(reversed(values))  # Reverse to get chronological order
        
        n = len(values)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(x[i] * y[i] for i in range(n))
        sum_x2 = sum(x[i] ** 2 for i in range(n))
        
        # Calculate slope and intercept
        denominator = n * sum_x2 - sum_x ** 2
        if denominator == 0:
            return {
                "trend": "no_trend",
                "samples": n,
                "slope": 0.0,
                "r_squared": 0.0
            }
        
        slope = (n * sum_xy - sum_x * sum_y) / denominator
        intercept = (sum_y - slope * sum_x) / n
        
        # Calculate R-squared
        y_mean = statistics.mean(y)
        ss_tot = sum((y[i] - y_mean) ** 2 for i in range(n))
        ss_res = sum((y[i] - (slope * x[i] + intercept)) ** 2 for i in range(n))
        
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0.0
        
        # Determine trend direction
        if abs(slope) < 0.01:  # Very small slope
            trend = "stable"
        elif slope > 0:
            trend = "increasing"
        else:
            trend = "decreasing"
        
        return {
            "trend": trend,
            "samples": n,
            "slope": slope,
            "r_squared": r_squared,
            "confidence": "high" if r_squared > 0.7 else "medium" if r_squared > 0.3 else "low"
        }


# Utility functions for integration
def initialize_history(reports_dir: Path) -> HistoryManager:
    """Initialize history manager for given reports directory.
    
    Args:
        reports_dir: Reports directory path
        
    Returns:
        Configured HistoryManager instance
    """
    history_dir = reports_dir / "history"
    return HistoryManager(history_dir)


def collect_and_store_metrics(reports_dir: Path, metrics: Dict[str, float]) -> MetricsSnapshot:
    """Convenience function to collect and store metrics.
    
    Args:
        reports_dir: Reports directory path
        metrics: Metrics to store
        
    Returns:
        Created snapshot
    """
    history = initialize_history(reports_dir)
    return history.collect_current_and_append(metrics)