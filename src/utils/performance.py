import time
import psutil
import os
import sys
from typing import Dict, Any, Optional, Callable, List
from functools import wraps
from dataclasses import dataclass, field
from enum import Enum


class PerformanceMetric(Enum):
    EXECUTION_TIME = "execution_time"
    MEMORY_USAGE = "memory_usage"
    NODES_EVALUATED = "nodes_evaluated"
    BRANCHES_PRUNED = "branches_pruned"
    CACHE_HITS = "cache_hits"
    CALL_COUNT = "call_count"


@dataclass
class PerformanceStats:
    execution_time: float = 0.0
    peak_memory_mb: float = 0.0
    nodes_evaluated: int = 0
    branches_pruned: int = 0
    cache_hits: int = 0
    call_count: int = 0
    start_time: float = field(default_factory=time.time, init=False)
    start_memory: float = field(default_factory=lambda: psutil.Process().memory_info().rss, init=False)
    
    def start_timer(self) -> None:
        self.start_time = time.time()
        self.start_memory = psutil.Process().memory_info().rss
    
    def stop_timer(self) -> None:
        current_memory = psutil.Process().memory_info().rss
        self.execution_time = time.time() - self.start_time
        self.peak_memory_mb = max(self.peak_memory_mb, 
                                 (current_memory - self.start_memory) / (1024 * 1024))
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "execution_time_seconds": round(self.execution_time, 4),
            "peak_memory_mb": round(self.peak_memory_mb, 2),
            "nodes_evaluated": self.nodes_evaluated,
            "branches_pruned": self.branches_pruned,
            "cache_hits": self.cache_hits,
            "call_count": self.call_count,
            "nodes_per_second": round(self.nodes_evaluated / self.execution_time, 2) 
                               if self.execution_time > 0 else 0,
            "pruning_efficiency": round(self.branches_pruned / (self.nodes_evaluated + self.branches_pruned), 4) 
                                if (self.nodes_evaluated + self.branches_pruned) > 0 else 0
        }
    
    def reset(self) -> None:
        self.execution_time = 0.0
        self.peak_memory_mb = 0.0
        self.nodes_evaluated = 0
        self.branches_pruned = 0
        self.cache_hits = 0
        self.call_count = 0


