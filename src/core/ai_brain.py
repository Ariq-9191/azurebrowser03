import logging
import numpy as np
from typing import List, Dict, Any
import tensorflow as tf
from .advanced_ai_model import load_model
import json
from pathlib import Path
import time
import random

class AIBrain:
	def __init__(self):
		self.logger = logging.getLogger(__name__)
		self.model = None
		self.behavior_model = None
		self.interaction_history = []
		self.load_models()
		self.behavior_params = self._load_behavior_params()
		self.bot_detection_thresholds = {
			'interaction_consistency': 0.95,  # Too consistent = bot-like
			'timing_regularity': 0.90,
			'movement_precision': 0.95,
			'scroll_pattern_similarity': 0.90
		}
		self.detection_history = []
		
	def load_models(self):
		"""Load AI models"""
		try:
			self.model = load_model()
			self.behavior_model = self._load_behavior_model()
		except Exception as e:
			self.logger.error(f"Failed to load AI model: {str(e)}")
			
	def optimize_tasks(self, tasks: List[Dict]) -> List[Dict]:
		"""Optimize task execution order and parameters"""
		try:
			if not self.model:
				return tasks
				
			optimized_tasks = []
			for task in tasks:
				task_features = self._extract_features(task)
				optimization_score = self._predict_optimization(task_features)
				
				optimized_task = self._apply_optimization(task, optimization_score)
				optimized_tasks.append(optimized_task)
			
			# Sort by optimization potential
			optimized_tasks.sort(key=lambda x: x.get('optimization_score', 0), reverse=True)
			return optimized_tasks
			
		except Exception as e:
			self.logger.error(f"Task optimization failed: {str(e)}")
			return tasks
			
	def get_behavior_parameters(self) -> Dict:
		"""Enhanced behavior parameters with anti-detection measures"""
		try:
			if len(self.interaction_history) > 0:
				recent_patterns = self._analyze_recent_patterns()
				base_params = {
					'interaction_frequency': recent_patterns['avg_frequency'],
					'scroll_speed': recent_patterns['avg_scroll_speed'],
					'typing_speed': recent_patterns['avg_typing_speed'],
					'pause_duration': recent_patterns['avg_pause'],
					'movement_pattern': recent_patterns['movement_pattern']
				}
				
				# Analyze recent detection history
				if self.detection_history:
					recent_risks = [d['risk_score'] for d in self.detection_history[-10:]]
					avg_risk = sum(recent_risks) / len(recent_risks)
					
					if avg_risk > 0.7:  # High risk of detection
						# Add more randomness to behavior
						base_params.update({
							'interaction_frequency': random.uniform(0.1, 0.3),
							'movement_randomness': random.uniform(0.3, 0.7),
							'timing_variation': random.uniform(1.0, 2.0),
							'scroll_randomness': random.uniform(0.2, 0.5)
						})
				
				return base_params
			return self.behavior_params['defaults']
		except Exception as e:
			self.logger.error(f"Failed to get behavior parameters: {str(e)}")
			return self.behavior_params['defaults']
			
	def record_interaction(self, metrics: Dict):
		"""Record interaction metrics for learning"""
		try:
			self.interaction_history.append({
				'timestamp': time.time(),
				'metrics': metrics,
				'success': metrics.get('interaction_consistency', 0) > 0.7
			})
			
			# Update behavior model if enough data
			if len(self.interaction_history) >= 100:
				self._update_behavior_model()
				
		except Exception as e:
			self.logger.error(f"Failed to record interaction: {str(e)}")
			
	def should_perform_interaction(self, current_metrics: Dict) -> bool:
		"""Decide if interaction should be performed"""
		try:
			if self.behavior_model:
				features = self._extract_behavior_features(current_metrics)
				return bool(self.behavior_model.predict(features) > 0.5)
			return random.random() < self.behavior_params['defaults']['interaction_probability']
		except:
			return True
			
	def _extract_features(self, task: Dict) -> np.ndarray:
		"""Extract features for AI analysis"""
		features = [
			task.get('priority', 0),
			task.get('complexity', 0),
			task.get('expected_time', 0),
			task.get('resource_intensity', 0)
		]
		return np.array(features).reshape(1, -1)
		
	def _predict_optimization(self, features: np.ndarray) -> float:
		"""Predict optimization potential"""
		try:
			if self.model:
				prediction = self.model.predict(features)
				return float(prediction[0])
			return 0.5
		except Exception as e:
			self.logger.error(f"Prediction failed: {str(e)}")
			return 0.5
			
	def _apply_optimization(self, task: Dict, score: float) -> Dict:
		"""Apply optimization based on AI prediction"""
		optimized_task = task.copy()
		
		# Apply optimization strategies
		if score > 0.8:
			optimized_task['priority'] = 'high'
			optimized_task['batch_size'] = 2
		elif score > 0.5:
			optimized_task['priority'] = 'medium'
			optimized_task['batch_size'] = 1
		else:
			optimized_task['priority'] = 'low'
			optimized_task['batch_size'] = 1
			
		optimized_task['optimization_score'] = score
		return optimized_task
		
	def _load_behavior_model(self):
		"""Load behavior prediction model"""
		try:
			model_path = Path(__file__).parent.parent.parent / 'models' / 'behavior_model.h5'
			if model_path.exists():
				return tf.keras.models.load_model(str(model_path))
			return self._create_behavior_model()
		except:
			return None
			
	def _create_behavior_model(self):
		"""Create new behavior model"""
		model = tf.keras.Sequential([
			tf.keras.layers.Dense(32, activation='relu', input_shape=(10,)),
			tf.keras.layers.Dense(16, activation='relu'),
			tf.keras.layers.Dense(1, activation='sigmoid')
		])
		model.compile(optimizer='adam', loss='binary_crossentropy')
		return model
		
	def _load_behavior_params(self) -> Dict:
		"""Load behavior parameters"""
		try:
			config_path = Path(__file__).parent.parent.parent / 'config' / 'ai_config.json'
			with open(config_path) as f:
				return json.load(f)
		except:
			return {
				'defaults': {
					'interaction_probability': 0.2,
					'scroll_speed': 1.0,
					'typing_speed': 1.0,
					'pause_duration': 2.0,
					'movement_pattern': 'natural'
				}
			}
			
	def _analyze_recent_patterns(self) -> Dict:
		"""Analyze recent interaction patterns"""
		recent = self.interaction_history[-50:]
		return {
			'avg_frequency': np.mean([x['metrics']['interaction_frequency'] for x in recent]),
			'avg_scroll_speed': np.mean([x['metrics'].get('scroll_speed', 1.0) for x in recent]),
			'avg_typing_speed': np.mean([x['metrics'].get('typing_speed', 1.0) for x in recent]),
			'avg_pause': np.mean([x['metrics'].get('pause_duration', 2.0) for x in recent]),
			'movement_pattern': self._determine_movement_pattern(recent)
		}
		
	def analyze_bot_risk(self, metrics: Dict) -> Tuple[float, Dict]:
		"""Analyze risk of bot detection"""
		try:
			risk_factors = {
				'timing_regularity': self._analyze_timing_regularity(metrics),
				'movement_precision': self._analyze_movement_precision(metrics),
				'interaction_consistency': metrics.get('interaction_consistency', 0),
				'scroll_pattern_similarity': self._analyze_scroll_patterns(metrics)
			}
			
			# Calculate overall risk score
			risk_score = sum(score for score in risk_factors.values()) / len(risk_factors)
			
			# Record detection attempt
			self.detection_history.append({
				'timestamp': time.time(),
				'risk_score': risk_score,
				'factors': risk_factors
			})
			
			return risk_score, risk_factors
			
		except Exception as e:
			self.logger.error(f"Bot risk analysis failed: {str(e)}")
			return 0.5, {}
			
	def _analyze_timing_regularity(self, metrics: Dict) -> float:
		"""Analyze timing patterns for regularity"""
		try:
			interaction_times = metrics.get('interaction_times', [])
			if len(interaction_times) < 2:
				return 0.5
				
			# Calculate time differences between interactions
			time_diffs = np.diff(interaction_times)
			
			# Calculate coefficient of variation (lower = more regular = more bot-like)
			cv = np.std(time_diffs) / np.mean(time_diffs)
			
			# Convert to risk score (high CV = low risk)
			return max(0, 1 - cv)
			
		except Exception as e:
			self.logger.error(f"Timing analysis failed: {str(e)}")
			return 0.5
			
	def _analyze_movement_precision(self, metrics: Dict) -> float:
		"""Analyze mouse movement precision"""
		try:
			movements = metrics.get('mouse_movements', [])
			if not movements:
				return 0.5
				
			# Calculate movement precision metrics
			precision_scores = []
			for move in movements:
				if isinstance(move, dict):
					# Analyze path smoothness and speed consistency
					smoothness = move.get('path_smoothness', 0.5)
					speed_consistency = move.get('speed_consistency', 0.5)
					precision_scores.append((smoothness + speed_consistency) / 2)
					
			return sum(precision_scores) / len(precision_scores) if precision_scores else 0.5
			
		except Exception as e:
			self.logger.error(f"Movement analysis failed: {str(e)}")
			return 0.5
			
	def _analyze_scroll_patterns(self, metrics: Dict) -> float:
		"""Analyze scroll pattern naturalness"""
		try:
			scroll_patterns = metrics.get('scroll_patterns', [])
			if not scroll_patterns:
				return 0.5
				
			# Analyze scroll speed variations and directions
			variations = np.std([p.get('speed', 1.0) for p in scroll_patterns])
			direction_changes = sum(1 for i in range(len(scroll_patterns)-1)
								 if scroll_patterns[i].get('direction') != 
									scroll_patterns[i+1].get('direction'))
									
			# More variations and direction changes = more natural
			naturalness = (variations + direction_changes/len(scroll_patterns)) / 2
			return max(0, 1 - naturalness)  # Convert to risk score
			
		except Exception as e:
			self.logger.error(f"Scroll pattern analysis failed: {str(e)}")
			return 0.5
			
	def _determine_movement_pattern(self, interactions: List[Dict]) -> str:
		"""Analyze and determine movement pattern type"""
		try:
			patterns = [x['metrics'].get('movement_pattern', 'natural') for x in interactions]
			return max(set(patterns), key=patterns.count)
		except:
			return 'natural'
			
	def _extract_behavior_features(self, metrics: Dict) -> np.ndarray:
		"""Extract features for behavior prediction"""
		features = [
			metrics.get('interaction_frequency', 0),
			metrics.get('scroll_speed', 1.0),
			metrics.get('typing_speed', 1.0),
			metrics.get('pause_duration', 2.0),
			metrics.get('mouse_movement_speed', 1.0),
			metrics.get('click_accuracy', 1.0),
			metrics.get('scroll_pattern_regularity', 1.0),
			metrics.get('interaction_consistency', 1.0),
			metrics.get('session_duration', 0),
			metrics.get('watch_duration', 0)
		]
		return np.array(features).reshape(1, -1)
		
	def _update_behavior_model(self):
		"""Update behavior model with new interaction data"""
		try:
			if not self.behavior_model:
				self.behavior_model = self._create_behavior_model()
				
			# Prepare training data
			X = np.array([self._extract_behavior_features(x['metrics'])[0] 
						 for x in self.interaction_history])
			y = np.array([int(x['success']) for x in self.interaction_history])
			
			# Train model
			self.behavior_model.fit(X, y, epochs=5, batch_size=32, verbose=0)
			
			# Save updated model
			model_path = Path(__file__).parent.parent.parent / 'models' / 'behavior_model.h5'
			self.behavior_model.save(str(model_path))
			
		except Exception as e:
			self.logger.error(f"Failed to update behavior model: {str(e)}")