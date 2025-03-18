import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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

# Memuat data dari file 'main_data.csv'
maindata = load_data("main_data.csv")

# Hentikan eksekusi jika data gagal dimuat
if maindata is None:
    st.stop()

# --- PREPROCESSING DATA ---
# Mempetakan kategori cuaca berdasarkan data yang sudah diberikan
# (Menggunakan data yang ada: "Cerah", "Berawan", "Hujan Ringan", "Hujan Berat")
maindata['weathersit'] = maindata['weathersit'].fillna('Unknown')

# Menambahkan kolom hari dalam seminggu
maindata['weekday_name'] = maindata['dteday'].dt.day_name()
maindata['weekday'] = maindata['dteday'].dt.weekday

# Normalisasi suhu ke skala Celsius
maindata['temp_celsius'] = maindata['temp'] * 41

# Clustering manual untuk analisis lanjutan
bins = [0, 2000, 4000, 6000, 8000]
labels = ['Sangat Rendah', 'Rendah', 'Sedang', 'Tinggi']
maindata['usage_category'] = pd.cut(maindata['cnt'], bins=bins, labels=labels, include_lowest=True)

# --- SIDEBAR: FILTER INTERAKTIF ---
st.sidebar.header("🔧 Filter Data")
st.sidebar.markdown("Sesuaikan parameter untuk eksplorasi data:")

# Filter cuaca
weather_options = st.sidebar.multiselect(
    "Kondisi Cuaca",
    options=maindata['weathersit'].unique(),
    default=maindata['weathersit'].unique(),
    help="Filter berdasarkan kondisi cuaca."
)

# Filter hari
day_options = st.sidebar.multiselect(
    "Hari",
    options=maindata['weekday_name'].unique(),
    default=maindata['weekday_name'].unique(),
    help="Filter berdasarkan hari dalam seminggu."
)

# Filter rentang suhu
temp_min, temp_max = float(maindata['temp_celsius'].min()), float(maindata['temp_celsius'].max())
temp_range = st.sidebar.slider(
    "Rentang Suhu (°C)",
    min_value=temp_min,
    max_value=temp_max,
    value=(temp_min, temp_max),
    step=0.5,
    help="Atur rentang suhu untuk analisis."
)

# Filter rentang tanggal
date_min, date_max = maindata['dteday'].min(), maindata['dteday'].max()
date_range = st.sidebar.date_input(
    "Rentang Tanggal",
    value=(date_min, date_max),
    min_value=date_min,
    max_value=date_max,
    help="Pilih periode analisis."
)

# --- FILTER DATA ---
# Menerapkan filter ke data
filtered_data = maindata[
    (maindata['weathersit'].isin(weather_options)) &
    (maindata['weekday_name'].isin(day_options)) &
    (maindata['temp_celsius'].between(temp_range[0], temp_range[1])) &
    (maindata['dteday'].between(pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])))
]

# Tampilkan jumlah data yang difilter
st.sidebar.markdown(f"**Data Terfilter:** {len(filtered_data)} baris")

# --- METRIK KUNCI ---
st.markdown('<div class="subheader">📊 Ringkasan Statistik</div>', unsafe_allow_html=True)
if len(filtered_data) == 0:
    st.markdown('<p class="warning">Tidak ada data yang sesuai dengan filter. Silakan sesuaikan filter di sidebar.</p>', unsafe_allow_html=True)
else:
    col_metrics = st.columns(4)
    with col_metrics[0]:
        st.markdown('<div class="metric-box">', unsafe_allow_html=True)
        st.metric("Total Penyewaan", f"{filtered_data['cnt'].sum():,.0f}")
        st.markdown('</div>', unsafe_allow_html=True)
    with col_metrics[1]:
        st.markdown('<div class="metric-box">', unsafe_allow_html=True)
        st.metric("Rata-rata Harian", f"{filtered_data['cnt'].mean():,.0f}")
        st.markdown('</div>', unsafe_allow_html=True)
    with col_metrics[2]:
        st.markdown('<div class="metric-box">', unsafe_allow_html=True)
        st.metric("Penyewaan Maksimum", f"{filtered_data['cnt'].max():,.0f}")
        st.markdown('</div>', unsafe_allow_html=True)
    with col_metrics[3]:
        st.markdown('<div class="metric-box">', unsafe_allow_html=True)
        st.metric("Hari Aktif", f"{len(filtered_data)}")
        st.markdown('</div>', unsafe_allow_html=True)

# --- VISUALISASI 1: PERTANYAAN 1 - PENGARUH CUACA ---
st.markdown('<div class="subheader">📊 Pengaruh Kondisi Cuaca terhadap Penyewaan Sepeda</div>', unsafe_allow_html=True)
if len(filtered_data) > 0:
    weather_agg = filtered_data.groupby('weathersit')['cnt'].agg(['mean', 'std', 'count']).reset_index()

    # Membuat bar plot untuk rata-rata penyewaan berdasarkan kondisi cuaca dengan error bars
    fig = go.Figure(data=[
        go.Bar(
            x=weather_agg['weathersit'],
            y=weather_agg['mean'],
            text=weather_agg['mean'].round().astype(int),
            textposition='auto',
            marker_color='steelblue',  # Menggunakan warna yang seragam untuk kategori
            error_y=dict(type='data', array=weather_agg['std'], visible=True)  # Menambahkan error bars
        )
    ])
    
    # Update layout plot
    fig.update_layout(
        title='Rata-rata Penyewaan Sepeda Berdasarkan Kondisi Cuaca',
        xaxis_title='Kondisi Cuaca',
        yaxis_title='Jumlah Penyewaan (Rata-rata)',
        template='plotly_white',
        height=500,
        bargap=0.2,
        font=dict(family='Arial', size=12)
    )
    st.plotly_chart(fig, use_container_width=True)

# --- VISUALISASI 2: PERTANYAAN 2 - POLA PENGGUNAAN SEPEDA ---
st.markdown('<div class="subheader">📊 Pola Penggunaan Sepeda Berdasarkan Jam dan Hari dalam Seminggu</div>', unsafe_allow_html=True)
# Menambahkan kolom 'hour' untuk jam di filtered_data
filtered_data['hour'] = filtered_data['dteday'].dt.hour

hourly_usage = filtered_data.groupby(['weekday_name', 'hour'])['cnt'].mean().reset_index()

# Membuat heatmap untuk visualisasi
fig2 = px.density_heatmap(hourly_usage, x="hour", y="weekday_name", z="cnt", 
                         labels={'hour': 'Jam', 'weekday_name': 'Hari dalam Seminggu', 'cnt': 'Rata-rata Penyewaan'},
                         title="Pola Penggunaan Sepeda Berdasarkan Jam dan Hari dalam Seminggu")
fig2.update_layout(template="plotly_white", height=500)
st.plotly_chart(fig2, use_container_width=True)

# --- FOOTER ---
st.markdown('<div class="footer">Data dari <a href="https://www.kaggle.com/datasets/robikscube/bike-sharing-dataset">Bike Sharing Dataset (Kaggle)</a></div>', unsafe_allow_html=True)
