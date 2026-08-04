import streamlit as st
import pandas as pd
import datetime
import os
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Grow.TrackID", page_icon="🩺")

st.title("🩺 GENTALA - Skrining Gizi")
st.write("Inovasi Program Puskesmas Batu Tangga")

# --- SETUP PATH OTOMATIS FOR EXCEL ---
current_dir = os.path.dirname(__file__)

# --- KONEKSI GOOGLE SPREADSHEET ---
def koneksi_spreadsheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_dict = st.secrets["gcp_service_account"] 
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(creds)
    sheet = client.open("GrowTrack Database").worksheet("Sheet2")
    return sheet

# --- FUNGSI VALIDASI ANTROPOMETRI (SANITY CHECK) ---
def validasi_input_antropometri(bb, tb):
    """
    Mengecek kelayakan data antropometri sebelum dihitung dan disimpan.
    """
    # 1. Cek apabila TB dan BB tertukar atau terbalik
    if tb <= bb:
        return False, (
            f"⚠️ **Peringatan Data Tidak Valid:** Tinggi/Panjang Badan ({tb:.1f} cm) "
            f"kurang dari atau sama dengan Berat Badan ({bb:.1f} kg).\n\n"
            "Posisi input **terindikasi tertukar** atau terdapat kesalahan ketik (typo). "
            "Mohon periksa dan perbaiki nilai TB dan BB sebelum melanjutkan."
        )
    
    # 2. Cek rentang nilai fisis wajar untuk balita (0-60 bulan)
    if tb < 30.0 or tb > 130.0:
        return False, (
            f"⚠️ **Peringatan Tinggi Badan:** Nilai TB ({tb:.1f} cm) berada di luar rentang "
            "wajar pemeriksaan balita (30.0 cm - 130.0 cm)."
        )
        
    if bb < 1.0 or bb > 40.0:
        return False, (
            f"⚠️ **Peringatan Berat Badan:** Nilai BB ({bb:.1f} kg) berada di luar rentang "
            "wajar pemeriksaan balita (1.0 kg - 40.0 kg)."
        )

    return True, ""

# --- FORM INPUT ---
with st.form("input_data"):
    st.markdown("### 📋 Form Input Data Pasien")
    nama = st.text_input("Nama Anak")
    alamat_pasien = st.selectbox(
        "Alamat (Desa/Kelurahan)",
        ["Batu Tangga", "Muara Hungi", "Pembakulan", "Nateh", "Datar Batung", "Desa Lainnya"]
    )
    jk = st.radio("Jenis Kelamin", ["Laki-laki", "Perempuan"])
    st.markdown("*(Sesuai aturan Kemenkes, sisa hari tidak digenapkan ke atas. Contoh: 2 bulan 29 hari = 2 bulan)*")
    tgl_lahir = st.date_input("Tanggal Lahir", value=datetime.date(2024, 1, 1))
    tgl_periksa = st.date_input("Tanggal Pemeriksaan")
    tinggi = st.number_input("Tinggi/Panjang Badan (cm)", format="%.1f")
    berat = st.number_input("Berat Badan (kg)", format="%.1f")
    submitted = st.form_submit_button("SUBMIT DATA & SIMPAN")

# --- FUNGSI Z-SCORE KONDISIONAL MULTI-LEVEL (PRESISI KEMENKES) ---
def hitung_zscore_multi(nilai, m, sd_m1, sd_m2, sd_m3, sd_p1, sd_p2, sd_p3):
    if nilai == m:
        return 0.0
    
    # Jika nilai berada di bawah median
    elif nilai < m:
        if nilai >= sd_m1:
            return (nilai - m) / (m - sd_m1)
        elif nilai >= sd_m2:
            return -1.0 + ((nilai - sd_m1) / (sd_m1 - sd_m2))
        elif nilai >= sd_m3:
            return -2.0 + ((nilai - sd_m2) / (sd_m2 - sd_m3))
        else:
            return -3.0 + ((nilai - sd_m3) / (sd_m2 - sd_m3))
            
    # Jika nilai berada di atas median
    else:
        if nilai <= sd_p1:
            return (nilai - m) / (sd_p1 - m)
        elif nilai <= sd_p2:
            return 1.0 + ((nilai - sd_p1) / (sd_p2 - sd_p1))
        elif nilai <= sd_p3:
            return 2.0 + ((nilai - sd_p2) / (sd_p3 - sd_p2))
        else:
            return 3.0 + ((nilai - sd_p3) / (sd_p3 - sd_p2))

