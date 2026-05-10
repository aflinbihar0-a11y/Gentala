import streamlit as st
import pandas as pd
import datetime
import os

st.set_page_config(page_title="Grow.TrackID", page_icon="🩺")

st.title("🩺 Grow.TrackID")
st.write("Inovasi Program Puskesmas Batu Tangga")

# --- SETUP PATH OTOMATIS ---
# Menghindari error "No such file or directory" karena file berada di folder 'pages'
current_dir = os.path.dirname(__file__)

# --- FORM INPUT ---
with st.form("input_data"):
    st.markdown("### 📋 Form Input Data Pasien")
    nama = st.text_input("Nama Anak")
    jk = st.radio("Jenis Kelamin", ["Laki-laki", "Perempuan"])
    tgl_lahir = st.date_input("Tanggal Lahir", value=datetime.date(2024, 1, 1))
    tgl_periksa = st.date_input("Tanggal Pemeriksaan")
    tinggi = st.number_input("Tinggi/Panjang Badan (cm)", format="%.1f")
    berat = st.number_input("Berat Badan (kg)", format="%.1f")
    submitted = st.form_submit_button("SUBMIT DATA")

# --- FUNGSI Z-SCORE (STANDAR WHO) ---
def hitung_zscore(nilai, median, sd_min1, sd_plus1):
    if nilai < median:
        return (nilai - median) / (median - sd_min1)
    else:
        return (nilai - median) / (sd_plus1 - median)

if submitted:
    # Perhitungan umur bulat sesuai standar puskesmas (24 bulan tetap 24)
    hari = (tgl_periksa - tgl_lahir).days
    umur_bulan = round(hari / 30.44)
    prefix = "Laki" if jk == "Laki-laki" else "Perempuan"
    
    try:
        # Load file dengan path absolut agar tidak error di folder 'pages'
        df_bb = pd.read_excel(os.path.join(current_dir, f"BB_{prefix}.xlsx"))
        df_tb = pd.read_excel(os.path.join(current_dir, f"TB_{prefix}.xlsx"))
        
        st.divider()
        st.subheader(f"Hasil Analisis: {nama}")
        st.info(f"Analisis berdasarkan Umur: {umur_bulan} Bulan")

        # --- 1. ANALISIS BB/U ---
        data_bb = df_bb[df_bb['Umur (bulan)'] == umur_bulan]
        if not data_bb.empty:
            row = data_bb.iloc[0]
            z_bb = hitung_zscore(berat, row['Median'], row['-1 SD'], row['+1 SD'])
            st.write(f"**Z-Score BB/U:** `{z_bb:.2f} SD`")
            if z_bb < -3: st.error("Status: Berat badan sangat kurang")
            elif z_bb < -2: st.warning("Status: Berat badan kurang")
            elif z_bb <= 1: st.success("Status: Berat badan normal")
            else: st.info("Status: Risiko berat badan lebih")

        # --- 2. ANALISIS TB/U ---
        data_tb = df_tb[df_tb['Umur (bulan)'] == umur_bulan]
        if not data_tb.empty:
            row_t = data_tb.iloc[0]
            z_tb = hitung_zscore(tinggi, row_t['Median'], row_t['-1 SD'], row_t['+1 SD'])
            st.write(f"**Z-Score TB/U:** `{z_tb:.2f} SD`")
            if z_tb < -3: st.error("Status: Sangat pendek (Severely stunted)")
            elif z_tb < -2: st.error("Status: Pendek (Stunted)")
            elif z_tb <= 3: st.success("Status: Normal")
            else: st.info("Status: Tinggi")

        # --- 3. ANALISIS BB/TB (WASTING) ---
        file_w_name = f"BBPB_0_24_{prefix}.xlsx" if umur_bulan <= 24 else f"BBTB_24_60_{prefix}.xlsx"
        kolom_tb = "Panjang Badan (cm)" if umur_bulan <= 24 else "Tinggi Badan (cm)"
        
        df_w = pd.read_excel(os.path.join(current_dir, file_w_name))
        t_lookup = round(tinggi * 2) / 2
        data_w = df_w[df_w[kolom_tb] == t_lookup]
        
        if not data_w.empty:
            row_w = data_w.iloc[0]
            z_w = hitung_zscore(berat, row_w['Median'], row_w['-1 SD'], row_w['+1 SD'])
            st.write(f"**Z-Score BB/TB:** `{z_w:.2f} SD`")
            if z_w < -3: st.error("Status: Gizi buruk")
            elif z_w < -2: st.warning("Status: Gizi kurang")
            elif z_w <= 1: st.success("Status: Gizi baik (Normal)")
            elif z_w <= 2: st.info("Status: Berisiko gizi lebih")
            elif z_w <= 3: st.warning("Status: Gizi lebih")
            else: st.error("Status: Obesitas")

    except Exception as e:
        st.error(f"Error: {e}")
        st.info("Pastikan semua file Excel referensi ada di dalam folder 'pages'.")