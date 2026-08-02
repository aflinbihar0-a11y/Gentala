import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import plotly.express as px
import streamlit as st


# =========================================================================
# 1. FUNGSI AMBIL DATA REAL-TIME DARI GOOGLE SHEETS
# =========================================================================
@st.cache_data(ttl=60)
def ambil_data_database():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]

    # Mengambil kredensial GCP dari Streamlit Secrets
    creds_dict = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(creds)

    # Buka file induk database
    file_induk = client.open("GrowTrack Database")

    # Tarik data dari masing-masing Worksheet
    raw_gizi = file_induk.worksheet("Sheet2").get_all_records()
    raw_mental = file_induk.worksheet("Sheet_Mental_Health").get_all_records()

    return pd.DataFrame(raw_gizi), pd.DataFrame(raw_mental)


# =========================================================================
# 2. ANTARMUKA UTAMA DASHBOARD
# =========================================================================
st.set_page_config(
    page_title="Dashboard Surveilans", page_icon="📊", layout="wide"
)

st.title("📊 Dashboard Kunjungan")
st.caption("Data Terintegrasi Aplikasi GENTALA — Puskesmas Batu Tangga, HST")

try:
    # Memuat data dari fungsi gspread
    df_gizi, df_mental = ambil_data_database()

    # Membuat Tab Navigasi Utama di Dashboard
    tab_gizi, tab_mental = st.tabs(
        ["🧸 Surveilans Gizi Anak", "🧠 Surveilans Kesehatan Jiwa"]
    )

    # =========================================================================
    # --- TAB 1: DASHBOARD GIZI & TUMBUH KEMBANG ANAK (FILTER BULAN & DESA)
    # =========================================================================
    with tab_gizi:
        st.subheader("Analisis Status Gizi & Tren Kunjungan Anak")

        # ---------------------------------------------------------------------
        # FITUR FILTER MULTI-INDIKATOR (BULAN & DESA)
        # ---------------------------------------------------------------------
        # Penanganan Filter Bulan
        kolom_waktu = "Tanggal Periksa"
        if kolom_waktu in df_gizi.columns and not df_gizi.empty:
            df_gizi["Datetime"] = pd.to_datetime(
                df_gizi[kolom_waktu], errors="coerce"
            )
            df_gizi["Bulan_Filter"] = df_gizi["Datetime"].dt.strftime("%Y-%m")
            daftar_bulan = ["Semua Bulan"] + sorted(
                df_gizi["Bulan_Filter"].dropna().unique().tolist(), reverse=True
            )
        else:
            daftar_bulan = ["Semua Bulan"]
            df_gizi["Bulan_Filter"] = "Semua Bulan"

        # Penanganan Filter Desa
        # (Ubah 'Desa' jika di Google Sheets Dokter menggunakan nama lain, misal: 'Alamat' / 'Posyandu')
        kolom_desa = "Desa"
        if kolom_desa in df_gizi.columns and not df_gizi.empty:
            daftar_desa = ["Semua Desa"] + sorted(
                df_gizi[kolom_desa].astype(str).unique().tolist()
            )
        else:
            daftar_desa = ["Semua Desa"]

        # Menampilkan Filter Berdampingan (2 Kolom)
        col_filter1, col_filter2 = st.columns(2)

        with col_filter1:
            bulan_terpilih = st.selectbox(
                "🗓️ Pilih Bulan Evaluasi:", daftar_bulan
            )

        with col_filter2:
            desa_terpilih = st.selectbox("🏡 Pilih Wilayah / Desa:", daftar_desa)

        # Proses Penyaringan Data Frame
        df_gizi_visual = df_gizi.copy()

        if bulan_terpilih != "Semua Bulan":
            df_gizi_visual = df_gizi_visual[
                df_gizi_visual["Bulan_Filter"] == bulan_terpilih
            ]

        if desa_terpilih != "Semua Desa" and kolom_desa in df_gizi_visual.columns:
            df_gizi_visual = df_gizi_visual[
                df_gizi_visual[kolom_desa].astype(str) == desa_terpilih
            ]

        # Tampilkan Notifikasi Filter Aktif
        st.info(
            f"📌 Menampilkan data untuk periode: **{bulan_terpilih}** | Wilayah: **{desa_terpilih}** (Total: {len(df_gizi_visual)} Anak)"
        )

        st.markdown("---")

        # Layout Utama: 2 Kolom (Kiri untuk Status Gizi, Kanan untuk Tren Kunjungan)
        kolom_kiri, kolom_kanan = st.columns([1.2, 1])

        # ---------------------------------------------------------------------
        # KOLOM KIRI: STATUS GIZI (SESUAI HASIL FILTER BULAN & DESA)
        # ---------------------------------------------------------------------
        with kolom_kiri:
            subtab_tbu, subtab_bbu, subtab_bbtb = st.tabs(
                [
                    "📏 TB/U (Stunting)",
                    "⚖️ BB/U (Underweight)",
                    "🥗 BB/TB (Wasting)",
                ]
            )

            # --- A. INDIKATOR TB/U ---
            with subtab_tbu:
                st.markdown("##### 🍩 Proporsi Status TB/U")
                kolom_tbu = "Status TB/U"

                if (
                    kolom_tbu in df_gizi_visual.columns
                    and not df_gizi_visual.empty
                ):
                    hitung_tbu = (
                        df_gizi_visual[kolom_tbu].value_counts().reset_index()
                    )
                    hitung_tbu.columns = ["Status Gizi", "Jumlah Anak"]

                    fig_tbu = px.pie(
                        hitung_tbu,
                        values="Jumlah Anak",
                        names="Status Gizi",
                        hole=0.45,
                        color="Status Gizi",
                        color_discrete_map={
                            "Sangat Pendek": "#DC2626",
                            "Sangat Pendek (Severely Stunted)": "#DC2626",
                            "Pendek": "#60A5FA",
                            "Pendek (Stunted)": "#60A5FA",
                            "Normal": "#2563EB",
                            "Tinggi": "#10B981",
                        },
                    )
                    fig_tbu.update_traces(
                        textinfo="percent+value", hoverinfo="label+value"
                    )
                    fig_tbu.update_layout(
                        showlegend=True, margin=dict(t=10, b=10, l=10, r=10)
                    )
                    st.plotly_chart(fig_tbu, use_container_width=True)
                else:
                    st.warning("Data kosong untuk kombinasi filter ini.")

            # --- B. INDIKATOR BB/U ---
            with subtab_bbu:
                st.markdown("##### 🍩 Proporsi Status BB/U")
                kolom_bbu = "Status BB/U"

                if (
                    kolom_bbu in df_gizi_visual.columns
                    and not df_gizi_visual.empty
                ):
                    hitung_bbu = (
                        df_gizi_visual[kolom_bbu].value_counts().reset_index()
                    )
                    hitung_bbu.columns = ["Status Gizi", "Jumlah Anak"]

                    fig_bbu = px.pie(
                        hitung_bbu,
                        values="Jumlah Anak",
                        names="Status Gizi",
                        hole=0.45,
                        color="Status Gizi",
                        color_discrete_map={
                            "Sangat Kurang": "#DC2626",
                            "Sangat Kurang (Severely Underweight)": "#DC2626",
                            "Kurang": "#F59E0B",
                            "Kurang (Underweight)": "#F59E0B",
                            "Normal": "#2563EB",
                            "Risiko BB Lebih": "#10B981",
                        },
                    )
                    fig_bbu.update_traces(
                        textinfo="percent+value", hoverinfo="label+value"
                    )
                    fig_bbu.update_layout(
                        showlegend=True, margin=dict(t=10, b=10, l=10, r=10)
                    )
                    st.plotly_chart(fig_bbu, use_container_width=True)
                else:
                    st.warning("Data kosong untuk kombinasi filter ini.")

            # --- C. INDIKATOR BB/TB ---
            with subtab_bbtb:
                st.markdown("##### 🍩 Proporsi Status BB/TB")
                kolom_bbtb = "Status BB/TB"

                if (
                    kolom_bbtb in df_gizi_visual.columns
                    and not df_gizi_visual.empty
                ):
                    hitung_bbtb = (
                        df_gizi_visual[kolom_bbtb].value_counts().reset_index()
                    )
                    hitung_bbtb.columns = ["Status Gizi", "Jumlah Anak"]

                    fig_bbtb = px.pie(
                        hitung_bbtb,
                        values="Jumlah Anak",
                        names="Status Gizi",
                        hole=0.45,
                        color="Status Gizi",
                        color_discrete_map={
                            "Gizi Buruk": "#7F1D1D",
                            "Gizi Buruk (Severely Wasted)": "#7F1D1D",
                            "Gizi Kurang": "#DC2626",
                            "Gizi Kurang (Wasted)": "#DC2626",
                            "Gizi Baik": "#2563EB",
                            "Gizi Baik (Normal)": "#2563EB",
                            "Berisiko Gizi Lebih": "#FBBF24",
                            "Gizi Lebih": "#F59E0B",
                            "Obesitas": "#9333EA",
                        },
                    )
                    fig_bbtb.update_traces(
                        textinfo="percent+value", hoverinfo="label+value"
                    )
                    fig_bbtb.update_layout(
                        showlegend=True, margin=dict(t=10, b=10, l=10, r=10)
                    )
                    st.plotly_chart(fig_bbtb, use_container_width=True)
                else:
                    st.warning("Data kosong untuk kombinasi filter ini.")

        # ---------------------------------------------------------------------
        # KOLOM KANAN: TREN KUNJUNGAN (SESUAI DESA YANG DIPILIH)
        # ---------------------------------------------------------------------
        with kolom_kanan:
            st.markdown("#### 📅 Tren Kunjungan Pemeriksaan Gizi")

            # Jika desa dipilih, grafik tren hanya menampilkan kunjungan desa tersebut dari bulan ke bulan
            df_tren_desa = df_gizi.copy()
            if (
                desa_terpilih != "Semua Desa"
                and kolom_desa in df_tren_desa.columns
            ):
                df_tren_desa = df_tren_desa[
                    df_tren_desa[kolom_desa].astype(str) == desa_terpilih
                ]

            if kolom_waktu in df_tren_desa.columns and not df_tren_desa.empty:
                tren_bulanan = (
                    df_tren_desa["Bulan_Filter"]
                    .value_counts()
                    .sort_index()
                    .reset_index()
                )
                tren_bulanan.columns = ["Bulan", "Jumlah Pemeriksaan"]
                tren_bulanan = tren_bulanan[
                    tren_bulanan["Bulan"] != "Semua Bulan"
                ]

                st.bar_chart(tren_bulanan.set_index("Bulan"))
            else:
                st.info("Belum ada data kunjungan untuk wilayah ini.")

    # =========================================================================
    # --- TAB 2: DASHBOARD KESEHATAN JIWA ---
    # =========================================================================
    with tab_mental:
        st.subheader("Analisis Beban Skrining Jiwa & Tindakan Klinis")

        st.markdown("#### 📊 Distribusi Penggunaan Kuesioner Skrining")
        kolom_kuesioner = "Jenis Kuesioner"

        if kolom_kuesioner in df_mental.columns and not df_mental.empty:
            hitung_kuesioner = (
                df_mental[kolom_kuesioner].value_counts().reset_index()
            )
            hitung_kuesioner.columns = ["Jenis Kuesioner", "Jumlah"]
            st.bar_chart(hitung_kuesioner.set_index("Jenis Kuesioner"))
        else:
            st.info("Belum ada data skrining jiwa masuk.")

        st.divider()

        # Fitur Kegawatan Klinis: Critical Action List
        st.markdown(
            "#### 🚨 Daftar Prioritas Rujukan Jiwa (Critical Action List)"
        )
        st.caption(
            "Menyaring otomatis pasien dengan indikasi risiko tinggi/ide cedera diri untuk intervensi segera."
        )

        kolom_rekomendasi = "Rekomendasi Klinis"
        kolom_hasil_universal = "Interpretasi Hasil"
        kolom_interpretasi_f = "Status Interpretasi"
        kolom_risiko = "Faktor Risiko"

        if kolom_rekomendasi in df_mental.columns:
            df_kritis = df_mental[
                (
                    df_mental[kolom_rekomendasi].str.contains(
                        "mengakhiri hidup|psikiatrik|kritis|Rujuk|cedera diri",
                        case=False,
                        na=False,
                    )
                )
                | (
                    df_mental.get(
                        kolom_hasil_universal, pd.Series(dtype=str)
                    ).str.contains(
                        "Kritis|Tinggi|Abnormal|mengarah kuat|Risiko tinggi|Indikasi Masalah",
                        case=False,
                        na=False,
                    )
                )
                | (
                    df_mental.get(
                        kolom_interpretasi_f, pd.Series(dtype=str)
                    ).str.contains(
                        "Kritis|Tinggi|Abnormal|Risiko Tinggi",
                        case=False,
                        na=False,
                    )
                )
                | (
                    df_mental.get(
                        kolom_risiko, pd.Series(dtype=str)
                    ).str.contains("Ada|Ya", case=False, na=False)
                )
            ]

            if not df_kritis.empty:
                st.error(
                    f"⚠️ PERHATIAN DARURAT! Ditemukan {len(df_kritis)} kasus kesehatan jiwa yang memerlukan tatalaksana/intervensi segera."
                )
                kolom_tampil = [
                    "Waktu Input",
                    "Nama Pasien",
                    "Jenis Kuesioner",
                    kolom_hasil_universal,
                    "Rekomendasi Klinis",
                    "Pemeriksa",
                ]
                kolom_tampil = [
                    c for c in kolom_tampil if c in df_kritis.columns
                ]
                st.dataframe(df_kritis[kolom_tampil], use_container_width=True)
            else:
                st.success(
                    "✅ Seluruh data terpantau aman. Tidak ada indikasi kegawatan mental/ide cedera diri saat ini."
                )
        else:
            st.info("Sistem siap. Menunggu entri data kuesioner kesehatan jiwa.")

except Exception as e:
    st.error(f"Gagal memuat visualisasi dashboard. Detail teknis: {e}")
