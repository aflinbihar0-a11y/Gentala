import os
import datetime
import pandas as pd
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import plotly.graph_objects as go

# =========================================================================
# FUNGSI HELPER: KURVA PERTUMBUHAN INTERAKTIF
# =========================================================================
def plot_kurva_zscore(df_ref, x_col, x_val, y_val, title_text, x_label, y_label):
    df_chart = df_ref.copy().sort_values(x_col)

    c_sd3neg = '- 3 SD' if '- 3 SD' in df_chart.columns else '-3 SD'
    c_sd2neg = '- 2 SD' if '- 2 SD' in df_chart.columns else '-2 SD'
    c_sd1neg = '- 1 SD' if '- 1 SD' in df_chart.columns else '-1 SD'
    c_median = 'Median' if 'Median' in df_chart.columns else 'MEDIAN'
    c_sd1pos = '+1 SD' if '+1 SD' in df_chart.columns else '+ 1 SD'
    c_sd2pos = '+2 SD' if '+2 SD' in df_chart.columns else '+ 2 SD'
    c_sd3pos = '+3 SD' if '+3 SD' in df_chart.columns else '+ 3 SD'

    fig = go.Figure()

    # Garis-garis SD Kemenkes
    fig.add_trace(go.Scatter(x=df_chart[x_col], y=df_chart[c_sd3neg], mode='lines', name='-3 SD', line=dict(color='#8B0000', width=1.5)))
    fig.add_trace(go.Scatter(x=df_chart[x_col], y=df_chart[c_sd2neg], mode='lines', name='-2 SD', line=dict(color='#FF0000', width=1.5)))
    fig.add_trace(go.Scatter(x=df_chart[x_col], y=df_chart[c_sd1neg], mode='lines', name='-1 SD', line=dict(color='#FFD700', width=1.5)))
    fig.add_trace(go.Scatter(x=df_chart[x_col], y=df_chart[c_median], mode='lines', name='Median', line=dict(color='#00FF00', width=2)))
    fig.add_trace(go.Scatter(x=df_chart[x_col], y=df_chart[c_sd1pos], mode='lines', name='+1 SD', line=dict(color='#FFD700', width=1.5)))
    fig.add_trace(go.Scatter(x=df_chart[x_col], y=df_chart[c_sd2pos], mode='lines', name='+2 SD', line=dict(color='#FF0000', width=1.5)))
    fig.add_trace(go.Scatter(x=df_chart[x_col], y=df_chart[c_sd3pos], mode='lines', name='+3 SD', line=dict(color='#8B0000', width=1.5)))

    # Plot Titik Posisi Pasien
    fig.add_trace(go.Scatter(
        x=[x_val],
        y=[y_val],
        mode='markers',
        name='Anak Anda',
        marker=dict(color='blue', size=12, symbol='circle')
    ))

    fig.update_layout(
        title=f"<b>{title_text}</b>",
        xaxis_title=x_label,
        yaxis_title=y_label,
        legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5),
        margin=dict(l=20, r=20, t=40, b=20),
        template="plotly_white"
    )

    return fig

# =========================================================================
# CONFIG & HELPER SETUP
# =========================================================================
st.set_page_config(page_title="Grow.TrackID - Skrining Gizi", page_icon="🩺", layout="centered")

current_dir = os.path.dirname(__file__)

def koneksi_spreadsheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_dict = st.secrets["gcp_service_account"] 
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(creds)
    sheet = client.open("GrowTrack Database").worksheet("Sheet2")
    return sheet

@st.cache_data
def load_ref_imtu():
    df_l = pd.read_excel(os.path.join(current_dir, "IMT-U 5-18 thn L.xlsx"), header=1)
    df_p = pd.read_excel(os.path.join(current_dir, "IMT-U 5-18 Thn P.xlsx"), header=1)
    return df_l, df_p

def validasi_input_antropometri(bb, tb):
    if tb <= bb:
        return False, (
            f"⚠️ **Peringatan Data Tidak Valid:** Tinggi/Panjang Badan ({tb:.1f} cm) "
            f"kurang dari atau sama dengan Berat Badan ({bb:.1f} kg).\n\n"
            "Posisi input **terindikasi tertukar** atau terdapat kesalahan ketik (typo). "
            "Mohon periksa dan perbaiki nilai TB dan BB sebelum melanjutkan."
        )
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

