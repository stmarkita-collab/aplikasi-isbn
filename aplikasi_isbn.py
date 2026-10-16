import streamlit as st
import random
import pandas as pd

# Konfigurasi Halaman Utama
st.set_page_config(page_title="Sistem Manajemen & Registrasi ISBN", page_icon="📚", layout="wide")

# Inisialisasi Basis Data Sederhana di Session State agar data tidak hilang saat refresh/pindah menu
if "database_buku" not in st.session_state:
    st.session_state.database_buku = [
        {"isbn": "978-623-224-115-2", "judul": "Laskar Pelangi", "penulis": "Andrea Hirata", "penerbit": "Bentang Pustaka", "tahun": "2005", "kategori": "Fiksi / Novel"},
        {"isbn": "978-623-901-550-4", "judul": "Bumi Manusia", "penulis": "Pramoedya Ananta Toer", "penerbit": "Lentera Dipantara", "tahun": "1980", "kategori": "Fiksi / Sejarah"},
    ]

# ----------------- FUNGSI UTAMA (LOGIKA MATEMATIS ISBN) -----------------
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
    
    if int(bersih[12]) == check_digit_seharusnya:
        return True, "ISBN Valid secara matematis standar internasional."
    else:
        return False, f"ISBN Tidak Valid. Angka pemeriksa terakhir seharusnya adalah '{check_digit_seharusnya}'."

# ----------------- ANTARMUKA APLIKASI (STREAMLIT UI) -----------------
st.title("📚 Sistem Informasi & Registrasi Pengajuan ISBN")
st.write("Aplikasi internal pengelolaan data publikasi, validasi, dan generator kode standar Perpusnas.")

# Navigasi Menu Samping (Sidebar)
menu = st.sidebar.radio("PILIH MENU APLIKASI:", ["Buat & Registrasi ISBN Baru", "Data & Koleksi Buku", "Validasi Kode ISBN"])

# ----------------- MENU 1: BUAT & REGISTRASI ISBN BARU -----------------
if menu == "Buat & Registrasi ISBN Baru":
    st.header("📝 Formulir Pengajuan & Pembuatan ISBN")
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

    st.subheader("📁 Unggah Berkas Persyaratan Perpusnas")
    file_halaman_judul = st.file_uploader("Unggah Halaman Judul & Daftar Isi (PDF/Format Gambar)", type=["pdf", "png", "jpg"])
    
    # Tombol Aksi Pembuatan
    if st.button("Proses & Buat Kode ISBN", type="primary"):
        if not judul or not penulis:
            st.error("❌ Gagal! Judul buku dan nama penulis wajib diisi.")
        elif not file_halaman_judul:
            st.warning("⚠️ Dokumen pelengkap belum diunggah, namun sistem lokal akan tetap menggenerasikan nomor simulasi.")
            
            # Generate ISBN Baru secara otomatis
            isbn_baru = generate_valid_isbn13()
            
            # Simpan data ke basis data lokal (Session State)
            data_baru = {"isbn": isbn_baru, "judul": judul, "penulis": penulis, "penerbit": penerbit, "tahun": tahun, "kategori": kategori}
            st.session_state.database_buku.append(data_baru)
            
            st.success(f"🎉 **Sukses! Kode ISBN Baru Berhasil Dibuat: {isbn_baru}**")
            st.info("Buku telah berhasil disimpan ke database internal. Anda bisa mengeceknya di menu 'Data & Koleksi Buku'.")
        else:
            isbn_baru = generate_valid_isbn13()
            data_baru = {"isbn": isbn_baru, "judul": judul, "penulis": penulis, "penerbit": penerbit, "tahun": tahun, "kategori": kategori}
            st.session_state.database_buku.append(data_baru)
            
            st.success(f"🎉 **Sukses! Registrasi Berhasil. Kode Resmi Anda: {isbn_baru}**")
            st.balloons()

# ----------------- MENU 2: DATA & KOLEKSI BUKU -----------------
elif menu == "Data & Koleksi Buku":
    st.header("📊 Database Buku ber-ISBN")
    
    # Fitur Pencarian Dinamis
    pencarian = st.text_input("🔍 Cari data buku (masukkan judul, penulis, atau nomor ISBN):")
    
    # Konversi data ke Dataframe Pandas agar visualisasi tabel rapi
    df = pd.DataFrame(st.session_state.database_buku)
    
    if pencarian:
        df_filtered = df[df['judul'].str.contains(pencarian, case=False) | 
                         df['penulis'].str.contains(pencarian, case=False) | 
                         df['isbn'].str.contains(pencarian, case=False)]
        st.write(f"Menampilkan hasil pencarian untuk: '{pencarian}'")
        st.dataframe(df_filtered, use_container_width=True)
    else:
        st.write("Daftar seluruh buku terdaftar saat ini:")
        st.dataframe(df, use_container_width=True)

# ----------------- MENU 3: VALIDASI KODE ISBN -----------------
elif menu == "Validasi Kode ISBN":
    st.header("🔍 Alat Validasi Validitas ISBN-13")
    st.write("Gunakan menu ini untuk memverifikasi apakah kombinasi angka pada kode ISBN buku Anda sudah benar secara formula internasional atau mengandung kesalahan ketik (*typo*).")
    
    input_isbn = st.text_input("Masukkan Kode ISBN-13 yang akan dicek:", placeholder="Contoh: 978-623-224-115-2")
    
    if st.button("Cek Validitas"):
        if input_isbn:
            is_valid, pesan = validasi_isbn13(input_isbn)
            if is_valid:
                st.success(f"✅ {pesan}")
            else:
                st.error(f"❌ {pesan}")
        else:
            st.warning("Silakan masukkan kode ISBN terlebih dahulu.")
