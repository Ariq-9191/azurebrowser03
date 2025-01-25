# Modul Simulasi Perilaku Manusia

import random
import time
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class HumanBehaviorSimulator:
    def __init__(self, driver):
        """
        Inisialisasi simulator perilaku manusia
        :param driver: Instance WebDriver
        """
        self.driver = driver
        self.action_chains = ActionChains(driver)
    
    def natural_scroll(self, element=None, min_duration=1, max_duration=3):
        """
        Simulasi scrolling alami
        :param element: Elemen target untuk scroll
        :param min_duration: Durasi minimal scrolling
        :param max_duration: Durasi maksimal scrolling
        """
        # Jika tidak ada elemen, scroll halaman
        if element is None:
            total_height = self.driver.execute_script("return document.body.scrollHeight")
            scroll_points = random.randint(3, 7)
            
            for _ in range(scroll_points):
                # Scroll ke posisi acak
                scroll_position = random.randint(0, total_height)
                self.driver.execute_script(f"window.scrollTo(0, {scroll_position});")
                
                # Pause dengan durasi alami
                time.sleep(random.uniform(min_duration, max_duration))
        else:
            # Scroll ke elemen spesifik
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth'});", element)
            time.sleep(random.uniform(min_duration, max_duration))
    
    def human_like_click(self, element, natural_delay=True):
        """
        Klik dengan gerakan mouse alami
        :param element: Elemen yang akan diklik
        :param natural_delay: Tambahkan delay alami
        """
        try:
            # Gerakkan mouse secara bertahap
            self.action_chains.move_to_element(element).perform()
            
            # Delay sebelum klik (opsional)
            if natural_delay:
                time.sleep(random.uniform(0.5, 1.5))
            
            # Klik dengan variasi
            click_types = [
                lambda: self.action_chains.click(element).perform(),
                lambda: element.click()
            ]
            random.choice(click_types)()
        
        except Exception as e:
            print(f"Error saat klik: {e}")
    
    def random_hover(self, elements):
        """
        Hover secara acak pada beberapa elemen
        :param elements: Daftar elemen untuk hover
        """
        num_hovers = random.randint(1, min(3, len(elements)))
        selected_elements = random.sample(elements, num_hovers)
        
        for element in selected_elements:
            self.action_chains.move_to_element(element).perform()
            time.sleep(random.uniform(0.5, 2))
    
    def simulate_video_interaction(self, video_element):
        """
        Simulasi interaksi video realistis
        :param video_element: Elemen video YouTube
        """
        # Tunggu video dapat diputar
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(video_element)
        )
        
        # Interaksi awal
        self.human_like_click(video_element)
        
        # Variasi interaksi
        interactions = [
            self._pause_resume,
            self._change_volume,
            self._seek_video
        ]
        
        # Lakukan beberapa interaksi
        for _ in range(random.randint(1, 3)):
            random.choice(interactions)(video_element)
            time.sleep(random.uniform(1, 3))
    
    def _pause_resume(self, video_element):
        """
        Pause dan resume video
        """
        try:
            pause_button = self.driver.find_element(By.CLASS_NAME, "ytp-play-button")
            self.human_like_click(pause_button)
            time.sleep(random.uniform(1, 3))
            self.human_like_click(pause_button)
        except Exception:
            pass
    
    def _change_volume(self, video_element):
        """
        Ubah volume video
        """
        try:
            volume_button = self.driver.find_element(By.CLASS_NAME, "ytp-volume-panel")
            self.human_like_click(volume_button)
        except Exception:
            pass
    
    def _seek_video(self, video_element):
        """
        Geser posisi video
        """
        try:
            progress_bar = self.driver.find_element(By.CLASS_NAME, "ytp-progress-bar")
            # Geser ke posisi acak
            self.action_chains.move_to_element_with_offset(
                progress_bar, 
                random.uniform(0, progress_bar.size['width']), 
                0
            ).click().perform()
        except Exception:
            pass

# Contoh penggunaan
def test_human_simulator(driver):
    # Buka YouTube
    driver.get("https://www.youtube.com")
    
    # Inisialisasi simulator
    simulator = HumanBehaviorSimulator(driver)
    
    # Contoh scrolling
    simulator.natural_scroll()
    
    # Tunggu beberapa detik
    time.sleep(2)
    
    # Cari video
    try:
        video_elements = driver.find_elements(By.ID, "video-title")
        
        if video_elements:
            # Pilih video acak
            video = random.choice(video_elements)
            
            # Klik video
            simulator.human_like_click(video)
            
            # Tunggu video dimuat
            time.sleep(3)
            
            # Simulasi interaksi video
            video_player = driver.find_element(By.CLASS_NAME, "html5-video-player")
            simulator.simulate_video_interaction(video_player)
    
    except Exception as e:
        print(f"Error dalam simulasi: {e}")

# Jalankan test (membutuhkan browser manager)
if __name__ == "__main__":
    from browser_manager import BrowserManager
    
    # Buat browser
    browser_manager = BrowserManager()
    driver = browser_manager.create_browser()
    
    try:
        test_human_simulator(driver)
    finally:
        driver.quit()