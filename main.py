from tefas import Crawler
import pandas as pd
from datetime import datetime, timedelta

# --- AYARLAR ---
FONLAR = ["TI3", "IDH", "MAC", "GMR", "TCD"]

def verileri_getir():
    crawler = Crawler()
    
    bugun = datetime.now().date()
    # DÜZELTME: 30 gün yerine 4 gün yapıyoruz. 
    # Bu sayede işlem saniyeler içinde bitecek.
    baslangic = bugun - timedelta(days=4) 
    
    print(f"Hızlı Tarama: {baslangic} - {bugun}")

    try:
        # start ve end komutları doğru, sadece tarih aralığı kısaldı
        df = crawler.fetch(start=str(baslangic), end=str(bugun))
        
        if df is None or df.empty:
            print("HATA: Veri dönmedi.")
            return

        # Filtreleme
        df_bizim = df[df['code'].isin(FONLAR)].copy()
        
        if df_bizim.empty:
            print("HATA: Belirtilen fonlar bulunamadı.")
            return

        # En güncel veriyi al
        df_bizim = df_bizim.sort_values(by='date', ascending=False)
        df_sonuc = df_bizim.drop_duplicates(subset=['code'], keep='first')
        
        # Kayıt
        df_sonuc = df_sonuc[['date', 'code', 'title', 'price']]
        df_sonuc.to_csv("guncel_fonlar.csv", index=False, encoding='utf-8-sig')
        
        print("BAŞARILI: Veriler ışık hızıyla kaydedildi.")
        print(df_sonuc)

    except Exception as e:
        print(f"HATA: {e}")

if __name__ == "__main__":
    verileri_getir()
