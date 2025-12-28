from tefas import Crawler
import pandas as pd
from datetime import datetime, timedelta
import os

# --- AYARLAR ---
# Takip etmek istediğiniz fonları buraya ekleyin
FONLAR = ["TI3", "IDH", "MAC", "GMR", "TCD"]

def verileri_getir():
    crawler = Crawler()
    
    # Hafta sonu riskine karşı son 3 günü tarayalım, en güncelini alalım
    bugun = datetime.now().date()
    baslangic = bugun - timedelta(days=3) 
    
    print(f"{baslangic} ile {bugun} arasındaki veriler taranıyor...")

    try:
        # TEFAS'tan veriyi çek
        df = crawler.fetch(start_date=str(baslangic), end_date=str(bugun))
        
        if df is None or df.empty:
            print("Veri bulunamadı!")
            return

        # Sadece bizim fonları filtrele
        df_bizim = df[df['code'].isin(FONLAR)].copy()
        
        # Sütunları düzenle (Tarih, Kod, Fon Adı, Fiyat)
        df_sonuc = df_bizim[['date', 'code', 'title', 'price']]
        
        # Tarihe göre sırala (En yeni en üstte olsun)
        df_sonuc = df_sonuc.sort_values(by='date', ascending=False)
        
        # CSV Dosyasına Kaydet
        # index=False -> Satır numaralarını yazma
        df_sonuc.to_csv("guncel_fonlar.csv", index=False)
        
        print("İşlem Başarılı! guncel_fonlar.csv dosyası oluşturuldu.")
        print(df_sonuc.head())

    except Exception as e:
        print(f"Bir hata oluştu: {e}")

if __name__ == "__main__":
    verileri_getir()
