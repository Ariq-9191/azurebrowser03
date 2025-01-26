import logging
import random
import time
from typing import Optional
import numpy as np
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from typing import Dict, Any, Tuple

class InteractionSimulator:
	def __init__(self, ai_brain=None):
		self.logger = logging.getLogger(__name__)
		self.ai_brain = ai_brain
		self.interaction_patterns = self._load_patterns()
		self.metrics_collector = {
			'mouse_movements': [],
			'scroll_patterns': [],
			'typing_speeds': [],
			'interaction_times': []
		}
		
	def _init_metrics(self) -> Dict:
		"""Initialize metrics dictionary"""
		return {
			'watch_duration': 0,
			'scroll_count': 0,
			'interaction_frequency': 0,
			'mouse_movement_speed': 0,
			'typing_speed': 0,
			'pause_frequency': 0,
			'click_accuracy': 0,
			'scroll_pattern_regularity': 0,
			'interaction_consistency': 0,
			'session_duration': 0,
			'completion_rate': 0
		}

	def simulate_video_interaction(self, driver: Any, video_url: str, params: Dict = None) -> Tuple[bool, Dict]:
		"""Simulate human-like video interaction"""
		try:
			start_time = time.time()
			metrics = self._init_metrics()
			
			driver.get(video_url)
			self._wait_for_video_load(driver)
			
			# Get video duration
			video_duration = self._get_video_duration(driver)
			if not video_duration:
				return False, metrics
				
			# Calculate target watch duration
			target_duration = min(
				params.get('duration', 180),
				int(video_duration * params.get('min_completion', 0.8))
			)
			
			# Initial random delay before interaction
			time.sleep(random.uniform(2, 5))
			
			# Execute pre-watch interactions
			self._pre_watch_interactions(driver, metrics)
			
			# Watch video with natural interactions
			watch_success = self._watch_video_naturally(
				driver, 
				target_duration,
				params.get('interaction_frequency', 0.2),
				metrics
			)
			
			if watch_success:
				# Post-watch interactions
				self._post_watch_interactions(driver, metrics)
				
			metrics['session_duration'] = time.time() - start_time
			metrics['completion_rate'] = metrics['watch_duration'] / video_duration if video_duration else 0
			
			# Save metrics for AI learning if available
			if self.ai_brain:
				self.ai_brain.record_interaction(metrics)
			
			return watch_success, metrics
			
		except Exception as e:
			self.logger.error(f"Video interaction failed: {str(e)}")
			return False, metrics
			
	def _watch_video_naturally(self, driver: Any, duration: int, interaction_freq: float, metrics: Dict) -> bool:
		"""Watch video with natural viewing patterns"""
		start_time = time.time()
		last_interaction = 0
		pause_count = 0
		
		while time.time() - start_time < duration:
			current_time = time.time()
			elapsed = current_time - start_time
			
			# Random pauses (max 2 times)
			if pause_count < 2 and random.random() < 0.1:
				self._pause_video(driver)
				time.sleep(random.uniform(2, 5))
				self._play_video(driver)
				pause_count += 1
				
			# Natural interactions
			if current_time - last_interaction > random.uniform(10, 30):
				if random.random() < interaction_freq:
					interaction = random.choice([
						self._scroll_slightly,
						self._move_mouse_randomly,
						self._hover_progress_bar,
						self._adjust_volume
					])
					interaction(driver)
					last_interaction = current_time
					
			# Simulate attention spans
			if elapsed > 30 and random.random() < 0.1:
				time.sleep(random.uniform(0.5, 2))
				
			time.sleep(0.5)  # Base loop delay
			
		metrics['watch_duration'] = time.time() - start_time
		return True

	def _get_video_duration(self, driver: Any) -> Optional[int]:
		"""Get video duration in seconds"""
		try:
			duration_element = WebDriverWait(driver, 10).until(
				EC.presence_of_element_located((By.CLASS_NAME, "ytp-time-duration"))
			)
			duration_text = duration_element.text
			parts = duration_text.split(':')
			if len(parts) == 2:
				return int(parts[0]) * 60 + int(parts[1])
			elif len(parts) == 3:
				return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
		except:
			self.logger.warning("Could not get video duration")
			return None

	def _pre_watch_interactions(self, driver: Any, metrics: Dict):
		"""Perform pre-watch interactions"""
		# Random initial scroll
		if random.random() < 0.7:
			self._scroll_slightly(driver)
			time.sleep(random.uniform(1, 3))
		
		# Sometimes check video description
		if random.random() < 0.3:
			self._expand_description(driver)
			time.sleep(random.uniform(2, 4))

	def _post_watch_interactions(self, driver: Any, metrics: Dict):
		"""Perform post-watch interactions"""
		# Sometimes like video
		if random.random() < 0.2:
			self._like_video(driver)
			
		# Sometimes check related videos
		if random.random() < 0.4:
			self._scroll_to_recommendations(driver)
			time.sleep(random.uniform(2, 4))

	def _pause_video(self, driver: Any):
		"""Pause video playback"""
		try:
			video = WebDriverWait(driver, 3).until(
				EC.presence_of_element_located((By.CLASS_NAME, "html5-main-video"))
			)
			video.click()
		except:
			self.logger.debug("Could not pause video")

	def _play_video(self, driver: Any):
		"""Resume video playback"""
		try:
			video = WebDriverWait(driver, 3).until(
				EC.presence_of_element_located((By.CLASS_NAME, "html5-main-video"))
			)
			video.click()
		except:
			self.logger.debug("Could not play video")

	def _expand_description(self, driver: Any):
		"""Expand video description"""
		try:
			expand_button = WebDriverWait(driver, 3).until(
				EC.presence_of_element_located((By.CSS_SELECTOR, "tp-yt-paper-button#expand"))
			)
			expand_button.click()
		except:
			self.logger.debug("Could not expand description")

	def _scroll_to_recommendations(self, driver: Any):
		"""Scroll to video recommendations"""
		try:
			driver.execute_script("window.scrollTo(0, window.innerHeight);")
		except:
			self.logger.debug("Could not scroll to recommendations")
			
	def _random_interaction(self, driver: Any):
		"""Perform random interaction"""
		interactions = [
			self._scroll_slightly,
			self._move_mouse_randomly,
			self._adjust_volume,
			self._hover_progress_bar
		]
		random.choice(interactions)(driver)
		
	def _simulate_scroll_pattern(self, driver: Any):
		"""Simulate natural scrolling pattern"""
		scroll_points = random.randint(2, 5)
		for _ in range(scroll_points):
			scroll_amount = random.randint(100, 500)
			driver.execute_script(f"window.scrollBy(0, {scroll_amount})")
			time.sleep(random.uniform(0.5, 2))
			
	def _move_mouse_randomly(self, driver: Any):
		"""Move mouse in natural pattern"""
		action = ActionChains(driver)
		x_offset = random.randint(-100, 100)
		y_offset = random.randint(-100, 100)
		action.move_by_offset(x_offset, y_offset).perform()
		
	def _determine_watch_duration(self, params: Dict = None) -> int:
		"""Determine video watch duration"""
		if params and 'duration' in params:
			base_duration = params['duration']
		else:
			base_duration = random.randint(30, 180)  # 30s to 3min
			
		# Add randomness
		variation = random.uniform(0.8, 1.2)
		return int(base_duration * variation)
		
	def _wait_for_video_load(self, driver: Any):
		"""Wait for video player to load"""
		try:
			WebDriverWait(driver, 10).until(
				EC.presence_of_element_located((By.CLASS_NAME, "html5-video-player"))
			)
		except Exception as e:
			self.logger.error(f"Video load timeout: {str(e)}")
			raise
			
	def _like_video(self, driver: Any):
		"""Like video with natural timing"""
		try:
			like_button = WebDriverWait(driver, 5).until(
				EC.presence_of_element_located((By.CSS_SELECTOR, "button[aria-label*='like']"))
			)
			time.sleep(random.uniform(0.5, 2))
			like_button.click()
		except:
			self.logger.warning("Could not like video")
			
	def _load_patterns(self) -> Dict:
		"""Load interaction patterns"""
		return {
			'scroll_speeds': [0.5, 1, 2],
			'pause_durations': [1, 2, 3, 5],
			'interaction_probability': 0.2
		}
		
	def _scroll_slightly(self, driver: Any):
		"""Scroll slightly up or down"""
		scroll_amount = random.randint(-50, 50)
		driver.execute_script(f"window.scrollBy(0, {scroll_amount})")
		time.sleep(random.uniform(0.3, 1))
		
	def _adjust_volume(self, driver: Any):
		"""Simulate volume adjustment"""
		try:
			volume_slider = WebDriverWait(driver, 3).until(
				EC.presence_of_element_located((By.CLASS_NAME, "ytp-volume-panel"))
			)
			action = ActionChains(driver)
			action.move_to_element(volume_slider).perform()
			time.sleep(random.uniform(0.5, 1))
		except:
			self.logger.debug("Could not adjust volume")
			
	def _hover_progress_bar(self, driver: Any):
		"""Hover over video progress bar"""
		try:
			progress_bar = WebDriverWait(driver, 3).until(
				EC.presence_of_element_located((By.CLASS_NAME, "ytp-progress-bar"))
			)
			action = ActionChains(driver)
			action.move_to_element(progress_bar).perform()
			time.sleep(random.uniform(0.5, 2))
		except:
			self.logger.debug("Could not hover over progress bar")
			
	def _calculate_consistency(self, metrics: Dict) -> float:
		"""Calculate interaction consistency score"""
		try:
			# Analyze patterns in collected metrics
			movement_consistency = np.std(self.metrics_collector['mouse_movements'])
			scroll_consistency = np.std(self.metrics_collector['scroll_patterns'])
			timing_consistency = np.std(self.metrics_collector['interaction_times'])
			
			# Normalize and combine scores
			return 1.0 - np.mean([movement_consistency, scroll_consistency, timing_consistency])
		except:
			return 0.5