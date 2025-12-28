from tefas import Crawler
import pandas as pd
from datetime import datetime, timedelta

# --- AYARLAR ---
FONLAR = list(set(["AJR", "CHG", "ATE", "CFA", "HES", "AHL", "ALI", "BPH", 
                   "FEI", "AGA", "AMF", "AMZ", "FFZ", "YLB", "YKT", "YDI", 
                   "AFA", "HKM", "IDH", "MAC", "TGE"]))

def verileri_getir():
    crawler = Crawler()
    
    bugun = datetime.now().date()
    
    # OPTİMİZASYON: 10 gün yerine 4 gün yeterli.
    # Cuma günü çeksen; Perşembe, Çarşamba, Salı'yı görür.
    # Pazartesi çeksen; Pazar, C.tesi, Cuma'yı görür. Veri kaybı olmaz, hız artar.
    baslangic = bugun - timedelta(days=4) 
    
    print(f"Hızlı Tarama: {baslangic} - {bugun}")

    try:
        # Veriyi çek
        df = crawler.fetch(start=str(baslangic), end=str(bugun))
        
        if df is None or df.empty:
            print("HATA: Veri bulunamadı.")
            with open("guncel_fonlar.csv", "w") as f:
                f.write("Tarih;Fon Kodu;Fon Adi;Fiyat\n")
            return

        # Filtreleme
        df_bizim = df[df['code'].isin(FONLAR)].copy()
        
        if df_bizim.empty:
            print("UYARI: Listendeki fonlara ait güncel veri bulunamadı.")
            return

        # En güncel veriyi yakala
        df_bizim = df_bizim.sort_values(by='date', ascending=False)
        df_sonuc = df_bizim.drop_duplicates(subset=['code'], keep='first')
        
        # Düzenleme
        df_sonuc = df_sonuc[['date', 'code', 'title', 'price']]
        df_sonuc.columns = ['Tarih', 'Fon Kodu', 'Fon Adi', 'Fiyat']
        
        # Formatlama (Nokta -> Virgül)
        df_sonuc['Fiyat'] = df_sonuc['Fiyat'].astype(str).str.replace('.', ',', regex=False)
        
        # Kaydet
        df_sonuc.to_csv("guncel_fonlar.csv", index=False, encoding='utf-8-sig', sep=';')
        
        print(f"BAŞARILI: {len(df_sonuc)} adet fon verisi hazırlandı.")
        print(df_sonuc)

    except Exception as e:
        print(f"SİSTEM HATASI: {e}")

if __name__ == "__main__":
    verileri_getir()
