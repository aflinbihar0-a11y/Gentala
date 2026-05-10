import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# ==========================================
# 1. KONFIGURASI HALAMAN & KONEKSI DATABASE
# ==========================================
st.set_page_config(
    page_title="Grow.TrackID - Beranda",
    page_icon="🏠",
    layout="wide"
)

# Fungsi untuk koneksi ke Google Sheets
def init_connection():
    try:
        # Menentukan cakupan akses (scope)
        scope = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        
        # Membaca file kunci JSON yang sudah Dokter pindahkan ke folder project
        # Pastikan nama filenya "Kunci.json" (perhatikan huruf kapital K)
        creds_dict = st.secrets["gcp_service_account"]
        creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
        client = gspread.authorize(creds)
        
        # MEMBUKA SPREADSHEET
        # Ganti "Untitled spreadsheet" dengan nama file Sheets Dokter jika sudah diubah
        return client.open("GrowTrack Database").sheet1
    except Exception as e:
        st.error(f"Koneksi Gagal: Pastikan pengaturan 'Secrets' di Streamlit Cloud sudah benar dan email robot sudah diberi akses Editor di Google Sheets. Error: {e}")
        return None

# Inisialisasi koneksi agar bisa dipakai di seluruh halaman
sheet = init_connection()

# ==========================================
# 2. TAMPILAN UTAMA (BERANDA)
# ==========================================
st.title("🏥 Selamat Datang di Grow.TrackID")
st.subheader("Inovasi Program Puskesmas Batu Tangga")

# Informasi Status Koneksi (Hanya muncul jika sukses)
if sheet:
    st.sidebar.success("✅ Database Terhubung")
else:
    st.sidebar.error("❌ Database Terputus")

st.markdown("""
Aplikasi ini dirancang untuk memudahkan tenaga kesehatan dalam memantau pertumbuhan anak dan melakukan koordinasi layanan kesehatan secara digital.

### 👈 Silakan pilih menu di samping:
1. **Skrining Gizi**: Untuk input data antropometri (BB/TB) dan cek status gizi anak secara otomatis.
2. **Telekonsultasi**: Untuk melaporkan hasil skrining atau berkonsultasi langsung dengan dokter.
""")

st.info("Gunakan menu di sebelah kiri untuk berpindah halaman.")

# Menambahkan footer sederhana
st.markdown("---")
st.caption(f"© 2026 Grow.TrackID - Puskesmas Batu Tangga | Logged in as: dr. Aflin Bihar")