def hitung_zscore_multi(nilai, m, sd_m1, sd_m2, sd_m3, sd_p1, sd_p2, sd_p3):
    if nilai == m:
        return 0.0
    elif nilai < m:
        if nilai >= sd_m1:
            return (nilai - m) / (m - sd_m1)
        elif nilai >= sd_m2:
            return -1.0 + ((nilai - sd_m1) / (sd_m1 - sd_m2))
        elif nilai >= sd_m3:
            return -2.0 + ((nilai - sd_m2) / (sd_m2 - sd_m3))
        else:
            return -3.0 + ((nilai - sd_m3) / (sd_m2 - sd_m3))
    else:
        if nilai <= sd_p1:
            return (nilai - m) / (sd_p1 - m)
        elif nilai <= sd_p2:
            return 1.0 + ((nilai - sd_p1) / (sd_p2 - sd_p1))
        elif nilai <= sd_p3:
            return 2.0 + ((nilai - sd_p2) / (sd_p3 - sd_p2))
        else:
            return 3.0 + ((nilai - sd_p3) / (sd_p3 - sd_p2))

# =========================================================================
# TAMPILAN UTAMA & NAVIGASI TABS
# =========================================================================
st.title("🩺 GENTALA - Skrining Gizi")
st.write("Inovasi Program Puskesmas Batu Tangga")

tab1, tab2, tab3 = st.tabs([
    "👶 Anak 0-5 Tahun (Balita)", 
    "🧒 Anak 5-18 Tahun (IMT/U)", 
    "⚖️ Indeks Massa Tubuh (Dewasa)"
])

