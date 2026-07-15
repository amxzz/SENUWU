# -*- coding: utf-8 -*-
"""
Dashboard Streamlit — Sistem Pemetaan Klasterisasi Kesejahteraan HKI
=====================================================================
Versi Revamp (Plotly WebGL, No-Lag, UI Academia)
"""

import streamlit as st
import pandas as pd
import numpy as np
import os
import sys
import json
import plotly.express as px
import plotly.graph_objects as go
import folium
import streamlit.components.v1 as components

# Add components to path
sys.path.append(os.path.dirname(__file__))
from components.narrative import (
    generate_narrative, format_value,
    FEATURE_LABELS, FEATURE_EMOJI, CLUSTER_DESCRIPTIONS
)
from streamlit_option_menu import option_menu
from components.ui_primitives import ui_volume_header, ui_ornate_divider

# ============================================================
# PAGE CONFIG & GLOBAL STATE
# ============================================================
st.set_page_config(
    page_title="Sistem Kesejahteraan",
    page_icon="📜",
    layout="wide",
    initial_sidebar_state="expanded"
)

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'show_csv_error_modal' not in st.session_state:
    st.session_state.show_csv_error_modal = False
if 'csv_error_message' not in st.session_state:
    st.session_state.csv_error_message = ""
if 'show_success_modal' not in st.session_state:
    st.session_state.show_success_modal = False
if 'success_modal_message' not in st.session_state:
    st.session_state.success_modal_message = ""
if 'uploader_key' not in st.session_state:
    st.session_state.uploader_key = 0

# --- THEME INJECTION ---
current_dir = os.path.dirname(os.path.abspath(__file__))
css_path = os.path.join(current_dir, "assets", "academia_style.css")
css_content = ""
if os.path.exists(css_path):
    with open(css_path, "r", encoding="utf-8") as f:
        css_content = f.read()

# Pure Light Mode (Academia Theme)
theme_mode = "light"
theme_vars = """
:root {
    --bg-base: #E8DFD4;
    --bg-card: #F3EFE9;
    --bg-input: #F3EFE9;
    --text-primary: #1C1714;
    --text-secondary: #4A3F35;
    --text-muted: #645648;
    --border-standard: #9C8B7A;
    --accent-brass: #A68641;
    --accent-crimson: #8B2635;
    --btn-text: #1C1714;
    --btn-grad: linear-gradient(180deg, #D4B872 0%, #C9A962 50%, #B8953F 100%);
}
"""

# Inject CSS and data-theme directly to Streamlit root wrapper
st.markdown(f"""
    <style>
        {theme_vars}
        {css_content}
        .stApp {{ background-color: var(--bg-base) !important; }}
    </style>
""", unsafe_allow_html=True)

# ============================================================
# CONSTANTS
# ============================================================
FEATURE_WEIGHTS = {
    'Persentase_Penduduk_Miskin': 0.10, 'Rata_rata_Lama_Sekolah': 0.15,
    'Pengeluaran_per_Kapita': 0.10, 'UHH': 0.25, 'Sanitasi_Layak': 0.05,
    'TPT': 0.15, 'PDRB_Konstan': 0.20
}
MAPPED_FEATURES = list(FEATURE_WEIGHTS.keys())

CLUSTER_NAMES = {
    3: "Urban Maju",
    2: "Transisi Seimbang",
    0: "Sentra Industri",
    1: "Area Rentan",
    -1: "Entitas Atipikal"
}

CLUSTER_COLORS = {
    "Urban Maju": "#388E3C",         # Hijau
    "Transisi Seimbang": "#1976D2",  # Biru
    "Sentra Industri": "#F57C00",    # Jingga
    "Area Rentan": "#D32F2F",        # Merah
    "Entitas Atipikal": "#9E9E9E"    # Abu-abu
}

def compute_welfare_score(feature_values, domain_max):
    score = 0.0
    for feat in MAPPED_FEATURES:
        val = feature_values[feat]
        m_val = domain_max[feat]
        if m_val == 0: norm = 0
        else:
            if feat in ['Persentase_Penduduk_Miskin', 'TPT']:
                norm = max(0.0, min(1.0, 1.0 - (val / m_val)))
            else:
                norm = max(0.0, min(1.0, val / m_val))
        score += FEATURE_WEIGHTS[feat] * norm
    return score

# ============================================================
# LOAD DATA (CACHED)
# ============================================================
# @st.cache_data
def load_app_data():
    base_path = os.path.join(os.path.dirname(__file__), "..", "dataset")
    data = {}
    try:
        data['narrative'] = pd.read_csv(os.path.join(base_path, "processed", "narrative_data.csv"))
        data['centroid'] = pd.read_csv(os.path.join(base_path, "results", "tables", "centroid_per_cluster.csv"), index_col=0)
        data['std'] = pd.read_csv(os.path.join(base_path, "results", "tables", "std_per_cluster.csv"), index_col=0)
        data['centroid_scaled'] = pd.read_csv(os.path.join(base_path, "results", "tables", "centroid_scaled_per_cluster.csv"), index_col=0)
        data['weights'] = pd.read_csv(os.path.join(base_path, "results", "tables", "feature_weights.csv"))
        data['summary'] = pd.read_csv(os.path.join(base_path, "results", "tables", "summary_metrics.csv"))
        
        # Map old names in centroid and std indexes to the new presentation names used in Streamlit
        old_to_new = {
            "Berkembang Industrial": "Sentra Industri",
            "Berkembang Rentan": "Area Rentan",
            "Berkembang Seimbang": "Transisi Seimbang",
            "Maju & Urbanized": "Urban Maju",
            "Entitas Atipikal": "Entitas Atipikal"
        }
        data['centroid'].index = data['centroid'].index.map(lambda x: old_to_new.get(x, x))
        data['std'].index = data['std'].index.map(lambda x: old_to_new.get(x, x))
        data['centroid_scaled'].index = data['centroid_scaled'].index.map(lambda x: old_to_new.get(x, x))
        df = data['narrative']
        # Pastikan kolom Klaster dan Tahun integer
        df['Klaster'] = df['Klaster'].astype(int)
        df['Tipologi'] = df['Klaster'].map(CLUSTER_NAMES)
        df['Tahun'] = df['Tahun'].fillna(2024).astype(int)
        
        # Buat Narasi Singkat Peta (Hover Insight) menggunakan hasil statistik riset (top1_feat & z-score)
        def generate_short_insight(row):
            insight = f"Wilayah ini tergolong {row['Tipologi']}."
            top_feat = row.get('top1_feat')
            
            if pd.isna(top_feat) or not top_feat:
                return insight + " Memerlukan akselerasi pembangunan pada berbagai sektor."
                
            z_val = float(row.get(f"{top_feat}_zscore", 0))
            
            # Map top feature to descriptive Indonesian sentence
            if top_feat == 'Persentase_Penduduk_Miskin':
                if z_val > 0:
                    insight += " Kemiskinan yang masih tinggi menjadi tantangan utama pembangunan wilayah."
                else:
                    insight += " Tingkat kemiskinan yang rendah menjadi modal sosial-ekonomi yang kuat."
            elif top_feat == 'PDRB_Konstan':
                if z_val > 0:
                    insight += " Kapasitas ekonomi daerah (PDRB) sangat masif dibanding rata-rata."
                else:
                    insight += " Kapasitas ekonomi daerah masih terbatas dan perlu stimulasi investasi."
            elif top_feat == 'TPT':
                if z_val > 0:
                    insight += " Tingkat pengangguran (TPT) yang cukup tinggi perlu mendapat perhatian khusus."
                else:
                    insight += " Kondisi ketenagakerjaan sangat baik dengan tingkat pengangguran rendah."
            elif top_feat == 'UHH':
                if z_val > 0:
                    insight += " Fasilitas kesehatan sangat baik, menunjang angka harapan hidup yang tinggi."
                else:
                    insight += " Kualitas kesehatan dan layanan dasar masyarakat perlu terus ditingkatkan."
            elif top_feat == 'Rata_rata_Lama_Sekolah':
                if z_val > 0:
                    insight += " Kualitas sumber daya manusia unggul dengan rata-rata lama sekolah yang tinggi."
                else:
                    insight += " Pemerataan akses pendidikan menengah/tinggi masih menjadi tantangan."
            elif top_feat == 'Pengeluaran_per_Kapita':
                if z_val > 0:
                    insight += " Daya beli dan tingkat konsumsi masyarakat tergolong tinggi."
                else:
                    insight += " Daya beli masyarakat masih perlu didorong melalui stimulus ekonomi lokal."
            elif top_feat == 'Sanitasi_Layak':
                if z_val > 0:
                    insight += " Akses sanitasi layak masyarakat sudah sangat merata."
                else:
                    insight += " Pembangunan infrastruktur sanitasi dasar masih perlu diakselerasi."
            else:
                insight += " Memerlukan akselerasi pembangunan pada berbagai sektor."
                
            return insight
            
        df['Insight'] = df.apply(generate_short_insight, axis=1)
        
        # Siapkan kolom untuk Peta (Hover) dengan normalisasi spasial yang presisi (seperti di skrip riset pemodelan)
        import re

        def normalize_for_match(s):
            s = str(s).upper().strip()
            s = re.sub(r'\s+', ' ', s)
            s = re.sub(r'^(KABUPATEN|KAB\.?|KOTA)\s+', '', s).strip()
            return s

        PROV_MAPPING = {
            'D I YOGYAKARTA': 'YOGYAKARTA',
            'DKI JAKARTA': 'JAKARTA RAYA',
            'KEP. BANGKA BELITUNG': 'BANGKA BELITUNG',
            'KEPULAUAN RIAU': 'RIAU ISLANDS',
            'PAPUA BARAT': 'WEST PAPUA',
        }

        def normalize_prov(s):
            s = str(s).upper().strip()
            s = PROV_MAPPING.get(s, s)
            return s.title()

        df['_match_key_w'] = df['Kab/Kota'].apply(normalize_for_match)
        df['_match_key_p'] = df['Provinsi'].apply(normalize_prov)
        
        # Load GeoJSON (Use simplified version to avoid lag and memory bloat)
        geojson_path = os.path.join(base_path, "kota-kabupaten-simplified.json")
        if os.path.exists(geojson_path):
            with open(geojson_path, 'r', encoding='utf-8') as f:
                geojson = json.load(f)
                
            # Add match keys to geojson properties
            for feature in geojson['features']:
                props = feature['properties']
                if 'NAME_2' in props and props['NAME_2'] and 'NAME_1' in props and props['NAME_1']:
                    props['match_key_w'] = normalize_for_match(props['NAME_2'])
                    props['match_key_p'] = normalize_prov(props['NAME_1'])
                else:
                    props['match_key_w'] = "UNKNOWN"
                    props['match_key_p'] = "UNKNOWN"
            data['geojson'] = geojson
        
        data['loaded'] = True
    except Exception as e:
        data['loaded'] = False
        data['error'] = str(e)
    return data

data = load_app_data()

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("<h2 style='text-align:center; margin-bottom: 0;'>SENUWU</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; margin-top: 0; font-size:1.1rem; font-family: \"Cormorant Garamond\", serif;'>Sistem Informasi Analitik<br>Ketimpangan Wilayah</p>", unsafe_allow_html=True)
    ui_ornate_divider()
    
    menu = option_menu(
        menu_title=None,
        options=["Beranda", "Cari", "Update Data Baru", "Info"],
        icons=["house", "search", "cloud-arrow-up", "info-circle"],
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "var(--bg-base)"},
            "nav-link": {"font-family": "'Crimson Pro', serif", "font-size": "18px", "text-align": "left", "margin":"5px", "color": "var(--text-primary)"},
            "nav-link-selected": {"background-color": "#F3EFE9", "color": "#1C1714", "font-weight": "bold"},
        }
    )
    ui_ornate_divider()
    st.markdown("<p style='font-size:14px; text-align:center; color: var(--text-muted);'>Sistem Pemetaan v2.0</p>", unsafe_allow_html=True)

if not data['loaded']:
    st.error(f"Gagal memuat data: {data.get('error')}")
    st.stop()

df = data['narrative']

# ============================================================
# MENU 1: BERANDA
# ============================================================
if menu == "Beranda":
    # --- HERO SECTION ---
    st.markdown("""
    <div style="text-align: center; margin-bottom: 25px; margin-top: 10px;">
        <h1 style="font-family: 'Cormorant Garamond', serif; font-size: 3.2rem; font-weight: bold; color: var(--text-primary); margin-bottom: 5px; line-height: 1.2;">SENUWU</h1>
        <h3 style="font-family: 'Cinzel', serif; font-size: 1.15rem; letter-spacing: 0.15em; color: var(--accent-brass); margin-top: 0; margin-bottom: 20px; font-weight: 500;">SISTEM INFORMASI ANALITIK KETIMPANGAN WILAYAH</h3>
        <p style="font-family: 'Crimson Pro', serif; font-size: 1.15rem; color: var(--text-secondary); max-width: 950px; margin: 0 auto; line-height: 1.7; text-align: justify;">
            SENUWU (Sistem Informasi Analitik Ketimpangan Wilayah) hadir sebagai platform visualisasi interaktif untuk memetakan kesamaan tingkat kesejahteraan kabupaten dan kota di Indonesia. Dengan memanfaatkan pendekatan machine learning, sistem ini dikembangkan untuk memberikan pemahaman awal yang komprehensif bagi publik maupun pemerintah dalam mengenali karakteristik wilayah secara objektif, guna mendukung perencanaan pembangunan yang lebih terarah dan inklusif.
        </p>
    </div>
    """, unsafe_allow_html=True)
    ui_ornate_divider()

    # --- PENDEKATAN PEMODELAN ---
    st.markdown("""
    <div style="margin-top: 25px; margin-bottom: 25px;">
        <h3 style="font-family: 'Cormorant Garamond', serif; font-size: 1.8rem; font-weight: bold; color: var(--accent-brass); border-bottom: 1px solid var(--border-standard); padding-bottom: 8px; margin-bottom: 15px;">Pendekatan Pemodelan</h3>
        <p style="font-family: 'Crimson Pro', serif; font-size: 1.15rem; color: var(--text-secondary); line-height: 1.7; text-align: justify; margin-top: 0; margin-bottom: 0;">
            Sistem ini mengintegrasikan metode <b>Hybrid Clustering</b> dengan menggabungkan algoritma HDBSCAN untuk mengenali struktur kelompok alami dan memisahkan data pencilan (noise), serta algoritma K-Means untuk memastikan setiap wilayah teralokasikan secara konsisten ke dalam klaster akhir.
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div style="background: #FFFFFF; border-radius: 8px; padding: 30px; box-shadow: 0 10px 30px rgba(92, 64, 51, 0.05); font-family: 'Crimson Pro', serif; text-align: left; max-width: 100%; margin: 25px auto; display: flex; gap: 40px; align-items: center;">
        <!-- Left Column (Title & Status) -->
        <div style="flex: 0 0 35%; border-right: 1px solid #E5DDCB; padding-right: 25px;">
            <div style="font-family: 'Cinzel', serif; font-size: 0.8rem; letter-spacing: 0.15em; color: #8a620b; font-weight: bold; text-transform: uppercase; margin-bottom: 8px;">Keandalan Sistem</div>
            <h3 style="font-family: 'Cormorant Garamond', serif; font-size: 1.6rem; color: #1C1714; font-weight: bold; line-height: 1.2; margin-bottom: 12px; border-bottom: none; padding-bottom: 0;">Evaluasi Model</h3>
            <div style="font-family: 'Cormorant Garamond', serif; font-size: 1.15rem; font-weight: bold; color: #2E7D32; display: flex; align-items: center; gap: 8px;">
                <span style="font-size: 1.3rem; line-height: 1;">✦</span> Tervalidasi
            </div>
        </div>
        <!-- Right Column (Description & Metrics Inline) -->
        <div style="flex: 1;">
            <p style="font-size: 1.1rem; line-height: 1.6; color: #1C1714; margin-bottom: 15px; font-family: 'Crimson Pro', serif;">
                Untuk menjamin keandalan pemetaan, model ini dievaluasi menggunakan metrik statistika berbasis data resmi BPS tahun 2024.
            </p>
            <div style="font-family: 'Cinzel', serif; font-size: 0.85rem; font-weight: bold; color: #8a620b; display: flex; flex-wrap: wrap; align-items: center; gap: 4px;">
                <span>WCVI</span>
                <span style="color: #D4AF37; margin: 0 6px; font-size: 0.6rem; vertical-align: middle;">●</span>
                <span>Hopkins Statistic</span>
                <span style="color: #D4AF37; margin: 0 6px; font-size: 0.6rem; vertical-align: middle;">●</span>
                <span>ARI</span>
                <span style="color: #D4AF37; margin: 0 6px; font-size: 0.6rem; vertical-align: middle;">●</span>
                <span>Random Forest</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # --- VISUALISASI UTAMA (PETA) ---
    col_map_title, col_map_year = st.columns([3, 1])
    with col_map_title:
        ui_volume_header("I", "Peta Klasifikasi Wilayah Indonesia")
    with col_map_year:
        map_years = sorted(df['Tahun'].unique().tolist())
        selected_map_year = st.selectbox("Tahun Peta:", map_years, key="selected_map_year")

    st.markdown("Halaman ini menampilkan visualisasi peta Choropleth mengenai hasil pengelompokan (*clustering*) wilayah di Indonesia. "
                "Arahkan kursor (*hover*) ke area peta untuk melihat detail indikator kesejahteraan seketika.")

    if 'geojson' in data:
        # Menyiapkan data untuk Plotly
        df_map = df[df['Tahun'] == selected_map_year].copy()
        
        # Inject data directly into geojson for folium using robust two-stage matching
        for feature in data['geojson']['features']:
            props = feature['properties']
            name_w = props.get('NAME_2', '')
            prov_raw = props.get('NAME_1', '')
            
            row = pd.DataFrame()
            if name_w and prov_raw:
                key_p = props.get('match_key_p', '')
                
                # 1. Try exact match (case-insensitive)
                row = df_map[(df_map['Kab/Kota'].str.upper() == name_w.upper()) & (df_map['_match_key_p'] == key_p)]
                
                # 2. Try exact match with normalized name (strip whitespace)
                if row.empty:
                    row = df_map[(df_map['Kab/Kota'].str.upper().str.strip() == name_w.upper().strip()) & (df_map['_match_key_p'] == key_p)]
                    
                # 3. Fallback to prefix-stripped matching (e.g. for "Surabaya" in GeoJSON -> "Kota Surabaya" in dataset)
                if row.empty:
                    key_w = props.get('match_key_w', '')
                    row = df_map[(df_map['_match_key_w'] == key_w) & (df_map['_match_key_p'] == key_p)]
            
            if not row.empty:
                feature['properties']['tipologi'] = str(row['Tipologi'].values[0])
                feature['properties']['color'] = CLUSTER_COLORS.get(feature['properties']['tipologi'], '#cccccc')
                feature['properties']['kab_name'] = str(row['Kab/Kota'].values[0])
                pdrb_val = float(row['PDRB_Konstan'].values[0]) / 1000
                feature['properties']['pdrb'] = f"Rp {pdrb_val:,.1f}".replace(',', '.') + " M"
                feature['properties']['uhh'] = f"{round(float(row['UHH'].values[0]),1)} Tahun"
                feature['properties']['tpt'] = f"{round(float(row['TPT'].values[0]),2)} %"
                pengeluaran_val = float(row['Pengeluaran_per_Kapita'].values[0]) * 1000
                feature['properties']['pengeluaran'] = f"Rp {pengeluaran_val:,.0f}".replace(',', '.') + " / Thn"
                feature['properties']['rls'] = f"{round(float(row['Rata_rata_Lama_Sekolah'].values[0]),1)} Tahun"
                feature['properties']['insight_singkat'] = str(row['Insight'].values[0])
            else:
                feature['properties']['color'] = '#cccccc'
                feature['properties']['kab_name'] = name_w if name_w else "Data Tidak Tersedia"
                feature['properties']['tipologi'] = "-"
                feature['properties']['pdrb'] = "-"
                feature['properties']['uhh'] = "-"
                feature['properties']['tpt'] = "-"
                feature['properties']['pengeluaran'] = "-"
                feature['properties']['rls'] = "-"
                feature['properties']['insight_singkat'] = "-"

        m = folium.Map(location=[-2.5, 118.0], zoom_start=5, tiles="CartoDB positron")
        
        folium.GeoJson(
            data['geojson'],
            style_function=lambda feature: {
                'fillColor': feature['properties'].get('color', '#cccccc'),
                'color': '#333333',
                'weight': 0.5,
                'fillOpacity': 0.7,
            },
            tooltip=folium.GeoJsonTooltip(
                fields=['kab_name', 'tipologi', 'pdrb', 'uhh', 'tpt', 'pengeluaran', 'rls', 'insight_singkat'],
                aliases=['Wilayah:', 'Klaster:', 'PDRB Konstan:', 'UHH:', 'Pengangguran (TPT):', 'Pengeluaran/Kapita:', 'Lama Sekolah:', 'Insight:'],
                style=""
            )
        ).add_to(m)
        
        # Inject CSS theme variables into folium iframe so tooltips match theme perfectly
        map_html = f"<style>{theme_vars} {css_content}</style>" + m.get_root().render()
        components.html(map_html, height=550)
    else:
        st.warning("Data GeoJSON batas wilayah tidak ditemukan. Peta tidak dapat ditampilkan.")

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Ringkasan Klaster Cards (Dynamic 2-column grid based on available clusters)
    st.markdown("<h3 class='sub-header'><i class='bi bi-grid-fill'></i> Ringkasan Kategori Klaster</h3>", unsafe_allow_html=True)
    
    unique_clusters = sorted([int(c) for c in df['Klaster'].unique() if int(c) in CLUSTER_NAMES])
    
    CLUSTER_DESC = {
        "Urban Maju": "Daerah metropolitan dan urban dengan infrastruktur masif dan stabilitas ekonomi tinggi.",
        "Transisi Seimbang": "Fasilitas mulai membaik secara merata, pertumbuhan kelas menengah stabil.",
        "Sentra Industri": "Kawasan industri manufaktur yang menyerap banyak tenaga kerja padat karya.",
        "Area Rentan": "Memiliki tingkat kemiskinan yang masih tinggi serta infrastruktur yang tertinggal.",
        "Entitas Atipikal": "Pola anomali/outlier statistik yang unik dan tidak masuk dalam kelompok konvensional."
    }
    
    # Render 4 clusters only, excluding Entitas Atipikal
    all_clusters = [k for k in CLUSTER_NAMES.keys() if k != -1]
    
    # Render cards in rows of 2
    for i in range(0, len(all_clusters), 2):
        cols = st.columns(2)
        for j, col in enumerate(cols):
            if i + j < len(all_clusters):
                cluster_id = all_clusters[i+j]
                c_name = CLUSTER_NAMES[cluster_id]
                c_color = CLUSTER_COLORS[c_name]
                c_desc = CLUSTER_DESC.get(c_name, "")
                count = len(df[df['Klaster'] == cluster_id])
                
                col.markdown(f"""
                <div class="academia-card" style="border-top: 5px solid {c_color}; margin-bottom: 20px;">
                    <h4 style="color: {c_color}; margin-top:0; font-size:1.4rem;">{c_name}</h4>
                    <p style="flex-grow: 1;">{c_desc}</p>
                    <hr style="margin: 10px 0; border-color: var(--border-standard);">
                    <p style="font-size: 1.1rem; color: var(--text-muted); margin-bottom:0;"><b>Total Wilayah:</b> {count}</p>
                </div>
                """, unsafe_allow_html=True)

# ============================================================
# MENU 2: CARI
# ============================================================
elif menu == "Cari":
    ui_volume_header("II", "Analisis Klasifikasi Spesifik")
    st.markdown("Pilih wilayah melalui *dropdown* di bawah ini untuk melihat metrik utama dan kesimpulan analisis secara ringkas dan bersih.")
    
    def reset_kabupaten():
        if 'selected_kab' in st.session_state:
            del st.session_state['selected_kab']

    def reset_provinsi():
        if 'selected_prov' in st.session_state:
            del st.session_state['selected_prov']
        if 'selected_kab' in st.session_state:
            del st.session_state['selected_kab']

    col_tahun, col1, col2 = st.columns([1, 1.5, 1.5])
    with col_tahun:
        tahun_list = sorted(df['Tahun'].unique().tolist())
        selected_tahun = st.selectbox("Pilih Tahun:", tahun_list, key='selected_tahun', on_change=reset_provinsi)
        
    df_filtered = df[df['Tahun'] == selected_tahun]

    with col1:
        provinsi_list = sorted(df_filtered['Provinsi'].unique().tolist())
        selected_prov = st.selectbox("Pilih Provinsi:", provinsi_list, key='selected_prov', on_change=reset_kabupaten)
    with col2:
        kab_list = sorted(df_filtered[df_filtered['Provinsi'] == selected_prov]['Kab/Kota'].unique().tolist())
        selected_kab = st.selectbox("Pilih Kabupaten/Kota:", kab_list, key='selected_kab')
        
    submitted = st.button("Tampilkan Analisis", type="primary")
    if submitted:
        row = df_filtered[(df_filtered['Provinsi'] == selected_prov) & (df_filtered['Kab/Kota'] == selected_kab)]
        if not row.empty:
            row = row.iloc[0]
            klaster = int(row['Klaster'])
            tipologi = CLUSTER_NAMES[klaster]
            welfare_score = float(row['Welfare_Score'])
            
            # Fetch Centroids & Z-scores for narrative
            centroid_df = data['centroid']
            tipologi_idx = data['narrative'][data['narrative']['Klaster']==klaster]['Tipologi'].iloc[0] # Get old name for centroid lookup
            
            if tipologi_idx in centroid_df.index:
                centroid_values = {feat: float(centroid_df.loc[tipologi_idx, feat]) for feat in MAPPED_FEATURES}
            else:
                centroid_values = {feat: 0.0 for feat in MAPPED_FEATURES}
                
            feature_values = {feat: float(row[feat]) for feat in MAPPED_FEATURES}
            z_scores = {feat: float(row.get(f'{feat}_zscore', 0)) for feat in MAPPED_FEATURES}
            
            top_features = [
                (row.get('top1_feat', MAPPED_FEATURES[0]), z_scores.get(row.get('top1_feat', MAPPED_FEATURES[0]),0), FEATURE_WEIGHTS.get(row.get('top1_feat'),0)),
                (row.get('top2_feat', MAPPED_FEATURES[1]), z_scores.get(row.get('top2_feat', MAPPED_FEATURES[1]),0), FEATURE_WEIGHTS.get(row.get('top2_feat'),0)),
                (row.get('top3_feat', MAPPED_FEATURES[2]), z_scores.get(row.get('top3_feat', MAPPED_FEATURES[2]),0), FEATURE_WEIGHTS.get(row.get('top3_feat'),0)),
            ]
            
            weights_df = data['weights']
            feature_importances = dict(zip(weights_df['Feature'], weights_df['RF_Importance']))
            
            st.markdown("<hr style='border-color: #E2D9C8;'>", unsafe_allow_html=True)
            
            # Header Wilayah
            color = CLUSTER_COLORS[tipologi]
            st.markdown(f"""
            <div style="border-left: 6px solid {color}; padding-left: 15px; margin-bottom: 25px;">
                <h2 style="margin:0; font-size:28px; color:#1C1714;">{selected_kab}</h2>
                <p style="margin:0; color:#1C1714; font-size:16px;">{selected_prov} &nbsp;|&nbsp; <b>Kategori: <span style="color:{color}">{tipologi}</span></b></p>
            </div>
            """, unsafe_allow_html=True)
            
            # Metric Section Removed as Requested
            
            
            # Insight Narrative
            st.markdown("<br>", unsafe_allow_html=True)
            narrative_text = generate_narrative(
                selected_kab, selected_prov, klaster, tipologi, welfare_score,
                feature_values, centroid_values, z_scores, FEATURE_WEIGHTS,
                top_features, feature_importances
            )
            st.markdown(f"<div style='background-color: var(--bg-card); border: 1px solid var(--border-standard); border-left: 6px solid {color}; padding: 30px; margin-top: 15px; color: #1C1714; box-shadow: 0 4px 12px rgba(0,0,0,0.04); border-radius: 8px; font-size: 16px; line-height: 1.75;'>\n\n{narrative_text}\n\n</div>", unsafe_allow_html=True)


# ============================================================
# MENU 3: UPDATE DATA BARU
# ============================================================
elif menu == "Update Data Baru":
    ui_volume_header("III", "Pembaruan Data Wilayah Baru")
    st.markdown("Halaman ini berfungsi untuk menambahkan baris data wilayah baru ke dalam sistem klasifikasi. Data baru diproses menggunakan *Pre-Trained Model* agar stabilitas klasifikasi peta utama tetap terjaga.")
    
    # CSS Custom for Glassmorphism Modals
    st.markdown("""
<style>
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background-color: rgba(0, 0, 0, 0.25) !important;
    backdrop-filter: blur(12px) !important;
    -webkit-backdrop-filter: blur(12px) !important;
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 99999;
}
.modal-container {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 90%;
    max-width: 480px;
    height: 320px !important;
    background: #FFFFFF !important;
    border-radius: 8px !important;
    padding: 35px 25px 25px 25px;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15) !important;
    text-align: center;
    font-family: 'Crimson Pro', serif;
    z-index: 100000;
    box-sizing: border-box;
}
.modal-warning {
    background: #FFEBEE !important;
    border: 1px solid rgba(211, 47, 47, 0.3) !important;
    color: #1C1714 !important;
}
.modal-success {
    background: #E8F5E9 !important;
    border: 1px solid rgba(46, 125, 50, 0.3) !important;
    color: #1C1714 !important;
}
.modal-icon-wrap {
    width: 48px;
    height: 48px;
    border-radius: 50%;
    margin: 0 auto 15px auto;
    display: flex;
    justify-content: center;
    align-items: center;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
}
.modal-warning .modal-icon-wrap {
    background: #FFCDD2 !important;
    border: 1.5px solid #EF9A9A !important;
}
.modal-success .modal-icon-wrap {
    background: #C8E6C9 !important;
    border: 1.5px solid #81C784 !important;
}
.modal-icon {
    font-size: 1.5rem;
    font-weight: bold;
    line-height: 1.0;
}
.modal-warning .modal-icon {
    color: #C62828 !important;
}
.modal-success .modal-icon {
    color: #2E7D32 !important;
}
.modal-title {
    font-family: 'Cinzel', serif;
    font-size: 1.15rem;
    font-weight: bold;
    margin-bottom: 12px;
    letter-spacing: 0.05em;
}
.modal-warning .modal-title {
    color: #C62828 !important;
}
.modal-success .modal-title {
    color: #2E7D32 !important;
}
.modal-desc {
    font-size: 1.05rem;
    line-height: 1.6;
    margin-bottom: 15px;
    max-height: 110px !important;
    overflow-y: auto !important;
    color: #4A3F35 !important;
}
.modal-divider {
    border: 0;
    border-top: 1px solid rgba(156, 139, 122, 0.2);
    margin-bottom: 20px;
}

/* Close button X positioning */
div:has(.modal-close-x-marker) + div {
    position: fixed !important;
    top: calc(50% - 135px) !important;
    left: calc(50% + 215px) !important;
    transform: translate(-50%, -50%) !important;
    z-index: 100001 !important;
}
div:has(.modal-close-x-marker) + div button {
    background: transparent !important;
    border: none !important;
    color: #645648 !important;
    font-size: 1.6rem !important;
    font-weight: normal !important;
    padding: 0 !important;
    margin: 0 !important;
    min-height: auto !important;
    width: auto !important;
    box-shadow: none !important;
    cursor: pointer;
    display: inline-block !important;
    line-height: 1 !important;
    transition: color 0.2s ease !important;
}
div:has(.modal-close-x-marker) + div button:hover {
    color: #1C1714 !important;
}

/* Main action buttons positioning and styling */
div:has(.modal-btn-marker) + div {
    position: fixed !important;
    top: calc(50% + 115px) !important;
    left: 50% !important;
    transform: translate(-50%, -50%) !important;
    z-index: 100001 !important;
}
div:has(.modal-btn-marker) + div button {
    border-radius: 8px !important;
    font-family: 'Cinzel', serif !important;
    font-weight: bold !important;
    font-size: 0.9rem !important;
    padding: 6px 24px !important;
    box-shadow: 0 4px 10px rgba(0,0,0,0.1) !important;
    transition: all 0.2s ease !important;
    display: inline-block !important;
    cursor: pointer;
    min-height: 36px !important;
    width: auto !important;
}
div:has(.modal-warning-btn) + div button {
    background: #C62828 !important;
    border: 1px solid #C62828 !important;
    color: #FFFFFF !important;
}
div:has(.modal-warning-btn) + div button:hover {
    background: #B71C1C !important;
    box-shadow: 0 6px 15px rgba(198, 40, 40, 0.3) !important;
}
div:has(.modal-success-btn) + div button {
    background: #2E7D32 !important;
    border: 1px solid #2E7D32 !important;
    color: #FFFFFF !important;
}
div:has(.modal-success-btn) + div button:hover {
    background: #1B5E20 !important;
    box-shadow: 0 6px 15px rgba(46, 125, 80, 0.3) !important;
}
</style>
""", unsafe_allow_html=True)

    # Initialize dynamic uploader key for CSV
    if 'uploader_key' not in st.session_state:
        st.session_state.uploader_key = 0

    # Render CSV Validation Error Modal
    if st.session_state.get('show_csv_error_modal', False):
        st.markdown(f"""
<div class="modal-overlay">
    <div class="modal-container modal-warning">
        <div class="modal-icon-wrap">
            <div class="modal-icon">!</div>
        </div>
        <div class="modal-title">Format Data Tidak Sesuai</div>
        <p class="modal-desc">{st.session_state.csv_error_message}</p>
        <hr class="modal-divider">
    </div>
</div>
        """, unsafe_allow_html=True)
        
        # Close button X marker
        st.markdown('<div class="modal-close-x-marker"></div>', unsafe_allow_html=True)
        close_x = st.button("X", key="close_csv_modal_x")
        
        # Cancel button marker
        st.markdown('<div class="modal-btn-marker modal-warning-btn"></div>', unsafe_allow_html=True)
        cancel_btn = st.button("Periksa Kembali", key="close_csv_modal_btn")
        
        if close_x or cancel_btn:
            st.session_state.show_csv_error_modal = False
            st.rerun()

    # Render Success Modal
    if st.session_state.get('show_success_modal', False):
        st.markdown(f"""
<div class="modal-overlay">
    <div class="modal-container modal-success">
        <div class="modal-icon-wrap">
            <div class="modal-icon">✓</div>
        </div>
        <div class="modal-title">Data Berhasil Ditambahkan</div>
        <p class="modal-desc">{st.session_state.success_modal_message}</p>
        <hr class="modal-divider">
    </div>
</div>
        """, unsafe_allow_html=True)
        
        # Close button X marker
        st.markdown('<div class="modal-close-x-marker"></div>', unsafe_allow_html=True)
        close_success_x = st.button("X", key="close_success_modal_x")
        
        # Continue button marker
        st.markdown('<div class="modal-btn-marker modal-success-btn"></div>', unsafe_allow_html=True)
        continue_btn = st.button("Lanjutkan", key="close_success_modal_btn")
        
        if close_success_x or continue_btn:
            st.session_state.show_success_modal = False
            st.rerun()

    # (Auth state is managed globally at the top of the file)
    if not st.session_state.authenticated:
        with st.container():
            pw = st.text_input("Kata Sandi:", type="password", placeholder="Masukkan kata sandi admin")
            if st.button("Buka Akses"):
                if pw == "admin123":
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("Kata sandi tidak valid.")
    else:
        st.markdown("<div style='display: inline-block; background-color: #F8F1DA; border-left: 4px solid #D4AF37; color: #5C4033; padding: 10px 16px; border-radius: 4px; margin-bottom: 20px; font-weight: 500; text-align: left; box-shadow: 0 2px 4px rgba(0,0,0,0.05);'><i class='bi bi-unlock-fill' style='margin-right: 8px;'></i>Akses Administrator Terbuka. Anda dapat memasukkan data baru.</div>", unsafe_allow_html=True)
        st.markdown("---")
        
        # Buat Tab untuk pilihan input: Input Manual atau Unggah CSV
        tab_manual, tab_csv = st.tabs(["Tambah Data Satuan", "Unggah Dataset (CSV)"])
        
        # Helper function for PowerTransformer (Yeo-Johnson)
        def get_fitted_transformer():
            base_path = os.path.join(os.path.dirname(__file__), "..", "dataset")
            raw_csv_path = os.path.join(base_path, "Klasifikasi Tingkat Kemiskinan di Indonesia.csv")
            df_raw = pd.read_csv(raw_csv_path)
            
            FEATURES_RAW = [
                "Persentase Penduduk Miskin (P0) Menurut Kabupaten/Kota (Persen)",
                "Rata-rata Lama Sekolah Penduduk 15+ (Tahun)",
                "Pengeluaran per Kapita Disesuaikan (Ribu Rupiah/Orang/Tahun)",
                "Umur Harapan Hidup (Tahun)",
                "Persentase rumah tangga yang memiliki akses terhadap sanitasi layak",
                "Tingkat Pengangguran Terbuka",
                "PDRB atas Dasar Harga Konstan menurut Pengeluaran (Rupiah)"
            ]
            FEATURE_MAP_LOCAL = {
                "Persentase Penduduk Miskin (P0) Menurut Kabupaten/Kota (Persen)": "Persentase_Penduduk_Miskin",
                "Rata-rata Lama Sekolah Penduduk 15+ (Tahun)": "Rata_rata_Lama_Sekolah",
                "Pengeluaran per Kapita Disesuaikan (Ribu Rupiah/Orang/Tahun)": "Pengeluaran_per_Kapita",
                "Umur Harapan Hidup (Tahun)": "UHH",
                "Persentase rumah tangga yang memiliki akses terhadap sanitasi layak": "Sanitasi_Layak",
                "Tingkat Pengangguran Terbuka": "TPT",
                "PDRB atas Dasar Harga Konstan menurut Pengeluaran (Rupiah)": "PDRB_Konstan"
            }
            for col in FEATURES_RAW:
                if df_raw[col].dtype == object:
                    df_raw[col] = pd.to_numeric(df_raw[col].astype(str).str.replace(',', '.'), errors='coerce')
                df_raw[col] = df_raw[col].fillna(df_raw[col].median())
                
            df_raw = df_raw[['Provinsi', 'Kab/Kota'] + FEATURES_RAW].copy()
            df_raw.rename(columns=FEATURE_MAP_LOCAL, inplace=True)
            
            from sklearn.preprocessing import PowerTransformer
            pt = PowerTransformer(method='yeo-johnson', standardize=True)
            pt.fit(df_raw[MAPPED_FEATURES].values)
            return pt
 
        with tab_manual:
            # Form Input Daerah Baru (Symmetrical 2-Column Grid)
            col_left, col_right = st.columns(2)
            with col_left:
                provinsi_list = sorted(df['Provinsi'].unique().tolist())
                provinsi_list.append("+ Tambah Provinsi Baru")
                selected_prov = st.selectbox("Provinsi:", provinsi_list, key="manual_prov_select")
                
                if selected_prov == "+ Tambah Provinsi Baru":
                    new_prov = st.text_input("Nama Provinsi Baru:", placeholder="Contoh: PAPUA BARAT DAYA", key="manual_new_prov")
                else:
                    new_prov = selected_prov
                    
                new_kab = st.text_input("Kabupaten/Kota:", placeholder="Contoh: Kota Nusantara", key="manual_new_kab")
                new_tahun = st.number_input("Tahun:", min_value=2000, max_value=2100, value=2024, step=1, key="manual_new_tahun")
                
            with col_right:
                lat_input = st.number_input("Latitude:", value=0.0, step=0.000001, format="%.6f", key="manual_lat")
                lon_input = st.number_input("Longitude:", value=0.0, step=0.000001, format="%.6f", key="manual_lon")
                
            st.markdown("<h3 style='margin-top: 45px; margin-bottom: 25px; font-weight: 700; color: #1C1714; border-bottom: 2px solid #8a620b; padding-bottom: 12px;'>Input 7 Indikator Kesejahteraan</h3>", unsafe_allow_html=True)
            
            # Symmetrical 2-Column Inputs Grid (4 on Left, 3 on Right)
            c_left, c_right = st.columns(2)
            with c_left:
                uh_input = st.number_input("1. Umur Harapan Hidup (Tahun)", value=70.0, step=0.1, key="manual_uh")
                rls_input = st.number_input("2. Rata-rata Lama Sekolah (Tahun)", value=8.5, step=0.1, key="manual_rls")
                peng_input = st.number_input("3. Pengeluaran per Kapita (Ribu Rp)", value=10000.0, step=100.0, key="manual_peng")
                pdrb_input = st.number_input("4. PDRB Konstan (Rp)", value=5e9, step=1e8, key="manual_pdrb")
            with c_right:
                miskin_input = st.number_input("5. Persentase Kemiskinan (%)", value=10.0, step=0.1, key="manual_miskin")
                sanitasi_input = st.number_input("6. Akses Sanitasi Layak (%)", value=75.0, step=0.1, key="manual_sanitasi")
                tpt_input = st.number_input("7. Tingkat Pengangguran Terbuka (%)", value=5.0, step=0.1, key="manual_tpt")
                
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("Simpan Data ke Sistem", type="primary", key="manual_save_btn"):
                if not new_kab or not new_prov:
                    st.error("Nama Provinsi dan Kabupaten/Kota tidak boleh kosong.")
                else:
                    # 1. Klasifikasi 7-Dimensi di ruang Yeo-Johnson
                    feature_values = {
                        'UHH': uh_input, 'Rata_rata_Lama_Sekolah': rls_input, 'PDRB_Konstan': pdrb_input,
                        'Persentase_Penduduk_Miskin': miskin_input, 'Pengeluaran_per_Kapita': peng_input,
                        'Sanitasi_Layak': sanitasi_input, 'TPT': tpt_input,
                    }
                    
                    # Ambil domain max untuk Welfare Score
                    domain_max = {}
                    weights_df = data['weights']
                    for feat in MAPPED_FEATURES:
                        row_w = weights_df[weights_df['Feature'] == feat]
                        domain_max[feat] = float(row_w['Domain_Max'].iloc[0]) if not row_w.empty else 1.0
                            
                    welfare_score = compute_welfare_score(feature_values, domain_max)
                    
                    # Prediksi Klaster 7D via Jarak Euclidean ke Centroid Scaled
                    best_klaster = 0
                    best_dist = float('inf')
                    try:
                        pt = get_fitted_transformer()
                        new_feat_array = np.array([[feature_values[feat] for feat in MAPPED_FEATURES]])
                        new_feat_scaled = pt.transform(new_feat_array)[0]
                        
                        centroid_scaled_df = data['centroid_scaled']
                        for k in CLUSTER_NAMES.keys():
                            if k == -1:
                                continue  # Skip outlier group
                            tipologi_name = CLUSTER_NAMES[k]
                            if tipologi_name in centroid_scaled_df.index:
                                c_vals_scaled = np.array([float(centroid_scaled_df.loc[tipologi_name, feat]) for feat in MAPPED_FEATURES])
                                dist = np.sqrt(np.sum((new_feat_scaled - c_vals_scaled) ** 2))
                                if dist < best_dist:
                                    best_dist = dist
                                    best_klaster = k
                    except Exception as ex_clf:
                        st.warning(f"Gagal melakukan klasifikasi multidimensi: {ex_clf}. Menggunakan fallback Welfare Score 1D.")
                        centroid_df = data['centroid']
                        for k in CLUSTER_NAMES.keys():
                            if k == -1:
                                continue
                            tipologi_name = CLUSTER_NAMES[k]
                            if tipologi_name in centroid_df.index:
                                c_vals = {feat: float(centroid_df.loc[tipologi_name, feat]) for feat in MAPPED_FEATURES}
                                c_score = compute_welfare_score(c_vals, domain_max)
                                if abs(welfare_score - c_score) < best_dist:
                                    best_dist = abs(welfare_score - c_score)
                                    best_klaster = k
                                    
                    # 2. Kalkulasi Dinamis Seluruh Kolom
                    new_prov_clean = new_prov.upper().strip()
                    
                    # Koordinat spasial dari input manual
                    lat_val = lat_input
                    lon_val = lon_input
                    
                    # Is Jawa
                    jawa_provinces = ["JAWA BARAT", "JAWA TENGAH", "D I YOGYAKARTA", "JAWA TIMUR", "BANTEN", "DKI JAKARTA"]
                    is_jawa_val = "Jawa" if new_prov_clean in jawa_provinces else "Luar Jawa"
                    
                    # Nilai normalisasi range [0, 1]
                    norm_features = {}
                    for feat in MAPPED_FEATURES:
                        val = feature_values[feat]
                        m_val = domain_max[feat]
                        if m_val == 0:
                            norm_val = 0.0
                        else:
                            if feat in ['Persentase_Penduduk_Miskin', 'TPT']:
                                norm_val = max(0.0, min(1.0, 1.0 - (val / m_val)))
                            else:
                                norm_val = max(0.0, min(1.0, val / m_val))
                        norm_features[f'{feat}_norm'] = norm_val
                        
                    # Nilai Z-Score regional per klaster
                    z_scores = {}
                    std_df = data['std']
                    centroid_df = data['centroid']
                    selected_tipologi_name = CLUSTER_NAMES[best_klaster]
                    
                    for feat in MAPPED_FEATURES:
                        c_val = float(centroid_df.loc[selected_tipologi_name, feat]) if selected_tipologi_name in centroid_df.index else 0.0
                        s_val = float(std_df.loc[selected_tipologi_name, feat]) if selected_tipologi_name in std_df.index else 0.0
                        z_scores[f'{feat}_zscore'] = (feature_values[feat] - c_val) / s_val if s_val > 0 else 0.0
                        
                    # Dominant features
                    importances = dict(zip(weights_df['Feature'], weights_df['RF_Importance']))
                    feature_scores = []
                    for feat in MAPPED_FEATURES:
                        z_abs = abs(z_scores[f'{feat}_zscore'])
                        weight = FEATURE_WEIGHTS[feat]
                        rf_imp = importances.get(feat, 0.0)
                        combined_score = z_abs * weight * rf_imp
                        feature_scores.append((feat, z_abs, weight, combined_score))
                    
                    feature_scores.sort(key=lambda x: x[3], reverse=True)
                    top3 = feature_scores[:3]
                    dominant_vals = {
                        'top1_feat': top3[0][0], 'top1_z': top3[0][1], 'top1_weight': top3[0][2],
                        'top2_feat': top3[1][0], 'top2_z': top3[1][1],
                        'top3_feat': top3[2][0], 'top3_z': top3[2][1]
                    }
                    
                    tipologi_db_map = {0: "Berkembang Industrial", 1: "Berkembang Rentan", 2: "Berkembang Seimbang", 3: "Maju & Urbanized", -1: "Entitas Atipikal"}
                    tipologi_db_val = tipologi_db_map.get(best_klaster, "Berkembang Rentan")
                    
                    # Gabungkan seluruh kolom
                    new_row = {
                        'Provinsi': new_prov_clean,
                        'Kab/Kota': new_kab.strip(),
                        'Persentase_Penduduk_Miskin': feature_values['Persentase_Penduduk_Miskin'],
                        'Rata_rata_Lama_Sekolah': feature_values['Rata_rata_Lama_Sekolah'],
                        'Pengeluaran_per_Kapita': feature_values['Pengeluaran_per_Kapita'],
                        'UHH': feature_values['UHH'],
                        'Sanitasi_Layak': feature_values['Sanitasi_Layak'],
                        'TPT': feature_values['TPT'],
                        'PDRB_Konstan': feature_values['PDRB_Konstan'],
                        'Latitude': lat_val,
                        'Longitude': lon_val,
                        'Tahun': int(new_tahun),
                        'Klaster': best_klaster,
                        'Tipologi': tipologi_db_val,
                        'Welfare_Score': welfare_score,
                        **norm_features,
                        'Is_Jawa': is_jawa_val,
                        **z_scores,
                        **dominant_vals
                    }
                    
                    # Simpan ke CSV di background (Appending)
                    base_path = os.path.join(os.path.dirname(__file__), "..", "dataset")
                    csv_path = os.path.join(base_path, "processed", "narrative_data.csv")
                    try:
                        df_new = pd.DataFrame([new_row])
                        db_cols = pd.read_csv(csv_path, nrows=0).columns.tolist()
                        df_new = df_new[db_cols]
                        df_new.to_csv(csv_path, mode='a', header=False, index=False)
                        
                        st.session_state.success_modal_message = f"Data wilayah <b>{new_kab}</b> (Provinsi {new_prov_clean}) tahun <b>{new_tahun}</b> berhasil ditambahkan ke database sistem klasifikasi."
                        st.session_state.show_success_modal = True
                        st.cache_data.clear()
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"Gagal menyimpan data: {e}")

        with tab_csv:
            st.markdown("<h3 style='font-family: \"Cormorant Garamond\", serif; font-size: 1.6rem; font-weight: bold; color: #1C1714; margin-top:10px; margin-bottom:15px;'>Unggah Dataset Wilayah Baru (.csv)</h3>", unsafe_allow_html=True)
            st.markdown("""<div style="font-family: 'Crimson Pro', serif; font-size: 1.05rem; line-height: 1.6; color: #1C1714; margin-bottom: 12px;">
            Unggah file berformat <b>.csv</b> untuk menambahkan banyak wilayah baru sekaligus secara cepat ke dalam database sistem.
            </div>""", unsafe_allow_html=True)
            
            with st.expander("📋 Kolom CSV yang Wajib Dimiliki", expanded=False):
                st.markdown("""
                <div style="font-family: 'Crimson Pro', serif; font-size: 1.1rem; color: #1C1714; margin-bottom: 12px;">
                Berkas CSV yang diunggah harus memiliki kolom-kolom individual berikut secara lengkap (nama kolom sensitif terhadap huruf besar/kecil):
                </div>
                <div style="display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 10px;">
                    <span style="background-color: #1C1714; color: #F3EFE9; font-family: 'Crimson Pro', serif; font-size: 0.95rem; padding: 6px 12px; border-radius: 4px; border: 1px solid #9C8B7A; font-weight: bold; display: inline-block; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">Provinsi</span>
                    <span style="background-color: #1C1714; color: #F3EFE9; font-family: 'Crimson Pro', serif; font-size: 0.95rem; padding: 6px 12px; border-radius: 4px; border: 1px solid #9C8B7A; font-weight: bold; display: inline-block; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">Kab/Kota</span>
                    <span style="background-color: #1C1714; color: #F3EFE9; font-family: 'Crimson Pro', serif; font-size: 0.95rem; padding: 6px 12px; border-radius: 4px; border: 1px solid #9C8B7A; font-weight: bold; display: inline-block; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">Persentase_Penduduk_Miskin</span>
                    <span style="background-color: #1C1714; color: #F3EFE9; font-family: 'Crimson Pro', serif; font-size: 0.95rem; padding: 6px 12px; border-radius: 4px; border: 1px solid #9C8B7A; font-weight: bold; display: inline-block; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">Rata_rata_Lama_Sekolah</span>
                    <span style="background-color: #1C1714; color: #F3EFE9; font-family: 'Crimson Pro', serif; font-size: 0.95rem; padding: 6px 12px; border-radius: 4px; border: 1px solid #9C8B7A; font-weight: bold; display: inline-block; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">Pengeluaran_per_Kapita</span>
                    <span style="background-color: #1C1714; color: #F3EFE9; font-family: 'Crimson Pro', serif; font-size: 0.95rem; padding: 6px 12px; border-radius: 4px; border: 1px solid #9C8B7A; font-weight: bold; display: inline-block; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">UHH</span>
                    <span style="background-color: #1C1714; color: #F3EFE9; font-family: 'Crimson Pro', serif; font-size: 0.95rem; padding: 6px 12px; border-radius: 4px; border: 1px solid #9C8B7A; font-weight: bold; display: inline-block; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">Sanitasi_Layak</span>
                    <span style="background-color: #1C1714; color: #F3EFE9; font-family: 'Crimson Pro', serif; font-size: 0.95rem; padding: 6px 12px; border-radius: 4px; border: 1px solid #9C8B7A; font-weight: bold; display: inline-block; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">TPT</span>
                    <span style="background-color: #1C1714; color: #F3EFE9; font-family: 'Crimson Pro', serif; font-size: 0.95rem; padding: 6px 12px; border-radius: 4px; border: 1px solid #9C8B7A; font-weight: bold; display: inline-block; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">PDRB_Konstan</span>
                    <span style="background-color: #1C1714; color: #F3EFE9; font-family: 'Crimson Pro', serif; font-size: 0.95rem; padding: 6px 12px; border-radius: 4px; border: 1px solid #9C8B7A; font-weight: bold; display: inline-block; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">Latitude</span>
                    <span style="background-color: #1C1714; color: #F3EFE9; font-family: 'Crimson Pro', serif; font-size: 0.95rem; padding: 6px 12px; border-radius: 4px; border: 1px solid #9C8B7A; font-weight: bold; display: inline-block; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">Longitude</span>
                    <span style="background-color: #1C1714; color: #F3EFE9; font-family: 'Crimson Pro', serif; font-size: 0.95rem; padding: 6px 12px; border-radius: 4px; border: 1px solid #9C8B7A; font-weight: bold; display: inline-block; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">Tahun</span>
                </div>
                """, unsafe_allow_html=True)
            
            # Reset file uploader dynamic key if validation fails to avoid infinite flicker loop
            uploaded_file = st.file_uploader("Pilih file CSV:", type=["csv"], key=f"csv_uploader_{st.session_state.uploader_key}")
            
            if uploaded_file is not None:
                try:
                    df_upload = pd.read_csv(uploaded_file)
                    required_cols = [
                        'Provinsi', 'Kab/Kota', 'Persentase_Penduduk_Miskin', 
                        'Rata_rata_Lama_Sekolah', 'Pengeluaran_per_Kapita', 'UHH', 
                        'Sanitasi_Layak', 'TPT', 'PDRB_Konstan', 'Latitude', 'Longitude', 'Tahun'
                    ]
                    missing_cols = [col for col in required_cols if col not in df_upload.columns]
                    
                    if missing_cols:
                        st.session_state.show_csv_error_modal = True
                        st.session_state.csv_error_message = f"Kolom wajib berikut tidak ditemukan di dalam file CSV Anda: <b>{', '.join(missing_cols)}</b>. Mohon periksa nama kolom Anda agar sesuai persis."
                        st.session_state.uploader_key += 1
                        st.rerun()
                    else:
                        pt = get_fitted_transformer()
                        
                        # Ambil domain_max untuk Welfare Score
                        domain_max = {}
                        weights_df = data['weights']
                        for feat in MAPPED_FEATURES:
                            row_w = weights_df[weights_df['Feature'] == feat]
                            domain_max[feat] = float(row_w['Domain_Max'].iloc[0]) if not row_w.empty else 1.0
                            
                        centroid_scaled_df = data['centroid_scaled']
                        centroid_df = data['centroid']
                        std_df = data['std']
                        importances = dict(zip(weights_df['Feature'], weights_df['RF_Importance']))
                        
                        processed_rows = []
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        total_rows = len(df_upload)
                        
                        for idx, row_csv in df_upload.iterrows():
                            # Parsing values
                            feature_values = {
                                'UHH': float(row_csv['UHH']),
                                'Rata_rata_Lama_Sekolah': float(row_csv['Rata_rata_Lama_Sekolah']),
                                'PDRB_Konstan': float(row_csv['PDRB_Konstan']),
                                'Persentase_Penduduk_Miskin': float(row_csv['Persentase_Penduduk_Miskin']),
                                'Pengeluaran_per_Kapita': float(row_csv['Pengeluaran_per_Kapita']),
                                'Sanitasi_Layak': float(row_csv['Sanitasi_Layak']),
                                'TPT': float(row_csv['TPT'])
                            }
                            
                            w_score = compute_welfare_score(feature_values, domain_max)
                            
                            best_klaster = 0
                            best_dist = float('inf')
                            try:
                                new_feat_array = np.array([[feature_values[feat] for feat in MAPPED_FEATURES]])
                                new_feat_scaled = pt.transform(new_feat_array)[0]
                                for k in CLUSTER_NAMES.keys():
                                    if k == -1:
                                        continue
                                    tipologi_name = CLUSTER_NAMES[k]
                                    if tipologi_name in centroid_scaled_df.index:
                                        c_vals_scaled = np.array([float(centroid_scaled_df.loc[tipologi_name, feat]) for feat in MAPPED_FEATURES])
                                        dist = np.sqrt(np.sum((new_feat_scaled - c_vals_scaled) ** 2))
                                        if dist < best_dist:
                                            best_dist = dist
                                            best_klaster = k
                            except Exception:
                                for k in CLUSTER_NAMES.keys():
                                    if k == -1:
                                        continue
                                    tipologi_name = CLUSTER_NAMES[k]
                                    if tipologi_name in centroid_df.index:
                                        c_vals = {feat: float(centroid_df.loc[tipologi_name, feat]) for feat in MAPPED_FEATURES}
                                        c_score = compute_welfare_score(c_vals, domain_max)
                                        if abs(w_score - c_score) < best_dist:
                                            best_dist = abs(w_score - c_score)
                                            best_klaster = k
                                            
                            norm_features = {}
                            for feat in MAPPED_FEATURES:
                                val = feature_values[feat]
                                m_val = domain_max[feat]
                                if m_val == 0:
                                    norm_val = 0.0
                                else:
                                    if feat in ['Persentase_Penduduk_Miskin', 'TPT']:
                                        norm_val = max(0.0, min(1.0, 1.0 - (val / m_val)))
                                    else:
                                        norm_val = max(0.0, min(1.0, val / m_val))
                                norm_features[f'{feat}_norm'] = norm_val
                                
                            z_scores = {}
                            selected_tipologi_name = CLUSTER_NAMES[best_klaster]
                            for feat in MAPPED_FEATURES:
                                c_val = float(centroid_df.loc[selected_tipologi_name, feat]) if selected_tipologi_name in centroid_df.index else 0.0
                                s_val = float(std_df.loc[selected_tipologi_name, feat]) if selected_tipologi_name in std_df.index else 0.0
                                z_scores[f'{feat}_zscore'] = (feature_values[feat] - c_val) / s_val if s_val > 0 else 0.0
                                
                            feature_scores = []
                            for feat in MAPPED_FEATURES:
                                z_abs = abs(z_scores[f'{feat}_zscore'])
                                weight = FEATURE_WEIGHTS[feat]
                                rf_imp = importances.get(feat, 0.0)
                                combined_score = z_abs * weight * rf_imp
                                feature_scores.append((feat, z_abs, weight, combined_score))
                                
                            feature_scores.sort(key=lambda x: x[3], reverse=True)
                            top3 = feature_scores[:3]
                            dominant_vals = {
                                'top1_feat': top3[0][0], 'top1_z': top3[0][1], 'top1_weight': top3[0][2],
                                'top2_feat': top3[1][0], 'top2_z': top3[1][1],
                                'top3_feat': top3[2][0], 'top3_z': top3[2][1]
                            }
                            
                            tipologi_db_map = {0: "Berkembang Industrial", 1: "Berkembang Rentan", 2: "Berkembang Seimbang", 3: "Maju & Urbanized", -1: "Entitas Atipikal"}
                            tipologi_db_val = tipologi_db_map.get(best_klaster, "Berkembang Rentan")
                            
                            prov_name_clean = str(row_csv['Provinsi']).upper().strip()
                            jawa_provinces = ["JAWA BARAT", "JAWA TENGAH", "D I YOGYAKARTA", "JAWA TIMUR", "BANTEN", "DKI JAKARTA"]
                            is_jawa_val = "Jawa" if prov_name_clean in jawa_provinces else "Luar Jawa"
                            
                            new_row_processed = {
                                'Provinsi': prov_name_clean,
                                'Kab/Kota': str(row_csv['Kab/Kota']).strip(),
                                'Persentase_Penduduk_Miskin': feature_values['Persentase_Penduduk_Miskin'],
                                'Rata_rata_Lama_Sekolah': feature_values['Rata_rata_Lama_Sekolah'],
                                'Pengeluaran_per_Kapita': feature_values['Pengeluaran_per_Kapita'],
                                'UHH': feature_values['UHH'],
                                'Sanitasi_Layak': feature_values['Sanitasi_Layak'],
                                'TPT': feature_values['TPT'],
                                'PDRB_Konstan': feature_values['PDRB_Konstan'],
                                'Latitude': float(row_csv['Latitude']),
                                'Longitude': float(row_csv['Longitude']),
                                'Tahun': int(row_csv['Tahun']),
                                'Klaster': best_klaster,
                                'Tipologi': tipologi_db_val,
                                'Welfare_Score': w_score,
                                **norm_features,
                                'Is_Jawa': is_jawa_val,
                                **z_scores,
                                **dominant_vals
                            }
                            processed_rows.append(new_row_processed)
                            progress_bar.progress((idx + 1) / total_rows)
                            status_text.text(f"Memproses wilayah ke-{idx+1} dari {total_rows}...")
                            
                        df_processed = pd.DataFrame(processed_rows)
                        base_path = os.path.join(os.path.dirname(__file__), "..", "dataset")
                        csv_path = os.path.join(base_path, "processed", "narrative_data.csv")
                        db_cols = pd.read_csv(csv_path, nrows=0).columns.tolist()
                        df_processed = df_processed[db_cols]
                        
                        df_processed.to_csv(csv_path, mode='a', header=False, index=False)
                        st.session_state.success_modal_message = f"Berhasil memproses dan mengunggah <b>{total_rows}</b> data wilayah secara massal ke database sistem."
                        st.session_state.show_success_modal = True
                        st.session_state.uploader_key += 1
                        st.cache_data.clear()
                        st.rerun()
                except Exception as e_csv:
                    st.error(f"Gagal memproses file CSV: {e_csv}")

# ============================================================
# MENU 4: INFO
# ============================================================
elif menu == "Info":
    ui_volume_header("IV", "Informasi Sistem & Metodologi")
    st.markdown("Dokumentasi teknis pemodelan, sumber data, dan validasi algoritma klasifikasi.")
    with st.container():
        st.markdown("<h3 style='font-family: \"Cormorant Garamond\", serif; font-size: 1.8rem; font-weight: bold; color: #1C1714; border-bottom: 1px solid var(--border-standard); padding-bottom: 8px; margin-bottom: 15px;'>Latar Belakang dan Tujuan</h3>", unsafe_allow_html=True)
        st.markdown("""
        <div style='font-family: "Crimson Pro", serif; font-size: 1.15rem; line-height: 1.7; color: #1C1714; text-align: justify; margin-bottom: 25px;'>
            Analisis ketimpangan wilayah di Indonesia secara historis sering kali berfokus pada perbandingan sederhana antara Pulau Jawa dan luar Pulau Jawa. SENUWU dikembangkan untuk menguji dinamika tersebut menggunakan data spasial berbasis klaster. Mengolah dataset resmi BPS lintas tahun yang mencakup seluruh kabupaten dan kota di Indonesia, pengelompokan ini tidak hanya bertumpu pada satu dimensi pembangunan saja, melainkan mengintegrasikan tujuh indikator kesejahteraan utama yang mencakup aspek sosial, ekonomi, hingga infrastruktur dasar wilayah.
            <br><br>
            <b>Tujuan Pengembangan.</b> Hasil pemetaan ini diharapkan dapat memberikan landasan empiris yang kuat untuk mendukung perumusan kebijakan berbasis bukti (<i>evidence-based policy</i>). Dengan memahami karakteristik unik dari setiap kelompok wilayah, para pemangku kepentingan dapat merancang strategi intervensi sosial-ekonomi yang lebih tepat sasaran, efektif, dan sesuai dengan kebutuhan riil masyarakat di lapangan.
        </div>
        """, unsafe_allow_html=True)

    with st.container():
        st.markdown("<h3 style='font-family: \"Cormorant Garamond\", serif; font-size: 1.8rem; font-weight: bold; color: #1C1714; border-bottom: 1px solid var(--border-standard); padding-bottom: 8px; margin-bottom: 25px; margin-top: 20px;'>Alur Kerja Proyek</h3>", unsafe_allow_html=True)
        st.markdown("""<div style="display: flex; flex-direction: column; gap: 20px; margin-bottom: 40px; font-family: 'Crimson Pro', serif; color: #1C1714;">
<div style="display: flex; align-items: flex-start; gap: 15px; border-left: 3px solid #8a620b; padding-left: 20px;">
<div style="font-family: 'Cinzel', serif; font-size: 1.1rem; color: #8a620b; font-weight: bold; min-width: 30px;">01</div>
<div>
<h4 style="margin: 0 0 5px 0; font-family: 'Cormorant Garamond', serif; font-size: 1.3rem; font-weight: bold; color: #1C1714;">Identifikasi Masalah</h4>
<p style="margin: 0; font-size: 1.05rem; color: #1C1714; line-height: 1.5;">Menentukan rumusan ketimpangan sosial-ekonomi antarwilayah serta merancang tujuan fungsionalitas sistem informasi.</p>
</div>
</div>
<div style="display: flex; align-items: flex-start; gap: 15px; border-left: 3px solid #8a620b; padding-left: 20px;">
<div style="font-family: 'Cinzel', serif; font-size: 1.1rem; color: #8a620b; font-weight: bold; min-width: 30px;">02</div>
<div>
<h4 style="margin: 0 0 5px 0; font-family: 'Cormorant Garamond', serif; font-size: 1.3rem; font-weight: bold; color: #1C1714;">Pengumpulan Data</h4>
<p style="margin: 0; font-size: 1.05rem; color: #1C1714; line-height: 1.5;">Mengambil 7 indikator pembangunan dan kesejahteraan resmi dari publikasi BPS lintas tahun yang mencakup seluruh kabupaten dan kota di Indonesia.</p>
</div>
</div>
<div style="display: flex; align-items: flex-start; gap: 15px; border-left: 3px solid #8a620b; padding-left: 20px;">
<div style="font-family: 'Cinzel', serif; font-size: 1.1rem; color: #8a620b; font-weight: bold; min-width: 30px;">03</div>
<div>
<h4 style="margin: 0 0 5px 0; font-family: 'Cormorant Garamond', serif; font-size: 1.3rem; font-weight: bold; color: #1C1714;">Pengolahan Data</h4>
<p style="margin: 0; font-size: 1.05rem; color: #1C1714; line-height: 1.5;">Melakukan pembersihan data, penanganan data pencilan (*outliers*), dan normalisasi skala fitur dengan transformasi Yeo-Johnson.</p>
</div>
</div>
<div style="display: flex; align-items: flex-start; gap: 15px; border-left: 3px solid #8a620b; padding-left: 20px;">
<div style="font-family: 'Cinzel', serif; font-size: 1.1rem; color: #8a620b; font-weight: bold; min-width: 30px;">04</div>
<div>
<h4 style="margin: 0 0 5px 0; font-family: 'Cormorant Garamond', serif; font-size: 1.3rem; font-weight: bold; color: #1C1714;">Analisis Pemodelan Data Mining</h4>
<p style="margin: 0; font-size: 1.05rem; color: #1C1714; line-height: 1.5;">Menerapkan model hybrid: mengidentifikasi struktur klaster alami dan memisahkan pencilan menggunakan algoritma <b>HDBSCAN</b>, kemudian mengalokasikan seluruh wilayah ke klaster final secara konsisten menggunakan <b>K-Means</b>.</p>
</div>
</div>
<div style="display: flex; align-items: flex-start; gap: 15px; border-left: 3px solid #8a620b; padding-left: 20px;">
<div style="font-family: 'Cinzel', serif; font-size: 1.1rem; color: #8a620b; font-weight: bold; min-width: 30px;">05</div>
<div>
<h4 style="margin: 0 0 5px 0; font-family: 'Cormorant Garamond', serif; font-size: 1.3rem; font-weight: bold; color: #1C1714;">Implementasi & Deployment</h4>
<p style="margin: 0; font-size: 1.05rem; color: #1C1714; line-height: 1.5;">Membangun peta choropleth interaktif dengan Folium, mendesain antarmuka dashboard, dan meluncurkannya menggunakan Streamlit.</p>
</div>
</div>
</div>""", unsafe_allow_html=True)

    # C. Analisis Kontribusi Variabel (Feature Importance)
    with st.container():
        st.markdown("<h3 style='font-family: \"Cormorant Garamond\", serif; font-size: 1.8rem; font-weight: bold; color: #1C1714; border-bottom: 1px solid var(--border-standard); padding-bottom: 8px; margin-bottom: 15px; margin-top: 20px;'>Indikator Pembentuk Klaster Utama (Feature Importance)</h3>", unsafe_allow_html=True)
        st.markdown("""
        <div style='font-family: "Crimson Pro", serif; font-size: 1.15rem; line-height: 1.7; color: #1C1714; text-align: justify; margin-bottom: 15px;'>
            Untuk memahami faktor utama yang paling membedakan profil kesejahteraan antarwilayah, tingkat kontribusi indikator dievaluasi menggunakan algoritma Random Forest. Grafik di bawah menunjukkan nilai penting (feature importance) dari setiap indikator. Semakin panjang diagram batang, semakin besar pengaruh indikator tersebut dalam menentukan pengelompokan wilayah ke dalam kategori Maju, Transisi, maupun Rentan.
        </div>
        """, unsafe_allow_html=True)
        
        # Load weights data directly to bypass any caching issues
        csv_path = os.path.join(current_dir, "..", "dataset", "results", "tables", "feature_weights.csv")
        if not os.path.exists(csv_path):
            csv_path = os.path.join(current_dir, "dataset", "results", "tables", "feature_weights.csv")
            
        if os.path.exists(csv_path):
            weights_sorted = pd.read_csv(csv_path).sort_values(by='RF_Importance', ascending=True).copy()
            weights_sorted['Feature_Label'] = weights_sorted['Feature'].map(FEATURE_LABELS)
            
            fig_importance = px.bar(
                weights_sorted,
                x='RF_Importance',
                y='Feature_Label',
                orientation='h',
                labels={'RF_Importance': 'Tingkat Kepentingan', 'Feature_Label': 'Indikator'},
                color='RF_Importance',
                color_continuous_scale=['#D2B48C', '#4A3B32']
            )
            fig_importance.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(family='Crimson Pro, serif', size=14, color='#1C1714'),
                margin=dict(l=160, r=20, t=10, b=10),
                coloraxis_showscale=False,
                xaxis=dict(
                    showgrid=True, 
                    gridcolor='#E8DFD4', 
                    zeroline=False,
                    tickfont=dict(family='Crimson Pro, serif', size=13, color='#1C1714'),
                    title=dict(font=dict(family='Crimson Pro, serif', size=14, color='#1C1714'))
                ),
                yaxis=dict(
                    title=None,
                    tickfont=dict(family='Crimson Pro, serif', size=13, color='#1C1714')
                ),
                hoverlabel=dict(
                    bgcolor='rgba(243, 239, 233, 0.8)',
                    bordercolor='#9C8B7A',
                    font=dict(family='Crimson Pro, serif', size=14, color='#1C1714')
                ),
                height=350
            )
            st.plotly_chart(fig_importance, use_container_width=True, theme=None)
        else:
            st.warning("Data Feature Importance (feature_weights.csv) tidak ditemukan di sistem.")

    # D. Profil Karakteristik Klaster (Cluster Profiling)
    with st.container():
        st.markdown("<h3 style='font-family: \"Cormorant Garamond\", serif; font-size: 1.8rem; font-weight: bold; color: #1C1714; border-bottom: 1px solid var(--border-standard); padding-bottom: 8px; margin-bottom: 15px; margin-top: 35px;'>Karakteristik Tiap Kategori (Cluster Profiling)</h3>", unsafe_allow_html=True)
        st.markdown("""
        <div style='font-family: "Crimson Pro", serif; font-size: 1.15rem; line-height: 1.7; color: #1C1714; text-align: justify; margin-bottom: 20px;'>
            Berdasarkan hasil pemodelan, setiap klaster memiliki pola kesejahteraan yang khas. Tabel di bawah ini merepresentasikan nilai rata-rata dari tujuh indikator pada masing-masing kategori, yang menjadi dasar interpretasi penamaan klaster:
        </div>
        """, unsafe_allow_html=True)
        
        # Render Heatmap-style Table
        clusters_to_show = ["Urban Maju", "Sentra Industri", "Transisi Seimbang", "Area Rentan"]
        df_centroid_display = data['centroid'].loc[clusters_to_show].copy()
        
        # Rename columns to human readable
        df_centroid_display.rename(columns=FEATURE_LABELS, inplace=True)
        
        # We create a styler
        styler = df_centroid_display.style
        
        # Formatter dictionary
        format_dict = {}
        for feat in MAPPED_FEATURES:
            label = FEATURE_LABELS[feat]
            if feat == 'PDRB_Konstan':
                format_dict[label] = lambda x: f"Rp {x * 1e6 / 1e9:.1f} M" if x * 1e6 < 1e12 else f"Rp {x * 1e6 / 1e12:.1f} T"
            elif feat in ['Persentase_Penduduk_Miskin', 'Sanitasi_Layak', 'TPT']:
                format_dict[label] = "{:.1f}%"
            elif feat in ['UHH', 'Rata_rata_Lama_Sekolah']:
                format_dict[label] = "{:.1f} tahun"
            elif feat == 'Pengeluaran_per_Kapita':
                format_dict[label] = lambda x: f"Rp {x * 1000:,.0f}".replace(',', '.')
                
        styler = styler.format(format_dict)
        
        # Positive indicators (high value is good)
        pos_cols = [FEATURE_LABELS[f] for f in ['UHH', 'Rata_rata_Lama_Sekolah', 'Pengeluaran_per_Kapita', 'Sanitasi_Layak', 'PDRB_Konstan']]
        styler = styler.background_gradient(cmap='YlGn', subset=pos_cols)
        
        # Negative indicators (low value is good)
        neg_cols = [FEATURE_LABELS[f] for f in ['Persentase_Penduduk_Miskin', 'TPT']]
        styler = styler.background_gradient(cmap='YlOrRd', subset=neg_cols)
        
        # Custom table styling for headers and cells
        styler = styler.set_table_styles([
            {
                'selector': 'th',
                'props': [
                    ('background-color', '#1C1714'),
                    ('color', '#FFFFFF'),
                    ('font-family', 'Cinzel, serif'),
                    ('font-weight', 'bold'),
                    ('border', '1px solid #9C8B7A'),
                    ('text-align', 'center'),
                    ('padding', '10px')
                ]
            },
            {
                'selector': 'td',
                'props': [
                    ('border', '1px solid #9C8B7A'),
                    ('padding', '10px'),
                    ('font-family', 'Crimson Pro, serif')
                ]
            }
        ])
        
        st.write(styler)
        
        # Narrative summaries for clusters
        st.markdown("""
        <div style='font-family: "Crimson Pro", serif; font-size: 1.15rem; line-height: 1.7; color: #1C1714; text-align: justify; margin-top: 25px;'>
            <p style="margin-bottom: 18px;">
                <b style="color: var(--accent-brass); font-size: 1.15rem;">• Urban Maju:</b> Kelompok wilayah perkotaan yang menonjol dengan angka harapan hidup tertinggi (rata-rata 72,7 tahun) dan tingkat kemiskinan paling rendah (6,7%). Meskipun memiliki infrastruktur dan layanan publik yang unggul, wilayah dalam kategori ini menghadapi tantangan pengangguran terbuka yang relatif tinggi (8,2%), dipicu oleh arus urbanisasi dan persaingan kerja yang ketat di area perkotaan.
            </p>
            <p style="margin-bottom: 18px;">
                <b style="color: var(--accent-brass); font-size: 1.15rem;">• Sentra Industri:</b> Kelompok wilayah yang dicirikan oleh aktivitas ekonomi sektor manufaktur yang sangat masif, menghasilkan rata-rata PDRB konstan yang tinggi (mencapai Rp34,1 triliun). Kelompok ini ditunjang oleh angka harapan hidup yang baik (72,0 tahun), namun juga mencatat tingkat pengangguran terbuka yang cukup tinggi (5,8%) akibat derasnya migrasi para pencari kerja.
            </p>
            <p style="margin-bottom: 18px;">
                <b style="color: var(--accent-brass); font-size: 1.15rem;">• Transisi Seimbang:</b> Kelompok wilayah yang menunjukkan pola pembangunan yang stabil dan merata. Kategori ini berhasil menjaga tingkat kemiskinan (8,8%) dan pengangguran terbuka (4,1%) tetap rendah, yang didukung oleh pemerataan akses sanitasi layak (82,5%) serta daya beli masyarakat yang relatif konsisten.
            </p>
            <p style="margin-bottom: 18px;">
                <b style="color: var(--accent-brass); font-size: 1.15rem;">• Area Rentan:</b> Kelompok wilayah yang masih memerlukan perhatian pembangunan lebih lanjut. Kategori ini mencatat rata-rata kemiskinan yang cukup tinggi (17,7%) dengan kapasitas PDRB daerah yang terbatas (rata-rata Rp4,6 triliun) serta akses sanitasi dasar yang masih perlu ditingkatkan (67,5%). Tingkat pengangguran terbuka tercatat rendah (3,8%) karena mayoritas penduduk bekerja di sektor informal dan pertanian.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    # Footer Credit (No Box)
    st.markdown("""<div style="margin-top: 50px; padding: 10px 0 30px 0; text-align: center;">
<hr style="border: 0; border-top: 1px solid #9C8B7A; margin-bottom: 4px;">
<hr style="border: 0; border-top: 1px solid #9C8B7A; margin-bottom: 30px;">
<h4 style="margin-top:0; color: #8a620b; font-family: 'Cormorant Garamond', serif;"><i class="bi bi-people-fill"></i> Tim Penyusun</h4>
<p style="margin-bottom: 1.5rem; color: #5C4033;"><b>Program Studi Sistem Informasi</b><br>Universitas Duta Bangsa Surakarta</p>
<div style="display: flex; justify-content: center; gap: 40px; flex-wrap: wrap;">
<div style="text-align: center;">
<i class="bi bi-person-fill" style="color:#8a620b; font-size: 1.5rem;"></i><br>
<b style="color: #5C4033;">Rahma Nurhuda Hanifah</b><br><span style="color:#8a620b; font-size: 0.9rem;">Mahasiswa 1</span>
</div>
<div style="text-align: center;">
<i class="bi bi-person-fill" style="color:#8a620b; font-size: 1.5rem;"></i><br>
<b style="color: #5C4033;">Naufal Azaria Sumpeno P</b><br><span style="color:#8a620b; font-size: 0.9rem;">Mahasiswa 2</span>
</div>
<div style="text-align: center;">
<i class="bi bi-person-fill" style="color:#8a620b; font-size: 1.5rem;"></i><br>
<b style="color: #5C4033;">Sita Mei Wulan S</b><br><span style="color:#8a620b; font-size: 0.9rem;">Mahasiswa 3</span>
</div>
<div style="text-align: center;">
<i class="bi bi-person-badge-fill" style="color:#8a620b; font-size: 1.5rem;"></i><br>
<b style="color: #5C4033;">Marta Ardiyanto, M.Kom</b><br><span style="color:#8a620b; font-size: 0.9rem;">Dosen Pembimbing</span>
</div>
</div>
</div>""", unsafe_allow_html=True)


