# src/core/performance_profiler.py
import logging
import time
from functools import wraps
from typing import Dict, List, Callable, Any, Optional
from collections import defaultdict
import json
from pathlib import Path
import numpy as np
from datetime import datetime
import sqlite3
import weakref
import gc

class PerformanceProfiler:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._metrics = defaultdict(list)  # Use weak references for metrics
        self._execution_history = []
        self.profile_db = self._initialize_profile_db()
        self.learning_threshold = 100
        self.pattern_cache = {}
        self._load_config()
        self._cleanup_interval = 1000  # Cleanup after 1000 records
        self._last_cleanup = time.time()
        
    def __del__(self):
        """Cleanup resources on deletion"""
        try:
            if hasattr(self, 'profile_db'):
                self.profile_db.close()
        except Exception as e:
            self.logger.error(f"Cleanup failed: {str(e)}")
            
    @property
    def metrics(self):
        """Safe access to metrics with memory management"""
        self._cleanup_old_metrics()
        return self._metrics
        
    def _cleanup_old_metrics(self):
        """Clean up old metrics to manage memory"""
        try:
            current_time = time.time()
            if current_time - self._last_cleanup > 3600:  # Cleanup every hour
                for func_name in list(self._metrics.keys()):
                    if len(self._metrics[func_name]) > self._cleanup_interval:
                        self._metrics[func_name] = self._metrics[func_name][-self._cleanup_interval:]
                gc.collect()  # Force garbage collection
                self._last_cleanup = current_time
        except Exception as e:
            self.logger.error(f"Metrics cleanup failed: {str(e)}")
        
    def _initialize_profile_db(self) -> sqlite3.Connection:
        """Initialize SQLite database for profiling data"""
        db_path = Path(__file__).parent.parent.parent / 'data' / 'profiling.db'
        db_path.parent.mkdir(exist_ok=True)
        conn = sqlite3.connect(str(db_path))
        c = conn.cursor()
        
        c.execute('''CREATE TABLE IF NOT EXISTS execution_metrics
                    (id INTEGER PRIMARY KEY, function_name TEXT,
                     execution_time REAL, timestamp TEXT,
                     context TEXT)''')
                     
        c.execute('''CREATE TABLE IF NOT EXISTS performance_patterns
                    (id INTEGER PRIMARY KEY, pattern_type TEXT,
                     pattern_data TEXT, confidence REAL)''')
                     
        conn.commit()
        return conn
        
    def _load_config(self):
        """Load profiler configuration"""
        try:
            config_path = Path(__file__).parent.parent.parent / 'config' / 'profiler_config.json'
            if config_path.exists():
                with open(config_path) as f:
                    self.config = json.load(f)
            else:
                self.config = self._create_default_config()
        except Exception as e:
            self.logger.error(f"Failed to load config: {str(e)}")
            self.config = self._create_default_config()
            
    def _create_default_config(self) -> Dict:
        """Create default profiler configuration"""
        return {
            'sampling_rate': 0.1,
            'history_limit': 1000,
            'pattern_confidence_threshold': 0.8,
            'learning_batch_size': 50,
            'metrics_aggregation_interval': 300  # 5 minutes
        }
        
    def measure_execution_time(self, func: Callable) -> Callable:
        """Enhanced decorator with error recovery"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            context = self._capture_execution_context()
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                self._record_execution_metric(
                    func.__name__,
                    execution_time,
                    context,
                    success=True
                )
                
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                self._record_execution_metric(
                    func.__name__,
                    execution_time,
                    context,
                    success=False,
                    error=str(e)
                )
                self.logger.error(f"Error in {func.__name__}: {str(e)}")
                raise
        return wrapper
        
    def _capture_execution_context(self) -> Dict:
        """Capture execution context for analysis"""
        return {
            'timestamp': datetime.now().isoformat(),
            'system_load': self._get_system_load(),
            'memory_usage': self._get_memory_usage()
        }
        
    def _record_execution_metric(self, func_name: str, execution_time: float, 
                               context: Dict, success: bool, error: str = None):
        """Record execution metric with error handling"""
        try:
            self._metrics[func_name].append(execution_time)
            
            # Store in database with error information
            c = self.profile_db.cursor()
            c.execute('''INSERT INTO execution_metrics
                        (function_name, execution_time, timestamp, context, success, error)
                        VALUES (?, ?, ?, ?, ?, ?)''',
                        (func_name, execution_time,
                         context['timestamp'],
                         json.dumps(context),
                         int(success),
                         error))
                         
            self.profile_db.commit()
            
        except sqlite3.Error as e:
            self.logger.error(f"Database error: {str(e)}")
            self._handle_db_error()
        except Exception as e:
            self.logger.error(f"Metric recording failed: {str(e)}")
            
    def _handle_db_error(self):
        """Handle database errors"""
        try:
            self.profile_db.rollback()
            # Attempt to recreate tables if they're corrupted
            self._initialize_profile_db()
        except Exception as e:
            self.logger.error(f"Database recovery failed: {str(e)}")
            
    def _analyze_performance_patterns(self, func_name: str):
        """Analyze performance patterns for learning"""
        try:
            metrics_data = np.array(self.metrics[func_name])
            
            patterns = {
                'trend': self._calculate_trend(metrics_data),
                'variability': self._calculate_variability(metrics_data),
                'anomalies': self._detect_anomalies(metrics_data)
            }
            
            # Store patterns if confidence is high enough
            if patterns['trend']['confidence'] > self.config['pattern_confidence_threshold']:
                self._store_pattern(func_name, 'trend', patterns['trend'])
                
        except Exception as e:
            self.logger.error(f"Pattern analysis failed: {str(e)}")
            
    def _calculate_trend(self, data: np.ndarray) -> Dict:
        """Calculate performance trend"""
        try:
            x = np.arange(len(data))
            z = np.polyfit(x, data, 1)
            slope = z[0]
            
            return {
                'slope': slope,
                'direction': 'improving' if slope < 0 else 'degrading',
                'confidence': self._calculate_trend_confidence(data, z)
            }
        except:
            return {'slope': 0, 'direction': 'stable', 'confidence': 0}
            
    def _calculate_variability(self, data: np.ndarray) -> Dict:
        """Calculate performance variability"""
        try:
            return {
                'std_dev': float(np.std(data)),
                'cv': float(np.std(data) / np.mean(data)),
                'range': float(np.ptp(data))
            }
        except:
            return {'std_dev': 0, 'cv': 0, 'range': 0}
            
    def _detect_anomalies(self, data: np.ndarray) -> Dict:
        """Detect performance anomalies"""
        try:
            mean = np.mean(data)
            std = np.std(data)
            threshold = 3
            
            anomalies = data[abs(data - mean) > threshold * std]
            return {
                'count': len(anomalies),
                'indices': list(np.where(abs(data - mean) > threshold * std)[0]),
                'values': list(anomalies)
            }
        except:
            return {'count': 0, 'indices': [], 'values': []}
            
    def _store_pattern(self, func_name: str, pattern_type: str, pattern_data: Dict):
        """Store performance pattern in database"""
        c = self.profile_db.cursor()
        c.execute('''INSERT INTO performance_patterns
                    (pattern_type, pattern_data, confidence)
                    VALUES (?, ?, ?)''',
                    (pattern_type,
                     json.dumps(pattern_data),
                     pattern_data.get('confidence', 0)))
        self.profile_db.commit()
        
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        report = {
            'metrics': self.get_metrics(),
            'patterns': self._get_performance_patterns(),
            'anomalies': self._get_anomaly_summary(),
            'recommendations': self._generate_recommendations()
        }
        return report
        
    def _get_performance_patterns(self) -> Dict:
        """Get analyzed performance patterns"""
        patterns = {}
        c = self.profile_db.cursor()
        for row in c.execute('SELECT pattern_type, pattern_data FROM performance_patterns'):
            pattern_type, pattern_data = row
            if pattern_type not in patterns:
                patterns[pattern_type] = []
            patterns[pattern_type].append(json.loads(pattern_data))
        return patterns
        
    def _generate_recommendations(self) -> List[Dict]:
        """Generate performance improvement recommendations"""
        recommendations = []
        patterns = self._get_performance_patterns()
        
        for func_name, metrics in self.metrics.items():
            if len(metrics) >= self.learning_threshold:
                trend = self._calculate_trend(np.array(metrics))
                if trend['direction'] == 'degrading':
                    recommendations.append({
                        'function': func_name,
                        'issue': 'Performance degradation detected',
                        'suggestion': 'Consider optimization or caching'
                    })
                    
        return recommendations
        
    def _get_system_load(self) -> float:
        """Get current system load"""
        try:
            return [x / 100 for x in time.getloadavg()][0]
        except:
            return 0.0
            
    def _get_memory_usage(self) -> Dict:
        """Get current memory usage"""
        try:
            import psutil
            mem = psutil.virtual_memory()
            return {
                'total': mem.total,
                'available': mem.available,
                'percent': mem.percent
            }
        except:
            return {'total': 0, 'available': 0, 'percent': 0}
