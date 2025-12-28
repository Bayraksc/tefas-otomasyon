from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# --- AYARLAR ---
fon_kodlari = ["ATE", "HES", "AMZ", "YKT", "MAC", "IDH", "AMF", "FFZ", "YLB", "FEI", "AJR", "BPH", "AFA", "ALI", "AHL", "HKM", "CFA", "YDI", "CHG", "AGA", "TGE"]

def get_tefas_price():
    # Tarayıcı Ayarları (Hız için Headless mod ve Anti-Blok önlemleri)
    chrome_options = Options()
    chrome_options.add_argument("--headless") # Arka planda çalıştır (Pencere açmaz)
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(options=chrome_options)
    print(f"🚀 Veri çekme işlemi başladı... ({len(fon_kodlari)} Fon)")
    print("-" * 30)

    try:
        for fon in fon_kodlari:
            try:
                # 1. Doğrudan Fonun Detay Sayfasına Git
                url = f"https://www.tefas.gov.tr/FonAnaliz.aspx?FonKod={fon}"
                driver.get(url)

                # 2. "Son Fiyat" verisinin yüklenmesini bekle (En fazla 10 sn)
                # XPath Mantığı: 'top-list' sınıfına sahip listenin ilk elemanındaki span'ı bul.
                wait = WebDriverWait(driver, 10)
                
                # Fiyat genelde ilk sırada çıkar: Son Fiyat: X,XXXXXX
                fiyat_elementi = wait.until(EC.presence_of_element_located((By.XPATH, "//ul[@class='top-list']/li[1]/span")))
                
                fiyat = fiyat_elementi.text
                
                # Sonucu Yazdır
                print(f"✅ {fon}: {fiyat}")
                
                # Seri isteklerde IP ban yememek için minik bekleme
                time.sleep(0.5) 

            except Exception as e:
                print(f"❌ {fon}: Veri alınamadı.")
                
    except Exception as general_error:
        print(f"Genel Hata: {general_error}")
    finally:
        driver.quit()
        print("-" * 30)
        print("🛑 İşlem Tamamlandı.")

if __name__ == "__main__":
    get_tefas_price()
