from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv

# --- AYARLAR ---
fon_kodlari = ["ATE", "HES", "AMZ", "YKT", "MAC", "IDH", "AMF", "FFZ", "YLB", "FEI", "AJR", "BPH", "AFA", "ALI", "AHL", "HKM", "CFA", "YDI", "CHG", "AGA", "TGE"]
dosya_adi = "fon_fiyatlari.csv"

def get_tefas_price_optimized():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--log-level=3") # Gereksiz logları gizle
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36")
    
    # --- KRİTİK HIZ AYARLARI ---
    # 1. Sayfanın tam yüklenmesini bekleme, HTML oluşunca dal.
    chrome_options.page_load_strategy = 'eager' 
    
    # 2. Resimleri ve gereksiz içerikleri yükleme
    prefs = {
        "profile.managed_default_content_settings.images": 2, # Resim yok
        "profile.managed_default_content_settings.stylesheets": 2, # CSS yok (bazen yapı bozabilir ama hız katar)
    }
    chrome_options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(options=chrome_options)
    print(f"🚀 (TURBO MOD) Veri çekme işlemi başladı... ({len(fon_kodlari)} Fon)")
    print("-" * 30)

    start_time = time.time()

    with open(dosya_adi, mode='w', newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['Fon Kodu', 'Son Fiyat'])

        for fon in fon_kodlari:
            try:
                url = f"https://www.tefas.gov.tr/FonAnaliz.aspx?FonKod={fon}"
                driver.get(url)

                # Bekleme süresini düşürdük çünkü eager modda HTML zaten hazırdır
                wait = WebDriverWait(driver, 5)
                fiyat_elementi = wait.until(EC.presence_of_element_located((By.XPATH, "//ul[@class='top-list']/li[1]/span")))
                fiyat = fiyat_elementi.text
                
                print(f"✅ {fon}: {fiyat}")
                writer.writerow([fon, fiyat])

            except Exception as e:
                print(f"❌ {fon}: Veri alınamadı.")
                writer.writerow([fon, "HATA"])
    
    driver.quit()
    duration = time.time() - start_time
    print("-" * 30)
    print(f"🛑 İşlem {duration:.2f} saniyede tamamlandı. Veriler '{dosya_adi}' dosyasında.")

if __name__ == "__main__":
    get_tefas_price_optimized()
