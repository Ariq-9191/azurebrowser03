import logging
from .performance_optimizer import PerformanceOptimizer
from .resource_manager import ResourceManager
from .performance_profiler import PerformanceProfiler
from .ai_brain import AIBrain

class YouTubeAutomationEngine:
    def __init__(self, config=None):
        self.logger = logging.getLogger(__name__)
        self.performance_optimizer = PerformanceOptimizer()
        self.resource_manager = ResourceManager()
        self.performance_profiler = PerformanceProfiler()
        self.ai_brain = AIBrain()
        self.config = config or {}
    
    @performance_profiler.measure_execution_time
    def run_optimized(self, tasks):
        """
        Run tasks with optimization and AI-driven decision making
        """
        try:
            # Resource allocation
            resources = self.resource_manager.allocate_resources(len(tasks))
            
            # AI analysis for task optimization
            optimized_tasks = self.ai_brain.optimize_tasks(tasks)
            
            # Parallel execution with performance monitoring
            results = self.performance_optimizer.parallel_execution(
                optimized_tasks,
                resources=resources,
                monitoring=True
            )
            
            # Performance analysis and adaptation
            self.performance_optimizer.analyze_and_adapt(results)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Automation engine error: {str(e)}")
            raise

    def add_task(self, task):
        """Add new task to queue"""
        return self.resource_manager.queue_task(task)
        
    def get_performance_metrics(self):
        """Get current performance metrics"""
        return self.performance_profiler.get_metrics()