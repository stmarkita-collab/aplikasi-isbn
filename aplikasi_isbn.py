import streamlit as st
import random
import pandas as pd
import io

# Konfigurasi Halaman Utama
st.set_page_config(page_title="Sistem Manajemen & Registrasi ISBN", page_icon="ðŸ“š", layout="wide")

# Inisialisasi Basis Data Sederhana di Session State agar data tidak hilang saat refresh/pindah menu
if "database_buku" not in st.session_state:
    st.session_state.database_buku = [
        {"isbn": "978-623-224-115-2", "judul": "Laskar Pelangi", "penulis": "Andrea Hirata", "penerbit": "Bentang Pustaka", "tahun": "2025", "kategori": "Fiksi / Novel"},
        {"isbn": "978-623-901-550-4", "judul": "Bumi Manusia", "penulis": "Pramoedya Ananta Toer", "penerbit": "Lentera Dipantara", "tahun": "2024", "kategori": "Fiksi / Sejarah"},
        {"isbn": "978-623-123-456-7", "judul": "Belajar Python Dasar", "penulis": "Rian Wijaya", "penerbit": "Tekno Press", "tahun": "2025", "kategori": "Sains & Teknologi"},
    ]

# ----------------- FUNGSI UTAMA (LOGIKA MATEMATIS ISBN & BARCODE) -----------------
def hitung_check_digit_isbn13(sembilan_digit_awal):
    """Menghitung check digit (angka ke-13) berdasarkan formula standar EAN-13"""
    total = 0
    for i, digit in enumerate(sembilan_digit_awal):
        bobot = 1 if i % 2 == 0 else 3
        total += int(digit) * bobot
    sisa = total % 10
    check_digit = (10 - sisa) % 10
    return str(check_digit)

def generate_valid_isbn13():
    """Membuat simulasi deretan ISBN-13 Indonesia yang valid secara matematis"""
    prefix = "978"        # Buku fisik komersial
    group_id = "623"      # Kode geografis Indonesia terbaru
    registrant = str(random.randint(100, 999))  # Kode unik penerbit (simulasi)
    publication = str(random.randint(1000, 9999)) # Kode urut judul buku
    
    gabungan_12_digit = prefix + group_id + registrant + publication
    check_digit = hitung_check_digit_isbn13(gabungan_12_digit)
    
    isbn_rapi = f"{prefix}-{group_id}-{registrant}-{publication}-{check_digit}"
    return isbn_rapi

def validasi_isbn13(isbn_str):
    """Memvalidasi keaslian format dan matematika ISBN-13"""
    bersih = isbn_str.replace("-", "").replace(" ", "")
    if len(bersih) != 13 or not bersih.isdigit():
        return False, "ISBN harus terdiri dari 13 digit angka."
    
    total = 0
    for i in range(12):
        bobot = 1 if i % 2 == 0 else 3
        total += int(bersih[i]) * bobot
    
    sisa = total % 10
    check_digit_seharusnya = (10 - sisa) % 10
    
    if int(bersih[-1]) == check_digit_seharusnya:
        return True, "ISBN Valid secara matematis standar internasional."
    else:
        return False, f"ISBN Tidak Valid. Angka pemeriksa terakhir seharusnya adalah '{check_digit_seharusnya}'."

def konversi_ke_excel(df_data):
    """Mengonversi DataFrame ke bentuk bytes Excel menggunakan engine openpyxl"""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_data.to_excel(writer, index=False, sheet_name='Data ISBN Buku')
    return output.getvalue()

def buat_gambar_barcode(isbn_str):
    """Membuat visualisasi barcode EAN-13 menggunakan library python-barcode dalam memori"""
    import barcode
    from barcode.writer import ImageWriter
    
    # Bersihkan karakter strip agar tersisa 13 angka penuh
    isbn_bersih = isbn_str.replace("-", "").replace(" ", "")
    
    # Ambil 12 angka pertama karena library otomatis menghitung ulang check digit terakhir
    isbn_12 = isbn_bersih[:12]
    
    EAN = barcode.get_by_name('ean13')
    my_barcode = EAN(isbn_12, writer=ImageWriter())
    
    # Simpan ke byte stream dalam bentuk file PNG
    fp = io.BytesIO()
    my_barcode.write(fp)
    return fp.getvalue()

