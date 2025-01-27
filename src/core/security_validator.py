import logging
from typing import Dict, List, Any, Optional, Set
from pathlib import Path
import json
import re
import hashlib
import time
from datetime import datetime
import sqlite3
import threading
from concurrent.futures import ThreadPoolExecutor
import os
from cryptography.fernet import Fernet
import base64

class SecurityValidationError(Exception):
	"""Custom exception for security validation errors"""
	pass

class SecurityValidator:
	def __init__(self):
		self.logger = logging.getLogger(__name__)
		self.security_db = self._initialize_security_db()
		self.risk_patterns = self._load_risk_patterns()
		self.validation_history = []
		self.encryption_key = self._load_or_generate_key()
		self.cipher_suite = Fernet(self.encryption_key)
		self.security_config = self._load_security_config()
		self.threat_levels = {
			'low': 0.3,
			'medium': 0.6,
			'high': 0.8,
			'critical': 0.95
		}
		self._pattern_cache = {}
		self._lock = threading.Lock()
		self._blacklisted_patterns = set()
		self._initialize_blacklist()
		
	def _initialize_blacklist(self):
		"""Initialize security blacklist"""
		self._blacklisted_patterns = {
			r'(eval|exec)\s*\([\'"]',
			r'os\.(system|popen|exec)',
			r'subprocess\.(call|Popen)',
			r'__import__\s*\(',
			r'input\s*\(',
			r'open\s*\(.+,\s*[\'"]w[\'"]\)'
		}
		
	def _initialize_security_db(self) -> sqlite3.Connection:
		"""Initialize security database"""
		db_path = Path(__file__).parent.parent.parent / 'data' / 'security.db'
		db_path.parent.mkdir(exist_ok=True)
		conn = sqlite3.connect(str(db_path))
		c = conn.cursor()
		
		c.execute('''CREATE TABLE IF NOT EXISTS security_incidents
					(id INTEGER PRIMARY KEY, timestamp TEXT,
					 threat_type TEXT, severity REAL,
					 details TEXT)''')
					 
		c.execute('''CREATE TABLE IF NOT EXISTS validation_patterns
					(id INTEGER PRIMARY KEY, pattern_type TEXT,
					 pattern_data TEXT, last_updated TEXT)''')
					 
		conn.commit()
		return conn
		
	def _load_risk_patterns(self) -> Dict:
		"""Load security risk patterns"""
		try:
			patterns_path = Path(__file__).parent.parent.parent / 'config' / 'security_patterns.json'
			if patterns_path.exists():
				with open(patterns_path) as f:
					return json.load(f)
			return self._get_default_patterns()
		except Exception as e:
			self.logger.error(f"Failed to load risk patterns: {str(e)}")
			return self._get_default_patterns()
			
	def _get_default_patterns(self) -> Dict:
		"""Get default security patterns"""
		return {
			'code_injection': [
				r'eval\s*\(',
				r'exec\s*\(',
				r'system\s*\('
			],
			'data_exposure': [
				r'password',
				r'secret',
				r'api_key'
			],
			'unsafe_operations': [
				r'rm\s+-rf',
				r'DELETE\s+FROM',
				r'DROP\s+TABLE'
			]
		}
		
	def _load_or_generate_key(self) -> bytes:
		"""Load existing or generate new encryption key"""
		key_path = Path(__file__).parent.parent.parent / 'config' / '.secret_key'
		if key_path.exists():
			return open(key_path, 'rb').read()
		else:
			key = Fernet.generate_key()
			key_path.parent.mkdir(exist_ok=True)
			with open(key_path, 'wb') as f:
				f.write(key)
			return key
			
	def encrypt_sensitive_data(self, data: Dict) -> Dict:
		"""Encrypt sensitive data"""
		try:
			encrypted_data = {}
			for key, value in data.items():
				if key in self.security_config['sensitive_fields']:
					encrypted_value = self.cipher_suite.encrypt(str(value).encode())
					encrypted_data[key] = base64.b64encode(encrypted_value).decode()
				else:
					encrypted_data[key] = value
			return encrypted_data
		except Exception as e:
			self.logger.error(f"Encryption failed: {str(e)}")
			return data
			
	def decrypt_sensitive_data(self, data: Dict) -> Dict:
		"""Decrypt sensitive data"""
		try:
			decrypted_data = {}
			for key, value in data.items():
				if key in self.security_config['sensitive_fields']:
					encrypted_value = base64.b64decode(value.encode())
					decrypted_value = self.cipher_suite.decrypt(encrypted_value)
					decrypted_data[key] = decrypted_value.decode()
				else:
					decrypted_data[key] = value
			return decrypted_data
		except Exception as e:
			self.logger.error(f"Decryption failed: {str(e)}")
			return data
			
	def validate_session(self, session_data: Dict) -> bool:
		"""Validate session integrity"""
		try:
			if not session_data.get('signature'):
				return False
				
			computed_signature = self._compute_signature(session_data)
			return computed_signature == session_data['signature']
		except:
			return False
			
	def _compute_signature(self, data: Dict) -> str:
		"""Compute data signature"""
		data_str = json.dumps(data, sort_keys=True)
		return hashlib.sha256(
			(data_str + self.encryption_key.decode()).encode()
		).hexdigest()
		
	def _load_security_config(self) -> Dict:
		"""Load security configuration"""
		try:
			config_path = Path(__file__).parent.parent.parent / 'config' / 'security_config.json'
			if config_path.exists():
				with open(config_path) as f:
					return json.load(f)
			return self._create_default_security_config()
		except:
			return self._create_default_security_config()
			
	def _create_default_security_config(self) -> Dict:
		"""Create default security configuration"""
		return {
			'sensitive_fields': [
				'password',
				'token',
				'cookie',
				'session_id',
				'api_key'
			],
			'encryption_algorithm': 'Fernet',
			'signature_algorithm': 'SHA256',
			'session_timeout': 3600,
			'max_failed_attempts': 3
		}
		
	def validate_code(self, code: str, context: Dict = None) -> Dict:
		"""Validate code with enhanced security checks"""
		try:
			with self._lock:
				risks = []
				total_risk_score = 0.0
				
				# Check for immediate security violations
				if self._check_blacklist(code):
					raise SecurityValidationError("Code contains blacklisted patterns")
					
				# Check for known risk patterns
				pattern_risks = self._check_patterns(code)
				risks.extend(pattern_risks)
				
				# Check for custom security rules
				custom_risks = self._check_custom_rules(code)
				risks.extend(custom_risks)
				
				# Calculate total risk score
				total_risk_score = sum(risk['severity'] for risk in risks)
				
				# Record validation result
				result = {
					'risks': risks,
					'risk_score': min(total_risk_score, 1.0),
					'timestamp': datetime.now().isoformat(),
					'validation_id': self._generate_validation_id(code)
				}
				
				self._record_validation(result, context)
				return result
				
		except SecurityValidationError as e:
			self.logger.error(f"Security validation failed: {str(e)}")
			return {
				'risks': [{'type': 'critical', 'message': str(e), 'severity': 1.0}],
				'risk_score': 1.0
			}
		except Exception as e:
			self.logger.error(f"Unexpected error in validation: {str(e)}")
			return {'risks': [], 'risk_score': 0.0}
			
	def _check_blacklist(self, code: str) -> bool:
		"""Check for blacklisted patterns"""
		return any(re.search(pattern, code, re.IGNORECASE) 
				  for pattern in self._blacklisted_patterns)
				  
	def _check_patterns(self, code: str) -> List[Dict]:
		"""Check for known risk patterns"""
		risks = []
		for category, patterns in self.risk_patterns.items():
			for pattern in patterns:
				matches = re.finditer(pattern, code, re.IGNORECASE)
				for match in matches:
					risk = {
						'type': category,
						'pattern': pattern,
						'location': match.span(),
						'severity': self._calculate_severity(category, match.group()),
						'context': code[max(0, match.start()-20):
									 min(len(code), match.end()+20)]
					}
					risks.append(risk)
		return risks
		
	def _check_custom_rules(self, code: str) -> List[Dict]:
		"""Check custom security rules"""
		risks = []
		
		# Check for potential SQL injection
		if re.search(r'SELECT.*WHERE.*=\s*[\'"].*[\'"]\s*\+', code):
			risks.append({
				'type': 'sql_injection',
				'severity': 0.9,
				'message': 'Potential SQL injection detected'
			})
			
		# Check for hardcoded credentials
		credential_patterns = [
			r'password\s*=\s*[\'"][^\'"]+[\'"]',
			r'api_key\s*=\s*[\'"][^\'"]+[\'"]',
			r'secret\s*=\s*[\'"][^\'"]+[\'"]'
		]
		
		for pattern in credential_patterns:
			if re.search(pattern, code, re.IGNORECASE):
				risks.append({
					'type': 'hardcoded_credentials',
					'severity': 0.8,
					'message': 'Hardcoded credentials detected'
				})
				
		return risks
		
	def _generate_validation_id(self, code: str) -> str:
		"""Generate unique validation ID"""
		return hashlib.sha256(
			f"{code}{time.time()}".encode()
		).hexdigest()[:16]
			
	def validate_action(self, action: Dict) -> Dict:
		"""Validate browser automation action"""
		try:
			risk_score = 0.0
			risks = []
			
			# Validate action parameters
			if 'script' in action:
				code_risks = self.validate_code(action['script'])
				risks.extend(code_risks['risks'])
				risk_score += code_risks['risk_score']
				
			# Validate action type safety
			action_risk = self._validate_action_type(action)
			if action_risk:
				risks.append(action_risk)
				risk_score += action_risk['severity']
				
			return {
				'safe': risk_score < self.threat_levels['medium'],
				'risk_score': risk_score,
				'risks': risks
			}
			
		except Exception as e:
			self.logger.error(f"Action validation failed: {str(e)}")
			return {'safe': False, 'risk_score': 1.0}
			
	def _validate_action_type(self, action: Dict) -> Optional[Dict]:
		"""Validate specific action type"""
		risky_actions = {
			'execute_script': 0.8,
			'file_download': 0.7,
			'form_submit': 0.5
		}
		
		action_type = action.get('type', '')
		if action_type in risky_actions:
			return {
				'type': 'risky_action',
				'action': action_type,
				'severity': risky_actions[action_type]
			}
		return None
		
	def _calculate_severity(self, category: str, match: str) -> float:
		"""Calculate risk severity"""
		base_severity = {
			'code_injection': 0.9,
			'data_exposure': 0.7,
			'unsafe_operations': 0.8
		}.get(category, 0.5)
		
		# Adjust severity based on context
		context_multiplier = 1.0
		if any(pattern in match.lower() for pattern in ['admin', 'root', 'sudo']):
			context_multiplier = 1.2
			
		return min(base_severity * context_multiplier, 1.0)
		
	def _record_validation(self, result: Dict, context: Dict = None):
		"""Record validation result"""
		try:
			c = self.security_db.cursor()
			for risk in result['risks']:
				c.execute('''INSERT INTO security_incidents
							(timestamp, threat_type, severity, details)
							VALUES (?, ?, ?, ?)''',
							(result['timestamp'],
							 risk['type'],
							 risk['severity'],
							 json.dumps({
								 'pattern': risk['pattern'],
								 'location': risk['location'],
								 'context': context
							 })))
							 
			self.security_db.commit()
			
			# Update validation history
			self.validation_history.append({
				'timestamp': result['timestamp'],
				'risk_score': result['risk_score'],
				'context': context
			})
			
			# Keep history manageable
			if len(self.validation_history) > 1000:
				self.validation_history = self.validation_history[-1000:]
				
		except Exception as e:
			self.logger.error(f"Failed to record validation: {str(e)}")
			
	def get_security_report(self) -> Dict:
		"""Generate comprehensive security report"""
		try:
			with self._lock:
				c = self.security_db.cursor()
				recent_incidents = c.execute('''
					SELECT threat_type, COUNT(*), AVG(severity)
					FROM security_incidents
					WHERE timestamp > datetime('now', '-7 days')
					GROUP BY threat_type
				''').fetchall()
				
				# Analyze trends
				trend_analysis = self._analyze_security_trends()
				
				return {
					'recent_incidents': [
						{
							'type': threat_type,
							'count': count,
							'avg_severity': severity
						}
						for threat_type, count, severity in recent_incidents
					],
					'total_validations': len(self.validation_history),
					'high_risk_count': sum(1 for v in self.validation_history
										 if v['risk_score'] > self.threat_levels['high']),
					'trends': trend_analysis,
					'recommendations': self._generate_security_recommendations()
				}
				
		except Exception as e:
			self.logger.error(f"Failed to generate security report: {str(e)}")
			return {}
			
	def _analyze_security_trends(self) -> Dict:
		"""Analyze security incident trends"""
		try:
			c = self.security_db.cursor()
			daily_counts = c.execute('''
				SELECT DATE(timestamp) as date, COUNT(*) as count
				FROM security_incidents
				GROUP BY DATE(timestamp)
				ORDER BY date DESC
				LIMIT 30
			''').fetchall()
			
			return {
				'daily_incidents': [
					{'date': date, 'count': count}
					for date, count in daily_counts
				],
				'trend': self._calculate_trend([count for _, count in daily_counts])
			}
		except Exception as e:
			self.logger.error(f"Trend analysis failed: {str(e)}")
			return {}
			
	def _calculate_trend(self, values: List[int]) -> str:
		"""Calculate trend direction"""
		if len(values) < 2:
			return 'stable'
			
		avg_first_half = sum(values[:len(values)//2]) / (len(values)//2)
		avg_second_half = sum(values[len(values)//2:]) / (len(values) - len(values)//2)
		
		diff = avg_second_half - avg_first_half
		if diff > 0.1:
			return 'increasing'
		elif diff < -0.1:
			return 'decreasing'
		return 'stable'