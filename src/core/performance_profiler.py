# src/core/performance_profiler.py
import logging
import time
from functools import wraps
from typing import Dict, List, Callable, Any
from collections import defaultdict

class PerformanceProfiler:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.metrics = defaultdict(list)
        self.execution_history = []
        
    def measure_execution_time(self, func: Callable) -> Callable:
        """Decorator to measure function execution time"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                self._record_metric(func.__name__, execution_time)
                return result
            except Exception as e:
                self.logger.error(f"Error in {func.__name__}: {str(e)}")
                raise
        return wrapper
    
    def get_metrics(self) -> Dict[str, Dict[str, float]]:
        """Get performance metrics summary"""
        metrics_summary = {}
        for func_name, times in self.metrics.items():
            if times:
                metrics_summary[func_name] = {
                    'avg_time': sum(times) / len(times),
                    'min_time': min(times),
                    'max_time': max(times),
                    'total_calls': len(times)
                }
        return metrics_summary
    
    def _record_metric(self, func_name: str, execution_time: float) -> None:
        """Record execution time metric"""
        self.metrics[func_name].append(execution_time)
        self.execution_history.append({
            'function': func_name,
            'time': execution_time,
            'timestamp': time.time()
        })
        
        # Keep history manageable
        if len(self.execution_history) > 1000:
            self.execution_history = self.execution_history[-1000:]
            
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate detailed performance report"""
        report = {
            'metrics': self.get_metrics(),
            'total_functions': len(self.metrics),
            'total_executions': sum(len(times) for times in self.metrics.values())
        }
        return report