# =========================================================================
# TAB 1: ANAK 0-5 TAHUN (BALITA)
# =========================================================================
with tab1:
    with st.form("input_data_balita"):
        st.markdown("### 📋 Form Input Data Pasien Balita")
        nama = st.text_input("Nama Anak", key="tab1_nama")
        alamat_pasien = st.selectbox(
            "Alamat (Desa/Kelurahan)",
            ["Batu Tangga", "Muara Hungi", "Pembakulan", "Nateh", "Datar Batung", "Desa Lainnya"],
            key="tab1_alamat"
        )
        jk = st.radio("Jenis Kelamin", ["Laki-laki", "Perempuan"], key="tab1_jk")
        st.markdown("*(Sesuai aturan Kemenkes, sisa hari tidak digenapkan ke atas. Contoh: 2 bulan 29 hari = 2 bulan)*")
        tgl_lahir = st.date_input("Tanggal Lahir", value=datetime.date(2024, 1, 1), key="tab1_tgl_lahir")
        tgl_periksa = st.date_input("Tanggal Pemeriksaan", value=datetime.date.today(), key="tab1_tgl_periksa")
        tinggi = st.number_input("Tinggi/Panjang Badan (cm)", format="%.1f", key="tab1_tb")
        berat = st.number_input("Berat Badan (kg)", format="%.1f", key="tab1_bb")
        submitted = st.form_submit_button("SUBMIT DATA & SIMPAN")

    if submitted:
        is_valid, pesan_error = validasi_input_antropometri(berat, tinggi)
        if not is_valid:
            st.error(pesan_error)
            st.stop()

        selisih_tahun = tgl_periksa.year - tgl_lahir.year
        selisih_bulan = tgl_periksa.month - tgl_lahir.month
        umur_bulan = (selisih_tahun * 12) + selisih_bulan
        if tgl_periksa.day < tgl_lahir.day:
            umur_bulan -= 1
        if umur_bulan < 0:
            umur_bulan = 0
            
        prefix = "Laki" if jk == "Laki-laki" else "Perempuan"
        
        try:
            df_bb = pd.read_excel(os.path.join(current_dir, f"BB_{prefix}.xlsx"))
            df_tb = pd.read_excel(os.path.join(current_dir, f"TB_{prefix}.xlsx"))
            
            st.divider()
            st.subheader(f"Hasil Analisis: {nama}")
            st.info(f"Analisis berdasarkan Umur: {umur_bulan} Bulan (Standar Buku Antropometri Kemenkes)")

            status_bbu, status_tbu, status_bbtb = "Tidak Diketahui", "Tidak Diketahui", "Tidak Diketahui"
            z_bb, z_tb, z_w = 0.0, 0.0, 0.0

            # 1. ANALISIS BB/U
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

            # 2. ANALISIS TB/U
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

            # 3. ANALISIS BB/TB (WASTING)
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

            # =========================================================
            # 📈 TAMPILAN 3 KURVA PERTUMBUHAN INTERAKTIF (TAB 1)
            # =========================================================
            st.markdown("#### 📈 Grafis Kurva Pertumbuhan Pasien")
            tab_k1, tab_k2, tab_k3 = st.tabs([
                "📊 BB Menurut Umur (BB/U)", 
                "📏 TB/PB Menurut Umur (TB/U)", 
                "⚖️ BB Menurut TB/PB (BB/TB)"
            ])

            with tab_k1:
                fig_bbu = plot_kurva_zscore(
                    df_bb, 
                    x_col='Umur (bulan)', 
                    x_val=umur_bulan, 
                    y_val=berat, 
                    title_text="Kurva Berat Badan Menurut Umur (BB/U)", 
                    x_label="Umur (Bulan)", 
                    y_label="Berat Badan (kg)"
                )
                st.plotly_chart(fig_bbu, use_container_width=True)

            with tab_k2:
                label_tb = "Panjang Badan (cm)" if umur_bulan <= 24 else "Tinggi Badan (cm)"
                fig_tbu = plot_kurva_zscore(
                    df_tb, 
                    x_col='Umur (bulan)', 
                    x_val=umur_bulan, 
                    y_val=tinggi, 
                    title_text=f"Kurva {label_tb} Menurut Umur (TB/U)", 
                    x_label="Umur (Bulan)", 
                    y_label=label_tb
                )
                st.plotly_chart(fig_tbu, use_container_width=True)

            with tab_k3:
                fig_bbtb = plot_kurva_zscore(
                    df_w, 
                    x_col=kolom_tb, 
                    x_val=tinggi, 
                    y_val=berat, 
                    title_text=f"Kurva Berat Badan Menurut {label_tb} (BB/TB)", 
                    x_label=label_tb, 
                    y_label="Berat Badan (kg)"
                )
                st.plotly_chart(fig_bbtb, use_container_width=True)

            # PROSES SIMPAN KE GOOGLE SPREADSHEET
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

