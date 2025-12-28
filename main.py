from tefas import Crawler
import pandas as pd
from datetime import datetime, timedelta

# --- AYARLAR ---
FONLAR = ["TI3", "IDH", "MAC", "GMR", "TCD"]

def verileri_getir():
    crawler = Crawler()
    
    # Bugünün tarihi
    bugun = datetime.now().date()
    # Geriye dönük 30 gün (Veri garanti olsun)
    baslangic = bugun - timedelta(days=30) 
    
    print(f"Tarama: {baslangic} - {bugun}")

    try:
        # --- DÜZELTİLEN KISIM BURASI ---
        # start_date yerine start, end_date yerine end kullanıyoruz
        df = crawler.fetch(start=str(baslangic), end=str(bugun))
        # -------------------------------

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
        
        # Sütun seçimi ve Kayıt
        df_sonuc = df_sonuc[['date', 'code', 'title', 'price']]
        df_sonuc.to_csv("guncel_fonlar.csv", index=False, encoding='utf-8-sig')
        
        print("BAŞARILI: Veriler CSV dosyasina yazildi.")
        print(df_sonuc)

    except Exception as e:
        print(f"SİSTEM HATASI: {e}")
        # Hata detayını tam görelim
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verileri_getir()
