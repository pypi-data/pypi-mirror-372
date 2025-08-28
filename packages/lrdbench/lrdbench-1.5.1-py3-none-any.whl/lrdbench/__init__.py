"""
LRDBench: Long-Range Dependence Benchmarking Toolkit

A comprehensive toolkit for benchmarking long-range dependence estimators
on synthetic and real-world time series data.
"""

__version__ = "1.5.1"
__author__ = "LRDBench Development Team"
__email__ = "lrdbench@example.com"

# Core components
from .analysis.benchmark import ComprehensiveBenchmark
from .models.data_models import FBMModel, FGNModel, ARFIMAModel, MRWModel

# Analytics components
from .analytics import (
    UsageTracker,
    PerformanceMonitor,
    ErrorAnalyzer,
    WorkflowAnalyzer,
    AnalyticsDashboard,
)

# Convenience functions
from .analytics.dashboard import quick_analytics_summary, get_analytics_dashboard
from .analytics.usage_tracker import get_usage_tracker, track_usage
from .analytics.performance_monitor import get_performance_monitor, monitor_performance
from .analytics.error_analyzer import get_error_analyzer, track_errors
from .analytics.workflow_analyzer import get_workflow_analyzer, track_workflow


# High-level API
def enable_analytics(enable: bool = True, privacy_mode: bool = True):
    """
    Enable or disable analytics tracking
    """
    if enable:
        tracker = get_usage_tracker()
        tracker.enable_tracking = True
        tracker.privacy_mode = privacy_mode
        print("✅ Analytics tracking enabled")
    else:
        tracker = get_usage_tracker()
        tracker.enable_tracking = False
        print("❌ Analytics tracking disabled")


def get_analytics_summary(days: int = 30) -> str:
    """
    Get a quick summary of analytics data
    """
    return quick_analytics_summary(days)


def generate_analytics_report(days: int = 30, output_dir: str = None) -> str:
    """
    Generate comprehensive analytics report
    """
    dashboard = get_analytics_dashboard()
    return dashboard.generate_comprehensive_report(days, output_dir)


# Main exports
__all__ = [
    "ComprehensiveBenchmark",
    "FBMModel",
    "FGNModel",
    "ARFIMAModel",
    "MRWModel",
    "UsageTracker",
    "PerformanceMonitor",
    "ErrorAnalyzer",
    "WorkflowAnalyzer",
    "AnalyticsDashboard",
    "enable_analytics",
    "get_analytics_summary",
    "generate_analytics_report",
    "track_usage",
    "monitor_performance",
    "track_errors",
    "track_workflow",
    "__version__",
    "__author__",
    "__email__",
]

# Enable analytics by default (can be disabled by user)
try:
    enable_analytics(True, True)
except Exception as e:
    print(f"Warning: Could not initialize analytics: {e}")
