import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import plotly.express as px

# =========================================================================
# 1. FUNGSI AMBIL DATA REAL-TIME DARI GOOGLE SHEETS
# =========================================================================
@st.cache_data(ttl=60) # Cache selama 60 detik agar aplikasi cepat dan tidak terkena limit kuota Google API
def ambil_data_database():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    # Mengambil kredensial GCP dari Streamlit Secrets Dokter
    creds_dict = st.secrets["gcp_service_account"] 
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(creds)
    
    # Buka file induk database Anda
    file_induk = client.open("GrowTrack Database")
    
    # Tarik data dari masing-masing Worksheet
    raw_gizi = file_induk.worksheet("Sheet2").get_all_records()
    raw_mental = file_induk.worksheet("Sheet_Mental_Health").get_all_records()
    
    return pd.DataFrame(raw_gizi), pd.DataFrame(raw_mental)

# =========================================================================
# 2. ANTARMUKA UTAMA DASHBOARD
# =========================================================================
st.set_page_config(page_title="Dashboard Surveilans", page_icon="📊", layout="wide")

st.title("📊 Dashboard Pemantauan Wilayah")
st.caption("Data Terintegrasi Aplikasi GENTALA — Puskesmas Batu Tangga, HST")

try:
    # Memuat data dari fungsi gspread
    df_gizi, df_mental = ambil_data_database()
    
    # Membuat Tab Navigasi di Dashboard
    tab_gizi, tab_mental = st.tabs(["🧸 Surveilans Gizi Anak", "🧠 Surveilans Kesehatan Jiwa"])

    # --- TAB 1: DASHBOARD GIZI & TUMBUH KEMBANG ANAK ---
    with tab_gizi:
        st.subheader("Analisis Status Gizi Stunting & Kunjungan")
        
        # Membuat layout 2 kolom (Kiri untuk Donut Chart, Kanan untuk Bar Chart Tren)
        kolom_kiri, kolom_kanan = st.columns(2)
        
        with kolom_kiri:
            st.markdown("#### 🍩 Proporsi Status Tinggi Badan menurut Umur (TB/U)")
            
            # Kolom L di Google Sheets Anda terbaca sebagai 'Status TB/U'
            kolom_tbu = "Status TB/U"
            
            if kolom_tbu in df_gizi.columns and not df_gizi.empty:
                # Hitung distribusi frekuensi status gizi
                hitung_status = df_gizi[kolom_tbu].value_counts().reset_index()
                hitung_status.columns = ['Status Gizi', 'Jumlah Anak']
                
                # Membuat Donut Chart interaktif menggunakan Plotly
                fig_donut = px.pie(
                    hitung_status, 
                    values='Jumlah Anak', 
                    names='Status Gizi', 
                    hole=0.45,
                    color_discrete_map={
                        'Sangat Pendek': '#DC2626', # Merah
                        'Pendek': '#F59E0B',        # Jingga
                        'Normal': '#10B981',        # Hijau
                        'Tinggi': '#3B82F6'         # Biru
                    }
                )
                fig_donut.update_traces(textinfo='percent+value', hoverinfo='label+value')
                fig_donut.update_layout(showlegend=True, margin=dict(t=10, b=10, l=10, r=10))
                st.plotly_chart(fig_donut, use_container_width=True)
            else:
                st.info("Belum ada data atau kolom 'Status TB/U' tidak ditemukan.")
                
        with kolom_kanan:
            st.markdown("#### 📅 Tren Kunjungan Pemeriksaan Gizi")
            
            # Kolom A di Google Sheets Anda bernama 'Waktu Input'
            kolom_waktu = "Waktu Input"
            
            if kolom_waktu in df_gizi.columns and not df_gizi.empty:
                # Salin dataframe gizi untuk manipulasi tanggal
                df_tren = df_gizi.copy()
                # Konversi teks tanggal menjadi tipe datetime
                df_tren['Datetime'] = pd.to_datetime(df_tren[kolom_waktu], errors='coerce')
                # Buat format Tahun-Bulan (Contoh: 2026-06)
                df_tren['Bulan'] = df_tren['Datetime'].dt.strftime('%Y-%m')
                
                # Hitung jumlah kunjungan per bulan
                tren_bulanan = df_tren['Bulan'].value_counts().sort_index().reset_index()
                tren_bulanan.columns = ['Bulan', 'Jumlah Pemeriksaan']
                
                # Tampilkan grafik batang bawaan Streamlit
                st.bar_chart(tren_bulanan.set_index('Bulan'))
            else:
                st.info("Belum ada data atau kolom 'Waktu Input' tidak ditemukan.")

    # --- TAB 2: DASHBOARD KESEHATAN JIWA (SINOVIAL) ---
    with tab_mental:
        st.subheader("Analisis Beban Skrining Jiwa & Tindakan Klinis")
        
        # Grafik Batang Distribusi Jenis Kuesioner
        st.markdown("#### 📊 Distribusi Penggunaan Kuesioner Skrining")
        kolom_kuesioner = "Jenis Kuesioner"
        
        if kolom_kuesioner in df_mental.columns and not df_mental.empty:
            hitung_kuesioner = df_mental[kolom_kuesioner].value_counts().reset_index()
            hitung_kuesioner.columns = ['Jenis Kuesioner', 'Jumlah']
            st.bar_chart(hitung_kuesioner.set_index('Jenis Kuesioner'))
        else:
            st.info("Belum ada data skrining jiwa masuk.")
            
        st.divider()
        
        # Fitur Kegawatan Klinis: Critical Action List
        st.markdown("#### 🚨 Daftar Prioritas Rujukan Jiwa (Critical Action List)")
        st.caption("Menyaring otomatis pasien dengan indikasi risiko tinggi/ide cedera diri untuk intervensi segera.")
        
        # Filter data kritis berdasarkan interpretasi/risiko (Sesuaikan kolom di tab kesehatan jiwa Anda)
        kolom_interpretasi = "Status Interpretasi"
        kolom_risiko = "Faktor Risiko"
        
        if kolom_interpretasi in df_mental.columns:
            # Memfilter baris yang mengandung kata kunci tanda bahaya
            df_kritis = df_mental[
                (df_mental[kolom_interpretasi].str.contains('Kritis|Tinggi|Abnormal|Risiko Tinggi', case=False, na=False)) |
                (df_mental.get(kolom_risiko, pd.Series(dtype=str)).str.contains('Ada|Ya', case=False, na=False))
            ]
            
            if not df_kritis.empty:
                st.error(f"⚠️ Perhatian! Ditemukan {len(df_kritis)} kasus kesehatan jiwa yang memerlukan tatalaksana segera.")
                
                # Kolom esensial yang ingin ditampilkan ke petugas rujukan
                kolom_tampil = ['Waktu Input', 'Nama Pasien', 'Jenis Kuesioner', 'Status Interpretasi', 'Rekomendasi Klinis']
                kolom_tampil = [c for c in kolom_tampil if c in df_kritis.columns]
                
                st.dataframe(df_kritis[kolom_tampil], use_container_width=True)
            else:
                st.success("✅ Seluruh data terpantau aman. Tidak ada indikasi kegawatan mental/ide cedera diri saat ini.")
        else:
            st.info("Sistem siap. Menunggu entri data kuesioner kesehatan jiwa.")

except Exception as e:
    st.error(f"Gagal memuat visualisasi dashboard. Detail teknis: {e}")
