# src/core/resource_manager.py
import logging
import psutil
from queue import Queue
from typing import Dict, Any
from threading import Lock

class ResourceManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.task_queue = Queue()
        self.resource_lock = Lock()
        self.resource_limits = {
            'cpu_percent': 80.0,
            'memory_percent': 75.0,
            'max_tasks': 100
        }
        
    def allocate_resources(self, task_count: int) -> Dict[str, Any]:
        """Allocate system resources based on task requirements"""
        with self.resource_lock:
            cpu_count = psutil.cpu_count()
            memory = psutil.virtual_memory()
            
            # Calculate optimal worker count
            max_workers = min(
                cpu_count * 2,
                int((100 - psutil.cpu_percent()) / 10),
                task_count
            )
            
            return {
                'max_workers': max_workers,
                'memory_available': memory.available,
                'cpu_available': cpu_count
            }
    
    def queue_task(self, task: Dict) -> bool:
        """Add task to queue if resources allow"""
        try:
            if self.task_queue.qsize() < self.resource_limits['max_tasks']:
                if self._check_resource_availability():
                    self.task_queue.put(task)
                    return True
            return False
        except Exception as e:
            self.logger.error(f"Error queuing task: {str(e)}")
            return False
    
    def _check_resource_availability(self) -> bool:
        """Check if system resources are available"""
        try:
            cpu_percent = psutil.cpu_percent()
            memory_percent = psutil.virtual_memory().percent
            
            return (cpu_percent < self.resource_limits['cpu_percent'] and 
                    memory_percent < self.resource_limits['memory_percent'])
        except Exception as e:
            self.logger.error(f"Error checking resources: {str(e)}")
            return False
    
    def get_queued_tasks(self) -> int:
        """Get number of tasks in queue"""
        return self.task_queue.qsize()