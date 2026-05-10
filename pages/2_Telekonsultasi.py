import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import urllib.parse

# ==========================================
# 1. KONEKSI DATABASE
# ==========================================
def init_connection():
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        
        # Ambil data dari Secrets Streamlit (yang tadi Dokter paste di menu Secrets)
        creds_dict = st.secrets["gcp_service_account"]
        creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
        
        client = gspread.authorize(creds)
        return client.open("GrowTrack Database").sheet1
    except Exception as e:
        # Jika gagal, pesan error akan muncul di aplikasi
        st.error(f"Gagal Terhubung: {e}")
        return None

sheet = init_connection()

# ==========================================
# 2. TAMPILAN APLIKASI
# ==========================================
st.set_page_config(page_title="Synapse - Telemedicine", layout="wide")

st.title("🩺 Fitur Telekonsultasi (Nakes - Dokter)")

with st.sidebar:
    if sheet:
        st.success("✅ Database Terhubung")
    else:
        st.error("❌ Database Terputus")
    role = st.selectbox("Masuk Sebagai:", ["Nakes Desa", "Dokter Konsultan"])

if role == "Nakes Desa":
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

    # LOGIKA PENGIRIMAN (Harus sejajar dengan 'with st.form')
    if submit_btn:
        if sheet and nama_pasien and keluhan_utama:
            try:
                waktu_skrg = datetime.now().strftime("%d/%m/%Y %H:%M")
                
                # 1. Mengolah Gejala Penyerta agar tidak hilang
                gejala_str = ", ".join(keluhan_dipilih) if keluhan_dipilih else "-"
                
                # 2. Format Lengkap untuk Spreadsheet (Database)
                # Saya masukkan kembali PENYERTA dan FAKTOR +/- yang sebelumnya hilang
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
                
                # 3. Simpan ke Google Sheets
                baris_baru = [waktu_skrg, "Nakes Desa", nama_pasien, detail_gabungan, "-", "Menunggu Jawaban"]
                sheet.append_row(baris_baru)
                st.success("✅ Data Lengkap berhasil disimpan di Database!")

                # 4. SETUP WHATSAPP DOKTER
                no_wa_dokter = "6282157263167" # Nomor Dokter Aflin
                
                # Format pesan WA (dibuat ringkas namun informatif)
                pesan_wa = (
                    f"*KONSULTASI BARU: {nama_pasien}*\n"
                    f"TD: {tekanan_darah} | S: {temp} | Nadi: {nadi}\n"
                    f"*Keluhan:* {keluhan_utama}\n"
                    f"*Penyerta:* {gejala_str}\n"
                    f"------------------------\n"
                    f"Mohon arahan lanjut, Dok. SOAP lengkap sudah masuk Dashboard."
                )
                
                url_wa = f"https://wa.me/{no_wa_dokter}?text={urllib.parse.quote(pesan_wa)}"
                
                # Tampilkan tombol WA
                st.markdown(f"""
                    <a href="{url_wa}" target="_blank">
                        <button style="background-color:#25D366; color:white; border:none; padding:12px; border-radius:5px; width:100%; cursor:pointer; font-weight:bold;">
                            📱 LANJUTKAN KIRIM KE WHATSAPP DOKTER
                        </button>
                    </a>
                    """, unsafe_allow_html=True)
                
                st.balloons()
            except Exception as e:
                st.error(f"Gagal simpan: {e}")
        else:
            st.error("Lengkapi identitas dan keluhan utama!")

else:
    # Sisi Dokter (Daftar Konsul)
    st.subheader("📥 Daftar Konsultasi Masuk")
    if sheet:
        data = sheet.get_all_records()
        for i, row in enumerate(reversed(data)):
            if row['Status'] == "Menunggu Jawaban":
                with st.expander(f"🔴 {row['Timestamp']} - {row['Nama_Pasien']}"):
                    st.text(row['Detail_Klinis'])
                    jawab = st.text_area("Balasan Dokter:", key=f"ans_{i}")
                    if st.button("Kirim Jawaban", key=f"btn_{i}"):
                        idx = len(data) - i + 1
                        sheet.update_cell(idx, 5, jawab)
                        sheet.update_cell(idx, 6, "Sudah Dijawab")
                        st.success("Jawaban terkirim!")
                        st.rerun()