class PerformanceMonitor:
    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self.stats = PerformanceStats()
        self.history: List[Dict[str, Any]] = []
        
    def start(self) -> None:
        """Start monitoring."""
        if self.enabled:
            self.stats.start_timer()
    
    def stop(self) -> None:
        if self.enabled:
            self.stats.stop_timer()
            self.history.append(self.stats.to_dict())
    
    def record_metric(self, metric: PerformanceMetric, value: Any = 1) -> None:
        if not self.enabled:
            return
            
        if metric == PerformanceMetric.NODES_EVALUATED:
            self.stats.nodes_evaluated += int(value)
        elif metric == PerformanceMetric.BRANCHES_PRUNED:
            self.stats.branches_pruned += int(value)
        elif metric == PerformanceMetric.CACHE_HITS:
            self.stats.cache_hits += int(value)
        elif metric == PerformanceMetric.CALL_COUNT:
            self.stats.call_count += int(value)
    
    def get_current_stats(self) -> Dict[str, Any]:
        return self.stats.to_dict()
    
    def get_history(self) -> List[Dict[str, Any]]:
        return self.history.copy()
    
    def reset(self) -> None:
        self.stats.reset()
    
    def compare_algorithms(self, stats1: Dict[str, Any], stats2: Dict[str, Any], 
                          name1: str = "Algorithm 1", name2: str = "Algorithm 2") -> str:
        comparison = []
        comparison.append(f"\n{'='*60}")
        comparison.append("ALGORITHM PERFORMANCE COMPARISON")
        comparison.append(f"{'='*60}\n")
        
        metrics = [
            ("Execution Time (s)", "execution_time_seconds", True),
            ("Nodes Evaluated", "nodes_evaluated", False),
            ("Branches Pruned", "branches_pruned", False),
            ("Nodes/Second", "nodes_per_second", False),
            ("Pruning Efficiency", "pruning_efficiency", True),
            ("Memory Usage (MB)", "peak_memory_mb", True)
        ]
        
        for label, key, is_percentage in metrics:
            val1 = stats1.get(key, 0)
            val2 = stats2.get(key, 0)
            
            if val1 == 0 and val2 == 0:
                continue
            
            if is_percentage:
                val1_str = f"{val1:.2%}" if isinstance(val1, float) else f"{val1}%"
                val2_str = f"{val2:.2%}" if isinstance(val2, float) else f"{val2}%"
            else:
                val1_str = f"{val1:,.2f}" if isinstance(val1, float) else f"{val1:,}"
                val2_str = f"{val2:,.2f}" if isinstance(val2, float) else f"{val2:,}"
            
            # Calculate improvement
            if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                if val1 != 0:
                    improvement = ((val1 - val2) / val1) * 100
                    if "Time" in label or "Memory" in label:
                        # Lower is better
                        direction = "faster" if improvement > 0 else "slower"
                    else:
                        # Higher is better
                        direction = "better" if improvement > 0 else "worse"
                    
                    improvement_str = f" ({abs(improvement):.1f}% {direction})"
                else:
                    improvement_str = ""
            else:
                improvement_str = ""
            
            comparison.append(f"{label:25} {name1:15} {val1_str:>15} {name2:15} {val2_str:>15}{improvement_str}")
        
        return "\n".join(comparison)
    
    def generate_report(self, algorithm_name: str = "Unknown") -> str:
        stats = self.get_current_stats()
        
        report = []
        report.append(f"\n{'='*60}")
        report.append(f"PERFORMANCE REPORT: {algorithm_name}")
        report.append(f"{'='*60}\n")
        
        report.append("SUMMARY:")
        report.append(f"  Execution Time: {stats['execution_time_seconds']:.4f} seconds")
        report.append(f"  Peak Memory: {stats['peak_memory_mb']:.2f} MB")
        report.append(f"  Nodes Evaluated: {stats['nodes_evaluated']:,}")
        report.append(f"  Branches Pruned: {stats['branches_pruned']:,}")
        report.append(f"  Cache Hits: {stats['cache_hits']:,}")
        report.append(f"  Nodes/Second: {stats['nodes_per_second']:,.0f}")
        report.append(f"  Pruning Efficiency: {stats['pruning_efficiency']:.2%}")
        
        report.append("\nANALYSIS:")
        if stats['execution_time_seconds'] < 0.1:
            report.append("Very fast execution")
        elif stats['execution_time_seconds'] < 1.0:
            report.append("Fast execution")
        elif stats['execution_time_seconds'] < 5.0:
            report.append("Moderate execution time")
        else:
            report.append("Slow execution - consider depth limiting")
        
        if stats['pruning_efficiency'] > 0.7:
            report.append("Excellent pruning efficiency")
        elif stats['pruning_efficiency'] > 0.3:
            report.append("Good pruning efficiency")
        else:
            report.append("Low pruning efficiency - algorithm exploring many branches")
        
        if stats['nodes_per_second'] > 10000:
            report.append("Excellent node evaluation rate")
        elif stats['nodes_per_second'] > 1000:
            report.append("Good node evaluation rate")
        else:
            report.append("Low node evaluation rate")
        
        return "\n".join(report)
    
    def memory_usage_decorator(self, func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not self.enabled:
                return func(*args, **kwargs)
            
            # Get memory before
            process = psutil.Process()
            memory_before = process.memory_info().rss / (1024 * 1024)  # MB
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Get memory after
            memory_after = process.memory_info().rss / (1024 * 1024)  # MB
            memory_diff = memory_after - memory_before
            
            # Record
            self.record_metric(PerformanceMetric.MEMORY_USAGE, memory_diff)
            
            return result
        
        return wrapper
    
    def execution_time_decorator(self, func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not self.enabled:
                return func(*args, **kwargs)
            
            start_time = time.time()
            result = func(*args, **kwargs)
            elapsed = time.time() - start_time
            
            self.record_metric(PerformanceMetric.EXECUTION_TIME, elapsed)
            
            return result
        
        return wrapper


class AlgorithmBenchmark:    
    def __init__(self):
        self.results = {}
        
    def run_benchmark(self, algorithms: Dict[str, Callable], test_cases: Dict[str, Any], 
                     iterations: int = 1) -> Dict[str, Dict[str, Any]]:
        benchmark_results = {}
        
        for test_name, test_data in test_cases.items():
            benchmark_results[test_name] = {}
            
            for algo_name, algo_func in algorithms.items():
                print(f"Benchmarking {algo_name} on {test_name}...")
                
                monitor = PerformanceMonitor(enabled=True)
                monitor.start()
                
                for _ in range(iterations):
                    result = algo_func(test_data)
                
                monitor.stop()
                
                benchmark_results[test_name][algo_name] = {
                    "stats": monitor.get_current_stats(),
                    "result": result
                }
        
        self.results = benchmark_results
        return benchmark_results
    
    def generate_benchmark_report(self) -> str:
        if not self.results:
            return "No benchmark results available."
        
        report = []
        report.append("\n" + "="*80)
        report.append("ALGORITHM BENCHMARK REPORT")
        report.append("="*80)
        
        for test_name, algorithms in self.results.items():
            report.append(f"\n{'='*60}")
            report.append(f"TEST CASE: {test_name}")
            report.append(f"{'='*60}\n")
            
            report.append(f"{'Algorithm':20} {'Time (s)':>10} {'Nodes':>10} {'Nodes/s':>10} {'Memory (MB)':>12} {'Pruning %':>10}")
            report.append("-"*80)
            
            for algo_name, result in algorithms.items():
                stats = result["stats"]
                report.append(f"{algo_name:20} "
                            f"{stats['execution_time_seconds']:10.4f} "
                            f"{stats['nodes_evaluated']:10,} "
                            f"{stats['nodes_per_second']:10,.0f} "
                            f"{stats['peak_memory_mb']:12.2f} "
                            f"{stats['pruning_efficiency']:10.2%}")
        
        report.append(f"\n{'='*80}")
        report.append("SUMMARY")
        report.append(f"{'='*80}")
        
        metrics = ["execution_time_seconds", "nodes_evaluated", "nodes_per_second", "pruning_efficiency"]
        metric_names = ["Fastest", "Most Efficient", "Highest Throughput", "Best Pruning"]
        
        for metric, name in zip(metrics, metric_names):
            best_algo = None
            best_value = None
            is_lower_better = metric in ["execution_time_seconds", "nodes_evaluated"]
            
            for test_name, algorithms in self.results.items():
                for algo_name, result in algorithms.items():
                    value = result["stats"][metric]
                    
                    if best_value is None:
                        best_value = value
                        best_algo = (algo_name, test_name)
                    elif is_lower_better and value < best_value:
                        best_value = value
                        best_algo = (algo_name, test_name)
                    elif not is_lower_better and value > best_value:
                        best_value = value
                        best_algo = (algo_name, test_name)
            
            if best_algo:
                if is_lower_better:
                    report.append(f"{name}: {best_algo[0]} (Test: {best_algo[1]}) with {best_value:.4f}")
                else:
                    report.append(f"{name}: {best_algo[0]} (Test: {best_algo[1]}) with {best_value:.2%}")
        
        return "\n".join(report)


def get_system_info() -> Dict[str, Any]:
    import platform
    
    system_info = {
        "python_version": sys.version,
        "platform": platform.platform(),
        "processor": platform.processor(),
        "cpu_count": psutil.cpu_count(),
        "total_memory_gb": psutil.virtual_memory().total / (1024**3),
        "available_memory_gb": psutil.virtual_memory().available / (1024**3)
    }
    
    return system_info


def estimate_complexity(stack_length: int, branching_factor: int = 2) -> Dict[str, Any]:
    max_depth = stack_length // 2
    
    # Theoretical node counts
    perfect_tree_nodes = sum(branching_factor ** i for i in range(max_depth + 1))
    
    # Realistic estimate (game ends when total reaches/exceeds 21)
    estimates = {
        "stack_length": stack_length,
        "max_depth": max_depth,
        "branching_factor": branching_factor,
        "perfect_tree_nodes": f"{perfect_tree_nodes:,}",
        "lower_bound_nodes": f"{max_depth * branching_factor:,}",
        "upper_bound_nodes": f"{perfect_tree_nodes:,}",
        "estimated_nodes": f"{int(perfect_tree_nodes * 0.3):,}",  # Rough estimate
        "complexity_class": "O(2^(n/2))"  # Exponential in stack length
    }
    
    return estimates


# Example usage
if __name__ == "__main__":
    monitor = PerformanceMonitor(enabled=True)
    
    @monitor.execution_time_decorator
    def test_function():
        """Test function for performance monitoring."""
        total = 0
        for i in range(1000000):
            total += i
        return total
    
    monitor.start()
    result = test_function()
    monitor.stop()
    
    # Print report
    print(monitor.generate_report("Test Algorithm"))
    
    print("\nSystem Information:")
    for key, value in get_system_info().items():
        print(f"  {key}: {value}")
    
    # Estimate complexity
    print("\nComplexity Estimation for stack length=12:")
    complexity = estimate_complexity(12)
    for key, value in complexity.items():
        print(f"  {key}: {value}")