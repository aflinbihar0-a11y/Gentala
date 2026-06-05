import streamlit as st
import streamlit as st

def tambahkan_tombol_cetak_pdf():
    # 1. CSS Media Print (Tetap di st.markdown agar memengaruhi seluruh halaman utama)
    st.markdown(
        """
        <style>
        @media print {
            /* Sembunyikan sidebar, header, footer, dan area tombol iframe saat cetak */
            [data-testid="stSidebar"], header, footer, .element-container:has(iframe) {
                display: none !important;
            }
            .main .block-container {
                padding-top: 1rem !important;
                padding-bottom: 1rem !important;
            }
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    # 2. Bungkus tombol HTML ke dalam iframe Streamlit menggunakan st.components.v1.html
    # Gunakan window.parent.print() agar yang dicetak adalah halaman utama, bukan isi iframe saja.
    tombol_html = """
    <style>
        .btn-print {
            width: 100%;
            background-color: #1E3A8A; /* Warna biru gelap sesuai tema aplikasi Anda */
            color: white;
            padding: 12px 24px;
            font-size: 16px;
            font-weight: bold;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        }
        .btn-print:hover {
            background-color: #152A66; /* Efek sedikit menggelap saat cursor di atas tombol */
        }
    </style>
    <button class="btn-print" onclick="window.parent.print()">
        🖨️ Cetak Hasil Skrining / Simpan ke PDF
    </button>
    """
    
    # Render menggunakan komponen HTML resmi Streamlit
    st.components.v1.html(tombol_html, height=55)
from datetime import datetime

# =========================================================================
# 1. IDENTITAS & FILTER UTAMA (Selalu Muncul di Paling Atas)
# =========================================================================
st.title("GENTALA-SKRINING KESEHATAN MENTAL")
st.caption("Aplikasi Deteksi Dini Kesehatan Mental Anak, Dewasa, & Ibu Pasca Melahirkan")

# Pilihan kategori utama yang mencakup seluruh sasaran skrining
kategori = st.selectbox(
    "Pilih Kelompok Sasaran Skrining:",
    ["Pasca Persalinan [EPDS]", "Anak & Remaja [SDQ]", "Orang Dewasa [SRQ-20]"],
    key="pilih_kategori_utama"
)

st.markdown("### 📋 Data Identitas")
col_id1, col_id2 = st.columns(2)

with col_id1:
    nama = st.text_input("Nama Lengkap Pasien:", key="id_nama")
    nik = st.text_input("Nomor NIK / No. RM:", key="id_nik")

with col_id2:
    tgl_lahir = st.date_input("Tanggal Lahir:", value=datetime(2000, 1, 1), key="id_tgl")
    pemeriksa = st.text_input("Nama Tenaga Kesehatan / Kader:", key="id_nakes")

st.markdown("---")


# =========================================================================
# KATEGORI: IBU HAMIL & MENYUSUI (EPDS)
# =========================================================================
if "EPDS" in kategori:
    st.subheader("🤰 Edinburgh Postnatal Depression Scale (EPDS)")
    st.info("Silakan memilih jawaban yang paling mirip dengan perasaan Anda selama 7 hari terakhir, tidak hanya perasaan Anda hari ini.")
    
    # --- FORM KUESIONER DENGAN OPSI SPESIFIK KEMENKES ---
    epds_1 = st.radio("1. Saya dapat tertawa dan melihat segi kelucuan hal-hal tertentu:", ["a. Seperti biasanya", "b. Sekarang tidak terlalu sering", "c. Sekarang agak jarang", "d. Tidak sama sekali"], key="epds_1")
    epds_2 = st.radio("2. Saya menanti-nanti untuk melakukan sesuatu dengan penuh harapan:", ["a. Sebanyak sebelumnya", "b. Agak sedikit kurang dibandingkan dengan sebelumnya", "c. Kurang dibandingkan dengan sebelumnya", "d. Tidak pernah sama sekali"], key="epds_2")
    epds_3 = st.radio("3. *Saya menyalahkan diri jika ada sesuatu yang tidak berjalan dengan baik:", ["a. Ya, hampir selalu", "b. Ya, kadang-kadang", "c. Tidak terlalu sering", "d. Tidak, tidak pernah"], key="epds_3")
    epds_4 = st.radio("4. Saya merasa cemas atau merasa khawatir tanpa alasan:", ["a. Tidak pernah sama sekali", "b. Hampir tidak pernah", "c. Ya, kadang-kadang", "d. Ya, sering sekali"], key="epds_4")
    epds_5 = st.radio("5. *Saya merasa takut atau panik tanpa alasan:", ["a. Ya, sering sekali", "b. Ya, kadang-kadang", "c. Tidak terlalu sering", "d. Tidak pernah sama sekali"], key="epds_5")
    epds_6 = st.radio("6. *Banyak hal menjadi beban untuk saya:", ["a. Ya, seringkali saya sama sekali tidak dapat mengatasinya", "b. Ya, kadang saya tidak dapat mengatasi seperti biasanya", "c. Tidak, biasanya saya dapat mengatasinya dengan baik", "d. Tidak, saya dapat mengatasinya dengan baik seperti biasanya"], key="epds_6")
    epds_7 = st.radio("7. *Saya merasa begitu sedih sampai sulit tidur:", ["a. Ya, hampir selalu", "b. Ya, kadang-kadang", "c. Tidak, tidak sering", "d. Tidak, tidak pernah"], key="epds_7")
    epds_8 = st.radio("8. *Saya merasa sedih atau susah:", ["a. Ya, hampir selalu", "b. Ya, sering", "c. Jarang", "d. Tidak pernah"], key="epds_8")
    epds_9 = st.radio("9. *Saya merasa sangat sedih sehingga saya menangis:", ["a. Ya, hampir selalu", "b. Ya, sering", "c. Hanya sekali-kali", "d. Tidak pernah"], key="epds_9")
    epds_10 = st.radio("10. *Pikiran untuk menyakiti diri saya sendiri sering muncul:", ["a. Ya, agak sering", "b. Kadang-kadang", "c. Hampir tidak pernah", "d. Tidak pernah"], key="epds_10")

    # --- TOMBOL HITUNG DAN PEMROSESAN SKOR ---
    if st.button("Hitung Skor EPDS", key="btn_epds"):
        
        # Kamus Konversi Nilai Berdasarkan Pilihan Huruf (a, b, c, d)
        skala_normal = {"a": 0, "b": 1, "c": 2, "d": 3}
        skala_terbalik = {"a": 3, "b": 2, "c": 1, "d": 0}
        
        # Ekstraksi nilai skor menggunakan huruf pertama string pilihan jawaban
        skor_1 = skala_normal[epds_1[0]]
        skor_2 = skala_normal[epds_2[0]]
        skor_3 = skala_terbalik[epds_3[0]]
        skor_4 = skala_normal[epds_4[0]]
        skor_5 = skala_terbalik[epds_5[0]]
        skor_6 = skala_terbalik[epds_6[0]]
        skor_7 = skala_terbalik[epds_7[0]]
        skor_8 = skala_terbalik[epds_8[0]]
        skor_9 = skala_terbalik[epds_9[0]]
        skor_10 = skala_terbalik[epds_10[0]]
        
        skor_total_epds = skor_1 + skor_2 + skor_3 + skor_4 + skor_5 + skor_6 + skor_7 + skor_8 + skor_9 + skor_10
        
        # --- LOGIKA INTERPRETASI 3 TIER SESUAI SLIDE (image_d43ddb.jpg) ---
        if skor_total_epds <= 9:
            status_epds = "Indikasi risiko rendah depresi"
            pesan_klinis = "Kondisi emosional ibu cenderung stabil. Tetap berikan dukungan psikososial dasar."
            warna_status = "success"
        elif 10 <= skor_total_epds <= 12:
            status_epds = "Risiko sedang; perlu pemantauan lebih lanjut"
            pesan_klinis = "Ibu menunjukkan gejala distres emosional sedang. Lakukan evaluasi ulang/pendampingan berkala oleh nakes."
            warna_status = "warning"
        else: # Skor >= 13
            status_epds = "Risiko tinggi depresi; disarankan konsultasi dengan profesional kesehatan mental"
            pesan_klinis = "Gejala mengarah kuat pada depresi perinatal. Segera rujuk atau konsultasikan dengan profesional kesehatan jiwa."
            warna_status = "error"
        
        # --- PRESENTASI ANTARMUKA MEDIS ---
        st.markdown("### 📊 Hasil Skoring Klasifikasi EPDS")
        st.metric(label="Skor Total Capaian", value=f"{skor_total_epds} / 30")
        
        # Visualisasi status dinamis menggunakan komponen bawaan streamlit
        if warna_status == "success":
            st.success(f"**Status:** {status_epds}")
        elif warna_status == "warning":
            st.warning(f"**Status:** {status_epds}")
        else:
            st.error(f"**Status:** {status_epds}")
            
        st.info(f"💡 **Rekomendasi Tindakan:** {pesan_klinis}")
        st.caption("ℹ️ *Catatan Penting: Skor tinggi tidak berarti diagnosis pasti depresi, tetapi menunjukkan perlunya evaluasi lebih lanjut.*")
        
        # Peringatan Keamanan Kritis Tambahan (Proteksi Pertanyaan Nomor 10)
        if skor_10 > 0:
            st.markdown("---")
            st.error("🚨 **ALARM UTAMA KLINIS (IDE CEDERA DIRI):**")
            st.markdown("Ibu memilih opsi yang mengindikasikan adanya pikiran untuk menyakiti diri sendiri pada nomor 10. **Tatalaksana pendampingan psikologis atau rujukan darurat wajib berjalan segera**, tanpa harus menunggu akumulasi skor total!")

        # --- ARSIP DATABASE CLOUD ---
        if 'sheet' in globals() or 'sheet' in locals():
            try:
                sheet.append_row([
                    str(datetime.now().strftime('%Y-%m-%d %H:%M')), 
                    nama, nik, str(tgl_lahir), 
                    f"EPDS - Skor: {skor_total_epds} ({status_epds})", 
                    skor_total_epds, status_epds, pemeriksa
                ])
                if warna_status == "success":
                    st.balloons()
            except:
                pass

        # 🖨️ MENAMPILKAN TOMBOL CETAK PDF UNTUK EPDS
        st.markdown("---")
        tambahkan_tombol_cetak_pdf()


# =========================================================================
# KATEGORI: ANAK & REMAJA (SDQ)
# =========================================================================
if "SDQ" in kategori:
    st.subheader("🧸 Kuesioner SDQ (Strengths and Difficulties Questionnaire)")
    
    tipe_sdq = st.selectbox(
        "Pilih Versi Instrumen SDQ:",
        ["SDQ Anak (Usia 4-10 Tahun / Parent-Report)", "SDQ Remaja (Usia 11-17 Tahun / Self-Report)"],
        key="pilih_versi_sdq"
    )
    
    opsi_sdq = ["Tidak Benar", "Agak Benar", "Selalu Benar"]
    
    if "Remaja" in tipe_sdq:
        st.info("Bahasanya telah disesuaikan menggunakan sudut pandang remaja (Self-Report).")
        q1 = st.radio("1. Aku berusaha bersikap baik kepada orang lain. Aku peduli dengan perasaan mereka (Pr1):", opsi_sdq, key="sdq_r1")
        q2 = st.radio("2. Aku gelisah, aku tidak dapat duduk diam untuk waktu lama (H1):", opsi_sdq, key="sdq_r2")
        q3 = st.radio("3. Aku sering mengeluh sakit kepala, sakit perut atau sakit-sakit lainnya (E1):", opsi_sdq, key="sdq_r3")
        q4 = st.radio("4. Kalau aku mempunyai mainan, makanan, atau pensil, aku bersedia berbagi dengan orang lain (Pr2):", opsi_sdq, key="sdq_r4")
        q5 = st.radio("5. Aku menjadi sangat marah dan sering tidak bisa mengendalikan kemarahanku (C1):", opsi_sdq, key="sdq_r5")
        q6 = st.radio("6. Aku cenderung menyendiri. Aku lebih suka bermain atau menghabiskan waktu seorang diri (P1):", opsi_sdq, key="sdq_r6")
        q7 = st.radio("7. Aku umumnya bertingkah laku baik dan biasanya melakukan apa yang diminta oleh orang dewasa (C2*):", opsi_sdq, key="sdq_r7")
        q8 = st.radio("8. Sering kali aku merasa khawatir terhadap banyak hal (E2):", opsi_sdq, key="sdq_r8")
        q9 = st.radio("9. Aku suka menolong jika ada seseorang yang terluka, kecewa, atau merasa sedih (Pr3):", opsi_sdq, key="sdq_r9")
        q10 = st.radio("10. Aku terus-menerus bergerak dengan resah atau menggeliat-geliat (H2):", opsi_sdq, key="sdq_r10")
        q11 = st.radio("11. Aku mempunyai satu atau lebih teman dekat yang sangat baik (P2*):", opsi_sdq, key="sdq_r11")
        q12 = st.radio("12. Aku sering bertengkar dengan anak-anak lain atau mengintimidasi mereka (C3):", opsi_sdq, key="sdq_r12")
        q13 = st.radio("13. Aku sering merasa tidak bahagia, sedih, bahkan sampai menangis (E3):", opsi_sdq, key="sdq_r13")
        q14 = st.radio("14. Pada umumnya, teman-teman sebayaku menyukai diriku (P3*):", opsi_sdq, key="sdq_r14")
        q15 = st.radio("15. Perhatianku mudah teralih dan aku sulit untuk berkonsentrasi (H3):", opsi_sdq, key="sdq_r15")
        q16 = st.radio("16. Aku merasa gugup atau sulit berpisah dengan orang tua dalam situasi baru; aku mudah kehilangan rasa percaya diri (E4):", opsi_sdq, key="sdq_r16")
        q17 = st.radio("17. Aku bersikap manis dan ramah terhadap anak-anak yang usianya lebih muda dariku (Pr4):", opsi_sdq, key="sdq_r17")
        q18 = st.radio("18. Aku sering dituduh berbohong atau berbuat curang (C4):", opsi_sdq, key="sdq_r18")
        q19 = st.radio("19. Aku sering diganggu, dipermainkan, diintimidasi, atau diancam oleh anak-anak lain (P4):", opsi_sdq, key="sdq_r19")
        q20 = st.radio("20. Aku sering menawarkan diri untuk membantu orang lain (orang tua, guru, atau teman-teman) (Pr5):", opsi_sdq, key="sdq_r20")
        q21 = st.radio("21. Sebelum melakukan sesuatu, aku biasanya berpikir dahulu tentang akibatnya (H4*):", opsi_sdq, key="sdq_r21")
        q22 = st.radio("22. Aku mengambil barang yang bukan milikku dari rumah, sekolah, atau tempat lain (C5):", opsi_sdq, key="sdq_r22")
        q23 = st.radio("23. Aku merasa lebih mudah berteman dengan orang dewasa daripada dengan anak-anak sebayaku (P5):", opsi_sdq, key="sdq_r23")
        q24 = st.radio("24. Banyak hal yang aku takuti, aku mudah menjadi takut (E5):", opsi_sdq, key="sdq_r24")
        q25 = st.radio("25. Aku memiliki perhatian yang baik terhadap tugas-tugas dan mampu menyelesaikannya hingga selesai (H5*):", opsi_sdq, key="sdq_r25")

    else:
        st.info("Bahasanya menggunakan sudut pandang orang tua/pengasuh (Parent-Report).")
        q1 = st.radio("1. Dapat memperdulikan perasaan orang lain (Pr1):", opsi_sdq, key="sdq_a1")
        q2 = st.radio("2. Gelisah, anak tidak dapat diam untuk waktu lama (H1):", opsi_sdq, key="sdq_a2")
        q3 = st.radio("3. Sering mengeluh sakit kepala, sakit perut atau sakit-sakit lainnya (E1):", opsi_sdq, key="sdq_a3")
        q4 = st.radio("4. Kalau anak mempunyai mainan, kesenangan atau pinsil, anak bersedia berbagi dengan anak-anak lain (Pr2):", opsi_sdq, key="sdq_a4")
        q5 = st.radio("5. Anak sering sulit mengendalikan kemarahannya (C1):", opsi_sdq, key="sdq_a5")
        q6 = st.radio("6. Cenderung menyendiri, lebih suka bermain dengan seorang diri (P1):", opsi_sdq, key="sdq_a6")
        q7 = st.radio("7. Umumnya bertingkah laku baik, biasanya melakukan apa yang disuruh oleh orang dewasa (C2*):", opsi_sdq, key="sdq_a7")
        q8 = st.radio("8. Banyak kekhawatiran atau sering tampak khawatir (E2):", opsi_sdq, key="sdq_a8")
        q9 = st.radio("9. Suka menolong jika seseorang terluka, kecewa atau merasa sakit (Pr3):", opsi_sdq, key="sdq_a9")
        q10 = st.radio("10. Terus menerus bergerak dengan resah atau menggeliat-geliat (H2):", opsi_sdq, key="sdq_a10")
        q11 = st.radio("11. Mempunyai satu atau lebih teman baik (P2*):", opsi_sdq, key="sdq_a11")
        q12 = st.radio("12. Sering berkelahi dengan anak-anak lain atau mengintimidasi mereka (C3):", opsi_sdq, key="sdq_a12")
        q13 = st.radio("13. Sering merasa tidak bahagia, sedih atau menangis (E3):", opsi_sdq, key="sdq_a13")
        q14 = st.radio("14. Pada umumnya disukai oleh anak-anak lain (P3*):", opsi_sdq, key="sdq_a14")
        q15 = st.radio("15. Mudah teralih perhatiannya, tidak dapat berkonsentrasi (H3):", opsi_sdq, key="sdq_a15")
        q16 = st.radio("16. Gugup atau sulit berpisah dengan orang tua/pengasuhnya pada situasi baru, mudah kehilangan rasa percaya diri (E4):", opsi_sdq, key="sdq_a16")
        q17 = st.radio("17. Bersikap baik terhadap anak-anak yang lebih muda (Pr4):", opsi_sdq, key="sdq_a17")
        q18 = st.radio("18. Sering berbohong atau berbuat curang (C4):", opsi_sdq, key="sdq_a18")
        q19 = st.radio("19. Diganggu, dipermainkan, diintimidasi atau diancam oleh anak-anak lain (P4):", opsi_sdq, key="sdq_a19")
        q20 = st.radio("20. Sering menawarkan diri untuk membantu orang lain (orangtua, guru, anak-anak lain) (Pr5):", opsi_sdq, key="sdq_a20")
        q21 = st.radio("21. Sebelum melakukan sesuatu ia berpikir dahulu tentang akibatnya (H4*):", opsi_sdq, key="sdq_a21")
        q22 = st.radio("22. Mencuri dari rumah, sekolah, atau tempat lain (C5):", opsi_sdq, key="sdq_a22")
        q23 = st.radio("23. Lebih mudah berteman dengan anak-anak lain daripada dengan anak-anak lain (P5):", opsi_sdq, key="sdq_a23")
        q24 = st.radio("24. Banyak yang ditakuti, mudah menjadi takut (E5):", opsi_sdq, key="sdq_a24")
        q25 = st.radio("25. Memiliki perhatian yang baik terhadap apapun, mampu menyelesaikan tugas atau pekerjaan rumah sampai selesai (H5*):", opsi_sdq, key="sdq_a25")

    if st.button("Hitung Skor SDQ", key="btn_sdq"):
        skala_dasar = {"Tidak Benar": 0, "Agak Benar": 1, "Selalu Benar": 2}
        skala_terbalik = {"Tidak Benar": 2, "Agak Benar": 1, "Selalu Benar": 0}

        # 1. Identifikasi Rumus Pengambilan Nilai Parameter Sesuai Kunci Ringkas Kemenkes
        skor_emosi = skala_dasar[q3] + skala_dasar[q8] + skala_dasar[q13] + skala_dasar[q16] + skala_dasar[q24]
        skor_perilaku = skala_dasar[q5] + skala_terbalik[q7] + skala_dasar[q12] + skala_dasar[q18] + skala_dasar[q22]
        skor_hiper = skala_dasar[q2] + skala_dasar[q10] + skala_dasar[q15] + skala_terbalik[q21] + skala_terbalik[q25]
        skor_sebaya = skala_dasar[q6] + skala_terbalik[q11] + skala_terbalik[q14] + skala_dasar[q19] + skala_dasar[q23]
        skor_prososial = skala_dasar[q1] + skala_dasar[q4] + skala_dasar[q9] + skala_dasar[q17] + skala_dasar[q20]
        
        total_kesulitan = skor_emosi + skor_perilaku + skor_hiper + skor_sebaya

        # 2. PROSES INTERPRETASI ADAPTIF BERDASARKAN TABEL KEMENKES (image_d53545.png)
        if "Remaja" in tipe_sdq:
            status_kesulitan = "Normal" if total_kesulitan <= 15 else ("Borderline" if total_kesulitan <= 19 else "Abnormal")
            status_emosi = "Normal" if skor_emosi <= 5 else ("Borderline" if skor_emosi == 6 else "Abnormal")
            status_perilaku = "Normal" if skor_perilaku <= 3 else ("Borderline" if skor_perilaku == 4 else "Abnormal")
            status_hiper = "Normal" if skor_hiper <= 5 else ("Borderline" if skor_hiper == 6 else "Abnormal")
            status_sebaya = "Normal" if skor_sebaya <= 3 else ("Borderline" if skor_sebaya in [4, 5] else "Abnormal")
        else:
            status_kesulitan = "Normal" if total_kesulitan <= 13 else ("Borderline" if total_kesulitan <= 16 else "Abnormal")
            status_emosi = "Normal" if skor_emosi <= 3 else ("Borderline" if skor_emosi == 4 else "Abnormal")
            status_perilaku = "Normal" if skor_perilaku <= 2 else ("Borderline" if skor_perilaku == 3 else "Abnormal")
            status_hiper = "Normal" if skor_hiper <= 5 else ("Borderline" if skor_hiper == 6 else "Abnormal")
            status_sebaya = "Normal" if skor_sebaya <= 2 else ("Borderline" if skor_sebaya == 3 else "Abnormal")
        
        status_prososial = "Normal" if skor_prososial >= 6 else ("Borderline" if skor_prososial == 5 else "Abnormal")

        # 3. DISPLAY PRESENTASI MEDIS YANG COMPREHENSIVE
        st.markdown("### 📊 Hasil Interpretasi")
        
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.metric(label="SKOR TOTAL KESULITAN", value=f"{total_kesulitan} / 40")
            if status_kesulitan == "Normal":
                st.success(f"Klasifikasi: **{status_kesulitan}**")
            elif status_kesulitan == "Borderline":
                st.warning(f"Klasifikasi: **{status_kesulitan}**")
            else:
                st.error(f"Klasifikasi: **{status_kesulitan}**")
                
        with col_m2:
            st.metric(label="SKOR PROSOSIAL (KEKUATAN)", value=f"{skor_prososial} / 10")
            st.info(f"Klasifikasi: **{status_prososial}**")
            
        st.markdown("#### 🔍 Breakdown Subskala Masalah Klinis:")
        st.markdown(f"""
        | Subskala Analisis | Skor Capaian | Status Interpretasi |
        | :--- | :---: | :--- |
        | 🧠 **Gejala Emosional (E)** | {skor_emosi} / 10 | {status_emosi} |
        | 🚸 **Masalah Perilaku (C)** | {skor_perilaku} / 10 | {status_perilaku} |
        | ⚡ **Hiperaktivitas/Inatensi (H)** | {skor_hiper} / 10 | {status_hiper} |
        | 👥 **Masalah Teman Sebaya (P)** | {skor_sebaya} / 10 | {status_sebaya} |
        """)

        # 4. MODUL DATABASE CLOUD
        if 'sheet' in globals() or 'sheet' in locals():
            try:
                sheet.append_row([
                    str(datetime.now().strftime('%Y-%m-%d %H:%M')), 
                    nama, nik, str(tgl_lahir), 
                    f"{tipe_sdq} - Total Kesulitan: {total_kesulitan} ({status_kesulitan})", 
                    total_kesulitan, status_kesulitan, pemeriksa
                ])
                st.balloons()
                st.success("Data Skrining Berhasil Diarsipkan Sesuai Standar Kemenkes!")
            except:
                pass

        # 🖨️ MENAMPILKAN TOMBOL CETAK PDF UNTUK SDQ
        st.markdown("---")
        tambahkan_tombol_cetak_pdf()


# =========================================================================
# KATEGORI: ORANG DEWASA / UMUM (SRQ-20)
# =========================================================================
if "SRQ" in kategori or "Dewasa" in kategori:
    st.subheader("📋 Self Reporting Questionnaire (SRQ-20)")
    st.info("Bacalah petunjuk ini seluruhnya sebelum mulai mengisi. Pertanyaan berikut berhubungan dengan masalah yang mungkin mengganggu Anda selama 30 hari terakhir.")
    
    pertanyaan_srq = [
        "1. Apakah Anda sering merasa sakit kepala?",
        "2. Apakah Anda kehilangan nafsu makan?",
        "3. Apakah tidur Anda tidak nyenyak?",
        "4. Apakah Anda mudah merasa takut?",
        "5. Apakah Anda merasa cemas, tegang, atau khawatir?",
        "6. Apakah tangan Anda gemetar?",
        "7. Apakah Anda mengalami gangguan pencernaan?",
        "8. Apakah Anda merasa sulit berpikir jernih?",
        "9. Apakah Anda merasa tidak bahagia?",
        "10. Apakah Anda lebih sering menangis?",
        "11. Apakah Anda merasa sulit untuk menikmati aktivitas sehari-hari?",
        "12. Apakah Anda mengalami kesulitan untuk mengambil keputusan?",
        "13. Apakah aktivitas/tugas sehari-hari Anda terbengkalai?",
        "14. Apakah Anda merasa tidak mampu berperan dalam kehidupan ini?",
        "15. Apakah Anda kehilangan minat terhadap banyak hal?",
        "16. Apakah Anda merasa tidak berharga?",
        "17. Apakah Anda mempunyai pikiran untuk mengakhiri hidup Anda?",
        "18. Apakah Anda merasa lelah sepanjang waktu?",
        "19. Apakah Anda merasa tidak enak di perut?",
        "20. Apakah Anda mudah lelah?"
    ]
    
    jawaban_srq = {}
    for i, q in enumerate(pertanyaan_srq):
        jawaban_srq[f"srq_{i+1}"] = st.radio(q, ["Tidak (T)", "Ya (Y)"], key=f"srq_q_{i+1}")

    # --- TOMBOL HITUNG DAN PEMROSESAN SKOR ---
    if st.button("Hitung Skor SRQ-20 & Simpan Data", key="btn_srq"):
        skor_total_srq = sum([1 if jawaban_srq[f"srq_{k}"] == "Ya (Y)" else 0 for k in range(1, 21)])
        ide_bunuh_diri = jawaban_srq["srq_17"] == "Ya (Y)"
        
        # --- LOGIKA INTERPRETASI ADAPTIF SESUAI SLIDE (image_c889ff.png) ---
        if ide_bunuh_diri:
            status_srq = "Indikasi Mengalami Masalah Kesehatan Jiwa (Kritis - Nomor 17 YA)"
            warna_status = "error"
            rekomendasi = "Terdapat ide mengakhiri hidup (Nomor 17). Sesuai panduan resmi, meskipun skor total < 6, pasien TETAP memerlukan pemeriksaan lanjutan wawancara psikiatrik secara segera."
        elif skor_total_srq >= 6:
            status_srq = "Indikasi Mengalami Masalah Kesehatan Jiwa"
            warna_status = "error"
            rekomendasi = "Skor total mencapai ambang batas (>= 6). Memerlukan pemeriksaan lanjutan wawancara psikiatrik untuk mengetahui ada atau tidaknya gangguan jiwa."
        else:
            status_srq = "Normal / Sehat Jiwa"
            warna_status = "success"
            rekomendasi = "Hasil skrining berada di bawah ambang batas kritis dan tidak ada indikasi ide cedera diri. Tetap berikan edukasi perawatan kesehatan mental mandiri."

        # --- PRESENTASI ANTARMUKA MEDIS ---
        st.markdown("### 📊 Hasil Skoring Resmi Kemenkes RI")
        st.metric(label="Skor Total Jawaban 'Ya'", value=f"{skor_total_srq} / 20")
        
        if warna_status == "error":
            st.error(f"**Status Interpretasi:** {status_srq}")
        else:
            st.success(f"**Status Interpretasi:** {status_srq}")
            
        st.info(f"💡 **Rekomendasi Tindakan Lanjutan:** {rekomendasi}")
        
        if ide_bunuh_diri:
            st.markdown("---")
            st.warning("🚨 **ALARM UTAMA (CRITICAL RED FLAG):** Segera lakukan pendampingan ketat dan koordinasikan alur rujukan sekunder. Jangan biarkan pasien tanpa pengawasan nakes.")

        # --- ARSIP DATABASE CLOUD ---
        if 'sheet' in globals() or 'sheet' in locals():
            try:
                sheet.append_row([
                    str(datetime.now().strftime('%Y-%m-%d %H:%M')), 
                    nama, nik, str(tgl_lahir), 
                    f"SRQ-20 - Skor: {skor_total_srq} ({status_srq})", 
                    skor_total_srq, status_srq, pemeriksa
                ])
                if warna_status == "success":
                    st.balloons()
            except:
                pass

        # 🖨️ MENAMPILKAN TOMBOL CETAK PDF UNTUK SRQ-20
        st.markdown("---")
        tambahkan_tombol_cetak_pdf()
