# src/core/performance_optimizer.py
import logging
import concurrent.futures
from typing import List, Dict, Any
import time

class PerformanceOptimizer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.performance_history = []
        self.optimization_threshold = 0.8
        
    def parallel_execution(self, tasks: List[Dict], resources: Dict = None, monitoring: bool = False) -> List[Any]:
        """Execute tasks in parallel with resource management"""
        start_time = time.time()
        results = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=resources.get('max_workers', 4)) as executor:
            future_to_task = {executor.submit(self._execute_task, task): task for task in tasks}
            for future in concurrent.futures.as_completed(future_to_task):
                try:
                    result = future.result()
                    results.append(result)
                    if monitoring:
                        self._monitor_task_performance(future_to_task[future], result)
                except Exception as e:
                    self.logger.error(f"Task execution failed: {str(e)}")
        
        execution_time = time.time() - start_time
        self.performance_history.append(execution_time)
        return results
    
    def analyze_and_adapt(self, results: List[Any]) -> None:
        """Analyze performance and adapt optimization parameters"""
        if len(self.performance_history) > 1:
            current_perf = self.performance_history[-1]
            avg_perf = sum(self.performance_history[:-1]) / len(self.performance_history[:-1])
            
            if current_perf > avg_perf * self.optimization_threshold:
                self._adjust_optimization_parameters()
    
    def _execute_task(self, task: Dict) -> Any:
        """Execute single task with performance monitoring"""
        try:
            start_time = time.time()
            result = task['function'](*task.get('args', []), **task.get('kwargs', {}))
            execution_time = time.time() - start_time
            
            return {
                'result': result,
                'execution_time': execution_time,
                'task_id': task.get('id')
            }
        except Exception as e:
            self.logger.error(f"Task execution error: {str(e)}")
            raise
    
    def _monitor_task_performance(self, task: Dict, result: Dict) -> None:
        """Monitor individual task performance"""
        if result['execution_time'] > task.get('expected_time', 1.0):
            self.logger.warning(f"Task {task.get('id')} exceeded expected execution time")
    
    def _adjust_optimization_parameters(self) -> None:
        """Adjust internal optimization parameters based on performance"""
        self.optimization_threshold *= 0.95  # Gradually reduce threshold for more aggressive optimization