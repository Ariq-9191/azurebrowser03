# Modul Otomatisasi Interaksi Video YouTube

import random
import time
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class YouTubeVideoInteraction:
    def __init__(self, driver, human_simulator):
        """
        Inisialisasi interaksi video
        :param driver: Instance WebDriver
        :param human_simulator: Instance HumanBehaviorSimulator
        """
        self.driver = driver
        self.simulator = human_simulator
        self.logger = logging.getLogger(__name__)
    
    def search_video(self, query):
        """
        Mencari video berdasarkan query
        :param query: Kata kunci pencarian
        :return: Daftar video hasil pencarian
        """
        try:
            # Temukan input pencarian
            search_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "search_query"))
            )
            
            # Simulasi pengetikan
            for char in query:
                search_input.send_keys(char)
                time.sleep(random.uniform(0.1, 0.3))
            
            # Tekan enter
            search_input.submit()
            
            # Tunggu hasil pencarian
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "video-title"))
            )
            
            # Ambil daftar video
            video_elements = self.driver.find_elements(By.ID, "video-title")
            
            return video_elements
        
        except Exception as e:
            self.logger.error(f"Gagal mencari video: {e}")
            return []
    
    def select_and_interact_video(self, video_elements, interaction_type='random'):
        """
        Memilih dan berinteraksi dengan video
        :param video_elements: Daftar elemen video
        :param interaction_type: Tipe interaksi (random, first, last)
        :return: Detail interaksi
        """
        if not video_elements:
            self.logger.warning("Tidak ada video untuk diinteraksi")
            return None
        
        try:
            # Pilih video
            if interaction_type == 'random':
                video = random.choice(video_elements)
            elif interaction_type == 'first':
                video = video_elements[0]
            elif interaction_type == 'last':
                video = video_elements[-1]
            else:
                video = random.choice(video_elements)
            
            # Scroll ke video
            self.simulator.natural_scroll(video)
            
            # Klik video
            self.simulator.human_like_click(video)
            
            # Tunggu video dimuat
            video_player = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "html5-video-player"))
            )
            
            # Interaksi dengan video
            return self._detailed_video_interaction(video_player)
        
        except Exception as e:
            self.logger.error(f"Gagal berinteraksi dengan video: {e}")
            return None
    
    def _detailed_video_interaction(self, video_player):
        """
        Interaksi mendalam dengan video
        :param video_player: Elemen video player
        :return: Detail interaksi
        """
        interaction_details = {
            'watched_duration': 0,
            'interactions': []
        }
        
        try:
            # Durasi menonton acak
            watch_duration = random.uniform(30, 180)  # 30-180 detik
            start_time = time.time()
            
            # Variasi interaksi
            interaction_methods = [
                self._pause_resume,
                self._change_volume,
                self._seek_video
            ]
            
            while time.time() - start_time < watch_duration:
                # Lakukan interaksi acak
                if random.random() < 0.3:  # 30% kesempatan interaksi
                    interaction = random.choice(interaction_methods)
                    result = interaction(video_player)
                    
                    if result:
                        interaction_details['interactions'].append(result)
                
                # Update durasi
                interaction_details['watched_duration'] = time.time() - start_time
                
                # Jeda singkat
                time.sleep(random.uniform(1, 3))
            
            return interaction_details
        
        except Exception as e:
            self.logger.error(f"Kesalahan interaksi video: {e}")
            return interaction_details
    
    def _pause_resume(self, video_player):
        """
        Pause dan resume video
        :param video_player: Elemen video player
        :return: Detail interaksi
        """
        try:
            pause_button = video_player.find_element(By.CLASS_NAME, "ytp-play-button")
            self.simulator.human_like_click(pause_button)
            
            # Pause sebentar
            time.sleep(random.uniform(1, 3))
            
            # Resume
            self.simulator.human_like_click(pause_button)
            
            return {
                'type': 'pause_resume',
                'duration': random.uniform(1, 3)
            }
        except Exception:
            return None
    
    def _change_volume(self, video_player):
        """
        Ubah volume video
        :param video_player: Elemen video player
        :return: Detail interaksi
        """
        try:
            volume_slider = video_player.find_element(By.CLASS_NAME, "ytp-volume-panel")
            self.simulator.human_like_click(volume_slider)
            
            return {
                'type': 'volume_change',
                'action': 'mute/unmute'
            }
        except Exception:
            return None
    
    def _seek_video(self, video_player):
        """
        Geser posisi video
        :param video_player: Elemen video player
        :return: Detail interaksi
        """
        try:
            progress_bar = video_player.find_element(By.CLASS_NAME, "ytp-progress-bar")
            
            # Geser ke posisi acak
            self.simulator.action_chains.move_to_element_with_offset(
                progress_bar, 
                random.uniform(0, progress_bar.size['width']), 
                0
            ).click().perform()
            
            return {
                'type': 'seek',
                'position': 'random'
            }
        except Exception:
            return None

# Contoh penggunaan
def test_youtube_video_interaction(driver, human_simulator):
    try:
        # Buka YouTube
        driver.get("https://www.youtube.com")
        
        # Inisialisasi interaksi video
        video_interaction = YouTubeVideoInteraction(driver, human_simulator)
        
        # Cari video
        videos = video_interaction.search_video("Tutorial Python")
        
        # Pilih dan interaksi video
        interaction_result = video_interaction.select_and_interact_video(videos)
        
        # Tampilkan hasil
        if interaction_result:
            print("Interaksi Video:")
            print(f"Durasi Ditonton: {interaction_result['watched_duration']:.2f} detik")
            print("Interaksi:", interaction_result['interactions'])
    
    except Exception as e:
        print(f"Kesalahan dalam test: {e}")

# Jalankan test (membutuhkan browser manager dan human simulator)
if __name__ == "__main__":
    from browser_manager import BrowserManager
    from human_simulator import HumanBehaviorSimulator
    
    # Buat browser
    browser_