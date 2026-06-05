import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import urllib.parse

# ==========================================
# 1. KONEKSI DATABASE VIA STREAMLIT SECRETS
# ==========================================
def init_connection():
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        
        # BARU: Menggunakan st.secrets (Bukan file fisik Kunci.json)
        creds = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"], 
            scopes=scope
        )
        client = gspread.authorize(creds)
        return client.open("GrowTrack Database").sheet1
    except Exception:
        return None

sheet = init_connection()

# ==========================================
# 2. TAMPILAN APLIKASI & SIDEBAR LOGIN
# ==========================================
st.set_page_config(page_title="Synapse - Telemedicine", layout="wide")

st.title("🩺GENTALA-Fitur Telekonsultasi (Nakes - Dokter)")

# Inisialisasi status login di dalam session state agar tidak reset saat berinteraksi
if "akses_diberikan" not in st.session_state:
    st.session_state.akses_diberikan = False

with st.sidebar:
    if sheet:
        st.success("✅ Database Terhubung")
    else:
        st.error("❌ Database Terputus")
        
    role = st.selectbox("Masuk Sebagai:", ["Nakes Pengonsul", "Dokter Konsultan"])
    
    # Input password (Hanya ditampilkan jika belum berhasil login)
    if not st.session_state.akses_diberikan:
        password_input = st.text_input("Masukkan Password Akses:", type="password")
        tombol_login = st.button("🔑 MASUK / LOGIN", use_container_width=True)
        
        # Validasi dijalankan HANYA saat tombol login diklik
        if tombol_login:
            if role == "Nakes Pengonsul":
                if password_input == "nakes123":      # <-- Password Nakes
                    st.session_state.akses_diberikan = True
                    st.success("🔓 Akses Terverifikasi!")
                    st.rerun()
                else:
                    st.error("❌ Password Salah")
                    
            elif role == "Dokter Konsultan":
                if password_input == "dokter123":     # <-- Password Dokter
                    st.session_state.akses_diberikan = True
                    st.success("🔓 Akses Terverifikasi!")
                    st.rerun()
                else:
                    st.error("❌ Password Salah")
    else:
        # Tampilkan status jika sudah berhasil login dan tombol logout
        st.info(f"👤 Aktif sebagai: {role}")
        if st.button("🚪 LOGOUT / KELUAR", use_container_width=True):
            st.session_state.akses_diberikan = False
            st.rerun()

