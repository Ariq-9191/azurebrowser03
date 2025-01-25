
# File: src/browser_manager.py
# Fungsi: Manajemen Browser dengan Proxy Cerdas

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from proxy_handler import ProxyManager
import random
import undetected_chromedriver as uc

class BrowserManager:
    def __init__(self, proxy_manager=None):
        """
        Inisialisasi Browser Manager dengan Proxy
        :param proxy_manager: Instance ProxyManager
        """
        self.proxy_manager = proxy_manager or ProxyManager()
        self.chrome_options = self._setup_chrome_options()
    
    def _setup_chrome_options(self):
        """
        Konfigurasi opsi Chrome
        :return: Objek Chrome Options
        """
        options = uc.ChromeOptions()
        
        # Pengaturan dasar
        options.add_argument("--start-maximized")
        options.add_argument("--disable-extensions")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        # Tambahan anti-detect
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        return options
    
    def create_browser(self, use_proxy=True):
        """
        Membuat instance browser baru
        :param use_proxy: Gunakan proxy atau tidak
        :return: Instance WebDriver
        """
        # Ambil proxy jika diminta
        proxy = None
        if use_proxy:
            proxy = self.proxy_manager.get_random_proxy()
        
        # Konfigurasi proxy
        if proxy:
            proxy_arg = f"--proxy-server={proxy['ip']}:{proxy['port']}"
            self.chrome_options.add_argument(proxy_arg)
        
        # Buat browser dengan undetected chromedriver
        driver = uc.Chrome(
            options=self.chrome_options,
            use_subprocess=True
        )
        
        # Tambahan anti-detect
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                })
            """
        })
        
        return driver
    
    def rotate_proxy(self, driver):
        """
        Rotate proxy untuk browser yang sudah ada
        :param driver: Instance WebDriver
        """
        # Tutup browser saat ini
        driver.quit()
        
        # Buat browser baru dengan proxy baru
        return self.create_browser(use_proxy=True)

# Contoh penggunaan
def test_browser_manager():
    # Inisialisasi
    proxy_manager = ProxyManager()
    browser_manager = BrowserManager(proxy_manager)
    
    # Update proxy list
    proxy_manager.update_proxy_list()
    
    # Buat browser
    driver = browser_manager.create_browser()
    
    try:
        # Contoh navigasi
        driver.get("https://ipinfo.io")
        
        # Tunggu sebentar untuk melihat IP
        import time
        time.sleep(5)
        
        # Rotate proxy
        driver = browser_manager.rotate_proxy(driver)
        driver.get("https://ipinfo.io")
        
        # Tunggu lagi
        time.sleep(5)
    
    finally:
        # Pastikan browser ditutup
        driver.quit()

# Jalankan test
if __name__ == "__main__":
    test_browser_manager()