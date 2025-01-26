import logging
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from typing import Dict, List, Optional, Any
import random
import json
import time
from pathlib import Path
from .profile_manager import ProfileManager
from .account_creator import GoogleAccountCreator
from .phone_verifier import PhoneVerifier
from .session_manager import SessionManager

class BrowserManager:
	def __init__(self, proxy_handler=None):
		self.logger = logging.getLogger(__name__)
		self.proxy_handler = proxy_handler
		self.active_browsers = {}
		self.fingerprint_pool = self._load_fingerprints()
		self.profile_manager = ProfileManager()
		self.session_manager = SessionManager()
		self.account_creator = GoogleAccountCreator(PhoneVerifier())
		self.max_concurrent = 1000
		
	def create_browser(self, session_id: str, region: str = 'US') -> uc.Chrome:
		"""Create new browser instance with unique fingerprint"""
		try:
			proxy = self.proxy_handler.get_proxy(region) if self.proxy_handler else None
			fingerprint = self._generate_fingerprint()
			
			options = uc.ChromeOptions()
			if proxy:
				options.add_argument(f'--proxy-server={proxy}')
			
			# Apply fingerprint modifications
			self._apply_fingerprint(options, fingerprint)
			
			driver = uc.Chrome(options=options)
			self.active_browsers[session_id] = {
				'driver': driver,
				'fingerprint': fingerprint,
				'proxy': proxy
			}
			return driver
			
		except Exception as e:
			self.logger.error(f"Browser creation failed: {str(e)}")
			raise
			
	def create_browser_with_account(self, region: str = 'US') -> Optional[Dict]:
		"""Create browser with new Google account"""
		try:
			# Create browser with unique fingerprint
			browser = self.create_browser(f"temp_{random.randint(1000,9999)}", region)
			
			# Create Google account
			account_info = self.account_creator.create_account(browser)
			if not account_info:
				browser.quit()
				return None
				
			# Create and save browser profile
			profile_id = self.profile_manager.create_profile({
				**account_info,
				'fingerprint': self._generate_fingerprint(),
				'proxy': self.proxy_handler.get_proxy(region) if self.proxy_handler else None
			})
			
			if profile_id:
				self.active_browsers[profile_id] = browser
				return {
					'profile_id': profile_id,
					'account': account_info,
					'browser': browser
				}
				
			browser.quit()
			return None
			
		except Exception as e:
			self.logger.error(f"Failed to create browser with account: {str(e)}")
			return None
			
	def create_or_load_browser(self, region: str = 'US') -> Optional[Dict]:
		"""Create new browser or load existing session"""
		try:
			# Check active sessions first
			sessions = self.session_manager.get_active_sessions()
			if sessions:
				# Filter sessions based on success rate and last used time
				valid_sessions = [
					s for s in sessions 
					if s.get('success_count', 0) > 5 and 
					time.time() - s.get('last_used', 0) > 3600  # At least 1 hour between uses
				]
				
				if valid_sessions:
					session = random.choice(valid_sessions)
					browser = self.create_browser(session['profile_id'], region)
					
					# Try loading session with retry mechanism
					retry_count = 0
					while retry_count < 3:
						if self.session_manager.load_session(session['profile_id'], browser):
							self.logger.info(f"Reused existing session: {session['email']}")
							return {'browser': browser, 'profile_id': session['profile_id']}
						retry_count += 1
						time.sleep(2)
					
					browser.quit()

			# Create new browser with account if no valid session
			return self.create_browser_with_account(region)

		except Exception as e:
			self.logger.error(f"Failed to create/load browser: {str(e)}")
			return None

	def watch_videos(self, main_video_url: str, watch_duration: int = 180, completion_target: float = 0.8):
		"""Watch random videos then focus on main video"""
		try:
			if len(self.active_browsers) >= self.max_concurrent:
				self.logger.warning("Maximum concurrent browsers reached")
				return False

			browser_info = self.create_or_load_browser()
			if not browser_info:
				return False

			browser = browser_info['browser']
			simulator = InteractionSimulator(self.ai_brain)

			# Watch 2-5 random videos first with varying durations
			random_watch_count = random.randint(2, 5)
			self._watch_random_videos(browser, simulator, random_watch_count)

			# Watch main video with completion tracking
			target_duration = int(watch_duration * completion_target)
			success, metrics = simulator.simulate_video_interaction(
				browser, 
				main_video_url,
				{
					'duration': target_duration,
					'min_completion': completion_target,
					'interaction_frequency': random.uniform(0.1, 0.3)
				}
			)

			# Save session only if watch was successful
			if success and metrics.get('watch_duration', 0) >= target_duration * 0.9:
				self.session_manager.save_session(
					browser_info['profile_id'],
					browser,
					{
						'email': browser_info.get('email', 'unknown'),
						'success_count': browser_info.get('success_count', 0) + 1,
						'last_metrics': metrics
					}
				)

			browser.quit()
			return success

		except Exception as e:
			self.logger.error(f"Video watching failed: {str(e)}")
			return False

	def _watch_random_videos(self, browser: Any, simulator: Any, count: int):
		"""Watch random YouTube videos"""
		try:
			browser.get('https://www.youtube.com')
			time.sleep(random.uniform(2, 4))

			for _ in range(count):
				# Find and click random video
				videos = browser.find_elements(By.ID, "video-title")
				if videos:
					video = random.choice(videos)
					simulator._move_mouse_randomly(browser)
					video.click()
					
					# Watch for random duration
					duration = random.randint(30, 120)
					simulator.simulate_video_interaction(
						browser,
						browser.current_url,
						{'duration': duration}
					)
					
					browser.back()
					time.sleep(random.uniform(1, 3))

		except Exception as e:
			self.logger.error(f"Random video watching failed: {str(e)}")
			
	def create_multiple_browsers(self, count: int, region: str = 'US') -> List[Dict]:
		"""Create multiple browser instances with unique accounts"""
		browsers = []
		for _ in range(count):
			result = self.create_browser_with_account(region)
			if result:
				browsers.append(result)
		return browsers
		
	def _generate_fingerprint(self) -> Dict:
		"""Generate unique browser fingerprint"""
		return {
			'user_agent': random.choice(self.fingerprint_pool['user_agents']),
			'platform': random.choice(self.fingerprint_pool['platforms']),
			'webgl_vendor': random.choice(self.fingerprint_pool['webgl_vendors']),
			'renderer': random.choice(self.fingerprint_pool['renderers']),
			'language': random.choice(['en-US', 'en-GB', 'de-DE', 'fr-FR'])
		}
		
	def _apply_fingerprint(self, options: uc.ChromeOptions, fingerprint: Dict):
		"""Apply fingerprint to browser options"""
		options.add_argument(f'user-agent={fingerprint["user_agent"]}')
		options.add_argument(f'--lang={fingerprint["language"]}')
		options.add_argument('--disable-blink-features=AutomationControlled')
		
		# Add CDP commands for advanced fingerprint spoofing
		options.add_argument('--enable-features=NetworkService,NetworkServiceInProcess')
		
	def _load_fingerprints(self) -> Dict:
		"""Load fingerprint data from configuration"""
		try:
			config_path = Path(__file__).parent.parent.parent / 'config' / 'fingerprints.json'
			with open(config_path) as f:
				return json.load(f)
		except Exception as e:
			self.logger.error(f"Failed to load fingerprints: {str(e)}")
			return self._get_default_fingerprints()
			
	def _get_default_fingerprints(self) -> Dict:
		"""Get default fingerprint pool"""
		return {
			'user_agents': [
				'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
				'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
			],
			'platforms': ['Win32', 'MacIntel', 'Linux x86_64'],
			'webgl_vendors': ['Google Inc.', 'Intel Inc.'],
			'renderers': ['ANGLE (Intel)', 'ANGLE (AMD)', 'ANGLE (NVIDIA)']
		}