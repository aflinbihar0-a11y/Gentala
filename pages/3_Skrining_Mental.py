import streamlit as st
import datetime
import os
import gspread
from google.oauth2.service_account import Credentials

# Mengatur konfigurasi dasar halaman utama Streamlit
st.set_page_config(page_title="GENTALA - Jiwa", page_icon="🧠", layout="centered")

# =========================================================================
# FUNGSI UTAMA: TOMBOL CETAK PDF (CSS MEDIA PRINT)
# =========================================================================
def tambahkan_tombol_cetak_pdf():
    st.markdown(
        """
        <style>
        @media print {
            /* Sembunyikan elemen navigasi Streamlit saat masuk mode print/PDF */
            [data-testid="stSidebar"], header, footer, .element-container:has(iframe), .stButton {
                display: none !important;
            }
            .main .block-container {
                padding-top: 0.5rem !important;
                padding-bottom: 0.5rem !important;
            }
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    tombol_html = """
    <style>
        .btn-print {
            width: 100%;
            background-color: #1E3A8A;
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
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        }
        .btn-print:hover {
            background-color: #152A66;
        }
    </style>
    <button class="btn-print" onclick="window.parent.print()">
        🖨️ Cetak Hasil Skrining / Simpan ke PDF
    </button>
    """
    st.components.v1.html(tombol_html, height=55)

# =========================================================================
# FUNGSI DATABASE: KONEKSI TAB SHEET_MENTAL_HEALTH
# =========================================================================
def koneksi_spreadsheet_mental():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_dict = st.secrets["gcp_service_account"] 
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(creds)
    # Membuka file utama dan mengunci spesifik ke tab Sheet_Mental_Health
    sheet = client.open("GrowTrack Database").worksheet("Sheet_Mental_Health")
    return sheet

# =========================================================================
# 1. IDENTITAS & FILTER UTAMA
# =========================================================================
st.title("🧠 GENTALA - Skrining Kesehatan Jiwa")
st.caption("Inovasi Program Integrasi - Puskesmas Batu Tangga")

kategori = st.selectbox(
    "Pilih Kelompok Sasaran Skrining:",
    ["Pasca Persalinan [EPDS]", "Anak & Remaja [SDQ]", "Orang Dewasa [SRQ-20]"],
    key="pilih_kategori_utama"
)

st.markdown("### 📋 Data Identitas Pasien")
col_id1, col_id2 = st.columns(2)

with col_id1:
    nama = st.text_input("Nama Lengkap Pasien:", key="id_nama")
    nik = st.text_input("Nomor NIK (Boleh dikosongkan):", key="id_nik")

with col_id2:
    tgl_lahir = st.date_input("Tanggal Lahir:", value=datetime.date(2000, 1, 1), key="id_tgl")
    pemeriksa = st.text_input("Nama Tenaga Kesehatan / Kader:", key="id_nakes")

st.markdown("---")

# Initialize shared upload variables
sudah_submit = False
baris_data_cloud = []

# =========================================================================
# 2. MODUL KUESIONER IBU HAMIL & MENYUSUI (EPDS)
# =========================================================================
if "EPDS" in kategori:
    st.subheader("🤰 Edinburgh Postnatal Depression Scale (EPDS)")
    st.info("Silakan memilih jawaban yang paling mirip dengan perasaan Anda selama 7 hari terakhir.")
    
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

    if st.button("Hitung & Simpan Skor EPDS", key="btn_epds"):
        skala_normal = {"a": 0, "b": 1, "c": 2, "d": 3}
        skala_terbalik = {"a": 3, "b": 2, "c": 1, "d": 0}
        
        skor_total = (skala_normal[epds_1[0]] + skala_normal[epds_2[0]] + skala_terbalik[epds_3[0]] + 
                      skala_normal[epds_4[0]] + skala_terbalik[epds_5[0]] + skala_terbalik[epds_6[0]] + 
                      skala_terbalik[epds_7[0]] + skala_terbalik[epds_8[0]] + skala_terbalik[epds_9[0]] + 
                      skala_terbalik[epds_10[0]])
        
        if skor_total <= 9:
            status_mental = "Risiko rendah depresi"
            rekomendasi = "Kondisi emosional stabil. Tetap berikan dukungan psikososial dasar."
            st.success(f"**Status:** {status_mental}")
        elif 10 <= skor_total <= 12:
            status_mental = "Risiko sedang (Distres emosional)"
            rekomendasi = "Perlu pemantauan lebih lanjut. Lakukan evaluasi ulang/pendampingan berkala oleh nakes."
            st.warning(f"**Status:** {status_mental}")
        else:
            status_mental = "Risiko tinggi depresi"
            rekomendasi = "Gejala mengarah kuat pada depresi perinatal. Segera rujuk ke profesional kesehatan jiwa."
            st.error(f"**Status:** {status_mental}")
            
        st.metric(label="SKOR TOTAL EPDS", value=f"{skor_total} / 30")
        st.info(f"💡 **Rekomendasi Tindakan:** {rekomendasi}")
        
        # Red-flag safety check pertanyaan no 10
        flag_danger = "Ada" if skala_terbalik[epds_10[0]] > 0 else "Tidak Ada"
        if flag_danger == "Ada":
            st.error("🚨 **ALARM UTAMA KLINIS (IDE CEDERA DIRI):** Pasien mengindikasikan pikiran menyakiti diri sendiri! Tatalaksana psikologis/rujukan darurat wajib berjalan segera!")
            
        # Mapping 12 Kolom standar database
        baris_data_cloud = [
            str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            nama, f"NIK/RM: {nik}", "EPDS (Ibu Perinatal)", skor_total, "-", status_mental, rekomendasi, "Ibu Hamil/Menyusui", flag_danger, pemeriksa, "-"
        ]
        sudah_submit = True

# =========================================================================
# 3. MODUL KUESIONER ANAK & REMAJA (SDQ)
# =========================================================================
elif "SDQ" in kategori:
    st.subheader("🧸 Kuesioner SDQ (Strengths and Difficulties Questionnaire)")
    tipe_sdq = st.selectbox("Pilih Versi Instrumen SDQ:", ["SDQ Anak (Usia 4-10 Tahun / Parent-Report)", "SDQ Remaja (Usia 11-17 Tahun / Self-Report)"], key="pilih_versi_sdq")
    opsi_sdq = ["Tidak Benar", "Agak Benar", "Selalu Benar"]
    
    # Render pertanyaan (Gunakan form radio button terpusat)
    if "Remaja" in tipe_sdq:
        st.info("Sudut pandang Remaja (Self-Report)")
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
        st.info("Sudut pandang Orang Tua/Pengasuh (Parent-Report)")
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
        q23 = st.radio("23. Lebih mudah berteman dengan anak-anak lain daripada dengan orang dewasa (P5):", opsi_sdq, key="sdq_a23")
        q24 = st.radio("24. Banyak yang ditakuti, mudah menjadi takut (E5):", opsi_sdq, key="sdq_a24")
        q25 = st.radio("25. Memiliki perhatian yang baik terhadap apapun, mampu menyelesaikan tugas atau pekerjaan rumah sampai selesai (H5*):", opsi_sdq, key="sdq_a25")

    if st.button("Hitung & Simpan Skor SDQ", key="btn_sdq"):
        skala_dasar = {"Tidak Benar": 0, "Agak Benar": 1, "Selalu Benar": 2}
        skala_terbalik = {"Tidak Benar": 2, "Agak Benar": 1, "Selalu Benar": 0}

        skor_emosi = skala_dasar[q3] + skala_dasar[q8] + skala_dasar[q13] + skala_dasar[q16] + skala_dasar[q24]
        skor_perilaku = skala_dasar[q5] + skala_terbalik[q7] + skala_dasar[q12] + skala_dasar[q18] + skala_dasar[q22]
        skor_hiper = skala_dasar[q2] + skala_dasar[q10] + skala_dasar[q15] + skala_terbalik[q21] + skala_terbalik[q25]
        skor_sebaya = skala_dasar[q6] + skala_terbalik[q11] + skala_terbalik[q14] + skala_dasar[q19] + skala_dasar[q23]
        skor_prososial = skala_dasar[q1] + skala_dasar[q4] + skala_dasar[q9] + skala_dasar[q17] + skala_dasar[q20]
        
        skor_total = skor_emosi + skor_perilaku + skor_hiper + skor_sebaya

        if "Remaja" in tipe_sdq:
            status_mental = "Normal" if skor_total <= 15 else ("Borderline" if skor_total <= 19 else "Abnormal")
        else:
            status_mental = "Normal" if skor_total <= 13 else ("Borderline" if skor_total <= 16 else "Abnormal")
            
        rekomendasi = "Edukasi kesehatan mental anak & evaluasi rutin." if status_mental == "Normal" else ("Jadwalkan skrining ulang & edukasi pola asuh." if status_mental == "Borderline" else "Rujuk ke poli tumbuh kembang anak / psikolog.")
        detail_sub = f"E:{skor_emosi}, P:{skor_perilaku}, H:{skor_hiper}, S:{skor_sebaya}, Pr:{skor_prososial}"
        
        # Tampilkan Hasil Presentasi Medis di Layar
        st.markdown("### 📊 Hasil Interpretasi")
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.metric(label="SKOR TOTAL KESULITAN", value=f"{skor_total} / 40")
            if status_mental == "Normal": st.success(f"Klasifikasi: **{status_mental}**")
            elif status_mental == "Borderline": st.warning(f"Klasifikasi: **{status_mental}**")
            else: st.error(f"Klasifikasi: **{status_mental}**")
        with col_m2:
            st.metric(label="SKOR PROSOSIAL (KEKUATAN)", value=f"{skor_prososial} / 10")
            st.info(f"Subskala Kekuatan: {status_mental}")

        st.markdown(f"""
        | Subskala Analisis | Skor Capaian |
        | :--- | :---: |
        | 🧠 **Gejala Emosional (E)** | {skor_emosi} / 10 |
        | 🚸 **Masalah Perilaku (C)** | {skor_perilaku} / 10 |
        | ⚡ **Hiperaktivitas/Inatensi (H)** | {skor_hiper} / 10 |
        | 👥 **Masalah Teman Sebaya (P)** | {skor_sebaya} / 10 |
        """)
        
        # Mapping 12 Kolom standar database
        baris_data_cloud = [
            str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            nama, f"NIK/RM: {nik}", tipe_sdq, skor_total, detail_sub, status_mental, rekomendasi, "Anak/Remaja", "-", pemeriksa, "-"
        ]
        sudah_submit = True

# =========================================================================
# 4. MODUL KUESIONER ORANG DEWASA / UMUM (SRQ-20)
# =========================================================================
else:
    st.subheader("📋 Self Reporting Questionnaire (SRQ-20)")
    st.info("Pertanyaan berikut berhubungan dengan masalah yang mungkin mengganggu Anda selama 30 hari terakhir.")
    
    pertanyaan_srq = [
        "1. Apakah Anda sering merasa sakit kepala?", "2. Apakah Anda kehilangan nafsu makan?", "3. Apakah tidur Anda tidak nyenyak?",
        "4. Apakah Anda mudah merasa takut?", "5. Apakah Anda merasa cemas, tegang, atau khawatir?", "6. Apakah tangan Anda gemetar?",
        "7. Apakah Anda mengalami gangguan pencernaan?", "8. Apakah Anda merasa sulit berpikir jernih?", "9. Apakah Anda merasa tidak bahagia?",
        "10. Apakah Anda lebih sering menangis?", "11. Apakah Anda merasa sulit untuk menikmati aktivitas sehari-hari?",
        "12. Apakah Anda mengalami kesulitan untuk mengambil keputusan?", "13. Apakah aktivitas/tugas sehari-hari Anda terbengkalai?",
        "14. Apakah Anda merasa tidak mampu berperan dalam kehidupan ini?", "15. Apakah Anda kehilangan minat terhadap banyak hal?",
        "16. Apakah Anda merasa tidak berharga?", "17. Apakah Anda mempunyai pikiran untuk mengakhiri hidup Anda?",
        "18. Apakah Anda merasa lelah sepanjang waktu?", "19. Apakah Anda merasa tidak enak di perut?", "20. Apakah Anda mudah lelah?"
    ]
    
    jawaban_srq = {}
    for i, q in enumerate(pertanyaan_srq):
        jawaban_srq[f"srq_{i+1}"] = st.radio(q, ["Tidak (T)", "Ya (Y)"], key=f"srq_q_{i+1}")

    if st.button("Hitung & Simpan Skor SRQ-20", key="btn_srq"):
        skor_total = sum([1 if jawaban_srq[f"srq_{k}"] == "Ya (Y)" else 0 for k in range(1, 21)])
        ide_bunuh_diri = "Ada" if jawaban_srq["srq_17"] == "Ya (Y)" else "Tidak Ada"
        
        if ide_bunuh_diri == "Ada":
            status_mental = "Indikasi Masalah Jiwa (Kritis - No 17 YA)"
            rekomendasi = "Terdapat pikiran mengakhiri hidup. Wajib segera lakukan pemeriksaan lanjutan wawancara psikiatrik dan pendampingan ketat."
            st.error(f"**Status:** {status_mental}")
        elif skor_total >= 6:
            status_mental = "Indikasi Masalah Kesehatan Jiwa"
            rekomendasi = "Skor total ≥ 6. Pasien memerlukan pemeriksaan lanjutan wawancara psikiatrik di Puskesmas."
            st.error(f"**Status:** {status_mental}")
        else:
            status_mental = "Normal / Sehat Jiwa"
            rekomendasi = "Hasil skrining normal. Berikan edukasi perawatan kesehatan mental mandiri."
            st.success(f"**Status:** {status_mental}")
            
        st.metric(label="SKOR JAWABAN 'YA'", value=f"{skor_total} / 20")
        st.info(f"💡 **Rekomendasi Tindakan:** {rekomendasi}")
        
        if ide_bunuh_diri == "Ada":
            st.warning("🚨 **CRITICAL RED FLAG:** Jangan biarkan pasien pulang tanpa pengawasan keluarga atau nakes!")
            
        # Mapping 12 Kolom standar database
        baris_baru = [
            str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")), # Kolom A: Waktu Input
            nama,                                               # Kolom B: Nama Pasien
            umur,                                               # Kolom C: Umur (Tahun/Bulan)
            jenis_kuesioner,                                           # Kolom D: Jenis Kuesioner (EPDS/SRQ-20/SDQ)
            sub_skor_detail,                                           # Kolom E: Sub-Skor / Detail
            status_interpretasi,                                       # Kolom F: Status Interpretasi
            rekomendasi_klinis,                                        # Kolom G: Rekomendasi Klinis
        # 🎯 SEKARANG KOLOM H BERSIFAT UNIVERSAL UNTUK SEMUA KUESIONER:
            kategori_hasil_kuesioner,                                  # Kolom H: Masukkan interpretasi teks di sini (Contoh: "Indikasi Masalah Jiwa", "Risiko Tinggi Depresi", atau "Normal")
            faktor_risiko,                                             # Kolom I: Faktor Risiko
            pemeriksa,                                                 # Kolom J: Pemeriksa
            catatan                                                    # Kolom K: Catatan
        ]
        sudah_submit = True

# =========================================================================
# 5. AKSI EKSEKUSI: PENGIRIMAN DATA CLOUD & TOMBOL PDF
# =========================================================================
if sudah_submit:
    with st.spinner("Sedang merekam hasil skrining ke database Google Sheets..."):
        try:
            sheet_mental = koneksi_spreadsheet_mental()
            sheet_mental.append_row(baris_data_cloud)
            st.balloons()
            st.success("✅ Seluruh data skrining kesehatan mental berhasil disimpan ke tab 'Sheet_Mental_Health'!")
        except Exception as e:
            st.error(f"⚠️ Gagal mengirim data ke Google Sheets. Periksa konfigurasi st.secrets Anda. Error: {e}")
            
    # Menampilkan tombol print PDF secara elegan tepat setelah proses kalkulasi & simpan sukses
    st.markdown("---")
    tambahkan_tombol_cetak_pdf()
