import logging
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
import time
import numpy as np
from datetime import datetime
import threading
from queue import Queue
import sqlite3

class AIMonitor:
	def __init__(self):
		self.logger = logging.getLogger(__name__)
		self.stats_file = Path(__file__).parent.parent.parent / 'data' / 'ai_stats.json'
		self.detection_history = []
		self.performance_metrics = {
			'success_rate': [],
			'detection_rate': [],
			'interaction_quality': []
		}
		self.monitoring_queue = Queue()
		self.monitoring_thread = None
		self.is_monitoring = False
		self.anomaly_threshold = 0.8
		self.monitor_db = self._initialize_monitor_db()
		self._load_stats()
		
	def _initialize_monitor_db(self) -> sqlite3.Connection:
		"""Initialize monitoring database"""
		db_path = Path(__file__).parent.parent.parent / 'data' / 'monitoring.db'
		db_path.parent.mkdir(exist_ok=True)
		conn = sqlite3.connect(str(db_path))
		
		c = conn.cursor()
		c.execute('''CREATE TABLE IF NOT EXISTS performance_metrics
					(id INTEGER PRIMARY KEY, timestamp TEXT,
					 metric_type TEXT, value REAL,
					 context TEXT)''')
					 
		c.execute('''CREATE TABLE IF NOT EXISTS anomalies
					(id INTEGER PRIMARY KEY, timestamp TEXT,
					 anomaly_type TEXT, severity REAL,
					 details TEXT)''')
					 
		conn.commit()
		return conn
		
	def __del__(self):
		"""Cleanup on deletion"""
		self.stop_monitoring()
		self._save_stats()
		
	def _initialize_monitoring(self):
		"""Initialize background monitoring"""
		self.is_monitoring = True
		self.monitoring_thread = threading.Thread(
			target=self._monitor_loop,
			daemon=True
		)
		self.monitoring_thread.start()
		
	def stop_monitoring(self):
		"""Stop monitoring thread"""
		self.is_monitoring = False
		if self.monitoring_thread:
			self.monitoring_thread.join(timeout=1)
			
	def _monitoring_loop(self):
		"""Main monitoring loop"""
		while self.is_monitoring:
			try:
				# Process monitoring queue
				while not self.monitoring_queue.empty():
					metric = self.monitoring_queue.get()
					self._process_metric(metric)
					
				# Analyze patterns
				self._analyze_patterns()
				
				# Check for anomalies
				self._check_anomalies()
				
				# Save stats periodically
				self._save_stats()
				
				time.sleep(5)  # Monitoring interval
				
			except Exception as e:
				self.logger.error(f"Monitoring error: {str(e)}")
				time.sleep(5)
				
	def _process_metric(self, metric: Dict):
		"""Process and store monitoring metric"""
		try:
			c = self.monitor_db.cursor()
			c.execute('''INSERT INTO performance_metrics
						(timestamp, metric_type, value, context)
						VALUES (?, ?, ?, ?)''',
						(datetime.now().isoformat(),
						 metric['type'],
						 metric['value'],
						 json.dumps(metric.get('context', {}))))
						 
			self.monitor_db.commit()
			
			# Update in-memory metrics
			if metric['type'] in self.performance_metrics:
				self.performance_metrics[metric['type']].append(metric['value'])
				
		except Exception as e:
			self.logger.error(f"Metric processing failed: {str(e)}")
			
	def _analyze_patterns(self):
		"""Analyze performance patterns"""
		try:
			for metric_type, values in self.performance_metrics.items():
				if len(values) >= 10:  # Minimum sample size
					pattern = self._detect_pattern(values[-10:])
					if pattern['confidence'] > 0.8:
						self._record_pattern(metric_type, pattern)
						
		except Exception as e:
			self.logger.error(f"Pattern analysis failed: {str(e)}")
			
	def _check_anomalies(self):
		"""Check for performance anomalies"""
		try:
			for metric_type, values in self.performance_metrics.items():
				if len(values) >= 20:  # Minimum sample size
					recent_values = values[-20:]
					mean = np.mean(recent_values)
					std = np.std(recent_values)
					
					# Check for anomalies
					latest = values[-1]
					z_score = abs(latest - mean) / std
					
					if z_score > 3:  # 3 sigma rule
						self._record_anomaly(metric_type, latest, z_score)
						
		except Exception as e:
			self.logger.error(f"Anomaly check failed: {str(e)}")
			
	def _detect_pattern(self, values: List[float]) -> Dict:
		"""Detect patterns in metric values"""
		try:
			# Calculate trend
			x = np.arange(len(values))
			z = np.polyfit(x, values, 1)
			slope = z[0]
			
			# Calculate periodicity
			fft = np.fft.fft(values)
			freq = np.fft.fftfreq(len(values))
			peak_freq = freq[np.argmax(np.abs(fft))]
			
			return {
				'trend': 'increasing' if slope > 0 else 'decreasing',
				'slope': float(slope),
				'periodicity': float(peak_freq),
				'confidence': float(np.corrcoef(x, values)[0,1])
			}
			
		except Exception as e:
			self.logger.error(f"Pattern detection failed: {str(e)}")
			return {'confidence': 0.0}
			
	def _record_pattern(self, metric_type: str, pattern: Dict):
		"""Record detected pattern"""
		try:
			c = self.monitor_db.cursor()
			c.execute('''INSERT INTO performance_metrics
						(timestamp, metric_type, value, context)
						VALUES (?, ?, ?, ?)''',
						(datetime.now().isoformat(),
						 f"{metric_type}_pattern",
						 pattern['confidence'],
						 json.dumps(pattern)))
						 
			self.monitor_db.commit()
			
		except Exception as e:
			self.logger.error(f"Pattern recording failed: {str(e)}")
			
	def _record_anomaly(self, metric_type: str, value: float, severity: float):
		"""Record detected anomaly"""
		try:
			c = self.monitor_db.cursor()
			c.execute('''INSERT INTO anomalies
						(timestamp, anomaly_type, severity, details)
						VALUES (?, ?, ?, ?)''',
						(datetime.now().isoformat(),
						 metric_type,
						 severity,
						 json.dumps({
							 'value': value,
							 'threshold': self.anomaly_threshold
						 })))
						 
			self.monitor_db.commit()
			
		except Exception as e:
			self.logger.error(f"Anomaly recording failed: {str(e)}")
				
	def _process_monitoring_event(self, event: Dict):
		"""Process monitoring event"""
		try:
			event_type = event.get('type')
			if event_type == 'detection':
				self.record_detection(event.get('details', {}))
			elif event_type == 'performance':
				self.record_performance(event.get('metrics', {}))
		except Exception as e:
			self.logger.error(f"Event processing failed: {str(e)}")
		
	def record_detection(self, details: Dict):
		"""Record bot detection incident with enhanced tracking"""
		try:
			incident = {
				'timestamp': time.time(),
				'proxy': details.get('proxy'),
				'fingerprint': details.get('fingerprint'),
				'interaction_pattern': details.get('pattern'),
				'url': details.get('url'),
				'severity': self._calculate_incident_severity(details)
			}
			
			self.detection_history.append(incident)
			self._trim_history()
			self._analyze_detection_pattern()
			self._save_stats()
			
		except Exception as e:
			self.logger.error(f"Failed to record detection: {str(e)}")
			
	def _calculate_incident_severity(self, details: Dict) -> float:
		"""Calculate incident severity"""
		try:
			base_severity = 0.5
			
			# Adjust for repeated detections
			if self._check_repeated_detection(details):
				base_severity += 0.2
				
			# Adjust for pattern type
			if details.get('pattern') == 'automated':
				base_severity += 0.3
				
			return min(1.0, base_severity)
		except Exception as e:
			self.logger.error(f"Severity calculation failed: {str(e)}")
			return 0.5
			
	def _check_repeated_detection(self, details: Dict) -> bool:
		"""Check for repeated detections"""
		try:
			recent = [d for d in self.detection_history[-10:]
					 if d.get('proxy') == details.get('proxy') or
						d.get('fingerprint') == details.get('fingerprint')]
			return len(recent) > 2
		except Exception:
			return False
		
	def record_performance(self, metrics: Dict):
		"""Record performance metrics"""
		for key, value in metrics.items():
			if key in self.performance_metrics:
				self.performance_metrics[key].append(value)
		
		self._save_stats()
		
	def get_detection_rate(self) -> float:
		"""Calculate current detection rate with error handling"""
		try:
			recent = self.detection_history[-100:] if len(self.detection_history) > 100 else self.detection_history
			if not recent:
				return 0.0
				
			weighted_detections = sum(d.get('severity', 1.0) for d in recent)
			return weighted_detections / len(recent)
			
		except Exception as e:
			self.logger.error(f"Detection rate calculation failed: {str(e)}")
			return 0.0
		
	def get_improvement_suggestions(self) -> List[str]:
		"""Generate improvement suggestions with enhanced analysis"""
		try:
			suggestions = []
			detection_rate = self.get_detection_rate()
			
			# Analyze detection patterns
			if detection_rate > 0.1:
				patterns = self._analyze_detection_pattern()
				
				if patterns.get('proxy_related', 0) > 0.5:
					suggestions.append({
						'type': 'proxy',
						'message': "Consider rotating proxies more frequently",
						'priority': 'high'
					})
					
				if patterns.get('fingerprint_related', 0) > 0.5:
					suggestions.append({
						'type': 'fingerprint',
						'message': "Increase fingerprint randomization",
						'priority': 'high'
					})
					
				if patterns.get('behavior_related', 0) > 0.5:
					suggestions.append({
						'type': 'behavior',
						'message': "Adjust interaction patterns for more natural behavior",
						'priority': 'medium'
					})
					
			# Analyze performance trends
			if self.performance_metrics['success_rate']:
				trend = np.mean(self.performance_metrics['success_rate'][-10:])
				if trend < 0.7:
					suggestions.append({
						'type': 'performance',
						'message': "Success rate dropping, consider adjusting browser parameters",
						'priority': 'high'
					})
					
			return sorted(suggestions, key=lambda x: x['priority'] == 'high', reverse=True)
			
		except Exception as e:
			self.logger.error(f"Failed to generate suggestions: {str(e)}")
			return []
		
	def _analyze_detection_pattern(self) -> Dict:
		"""Analyze detection patterns"""
		if not self.detection_history:
			return {}
			
		recent = self.detection_history[-50:]
		patterns = {
			'proxy_related': len([x for x in recent if 'proxy' in x.get('details', {})]) / len(recent),
			'fingerprint_related': len([x for x in recent if 'fingerprint' in x.get('details', {})]) / len(recent),
			'behavior_related': len([x for x in recent if 'behavior' in x.get('details', {})]) / len(recent)
		}
		
		return patterns
		
	def _load_stats(self):
		"""Load historical stats"""
		try:
			if self.stats_file.exists():
				with open(self.stats_file) as f:
					data = json.load(f)
					self.detection_history = data.get('detection_history', [])
					self.performance_metrics = data.get('performance_metrics', self.performance_metrics)
		except Exception as e:
			self.logger.error(f"Failed to load stats: {str(e)}")
			
	def _save_stats(self):
		"""Save current stats"""
		try:
			self.stats_file.parent.mkdir(parents=True, exist_ok=True)
			with open(self.stats_file, 'w') as f:
				json.dump({
					'detection_history': self.detection_history,
					'performance_metrics': self.performance_metrics,
					'last_update': datetime.now().isoformat()
				}, f, indent=4)
		except Exception as e:
			self.logger.error(f"Failed to save stats: {str(e)}")