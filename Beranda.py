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
Aplikasi ini dirancang untuk memudahkan tenaga kesehatan dalam melakukan skrining cepat status gizi anak (0-5 tahun), melakukan skrining jiwa dari ibu hamil, anak-anak hingga dewasa, dan memudahkan konsultasi layanan kesehatan antar nakes dan dokter secara digital.

### 👈 Silakan pilih menu di samping:
1. **Skrining Gizi**: Untuk input data antropometri (BB/TB) dan cek status gizi anak secara otomatis.
2. **Skrining Mental**: Untuk menilai status mental seseorang (Anak, Dewasa, & Ibu Pasca Melahirkan).
3. **Telekonsultasi**: Untuk melaporkan hasil skrining atau berkonsultasi langsung dengan dokter.
""")

st.info("Gunakan menu di sebelah kiri untuk berpindah halaman.")

# --- BAGIAN FOOTER / KONTAK BANTUAN ---
st.markdown("---")  # Membuat garis pembatas horizontal

# Membuat judul bagian bantuan
st.markdown("### 📞 Pusat Bantuan & Layanan Informasi")
st.write(
    "Jika Anda mengalami kendala teknis, kesalahan input data, atau memerlukan informasi lebih lanjut "
    "mengenai sistem GENTALA, silakan hubungi tim penanggung jawab melalui jalur di bawah ini:"
)

# Membagi menjadi 2 kolom untuk WhatsApp dan Email
col_wa, col_email = st.columns(2)

with col_wa:
    # Menggunakan komponen st.info agar tampilannya berbentuk card berwarna biru muda yang rapi
    st.info(
        "6282157263167 🟢 WhatsApp Hotline\n\n"
        "Hubungi admin GENTALA untuk respon cepat:\n\n"
        "[💬 Chat WhatsApp Klik Disini](https://wa.me/6282157263167)"
    )

with col_email:
    st.info(
        "Aflinbihar0@gamil.com ✉️ Email Resmi\n\n"
        "Kirimkan surat atau laporan kendala tertulis:\n\n"
        "[📧 Kirim Email Klik Disini](mailto:email.puskesmas@domain.com)"  # Ganti dengan email resmi Puskesmas/Inovasi Dokter
    )

import streamlit as st
from datetime import datetime
# Catatan: Pastikan 'import gspread' dan objek 'sh' (spreadsheet) sudah didefinisikan di bagian atas Beranda.py Dokter.
# Contoh jika di atas sudah ada: sh = gc.open("Nama_File_Google_Sheets_Dokter")

st.markdown("---") # Garis pembatas horizontal untuk memisahkan konten beranda dan form

# 1. Judul dan Sub-judul Bagian Pengaduan
st.markdown("## 📩 Kotak Saran & Pengaduan Layanan GENTALA")
st.write(
    "Komitmen Puskesmas Batu Tangga adalah terus berinovasi. Silakan sampaikan keluhan, "
    "kritik konstruktif, dan/atau saran pengembangan."
)

# 2. Membuat Wadah Formulir (st.form) agar halaman tidak reload setiap kali mengetik
with st.form(key="form_pengaduan_beranda", clear_on_submit=True):
    
    # Input Nama (Bisa Anonim demi kenyamanan pengadu)
    nama_pengirim = st.text_input(
        "Nama Lengkap / Instansi:", 
        placeholder="Contoh: Anonim / Kader Posyandu / Nakes"
    )
    
    # Pilihan Kategori menggunakan Selectbox
    kategori_feedback = st.selectbox(
        "Kategori Umpan Balik:",
        [
            "Saran Pengembangan Fitur", 
            "Kritik Konstruktif", 
            "Laporan Kendala Teknis / Eror Aplikasi", 
            "Pengaduan Layanan Sistem"
        ]
    )
    
    # Input Isi Detail Masukan
    isi_pesan = st.text_area(
        "Detail Keluhan / Kritik / Saran:", 
        placeholder="Tuliskan secara detail dan jelas masukan Anda demi penyempurnaan platform GENTALA ke depan..."
    )
    
    # Tombol Kirim di dalam Form
    submit_button = st.form_submit_button(label="🚀 Kirim Umpan Balik")

# 3. Logika Aksi Setelah Tombol Diklik
if submit_button:
    # Validasi: Isi pesan wajib diisi, tidak boleh kosong
    if not isi_pesan.strip():
        st.error("❌ Mohon maaf, kolom detail keluhan atau saran wajib diisi agar kami dapat mengevaluasinya.")
    else:
        try:
            # A. Membuat stempel waktu otomatis (Waktu Indonesia Tengah / WITA)
            waktu_sekarang = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # B. Validasi jika nama kosong atau hanya spasi, otomatis ubah jadi "Anonim"
            nama_fix = nama_pengirim.strip() if nama_pengirim.strip() != "" else "Anonim"
            
            # C. Menyusun data menjadi baris list
            data_baru = [waktu_sekarang, nama_fix, kategori_feedback, isi_pesan]
            
            # D. Memanggil secara spesifik TAB bernama "Pengaduan" di Google Sheets Dokter
            conn.append_row(data_baru, worksheet="Pengaduan")
            
            # E. Memasukkan data ke baris paling bawah pada Tab Pengaduan
            nama_worksheet_pengaduan.append_row(data_baru)
            
            # Jika berhasil, tampilkan pesan sukses
            st.success("✅ Terima kasih! Umpan balik Anda telah direkam dengan aman ke database internal Puskesmas Batu Tangga.")
            st.balloons() # Efek balon pelengkap biar interaktif di layar pengguna
            
        except Exception as e:
            # Jika koneksi database Sheets Dokter bermasalah, beri tahu pengguna
            st.error(f"❌ Terjadi kendala saat mengirim data ke server. Pastikan Tab 'Pengaduan' sudah dibuat di Google Sheets Anda. (Error: {e})")

# =========================================================================
# BAGIAN FOOTER / KONTAK UTAMA (BISA DILETAKKAN DI BAWAH FORM INI)
# =========================================================================

# Menambahkan footer sederhana
st.markdown("---")
st.caption(f"© 2026 Grow.TrackID - Puskesmas Batu Tangga | Crtd By: dr. Aflin Bihar")
