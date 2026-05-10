from playwright.sync_api import sync_playwright
from tests.base_page import BasePage

def test_orange_hrm_login():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        bp = BasePage(page) 
        
        page.goto("https://opensource-demo.orangehrmlive.com/")
        page.wait_for_load_state("networkidle")
        #Test 1
        bp.smart_fill("input[name='username']", "Admin")
        bp.smart_fill("input[name='password']", "admin123")        
        bp.smart_click("button[id='gecersiz-id-123']")
        bp.assert_url_contains("dashboard")
        #Test 2 
        bp.smart_click("text=Admin")        
        dropdown_selector = page.locator(".oxd-input-group").filter(has_text="User Role").locator(".oxd-select-wrapper")
        bp.smart_dropdown(dropdown_selector, "Admin")
        bp.smart_click("button[type='submit']")

        
        print("📋 Sonuçlar kontrol ediliyor...") 
        # Listede en az bir kayıt (Admin kullanıcısı) olmalı       
        
        bp.assert_text_equals("div.oxd-table-card >> nth=0 >> div[role='cell'] >> nth=1", "Admin")

        print("🎉 Test başarıyla tamamlandı!")
        page.wait_for_timeout(3000)
        browser.close()

if __name__ == "__main__":
    test_orange_hrm_login()