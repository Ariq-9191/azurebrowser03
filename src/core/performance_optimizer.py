# src/core/performance_optimizer.py
import logging
import concurrent.futures
from typing import List, Dict, Any, Tuple
import time
import numpy as np
from .ai_brain import AIBrain
from pathlib import Path
import json
import psutil
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed

@dataclass
class TaskMetrics:
    execution_time: float
    success: bool
    resource_usage: Dict[str, float]
    optimization_score: float

class PerformanceOptimizer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.performance_history = []
        self.optimization_threshold = 0.8
        self.ai_brain = AIBrain()
        self.optimization_cache = {}
        self.learning_rate = 0.002
        self.task_metrics = {}
        self.system_mode = self._determine_system_mode()
        self._load_optimization_config()

    def _determine_system_mode(self) -> str:
        """Determine optimal system mode based on hardware"""
        try:
            ram_gb = psutil.virtual_memory().total / (1024 * 1024 * 1024)
            cpu_cores = psutil.cpu_count()
            
            if ram_gb >= 32 and cpu_cores >= 12:
                return 'performance'
            elif ram_gb >= 16 and cpu_cores >= 8:
                return 'balanced'
            else:
                return 'memory_saving'
        except:
            return 'memory_saving'
            
    def optimize_for_current_system(self):
        """Apply optimizations based on system mode"""
        config = {
            'performance': {
                'browser_config': {
                    'disable_images': False,
                    'process_limit': -1,
                    'memory_limit': None
                },
                'cache_config': {
                    'max_size': '4GB',
                    'cleanup_interval': 3600
                },
                'ai_config': {
                    'enable_training': True,
                    'batch_size': 64
                }
            },
            'balanced': {
                'browser_config': {
                    'disable_images': False,
                    'process_limit': 50,
                    'memory_limit': '8GB'
                },
                'cache_config': {
                    'max_size': '2GB',
                    'cleanup_interval': 1800
                },
                'ai_config': {
                    'enable_training': True,
                    'batch_size': 32
                }
            },
            'memory_saving': {
                'browser_config': {
                    'disable_images': True,
                    'process_limit': 20,
                    'memory_limit': '4GB'
                },
                'cache_config': {
                    'max_size': '1GB',
                    'cleanup_interval': 900
                },
                'ai_config': {
                    'enable_training': False,
                    'batch_size': 16
                }
            }
        }
        
        return config[self.system_mode]
        
    def _load_optimization_config(self):
        """Load optimization configuration"""
        try:
            config_path = Path(__file__).parent.parent.parent / 'config' / 'optimization_config.json'
            if config_path.exists():
                with open(config_path) as f:
                    self.config = json.load(f)
            else:
                self.config = self._create_default_config()
        except Exception as e:
            self.logger.error(f"Failed to load config: {str(e)}")
            self.config = self._create_default_config()
            
    def _create_default_config(self) -> Dict:
        """Create default optimization configuration"""
        return {
            'max_parallel_tasks': 8,
            'resource_threshold': 0.75,
            'optimization_intervals': [100, 500, 1000],
            'learning_parameters': {
                'batch_size': 32,
                'epochs': 5,
                'validation_split': 0.2
            }
        }

    def parallel_execution(self, tasks: List[Dict], resources: Dict = None, monitoring: bool = False) -> List[Any]:
        """Enhanced parallel execution with adaptive optimization"""
        start_time = time.time()
        results = []
        
        # Analyze tasks for optimization potential
        optimized_tasks = self._optimize_task_batch(tasks)
        
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self._calculate_optimal_workers(resources)
        ) as executor:
            future_to_task = {
                executor.submit(
                    self._execute_task_with_learning,
                    task
                ): task for task in optimized_tasks
            }
            
            for future in concurrent.futures.as_completed(future_to_task):
                try:
                    result = future.result()
                    results.append(result)
                    if monitoring:
                        self._update_optimization_model(
                            future_to_task[future],
                            result
                        )
                except Exception as e:
                    self.logger.error(f"Task execution failed: {str(e)}")
                    
        execution_time = time.time() - start_time
        self._record_performance_metrics(execution_time, len(tasks), results)
        return results
        
    def _optimize_task_batch(self, tasks: List[Dict]) -> List[Dict]:
        """Optimize task batch using AI insights"""
        optimized_tasks = []
        for task in tasks:
            task_hash = self._calculate_task_hash(task)
            
            if task_hash in self.optimization_cache:
                optimized_task = self.optimization_cache[task_hash].copy()
            else:
                optimized_task = self._apply_ai_optimization(task)
                self.optimization_cache[task_hash] = optimized_task.copy()
                
            optimized_tasks.append(optimized_task)
            
        return self._balance_task_distribution(optimized_tasks)
        
    def _execute_task_with_learning(self, task: Dict) -> Dict:
        """Execute task with learning capabilities"""
        try:
            start_time = time.time()
            context = self._prepare_execution_context(task)
            
            result = task['function'](*task.get('args', []), **task.get('kwargs', {}))
            execution_time = time.time() - start_time
            
            # Record experience for learning
            self.ai_brain.store_experience(
                context=context,
                outcome={
                    'success': True,
                    'execution_time': execution_time,
                    'result': result
                },
                success=True
            )
            
            return {
                'result': result,
                'execution_time': execution_time,
                'task_id': task.get('id'),
                'optimization_data': context
            }
            
        except Exception as e:
            self.logger.error(f"Task execution failed: {str(e)}")
            self.ai_brain.store_experience(
                context=context,
                outcome={'error': str(e)},
                success=False
            )
            raise
            
    def _calculate_task_hash(self, task: Dict) -> str:
        """Calculate unique hash for task caching"""
        task_data = {
            'function': task['function'].__name__,
            'args': str(task.get('args', [])),
            'kwargs': str(task.get('kwargs', {}))
        }
        return str(hash(json.dumps(task_data, sort_keys=True)))
        
    def _apply_ai_optimization(self, task: Dict) -> Dict:
        """Apply AI-driven optimization to task"""
        optimized_task = task.copy()
        
        # Analyze task characteristics
        task_analysis = self.ai_brain.analyze_code_pattern(
            str(task['function'].__code__.co_code)
        )
        
        # Apply optimization based on analysis
        if task_analysis.get('complexity', 0) > 0.7:
            optimized_task['batch_size'] = self.config['learning_parameters']['batch_size']
            optimized_task['priority'] = 'high'
            
        return optimized_task
        
    def _record_performance_metrics(self, execution_time: float, task_count: int, results: List[Dict]):
        """Record detailed performance metrics"""
        metrics = {
            'execution_time': execution_time,
            'task_count': task_count,
            'success_rate': sum(1 for r in results if not r.get('error', None)) / task_count,
            'avg_task_time': execution_time / task_count if task_count > 0 else 0,
            'resource_usage': self._get_resource_usage()
        }
        self.performance_history.append(metrics)
        
        # Trim history if too long
        if len(self.performance_history) > 1000:
            self.performance_history = self.performance_history[-1000:]
            
    def _get_resource_usage(self) -> Dict[str, float]:
        """Get current resource usage"""
        try:
            return {
                'cpu_percent': psutil.cpu_percent(),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_io': psutil.disk_io_counters().read_bytes + 
                          psutil.disk_io_counters().write_bytes
            }
        except:
            return {}
            
    def _balance_task_distribution(self, tasks: List[Dict]) -> List[Dict]:
        """Balance task distribution for optimal performance"""
        if not tasks:
            return []
            
        # Sort tasks by priority and complexity
        tasks.sort(key=lambda x: (
            x.get('priority', 'medium'),
            x.get('complexity', 0)
        ), reverse=True)
        
        # Group tasks by resource requirements
        cpu_intensive = []
        io_intensive = []
        balanced = []
        
        for task in tasks:
            task_type = self._analyze_task_type(task)
            if task_type == 'cpu':
                cpu_intensive.append(task)
            elif task_type == 'io':
                io_intensive.append(task)
            else:
                balanced.append(task)
                
        # Interleave tasks for optimal resource usage
        optimized_tasks = []
        while any([cpu_intensive, io_intensive, balanced]):
            if cpu_intensive:
                optimized_tasks.append(cpu_intensive.pop(0))
            if io_intensive:
                optimized_tasks.append(io_intensive.pop(0))
            if balanced:
                optimized_tasks.append(balanced.pop(0))
                
        return optimized_tasks
        
    def _analyze_task_type(self, task: Dict) -> str:
        """Analyze task type based on characteristics"""
        if 'type' in task:
            return task['type']
            
        # Analyze based on function characteristics
        func = task['function']
        code = str(func.__code__.co_code)
        
        if 'read' in code or 'write' in code or 'open' in code:
            return 'io'
        elif any(op in code for op in ['multiply', 'divide', 'pow']):
            return 'cpu'
        return 'balanced'
        
    def _prepare_execution_context(self, task: Dict) -> Dict:
        """Prepare context for task execution"""
        return {
            'task_type': task['function'].__name__,
            'complexity': task.get('complexity', 0),
            'priority': task.get('priority', 'medium'),
            'timestamp': time.time()
        }
        
    def _update_optimization_model(self, task: Dict, result: Dict):
        """Update optimization model with execution results"""
        if len(self.performance_history) >= 100:
            self.ai_brain.learn_from_experience()
            self._adjust_optimization_parameters()
            
    def _adjust_optimization_parameters(self, metrics: Dict = None):
        """Adjust optimization parameters based on performance"""
        try:
            if self.system_mode == 'memory_saving':
                return  # Don't adjust in memory saving mode
                
            if metrics:
                avg_cpu = sum(metrics['cpu_usage']) / len(metrics['cpu_usage'])
                avg_memory = sum(metrics['memory_usage']) / len(metrics['memory_usage'])
                
                if avg_cpu > 80 or avg_memory > 80:
                    self._reduce_resource_usage()
                elif avg_cpu < 40 and avg_memory < 40:
                    self._increase_resource_usage()
            
            if len(self.performance_history) < 2:
                return
                
            recent_perf = self.performance_history[-1]
            prev_perf = self.performance_history[-2]
            
            # Calculate performance change
            perf_change = (recent_perf['success_rate'] - prev_perf['success_rate']) / prev_perf['success_rate']
            
            # Adjust learning rate
            if perf_change > 0:
                self.learning_rate *= 1.1  # Increase learning rate
            else:
                self.learning_rate *= 0.9  # Decrease learning rate
                
            # Keep learning rate in reasonable bounds
            self.learning_rate = max(0.0001, min(0.01, self.learning_rate))
            
            # Adjust optimization threshold
            if recent_perf['success_rate'] < 0.8:
                self.optimization_threshold *= 0.95
            else:
                self.optimization_threshold *= 1.05
                
            self.optimization_threshold = max(0.6, min(0.95, self.optimization_threshold))
                
        except Exception as e:
            self.logger.error(f"Parameter adjustment failed: {str(e)}")
            
    def execute_with_monitoring(self, task: Dict, callback: callable = None) -> Dict:
        """Execute task with performance monitoring"""
        try:
            start_time = time.time()
            metrics = {
                'cpu_usage': [],
                'memory_usage': [],
                'execution_time': 0
            }
            
            # Start monitoring
            monitor_thread = threading.Thread(
                target=self._monitor_execution,
                args=(metrics,)
            )
            monitor_thread.start()
            
            # Execute task
            result = self._execute_task(task)
            
            # Stop monitoring
            metrics['execution_time'] = time.time() - start_time
            
            # Analyze performance
            performance_score = self._analyze_performance(metrics)
            
            # Update optimization parameters if needed
            if performance_score < self.optimization_threshold:
                self._adjust_optimization_parameters(metrics)
                
            return {
                'success': True,
                'result': result,
                'metrics': metrics,
                'performance_score': performance_score
            }
            
        except Exception as e:
            self.logger.error(f"Execution failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
            
    def _monitor_execution(self, metrics: Dict):
        """Monitor system metrics during execution"""
        while True:
            try:
                metrics['cpu_usage'].append(psutil.cpu_percent())
                metrics['memory_usage'].append(psutil.virtual_memory().percent)
                time.sleep(0.1)
            except:
                break
                
    def _analyze_performance(self, metrics: Dict) -> float:
        """Analyze performance metrics"""
        try:
            cpu_score = 1.0 - (sum(metrics['cpu_usage']) / len(metrics['cpu_usage']) / 100)
            memory_score = 1.0 - (sum(metrics['memory_usage']) / len(metrics['memory_usage']) / 100)
            time_score = self._calculate_time_score(metrics['execution_time'])
            
            return (cpu_score + memory_score + time_score) / 3
            
        except Exception as e:
            self.logger.error(f"Performance analysis failed: {str(e)}")
            return 0.5
            
    def _reduce_resource_usage(self):
        """Reduce resource usage when system is under heavy load"""
        if self.system_mode == 'performance':
            self.system_mode = 'balanced'
        elif self.system_mode == 'balanced':
            self.system_mode = 'memory_saving'
            
    def _increase_resource_usage(self):
        """Increase resource usage when system has capacity"""
        if self.system_mode == 'memory_saving':
            self.system_mode = 'balanced'
        elif self.system_mode == 'balanced':
            self.system_mode = 'performance'
            
    def _calculate_time_score(self, execution_time: float) -> float:
        """Calculate time-based performance score"""
        try:
            baseline = self.config.get('baseline_execution_time', 1.0)
            ratio = baseline / execution_time
            return min(1.0, max(0.0, ratio))
        except:
            return 0.5
            
    def _calculate_optimal_workers(self, resources: Dict = None) -> int:
        """Calculate optimal number of worker threads"""
        if resources:
            return min(
                self.config['max_parallel_tasks'],
                resources.get('max_workers', 4)
            )
        return self.config['max_parallel_tasks']