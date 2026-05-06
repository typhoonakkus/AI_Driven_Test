🤖 AI-Powered QA Automation Framework
Bu proje, modern yazılım test süreçlerini yapay zeka ile hızlandırmak ve bakım maliyetlerini minimize etmek amacıyla geliştirilmiş, Self-Healing (Kendi Kendini Onaran) özellikli bir test otomasyon framework'üdür.

🚀 Öne Çıkan Özellikler
BDD (Behavior Driven Development): pytest-bdd ile Gherkin dilinde yazılmış, teknik olmayan paydaşların da anlayabileceği test senaryoları.

AI Self-Healing: Selector'lar değiştiğinde GPT-4o kullanarak HTML analizi yapar ve testi durdurmadan doğru elementi bulur.

Computer Vision Destekli Onarım: DOM analizi yetersiz kaldığında Vision AI ile ekran görüntüsü üzerinden element tespiti yapar.

Data-Driven Testing: Scenario Outline yapısıyla farklı veri setleriyle geniş kapsamlı test koşumu.

Gelişmiş Raporlama: Allure Report entegrasyonu ile her test adımının, ekran görüntüsünün ve AI müdahale loglarının görselleştirilmesi.

Paralel Koşum: pytest-xdist desteği ile çoklu tarayıcıda hızlı test execution.

🛠 Teknolojiler
Dil: Python 3.12+

Motor: Playwright

Test Runner: Pytest

AI: OpenAI GPT-4o (Vision & Text)

Raporlama: Allure Framework

📂 Proje Yapısı
Plaintext
├── tests/
│   ├── features/          # .feature (Gherkin) dosyaları
│   └── step_defs/         # Python step tanımlamaları
├── pages/
│   ├── base_page.py       # AI ve Playwright fonksiyonlarının kalbi
│   └── ai_client.py       # OpenAI entegrasyonu ve Self-Healing mantığı
├── allure-results/        # Test koşumundan sonra oluşan rapor verileri
├── .env                   # API Anahtarları (Gizli tutulmalıdır)
├── pytest.ini             # Log ve test konfigürasyonları
└── requirements.txt       # Bağımlılık listesi
⚙️ Kurulum
Sanal Ortamı Aktif Edin:

Bash
.\venv\Scripts\activate
Bağımlılıkları Yükleyin:

Bash
pip install -r requirements.txt
Playwright Tarayıcılarını Kurun:

Bash
playwright install
.env Dosyasını Yapılandırın:
OPENAI_API_KEY=your_key_here

🏃 Testleri Koşturma
Standart Koşum:
pytest

Rapor Üreterek Koşum:
pytest --alluredir=allure-result

Ortam Bazlı Koşum:
pytest --env=UAT --alluredir=allure-results

Farklı Browserlarda koşum:
Chromium: pytest --browser chromium --alluredir=allure-results
Firefox: pytest --browser firefox --alluredir=allure-results
Edge: pytest --browser webkit --alluredir=allure-results

Raporu Görüntüleme:
allure serve allure-results

Paralel Koşum (2 Thread):
pytest -n 2



🧠 AI Self-Healing Nasıl Çalışır?
Test sırasında bir element bulunamazsa sistem sırasıyla şu adımları izler:

Hata Yakalama: Standart Playwright hatası oluşmadan önce müdahale edilir.

HTML Analizi: Mevcut sayfa kaynağı AI'ya gönderilir ve en yakın selector istenir.

Vision Analizi: Eğer HTML analizi başarısız olursa, sayfa resmi çekilip Vision AI ile koordinat/selector tespiti yapılır.

Raporlama: Yapılan tüm bu onarımlar Allure raporunda "🤖 AI Self-Healing Log" başlığıyla detaylıca raporlanır.

Geliştiren: Typhoon - QA Lead & Test Architect