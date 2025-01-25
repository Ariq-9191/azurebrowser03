# Modul Manajemen Proxy Cerdas

import requests
import random
import json
import os
from typing import List, Dict

class ProxyManager:
    def __init__(self, config_path='config/proxy_config.json'):
        """
        Inisialisasi Proxy Manager
        :param config_path: Path konfigurasi proxy
        """
        self.config_path = config_path
        self.proxy_list = []
        self.load_proxy_config()
    
    def load_proxy_config(self):
        """
        Memuat konfigurasi proxy dari file
        """
        try:
            with open(self.config_path, 'r') as file:
                self.proxy_list = json.load(file)
        except FileNotFoundError:
            self.proxy_list = []
    
    def save_proxy_config(self):
        """
        Menyimpan konfigurasi proxy ke file
        """
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w') as file:
            json.dump(self.proxy_list, file, indent=4)
    
    def fetch_free_proxies(self, limit=50):
        """
        Mengambil proxy gratis dari berbagai sumber
        :param limit: Jumlah proxy maksimal
        :return: Daftar proxy
        """
        proxy_sources = [
            'https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all',
            'https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt'
        ]
        
        new_proxies = []
        
        for source in proxy_sources:
            try:
                response = requests.get(source, timeout=10)
                proxies = response.text.split('\n')
                
                for proxy in proxies:
                    if ':' in proxy and len(new_proxies) < limit:
                        new_proxies.append({
                            'ip': proxy.split(':')[0],
                            'port': proxy.split(':')[1],
                            'type': 'http',
                            'status': 'untested'
                        })
            except Exception as e:
                print(f"Error fetching proxies from {source}: {e}")
        
        return new_proxies
    
    def validate_proxy(self, proxy: Dict, timeout=5):
        """
        Validasi proxy
        :param proxy: Dictionary proxy
        :param timeout: Waktu timeout
        :return: Status proxy
        """
        try:
            proxies = {
                'http': f"http://{proxy['ip']}:{proxy['port']}",
                'https': f"http://{proxy['ip']}:{proxy['port']}"
            }
            
            response = requests.get(
                'http://ipinfo.io/json', 
                proxies=proxies, 
                timeout=timeout
            )
            
            if response.status_code == 200:
                proxy['status'] = 'active'
                proxy['location'] = response.json().get('country', 'Unknown')
                return True
        except Exception:
            proxy['status'] = 'inactive'
        
        return False
    
    def get_random_proxy(self, only_active=True):
        """
        Ambil proxy acak
        :param only_active: Hanya proxy aktif
        :return: Proxy acak
        """
        if only_active:
            active_proxies = [p for p in self.proxy_list if p['status'] == 'active']
            return random.choice(active_proxies) if active_proxies else None
        
        return random.choice(self.proxy_list) if self.proxy_list else None
    
    def update_proxy_list(self, refresh_count=50):
        """
        Update daftar proxy
        :param refresh_count: Jumlah proxy baru
        """
        # Ambil proxy baru
        new_proxies = self.fetch_free_proxies(refresh_count)
        
        # Validasi proxy
        for proxy in new_proxies:
            self.validate_proxy(proxy)
        
        # Tambahkan proxy baru
        self.proxy_list.extend(new_proxies)
        
        # Simpan konfigurasi
        self.save_proxy_config()
    
    def get_selenium_proxy_options(self, proxy):
        """
        Dapatkan opsi proxy untuk Selenium
        :param proxy: Proxy dictionary
        :return: Argumen proxy untuk Chrome
        """
        return f"--proxy-server={proxy['ip']}:{proxy['port']}"

# Contoh penggunaan
def test_proxy_manager():
    # Inisialisasi
    proxy_manager = ProxyManager()
    
    # Update proxy list
    proxy_manager.update_proxy_list()
    
    # Ambil proxy acak
    random_proxy = proxy_manager.get_random_proxy()
    
    if random_proxy:
        print("Proxy Terpilih:")
        print(f"IP: {random_proxy['ip']}")
        print(f"Port: {random_proxy['port']}")
        print(f"Status: {random_proxy['status']}")
    else:
        print("Tidak ada proxy aktif")

# Jalankan test
if __name__ == "__main__":
    test_proxy_manager()