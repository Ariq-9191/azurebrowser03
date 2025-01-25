import logging
import requests
import time
from typing import Optional, Dict
import json
from pathlib import Path

class PhoneVerifier:
	def __init__(self, config_path=None):
		self.logger = logging.getLogger(__name__)
		self.config = self._load_config(config_path)
		self.active_numbers = {}
		self.sms_services = {
			'sms-activate': self._SMSActivateHandler(self.config['sms-activate']),
			'smspva': self._SMSPVAHandler(self.config['smspva']),
			'5sim': self._5SimHandler(self.config['5sim'])
		}
		
	def get_phone_number(self, country: str = 'US') -> Optional[str]:
		"""Get virtual phone number from SMS service"""
		try:
			for service_name, handler in self.sms_services.items():
				number = handler.get_number(country)
				if number:
					self.active_numbers[number] = {
						'service': service_name,
						'time': time.time()
					}
					return number
			return None
			
		except Exception as e:
			self.logger.error(f"Failed to get phone number: {str(e)}")
			return None
			
	def wait_for_code(self, phone_number: str, timeout: int = 300) -> Optional[str]:
		"""Wait for SMS verification code"""
		try:
			start_time = time.time()
			number_info = self.active_numbers.get(phone_number)
			
			if not number_info:
				return None
				
			handler = self.sms_services[number_info['service']]
			
			while time.time() - start_time < timeout:
				code = handler.get_code(phone_number)
				if code:
					return code
				time.sleep(5)
				
			return None
			
		except Exception as e:
			self.logger.error(f"Failed to get verification code: {str(e)}")
			return None
			
	def _load_config(self, config_path=None) -> Dict:
		"""Load SMS service configuration"""
		try:
			if not config_path:
				config_path = Path(__file__).parent.parent.parent / 'config' / 'sms_config.json'
				
			with open(config_path) as f:
				return json.load(f)
		except Exception as e:
			self.logger.error(f"Failed to load config: {str(e)}")
			return self._get_default_config()
			
	def _get_default_config(self) -> Dict:
		"""Get default SMS service configuration"""
		return {
			'sms-activate': {
				'api_key': '',
				'base_url': 'https://api.sms-activate.org/stubs/handler_api.php'
			},
			'smspva': {
				'api_key': '',
				'base_url': 'https://smspva.com/priemnik.php'
			},
			'5sim': {
				'api_key': '',
				'base_url': 'https://5sim.net/v1/user'
			}
		}
		
	class _SMSServiceHandler:
		def __init__(self, config: Dict):
			self.config = config
			
		def get_number(self, country: str) -> Optional[str]:
			"""Get phone number from service"""
			raise NotImplementedError
			
		def get_code(self, phone_number: str) -> Optional[str]:
			"""Get verification code from service"""
			raise NotImplementedError
			
	class _SMSActivateHandler(_SMSServiceHandler):
		def get_number(self, country: str) -> Optional[str]:
			"""Get number from SMS Activate"""
			try:
				response = requests.get(
					f"{self.config['base_url']}",
					params={
						'api_key': self.config['api_key'],
						'action': 'getNumber',
						'service': 'go',
						'country': country
					}
				)
				if response.status_code == 200 and 'ACCESS_NUMBER' in response.text:
					return response.text.split(':')[2]
				return None
			except:
				return None
				
		def get_code(self, phone_number: str) -> Optional[str]:
			"""Get code from SMS Activate"""
			try:
				response = requests.get(
					f"{self.config['base_url']}",
					params={
						'api_key': self.config['api_key'],
						'action': 'getStatus',
						'id': phone_number
					}
				)
				if response.status_code == 200 and 'STATUS_OK' in response.text:
					return response.text.split(':')[1]
				return None
			except:
				return None
				
	class _SMSPVAHandler(_SMSServiceHandler):
		def get_number(self, country: str) -> Optional[str]:
			"""Get number from SMSPVA"""
			try:
				response = requests.get(
					f"{self.config['base_url']}",
					params={
						'apikey': self.config['api_key'],
						'method': 'get_number',
						'country': country,
						'service': 'google'
					}
				)
				data = response.json()
				if data.get('response') == '1':
					return data.get('phone')
				return None
			except:
				return None
				
		def get_code(self, phone_number: str) -> Optional[str]:
			"""Get code from SMSPVA"""
			try:
				response = requests.get(
					f"{self.config['base_url']}",
					params={
						'apikey': self.config['api_key'],
						'method': 'get_sms',
						'phone': phone_number
					}
				)
				data = response.json()
				if data.get('response') == '1':
					return data.get('sms')
				return None
			except:
				return None
				
	class _5SimHandler(_SMSServiceHandler):
		def get_number(self, country: str) -> Optional[str]:
			"""Get number from 5SIM"""
			try:
				headers = {'Authorization': f'Bearer {self.config["api_key"]}'}
				response = requests.get(
					f"{self.config['base_url']}/buy/activation/{country}/google/any",
					headers=headers
				)
				data = response.json()
				if data.get('phone'):
					return data['phone']
				return None
			except:
				return None
				
		def get_code(self, phone_number: str) -> Optional[str]:
			"""Get code from 5SIM"""
			try:
				headers = {'Authorization': f'Bearer {self.config["api_key"]}'}
				response = requests.get(
					f"{self.config['base_url']}/check/{phone_number}",
					headers=headers
				)
				data = response.json()
				if data.get('sms') and data['sms'][0].get('code'):
					return data['sms'][0]['code']
				return None
			except:
				return None