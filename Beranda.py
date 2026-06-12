import streamlit as st
import gspread
import base64
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
        
        # Membaca kredensial dari Streamlit Secrets
        creds = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"], 
            scopes=scope
        )
        client = gspread.authorize(creds)
        
        # Membuka file Spreadsheet utama secara utuh
        return client.open("GrowTrack Database")
    except Exception as e:
        return None

# Inisialisasi koneksi agar bisa dipakai di seluruh halaman
spreadsheet = init_connection()

# ==========================================
# 2. TAMPILAN UTAMA (BERANDA)
# ==========================================
st.title("🏥 Selamat Datang di GENTALA - Gerakan Terpadu Skrining Gizi, Mental, & Telekonsultasi Anak-Dewasa")
st.subheader("Inovasi Program Puskesmas Batu Tangga")

# Informasi Status Koneksi di Sidebar
if spreadsheet:
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

# ==========================================
# 3. BAGIAN EMBED MANUAL BOOK (METODE B)
# ==========================================
st.markdown("---")
st.markdown("### 📖 Buku Panduan Pengoperasian (Manual Book) GENTALA")
st.write(
    "Guna memudahkan kader posyandu dan tenaga kesehatan dalam mengoperasikan sistem, "
    "berikut adalah modul panduan langkah demi langkah yang dapat dibaca secara langsung:"
)

# Membaca file PDF lokal dari folder repository GitHub Dokter
try:
    with open("manual_book_gentala.pdf", "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    
    # Membuat komponen HTML iframe untuk menampilkan PDF secara interaktif
    pdf_display = f'''
        <iframe 
            src="data:application/pdf;base64,{base64_pdf}" 
            width="100%" 
            height="700px" 
            type="application/pdf"
            style="border: 1px solid #e2e8f0; border-radius: 8px;">
        </iframe>
    '''
    
    # Menampilkan file ke layar Streamlit
    st.markdown(pdf_display, unsafe_allow_html=True)

except FileNotFoundError:
    # Antisipasi jika file PDF belum di-upload ke GitHub atau salah ketik nama file
    st.warning("⚠️ File 'manual_book_gentala.pdf' belum ditemukan di sistem server GitHub Anda. Pastikan file telah dimasukkan ke folder yang sama dengan Beranda.py.")

# ==========================================
# 4. BAGIAN FOOTER / KONTAK BANTUAN
# ==========================================
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
    st.info(
        "6282157263167 🟢 WhatsApp Hotline\n\n"
        "Hubungi admin GENTALA untuk respon cepat:\n\n"
        "[💬 Chat WhatsApp Klik Disini](https://wa.me/6282157263167)"
    )

with col_email:
    st.info(
        "Aflinbihar0@gmail.com ✉️ Email Resmi\n\n"
        "Kirimkan surat atau laporan kendala tertulis:\n\n"
        "[📧 Kirim Email Klik Disini](mailto:Aflinbihar0@gmail.com)"
    )

# ==========================================
# 5. BAGIAN LAYANAN PENGADUAN & SARAN
# ==========================================
st.markdown("---") # Garis pembatas horizontal

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
        if not spreadsheet:
            st.error("❌ Terjadi kendala: Koneksi ke database terputus. Silakan hubungi Tim Teknis.")
        else:
            try:
                # A. Membuat stempel waktu otomatis (Waktu Indonesia Tengah / WITA)
                waktu_sekarang = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # B. Validasi jika nama kosong atau hanya spasi, otomatis ubah jadi "Anonim"
                nama_fix = nama_pengirim.strip() if nama_pengirim.strip() != "" else "Anonim"
                
                # C. Menyusun data menjadi baris list
                data_baru = [waktu_sekarang, nama_fix, kategori_feedback, isi_pesan]
                
                # D. Memanggil secara spesifik TAB bernama "Pengaduan" dari objek spreadsheet
                nama_worksheet_pengaduan = spreadsheet.worksheet("Pengaduan")
                
                # E. Memasukkan data ke baris paling bawah pada Tab Pengaduan
                nama_worksheet_pengaduan.append_row(data_baru)
                
                # Jika berhasil, tampilkan pesan sukses
                st.success("✅ Terima kasih! Umpan balik Anda telah direkam dengan aman ke database internal Puskesmas Batu Tangga.")
                st.balloons() # Efek balon pelengkap biar interaktif di layar pengguna
                
            except Exception as e:
                st.error(f"❌ Terjadi kendala saat mengirim data ke server. Pastikan Tab 'Pengaduan' sudah dibuat di Google Sheets Anda. (Error: {e})")

# =========================================================================
# BAGIAN FOOTER AKHIR
# =========================================================================
st.markdown("---")
st.caption(f"© 2026 Grow.TrackID - Puskesmas Batu Tangga | Crtd By: dr. Aflin Bihar")
