from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import pandas as pd
import time
from datetime import datetime

# --- TÜM LİSTE (YATIRIM + EMEKLİLİK + OKS) ---
FONLAR = list(set([
    "AJR", "CHG", "ATE", "CFA", "HES", "AHL", "ALI", "BPH", 
    "FEI", "AGA", "AMF", "AMZ", "FFZ", "YLB", "YKT", "YDI", 
    "AFA", "HKM", "IDH", "MAC", "TGE"
]))

def verileri_getir():
    print("🚀 Gizli Selenium Motoru Başlatılıyor...")

    # --- AYARLAR: KİMLİK GİZLEME (ANTI-BOT) ---
    chrome_options = Options()
    chrome_options.add_argument("--headless") 
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    # ÖNEMLİ 1: Pencere boyutu ver (Robotlar genelde 0x0 olur)
    chrome_options.add_argument("--window-size=1920,1080")
    # ÖNEMLİ 2: Gerçek insan kimliği (User-Agent)
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    sonuclar = []

    try:
        for fon_kodu in FONLAR:
            url = f"https://www.tefas.gov.tr/FonAnaliz.aspx?FonKod={fon_kodu}"
            print(f"-> {fon_kodu} taranıyor...")
            
            try:
                driver.get(url)
                # ÖNEMLİ 3: Sayfanın tam yüklenmesi için 3 saniye bekle
                time.sleep(3) 

                # --- VERİYİ SÖK AL ---
                
                # 1. Fiyat (Üst barın ilk kutusu)
                # CSS Selector XPath'e göre daha sağlamdır
                fiyat_element = driver.find_element(By.CSS_SELECTOR, ".top-list > li:nth-child(1) > span")
                fiyat_text = fiyat_element.text
                
                # 2. Tarih (Parantez içindeki tarih)
                tarih_element = driver.find_element(By.CSS_SELECTOR, ".top-list > li:nth-child(1)")
                tarih_ham = tarih_element.text # "Son Fiyat (27.12.2025)"
                tarih_str = tarih_ham.split('(')[-1].split(')')[0]
                
                # 3. Fon Adı
                baslik_element = driver.find_element(By.ID, "MainContent_PanelInfo")
                baslik_text = baslik_element.find_element(By.TAG_NAME, "h1").text

                print(f"   ✅ Bulundu: {fiyat_text} - {tarih_str}")

                sonuclar.append({
                    'Tarih': tarih_str,
                    'Fon Kodu': fon_kodu,
                    'Fon Adi': baslik_text,
                    'Fiyat': fiyat_text
                })
                
            except Exception as e:
                # Hata olursa o anki sayfanın başlığını yazdıralım ki ne olduğunu anlayalım
                page_title = driver.title
                print(f"   ❌ HATA ({fon_kodu}): Eleman bulunamadı. Sayfa Başlığı: {page_title}")
                # Hata detayını kısa kes
                continue

    except Exception as e:
        print(f"GENEL HATA: {e}")
    finally:
        driver.quit()
        print("🛑 Tarayıcı Kapatıldı.")

    # --- CSV KAYIT ---
    if sonuclar:
        df = pd.DataFrame(sonuclar)
        
        # Tarihe göre sırala
        df['Tarih_Obj'] = pd.to_datetime(df['Tarih'], format='%d.%m.%Y', errors='coerce')
        df = df.sort_values(by='Tarih_Obj', ascending=False)
        df = df.drop(columns=['Tarih_Obj'])

        # Kaydet
        df.to_csv("guncel_fonlar.csv", index=False, encoding='utf-8-sig', sep=';')
        
        print(f"\nBAŞARILI! {len(df)} adet fon verisi çekildi.")
        print(df[['Tarih', 'Fon Kodu', 'Fiyat']])
    else:
        print("HATA: Liste boş kaldı.")

if __name__ == "__main__":
    verileri_getir()
