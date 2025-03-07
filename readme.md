# Proyek Analisis Bike Sharing

## Deskripsi
Proyek ini menganalisis data penyewaan sepeda dari **Bike Sharing Dataset** untuk menjawab dua pertanyaan bisnis:
1. Bagaimana pengaruh cuaca terhadap jumlah penyewaan sepeda?
2. Apa pola penggunaan sepeda berdasarkan hari dan jam?

Proyek ini mencakup analisis data lengkap, visualisasi interaktif, dan dashboard menggunakan Streamlit.

## Cara Menjalankan Dashboard
1. Pastikan Anda berada di direktori proyek: `cd /path/to/submission`.
2. Aktifkan virtual environment:
   - macOS/Linux: `source venv/bin/activate`
   - Windows: `venv\Scripts\activate`
3. Instal dependensi: `pip install -r requirements.txt`.
4. Jalankan dashboard: `streamlit run dashboard/dashboard.py`.
5. Buka browser di `http://localhost:8501` untuk melihat dashboard.

## Struktur Direktori
ANALISIS DATA DENGAN PYTHON/
├── dashboard/
│   ├── dashboard.py          # Script utama untuk dashboard Streamlit
│   └── main_data.csv        # Data yang telah diproses untuk dashboard
├── data/
│   ├── day.csv             # Dataset harian penyewaan sepeda
│   └── hour.csv            # Dataset per jam penyewaan sepeda
├── notebook.ipynb          # Notebook Jupyter untuk analisis lengkap
├── README.md               # Dokumentasi proyek
├── requirements.txt        # Daftar dependensi Python
└── url.txt                 # Tautan ke dashboard online (Streamlit Cloud)


## Cara Menjalankan Proyek

### Prasyarat
- Python 3.x
- Virtual environment (opsional, direkomendasikan)
- Library yang diperlukan (tercantum di `requirements.txt`)

### Langkah-langkah
1. **Kloning Repository**
- git clone https://github.com/mocitaz/Submission-Analisis-Data-Dengan-Python.git
- cd ANALISIS DATA DENGAN PYTHON

2. **Siapkan Lingkungan**
- Buat virtual environment (opsional):
  python -m venv venv
  source venv/bin/activate  # macOS/Linux
  venv\Scripts\activate     # Windows
- Instal dependensi pip install -r requirements.txt


3. **Jalankan Notebook**
- Buka `notebook.ipynb` di Jupyter Notebook atau VSCode untuk melihat analisis lengkap


4. **Jalankan Dashboard**
- Aktifkan virtual environment (jika digunakan).
- Jalankan dashboard lokal

- Buka browser di `http://localhost:8501` untuk melihat dashboard.

5. **Akses Online (Opsional)**
- Kunjungi tautan di `url.txt` untuk mengakses dashboard yang dideploy di Streamlit Cloud.

## Fitur Utama
- **Visualisasi Interaktif**: Termasuk bar plot, box plot, scatter 3D, heatmap korelasi, heatmap pola jam, dan line plot tren waktu.
- **Filter Dinamis**: Cuaca, hari, suhu, musim, dan rentang tanggal dapat disesuaikan melalui sidebar.
- **Analisis Lanjutan**: Clustering manual dan korelasi untuk wawasan mendalam.
- **Desain Profesional**: Tema gelap dengan styling kustom untuk pengalaman pengguna yang menarik.

## Insight Utama
- **Pengaruh Cuaca**: Penyewaan tertinggi terjadi saat cuaca cerah (rata-rata > 4000), sementara hujan berat menurunkan penyewaan drastis (< 1000).
- **Pola Penggunaan**: Jam sibuk (08.00 dan 17.00-18.00) di hari kerja menunjukkan penggunaan untuk commuting, dengan pola merata di akhir pekan.
- **Tren Waktu**: Moving average (7 hari) mengindikasikan pola musiman yang dapat digunakan untuk perencanaan jangka panjang.

## Cara Deployment ke Streamlit Cloud
1. Buat akun di [Streamlit Community Cloud](https://streamlit.io/cloud).
2. Buat repository GitHub baru atau gunakan yang sudah ada (https://github.com/mocitaz/Submission-Analisis-Data-Dengan-Python).
3. Hubungkan repository ke Streamlit Cloud, tentukan `dashboard/dashboard.py` sebagai file utama.
4. Deploy aplikasi dan salin URL yang dihasilkan ke file `url.txt`.

## Kontributor
- **Pengembang**: [Nama Anda]  
- **Email**: [Email Anda, opsional]  
- **LinkedIn**: [Link LinkedIn, opsional]  

## Lisensi
Proyek ini bersifat open-source dan dapat digunakan untuk tujuan pembelajaran. Dataset berasal dari Kaggle dan digunakan sesuai ketentuan lisensi mereka.

## Catatan Tambahan
- Pastikan semua file dataset (`day.csv`, `hour.csv`) ada di folder `data/` sebelum menjalankan notebook atau dashboard.
- Perbarui `url.txt` setelah deployment untuk mencerminkan tautan aktif dashboard online.
- Untuk submission, kompres folder `ANALISIS DATA DENGAN PYTHON` menjadi file ZIP.