if submitted:
    # --- PROSES VALIDASI INPUT AWAL ---
    is_valid, pesan_error = validasi_input_antropometri(berat, tinggi)
    if not is_valid:
        st.error(pesan_error)
        st.stop()  # Menghentikan eksekusi jika data terdeteksi tertukar/tidak valid

    # --- LOGIKA UMUR BULAN PENUH (STANDAR KEMENKES) ---
    selisih_tahun = tgl_periksa.year - tgl_lahir.year
    selisih_bulan = tgl_periksa.month - tgl_lahir.month
    umur_bulan = (selisih_tahun * 12) + selisih_bulan
    if tgl_periksa.day < tgl_lahir.day:
        umur_bulan -= 1
    if umur_bulan < 0:
        umur_bulan = 0
        
    prefix = "Laki" if jk == "Laki-laki" else "Perempuan"
    
    try:
        # Load file referensi kriteria WHO
        df_bb = pd.read_excel(os.path.join(current_dir, f"BB_{prefix}.xlsx"))
        df_tb = pd.read_excel(os.path.join(current_dir, f"TB_{prefix}.xlsx"))
        
        st.divider()
        st.subheader(f"Hasil Analisis: {nama}")
        st.info(f"Analisis berdasarkan Umur: {umur_bulan} Bulan (Standar Buku Antropometri Kemenkes)")

        status_bbu, status_tbu, status_bbtb = "Tidak Diketahui", "Tidak Diketahui", "Tidak Diketahui"
        z_bb, z_tb, z_w = 0.0, 0.0, 0.0

        # --- 1. ANALISIS BB/U ---
        data_bb = df_bb[df_bb['Umur (bulan)'] == umur_bulan]
        if not data_bb.empty:
            row = data_bb.iloc[0]
            z_bb = hitung_zscore_multi(berat, row['Median'], row['-1 SD'], row['-2 SD'], row['-3 SD'], row['+1 SD'], row['+2 SD'], row['+3 SD'])
            st.write(f"**Z-Score BB/U:** `{z_bb:.2f} SD`")
            if z_bb < -3: status_bbu = "Berat badan sangat kurang"
            elif z_bb < -2: status_bbu = "Berat badan kurang"
            elif z_bb <= 1: status_bbu = "Berat badan normal"
            else: status_bbu = "Risiko berat badan lebih"
            st.caption(f"Status: {status_bbu}")

        # --- 2. ANALISIS TB/U ---
        data_tb = df_tb[df_tb['Umur (bulan)'] == umur_bulan]
        if not data_tb.empty:
            row_t = data_tb.iloc[0]
            z_tb = hitung_zscore_multi(tinggi, row_t['Median'], row_t['-1 SD'], row_t['-2 SD'], row_t['-3 SD'], row_t['+1 SD'], row_t['+2 SD'], row_t['+3 SD'])
            st.write(f"**Z-Score TB/U:** `{z_tb:.2f} SD`")
            if z_tb < -3: status_tbu = "Sangat pendek (Severely stunted)"
            elif z_tb < -2: status_tbu = "Pendek (Stunted)"
            elif z_tb <= 3: status_tbu = "Normal"
            else: status_tbu = "Tinggi"
            st.caption(f"Status: {status_tbu}")

        # --- 3. ANALISIS BB/TB (WASTING) ---
        file_w_name = f"BBPB_0_24_{prefix}.xlsx" if umur_bulan <= 24 else f"BBTB_24_60_{prefix}.xlsx"
        kolom_tb = "Panjang Badan (cm)" if umur_bulan <= 24 else "Tinggi Badan (cm)"
        
        df_w = pd.read_excel(os.path.join(current_dir, file_w_name))
        t_lookup = round(tinggi * 2) / 2
        data_w = df_w[df_w[kolom_tb] == t_lookup]
        
        if not data_w.empty:
            row_w = data_w.iloc[0]
            z_w = hitung_zscore_multi(berat, row_w['Median'], row_w['-1 SD'], row_w['-2 SD'], row_w['-3 SD'], row_w['+1 SD'], row_w['+2 SD'], row_w['+3 SD'])
            st.write(f"**Z-Score BB/TB:** `{z_w:.2f} SD`")
            if z_w < -3: status_bbtb = "Gizi buruk"
            elif z_w < -2: status_bbtb = "Gizi kurang"
            elif z_w <= 1: status_bbtb = "Gizi baik (Normal)"
            elif z_w <= 2: status_bbtb = "Berisiko gizi lebih"
            elif z_w <= 3: status_bbtb = "Gizi lebih"
            else: status_bbtb = "Obesitas"
            st.caption(f"Status: {status_bbtb}")

        # --- PROSES SIMPAN KE GOOGLE SPREADSHEET ---
        with st.spinner("Sedang menyimpan data ke database Google Sheets..."):
            try:
                sheet = koneksi_spreadsheet()
                baris_baru = [
                    str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                    nama, alamat_pasien, jk, str(tgl_lahir), str(tgl_periksa), umur_bulan, tinggi, berat,
                    f"{z_bb:.2f}", status_bbu, f"{z_tb:.2f}", status_tbu, f"{z_w:.2f}", status_bbtb
                ]
                sheet.append_row(baris_baru)
                st.success("✅ Data pasien dan hasil skrining berhasil disimpan ke Google Sheets!")
                
            except Exception as sheet_err:
                st.error(f"Gagal menyimpan ke Spreadsheet: {sheet_err}")

    except Exception as e:
        st.error(f"Error: {e}")
