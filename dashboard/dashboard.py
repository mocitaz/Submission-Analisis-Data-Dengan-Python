# Import library yang diperlukan untuk analisis dan visualisasi
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np

# --- KONFIGURASI HALAMAN ---
# Mengatur tampilan dashboard agar profesional dan responsif
st.set_page_config(
    page_title="Bike Sharing Advanced Analytics Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🚴‍♂️"
)

# --- CSS KUSTOM ---
# Menambahkan styling untuk estetika dan keterbacaan
st.markdown("""
    <style>
    .main-title { font-size: 38px; color: #1f77b4; font-weight: bold; text-align: center; margin-bottom: 10px; }
    .subheader { font-size: 26px; color: #ff7f0e; font-weight: bold; margin-top: 20px; }
    .metric-box { background-color: #f0f2f6; padding: 15px; border-radius: 8px; text-align: center; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); }
    .footer { font-size: 12px; color: #888888; text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #e6e6e6; }
    .warning { color: #d62728; font-weight: bold; font-size: 16px; }
    .bio-box { background-color: #f9f9f9; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

# --- HEADER DAN BIO ---
# Bagian header dengan deskripsi tugas
st.markdown('<div class="main-title">🚴‍♂️ Bike Sharing Advanced Analytics Dashboard</div>', unsafe_allow_html=True)
st.markdown("""
<div class="bio-box">
    <h3>Tentang Proyek Ini</h3>
    <p>Dashboard ini merupakan bagian dari proyek akhir kursus <b>Analisis Data dengan Python</b> yang diselenggarakan oleh Dicoding pada Maret 2025. Tujuannya adalah untuk menganalisis pola penyewaan sepeda dari <b>Bike Sharing Dataset</b> (sumber: Kaggle) guna mendukung pengambilan keputusan strategis dalam pengelolaan sistem penyewaan sepeda di Washington D.C. Proyek ini mencakup:</p>
    <ul>
        <li><b>Pertanyaan Bisnis</b>: Mengevaluasi pengaruh cuaca terhadap penyewaan dan mengidentifikasi pola penggunaan berdasarkan hari serta jam.</li>
        <li><b>Data Wrangling</b>: Membersihkan dan mentransformasi data untuk analisis.</li>
        <li><b>Visualisasi Interaktif</b>: Menyajikan wawasan melalui grafik yang kompleks dan dashboard berbasis Streamlit.</li>
        <li><b>Analisis Lanjutan</b>: Menggunakan teknik seperti clustering manual dan korelasi untuk eksplorasi mendalam.</li>
    </ul>
    <p>Dibuat oleh: <b>[Luthfi Fauzi]</b> | Tanggal Penyelesaian: Maret 2025</p>
</div>
""", unsafe_allow_html=True)

# --- LOAD DATA ---
# Fungsi untuk memuat data dengan caching dan penanganan error
@st.cache_data
def load_data(file_path):
    """Memuat data dari file CSV dengan caching untuk performa."""
    try:
        data = pd.read_csv(file_path)
        data['dteday'] = pd.to_datetime(data['dteday'])  # Memastikan kolom tanggal dalam format datetime
        return data
    except Exception as e:
        st.error(f"Gagal memuat {file_path}: {e}")
        return None

# Memuat data harian dan per jam
day_data = load_data("dashboard/main_data.csv")
hour_data = load_data("data/hour.csv")

# Hentikan eksekusi jika data gagal dimuat
if day_data is None or hour_data is None:
    st.stop()

# --- SIDEBAR ---
# Panel kontrol untuk filter interaktif
st.sidebar.header("🔧 Kontrol Analisis")
st.sidebar.markdown("Sesuaikan parameter untuk mengeksplorasi data:")

# Filter cuaca dengan checkbox tambahan untuk memilih semua
select_all_weather = st.sidebar.checkbox("Pilih Semua Cuaca", value=True)
weather_options = st.sidebar.multiselect(
    "Kondisi Cuaca",
    options=day_data['weathersit'].unique(),
    default=day_data['weathersit'].unique() if select_all_weather else [],
    help="Filter berdasarkan kondisi cuaca."
)

# Filter hari dengan checkbox tambahan
select_all_days = st.sidebar.checkbox("Pilih Semua Hari", value=True)
day_options = st.sidebar.multiselect(
    "Hari",
    options=day_data['weekday_name'].unique(),
    default=day_data['weekday_name'].unique() if select_all_days else [],
    help="Filter berdasarkan hari dalam seminggu."
)

# Filter rentang suhu dengan slider
temp_min, temp_max = float(day_data['temp_celsius'].min()), float(day_data['temp_celsius'].max())
temp_range = st.sidebar.slider(
    "Rentang Suhu (°C)",
    min_value=temp_min,
    max_value=temp_max,
    value=(temp_min, temp_max),
    step=0.5,
    help="Atur rentang suhu untuk analisis."
)

# Filter musim
season_options = st.sidebar.multiselect(
    "Musim",
    options=day_data['season_name'].unique(),
    default=day_data['season_name'].unique(),
    help="Filter berdasarkan musim."
)

# Filter rentang tanggal
date_min, date_max = day_data['dteday'].min(), day_data['dteday'].max()
date_range = st.sidebar.date_input(
    "Rentang Tanggal",
    value=(date_min, date_max),
    min_value=date_min,
    max_value=date_max,
    help="Pilih periode analisis."
)

# Tombol reset filter
if st.sidebar.button("Reset Semua Filter"):
    weather_options = day_data['weathersit'].unique().tolist()
    day_options = day_data['weekday_name'].unique().tolist()
    temp_range = (temp_min, temp_max)
    season_options = day_data['season_name'].unique().tolist()
    date_range = (date_min, date_max)

# --- FILTER DATA ---
# Menerapkan filter ke data harian
filtered_day_data = day_data[
    (day_data['weathersit'].isin(weather_options)) &
    (day_data['weekday_name'].isin(day_options)) &
    (day_data['temp_celsius'].between(temp_range[0], temp_range[1])) &
    (day_data['season_name'].isin(season_options)) &
    (day_data['dteday'].between(pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])))
]

# Filter data per jam
hour_filtered = hour_data[
    (hour_data['weathersit'].map({1: 'Cerah', 2: 'Berawan', 3: 'Hujan Ringan', 4: 'Hujan Berat'}).isin(weather_options)) &
    (hour_data['dteday'].between(pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])))
]

# Tampilkan jumlah data yang difilter untuk debugging
st.sidebar.markdown(f"**Data Harian Terfilter:** {len(filtered_day_data)} baris")
st.sidebar.markdown(f"**Data Per Jam Terfilter:** {len(hour_filtered)} baris")

# --- METRIK KUNCI ---
st.markdown('<div class="subheader">📊 Ringkasan Statistik</div>', unsafe_allow_html=True)
if len(filtered_day_data) == 0:
    st.markdown('<p class="warning">Tidak ada data yang sesuai dengan filter. Silakan sesuaikan filter di sidebar.</p>', unsafe_allow_html=True)
else:
    col_metrics = st.columns(4)
    with col_metrics[0]:
        st.markdown('<div class="metric-box">', unsafe_allow_html=True)
        st.metric("Total Penyewaan", f"{filtered_day_data['cnt'].sum():,.0f}")
        st.markdown('</div>', unsafe_allow_html=True)
    with col_metrics[1]:
        st.markdown('<div class="metric-box">', unsafe_allow_html=True)
        st.metric("Rata-rata Harian", f"{filtered_day_data['cnt'].mean():,.0f}")
        st.markdown('</div>', unsafe_allow_html=True)
    with col_metrics[2]:
        st.markdown('<div class="metric-box">', unsafe_allow_html=True)
        st.metric("Penyewaan Maksimum", f"{filtered_day_data['cnt'].max():,.0f}")
        st.markdown('</div>', unsafe_allow_html=True)
    with col_metrics[3]:
        st.markdown('<div class="metric-box">', unsafe_allow_html=True)
        st.metric("Hari Aktif", f"{len(filtered_day_data)}")
        st.markdown('</div>', unsafe_allow_html=True)

# --- VISUALISASI 1: BAR PLOT CUACA ---
st.markdown('<div class="subheader">📊 Analisis Pengaruh Cuaca</div>', unsafe_allow_html=True)
st.markdown("Bar plot ini menunjukkan rata-rata penyewaan sepeda berdasarkan kondisi cuaca, lengkap dengan variabilitas (error bars) dan jumlah hari.")
if len(filtered_day_data) > 0:
    weather_stats = filtered_day_data.groupby('weathersit')['cnt'].agg(['mean', 'std', 'count']).reset_index()
    fig1 = go.Figure(data=[
        go.Bar(
            x=weather_stats['weathersit'],
            y=weather_stats['mean'],
            text=weather_stats['mean'].round().astype(int),
            textposition='outside',
            marker_color=px.colors.qualitative.Bold,
            error_y=dict(type='data', array=weather_stats['std'], visible=True, color='gray'),
            hovertemplate="Cuaca: %{x}<br>Rata-rata: %{y:.0f}<br>Jumlah Hari: %{customdata}<extra></extra>",
            customdata=weather_stats['count']
        )
    ])
    fig1.update_layout(
        title="Rata-rata Penyewaan per Kondisi Cuaca",
        xaxis_title="Kondisi Cuaca",
        yaxis_title="Jumlah Penyewaan (Rata-rata)",
        template="plotly_dark",
        height=500,
        bargap=0.2,
        font=dict(family="Arial", size=12, color="white")
    )
    st.plotly_chart(fig1, use_container_width=True)
    with st.expander("Tabel Data Cuaca"):
        st.dataframe(weather_stats.style.format({"mean": "{:.0f}", "std": "{:.2f}", "count": "{:.0f}"}))
else:
    st.markdown('<p class="warning">Tidak ada data untuk visualisasi cuaca.</p>', unsafe_allow_html=True)

# --- VISUALISASI 2: BOX PLOT HARIAN ---
st.markdown('<div class="subheader">📈 Distribusi Penyewaan Harian</div>', unsafe_allow_html=True)
st.markdown("Box plot ini menggambarkan distribusi penyewaan sepeda per hari, menampilkan median, kuartil, dan outlier.")
if len(filtered_day_data) > 0:
    fig2 = px.box(
        filtered_day_data,
        x='weekday_name',
        y='cnt',
        color='weekday_name',
        title="Distribusi Penyewaan per Hari",
        labels={'cnt': 'Jumlah Penyewaan', 'weekday_name': 'Hari'},
        category_orders={"weekday_name": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]},
        points="outliers",
        color_discrete_sequence=px.colors.qualitative.Set1
    )
    fig2.update_traces(marker=dict(size=5), opacity=0.8)
    fig2.update_layout(
        template="plotly_dark",
        height=500,
        showlegend=False,
        font=dict(family="Arial", size=12, color="white")
    )
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.markdown('<p class="warning">Tidak ada data untuk visualisasi harian.</p>', unsafe_allow_html=True)

# --- VISUALISASI 3: SCATTER PLOT 3D ---
st.markdown('<div class="subheader">🌡️ Analisis Multidimensi: Suhu, Kelembapan, dan Penyewaan</div>', unsafe_allow_html=True)
st.markdown("Scatter plot 3D ini mengeksplorasi hubungan antara suhu, kelembapan, dan jumlah penyewaan, dengan warna berdasarkan musim dan ukuran titik berdasarkan volume penyewaan.")
if len(filtered_day_data) > 0:
    fig3 = px.scatter_3d(
        filtered_day_data,
        x='temp_celsius',
        y='hum',
        z='cnt',
        color='season_name',
        size='cnt',
        hover_data=['dteday', 'weathersit'],
        title="Penyewaan Sepeda: Suhu vs Kelembapan vs Jumlah",
        labels={
            'temp_celsius': 'Suhu (°C)',
            'hum': 'Kelembapan (%)',
            'cnt': 'Jumlah Penyewaan',
            'season_name': 'Musim'
        },
        color_discrete_sequence=px.colors.qualitative.Vivid
    )
    fig3.update_layout(
        template="plotly_dark",
        height=600,
        scene=dict(
            xaxis_title="Suhu (°C)",
            yaxis_title="Kelembapan (%)",
            zaxis_title="Jumlah Penyewaan",
            aspectmode='cube'
        ),
        font=dict(family="Arial", size=12, color="white")
    )
    st.plotly_chart(fig3, use_container_width=True)
else:
    st.markdown('<p class="warning">Tidak ada data untuk visualisasi 3D.</p>', unsafe_allow_html=True)

# --- VISUALISASI 4: HEATMAP KORELASI ---
st.markdown('<div class="subheader">🔗 Matriks Korelasi Faktor Lingkungan</div>', unsafe_allow_html=True)
st.markdown("Heatmap ini menampilkan korelasi antara suhu, kelembapan, kecepatan angin, dan jumlah penyewaan untuk memahami hubungan antar-variabel.")
if len(filtered_day_data) > 0:
    corr_matrix = filtered_day_data[['temp_celsius', 'hum', 'windspeed', 'cnt']].corr()
    fig4, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(
        corr_matrix,
        annot=True,
        cmap='RdBu_r',
        vmin=-1,
        vmax=1,
        center=0,
        square=True,
        linewidths=0.5,
        annot_kws={"size": 12},
        ax=ax
    )
    plt.title("Korelasi Faktor Lingkungan vs Penyewaan", fontsize=14, pad=20)
    st.pyplot(fig4)
else:
    st.markdown('<p class="warning">Tidak ada data untuk heatmap korelasi.</p>', unsafe_allow_html=True)

# --- VISUALISASI 5: HEATMAP POLA JAM ---
st.markdown('<div class="subheader">⏰ Pola Penyewaan Per Jam</div>', unsafe_allow_html=True)
st.markdown("Heatmap ini menggambarkan rata-rata penyewaan sepeda per jam dan hari dalam seminggu, berdasarkan data per jam.")
if len(hour_filtered) > 0:
    pivot_table = hour_filtered.pivot_table(values='cnt', index='hr', columns='weekday', aggfunc='mean')
    fig5, ax = plt.subplots(figsize=(12, 8))
    sns.heatmap(
        pivot_table,
        cmap='viridis',
        annot=True,
        fmt='.0f',
        linewidths=0.5,
        cbar_kws={'label': 'Jumlah Penyewaan'},
        ax=ax
    )
    plt.title("Rata-rata Penyewaan per Jam dan Hari", fontsize=14, pad=20)
    plt.xlabel("Hari (0 = Minggu, 6 = Sabtu)", fontsize=12)
    plt.ylabel("Jam (0-23)", fontsize=12)
    st.pyplot(fig5)
else:
    st.markdown('<p class="warning">Tidak ada data untuk heatmap pola jam.</p>', unsafe_allow_html=True)

# --- VISUALISASI 6: LINE PLOT TREN WAKTU ---
st.markdown('<div class="subheader">📅 Tren Penyewaan Harian</div>', unsafe_allow_html=True)
st.markdown("Line plot ini menunjukkan tren penyewaan sepeda dari waktu ke waktu, dengan garis rata-rata bergerak untuk melihat pola musiman.")
if len(filtered_day_data) > 0:
    fig6 = go.Figure()
    fig6.add_trace(go.Scatter(
        x=filtered_day_data['dteday'],
        y=filtered_day_data['cnt'],
        mode='lines+markers',
        name='Penyewaan Harian',
        line=dict(color='#1f77b4'),
        marker=dict(size=4)
    ))
    # Menambahkan moving average (7 hari)
    filtered_day_data['moving_avg'] = filtered_day_data['cnt'].rolling(window=7, min_periods=1).mean()
    fig6.add_trace(go.Scatter(
        x=filtered_day_data['dteday'],
        y=filtered_day_data['moving_avg'],
        mode='lines',
        name='Rata-rata Bergerak (7 Hari)',
        line=dict(color='#ff7f0e', dash='dash')
    ))
    fig6.update_layout(
        title="Tren Penyewaan Harian",
        xaxis_title="Tanggal",
        yaxis_title="Jumlah Penyewaan",
        template="plotly_dark",
        height=500,
        font=dict(family="Arial", size=12, color="white")
    )
    st.plotly_chart(fig6, use_container_width=True)
else:
    st.markdown('<p class="warning">Tidak ada data untuk tren waktu.</p>', unsafe_allow_html=True)

# --- FOOTER ---
st.markdown("""
<div class="footer">
    Dibuat oleh <b>[Luthfi Fauzi]</b> | Sumber Data: <a href="https://www.kaggle.com/datasets/lakshmi25npathi/bike-sharing-dataset" target="_blank">Bike Sharing Dataset (Kaggle)</a> | Tanggal: Maret 2025  
    Powered by <a href="https://streamlit.io" target="_blank">Streamlit</a> & <a href="https://plotly.com" target="_blank">Plotly</a>
</div>
""", unsafe_allow_html=True)