# Modul untuk membuat akun Google otomatis

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import random
import string

class GoogleAccountCreator:
    def __init__(self, browser_manager):
        """
        Inisialisasi pembuat akun Google
        :param browser_manager: Instance dari BrowserManager
        """
        self.browser_manager = browser_manager
    
    def generate_random_username(self, length=8):
        """
        Generate username acak
        :param length: Panjang username
        :return: Username acak
        """
        # Kombinasi huruf dan angka
        characters = string.ascii_lowercase + string.digits
        username = ''.join(random.choice(characters) for _ in range(length))
        return username
    
    def generate_strong_password(self, length=12):
        """
        Generate password kuat
        :param length: Panjang password
        :return: Password acak
        """
        # Kombinasi huruf besar, kecil, angka, dan karakter spesial
        characters = (
            string.ascii_lowercase + 
            string.ascii_uppercase + 
            string.digits + 
            "!@#$%^&*"
        )
        password = ''.join(random.choice(characters) for _ in range(length))
        return password
    
    def create_google_account(self):
        """
        Proses otomatis membuat akun Google
        :return: Detail akun (username, password)
        """
        # Buat browser baru
        driver = self.browser_manager.create_browser()
        
        try:
            # Buka halaman pendaftaran Google
            driver.get("https://accounts.google.com/signup")
            
            # Generate kredensial
            username = self.generate_random_username()
            password = self.generate_strong_password()
            
            # Contoh pengisian form (lokator bisa berbeda)
            # Catatan: Ini adalah simulasi, aktual bisa berbeda
            first_name_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "firstName"))
            )
            first_name_input.send_keys("AI Test")
            
            # Lanjutkan dengan pengisian form lainnya
            # Username
            username_input = driver.find_element(By.NAME, "username")
            username_input.send_keys(username)
            
            # Password
            password_input = driver.find_element(By.NAME, "password")
            password_input.send_keys(password)
            
            # Konfirmasi password
            confirm_password_input = driver.find_element(By.NAME, "confirm")
            confirm_password_input.send_keys(password)
            
            # Klik tombol selanjutnya
            next_button = driver.find_element(By.XPATH, "//button[@type='submit']")
            next_button.click()
            
            # Tunggu proses verifikasi
            WebDriverWait(driver, 20).until(
                EC.url_contains("challenge")
            )
            
            # Catatan: Verifikasi tambahan mungkin diperlukan
            
            return {
                "username": username,
                "password": password,
                "email": f"{username}@gmail.com"
            }
        
        except Exception as e:
            print(f"Error membuat akun: {e}")
            return None
        finally:
            # Tutup browser
            driver.quit()

# Contoh penggunaan
def test_account_creator():
    from browser_manager import BrowserManager
    
    # Inisialisasi
    browser_manager = BrowserManager()
    account_creator = GoogleAccountCreator(browser_manager)
    
    # Buat akun
    account_details = account_creator.create_google_account()
    
    if account_details:
        print("Akun berhasil dibuat:")
        print(f"Username: {account_details['username']}")
        print(f"Email: {account_details['email']}")
    else:
        print("Gagal membuat akun")

# Jalankan test jika file dieksekusi langsung
if __name__ == "__main__":
    test_account_creator()