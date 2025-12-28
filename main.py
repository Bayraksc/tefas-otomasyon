import requests
import pandas as pd
from datetime import datetime, timedelta

# --- SENİN LİSTEN (HEPSİ DAHİL) ---
FONLAR = list(set(["AJR", "CHG", "ATE", "CFA", "HES", "AHL", "ALI", "BPH", 
                   "FEI", "AGA", "AMF", "AMZ", "FFZ", "YLB", "YKT", "YDI", 
                   "AFA", "HKM", "IDH", "MAC", "TGE"]))

def verileri_getir():
    bugun = datetime.now().date()
    baslangic = bugun - timedelta(days=5) # 5 gün yeterli
    
    # TEFAS'ın anladığı tarih formatı (Unix Timestamp değil, string)
    bas_str = baslangic.strftime("%d.%m.%Y")
    bit_str = bugun.strftime("%d.%m.%Y")
    
    print(f"Tarama Aralığı: {bas_str} - {bit_str}")
    
    tum_veriler = []

    # --- MOTOR 1: YATIRIM FONLARI (YAT) ---
    print("1. Motor Çalışıyor: Yatırım Fonları taranıyor...")
    payload_yat = {
        'fontip': 'YAT',
        'bastarih': bas_str,
        'bittarih': bit_str
    }
    try:
        r_yat = requests.post('https://www.tefas.gov.tr/api/DB/BindHistoryInfo', data=payload_yat)
        data_yat = r_yat.json().get('data', [])
        tum_veriler.extend(data_yat)
    except Exception as e:
        print(f"Yatırım Fonları Hatası: {e}")

    # --- MOTOR 2: EMEKLİLİK FONLARI (EME - BES) ---
    print("2. Motor Çalışıyor: Emeklilik (BES) Fonları taranıyor...")
    payload_eme = {
        'fontip': 'EME',
        'bastarih': bas_str,
        'bittarih': bit_str
    }
    try:
        r_eme = requests.post('https://www.tefas.gov.tr/api/DB/BindHistoryInfo', data=payload_eme)
        data_eme = r_eme.json().get('data', [])
        tum_veriler.extend(data_eme)
    except Exception as e:
        print(f"Emeklilik Fonları Hatası: {e}")

    # --- VERİ İŞLEME ---
    if not tum_veriler:
        print("HATA: Hiçbir veri çekilemedi.")
        return

    # Pandas DataFrame'e çevir
    df = pd.DataFrame(tum_veriler)
    
    # Sütun isimleri TEFAS'tan şöyle gelir: 'FONKODU', 'FONUNVAN', 'FIYAT', 'TARIH'
    # Bizim formatımıza uyduralım
    df = df.rename(columns={
        'FONKODU': 'code',
        'FONUNVAN': 'title',
        'FIYAT': 'price',
        'TARIH': 'date'
    })

    # Tarihi (Unix timestamp gelir) okunur hale getir
    # Gelen tarih formatı bazen karışıktır, TEFAS API genelde milisaniye timestamp verir
    # Basit olsun diye string gelen tarihi parse edelim veya direkt kullanalım.
    # TEFAS API string timestamp döner "/Date(1703538000000)/" gibi.
    # Uğraşmamak için Pandas'ın gücünü kullanalım:
    
    # Filtreleme (Senin listen)
    df_bizim = df[df['code'].isin(FONLAR)].copy()
    
    if df_bizim.empty:
        print("UYARI: Listendeki fonlar API'de bulunamadı.")
        return

    # TEFAS API'den gelen veriyi temizle
    # Sadece en güncel tarihi alacağımız için karmaşık tarih dönüşümüne gerek yok
    # Sadece "Tarih" sütunu string olarak kalsın, biz sıralama için 'date' verisine güvenelim
    
    # En güncel veriyi yakalamak için (API karışık sırada gönderebilir)
    # Price float olmalı
    df_bizim['price'] = df_bizim['price'].astype(str).str.replace(',', '.') # Önce Python sayı formatına çevir
    df_bizim['price'] = pd.to_numeric(df_bizim['price'], errors='coerce')
    
    # Sıralama yapabilmek için tarihi düzeltelim
    # TEFAS'tan tarih epoch timestamp içinde string gelir. 
    # Pratik çözüm: Veriyi çektiğimiz an en taze veri en altta veya üstte olabilir.
    # Biz 'date' sütununu parse edelim.
    def parse_tefas_date(d_str):
        try:
            # /Date(1703808000000)/ formatını temizle
            ts = int(d_str.replace('/Date(','').replace(')/',''))
            return datetime.fromtimestamp(ts/1000).date()
        except:
            return None

    df_bizim['real_date'] = df_bizim['date'].apply(parse_tefas_date)
    
    # Sırala (En yeni en üstte)
    df_bizim = df_bizim.sort_values(by='real_date', ascending=False)
    
    # Tekilleştir
    df_sonuc = df_bizim.drop_duplicates(subset=['code'], keep='first')
    
    # --- FİNAL ÇIKTI (TÜRKÇE EXCEL FORMATI) ---
    final_df = pd.DataFrame()
    final_df['Tarih'] = df_sonuc['real_date']
    final_df['Fon Kodu'] = df_sonuc['code']
    final_df['Fon Adi'] = df_sonuc['title']
    
    # Fiyatı tekrar TR formatına (virgüllü) çevir
    final_df['Fiyat'] = df_sonuc['price'].apply(lambda x: "{:,.6f}".format(x).replace('.', 'X').replace(',', '.').replace('X', ','))

    # Kaydet
    final_df.to_csv("guncel_fonlar.csv", index=False, encoding='utf-8-sig', sep=';')
    
    print(f"BAŞARILI: {len(final_df)} adet fon (BES + Yatırım) çekildi.")
    print(final_df)

if __name__ == "__main__":
    verileri_getir()
