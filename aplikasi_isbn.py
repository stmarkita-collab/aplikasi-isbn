import streamlit as st
import random
import re

# Set page config
st.set_page_config(
    page_title="ISBN Master - Aplikasi Pengelola & Validasi ISBN",
    page_icon="📚",
    layout="wide"
)

# Custom Styling
st.markdown("""
    <style>
    .main-title {
        font-size: 32px;
        font-weight: bold;
        color: #1E3A8A;
        margin-bottom: 20px;
    }
    .card {
        padding: 20px;
        border-radius: 10px;
        background-color: #F3F4F6;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# Session state initialization for database mockup
if 'books_db' not in st.session_state:
    st.session_state.books_db = [
        {"isbn": "978-602-03-1234-5", "judul": "Laskar Pelangi", "penulis": "Andrea Hirata", "penerbit": "Bentang Pustaka", "tahun": "2005"},
        {"isbn": "978-623-24-4567-8", "judul": "Bumi", "penulis": "Tere Liye", "penerbit": "Gramedia Pustaka Utama", "tahun": "2014"},
        {"isbn": "978-979-43-3987-1", "judul": "Filosofi Kopi", "penulis": "Dee Lestari", "penerbit": "Bentang Budaya", "tahun": "2006"}
    ]

# Helper Functions
def validate_isbn13(isbn_str):
    # Clean string
    cleaned = re.sub(r'[- ]', '', isbn_str)
    if len(cleaned) != 13 or not cleaned.isdigit():
        return False
    
    # Calculate check digit
    total = 0
    for i, digit in enumerate(cleaned[:-1]):
        weight = 1 if i % 2 == 0 else 3
        total += int(digit) * weight
    
    check_digit = (10 - (total % 10)) % 10
    return check_digit == int(cleaned[-1])

def generate_random_isbn():
    prefix = "978"
    group = "623" # Indonesia new group
    publisher = f"{random.randint(10, 9999):02d}"
    title = f"{random.randint(10, 99999):02d}"
    
    # Combine first 12 digits
    partial = f"{prefix}{group}{publisher}{title}"
    partial = partial[:12] # Ensure exactly 12
    
    total = 0
    for i, digit in enumerate(partial):
        weight = 1 if i % 2 == 0 else 3
        total += int(digit) * weight
    check_digit = (10 - (total % 10)) % 10
    
    full_isbn = f"{partial}{check_digit}"
    # Format layout: 978-623-XXXX-XXX-X
    return f"{full_isbn[:3]}-{full_isbn[3:6]}-{full_isbn[6:10]}-{full_isbn[10:12]}-{full_isbn[12]}"

# Header UI
st.markdown("<div class='main-title'>📚 ISBN Master Dashboard</div>", unsafe_allow_html=True)
st.write("Aplikasi internal untuk manajemen data buku, validasi standardisasi ISBN-13, dan generator otomatis.")

# Sidebar Navigation
menu = st.sidebar.radio("Navigasi Menu", ["Daftar Buku (Database)", "Validasi & Cek ISBN", "Generator ISBN Baru"])

if menu == "Daftar Buku (Database)":
    st.subheader("🗄️ Database Registrasi Buku")
    
    # Form Tambah Buku
    with st.expander("➕ Daftarkan Buku Baru (Ber-ISBN)"):
        with st.form("add_book_form"):
            new_isbn = st.text_input("Nomor ISBN-13", placeholder="Contoh: 978-602-xxx-xxx-x")
            new_title = st.text_input("Judul Buku")
            new_author = st.text_input("Nama Penulis / Pengarang")
            new_publisher = st.text_input("Nama Penerbit")
            new_year = st.text_input("Tahun Terbit")
            
            submit = st.form_submit_button("Simpan ke Database")
            if submit:
                if not new_isbn or not new_title:
                    st.error("Gagal: ISBN dan Judul Buku wajib diisi!")
                elif not validate_isbn13(new_isbn):
                    st.warning("⚠️ Peringatan: Format atau Check Digit ISBN tidak valid. Pastikan kembali input Anda.")
                else:
                    st.session_state.books_db.append({
                        "isbn": new_isbn, "judul": new_title, "penulis": new_author, "penerbit": new_publisher, "tahun": new_year
                    })
                    st.success(f"Sukses: Buku '{new_title}' berhasil didaftarkan!")

    # Search bar
    search_query = st.text_input("🔍 Cari berdasarkan Judul, Penulis, atau ISBN:", "")
    
    # Filtered List
    filtered_books = [
        b for b in st.session_state.books_db 
        if search_query.lower() in b['judul'].lower() 
        or search_query.lower() in b['penulis'].lower() 
        or search_query.lower() in b['isbn'].lower()
    ]
    
    if filtered_books:
        st.table(filtered_books)
    else:
        st.info("Tidak ada data buku yang cocok dengan pencarian.")

elif menu == "Validasi & Cek ISBN":
    st.subheader("🔍 Validasi Keaslian Nomor ISBN")
    st.write("Masukkan 13 digit nomor ISBN untuk memverifikasi struktur kode matematisnya (*Check Digit*).")
    
    input_isbn = st.text_input("Masukkan Kode ISBN-13:", value="978-602-03-1234-5")
    
    if st.button("Jalankan Pemindaian Validitas"):
        is_valid = validate_isbn13(input_isbn)
        if is_valid:
            st.success("✅ ISBN VALID! Struktur penulisan dan Check Digit memenuhi standar internasional EAN/ISBN-13.")
            
            # Breakdown info basic parsing
            cleaned = re.sub(r'[- ]', '', input_isbn)
            st.markdown(f"""
            **Analisis Struktur Kode:**
            *   **Prefix Komersial:** {cleaned[:3]} (Identitas Buku Dunia)
            *   **Kode Negara/Grup:** {cleaned[3:6]} (Wilayah Registrasi)
            *   **Angka Pemeriksa (Check Digit):** {cleaned[-1]}
            """)
        else:
            st.error("❌ ISBN TIDAK VALID! Angka pemeriksa terakhir tidak cocok dengan kalkulasi algoritma tertimbang ISBN-13. Periksa salah ketik.")

elif menu == "Generator ISBN Baru":
    st.subheader("🎲 Alokasi Mock ISBN Generator")
    st.write("Fitur simulasi untuk memproduksi kode ISBN-13 acak yang valid dan siap pakai untuk draf buku mockup penerbitan.")
    
    col1, col2 = st.columns(2)
    with col1:
        jumlah = st.number_input("Jumlah Kode yang Dihasilkan:", min_value=1, max_value=20, value=5)
        if st.button("Generate Kode"):
            st.write("**Hasil Generate Terkini (Siap Digunakan):**")
            for i in range(jumlah):
                generated = generate_random_isbn()
                st.code(generated, language="text")
    with col2:
        st.info("💡 **Informasi Eksternal:**\nDi Indonesia, alokasi nomor resmi ber-barcode wajib melalui pintu gerbang satu pintu di situs [Perpustakaan Nasional RI](https://isbn.perpusnas.go.id/). Generator ini hanya memproduksi kode acak yang valid secara matematika untuk keperluan internal/testing sistem.")