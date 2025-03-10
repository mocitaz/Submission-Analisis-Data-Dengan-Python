import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Bike Sharing Analytics Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🚴‍♂️"
)

# --- CSS KUSTOM ---
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
st.markdown('<div class="main-title">🚴‍♂️ Bike Sharing Analytics Dashboard</div>', unsafe_allow_html=True)
st.markdown("""
<div class="bio-box">
    <h3>Tentang Proyek Ini</h3>
    <p>Dashboard ini merupakan bagian dari proyek akhir kursus <b>Analisis Data dengan Python</b> Dicoding, Maret 2025. Dashboard ini menganalisis <b>Bike Sharing Dataset</b> untuk menjawab dua pertanyaan bisnis utama:</p>
    <ul>
        <li><b>Pertanyaan 1:</b> Bagaimana kondisi cuaca memengaruhi penyewaan sepeda?</li>
        <li><b>Pertanyaan 2:</b> Bagaimana pola penggunaan sepeda berdasarkan hari dan jam?</li>
    </ul>
    <p>Proyek ini juga mencakup analisis lanjutan menggunakan clustering manual untuk mengelompokkan penyewaan harian.</p>
    <p>Dibuat oleh: <b>Luthfi Fauzi</b> | Email: luthfafiwork@gmail.com | ID Dicoding: mocitaz</p>
</div>
""", unsafe_allow_html=True)

# --- LOAD DATA ---
@st.cache_data
def load_data(file_path):
    """Memuat data dari file CSV dengan caching untuk performa."""
    try:
        data = pd.read_csv(file_path)
        data['dteday'] = pd.to_datetime(data['dteday'])
        return data
    except Exception as e:
        st.error(f"Gagal memuat {file_path}: {e}")
        return None

# Memuat data harian dan per jam
day_data = load_data("data/day.csv")
hour_data = load_data("data/hour.csv")

# Hentikan eksekusi jika data gagal dimuat
if day_data is None or hour_data is None:
    st.stop()

# --- PREPROCESSING DATA ---
# Mapping kategori cuaca
weather_map = {1: 'Cerah', 2: 'Berawan', 3: 'Hujan Ringan', 4: 'Hujan Berat'}
day_data['weathersit'] = day_data['weathersit'].map(weather_map)
hour_data['weathersit'] = hour_data['weathersit'].map(weather_map)

# Menambahkan kolom hari dalam seminggu
day_data['weekday_name'] = day_data['dteday'].dt.day_name()
hour_data['weekday_name'] = hour_data['dteday'].dt.day_name()
hour_data['weekday'] = hour_data['dteday'].dt.weekday

# Menambahkan kolom musiman
season_map = {1: 'Musim Dingin', 2: 'Musim Semi', 3: 'Musim Panas', 4: 'Musim Gugur'}
day_data['season_name'] = day_data['season'].map(season_map)

# Normalisasi suhu ke skala Celsius
day_data['temp_celsius'] = day_data['temp'] * 41
hour_data['temp_celsius'] = hour_data['temp'] * 41

# Clustering manual untuk analisis lanjutan
bins = [0, 2000, 4000, 6000, 8000]
labels = ['Sangat Rendah', 'Rendah', 'Sedang', 'Tinggi']
day_data['usage_category'] = pd.cut(day_data['cnt'], bins=bins, labels=labels, include_lowest=True)

# --- SIDEBAR: FILTER INTERAKTIF ---
st.sidebar.header("🔧 Filter Data")
st.sidebar.markdown("Sesuaikan parameter untuk eksplorasi data:")

# Filter cuaca
select_all_weather = st.sidebar.checkbox("Pilih Semua Cuaca", value=True)
weather_options = st.sidebar.multiselect(
    "Kondisi Cuaca",
    options=day_data['weathersit'].unique(),
    default=day_data['weathersit'].unique() if select_all_weather else [],
    help="Filter berdasarkan kondisi cuaca."
)

