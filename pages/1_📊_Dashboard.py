# =========================================================================
    # --- TAB 1: DASHBOARD GIZI & TUMBUH KEMBANG ANAK (DENGAN FILTER BULAN)
    # =========================================================================
    with tab_gizi:
        st.subheader("Analisis Status Gizi & Tren Kunjungan Anak")

        # ---------------------------------------------------------------------
        # FITUR FILTER DATA PER BULAN
        # ---------------------------------------------------------------------
        kolom_waktu = "Tanggal Periksa"
        if kolom_waktu in df_gizi.columns and not df_gizi.empty:
            # Buat kolom baru khusus untuk format Tahun-Bulan
            df_gizi["Datetime"] = pd.to_datetime(df_gizi[kolom_waktu], errors="coerce")
            df_gizi["Bulan_Filter"] = df_gizi["Datetime"].dt.strftime("%Y-%m")
            
            # Ambil daftar bulan unik yang ada di data (diurutkan dari terbaru)
            daftar_bulan = ["Semua Data"] + sorted(df_gizi["Bulan_Filter"].dropna().unique().tolist(), reverse=True)
        else:
            daftar_bulan = ["Semua Data"]
            df_gizi["Bulan_Filter"] = "Semua Data"

        # Tampilkan pilihan selectbox ke pengguna
        bulan_terpilih = st.selectbox("🗓️ Pilih Bulan Evaluasi:", daftar_bulan)

        # Lakukan penyaringan (filtering) dataframe sesuai pilihan
        if bulan_terpilih != "Semua Data":
            df_gizi_visual = df_gizi[df_gizi["Bulan_Filter"] == bulan_terpilih]
            st.info(f"Menampilkan proporsi status gizi untuk periode: **{bulan_terpilih}**")
        else:
            df_gizi_visual = df_gizi.copy()

        st.markdown("---")

        # Layout Utama: 2 Kolom (Kiri untuk Status Gizi, Kanan untuk Tren Kunjungan)
        kolom_kiri, kolom_kanan = st.columns([1.2, 1])

        # ---------------------------------------------------------------------
        # KOLOM KIRI: STATUS GIZI (MENGGUNAKAN DATA YANG SUDAH DIFILTER)
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

                if kolom_tbu in df_gizi_visual.columns and not df_gizi_visual.empty:
                    hitung_tbu = df_gizi_visual[kolom_tbu].value_counts().reset_index()
                    hitung_tbu.columns = ["Status Gizi", "Jumlah Anak"]

                    fig_tbu = px.pie(
                        hitung_tbu,
                        values="Jumlah Anak",
                        names="Status Gizi",
                        hole=0.45,
                        color="Status Gizi",
                        color_discrete_map={
                            "Sangat Pendek": "#DC2626", "Sangat Pendek (Severely Stunted)": "#DC2626",
                            "Pendek": "#60A5FA", "Pendek (Stunted)": "#60A5FA",
                            "Normal": "#2563EB",
                            "Tinggi": "#10B981",
                        },
                    )
                    fig_tbu.update_traces(textinfo="percent+value", hoverinfo="label+value")
                    fig_tbu.update_layout(showlegend=True, margin=dict(t=10, b=10, l=10, r=10))
                    st.plotly_chart(fig_tbu, use_container_width=True)
                else:
                    st.warning("Data kosong untuk bulan ini.")

            # --- B. INDIKATOR BB/U ---
            with subtab_bbu:
                st.markdown("##### 🍩 Proporsi Status BB/U")
                kolom_bbu = "Status BB/U"

                if kolom_bbu in df_gizi_visual.columns and not df_gizi_visual.empty:
                    hitung_bbu = df_gizi_visual[kolom_bbu].value_counts().reset_index()
                    hitung_bbu.columns = ["Status Gizi", "Jumlah Anak"]

                    fig_bbu = px.pie(
                        hitung_bbu,
                        values="Jumlah Anak",
                        names="Status Gizi",
                        hole=0.45,
                        color="Status Gizi",
                        color_discrete_map={
                            "Sangat Kurang": "#DC2626", "Sangat Kurang (Severely Underweight)": "#DC2626",
                            "Kurang": "#F59E0B", "Kurang (Underweight)": "#F59E0B",
                            "Normal": "#2563EB",
                            "Risiko BB Lebih": "#10B981",
                        },
                    )
                    fig_bbu.update_traces(textinfo="percent+value", hoverinfo="label+value")
                    fig_bbu.update_layout(showlegend=True, margin=dict(t=10, b=10, l=10, r=10))
                    st.plotly_chart(fig_bbu, use_container_width=True)
                else:
                    st.warning("Data kosong untuk bulan ini.")

            # --- C. INDIKATOR BB/TB ---
            with subtab_bbtb:
                st.markdown("##### 🍩 Proporsi Status BB/TB")
                kolom_bbtb = "Status BB/TB"

                if kolom_bbtb in df_gizi_visual.columns and not df_gizi_visual.empty:
                    hitung_bbtb = df_gizi_visual[kolom_bbtb].value_counts().reset_index()
                    hitung_bbtb.columns = ["Status Gizi", "Jumlah Anak"]

                    fig_bbtb = px.pie(
                        hitung_bbtb,
                        values="Jumlah Anak",
                        names="Status Gizi",
                        hole=0.45,
                        color="Status Gizi",
                        color_discrete_map={
                            "Gizi Buruk": "#7F1D1D", "Gizi Buruk (Severely Wasted)": "#7F1D1D",
                            "Gizi Kurang": "#DC2626", "Gizi Kurang (Wasted)": "#DC2626",
                            "Gizi Baik": "#2563EB", "Gizi Baik (Normal)": "#2563EB",
                            "Berisiko Gizi Lebih": "#FBBF24",
                            "Gizi Lebih": "#F59E0B",
                            "Obesitas": "#9333EA",
                        },
                    )
                    fig_bbtb.update_traces(textinfo="percent+value", hoverinfo="label+value")
                    fig_bbtb.update_layout(showlegend=True, margin=dict(t=10, b=10, l=10, r=10))
                    st.plotly_chart(fig_bbtb, use_container_width=True)
                else:
                    st.warning("Data kosong untuk bulan ini.")

        # ---------------------------------------------------------------------
        # KOLOM KANAN: TREN KUNJUNGAN (TETAP MENAMPILKAN SEMUA DATA)
        # ---------------------------------------------------------------------
        with kolom_kanan:
            st.markdown("#### 📅 Tren Kunjungan Pemeriksaan Gizi")
            
            # Tren kunjungan kita buat tetap membaca df_gizi (tanpa filter) 
            # agar grafik batang bulanannya tidak hilang.
            if kolom_waktu in df_gizi.columns and not df_gizi.empty:
                tren_bulanan = df_gizi["Bulan_Filter"].value_counts().sort_index().reset_index()
                tren_bulanan.columns = ["Bulan", "Jumlah Pemeriksaan"]
                
                # Hapus baris 'Semua Data' jika ada
                tren_bulanan = tren_bulanan[tren_bulanan["Bulan"] != "Semua Data"]

                st.bar_chart(tren_bulanan.set_index("Bulan"))
            else:
                st.info("Belum ada data atau kolom 'Tanggal Periksa' tidak ditemukan.")
