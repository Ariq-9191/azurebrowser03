import logging
import random
import string
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from typing import Dict, Optional, Any
import sqlite3
from pathlib import Path

class GoogleAccountCreator:
	def __init__(self, phone_verifier=None, database_path=None):
		self.logger = logging.getLogger(__name__)
		self.phone_verifier = phone_verifier
		self.db_path = database_path or str(Path(__file__).parent.parent.parent / 'data' / 'accounts.db')
		self._init_database()
		
	def create_account(self, driver: Any) -> Optional[Dict]:
		"""Create new Google account with AI-driven interaction"""
		try:
			driver.get("https://accounts.google.com/signup")
			
			# Generate account details
			account_info = self._generate_account_info()
			
			# Fill registration form
			self._fill_registration_form(driver, account_info)
			
			# Handle phone verification if needed
			if self._requires_phone_verification(driver):
				phone_number = self.phone_verifier.get_phone_number()
				if not self._handle_phone_verification(driver, phone_number):
					return None
					
			# Complete registration
			if self._complete_registration(driver):
				self._save_account(account_info)
				return account_info
				
			return None
			
		except Exception as e:
			self.logger.error(f"Account creation failed: {str(e)}")
			return None
			
	def _generate_account_info(self) -> Dict:
		"""Generate random account information"""
		first_name = self._generate_name()
		last_name = self._generate_name()
		username = f"{first_name.lower()}{last_name.lower()}{random.randint(100,999)}"
		
		return {
			'first_name': first_name,
			'last_name': last_name,
			'username': username,
			'email': f"{username}@gmail.com",
			'password': self._generate_password(),
			'birth_date': self._generate_birth_date()
		}
		
	def _fill_registration_form(self, driver: Any, account_info: Dict):
		"""Fill registration form with human-like timing"""
		fields = {
			'firstName': account_info['first_name'],
			'lastName': account_info['last_name'],
			'Username': account_info['username'],
			'Passwd': account_info['password'],
			'ConfirmPasswd': account_info['password']
		}
		
		for field_id, value in fields.items():
			element = WebDriverWait(driver, 10).until(
				EC.presence_of_element_located((By.NAME, field_id))
			)
			self._type_like_human(element, value)
			time.sleep(random.uniform(0.5, 1.5))
			
	def _handle_phone_verification(self, driver: Any, phone_number: str) -> bool:
		"""Handle phone verification process"""
		try:
			# Enter phone number
			phone_input = WebDriverWait(driver, 10).until(
				EC.presence_of_element_located((By.ID, "phoneNumberId"))
			)
			self._type_like_human(phone_input, phone_number)
			
			# Wait for and enter verification code
			code = self.phone_verifier.wait_for_code(phone_number)
			if not code:
				return False
				
			code_input = WebDriverWait(driver, 10).until(
				EC.presence_of_element_located((By.NAME, "code"))
			)
			self._type_like_human(code_input, code)
			return True
			
		except Exception as e:
			self.logger.error(f"Phone verification failed: {str(e)}")
			return False
			
	def _init_database(self):
		"""Initialize SQLite database for account storage"""
		conn = sqlite3.connect(self.db_path)
		cursor = conn.cursor()
		cursor.execute('''
			CREATE TABLE IF NOT EXISTS accounts (
				email TEXT PRIMARY KEY,
				username TEXT,
				password TEXT,
				creation_date TEXT,
				last_used TEXT,
				browser_profile TEXT
			)
		''')
		conn.commit()
		conn.close()
		
	def _save_account(self, account_info: Dict):
		"""Save account to database"""
		conn = sqlite3.connect(self.db_path)
		cursor = conn.cursor()
		cursor.execute('''
			INSERT INTO accounts (email, username, password, creation_date, last_used)
			VALUES (?, ?, ?, datetime('now'), datetime('now'))
		''', (account_info['email'], account_info['username'], account_info['password']))
		conn.commit()
		conn.close()
		
	def _generate_name(self) -> str:
		"""Generate random human-like name"""
		consonants = 'bcdfghjklmnpqrstvwxyz'
		vowels = 'aeiou'
		length = random.randint(4, 8)
		name = random.choice(consonants).upper()
		
		for i in range(length - 1):
			if i % 2 == 0:
				name += random.choice(vowels)
			else:
				name += random.choice(consonants)
				
		return name
		
	def _generate_password(self) -> str:
		"""Generate strong random password"""
		length = random.randint(12, 16)
		chars = string.ascii_letters + string.digits + "!@#$%^&*"
		return ''.join(random.choice(chars) for _ in range(length))
		
	def _generate_birth_date(self) -> Dict:
		"""Generate random birth date for account"""
		year = random.randint(1980, 2000)
		month = random.randint(1, 12)
		day = random.randint(1, 28)  # Using 28 to avoid invalid dates
		return {'year': year, 'month': month, 'day': day}
		
	def _type_like_human(self, element: Any, text: str):
		"""Simulate human-like typing"""
		for char in text:
			element.send_keys(char)
			time.sleep(random.uniform(0.1, 0.3))
			
	def _requires_phone_verification(self, driver: Any) -> bool:
		"""Check if phone verification is required"""
		try:
			WebDriverWait(driver, 5).until(
				EC.presence_of_element_located((By.ID, "phoneNumberId"))
			)
			return True
		except:
			return False
			
	def _complete_registration(self, driver: Any) -> bool:
		"""Complete the registration process"""
		try:
			# Click final submit button
			submit_button = WebDriverWait(driver, 10).until(
				EC.element_to_be_clickable((By.NAME, "submitbutton"))
			)
			submit_button.click()
			
			# Wait for success indicator
			WebDriverWait(driver, 20).until(
				EC.presence_of_element_located((By.CLASS_NAME, "success-message"))
			)
			return True
			
		except Exception as e:
			self.logger.error(f"Failed to complete registration: {str(e)}")
			return False