# Filter hari
select_all_days = st.sidebar.checkbox("Pilih Semua Hari", value=True)
day_options = st.sidebar.multiselect(
    "Hari",
    options=day_data['weekday_name'].unique(),
    default=day_data['weekday_name'].unique() if select_all_days else [],
    help="Filter berdasarkan hari dalam seminggu."
)

# Filter rentang suhu
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
    (hour_data['weathersit'].isin(weather_options)) &
    (hour_data['weekday_name'].isin(day_options)) &
    (hour_data['temp_celsius'].between(temp_range[0], temp_range[1])) &
    (hour_data['dteday'].between(pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])))
]

# Tampilkan jumlah data yang difilter
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

# --- VISUALISASI 1: PERTANYAAN 1 - PENGARUH CUACA ---
st.markdown('<div class="subheader">📊 Pengaruh Kondisi Cuaca terhadap Penyewaan Sepeda</div>', unsafe_allow_html=True)
st.markdown("Bar plot ini menunjukkan rata-rata penyewaan sepeda berdasarkan kondisi cuaca, dengan error bars untuk variabilitas.")
if len(filtered_day_data) > 0:
    weather_stats = filtered_day_data.groupby('weathersit')['cnt'].agg(['mean', 'std', 'count']).reset_index()
    fig1 = go.Figure(data=[
        go.Bar(
            x=weather_stats['weathersit'],
            y=weather_stats['mean'],
            text=weather_stats['mean'].round().astype(int),
            textposition='outside',
            marker_color=['#ff7f0e', '#1f77b4', '#2ca02c'],  # Sesuai dengan urutan: Berawan, Cerah, Hujan Ringan
            error_y=dict(type='data', array=weather_stats['std'], visible=True, color='gray'),
            hovertemplate="Cuaca: %{x}<br>Rata-rata: %{y:.0f}<br>Jumlah Hari: %{customdata}<extra></extra>",
            customdata=weather_stats['count']
        )
    ])
    fig1.update_layout(
        title="Rata-rata Penyewaan Sepeda Berdasarkan Kondisi Cuaca",
        xaxis_title="Kondisi Cuaca",
        yaxis_title="Jumlah Penyewaan (Rata-rata)",
        template="plotly_white",
        height=500,
        bargap=0.2,
        font=dict(family="Arial", size=12)
    )
    st.plotly_chart(fig1, use_container_width=True)
    with st.expander("Tabel Data Cuaca"):
        st.dataframe(weather_stats.style.format({"mean": "{:.0f}", "std": "{:.2f}", "count": "{:.0f}"}))
else:
    st.markdown('<p class="warning">Tidak ada data untuk visualisasi cuaca.</p>', unsafe_allow_html=True)

# --- VISUALISASI 2: PERTANYAAN 2 - POLA HARI DAN JAM ---
st.markdown('<div class="subheader">⏰ Pola Penggunaan Sepeda Berdasarkan Hari dan Jam</div>', unsafe_allow_html=True)
st.markdown("Heatmap ini menunjukkan rata-rata penyewaan sepeda per jam dan hari dalam seminggu.")
if len(hour_filtered) > 0:
    pivot_table = hour_filtered.pivot_table(values='cnt', index='hr', columns='weekday', aggfunc='mean')
    fig2 = px.imshow(
        pivot_table,
        labels=dict(x="Hari (0=Minggu, 6=Sabtu)", y="Jam (0-23)", color="Rata-rata Penyewaan"),
        title="Rata-rata Penyewaan Sepeda per Jam dan Hari",
        color_continuous_scale='Viridis',
        text_auto=True
    )
    fig2.update_layout(
        template="plotly_white",
        height=600,
        font=dict(family="Arial", size=12)
    )
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.markdown('<p class="warning">Tidak ada data untuk heatmap pola jam.</p>', unsafe_allow_html=True)

