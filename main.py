from tefas import Crawler
import pandas as pd
from datetime import datetime, timedelta

# --- AYARLAR ---
FONLAR = ["TI3", "IDH", "MAC", "GMR", "TCD"]

def verileri_getir():
    crawler = Crawler()
    
    # GARANTİ YÖNTEM: Son 10 günü tara (Tatil vs. riski yok)
    bugun = datetime.now().date()
    baslangic = bugun - timedelta(days=10) 
    
    print(f"{baslangic} ile {bugun} arası taranıyor...")

    try:
        # Veriyi çek
        df = crawler.fetch(start_date=str(baslangic), end_date=str(bugun))
        
        if df is None or df.empty:
            print("HATA: Hiç veri dönmedi. TEFAS yanıt vermiyor olabilir.")
            # Boş da olsa dosyayı oluştur ki Workflow hata vermesin
            pd.DataFrame(columns=['date', 'code', 'title', 'price']).to_csv("guncel_fonlar.csv", index=False)
            return

        # İlgilendiğimiz fonları filtrele
        df_bizim = df[df['code'].isin(FONLAR)].copy()
        
        if df_bizim.empty:
            print("HATA: Bizim fonlara ait veri bulunamadı.")
            pd.DataFrame(columns=['date', 'code', 'title', 'price']).to_csv("guncel_fonlar.csv", index=False)
            return

        # HER FON İÇİN EN GÜNCEL TARİHLİ VERİYİ AL
        # 1. Tarihe göre sırala (Yeni -> Eski)
        df_bizim = df_bizim.sort_values(by='date', ascending=False)
        # 2. Her fon kodundan sadece en üsttekini (en güncelini) tut
        df_sonuc = df_bizim.drop_duplicates(subset=['code'], keep='first')
        
        # İstediğimiz sütunlar
        df_sonuc = df_sonuc[['date', 'code', 'title', 'price']]
        
        # CSV Dosyasına Kaydet
        df_sonuc.to_csv("guncel_fonlar.csv", index=False)
        
        print("BAŞARILI: Veriler kaydedildi.")
        print(df_sonuc)

    except Exception as e:
        print(f"KRİTİK HATA: {e}")
        # Hata olsa bile boş dosya oluştur
        pd.DataFrame().to_csv("guncel_fonlar.csv", index=False)

if __name__ == "__main__":
    verileri_getir()
