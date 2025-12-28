from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import pandas as pd
import time
from datetime import datetime

# --- SENİN LİSTEN (HEPSİ) ---
FONLAR = list(set([
    "AJR", "CHG", "ATE", "CFA", "HES", "AHL", "ALI", "BPH", 
    "FEI", "AGA", "AMF", "AMZ", "FFZ", "YLB", "YKT", "YDI", 
    "AFA", "HKM", "IDH", "MAC", "TGE"
]))

def verileri_getir():
    print("🚀 Selenium Motoru Başlatılıyor...")

    # 1. CHROME AYARLARI (HEADLESS MOD)
    # GitHub sunucusunda ekran olmadığı için 'headless' olmak zorunda.
    chrome_options = Options()
    chrome_options.add_argument("--headless") 
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    
    # Tarayıcıyı Başlat
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    sonuclar = []

    try:
        # Her fon için tek tek sayfasına git
        for fon_kodu in FONLAR:
            url = f"https://www.tefas.gov.tr/FonAnaliz.aspx?FonKod={fon_kodu}"
            print(f"-> {fon_kodu} bağlanılıyor...")
            
            driver.get(url)
            # Sayfanın yüklenmesi için kısa bir bekleme (Garanti olsun)
            time.sleep(1) 
            
            try:
                # --- VERİYİ SAYFADAN KAZIMA (SCRAPING) ---
                
                # 1. Fiyatı Bul (Genelde üst barda olur)
                # XPath: class'ı 'top-list' olan ul'nin ilk li'sinin içindeki span
                fiyat_element = driver.find_element(By.XPATH, "//*[@id='MainContent_PanelInfo']/div[1]/ul/li[1]/span")
                fiyat_text = fiyat_element.text
                
                # 2. Tarihi Bul (Son Fiyat (27.12.2025) yazan yer)
                tarih_element = driver.find_element(By.XPATH, "//*[@id='MainContent_PanelInfo']/div[1]/ul/li[1]")
                tarih_text_raw = tarih_element.text # "Son Fiyat (26.12.2025)" gelir
                
                # Tarihi parantez içinden söküp alalım
                # Örnek metin: "Son Fiyat (26.12.2025)" -> "26.12.2025"
                tarih_str = tarih_text_raw.split('(')[-1].split(')')[0]
                
                # Fon Adını Bul
                baslik_element = driver.find_element(By.XPATH, "//*[@id='MainContent_PanelInfo']/h1")
                baslik_text = baslik_element.text

                # Veriyi listeye ekle
                sonuclar.append({
                    'Tarih': tarih_str,
                    'Fon Kodu': fon_kodu,
                    'Fon Adi': baslik_text,
                    'Fiyat': fiyat_text
                })
                
            except Exception as e:
                print(f"HATA ({fon_kodu}): Veri okunamadı. Sayfa yapısı farklı olabilir. {e}")
                continue

    except Exception as e:
        print(f"GENEL HATA: {e}")
    finally:
        # İş bitince tarayıcıyı kapat (RAM şişmesin)
        driver.quit()
        print("🛑 Tarayıcı Kapatıldı.")

    # --- CSV OLUŞTURMA ---
    if sonuclar:
        df = pd.DataFrame(sonuclar)
        
        # Tarih formatını standartlaştır (Opsiyonel, sıralama için iyi olur)
        df['Tarih_Obj'] = pd.to_datetime(df['Tarih'], format='%d.%m.%Y', errors='coerce')
        df = df.sort_values(by='Tarih_Obj', ascending=False)
        df = df.drop(columns=['Tarih_Obj']) # Yardımcı sütunu sil

        # Fiyat zaten virgüllü geliyor TEFAS'tan (TR formatında), dokunmaya gerek yok.
        # Sadece emin olmak için temizlik yapabiliriz ama Selenium gördüğünü alır.
        
        # Dosyayı kaydet
        df.to_csv("guncel_fonlar.csv", index=False, encoding='utf-8-sig', sep=';')
        
        print(f"\nBAŞARILI! {len(df)} fon verisi Selenium ile çekildi.")
        print(df)
    else:
        print("HATA: Hiçbir veri listeye eklenemedi.")

if __name__ == "__main__":
    verileri_getir()
