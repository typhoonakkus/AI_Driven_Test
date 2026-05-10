import pytest
from tests.base_page import BasePage
import allure
from ai_client import analyze_failure
from vector_store import TestMemory 

memory = TestMemory()

@pytest.fixture
def bp(page, request):
    return BasePage(page, request)

def pytest_addoption(parser):
    parser.addoption("--env", action="store", default="UAT", help="Çalışılacak ortam: UAT veya INT")

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    
    if report.when == "call" and report.failed:
        page = item.funcargs.get('page') if 'page' in item.funcargs else None
        
        if page:
            try:             
                page.wait_for_load_state("networkidle") 
                screenshot = page.screenshot(full_page=True)
                allure.attach(
                    screenshot, 
                    name="❌ HATA ANI EKRAN GÖRÜNTÜSÜ", 
                    attachment_type=allure.attachment_type.PNG
                )
            except Exception as e:
                print(f"Screenshot alınamadı: {e}")

        # --- AI Analizini Rapora Yansıt ---
        error_msg = str(report.longreprtext)
        test_id = item.nodeid
        with allure.step("🤖 AI Hata Analizi (Root Cause Analysis)"):
            try:                
                ai_analysis = analyze_failure(error_msg, test_id)               
                
                allure.attach(
                    ai_analysis,
                    name="AI Kök Neden Analizi ve Sınıflandırma",
                    attachment_type=allure.attachment_type.TEXT
                )
                
            except Exception as e:
                allure.attach(f"AI Analizi sırasında hata: {str(e)}", name="AI Hata")