# ----------------- ANTARMUKA APLIKASI (STREAMLIT UI) -----------------
st.title("ðŸ“š Sistem Informasi & Registrasi Pengajuan ISBN")
st.write("Aplikasi internal pengelolaan data publikasi, validasi, dan generator kode standar Perpusnas.")

# Navigasi Menu Samping (Sidebar)
menu = st.sidebar.radio("PILIH MENU APLIKASI:", ["Buat & Registrasi ISBN Baru", "Data & Koleksi Buku", "Validasi Kode ISBN"])

# ----------------- MENU 1: BUAT & REGISTRASI ISBN BARU -----------------
if menu == "Buat & Registrasi ISBN Baru":
    st.header("ðŸ“ Formulir Pengajuan & Pembuatan ISBN")
    st.write("Isi metadata buku di bawah ini untuk menggenerasikan kode ISBN resmi ke dalam sistem.")
    
    col1, col2 = st.columns(2)
    with col1:
        judul = st.text_input("Judul Lengkap Buku", placeholder="Contoh: Pemrograman Python untuk Pemula")
        penulis = st.text_input("Nama Penulis / Pengarang", placeholder="Contoh: Budi Santoso, M.Kom.")
        penerbit = st.text_input("Nama Penerbit", value="Penerbit Interaktif Indonesia")
    
    with col2:
        tahun = st.selectbox("Tahun Terbit", [str(x) for x in range(2027, 2020, -1)])
        kategori = st.selectbox("Kategori / Subjek Buku", ["Fiksi / Novel", "Sains & Teknologi", "Sosial & Humaniora", "Buku Teks Akademik", "Anak-anak", "Biografi"])
        format_buku = st.radio("Format Publikasi", ["Cetak (Paperback)", "Digital (E-Book / PDF)"])

    st.subheader("ðŸ“ Unggah Berkas Persyaratan Perpusnas")
    file_halaman_judul = st.file_uploader("Unggah Halaman Judul & Daftar Isi (PDF/Format Gambar)", type=["pdf", "png", "jpg"])
    
    if st.button("Proses & Buat Kode ISBN", type="primary"):
        if not judul or not penulis:
            st.error("âŒ Gagal! Judul buku dan nama penulis wajib diisi.")
        else:
            isbn_baru = generate_valid_isbn13()
            data_baru = {"isbn": isbn_baru, "judul": judul, "penulis": penulis, "penerbit": penerbit, "tahun": tahun, "kategori": kategori}
            st.session_state.database_buku.append(data_baru)
            
            st.success(f"ðŸŽ‰ **Sukses! Registrasi Berhasil. Kode Resmi Anda: {isbn_baru}**")
            st.balloons()
            
            # --- TAMPILAN BARCODE SETELAH SUKSES REGISTRASI ---
            st.write("---")
            st.subheader("ðŸ–¨ï¸ Hasil Cetak Barcode EAN-13")
            
            try:
                gambar_barcode = buat_gambar_barcode(isbn_baru)
                
                # Buat susunan layout tengah agar gambar tidak terlalu melebar
                b_col1, b_col2, b_col3 = st.columns()
                with b_col2:
                    st.image(gambar_barcode, caption=f"Kode Batang Resmi ISBN: {isbn_baru}", use_container_width=True)
                    st.download_button(
                        label="ðŸ’¾ Unduh Gambar Barcode (.png)",
                        data=gambar_barcode,
                        file_name=f"barcode_{isbn_baru.replace('-', '')}.png",
                        mime="image/png"
                    )
            except Exception as e:
                st.warning("Gagal membuat visualisasi barcode. Pastikan semua library pendukung sudah terpasang.")

