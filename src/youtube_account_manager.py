# Modul Manajemen Akun YouTube

import random
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from account_creator import GoogleAccountCreator
from human_simulator import HumanBehaviorSimulator
from browser_manager import BrowserManager

class YouTubeAccountManager:
    def __init__(self, browser_manager, account_creator):
        """
        Inisialisasi Manajer Akun YouTube
        :param browser_manager: Instance BrowserManager
        :param account_creator: Instance AccountCreator
        """
        self.browser_manager = browser_manager
        self.account_creator = account_creator
        self.accounts = []
    
    def create_youtube_account(self, verify_email=False):
        """
        Membuat akun YouTube baru
        :param verify_email: Apakah perlu verifikasi email
        :return: Detail akun
        """
        # Buat browser baru
        driver = self.browser_manager.create_browser()
        simulator = HumanBehaviorSimulator(driver)
        
        try:
            # Buka halaman YouTube
            driver.get("https://www.youtube.com")
            
            # Simulasi perilaku manusia sebelum login
            simulator.natural_scroll()
            time.sleep(random.uniform(1, 3))
            
            # Klik tombol login
            login_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//ytd-button-renderer[@id='sign-in-button']"))
            )
            simulator.human_like_click(login_button)
            
            # Buat akun Google baru
            account_details = self.account_creator.create_google_account(driver)
            
            if account_details:
                # Verifikasi akun YouTube (jika diperlukan)
                if verify_email:
                    self._verify_youtube_account(driver, account_details)
                
                # Simpan detail akun
                self.accounts.append(account_details)
                
                return account_details
            
            return None
        
        except Exception as e:
            print(f"Error membuat akun YouTube: {e}")
            return None
        finally:
            driver.quit()
    
    def _verify_youtube_account(self, driver, account_details):
        """
        Proses verifikasi akun YouTube
        :param driver: Instance WebDriver
        :param account_details: Detail akun
        """
        try:
            # Implementasi verifikasi (contoh sederhana)
            # Dalam praktiknya, memerlukan metode kompleks
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "verify-email-button"))
            )
            
            # Simulasi proses verifikasi
            time.sleep(random.uniform(2, 5))
            
            # Tambahkan logika verifikasi email
            print("Proses verifikasi akun YouTube")
        
        except Exception as e:
            print(f"Gagal verifikasi akun: {e}")
    
    def bulk_create_accounts(self, num_accounts=5):
        """
        Membuat beberapa akun YouTube sekaligus
        :param num_accounts: Jumlah akun yang akan dibuat
        :return: Daftar akun yang berhasil dibuat
        """
        successful_accounts = []
        
        for _ in range(num_accounts):
            try:
                account = self.create_youtube_account()
                if account:
                    successful_accounts.append(account)
                
                # Jeda antar pembuatan akun
                time.sleep(random.uniform(3, 7))
            
            except Exception as e:
                print(f"Gagal membuat akun: {e}")
        
        return successful_accounts
    
    def get_account_details(self):
        """
        Mendapatkan detail semua akun yang telah dibuat
        :return: Daftar akun
        """
        return self.accounts

# Contoh penggunaan
def test_youtube_account_manager():
    # Inisialisasi komponen
    browser_manager = BrowserManager()
    account_creator = GoogleAccountCreator()
    
    # Buat manajer akun YouTube
    youtube_account_manager = YouTubeAccountManager(
        browser_manager, 
        account_creator
    )
    
    # Buat beberapa akun
    accounts = youtube_account_manager.bulk_create_accounts(num_accounts=3)
    
    # Tampilkan akun yang berhasil dibuat
    print("Akun YouTube yang Berhasil Dibuat:")
    for account in accounts:
        print(f"Email: {account.get('email', 'N/A')}")
        print(f"Username: {account.get('username', 'N/A')}")
        print("---")

# Jalankan test
if __name__ == "__main__":
    test_youtube_account_manager()