# =========================================================================
# TAB 2: ANAK 5-18 TAHUN (IMT/U PRESISI & SIMPAN KE SHEET3)
# =========================================================================
with tab2:
    st.markdown("### 📏 Skrining Gizi Anak & Remaja (5-18 Tahun)")
    
    col_id1, col_id2 = st.columns(2)
    with col_id1:
        nama_rem = st.text_input("Nama Anak/Remaja:", key="tab2_nama")
        jk_rem = st.selectbox("Jenis Kelamin:", ["Laki-laki", "Perempuan"], key="tab2_jk")
    with col_id2:
        tgl_lahir_rem = st.date_input("Tanggal Lahir:", value=datetime.date(2015, 1, 1), key="tab2_tgl_lahir")
        tgl_periksa_rem = st.date_input("Tanggal Pemeriksaan:", value=datetime.date.today(), key="tab2_tgl_periksa")

    total_bulan_rem = (tgl_periksa_rem.year - tgl_lahir_rem.year) * 12 + (tgl_periksa_rem.month - tgl_lahir_rem.month)
    if tgl_periksa_rem.day < tgl_lahir_rem.day:
        total_bulan_rem -= 1

    tahun_lookup = total_bulan_rem // 12
    bulan_lookup = total_bulan_rem % 12

    st.info(f"ℹ️ **Umur Terkalkulasi:** {tahun_lookup} Tahun {bulan_lookup} Bulan ({total_bulan_rem} Bulan)")

    col_bb, col_tb = st.columns(2)
    with col_bb:
        bb_rem = st.number_input("Berat Badan (kg):", min_value=5.0, max_value=150.0, value=33.0, step=0.1, key="tab2_bb")
    with col_tb:
        tb_rem = st.number_input("Tinggi Badan (cm):", min_value=50.0, max_value=220.0, value=140.0, step=0.5, key="tab2_tb")

    if st.button("HITUNG & SIMPAN STATUS GIZI (IMT/U)", key="btn_tab2"):
        if not nama_rem.strip():
            st.warning("⚠️ Mohon isi nama anak/remaja terlebih dahulu.")
        else:
            tb_m = tb_rem / 100
            imt_rem = bb_rem / (tb_m ** 2)
            
            try:
                df_l, df_p = load_ref_imtu()
                df_selected = df_l if jk_rem == "Laki-laki" else df_p
                
                row = df_selected[(df_selected['Tahun'] == tahun_lookup) & (df_selected['Bulan'] == bulan_lookup)]
                
                if row.empty:
                    st.warning(f"⚠️ Umur ({tahun_lookup} Thn {bulan_lookup} Bln) di luar jangkauan tabel referensi (5-18 Tahun).")
                else:
                    row_data = row.iloc[0]
                    
                    sd3neg = row_data['- 3 SD'] if '- 3 SD' in row_data else row_data['-3 SD']
                    sd2neg = row_data['- 2 SD'] if '- 2 SD' in row_data else row_data['-2 SD']
                    sd1neg = row_data['- 1 SD'] if '- 1 SD' in row_data else row_data['-1 SD']
                    median = row_data['Median'] if 'Median' in row_data else row_data['MEDIAN']
                    sd1pos = row_data['+1 SD'] if '+1 SD' in row_data else row_data['+ 1 SD']
                    sd2pos = row_data['+2 SD'] if '+2 SD' in row_data else row_data['+ 2 SD']
                    sd3pos = row_data['+3 SD'] if '+3 SD' in row_data else row_data['+ 3 SD']

                    z_imtu = hitung_zscore_multi(imt_rem, median, sd1neg, sd2neg, sd3neg, sd1pos, sd2pos, sd3pos)

                    if imt_rem < sd3neg:
                        kat_rem = "Gizi buruk (severely thinness)"
                    elif sd3neg <= imt_rem < sd2neg:
                        kat_rem = "Gizi kurang (thinness)"
                    elif sd2neg <= imt_rem <= sd1pos:
                        kat_rem = "Gizi baik (normal)"
                    elif sd1pos < imt_rem <= sd2pos:
                        kat_rem = "Gizi lebih (overweight)"
                    else:
                        kat_rem = "Obesitas (obese)"

                    st.divider()
                    st.subheader(f"Hasil Analisis: {nama_rem}")
                    st.info(f"Analisis berdasarkan Umur: {tahun_lookup} Tahun {bulan_lookup} Bulan (Standar Buku Antropometri Kemenkes)")

                    st.write(f"**Nilai IMT Pasien:** `{imt_rem:.2f} kg/m²`")
                    st.write(f"**Z-Score IMT/U:** `{z_imtu:.2f} SD`")
                    st.caption(f"Status: {kat_rem}")

                    # =========================================================
                    # 📈 TAMPILAN KURVA IMT/U (TAB 2)
                    # =========================================================
                    st.markdown("#### 📈 Grafis Kurva Pertumbuhan Pasien (IMT/U)")
                    df_chart_tab2 = df_selected.copy()
                    df_chart_tab2['Total_Bulan'] = df_chart_tab2['Tahun'] * 12 + df_chart_tab2['Bulan']
                    
                    fig_imtu = plot_kurva_zscore(
                        df_chart_tab2,
                        x_col='Total_Bulan',
                        x_val=total_bulan_rem,
                        y_val=imt_rem,
                        title_text="Kurva Indeks Massa Tubuh Menurut Umur (IMT/U)",
                        x_label="Umur (Bulan)",
                        y_label="IMT (kg/m²)"
                    )
                    st.plotly_chart(fig_imtu, use_container_width=True)

                    # PROSES SIMPAN KE GOOGLE SPREADSHEET (SHEET3)
                    with st.spinner("Sedang menyimpan data ke database Google Sheets (Sheet3)..."):
                        try:
                            client_sheet = koneksi_spreadsheet().spreadsheet
                            sheet3 = client_sheet.worksheet("Sheet3")

                            if len(sheet3.get_all_values()) == 0:
                                header = [
                                    "Waktu Input", "Nama Anak", "Jenis Kelamin", 
                                    "Tgl Lahir", "Tgl Periksa", "Umur (Tahun)", "Umur (Bulan)", 
                                    "BB (kg)", "TB (cm)", "IMT (kg/m²)", "Z-Score IMT/U (SD)", "Status Gizi"
                                ]
                                sheet3.append_row(header)

                            waktu_skrg = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            baris_baru_tab2 = [
                                waktu_skrg, nama_rem, jk_rem, str(tgl_lahir_rem), str(tgl_periksa_rem),
                                tahun_lookup, bulan_lookup, bb_rem, tb_rem, f"{imt_rem:.2f}",
                                f"{z_imtu:.2f}", kat_rem
                            ]

                            sheet3.append_row(baris_baru_tab2)
                            st.success("✅ Data pasien dan hasil skrining berhasil disimpan ke Sheet3!")

                        except Exception as sheet_err:
                            st.error(f"Gagal menyimpan ke Sheet3: {sheet_err}")

                    with st.expander("📖 Lihat Tabel Referensi Ambang Batas (Z-Score) Kemenkes"):
                        st.markdown("""
                        | Indeks | Kategori Status Gizi | Ambang Batas (Z-Score) |
                        | :--- | :--- | :--- |
                        | **Indeks Massa Tubuh menurut Umur (IMT/U) anak usia 5 - 18 tahun** | Gizi buruk (*severely thinness*) | < -3 SD |
                        | | Gizi kurang (*thinness*) | -3 SD sd < -2 SD |
                        | | Gizi baik (*normal*) | -2 SD sd +1 SD |
                        | | Gizi lebih (*overweight*) | +1 SD sd +2 SD |
                        | | Obesitas (*obese*) | > +2 SD |
                        """)

            except Exception as err_imtu:
                st.error(f"Gagal membaca file referensi Excel IMT/U: {err_imtu}")

# =========================================================================
# TAB 3: INDEKS MASSA TUBUH (DEWASA > 18 TAHUN)
# =========================================================================
with tab3:
    st.markdown("### ⚖️ Kalkulator Indeks Massa Tubuh (Dewasa > 18 Tahun)")
    
    col_dw1, col_dw2 = st.columns(2)
    with col_dw1:
        nama_dw = st.text_input("Nama Pasien:", key="tab3_nama")
        bb_dw = st.number_input("Berat Badan (kg):", min_value=20.0, max_value=250.0, value=60.0, step=0.1, key="tab3_bb")
        tb_dw = st.number_input("Tinggi Badan (cm):", min_value=100.0, max_value=250.0, value=160.0, step=0.5, key="tab3_tb")

    if st.button("HITUNG IMT DEWASA", key="btn_tab3"):
        tb_m_dw = tb_dw / 100
        imt_dw = bb_dw / (tb_m_dw ** 2)

        if imt_dw < 18.5:
            kat_dw, box_dw = "Berat Badan Kurang (Underweight)", st.warning
        elif 18.5 <= imt_dw <= 22.9:
            kat_dw, box_dw = "Berat Badan Normal", st.success
        elif 23.0 <= imt_dw <= 24.9:
            kat_dw, box_dw = "Kelebihan Berat Badan Tingkat Ringan (Overweight)", st.warning
        else:
            kat_dw, box_dw = "Obesitas", st.error

        st.markdown("#### 📊 Hasil Evaluasi IMT Dewasa")
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            st.metric("Nilai IMT Dewasa", f"{imt_dw:.2f} kg/m²")
        with col_d2:
            st.write("**Kategori IMT (Kemenkes):**")
            box_dw(kat_dw)
