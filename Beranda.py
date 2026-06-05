import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# ==========================================
# 1. KONFIGURASI HALAMAN & KONEKSI DATABASE
# ==========================================
st.set_page_config(
    page_title="Grow.TrackID - Beranda",
    page_icon="Logo.png",
    layout="wide"
)

# Fungsi untuk koneksi ke Google Sheets menggunakan Streamlit Secrets
def init_connection():
    try:
        # Menentukan cakupan akses (scope)
        scope = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        
        # BARU: Membaca kredensial dari Streamlit Secrets (bukan file fisik Kunci.json)
        creds = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"], 
            scopes=scope
        )
        client = gspread.authorize(creds)
        
        # Membuka Spreadsheet
        return client.open("GrowTrack Database").sheet1
    except Exception as e:
        # Mengembalikan None jika gagal koneksi tanpa memunculkan error file fisik
        return None

# Inisialisasi koneksi agar bisa dipakai di seluruh halaman
sheet = init_connection()

# ==========================================
# 2. TAMPILAN UTAMA (BERANDA)
# ==========================================
st.title("🏥 Selamat Datang di GENTALA - Gerakan Terpadu Skrinig Gizi, Mental, & Telekonsultasi Anak")
st.subheader("Inovasi Program Puskesmas Batu Tangga")

# Informasi Status Koneksi di Sidebar
if sheet:
    st.sidebar.success("✅ Database Terhubung")
else:
    st.sidebar.error("❌ Database Terputus")
    st.error("Koneksi Gagal: Pastikan konfigurasi 'Secrets' di Streamlit Cloud sudah benar dan email robot (client_email) sudah diberi izin akses Editor di Google Sheets Anda.")

st.markdown("""
Aplikasi ini dirancang untuk memudahkan tenaga kesehatan dalam memantau pertumbuhan anak dan melakukan koordinasi layanan kesehatan secara digital.

### 👈 Silakan pilih menu di samping:
1. **Skrining Gizi**: Untuk input data antropometri (BB/TB) dan cek status gizi anak secara otomatis.
2. **Skrining Mental**: Untuk menilai status mental seseorang (Anak, Dewasa, & Ibu Pasca Melahirkan).
3. **Telekonsultasi**: Untuk melaporkan hasil skrining atau berkonsultasi langsung dengan dokter.
""")

st.info("Gunakan menu di sebelah kiri untuk berpindah halaman.")

# Menambahkan footer sederhana
st.markdown("---")
st.caption(f"© 2026 Grow.TrackID - Puskesmas Batu Tangga | Logged in as: dr. Aflin Bihar")
