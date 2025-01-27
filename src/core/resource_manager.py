# src/core/resource_manager.py
import logging
import psutil
from queue import Queue, PriorityQueue
from typing import Dict, Any, List, Tuple, Optional
from threading import Lock
import threading
from concurrent.futures import ThreadPoolExecutor

class ResourceError(Exception):
    """Custom exception for resource-related errors"""
    pass
import time
import json
from pathlib import Path
import numpy as np
from .ai_brain import AIBrain

class ResourceManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.task_queue = PriorityQueue()
        self.resource_lock = Lock()
        self.ai_brain = AIBrain()
        self.resource_history = []
        self.resource_limits = self._load_resource_limits()
        self.monitoring_interval = 5  # seconds
        self.last_optimization = time.time()
        self.monitoring_thread = None
        self.is_monitoring = False
        self.system_specs = self._get_system_specs()
        self.pause_task_acceptance = False
        self.resource_thresholds = {
            'cpu_warning': 80,
            'memory_warning': 85,
            'cpu_critical': 90,
            'memory_critical': 95
        }
        self._start_resource_monitoring()
        
    def __del__(self):
        self.stop_monitoring()
        
    def _start_resource_monitoring(self):
        """Start background resource monitoring"""
        self.is_monitoring = True
        self.monitoring_thread = threading.Thread(
            target=self._monitor_resources,
            daemon=True
        )
        self.monitoring_thread.start()
        
    def stop_monitoring(self):
        """Stop resource monitoring"""
        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=1)
            
    def _monitor_resources(self):
        """Background resource monitoring"""
        while self.is_monitoring:
            try:
                metrics = self._get_system_metrics()
                self._check_resource_thresholds(metrics)
                time.sleep(self.monitoring_interval)
            except Exception as e:
                self.logger.error(f"Resource monitoring error: {str(e)}")
                
    def _check_resource_thresholds(self, metrics: Dict[str, float]):
        """Check if resources exceed critical thresholds"""
        try:
            critical_thresholds = {
                'cpu_percent': 90.0,
                'memory_percent': 85.0,
                'disk_percent': 90.0
            }
            
            for metric, value in metrics.items():
                if metric in critical_thresholds and value > critical_thresholds[metric]:
                    self.logger.warning(f"Critical resource usage: {metric} at {value}%")
                    self._handle_resource_pressure(metric, value)
        except Exception as e:
            self.logger.error(f"Threshold check failed: {str(e)}")
            
    def _handle_resource_pressure(self, resource: str, value: float):
        """Handle high resource pressure"""
        try:
            with self.resource_lock:
                # Temporarily reduce resource limits
                self.resource_limits[f"{resource}_limit"] *= 0.8
                
                # Cancel low priority tasks if needed
                self._cancel_low_priority_tasks()
                
        except Exception as e:
            self.logger.error(f"Failed to handle resource pressure: {str(e)}")
            
    def _cancel_low_priority_tasks(self):
        """Cancel low priority tasks under pressure"""
        try:
            temp_queue = PriorityQueue()
            while not self.task_queue.empty():
                priority, task = self.task_queue.get()
                if priority > 30:  # Keep only high priority tasks
                    temp_queue.put((priority, task))
            self.task_queue = temp_queue
        except Exception as e:
            self.logger.error(f"Task cancellation failed: {str(e)}")
        
    def _load_resource_limits(self) -> Dict:
        """Load resource limits from config"""
        try:
            config_path = Path(__file__).parent.parent.parent / 'config' / 'resource_config.json'
            if config_path.exists():
                with open(config_path) as f:
                    return json.load(f)
            return self._get_default_limits()
        except Exception as e:
            self.logger.error(f"Failed to load resource limits: {str(e)}")
            return self._get_default_limits()
            
    def _get_default_limits(self) -> Dict:
        """Get default resource limits"""
        return {
            'cpu_percent': 80.0,
            'memory_percent': 75.0,
            'max_tasks': 100,
            'io_threshold': 70.0,
            'network_threshold': 80.0,
            'gpu_memory_percent': 70.0
        }
        
    def allocate_resources(self, task_count: int) -> Dict[str, Any]:
        """Allocate system resources with AI optimization"""
        try:
            with self.resource_lock:
                system_metrics = self._get_system_metrics()
                if not system_metrics:
                    raise ResourceError("Failed to get system metrics")
                    
                # Check resource availability
                if not self._check_resource_availability():
                    raise ResourceError("Insufficient resources available")
                    
                allocation = self._optimize_resource_allocation(
                    system_metrics,
                    task_count
                )
                
                self._record_allocation(allocation)
                return allocation
                
        except ResourceError as e:
            self.logger.error(f"Resource allocation failed: {str(e)}")
            return self._get_fallback_allocation(task_count)
        except Exception as e:
            self.logger.error(f"Unexpected error in resource allocation: {str(e)}")
            return self._get_fallback_allocation(task_count)
            
    def _get_system_specs(self) -> Dict:
        """Get system specifications"""
        return {
            'cpu_cores': psutil.cpu_count(),
            'ram': psutil.virtual_memory().total / (1024 * 1024 * 1024),  # GB
            'cpu_freq': psutil.cpu_freq().max if psutil.cpu_freq() else 0,
            'has_gpu': self._check_gpu_availability()
        }

    def get_optimal_browser_count(self) -> int:
        """Calculate optimal number of browser instances"""
        ram_gb = self.system_specs['ram']
        cpu_cores = self.system_specs['cpu_cores']
        
        # Base calculations
        ram_based = int(ram_gb * 5)  # 5 instances per GB
        cpu_based = cpu_cores * 10   # 10 instances per core
        
        # Take the lower value
        base_count = min(ram_based, cpu_based)
        
        # Apply safety factor
        return int(base_count * 0.8)  # 80% of theoretical maximum

    def _handle_critical_load(self):
        """Handle critical system load"""
        with self.resource_lock:
            self.logger.warning("Critical system load detected!")
            # Stop accepting new tasks
            self.pause_task_acceptance = True
            # Reduce active browser count
            self.reduce_active_browsers(reduction_percent=50)
            
    def _handle_high_load(self):
        """Handle high system load"""
        with self.resource_lock:
            self.logger.info("High system load detected")
            # Reduce new task acceptance
            self.pause_task_acceptance = True
            # Reduce active browser count
            self.reduce_active_browsers(reduction_percent=25)
            
    def _check_gpu_availability(self) -> bool:
        """Check for GPU availability"""
        try:
            import tensorflow as tf
            return len(tf.config.list_physical_devices('GPU')) > 0
        except:
            return False
            
    def get_resource_report(self) -> Dict:
        """Generate resource usage report"""
        return {
            'system_specs': self.system_specs,
            'current_usage': {
                'cpu': psutil.cpu_percent(),
                'memory': psutil.virtual_memory().percent
            },
            'optimal_browser_count': self.get_optimal_browser_count(),
            'resource_history': self.resource_history[-10:]  # Last 10 records
        }

    def reduce_active_browsers(self, reduction_percent: int):
        """Reduce active browser count by percentage"""
        try:
            with self.resource_lock:
                current_tasks = list(self.task_queue.queue)
                reduction_count = int(len(current_tasks) * (reduction_percent / 100))
                
                # Keep high priority tasks
                current_tasks.sort(key=lambda x: x[0], reverse=True)
                self.task_queue = PriorityQueue()
                
                # Re-add tasks after reduction
                for i, task in enumerate(current_tasks):
                    if i >= reduction_count:
                        self.task_queue.put(task)
                        
                self.logger.info(f"Reduced active browsers by {reduction_percent}%")
        except Exception as e:
            self.logger.error(f"Failed to reduce browsers: {str(e)}")

    def _get_system_metrics(self) -> Dict[str, float]:
        """Get comprehensive system metrics"""
        try:
            cpu_count = psutil.cpu_count()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            metrics = {
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_available': memory.available,
                'memory_percent': memory.percent,
                'disk_percent': disk.percent,
                'cpu_count': cpu_count,
                'load_average': psutil.getloadavg()[0] / cpu_count * 100
            }
            
            # Add GPU metrics if available
            gpu_metrics = self._get_gpu_metrics()
            if gpu_metrics:
                metrics.update(gpu_metrics)
                
            return metrics
        except Exception as e:
            self.logger.error(f"Error getting system metrics: {str(e)}")
            return {}
            
    def _optimize_resource_allocation(self, metrics: Dict, task_count: int) -> Dict[str, Any]:
        """Optimize resource allocation using AI"""
        try:
            # Calculate base allocation
            cpu_available = 100 - metrics.get('cpu_percent', 0)
            memory_available = 100 - metrics.get('memory_percent', 0)
            
            # Get AI recommendations
            optimization_data = {
                'metrics': metrics,
                'task_count': task_count,
                'history': self.resource_history[-50:] if self.resource_history else []
            }
            
            ai_recommendations = self.ai_brain.analyze_resource_patterns(optimization_data)
            
            # Calculate optimal worker count
            max_workers = min(
                metrics.get('cpu_count', 1) * 2,
                int(cpu_available / 10),
                task_count,
                int(ai_recommendations.get('recommended_workers', task_count))
            )
            
            return {
                'max_workers': max_workers,
                'memory_allocation': memory_available * 0.8,  # 80% of available
                'cpu_allocation': cpu_available * 0.8,
                'priority_level': ai_recommendations.get('priority_level', 'medium')
            }
            
        except Exception as e:
            self.logger.error(f"Resource optimization failed: {str(e)}")
            return self._get_fallback_allocation(task_count)
            
    def queue_task(self, task: Dict) -> bool:
        """Queue task with priority and resource checks"""
        try:
            if self.task_queue.qsize() < self.resource_limits['max_tasks']:
                if self._check_resource_availability():
                    priority = self._calculate_task_priority(task)
                    self.task_queue.put((priority, task))
                    
                    # Store task metrics for learning
                    self._record_task_metrics(task, priority)
                    return True
            return False
        except Exception as e:
            self.logger.error(f"Error queuing task: {str(e)}")
            return False
            
    def _calculate_task_priority(self, task: Dict) -> int:
        """Calculate task priority using AI insights"""
        try:
            task_features = {
                'type': task.get('type', 'default'),
                'size': task.get('size', 1),
                'deadline': task.get('deadline', float('inf')),
                'resource_requirements': task.get('resources', {})
            }
            
            priority_score = self.ai_brain.analyze_task_priority(task_features)
            return int(priority_score * 100)  # Convert to integer priority
        except Exception as e:
            self.logger.error(f"Priority calculation failed: {str(e)}")
            return 50  # Default medium priority
            
    def _record_task_metrics(self, task: Dict, priority: int):
        """Record task metrics for learning"""
        metrics = {
            'task_type': task.get('type', 'unknown'),
            'priority': priority,
            'timestamp': time.time(),
            'resource_state': self._get_system_metrics()
        }
        self.resource_history.append(metrics)
        
        # Trim history if too long
        if len(self.resource_history) > 1000:
            self.resource_history = self.resource_history[-1000:]
            
    def _get_gpu_metrics(self) -> Dict[str, float]:
        """Get GPU metrics if available"""
        try:
            import pynvml
            pynvml.nvmlInit()
            metrics = {}
            
            device_count = pynvml.nvmlDeviceGetCount()
            for i in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                util = pynvml.nvmlDeviceGetUtilizationRates(handle)
                
                metrics[f'gpu_{i}_memory_used'] = info.used / info.total * 100
                metrics[f'gpu_{i}_utilization'] = util.gpu
                
            return metrics
        except ImportError:
            return {}  # GPU monitoring not available
        except Exception as e:
            self.logger.error(f"GPU metrics collection failed: {str(e)}")
            return {}
            
    def _get_fallback_allocation(self, task_count: int) -> Dict[str, Any]:
        """Get fallback resource allocation"""
        return {
            'max_workers': min(4, task_count),
            'memory_allocation': 50.0,
            'cpu_allocation': 50.0,
            'priority_level': 'medium'
        }
            
    def _check_resource_availability(self) -> bool:
        """Check if system resources are available"""
        try:
            metrics = self._get_system_metrics()
            
            return all([
                metrics.get('cpu_percent', 100) < self.resource_limits['cpu_percent'],
                metrics.get('memory_percent', 100) < self.resource_limits['memory_percent'],
                metrics.get('disk_percent', 100) < self.resource_limits.get('io_threshold', 70)
            ])
        except Exception as e:
            self.logger.error(f"Error checking resources: {str(e)}")
            return False
    
    def get_queued_tasks(self) -> int:
        """Get number of tasks in queue"""
        return self.task_queue.qsize()