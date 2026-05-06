import os
import allure
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_healed_selector(broken_selector, error_message, html_content):
    prompt = f"""
    Sen bir Senior QA Automation Engineer'sın. 
    Hata Alan Selector: '{broken_selector}'
    Hata Mesajı: {error_message}
    
    Aşağıdaki HTML kesitinde bu elementin yeni halini bul ve SADECE en doğru CSS selector'ı döndür.
    Markdown veya açıklama ekleme.
    
    HTML:
    {html_content[:30000]}
    """
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    raw_content = response.choices[0].message.content.strip()        
    clean_selector = raw_content.replace("```css", "").replace("```", "").strip()

    # --- ALLURE REPORTING ---
    try:
        with allure.step("🤖 AI Self-Healing: HTML Analizi"):
            allure.attach(
                f"Bozuk Selector: {broken_selector}\n"
                f"AI Tarafından Önerilen: {clean_selector}\n"
                f"Yöntem: DOM Parsing",
                name="Self-Healing Detayları",
                attachment_type=allure.attachment_type.TEXT
            )
    except Exception:
        pass # Allure kurulu olmayan ortamlar için koruma
    # ------------------------

    return clean_selector
    #return "button#hatalıId" # Vision AI devreye girmesi için

def get_vision_analysis(broken_selector, base64_image):
    prompt = f"Şu selector çalışmıyor: {broken_selector}. Ekran görüntüsüne bakarak bu butonun yeni selector'ını bul. Sadece selector'ı döndür."
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{base64_image}"}
                    },
                ],
            }
        ],
        max_tokens=300,
    )
    raw_content = response.choices[0].message.content.strip()    
    clean_selector = raw_content.replace("```css", "").replace("```", "").strip()

    # --- ALLURE REPORTING ---
    try:
        with allure.step("🤖 AI Self-Healing: Vision AI (Görüntü İşleme)"):
            allure.attach(
                f"Bozuk Selector: {broken_selector}\n"
                f"Vision AI Tespit Edilen: {clean_selector}\n"
                f"Yöntem: Computer Vision",
                name="Vision AI Onarım Detayları",
                attachment_type=allure.attachment_type.TEXT
            )
            allure.attach(
                base64_image, 
                name="AI Analiz Ekran Görüntüsü", 
                attachment_type=allure.attachment_type.PNG
            )
    except Exception:
        pass
    # ------------------------
    
    return clean_selector  

def analyze_failure(error_message, logs=None):
    prompt = f"""
    Sen bir Senior QA Automation Lead'sin. Test sonucunu analiz et:
    Hata Mesajı: {error_message}

    KARAR ALMA REHBERİ:
    1. Eğer hata 'AssertionError' ise ve beklenen/gelen değerler farklıysa, bu bir 'BUG' dır. Asla selector hatası deme!
    2. Eğer hata 'Timeout' ise , 'ENVIRONMENT' hatasıdır.
    3. Eğer hata 'NoSuchElement' ise ,'SELECTOR'hatasıdır.
    4. Eğer hata 'Server Error' içeriyorsa 'BACKEND ISSUE'dur.
    5. Eğer hata rastgele zamanlarda (timeout vb.) geliyorsa 'FLAKY' ihtimalini değerlendir.
    6. Eğer hata 'Element not interactable' ise sayfa yüklenme hızıyla ilgili bir 'ENVIRONMENTAL FLAKY' durumu olabilir.

    Analizini bu mantıkla yap ve şu formatta ver:
    - **Hata Sınıflandırması:** (BUG / ENVIRONMENT / SELECTOR / BACKEND ISSUE / FLAKY)
    - **Kök Neden:** (Neden hata aldık? Sen sistem testçisisin hata detayına odaklan ve açıkla.)
    - **Çözüm Önerisi:** (Yazılımcıya mı yoksa test verisine mi gidilmeli? Yoksa bu bir Flaky testmidir)
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip()