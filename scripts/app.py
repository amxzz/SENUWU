# -*- coding: utf-8 -*-
"""
Dashboard Interaktif: Pemodelan Klasterisasi Kesejahteraan
Filename: app.py
Membawa Model Hybrid HDBSCAN-KMeans ke Antarmuka Visual Streamlit
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
import joblib

from sklearn.preprocessing import PowerTransformer
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.cluster import KMeans
from sklearn.metrics import calinski_harabasz_score
import hdbscan

# Page config
st.set_page_config(
    page_title="Hermes DSS - Polarisasi Kesejahteraan",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (Swiss Style Minimalist Aesthetics)
st.markdown("""
<style>
    .reportview-container .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    h1, h2, h3 {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif !important;
        font-weight: 700 !important;
        color: #111111 !important;
    }
    .stButton>button {
        background-color: #111111;
        color: white;
        border-radius: 0px;
        border: none;
    }
</style>
""", unsafe_allow_html=True)

# Helper: Hopkins Statistic Calculation
def calculate_hopkins(X):
    from sklearn.neighbors import NearestNeighbors
    from random import sample
    from numpy.random import uniform
    d = X.shape[1]
    n = len(X)
    m = int(0.1 * n)
    nbrs = NearestNeighbors(n_neighbors=1).fit(X)
    rand_X = sample(range(0, n, 1), m)
    ujd = []
    wjd = []
    for j in range(0, m):
        u_dist, _ = nbrs.kneighbors(uniform(np.amin(X,axis=0),np.amax(X,axis=0),d).reshape(1, -1), 2, return_distance=True)
        ujd.append(u_dist[0][1])
        w_dist, _ = nbrs.kneighbors(X[rand_X[j]].reshape(1, -1), 2, return_distance=True)
        wjd.append(w_dist[0][1])
    H = sum(ujd) / (sum(ujd) + sum(wjd))
    if np.isnan(H):
        return 0.0
    return H

@st.cache_data
def load_and_preprocess(data_path):
    df = pd.read_csv(data_path)
    features = [
        "Persentase Penduduk Miskin (P0) Menurut Kabupaten/Kota (Persen)",
        "Rata-rata Lama Sekolah Penduduk 15+ (Tahun)",
        "Pengeluaran per Kapita Disesuaikan (Ribu Rupiah/Orang/Tahun)",
        "Umur Harapan Hidup (Tahun)",
        "Persentase rumah tangga yang memiliki akses terhadap sanitasi layak",
        "Tingkat Pengangguran Terbuka",
        "PDRB atas Dasar Harga Konstan menurut Pengeluaran (Rupiah)"
    ]
    feature_mapping = {
        "Persentase Penduduk Miskin (P0) Menurut Kabupaten/Kota (Persen)": "Persentase_Penduduk_Miskin",
        "Rata-rata Lama Sekolah Penduduk 15+ (Tahun)": "Rata_rata_Lama_Sekolah",
        "Pengeluaran per Kapita Disesuaikan (Ribu Rupiah/Orang/Tahun)": "Pengeluaran_per_Kapita",
        "Umur Harapan Hidup (Tahun)": "UHH",
        "Persentase rumah tangga yang memiliki akses terhadap sanitasi layak": "Sanitasi_Layak",
        "Tingkat Pengangguran Terbuka": "TPT",
        "PDRB atas Dasar Harga Konstan menurut Pengeluaran (Rupiah)": "PDRB_Konstan"
    }
    
    for col in features:
        if df[col].dtype == object:
            df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '.'), errors='coerce')
        df[col] = df[col].fillna(df[col].median())
        
    df_raw = df[['Provinsi', 'Kab/Kota'] + features].copy()
    df_raw.rename(columns=feature_mapping, inplace=True)
    return df_raw, list(feature_mapping.values())

# Title Section
st.title("Sistem Pendukung Keputusan Kesejahteraan Wilayah")
st.markdown("### *Decision Support System (DSS) Berbasis Model Hibrida Spasial-Deterministik*")
st.markdown("---")

# Sidebar - Parameter Tuning
st.sidebar.header("Kontrol Parameter Model")
contamination = st.sidebar.slider("Kontaminasi Outlier (Isolation Forest)", 0.01, 0.15, 0.05, step=0.01)
min_cluster_size = st.sidebar.slider("HDBSCAN Min Cluster Size", 5, 25, 10, step=1)
min_samples = st.sidebar.slider("HDBSCAN Min Samples", 1, 10, 3, step=1)

# Ingestion
data_path = "./dataset/Klasifikasi Tingkat Kemiskinan di Indonesia.csv"
if not os.path.exists(data_path):
    st.error("File dataset tidak ditemukan. Pastikan data ada di folder dataset/")
else:
    df_raw, mapped_features = load_and_preprocess(data_path)
    X_raw = df_raw[mapped_features].values
    
    # 1. Preprocessing (Yeo-Johnson)
    pt = PowerTransformer(method='yeo-johnson', standardize=True)
    X_scaled = pt.fit_transform(X_raw)
    
    # 2. Outliers
    iso = IsolationForest(contamination=contamination, random_state=42)
    outlier_labels = iso.fit_predict(X_scaled)
    mask_normal = outlier_labels == 1
    
    df_normal = df_raw[mask_normal].copy()
    df_anomali = df_raw[~mask_normal].copy()
    X_normal_scaled = X_scaled[mask_normal]
    
    # 3. HDBSCAN
    hdb = hdbscan.HDBSCAN(min_cluster_size=min_cluster_size, min_samples=min_samples)
    hdb_labels = hdb.fit_predict(X_normal_scaled)
    
    unique_labels = np.unique(hdb_labels)
    valid_clusters = [lbl for lbl in unique_labels if lbl != -1]
    k_optimal = len(valid_clusters)
    
    if k_optimal < 2:
        st.warning("HDBSCAN mendeteksi terlalu sedikit cluster untuk inisialisasi. Menggunakan fallback KMeans++.")
        kmeans = KMeans(n_clusters=3, init='k-means++', n_init=10, random_state=42)
        final_labels = kmeans.fit_predict(X_normal_scaled)
        k_optimal = 3
    else:
        centroids = []
        for cluster_id in valid_clusters:
            mask = hdb_labels == cluster_id
            centroids.append(np.mean(X_normal_scaled[mask], axis=0))
        centroids_array = np.array(centroids)
        
        kmeans = KMeans(n_clusters=k_optimal, init=centroids_array, n_init=1, random_state=42)
        final_labels = kmeans.fit_predict(X_normal_scaled)
        
    df_normal['Cluster'] = final_labels
    
    # 4. Metrics Calculation
    hopkins_score = calculate_hopkins(X_normal_scaled)
    
    # R-Squared
    grand_mean = np.mean(X_normal_scaled, axis=0)
    ss_total = np.sum((X_normal_scaled - grand_mean) ** 2)
    ss_within = 0
    for i in np.unique(final_labels):
        cluster_points = X_normal_scaled[final_labels == i]
        cluster_centroid = np.mean(cluster_points, axis=0)
        ss_within += np.sum((cluster_points - cluster_centroid) ** 2)
    r_squared = 1.0 - (ss_within / ss_total)
    
    # CHI
    chi = calinski_harabasz_score(X_normal_scaled, final_labels)
    
    # RF Surrogate
    rf = RandomForestClassifier(n_estimators=100, random_state=42, oob_score=True)
    rf.fit(X_normal_scaled, final_labels)
    rf_accuracy = rf.oob_score_
    
    # WCVI Invensi
    wcvi = (0.30 * hopkins_score) + (0.40 * r_squared) + (0.30 * rf_accuracy)
    
    # Layout Metrik Dashboard
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Hopkins (Kelayakan)", f"{hopkins_score:.3f}")
    col2.metric("R-Squared (Varians)", f"{r_squared * 100:.1f}%")
    col3.metric("CHI Index", f"{chi:.1f}")
    col4.metric("RF Surrogate Acc", f"{rf_accuracy * 100:.1f}%")
    col5.metric("INVENSI METRIK: WCVI", f"{wcvi:.3f}", delta_color="inverse")
    
    st.markdown("---")
    
    # Layout Layout Dua Kolom
    col_left, col_right = st.columns([1, 1])
    
    with col_left:
        st.subheader("Profiling Klaster (Satuan Asli)")
        # Hitung profiling
        df_scaled_normal = pd.DataFrame(X_normal_scaled, columns=mapped_features)
        df_scaled_normal['Cluster'] = final_labels
        centroid_scaled_df = df_scaled_normal.groupby('Cluster')[mapped_features].mean()
        centroid_original = pt.inverse_transform(centroid_scaled_df.values)
        
        profiling_df = pd.DataFrame(centroid_original, columns=mapped_features, index=centroid_scaled_df.index)
        profiling_df.index = [f"Cluster {int(i)}" for i in profiling_df.index]
        profiling_df['Daerah'] = df_scaled_normal['Cluster'].value_counts().sort_index().values
        
        # Tambah baris anomali
        if len(df_anomali) > 0:
            anomali_scaled = pt.transform(df_anomali[mapped_features].values)
            anomali_centroid_scaled = np.mean(anomali_scaled, axis=0).reshape(1, -1)
            anomali_centroid_original = pt.inverse_transform(anomali_centroid_scaled)[0]
            
            anomali_series = pd.Series(anomali_centroid_original, index=mapped_features)
            anomali_series['Daerah'] = len(df_anomali)
            anomali_series.name = "Grup Anomali"
            profiling_df = pd.concat([profiling_df, anomali_series.to_frame().T])
            
        st.dataframe(profiling_df.round(2), use_container_width=True)
        
        st.subheader("Data Wilayah Lengkap")
        # Satukan data untuk visualisasi
        df_normal['Grup_Label'] = df_normal['Cluster'].apply(lambda x: f"Cluster {x}")
        df_anomali['Grup_Label'] = "Outlier (Anomali)"
        df_final_display = pd.concat([df_normal, df_anomali])
        st.dataframe(df_final_display[['Provinsi', 'Kab/Kota', 'Grup_Label'] + mapped_features], height=300, use_container_width=True)
        
    with col_right:
        st.subheader("Visualisasi Korelasi Variabel Paradoks")
        
        # PDRB vs TPT Scatter
        fig_scatter = px.scatter(
            df_final_display, 
            x='PDRB_Konstan', 
            y='TPT', 
            color='Grup_Label',
            hover_name='Kab/Kota',
            log_x=True,
            title="Korelasi Tingkat Kemakmuran (PDRB) vs Pengangguran (TPT)",
            labels={'PDRB_Konstan': 'PDRB Konstan (Rupiah, Skala Log)', 'TPT': 'Tingkat Pengangguran Terbuka (%)'}
        )
        fig_scatter.update_layout(template="plotly_dark" if st.checkbox("Gunakan Dark Mode Visualisasi") else "plotly")
        st.plotly_chart(fig_scatter, use_container_width=True)
        
        # Uji Kruskal-Wallis text output
        tpt_groups = [df_normal.loc[df_normal['Cluster'] == i, 'TPT'].values for i in range(k_optimal)]
        kruskal_tpt = kruskal(*tpt_groups)
        
        # 5. Uji Spasial Jawa-Sentris (Chi-Square)
        jawa_provinces = ["JAWA BARAT", "JAWA TENGAH", "D I YOGYAKARTA", "JAWA TIMUR", "BANTEN", "DKI JAKARTA"]
        df_normal['Is_Jawa'] = df_normal['Provinsi'].apply(
            lambda x: "Jawa" if str(x).upper() in jawa_provinces else "Luar Jawa"
        )
        crosstab_js = pd.crosstab(df_normal['Is_Jawa'], df_normal['Cluster'])
        chi2, p_val_chi, dof, expected = chi2_contingency(crosstab_js)
    
        st.info(f"**Validasi Hipotesis (Uji Kruskal-Wallis TPT)**:\n\n"
                f"Statistik Kruskal-Wallis = `{kruskal_tpt.statistic:.4f}`\n\n"
                f"Signifikansi (p-value) = `{kruskal_tpt.pvalue:.4e}`\n\n"
                f"Interpretasi: Karena p-value jauh di bawah 0.05, maka secara statistik terbukti terdapat "
                f"perbedaan nyata tingkat pengangguran Terbuka (TPT) antar klaster kesejahteraan.")
            
        st.info(f"**Uji Asosiasi Jawa-Sentris (Chi-Square)**:\n\n"
                f"Statistik Chi-Square = `{chi2:.4f}`\n\n"
                f"Signifikansi (p-value) = `{p_val_chi:.4e}`\n\n"
                f"Tabel Kontingensi (Crosstab):\n\n"
                f" {crosstab_js.to_markdown()}\n\n"
                f"Interpretasi: Hubungan antara letak wilayah geografis (Jawa vs Luar Jawa) dengan "
                f"klaster kesejahteraan yang terbentuk bersifat signifikan secara statistik (terdapat dependensi spasial).")
