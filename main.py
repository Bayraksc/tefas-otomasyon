from tefas import Crawler
import pandas as pd
from datetime import datetime, timedelta

# --- AYARLAR ---
FONLAR = ["TI3", "IDH", "MAC", "GMR", "TCD"]

def verileri_getir():
    crawler = Crawler()
    
    # Bugünün tarihi
    bugun = datetime.now().date()
    
    # Çözüm: Son 30 günü tarayalım ki araya bayram/hafta sonu girse bile veri bulsun
    baslangic = bugun - timedelta(days=30) 
    
    print(f"Tarama Aralığı: {baslangic} - {bugun}")

    try:
        # 1. Geniş tarih aralığıyla veriyi çek
        df = crawler.fetch(start_date=str(baslangic), end_date=str(bugun))
        
        if df is None or df.empty:
            print("HATA: TEFAS'tan hiç veri dönmedi.")
            return

        # 2. Sadece bizim fonları filtrele
        df_bizim = df[df['code'].isin(FONLAR)].copy()
        
        if df_bizim.empty:
            print("HATA: Seçilen fonlara ait veri bulunamadı.")
            return

        # 3. KRİTİK NOKTA: Her fon için en güncel tarihi bul
        # Tarihe göre sırala (En yeni en üstte)
        df_bizim = df_bizim.sort_values(by='date', ascending=False)
        
        # Her fon kodundan sadece ilkini (en güncelini) al
        df_sonuc = df_bizim.drop_duplicates(subset=['code'], keep='first')
        
        # Sütunları düzenle
        df_sonuc = df_sonuc[['date', 'code', 'title', 'price']]
        
        # 4. CSV oluştur (UTF-8 formatında, Excel uyumlu)
        df_sonuc.to_csv("guncel_fonlar.csv", index=False, encoding='utf-8-sig')
        
        print(f"BAŞARILI! {len(df_sonuc)} adet fon verisi kaydedildi.")
        print(df_sonuc)

    except Exception as e:
        print(f"SİSTEM HATASI: {e}")

if __name__ == "__main__":
    verileri_getir()
