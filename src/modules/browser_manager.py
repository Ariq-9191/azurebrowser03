import logging
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from typing import Dict, List
import random
import json
from pathlib import Path

class BrowserManager:
    def __init__(self, proxy_handler=None):
        self.logger = logging.getLogger(__name__)
        self.proxy_handler = proxy_handler
        self.active_browsers = {}
        self.fingerprint_pool = self._load_fingerprints()
        
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
            
    def create_multiple_browsers(self, count: int, region: str = 'US') -> List[uc.Chrome]:
        """Create multiple browser instances with unique fingerprints"""
        browsers = []
        for i in range(count):
            session_id = f"session_{i}"
            try:
                browser = self.create_browser(session_id, region)
                browsers.append(browser)
            except Exception as e:
                self.logger.error(f"Failed to create browser {i}: {str(e)}")
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