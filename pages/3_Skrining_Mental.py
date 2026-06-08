import streamlit as st
import datetime
import os
import gspread
from google.oauth2.service_account import Credentials

# Mengatur konfigurasi dasar halaman utama Streamlit
st.set_page_config(page_title="GENTALA - Jiwa", page_icon="🧠", layout="centered")

# =========================================================================
# FUNGSI UTAMA: TOMBOL CETAK PDF (CSS MEDIA PRINT)
# =========================================================================
def tambahkan_tombol_cetak_pdf():
    st.markdown(
        """
        <style>
        @media print {
            /* Sembunyikan elemen navigasi Streamlit saat masuk mode print/PDF */
            [data-testid="stSidebar"], header, footer, .element-container:has(iframe), .stButton {
                display: none !important;
            }
            .main .block-container {
                padding-top: 0.5rem !important;
                padding-bottom: 0.5rem !important;
            }
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    tombol_html = """
    <style>
        .btn-print {
            width: 100%;
            background-color: #1E3A8A;
            color: white;
            padding: 12px 24px;
            font-size: 16px;
            font-weight: bold;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        }
        .btn-print:hover {
            background-color: #152A66;
        }
    </style>
    <button class="btn-print" onclick="window.parent.print()">
        🖨️ Cetak Hasil Skrining / Simpan ke PDF
    </button>
    """
    st.components.v1.html(tombol_html, height=55)

# =========================================================================
# FUNGSI DATABASE: KONEKSI TAB SHEET_MENTAL_HEALTH
# =========================================================================
def koneksi_spreadsheet_mental():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_dict = st.secrets["gcp_service_account"] 
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(creds)
    # Membuka file utama dan mengunci spesifik ke tab Sheet_Mental_Health
    sheet = client.open("GrowTrack Database").worksheet("Sheet_Mental_Health")
    return sheet

# =========================================================================
# 1. IDENTITAS & FILTER UTAMA
# =========================================================================
st.title("🧠 GENTALA - Skrining Kesehatan Jiwa")
st.caption("Inovasi Program Integrasi - Puskesmas Batu Tangga")

kategori = st.selectbox(
    "Pilih Kelompok Sasaran Skrining:",
    ["Pasca Persalinan [EPDS]", "Anak & Remaja [SDQ]", "Orang Dewasa [SRQ-20]"],
    key="pilih_kategori_utama"
)

st.markdown("### 📋 Data Identitas Pasien")
col_id1, col_id2 = st.columns(2)

with col_id1:
    nama = st.text_input("Nama Lengkap Pasien:", key="id_nama")
    nik = st.text_input("Nomor NIK (Boleh dikosongkan):", key="id_nik")

with col_id2:
    tgl_lahir = st.date_input("Tanggal Lahir:", value=datetime.date(2000, 1, 1), key="id_tgl")
    pemeriksa = st.text_input("Nama Tenaga Kesehatan / Kader:", key="id_nakes")

# 🎯 LOGIKA OTOMATIS: Menghitung Umur Pasien Berdasarkan Tanggal Lahir (Mencegah NameError)
hari_ini = datetime.date.today()
hitung_umur = hari_ini.year - tgl_lahir.year - ((hari_ini.month, hari_ini.day) < (tgl_lahir.month, tgl_lahir.day))

# Teks konversi untuk mempermudah pembacaan di kuesioner anak vs dewasa
if hitung_umur < 1:
    # Jika di bawah 1 tahun, hitung dalam bulan
    selisih_bulan = (hari_ini.year - tgl_lahir.year) * 12 + hari_ini.month - tgl_lahir.month
    umur_pasien_teks = f"{selisih_bulan} Bulan"
else:
    umur_pasien_teks = f"{hitung_umur} Tahun"

# Tampilkan info umur riil agar petugas tahu kalkulasi berjalan sukses
st.write(f"ℹ️ **Umur Terkalkulasi:** {umur_pasien_teks}")

st.markdown("---")

# Initialize shared upload variables
sudah_submit = False
baris_data_cloud = []

# =========================================================================
# 2. MODUL KUESIONER IBU HAMIL & MENYUSUI (EPDS)
# =========================================================================
if "EPDS" in kategori:
    st.subheader("🤰 Edinburgh Postnatal Depression Scale (EPDS)")
    st.info("Silakan memilih jawaban yang paling mirip dengan perasaan Anda selama 7 hari terakhir.")
    
    epds_1 = st.radio("1. Saya dapat tertawa dan melihat segi kelucuan hal-hal tertentu:", ["a. Seperti biasanya", "b. Sekarang tidak terlalu sering", "c. Sekarang agak jarang", "d. Tidak sama sekali"], key="epds_1")
    epds_2 = st.radio("2. Saya menanti-nanti untuk melakukan sesuatu dengan penuh harapan:", ["a. Sebanyak sebelumnya", "b. Agak sedikit kurang dibandingkan dengan sebelumnya", "c. Kurang dibandingkan dengan sebelumnya", "d. Tidak pernah sama sekali"], key="epds_2")
    epds_3 = st.radio("3. *Saya menyalahkan diri jika ada sesuatu yang tidak berjalan dengan baik:", ["a. Ya, hampir selalu", "b. Ya, kadang-kadang", "c. Tidak terlalu sering", "d. Tidak, tidak pernah"], key="epds_3")
    epds_4 = st.radio("4. Saya merasa cemas atau merasa khawatir tanpa alasan:", ["a. Tidak pernah sama sekali", "b. Hampir tidak pernah", "c. Ya, kadang-kadang", "d. Ya, sering sekali"], key="epds_4")
    epds_5 = st.radio("5. *Saya merasa takut atau panik tanpa alasan:", ["a. Ya, sering sekali", "b. Ya, kadang-kadang", "c. Tidak terlalu sering", "d. Tidak pernah sama sekali"], key="epds_5")
    epds_6 = st.radio("6. *Banyak hal menjadi beban untuk saya:", ["a. Ya, seringkali saya sama sekali tidak dapat mengatasinya", "b. Ya, kadang saya tidak dapat mengatasi seperti biasanya", "c. Tidak, biasanya saya dapat mengatasinya dengan baik", "d. Tidak, saya dapat mengatasinya dengan baik seperti biasanya"], key="epds_6")
    epds_7 = st.radio("7. *Saya merasa begitu sedih sampai sulit tidur:", ["a. Ya, hampir selalu", "b. Ya, kadang-kadang", "c. Tidak, tidak sering", "d. Tidak, tidak pernah"], key="epds_7")
    epds_8 = st.radio("8. *Saya merasa sedih atau susah:", ["a. Ya, hampir selalu", "b. Ya, sering", "c. Jarang", "d. Tidak pernah"], key="epds_8")
    epds_9 = st.radio("9. *Saya merasa sangat sedih sehingga saya menangis:", ["a. Ya, hampir selalu", "b. Ya, sering", "c. Hanya sekali-kali", "d. Tidak pernah"], key="epds_9")
    epds_10 = st.radio("10. *Pikiran untuk menyakiti diri saya sendiri sering muncul:", ["a. Ya, agak sering", "b. Kadang-kadang", "c. Hampir tidak pernah", "d. Tidak pernah"], key="epds_10")

    if st.button("Hitung & Simpan Skor EPDS", key="btn_epds"):
        skala_normal = {"a": 0, "b": 1, "c": 2, "d": 3}
        skala_terbalik = {"a": 3, "b": 2, "c": 1, "d": 0}
        
        skor_total = (skala_normal[epds_1[0]] + skala_normal[epds_2[0]] + skala_terbalik[epds_3[0]] + 
                      skala_normal[epds_4[0]] + skala_terbalik[epds_5[0]] + skala_terbalik[epds_6[0]] + 
                      skala_terbalik[epds_7[0]] + skala_terbalik[epds_8[0]] + skala_terbalik[epds_9[0]] + 
                      skala_terbalik[epds_10[0]])
        
        if skor_total <= 9:
            status_mental = "Risiko rendah depresi"
            rekomendasi = "Kondisi emosional stabil. Tetap berikan dukungan psikososial dasar."
            st.success(f"**Status:** {status_mental}")
        elif 10 <= skor_total <= 12:
            status_mental = "Risiko sedang (Distres emosional)"
            rekomendasi = "Perlu pemantauan lebih lanjut. Lakukan evaluasi ulang/pendampingan berkala oleh nakes."
            st.warning(f"**Status:** {status_mental}")
        else:
            status_mental = "Risiko tinggi depresi"
            rekomendasi = "Gejala mengarah kuat pada depresi perinatal. Segera rujuk ke profesional kesehatan jiwa."
            st.error(f"**Status:** {status_mental}")
            
        st.metric(label="SKOR TOTAL EPDS", value=f"{skor_total} / 30")
        st.info(f"💡 **Rekomendasi Tindakan:** {rekomendasi}")
        
        # Red-flag safety check pertanyaan no 10
        flag_danger = "Ada" if skala_terbalik[epds_10[0]] > 0 else "Tidak Ada"
        if flag_danger == "Ada":
            st.error("🚨 **ALARM UTAMA KLINIS (IDE CEDERA DIRI):** Pasien mengindikasikan pikiran menyakiti diri sendiri! Tatalaksana psikologis/rujukan darurat wajib berjalan segera!")
            
        # Mapping 12 Kolom standar database untuk EPDS (Menggunakan umur_pasien_teks)
        baris_data_cloud = [
            str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")), # Kolom A: Waktu Input
            nama,                                                      # Kolom B: Nama Pasien
            f"NIK/RM: {nik}",                                          # Kolom C: NIK
            umur_pasien_teks,                                          # Kolom D: Umur Universal Pasien
            "EPDS (Ibu Perinatal)",                                    # Kolom E: Jenis Kuesioner
            skor_total,                                                # Kolom F: Sub-Skor / Detail
            "-",                                                       # Kolom G: Status Interpretasi
            status_mental,                                             # Kolom H: Rekomendasi Klinis
            rekomendasi,                                               # Kolom I: Interpretasi Hasil
            "Ibu Hamil/Menyusui",                                      # Kolom J: Kategori Lingkungan / Faktor Risiko
            pemeriksa,                                                 # Kolom K: Pemeriksa
            "-"                                                        # Kolom L: Catatan
        ]
        sudah_submit = True

# =========================================================================
# 3. MODUL KUESIONER ANAK & REMAJA (SDQ)
# =========================================================================
elif "SD
