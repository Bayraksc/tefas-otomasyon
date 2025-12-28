from tefas import Crawler
import pandas as pd
from datetime import datetime, timedelta

# --- AYARLAR ---
FONLAR = ["TI3", "IDH", "MAC", "GMR", "TCD"]

def verileri_getir():
    crawler = Crawler()
    
    bugun = datetime.now().date()
    # 5 günlük tarama yeterli ve hızlıdır
    baslangic = bugun - timedelta(days=5) 
    
    print(f"Tarama: {baslangic} - {bugun}")

    try:
        # Veriyi çek
        df = crawler.fetch(start=str(baslangic), end=str(bugun))
        
        if df is None or df.empty:
            print("Veri bulunamadı, boş dosya oluşturuluyor.")
            # Boş dosya oluştur ama başlıkları ekle
            with open("guncel_fonlar.csv", "w") as f:
                f.write("Tarih;Fon Kodu;Fon Adi;Fiyat\n")
            return

        # Filtreleme
        df_bizim = df[df['code'].isin(FONLAR)].copy()
        
        # En güncel veriyi al
        df_bizim = df_bizim.sort_values(by='date', ascending=False)
        df_sonuc = df_bizim.drop_duplicates(subset=['code'], keep='first')
        
        # Sütunları seç
        df_sonuc = df_sonuc[['date', 'code', 'title', 'price']]
        
        # --- KRİTİK MÜDAHALE (TÜRKÇELEŞTİRME) ---
        # 1. Fiyat sütununu metne çevir ve noktayı virgüle yap
        df_sonuc['price'] = df_sonuc['price'].astype(str).str.replace('.', ',', regex=False)
        
        # 2. Kaydederken ayırıcı olarak 'sep=;' kullanıyoruz.
        # Böylece virgüllü fiyatlar sütunları karıştırmaz.
        df_sonuc.to_csv("guncel_fonlar.csv", index=False, encoding='utf-8-sig', sep=';')
        
        print("BAŞARILI: Veriler Türkçe formatında (;) kaydedildi.")
        print(df_sonuc)

    except Exception as e:
        print(f"HATA: {e}")

if __name__ == "__main__":
    verileri_getir()
