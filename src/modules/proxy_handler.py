import logging
import requests
import json
from typing import Dict, List, Optional
from pathlib import Path
import random
import time

class ProxyHandler:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.proxy_pool = {}
        self.proxy_config = self._load_proxy_config()
        self.last_refresh = time.time()
        self._initialize_proxy_pool()
        
    def get_proxy(self, region: str = 'US') -> Optional[str]:
        """Get working proxy for specified region"""
        try:
            if self._should_refresh_proxies():
                self._refresh_proxy_pool()
                
            available_proxies = self.proxy_pool.get(region, [])
            if not available_proxies:
                self.logger.warning(f"No proxies available for region {region}")
                return None
                
            proxy = random.choice(available_proxies)
            if self._test_proxy(proxy):
                return proxy
                
            # Remove failed proxy and try another
            available_proxies.remove(proxy)
            return self.get_proxy(region)
            
        except Exception as e:
            self.logger.error(f"Error getting proxy: {str(e)}")
            return None
            
    def _initialize_proxy_pool(self):
        """Initialize proxy pool from multiple sources"""
        try:
            # Load from API sources
            for source in self.proxy_config['proxy_sources']:
                proxies = self._fetch_proxies_from_source(source)
                self._add_proxies_to_pool(proxies)
                
            # Load from backup file
            backup_proxies = self._load_backup_proxies()
            if backup_proxies:
                self._add_proxies_to_pool(backup_proxies)
                
        except Exception as e:
            self.logger.error(f"Proxy pool initialization failed: {str(e)}")
            
    def _fetch_proxies_from_source(self, source: Dict) -> List[Dict]:
        """Fetch proxies from API source"""
        try:
            response = requests.get(
                source['url'],
                headers=source.get('headers', {}),
                timeout=10
            )
            response.raise_for_status()
            
            proxies = []
            for proxy in response.json():
                proxies.append({
                    'address': f"{proxy['ip']}:{proxy['port']}",
                    'region': proxy.get('country', 'Unknown'),
                    'type': proxy.get('type', 'http')
                })
            return proxies
            
        except Exception as e:
            self.logger.error(f"Failed to fetch proxies from {source['url']}: {str(e)}")
            return []
            
    def _test_proxy(self, proxy: str) -> bool:
        """Test if proxy is working"""
        try:
            response = requests.get(
                'https://www.google.com',
                proxies={'http': proxy, 'https': proxy},
                timeout=5
            )
            return response.status_code == 200
        except:
            return False
            
    def _should_refresh_proxies(self) -> bool:
        """Check if proxy pool should be refreshed"""
        return time.time() - self.last_refresh > self.proxy_config['refresh_interval']
        
    def _refresh_proxy_pool(self):
        """Refresh proxy pool"""
        self._initialize_proxy_pool()
        self.last_refresh = time.time()
        
    def _load_proxy_config(self) -> Dict:
        """Load proxy configuration"""
        try:
            config_path = Path(__file__).parent.parent.parent / 'config' / 'proxy_config.json'
            with open(config_path) as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load proxy config: {str(e)}")
            return self._get_default_config()
            
    def _get_default_config(self) -> Dict:
        """Get default proxy configuration"""
        return {
            'proxy_sources': [
                {
                    'url': 'https://proxylist.geonode.com/api/proxy-list',
                    'headers': {'Accept': 'application/json'}
                }
            ],
            'refresh_interval': 3600,  # 1 hour
            'regions': ['US', 'GB', 'DE', 'FR']
        }
        
    def _add_proxies_to_pool(self, proxies: List[Dict]):
        """Add proxies to pool by region"""
        for proxy in proxies:
            region = proxy['region']
            if region not in self.proxy_pool:
                self.proxy_pool[region] = []
            self.proxy_pool[region].append(proxy['address'])
            
    def _load_backup_proxies(self) -> List[Dict]:
        """Load backup proxies from file"""
        try:
            backup_path = Path(__file__).parent.parent.parent / 'config' / 'backup_proxies.json'
            if backup_path.exists():
                with open(backup_path) as f:
                    return json.load(f)
            return []
        except Exception as e:
            self.logger.error(f"Failed to load backup proxies: {str(e)}")
            return []