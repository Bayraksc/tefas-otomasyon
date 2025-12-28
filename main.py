from tefas import Crawler
import pandas as pd
from datetime import datetime, timedelta

# --- AYARLAR ---
# set() kullanarak mükerrer (çift) yazılanları otomatik temizliyoruz
FONLAR = list(set(["AJR", "CHG", "ATE", "CFA", "HES", "AHL", "ALI", "BPH", "FEI", "AGA", "AMF", "AMZ", "FFZ","YLB", "YKT", "YDI", "AFA", "HKM", "IDH", "MAC", "TGE"]))

def verileri_getir():
    crawler = Crawler()
    
    bugun = datetime.now().date()
    # DÜZELTME 1: 5 gün riskli olabilir (Bayram vs.), 10 gün garanti çözümdür.
    baslangic = bugun - timedelta(days=10) 
    
    print(f"Tarama: {baslangic} - {bugun}")

    try:
        # Veriyi çek
        df = crawler.fetch(start=str(baslangic), end=str(bugun))
        
        if df is None or df.empty:
            print("Veri bulunamadı, boş dosya oluşturuluyor.")
            with open("guncel_fonlar.csv", "w") as f:
                # DÜZELTME 2: Boş dosya oluşsa bile başlıklar Türkçe olsun
                f.write("Tarih;Fon Kodu;Fon Adi;Fiyat\n")
            return

        # Filtreleme
        df_bizim = df[df['code'].isin(FONLAR)].copy()
        
        # En güncel veriyi al
        df_bizim = df_bizim.sort_values(by='date', ascending=False)
        df_sonuc = df_bizim.drop_duplicates(subset=['code'], keep='first')
        
        # Sütunları seç
        df_sonuc = df_sonuc[['date', 'code', 'title', 'price']]

        # DÜZELTME 3: Başlıkları Türkçeleştirme (Sheets'te şık durması için)
        df_sonuc.columns = ['Tarih', 'Fon Kodu', 'Fon Adi', 'Fiyat']
        
        # Formatlama (Nokta -> Virgül)
        df_sonuc['Fiyat'] = df_sonuc['Fiyat'].astype(str).str.replace('.', ',', regex=False)
        
        # Kayıt
        df_sonuc.to_csv("guncel_fonlar.csv", index=False, encoding='utf-8-sig', sep=';')
        
        print("BAŞARILI: Veriler Türkçe formatında (;) kaydedildi.")
        print(df_sonuc)

    except Exception as e:
        print(f"HATA: {e}")

if __name__ == "__main__":
    verileri_getir()
