import os
import allure
import json
from openai import OpenAI
from dotenv import load_dotenv
from vector_store import TestMemory

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

def get_vision_analysis(broken_selector, base64_image):
    prompt = f"""
    GÖREV: Web otomasyonunda bozulan bir selector'ı onar.
    BOZUK SELECTOR: {broken_selector}
    
    TALİMAT:
    1. Ekran görüntüsüne bak ve bu elementin yeni CSS selector'ını bul.
    2. SADECE selector metnini döndür (Örn: #username veya input[name='user']).
    3. ASLA açıklama yapma, "Özür dilerim", "Şunu deneyin" gibi cümleler kurma.
    4. Selector'ı ``` (backtick) içine alma, düz metin olarak ver.
    5. Eğer bulamazsan sadece 'NOT_FOUND' yaz.
    """
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

memory = TestMemory()

def analyze_failure(error_message, test_id="Unknown_Test"):   
    
    # 1. HAFIZADAN (VECTOR DB) BENZER HATALARI GETİR
    past_experiences = ""
    try:
        clean_query = error_message.split('\n')[0][:200]
        similar_cases = memory.get_similar_cases(clean_query, n=2)
        # Debug için terminale bas:
        print(f"DEBUG - Veritabanından gelen ham veri: {similar_cases}")
        
        if similar_cases and len(similar_cases) > 0 and len(similar_cases[0]) > 0:
            past_experiences = "\n### 🚨 GEÇMİŞ HAFIZA KAYITLARI (RAG) 🚨\n"
            for doc in similar_cases[0]:
                past_experiences += f"- {doc}\n"
            past_experiences += "----------------------------------------------------------\n"
        else:
            print("DEBUG - Benzer hata bulunamadı.")
            past_experiences = "\n(Bu hata bu test özelinde ilk kez alınıyor olabilir, hafızada benzer bir kayıt yok.)\n"
    except Exception as e:
        print(f"Hafıza sorgulama hatası: {e}")

    # 2. PROMPT'U GEÇMİŞ BİLGİLERLE ZENGİNLEŞTİR
    prompt = f"""
    Sen bir Senior QA Automation Lead'sin. Aşağıdaki hatayı 'Analiz Protokolü'ne göre incele:
    **Mevcut Hata Mesajı:** 
    {error_message}

    **Geçmiş Hafıza Kayıtları:** 
    {past_experiences}    

    ANALİZ PROTOKOLÜ (Sırasıyla Uygula):
    1. ÖNCELİK (İş Mantığı): Eğer loglarda bir 'Assertion' (beklenen/gelen uyuşmazlığı) varsa, bu bir BUG'dır. Diğer teknik logları (wait, timeout) gürültü olarak kabul et.
    2. ÖNCELİK (Yapısal): Element bulunamıyorsa (NoSuchElement/Visible), selector veya DOM yapısına odaklan.
    3. ÖNCELİK (Çevresel): Sadece zaman aşımı varsa ENVIRONMENT/FLAKY olarak değerlendir.
    4. ÖNCELİK (Backend): Eğer hata 'Server Error' içeriyorsa 'BACKEND ISSUE'dur.   
    5. Eğer hata 'Element not interactable' ise sayfa yüklenme hızıyla ilgili bir 'ENVIRONMENTAL FLAKY' durumu olabilir.
    6. [Geçmiş Hafıza Kayıtları] kısmını oku. Benzer alanda aynı hata türüne yakın benzerlik varsa analizinde mutlaka 'Bu hata daha önce de şu tarihlerde ve şu şekilde yaşanmıştı' gibi bir karşılaştırma yaparak yeni analizinle geçmiş tecrübe arasında bağ kur.

    Analizini şu formatta ver:
    - **Hata Sınıflandırması:** (BUG / ENVIRONMENT / SELECTOR / BACKEND ISSUE / FLAKY)
    - **Kök Neden:** (Teknik detaylara odaklanarak açıkla)
    - **Hafıza Sorgu Sonucu (RAG):** (Geçmişte bu hata var mıydı? Kaç kere olmuş? Geçmişteki yorumla şimdiki arasındaki fark nedir? MUTLAKA BELİRT)
    - **Çözüm Önerisi:** (Kalıcı çözüm için aksiyon planı)
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": "Sen tecrübeli bir QA Lead'sin."},
                  {"role": "user", "content": prompt}]
    )

    ai_analysis = response.choices[0].message.content.strip()

    # 3. ANALİZİ DB YE KAYDEDER
    try:
        memory.save_failure(
            test_id=test_id,
            error_msg=error_message[:500],
            ai_analysis=ai_analysis
        )
        print(f"✅ [MEMORY UPDATED]: {test_id} için yeni analiz kaydedildi.")
    except Exception as e:
        print(f"❌ [MEMORY ERROR]: Kayıt başarısız: {e}")

    return ai_analysis