import logging
import json
import sqlite3
import pickle
from pathlib import Path
from typing import Dict, Optional, List
import time
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webdriver import WebDriver

class SessionManager:
	def __init__(self, database_path=None):
		self.logger = logging.getLogger(__name__)
		self.db_path = database_path or str(Path(__file__).parent.parent.parent / 'data' / 'sessions.db')
		self.cookies_dir = Path(__file__).parent.parent.parent / 'data' / 'cookies'
		self.cookies_dir.mkdir(parents=True, exist_ok=True)
		self._init_database()
		
	def save_session(self, profile_id: str, driver: WebDriver, account_info: Dict) -> bool:
		"""Save browser session and cookies"""
		try:
			# Save cookies
			cookies = driver.get_cookies()
			cookie_path = self.cookies_dir / f"{profile_id}.pkl"
			with open(cookie_path, 'wb') as f:
				pickle.dump(cookies, f)
				
			# Save session info
			self._save_session_to_db(profile_id, {
				'last_used': time.time(),
				'account_email': account_info['email'],
				'cookie_path': str(cookie_path),
				'user_agent': driver.execute_script("return navigator.userAgent"),
				'success_count': account_info.get('success_count', 0) + 1
			})
			return True
			
		except Exception as e:
			self.logger.error(f"Failed to save session: {str(e)}")
			return False
			
	def load_session(self, profile_id: str, driver: WebDriver) -> bool:
		"""Load saved session into browser"""
		try:
			session = self._get_session(profile_id)
			if not session:
				return False
				
			# Load cookies
			cookie_path = Path(session['cookie_path'])
			if cookie_path.exists():
				with open(cookie_path, 'rb') as f:
					cookies = pickle.load(f)
					
				# Clear existing cookies
				driver.delete_all_cookies()
				
				# Add saved cookies
				driver.get('https://youtube.com')
				for cookie in cookies:
					try:
						driver.add_cookie(cookie)
					except:
						continue
						
				# Refresh to apply cookies
				driver.refresh()
				return True
				
			return False
			
		except Exception as e:
			self.logger.error(f"Failed to load session: {str(e)}")
			return False
			
	def get_active_sessions(self, limit: int = 1000) -> List[Dict]:
		"""Get list of active sessions"""
		try:
			conn = sqlite3.connect(self.db_path)
			cursor = conn.cursor()
			cursor.execute('''
				SELECT profile_id, account_email, last_used, success_count
				FROM sessions
				ORDER BY last_used DESC
				LIMIT ?
			''', (limit,))
			
			sessions = []
			for row in cursor.fetchall():
				sessions.append({
					'profile_id': row[0],
					'email': row[1],
					'last_used': row[2],
					'success_count': row[3]
				})
			return sessions
			
		except Exception as e:
			self.logger.error(f"Failed to get sessions: {str(e)}")
			return []
			
	def _init_database(self):
		"""Initialize sessions database"""
		conn = sqlite3.connect(self.db_path)
		cursor = conn.cursor()
		cursor.execute('''
			CREATE TABLE IF NOT EXISTS sessions (
				profile_id TEXT PRIMARY KEY,
				account_email TEXT UNIQUE,
				last_used REAL,
				cookie_path TEXT,
				user_agent TEXT,
				success_count INTEGER DEFAULT 0
			)
		''')
		conn.commit()
		conn.close()
		
	def _save_session_to_db(self, profile_id: str, data: Dict):
		"""Save session data to database"""
		conn = sqlite3.connect(self.db_path)
		cursor = conn.cursor()
		cursor.execute('''
			INSERT OR REPLACE INTO sessions 
			(profile_id, account_email, last_used, cookie_path, user_agent, success_count)
			VALUES (?, ?, ?, ?, ?, ?)
		''', (
			profile_id,
			data['account_email'],
			data['last_used'],
			data['cookie_path'],
			data['user_agent'],
			data['success_count']
		))
		conn.commit()
		conn.close()
		
	def _get_session(self, profile_id: str) -> Optional[Dict]:
		"""Get session data from database"""
		conn = sqlite3.connect(self.db_path)
		cursor = conn.cursor()
		cursor.execute('SELECT * FROM sessions WHERE profile_id = ?', (profile_id,))
		row = cursor.fetchone()
		conn.close()
		
		if row:
			return {
				'profile_id': row[0],
				'account_email': row[1],
				'last_used': row[2],
				'cookie_path': row[3],
				'user_agent': row[4],
				'success_count': row[5]
			}
		return None