# --- VISUALISASI 3: ANALISIS LANJUTAN - CLUSTERING ---
st.markdown('<div class="subheader">📈 Distribusi Kategori Penggunaan Sepeda Harian</div>', unsafe_allow_html=True)
st.markdown("Histogram ini menunjukkan distribusi kategori penyewaan harian (Sangat Rendah, Rendah, Sedang, Tinggi) berdasarkan clustering manual.")
if len(filtered_day_data) > 0:
    fig3 = px.histogram(
        filtered_day_data,
        x='usage_category',
        title='Distribusi Kategori Penggunaan Sepeda Harian',
        labels={'usage_category': 'Kategori Penggunaan', 'count': 'Jumlah Hari'},
        color='usage_category',
        color_discrete_sequence=px.colors.sequential.Plasma
    )
    fig3.update_layout(
        bargap=0.1,
        template='plotly_white',
        height=500,
        font=dict(family="Arial", size=12)
    )
    st.plotly_chart(fig3, use_container_width=True)

    # Tabel distribusi kategori
    category_counts = filtered_day_data['usage_category'].value_counts()
    total_days = len(filtered_day_data)
    category_percentages = (category_counts / total_days * 100).round(2)
    category_df = pd.DataFrame({
        'Kategori': category_counts.index,
        'Jumlah Hari': category_counts.values,
        'Persentase (%)': category_percentages.values
    })
    with st.expander("Tabel Distribusi Kategori"):
        st.dataframe(category_df.style.format({"Jumlah Hari": "{:.0f}", "Persentase (%)": "{:.2f}"}))
else:
    st.markdown('<p class="warning">Tidak ada data untuk visualisasi clustering.</p>', unsafe_allow_html=True)

# --- VISUALISASI 4: KORELASI FAKTOR LINGKUNGAN ---
st.markdown('<div class="subheader">🔗 Matriks Korelasi Faktor Lingkungan</div>', unsafe_allow_html=True)
st.markdown("Heatmap ini menampilkan korelasi antara suhu, kelembapan, kecepatan angin, dan jumlah penyewaan.")
if len(filtered_day_data) > 0:
    corr_matrix = filtered_day_data[['temp_celsius', 'hum', 'windspeed', 'cnt']].corr()
    fig4, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(
        corr_matrix,
        annot=True,
        cmap='coolwarm',
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

# --- VISUALISASI 5: TREN BULANAN ---
st.markdown('<div class="subheader">📅 Tren Rata-rata Penyewaan per Bulan</div>', unsafe_allow_html=True)
st.markdown("Line plot ini menunjukkan tren rata-rata penyewaan sepeda per bulan.")
if len(filtered_day_data) > 0:
    filtered_day_data['month'] = filtered_day_data['dteday'].dt.month
    monthly_trend = filtered_day_data.groupby('month')['cnt'].mean().reset_index()
    fig5 = px.line(
        monthly_trend,
        x='month',
        y='cnt',
        title='Tren Rata-rata Penyewaan per Bulan',
        labels={'month': 'Bulan', 'cnt': 'Rata-rata Penyewaan'},
        markers=True,
        color_discrete_sequence=['#1f77b4']
    )
    fig5.update_layout(
        template="plotly_white",
        height=500,
        xaxis=dict(tickmode='linear', tick0=1, dtick=1),
        font=dict(family="Arial", size=12)
    )
    st.plotly_chart(fig5, use_container_width=True)
else:
    st.markdown('<p class="warning">Tidak ada data untuk tren bulanan.</p>', unsafe_allow_html=True)

# --- FOOTER ---
st.markdown("""
<div class="footer">
    Dibuat oleh <b>Luthfi Fauzi</b> | Email: luthfafiwork@gmail.com | ID Dicoding: mocitaz<br>
    Sumber Data: <a href="https://www.kaggle.com/datasets/lsind18/bike-sharing-dataset" target="_blank">Bike Sharing Dataset (Kaggle)</a> | Tanggal: Maret 2025<br>
    Powered by <a href="https://streamlit.io" target="_blank">Streamlit</a> & <a href="https://plotly.com" target="_blank">Plotly</a>
</div>
""", unsafe_allow_html=True)