# ==========================================
# 3. KONTROL AKSES & LOGIKA UTAMA APLIKASI
# ==========================================
if st.session_state.akses_diberikan:

    if role == "Nakes Pengonsul":
        st.subheader("📝 Laporan Kasus Terstruktur")
        
        with st.form("form_telekonsultasi"):
            # Bagian 1: Identitas
            col1, col2, col3 = st.columns([2,1,1])
            with col1:
                nama_pasien = st.text_input("Inisial Pasien / No. RM")
            with col2:
                gender = st.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"])
            with col3:
                tgl_lahir = st.date_input("Tanggal Lahir", value=datetime(2024,1,1), min_value=datetime(1930,1,1))

            # Bagian 2: Klinis
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                berat_badan = st.number_input("BB (kg)", min_value=0.0)
                tinggi_badan = st.number_input("TB (cm)", min_value=0.0)
            with c2:
                temp = st.number_input("Suhu (°C)", value=36.5)
                kesadaran = st.selectbox("Kesadaran", ["Compos Mentis", "Apatis", "Somnolen", "Sopor", "Koma"])
            with c3:
                nadi = st.text_input("Nadi (x/mnt)")
                napas = st.text_input("Napas (x/mnt)")
            with c4:
                tekanan_darah = st.text_input("Tekanan Darah", placeholder="120/80")

            # Bagian 3: SOAP
            keluhan_utama = st.text_input("Keluhan Utama & Onset")
            keluhan_dipilih = st.multiselect("Gejala Penyerta:", ["Demam", "Nyeri kepala", "Pusing Berputar", "Pilek", "Batuk", "Nyeri menelan", "Mual", "Muntah", "Sesak", "Nyeri Dada", "Nyeri Ulu Hati", "Diare", "Nyeri Perut", "Nyeri Berkemih"])
            
            s1, s2 = st.columns(2)
            with s1:
                lokasi_kualitas = st.text_area("Kualitas Keluhan (Sacred Seven)")
            with s2:
                faktor_penyerta = st.text_area("Faktor Memperberat/Meringankan")
                
            riwayat_alergi = st.text_input("Riwayat Medis/Alergi")
            pemeriksaan_fisik = st.text_area("Hasil Pemeriksaan Fisik (O)")
            assessment_plan = st.text_area("Assessment & Plan Awal (A/P)")

            submit_btn = st.form_submit_button("KIRIM LAPORAN KE DOKTER")

        # LOGIKA PENGIRIMAN DATA NAKES
        if submit_btn:
            if sheet and nama_pasien and keluhan_utama:
                with st.spinner("Menyimpan data laporan ke database..."):
                    try:
                        waktu_skrg = datetime.now().strftime("%d/%m/%Y %H:%M")
                        gejala_str = ", ".join(keluhan_dipilih) if keluhan_dipilih else "-"
                        
                        detail_gabungan = (
                            f"PASIEN: {gender} | BB:{berat_badan}kg | TB:{tinggi_badan}cm | S:{temp}°C\n"
                            f"TD: {tekanan_darah} mmHg | NADI:{nadi} | NAPAS:{napas} | KES:{kesadaran}\n\n"
                            f"--- ANAMNESIS ---\n"
                            f"K. UTAMA: {keluhan_utama}\n"
                            f"PENYERTA: {gejala_str}\n"
                            f"KUALITAS: {lokasi_kualitas}\n"
                            f"FAKTOR +/-: {faktor_penyerta}\n"
                            f"RIWAYAT: {riwayat_alergi}\n\n"
                            f"--- FISIK ---\n{pemeriksaan_fisik}\n\n"
                            f"--- A/P ---\n{assessment_plan}"
                        )
                        
                        # Menyusun baris baru ke Google Sheets
                        baris_baru = [waktu_skrg, "Nakes Pengonsul", nama_pasien, detail_gabungan, "-", "Menunggu Jawaban"]
                        sheet.append_row(baris_baru)
                        st.success("✅ Data Lengkap berhasil disimpan di Database!")

                        # SETUP WHATSAPP GATEWAY DOKTER
                        no_wa_dokter = "6282157263167"
                        pesan_wa = (
                            f"*KONSULTASI BARU: {nama_pasien}*\n"
                            f"TD: {tekanan_darah} | S: {temp} | Nadi: {nadi}\n"
                            f"*Keluhan:* {keluhan_utama}\n"
                            f"*Penyerta:* {gejala_str}\n"
                            f"------------------------\n"
                            f"Mohon arahan lanjut, Dok. SOAP lengkap sudah masuk Dashboard."
                        )
                        
                        url_wa = f"https://wa.me/{no_wa_dokter}?text={urllib.parse.quote(pesan_wa)}"
                        
                        st.markdown(f"""
                            <a href="{url_wa}" target="_blank">
                                <button style="background-color:#25D366; color:white; border:none; padding:12px; border-radius:5px; width:100%; cursor:pointer; font-weight:bold;">
                                    📱 LANJUTKAN KIRIM KE WHATSAPP DOKTER
                                </button>
                            </a>
                            """, unsafe_allow_html=True)
                        
                        st.balloons()
                    except Exception as e:
                        st.error(f"Gagal simpan ke database: {e}")
            else:
                st.error("Gagal mengirim! Lengkapi identitas nama pasien dan keluhan utama terlebih dahulu.")

    else:
        # SISI DOKTER KONSULTAN (DAFTAR KONSUL)
        st.subheader("📥 Daftar Konsultasi Masuk")
        if sheet:
            with st.spinner("Memuat daftar konsultasi dari Google Sheets..."):
                # Mengambil baris data mentah agar penulisan indeks kolom (1-6) lebih aman
                data_mentah = sheet.get_all_values()
            
            if len(data_mentah) > 1:
                headers = data_mentah[0]
                baris_isi = data_mentah[1:]
                
                # Menemukan indeks kolom Status dan Jawaban berdasarkan header
                try:
                    idx_status = headers.index("Status")
                    idx_jawaban = headers.index("Jawaban/Saran Dokter") if "Jawaban/Saran Dokter" in headers else 4 # Fallback kolom ke-5
                except ValueError:
                    # Default jika nama header kolom kustom berbeda
                    idx_status = 5 # Kolom F (0-indexed: 5)
                    idx_jawaban = 4 # Kolom E (0-indexed: 4)

                ada_pasien = False
                
                # Menampilkan data dari baris paling baru (Reversed)
                for i in reversed(range(len(baris_isi))):
                    row = baris_isi[i]
                    nomor_baris_sheets = i + 2 # Header + 0-index offset
                    
                    # Cek status 'Menunggu Jawaban'
                    if row[idx_status] == "Menunggu Jawaban":
                        ada_pasien = True
                        timestamp = row[0]
                        nama_p = row[2]
                        detail_k = row[3]
                        
                        with st.expander(f"🔴 {timestamp} - {nama_p}"):
                            st.text(detail_k)
                            jawab = st.text_area("Balasan Dokter / Rencana Terapi:", key=f"ans_{nomor_baris_sheets}")
                            
                            if st.button("Kirim Jawaban Klinik", key=f"btn_{nomor_baris_sheets}"):
                                if jawab.strip():
                                    with st.spinner("Mengirim balasan ke database..."):
                                        # Update kolom Jawaban (kolom ke-5 / E) dan Status (kolom ke-6 / F)
                                        sheet.update_cell(nomor_baris_sheets, idx_jawaban + 1, jawab)
                                        sheet.update_cell(nomor_baris_sheets, idx_status + 1, "Sudah Dijawab")
                                    st.success("✅ Jawaban dan instruksi medis berhasil dikirim!")
                                    st.rerun()
                                else:
                                    st.error("Isi balasan dokter tidak boleh kosong!")
                
                if not ada_pasien:
                    st.info("🟢 Belum ada data konsultasi baru yang memerlukan jawaban.")
            else:
                st.info("🟢 Belum ada data konsultasi di dalam lembar database.")
        else:
            st.error("Koneksi database ke Google Sheets terputus.")

else:
    # Tampilan awal beranda pengunci sebelum login
    st.info("👋 Silakan tentukan Akses Menu, masukkan Password dengan benar, kemudian klik tombol **MASUK / LOGIN** pada sidebar di sebelah kiri.")
