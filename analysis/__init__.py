"""
Analysis module for statistical aggregation and visualization
"""

from .statistical_aggregator import StatisticalAggregator, analyze_multiple_runs
from .comparative_visualizer import ComparativeVisualizer, visualize_run
from .result_explorer import ResultExplorer

__all__ = [
    'StatisticalAggregator',
    'analyze_multiple_runs',
    'ComparativeVisualizer', 
    'visualize_run',
    'ResultExplorer'
]