# ----------------- MENU 2: DATA & KOLEKSI BUKU -----------------
elif menu == "Data & Koleksi Buku":
    st.header("ðŸ“Š Database Buku ber-ISBN")
    
    pencarian = st.text_input("ðŸ” Cari data buku (masukkan judul, penulis, atau nomor ISBN):")
    df = pd.DataFrame(st.session_state.database_buku)
    
    if pencarian:
        df_tampilan = df[df['judul'].str.contains(pencarian, case=False) | 
                         df['penulis'].str.contains(pencarian, case=False) | 
                         df['isbn'].str.contains(pencarian, case=False)]
        st.write(f"Menampilkan hasil pencarian untuk: '{pencarian}'")
    else:
        df_tampilan = df
        st.write("Daftar seluruh buku terdaftar saat ini:")
        
    tab_tabel, tab_grafik, tab_cetak_barcode = st.tabs(["ðŸ“‹ Tabel Data Buku", "ðŸ“Š Grafik Statistik", "ðŸ–¨ï¸ Cetak Ulang Barcode"])
    
    with tab_tabel:
        st.dataframe(df_tampilan, use_container_width=True)
        st.write("---")
        st.subheader("ðŸ“¥ Ekspor Laporan")
        data_excel = konversi_ke_excel(df_tampilan)
        st.download_button(
            label="ðŸŸ¢ Unduh Data Buku (.xlsx)",
            data=data_excel,
            file_name="laporan_database_isbn.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
    with tab_grafik:
        if not df_tampilan.empty:
            st.subheader("ðŸ“ˆ Analisis Distribusi Buku")
            g_col1, g_col2 = st.columns(2)
            
            with g_col1:
                st.write("**Jumlah Buku berdasarkan Kategori**")
                stat_kategori = df_tampilan['kategori'].value_counts().reset_index()
                stat_kategori.columns = ['Kategori', 'Jumlah Buku']
                st.bar_chart(data=stat_kategori, x='Kategori', y='Jumlah Buku', color='#2b5c8f')
                
            with g_col2:
                st.write("**Jumlah Buku berdasarkan Tahun Terbit**")
                stat_tahun = df_tampilan['tahun'].value_counts().reset_index()
                stat_tahun.columns = ['Tahun', 'Jumlah Buku']
                stat_tahun = stat_tahun.sort_values(by='Tahun')
                st.bar_chart(data=stat_tahun, x='Tahun', y='Jumlah Buku', color='#e07a5f')
        else:
            st.info("Tidak ada data untuk divisualisasikan.")

    with tab_cetak_barcode:
        st.subheader("ðŸ” Pilih Buku untuk Cetak Barcode")
        if not df_tampilan.empty:
            pilihan_buku = st.selectbox(
                "Pilih judul buku yang ingin dicetak barcode-nya:",
                options=df_tampilan.index,
                format_func=lambda x: f"{df_tampilan.loc[x, 'judul']} ({df_tampilan.loc[x, 'isbn']})"
            )
            
            isbn_terpilih = df_tampilan.loc[pilihan_buku, 'isbn']
            judul_terpilih = df_tampilan.loc[pilihan_buku, 'judul']
            
            st.write(f"Menyiapkan cetakan barcode untuk buku: **{judul_terpilih}**")
            
            barcode_bytes = buat_gambar_barcode(isbn_terpilih)
            
            bc1, bc2, bc3 = st.columns([1, 1.5, 1])
            with bc2:
                st.image(barcode_bytes, caption=f"Barcode EAN-13: {isbn_terpilih}", use_container_width=True)
                st.download_button(
                    label=f"ðŸ’¾ Download Barcode - {judul_terpilih[:15]}...",
                    data=barcode_bytes,
                    file_name=f"barcode_{isbn_terpilih.replace('-', '')}.png",
                    mime="image/png"
                )
        else:
            st.info("Tidak ada buku yang dapat dipilih.")

# ----------------- MENU 3: VALIDASI KODE ISBN -----------------
elif menu == "Validasi Kode ISBN":
    st.header("ðŸ” Alat Validasi Validitas ISBN-13")
    st.write("Gunakan menu ini untuk memverifikasi apakah kombinasi angka pada kode ISBN buku Anda sudah benar secara formula internasional.")
    
    input_isbn = st.text_input("Masukkan Kode ISBN-13 yang akan dicek:", placeholder="Contoh: 978-623-224-115-2")
    
    if st.button("Cek Validitas"):
        if input_isbn:
            is_valid, pesan = validasi_isbn13(input_isbn)
            if is_valid:
                st.success(f"âœ… {pesan}")
            else:
                st.error(f"âŒ {pesan}")
        else:
            st.warning("Silakan masukkan kode ISBN terlebih dahulu.")
