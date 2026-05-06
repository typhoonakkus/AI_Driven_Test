from ai_client import get_healed_selector, get_vision_analysis
from playwright.sync_api import expect
import base64
import time
import re
import allure
import os

class BasePage:
    def __init__(self, page, request=None):
        self.page = page
        self.env = request.config.getoption("--env").upper() if request else "UAT"
        self.base_url = os.getenv(f"{self.env}_URL")

    def goto_base_url(self):        
        if self.base_url:
            self.page.goto(self.base_url)
        else:
            raise Exception("HATA: .env dosyasında BASE_URL tanımlanmamış!")

    def smart_fill(self, selector, value):
        try:            
            self.page.fill(selector, value, timeout=3000)
        except Exception as e1:
            print(f"⚠️ '{selector}' alanına yazılamadı. HTML analizi deneniyor...")  

            # 1. ADIM: HTML Analizi
            try:                
                new_selector = get_healed_selector(selector, str(e1), self.page.content())
                self.page.fill(new_selector, value, timeout=3000)                
                print(f"📌 [SELF-HEALING REPORT]: '{selector}' değişmiş. Yeni hali: '{new_selector}' olarak güncellendi.")
            except Exception as e2:
                print("❌ HTML analizi yetersiz kaldı. Görsel (Vision) analizi başlatılıyor...")
                
                # 2. ADIM: Görsel (Vision) Analizi
                try:                    
                    screenshot_path = f"logs/fill_error_{int(time.time())}.png"
                    self.page.screenshot(path=screenshot_path)                  
                    
                    with open(screenshot_path, "rb") as f:
                        base64_image = base64.b64encode(f.read()).decode('utf-8')

                    # Vision modeline hem bozulan selector'ı hem görseli gönderme
                    vision_selector = get_vision_analysis(selector, base64_image)
                    
                    print(f"🤖 Vision AI input alanını tespit etti: {vision_selector}")
                    self.page.fill(vision_selector, value, timeout=3000)
                    print(f"🚀 Vision sayesinde '{value}' değeri başarıyla yazıldı.")
                except Exception as final_error:
                    print(f"💀 Kritik Hata: Alan hiçbir yöntemle doldurulamadı. {final_error}")
                    raise                     

    def smart_click(self, selector):
        try:            
            self.page.click(selector, timeout=3000)
            print(f"✅ Click başarılı : {selector}")
        except Exception as e1:
            print(f"⚠️ HTML analizi başlıyor: {selector}")
            
            try:
                # 1. ADIM: HTML Analizi

                new_selector = get_healed_selector(selector, str(e1), self.page.content())                
                self.page.click(new_selector, timeout=2000)
                print(f"📌 [SELF-HEALING REPORT]: '{selector}' değişmiş. Yeni hali: '{new_selector}' olarak güncellendi.")
                
            except Exception:
                # 3. ADIM: Vision Analizi     
                           
                print("❌ HTML analizi hatalı selector verdi veya tıklayamadı. Vision devreye giriyor...")

                screenshot_path = f"logs/error_{int(time.time())}.png"
                self.page.screenshot(path=screenshot_path)
                
                with open(screenshot_path, "rb") as f:
                    base64_image = base64.b64encode(f.read()).decode('utf-8')
                
                vision_selector = get_vision_analysis(selector, base64_image)
                print(f"🤖 Vision AI tespit etti: {vision_selector}")
                
                self.page.click(vision_selector, timeout=3000)

    def smart_dropdown(self, dropdown_selector, option_text):
        try:            
            print(f"Opening dropdown: {dropdown_selector}")
            self.smart_click(dropdown_selector)
            self.page.wait_for_timeout(500)             
            
            option_locator = f"//*[contains(text(), '{option_text}')]"
            try:                
                self.smart_click(option_locator)
                print(f"✅ Seçim başarılı: {option_text}")
            except Exception as e1:
                print(f"⚠️ Seçim başarısız '{option_text}' seçilemedi. AI Healing... ****HATA: {e1}")
                
                try:
                    # 1. ADIM: HTML Healing
                    new_option_selector = get_healed_selector(option_locator, str(e1), self.page.content())
                    self.page.click(new_option_selector, timeout=2000)
                    print(f"✅ HTML Healing ile seçildi: {new_option_selector}")
                except Exception:
                    # 2. ADIM: VISION HEALING
                    print(f"❌ HTML ile başarısız olundu. Vision ile '{option_text}' aranıyor...")
                    
                    screenshot_path = f"logs/dropdown_error_{int(time.time())}.png"
                    self.page.screenshot(path=screenshot_path)
                    
                    with open(screenshot_path, "rb") as f:
                        base64_image = base64.b64encode(f.read()).decode('utf-8')
                    
                    # "Ekranda bu metni içeren tıklanabilir yeri bul"
                    vision_selector = get_vision_analysis(f"Dropdown içindeki '{option_text}' seçeneği", base64_image)
                    
                    print(f"🤖 Vision AI seçeneği buldu: {vision_selector}")
                    self.page.click(vision_selector, timeout=3000)
        except Exception as final_e:
            print(f" ****Dropdown tıklama hata verdi: {final_e}")
            raise final_e

    def _smart_report(self, step_name, action_func, selector=None):
        
        with allure.step(f"🔍 {step_name}"):
            try:               
                if selector:                   
                    self.page.locator(selector).wait_for(state="visible", timeout=5000)              
                
                self.page.wait_for_load_state("networkidle") 

                screenshot = self.page.screenshot(full_page=False)
                allure.attach(
                    screenshot, 
                    name=f"Screenshot: {step_name}", 
                    attachment_type=allure.attachment_type.PNG
                )               
                
                action_func()
                print(f"✅ {step_name} Başarılı.")
                
            except Exception as e:
                print(f"❌ {step_name} HATALI!")
                raise e

    def assert_element_exists(self, selector, timeout=5000):
        """Elementin sayfada mevcut olduğunu doğrular."""
        def action():
            expect(self.page.locator(selector)).to_be_visible(timeout=timeout)
        
        self._smart_report(f"Element Kontrolü: {selector}", action, selector=selector)

    def assert_text_equals(self, selector, expected_text):
        """Elementin içindeki metnin beklenen değerle aynı olduğunu doğrular."""
        def action():            
            expect(self.page.locator(selector)).to_have_text(expected_text)
            
        self._smart_report(f"Metin Doğrulama: '{expected_text}'", action, selector=selector)

    def assert_url_contains(self, partial_url):
        """URL'in belirli bir metni içerdiğini doğrular."""
        def action():
            expect(self.page).to_have_url(re.compile(f".*{partial_url}.*"), timeout=5000)
            
        self._smart_report(f"URL İçerik Kontrolü: {partial_url}", action)