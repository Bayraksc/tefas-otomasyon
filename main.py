import requests
import pandas as pd
from datetime import datetime, timedelta

# --- HEDEF LİSTE ---
FONLAR = list(set([
    "AJR", "CHG", "ATE", "CFA", "HES", "AHL", "ALI", "BPH", 
    "FEI", "AGA", "AMF", "AMZ", "FFZ", "YLB", "YKT", "YDI", 
    "AFA", "HKM", "IDH", "MAC", "TGE"
]))

def verileri_getir():
    bugun = datetime.now().date()
    baslangic = bugun - timedelta(days=5)
    
    bas_str = baslangic.strftime("%d.%m.%Y")
    bit_str = bugun.strftime("%d.%m.%Y")
    
    print(f"Tarama: {bas_str} - {bit_str}")
    
    # --- KRİTİK EKLENTİ: KİMLİK KARTI (HEADERS) ---
    # TEFAS robotları engeller, bu ayarlar bizi Chrome tarayıcısı gibi gösterir.
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://www.tefas.gov.tr/TarihselVeriler.aspx',
        'X-Requested-With': 'XMLHttpRequest',
        'Origin': 'https://www.tefas.gov.tr',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
    }

    tum_veriler = []

    # --- 1. YATIRIM FONLARI ---
    try:
        payload = {'fontip': 'YAT', 'bastarih': bas_str, 'bittarih': bit_str}
        r = requests.post('https://www.tefas.gov.tr/api/DB/BindHistoryInfo', data=payload, headers=headers)
        data = r.json().get('data', [])
        tum_veriler.extend(data)
        print(f"-> Yatırım Fonları: {len(data)} veri")
    except Exception as e:
        print(f"HATA (Yatırım): {e}")

    # --- 2. EMEKLİLİK (BES) FONLARI ---
    try:
        payload = {'fontip': 'EME', 'bastarih': bas_str, 'bittarih': bit_str}
        r = requests.post('https://www.tefas.gov.tr/api/DB/BindHistoryInfo', data=payload, headers=headers)
        data = r.json().get('data', [])
        tum_veriler.extend(data)
        print(f"-> BES Fonları: {len(data)} veri")
    except Exception as e:
        print(f"HATA (BES): {e}")

    # --- İŞLEME ---
    if not tum_veriler:
        print("HATA: Veri çekilemedi. Header ayarları kontrol edilmeli.")
        return

    df = pd.DataFrame(tum_veriler)
    df = df.rename(columns={'FONKODU': 'code', 'FONUNVAN': 'title', 'FIYAT': 'price', 'TARIH': 'date_raw'})
    
    # Listemizi filtrele
    df_bizim = df[df['code'].isin(FONLAR)].copy()
    
    if df_bizim.empty:
        print("UYARI: Seçilen fonlara ait veri gelmedi.")
        return

    # Fiyat düzeltme
    df_bizim['price'] = df_bizim['price'].astype(str).str.replace(',', '.')
    df_bizim['price'] = pd.to_numeric(df_bizim['price'], errors='coerce')

    # Tarih düzeltme
    def clean_date(d):
        try:
            ts = int(d.replace('/Date(','').replace(')/',''))
            return datetime.fromtimestamp(ts/1000).date()
        except:
            return None
    df_bizim['real_date'] = df_bizim['date_raw'].apply(clean_date)
    
    # En güncel veriyi al
    df_bizim = df_bizim.sort_values(by='real_date', ascending=False)
    df_sonuc = df_bizim.drop_duplicates(subset=['code'], keep='first')
    
    # ÇIKTI
    final_df = pd.DataFrame()
    final_df['Tarih'] = df_sonuc['real_date']
    final_df['Fon Kodu'] = df_sonuc['code']
    final_df['Fon Adi'] = df_sonuc['title']
    
    # Türkçe Fiyat (Virgüllü)
    final_df['Fiyat'] = df_sonuc['price'].apply(lambda x: "{:,.6f}".format(x).replace('.', 'X').replace(',', '.').replace('X', ','))

    final_df.to_csv("guncel_fonlar.csv", index=False, encoding='utf-8-sig', sep=';')
    
    print("\nBAŞARILI! Tüm fonlar (CHG dahil) çekildi.")
    print(final_df[['Tarih', 'Fon Kodu', 'Fiyat']])

if __name__ == "__main__":
    verileri_getir()
