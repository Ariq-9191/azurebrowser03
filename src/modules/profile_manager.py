import logging
import json
import sqlite3
import os
from pathlib import Path
from typing import Dict, List, Optional
import shutil

class ProfileManager:
	def __init__(self, database_path=None, profiles_dir=None):
		self.logger = logging.getLogger(__name__)
		self.db_path = database_path or str(Path(__file__).parent.parent.parent / 'data' / 'profiles.db')
		self.profiles_dir = profiles_dir or str(Path(__file__).parent.parent.parent / 'browser_profiles')
		self._init_storage()
		
	def create_profile(self, account_info: Dict) -> Optional[str]:
		"""Create new browser profile and associate with account"""
		try:
			profile_id = self._generate_profile_id(account_info['email'])
			profile_path = os.path.join(self.profiles_dir, profile_id)
			
			# Create profile directory
			os.makedirs(profile_path, exist_ok=True)
			
			# Save profile metadata
			profile_data = {
				'profile_id': profile_id,
				'email': account_info['email'],
				'creation_date': account_info.get('creation_date'),
				'fingerprint': account_info.get('fingerprint', {}),
				'proxy': account_info.get('proxy')
			}
			
			self._save_profile_to_db(profile_data)
			return profile_id
			
		except Exception as e:
			self.logger.error(f"Failed to create profile: {str(e)}")
			return None
			
	def get_profile(self, email: str) -> Optional[Dict]:
		"""Get browser profile by email"""
		try:
			conn = sqlite3.connect(self.db_path)
			cursor = conn.cursor()
			cursor.execute('''
				SELECT profile_id, email, creation_date, fingerprint, proxy, last_used
				FROM profiles WHERE email = ?
			''', (email,))
			result = cursor.fetchone()
			
			if result:
				return {
					'profile_id': result[0],
					'email': result[1],
					'creation_date': result[2],
					'fingerprint': json.loads(result[3]),
					'proxy': result[4],
					'last_used': result[5]
				}
			return None
			
		except Exception as e:
			self.logger.error(f"Failed to get profile: {str(e)}")
			return None
			
	def update_profile(self, profile_id: str, updates: Dict) -> bool:
		"""Update browser profile information"""
		try:
			conn = sqlite3.connect(self.db_path)
			cursor = conn.cursor()
			
			update_fields = []
			values = []
			for key, value in updates.items():
				if key in ['fingerprint', 'proxy', 'last_used']:
					update_fields.append(f"{key} = ?")
					values.append(json.dumps(value) if isinstance(value, dict) else value)
					
			if update_fields:
				query = f"UPDATE profiles SET {', '.join(update_fields)} WHERE profile_id = ?"
				values.append(profile_id)
				cursor.execute(query, values)
				conn.commit()
				
			return True
			
		except Exception as e:
			self.logger.error(f"Failed to update profile: {str(e)}")
			return False
			
	def _init_storage(self):
		"""Initialize storage for browser profiles"""
		os.makedirs(self.profiles_dir, exist_ok=True)
		
		conn = sqlite3.connect(self.db_path)
		cursor = conn.cursor()
		cursor.execute('''
			CREATE TABLE IF NOT EXISTS profiles (
				profile_id TEXT PRIMARY KEY,
				email TEXT UNIQUE,
				creation_date TEXT,
				fingerprint TEXT,
				proxy TEXT,
				last_used TEXT
			)
		''')
		conn.commit()
		conn.close()
		
	def _generate_profile_id(self, email: str) -> str:
		"""Generate unique profile ID"""
		return f"profile_{hash(email)}"
		
	def _save_profile_to_db(self, profile_data: Dict):
		"""Save profile metadata to database"""
		conn = sqlite3.connect(self.db_path)
		cursor = conn.cursor()
		cursor.execute('''
			INSERT INTO profiles (profile_id, email, creation_date, fingerprint, proxy, last_used)
			VALUES (?, ?, ?, ?, ?, datetime('now'))
		''', (
			profile_data['profile_id'],
			profile_data['email'],
			profile_data['creation_date'],
			json.dumps(profile_data['fingerprint']),
			profile_data['proxy']
		))
		conn.commit()
		conn.close()