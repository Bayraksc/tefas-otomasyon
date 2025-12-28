from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
from datetime import datetime

# --- LİSTE ---
FONLAR = list(set([
    "AJR", "CHG", "ATE", "CFA", "HES", "AHL", "ALI", "BPH", 
    "FEI", "AGA", "AMF", "AMZ", "FFZ", "YLB", "YKT", "YDI", 
    "AFA", "HKM", "IDH", "MAC", "TGE"
]))

def verileri_getir():
    print("🚀 PRO Selenium Motoru Başlatılıyor (Anti-Detect Modu)...")

    # --- AYARLAR: GELİŞMİŞ GİZLİLİK ---
    chrome_options = Options()
    chrome_options.add_argument("--headless") 
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    # Robotu gizleyen kritik komutlar
    chrome_options.add_argument("--disable-blink-features=AutomationControlled") 
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    # JavaScript ile 'navigator.webdriver' özelliğini siliyoruz (Robot olduğumuzu gizler)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    sonuclar = []

    try:
        # 1. ADIM: OTURUM ISITMA (Session Priming)
        # Doğrudan fon linkine gitmeden önce ana sayfaya gidip "Cookie" alıyoruz.
        print("🌍 Ana sayfaya bağlanılıyor (Oturum Açılıyor)...")
        driver.get("https://www.tefas.gov.tr")
        time.sleep(3) # Çerezlerin oturması için bekle

        for fon_kodu in FONLAR:
            url = f"https://www.tefas.gov.tr/FonAnaliz.aspx?FonKod={fon_kodu}"
            print(f"-> {fon_kodu} verisi isteniyor...")
            
            try:
                driver.get(url)
                
                # AKILLI BEKLEME (Explicit Wait)
                # Sayfanın yüklenmesini değil, "Son Fiyat" yazan kutunun belirmesini bekle (Max 20 sn)
                wait = WebDriverWait(driver, 20)
                
                # Fiyat elementini bekle (.top-list içindeki ilk span)
                fiyat_element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".top-list > li:nth-child(1) > span")))
                fiyat_text = fiyat_element.text
                
                # Tarihi al
                tarih_element = driver.find_element(By.CSS_SELECTOR, ".top-list > li:nth-child(1)")
                tarih_ham = tarih_element.text 
                tarih_str = tarih_ham.split('(')[-1].split(')')[0]
                
                # Başlığı al
                baslik_element = driver.find_element(By.ID, "MainContent_PanelInfo")
                baslik_text = baslik_element.find_element(By.TAG_NAME, "h1").text

                print(f"   ✅ ALINDI: {fiyat_text} | {baslik_text}")

                sonuclar.append({
                    'Tarih': tarih_str,
                    'Fon Kodu': fon_kodu,
                    'Fon Adi': baslik_text,
                    'Fiyat': fiyat_text
                })
                
            except Exception as e:
                # Hata durumunda sayfanın o anki HTML'inden ufak bir parça göster ki ne olduğunu anlayalım
                body_text = driver.find_element(By.TAG_NAME, "body").text[:100]
                print(f"   ❌ HATA ({fon_kodu}): Veri gelmedi. Sayfada görünen: {body_text}...")
                continue

    except Exception as e:
        print(f"GENEL SİSTEM HATASI: {e}")
    finally:
        driver.quit()
        print("🛑 Tarayıcı Kapatıldı.")

    # --- CSV KAYIT ---
    if sonuclar:
        df = pd.DataFrame(sonuclar)
        
        # Tarih Sıralama
        df['Tarih_Obj'] = pd.to_datetime(df['Tarih'], format='%d.%m.%Y', errors='coerce')
        df = df.sort_values(by='Tarih_Obj', ascending=False)
        df = df.drop(columns=['Tarih_Obj'])

        # Kaydet
        df.to_csv("guncel_fonlar.csv", index=False, encoding='utf-8-sig', sep=';')
        
        print(f"\nBAŞARILI! Toplam {len(df)} fon verisi CSV'ye yazıldı.")
        print(df[['Tarih', 'Fon Kodu', 'Fiyat']])
    else:
        print("HATA: Hiçbir veri çekilemedi. TEFAS robotu engelliyor olabilir.")

if __name__ == "__main__":
    verileri_getir()
