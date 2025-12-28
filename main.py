import requests
import pandas as pd
from datetime import datetime, timedelta

# --- HEDEF: SADECE CHG ---
FONLAR = ["CHG"]

def verileri_getir():
    # Tarih Ayarı (Garanti olsun diye son 5 güne bakar)
    bugun = datetime.now().date()
    baslangic = bugun - timedelta(days=5)
    
    bas_str = baslangic.strftime("%d.%m.%Y")
    bit_str = bugun.strftime("%d.%m.%Y")
    
    print(f"Hedef: CHG Fonu aranıyor ({bas_str} - {bit_str})...")
    
    tum_veriler = []

    # --- 1. ADIM: EMEKLİLİK (BES) VERİTABANINA BAĞLAN ---
    # CHG bir BES fonu olduğu için burası kritik.
    try:
        payload = {'fontip': 'EME', 'bastarih': bas_str, 'bittarih': bit_str}
        # TEFAS'a doğrudan istek atıyoruz
        r = requests.post('https://www.tefas.gov.tr/api/DB/BindHistoryInfo', data=payload)
        data = r.json().get('data', [])
        tum_veriler.extend(data)
        print(f"-> Veritabanından {len(data)} adet veri çekildi.")
    except Exception as e:
        print(f"HATA: {e}")
        return

    # --- 2. ADIM: AYIKLAMA ---
    df = pd.DataFrame(tum_veriler)
    
    # Sütun isimlerini düzelt
    df = df.rename(columns={'FONKODU': 'code', 'FONUNVAN': 'title', 'FIYAT': 'price', 'TARIH': 'date_raw'})
    
    # Sadece CHG'yi süz
    df_bizim = df[df['code'].isin(FONLAR)].copy()
    
    if df_bizim.empty:
        print("HATA: CHG fonu veritabanında bulunamadı!")
        return

    # Fiyat Formatı (1,234 -> 1.234)
    df_bizim['price'] = df_bizim['price'].astype(str).str.replace(',', '.')
    df_bizim['price'] = pd.to_numeric(df_bizim['price'], errors='coerce')

    # Tarih Formatı
    def clean_date(d):
        try:
            ts = int(d.replace('/Date(','').replace(')/',''))
            return datetime.fromtimestamp(ts/1000).date()
        except:
            return None
    df_bizim['real_date'] = df_bizim['date_raw'].apply(clean_date)
    
    # En güncelini al
    df_bizim = df_bizim.sort_values(by='real_date', ascending=False)
    df_sonuc = df_bizim.drop_duplicates(subset=['code'], keep='first')
    
    # --- 3. ADIM: KAYIT ---
    final_df = pd.DataFrame()
    final_df['Tarih'] = df_sonuc['real_date']
    final_df['Fon Kodu'] = df_sonuc['code']
    final_df['Fon Adi'] = df_sonuc['title']
    
    # Türkçe Excel Formatı (Virgüllü)
    final_df['Fiyat'] = df_sonuc['price'].apply(lambda x: "{:,.6f}".format(x).replace('.', 'X').replace(',', '.').replace('X', ','))

    final_df.to_csv("guncel_fonlar.csv", index=False, encoding='utf-8-sig', sep=';')
    
    print("\nBAŞARILI! CHG verisi hazır.")
    print(final_df)

if __name__ == "__main__":
    verileri_getir()
