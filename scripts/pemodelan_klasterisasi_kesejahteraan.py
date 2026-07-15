# -*- coding: utf-8 -*-
"""
pemodelan_klasterisasi_kesejahteraan.py
========================================
Pemodelan Klasterisasi Kesejahteraan Antarwilayah
Berbasis Pipeline Hybrid HDBSCAN-KMeans dengan Welfare Clustering Validity Index (WCVI)

Dokumentasi Teknis Program Komputer - Pendaftaran Hak Kekayaan Intelektual (HKI)
Kategori: Program Komputer (Sains Data & Ekonomi Regional)
Teknologi: Python 3.9+ | Scikit-Learn | HDBSCAN | PySAL | Matplotlib | Seaborn

Disusun oleh:
1. Naufal Azaria Sumpeno P (230101026)
2. Rahma Nurhuda Hanifah (230101033)
3. Sita Mei Wulan S (230101036)

CARA PAKAI:
-----------
1. Pastikan dataset CSV tersedia di: dataset/Klasifikasi Tingkat Kemiskinan di Indonesia.csv
   (Jika belum ada, skrip akan memberi pesan cara mendapatkannya)

2. Install dependensi (sekali saja):
   pip install pandas numpy scikit-learn scipy matplotlib seaborn \\
               hdbscan libpysal esda scikit-posthocs

3. Run:
   python pemodelan_klasterisasi_kesejahteraan.py

Skrip ini akan otomatis:
- Membuat folder output yang dibutuhkan (dataset/processed, dataset/results/*, dll)
- Generate master koordinat jika belum ada (dataset/raw/master_koordinat_id.csv)
- Menjalankan 7 langkah pipeline end-to-end
- Menyimpan tabel CSV, figur PNG, dan log eksekusi
"""

import os
import sys
import re
import logging
import warnings
import subprocess
import time

# ============================================================
# SETUP 0: AUTO-INSTALL DEPENDENCIES (jika belum tersedia)
# ============================================================
def _install_if_missing(package_name, import_name=None):
    """Install package via pip jika belum tersedia."""
    if import_name is None:
        import_name = package_name
    try:
        __import__(import_name)
    except ImportError:
        print(f"  ⚠ {package_name} belum terinstall, menginstall...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--quiet', package_name])
            print(f"  ✓ {package_name} berhasil diinstall")
        except subprocess.CalledProcessError as e:
            print(f"  ✗ Gagal install {package_name}: {e}")
            print(f"    Coba manual: pip install {package_name}")
            sys.exit(1)

print("=" * 70)
print("SETUP 0: Cek & Install Dependensi")
print("=" * 70)
for pkg, imp in [('hdbscan', 'hdbscan'), ('libpysal', 'libpysal'),
                  ('esda', 'esda'), ('scikit-posthocs', 'scikit_posthocs'),
                  ('geopandas', 'geopandas'), ('requests', 'requests')]:
    _install_if_missing(pkg, imp)


# ============================================================
# IMPORT LIBRARY
# ============================================================
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # headless-safe
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.preprocessing import PowerTransformer
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.neighbors import NearestNeighbors
from sklearn.metrics import adjusted_rand_score

import hdbscan
from scipy.stats import kruskal, chi2_contingency, spearmanr
import scikit_posthocs as sp
from libpysal.weights import W, KNN
from esda.moran import Moran
import geopandas as gpd
import requests

# Konfigurasi visualisasi
plt.rcParams["figure.dpi"] = 150
plt.rcParams["font.family"] = "serif"
sns.set_style("whitegrid")
pd.set_option('display.float_format', lambda x: '%.4f' % x)


# Suppress warning yang noisy
import warnings
warnings.filterwarnings('ignore')
import os
os.environ['PYTHONWARNINGS'] = 'ignore'


# ============================================================
# SETUP 1: AUTO-CREATE FOLDERS
# ============================================================
print("=" * 70)
print("SETUP 1: Auto-Create Folder Output")
print("=" * 70)

PATH_DATA = "dataset/Klasifikasi Tingkat Kemiskinan di Indonesia.csv"
PATH_COORDS = "dataset/raw/master_koordinat_id.csv"
DIRS = [
    "dataset/raw",
    "dataset/processed",
    "dataset/results/tables",
    "dataset/results/figures",
    "dataset/results/models",
    "dataset/results/reports",
]

for d in DIRS:
    os.makedirs(d, exist_ok=True)
    print(f"  ✓ {d}/")
print()


# ============================================================
# SETUP 2: AUTO-GENERATE MASTER KOORDINAT (jika belum ada)
# ============================================================
print("=" * 70)
print("SETUP 2: Cek Master Koordinat")
print("=" * 70)

def generate_master_koordinat(path):
    """Generate master_koordinat_id.csv berisi Lat/Lon 514 kab/kota Indonesia.
    Sumber: koordinat ibukota kabupaten/kota (BPS-level accuracy)."""

    # Koordinat 34 provinsi (untuk fallback)
    PROV_FALLBACK = {
        "ACEH": (4.0, 97.0), "SUMATERA UTARA": (2.0, 99.0),
        "SUMATERA BARAT": (-0.5, 100.5), "RIAU": (0.5, 101.5),
        "KEPULAUAN RIAU": (1.0, 104.0), "JAMBI": (-1.5, 103.0),
        "BENGKULU": (-3.5, 102.5), "SUMATERA SELATAN": (-3.0, 104.5),
        "KEP. BANGKA BELITUNG": (-2.5, 106.5), "LAMPUNG": (-4.5, 105.5),
        "BANTEN": (-6.5, 106.0), "DKI JAKARTA": (-6.2, 106.8),
        "JAWA BARAT": (-7.0, 107.5), "JAWA TENGAH": (-7.3, 110.0),
        "D I YOGYAKARTA": (-7.8, 110.4), "JAWA TIMUR": (-7.7, 112.5),
        "BALI": (-8.4, 115.2), "NUSA TENGGARA BARAT": (-8.5, 117.0),
        "NUSA TENGGARA TIMUR": (-9.0, 121.5), "KALIMANTAN BARAT": (-0.3, 111.0),
        "KALIMANTAN TENGAH": (-2.0, 113.0), "KALIMANTAN SELATAN": (-3.0, 115.0),
        "KALIMANTAN TIMUR": (-0.5, 117.0), "KALIMANTAN UTARA": (3.0, 117.0),
        "SULAWESI UTARA": (1.3, 124.5), "SULAWESI TENGAH": (-1.5, 121.0),
        "SULAWESI SELATAN": (-4.0, 120.0), "SULAWESI TENGGARA": (-4.0, 122.5),
        "SULAWESI BARAT": (-2.7, 119.0), "GORONTALO": (0.7, 122.0),
        "MALUKU": (-3.5, 129.0), "MALUKU UTARA": (0.7, 128.0),
        "PAPUA BARAT": (-1.5, 133.0), "PAPUA": (-4.0, 138.0),
    }

    # Subset koordinat per provinsi (kab/kota utama, sisanya pakai fallback provinsi)
    COORDS = {
        "ACEH": {"Simeulue": (2.6167, 96.0833), "Aceh Singkil": (2.4167, 97.7667),
                 "Aceh Selatan": (3.1167, 97.4667), "Aceh Tenggara": (3.5667, 97.6833),
                 "Aceh Timur": (4.55, 97.7), "Aceh Tengah": (4.6167, 96.85),
                 "Aceh Barat": (4.45, 96.1833), "Aceh Besar": (5.45, 95.4),
                 "Pidie": (5.35, 95.9667), "Bireuen": (5.2, 96.7), "Aceh Utara": (5.1833, 96.7),
                 "Aceh Barat Daya": (4.0167, 96.7333), "Gayo Lues": (3.9167, 97.0833),
                 "Aceh Jaya": (4.7333, 95.6), "Nagan Raya": (4.1833, 96.5333),
                 "Aceh Tamiang": (4.5833, 97.95), "Bener Meriah": (4.7, 96.85),
                 "Pidie Jaya": (5.0833, 96.1833), "Kota Banda Aceh": (5.55, 95.3167),
                 "Kota Sabang": (5.8833, 95.3167), "Kota Lhokseumawe": (5.1833, 96.7),
                 "Kota Langsa": (4.4667, 97.9667), "Kota Subulussalam": (2.6333, 98.0)},
        "SUMATERA UTARA": {"Nias": (0.7833, 97.6333), "Mandailing Natal": (0.5833, 99.3333),
                          "Tapanuli Selatan": (1.1833, 99.4), "Tapanuli Tengah": (1.7, 98.8),
                          "Tapanuli Utara": (2.1167, 98.9), "Dairi": (2.5667, 98.2),
                          "Karo": (3.1167, 98.4667), "Deli Serdang": (3.55, 98.6833),
                          "Simalungun": (2.9833, 99.0), "Asahan": (2.7667, 99.3667),
                          "Labuhanbatu": (2.35, 99.8833), "Labuhanbatu Selatan": (1.7, 100.0667),
                          "Labuhanbatu Utara": (2.4, 99.7), "Nias Selatan": (0.5833, 97.7),
                          "Nias Barat": (1.0833, 97.3333), "Nias Utara": (1.2667, 97.5167),
                          "Padang Lawas": (1.3, 99.65), "Padang Lawas Utara": (1.5, 99.7),
                          "Samosir": (2.5833, 98.85), "Serdang Bedagai": (3.5667, 99.1167),
                          "Batu Bara": (3.05, 99.4667), "Toba Samosir": (2.5333, 99.0),
                          "Kota Medan": (3.5833, 98.6667), "Kota Pematangsiantar": (2.9667, 99.0667),
                          "Kota Sibolga": (1.75, 98.7833), "Kota Tanjungbalai": (2.9667, 99.8),
                          "Kota Tebingtinggi": (3.3333, 99.15), "Kota Binjai": (3.6, 98.4833),
                          "Kota Padang Sidempuan": (1.3833, 99.2667), "Kota Gunungsitoli": (1.2833, 97.6167)},
        "JAWA BARAT": {"Bogor": (-6.5833, 106.7833), "Sukabumi": (-6.9333, 106.9333),
                       "Cianjur": (-6.8167, 107.15), "Bandung": (-6.9167, 107.6),
                       "Garut": (-7.2167, 107.9), "Tasikmalaya": (-7.35, 108.2),
                       "Ciamis": (-7.3333, 108.35), "Kuningan": (-6.9833, 108.4833),
                       "Cirebon": (-6.7, 108.55), "Majalengka": (-6.75, 108.2333),
                       "Sumedang": (-6.85, 107.9333), "Indramayu": (-6.3333, 108.3333),
                       "Subang": (-6.5667, 107.75), "Purwakarta": (-6.55, 107.4333),
                       "Karawang": (-6.3, 107.3), "Bekasi": (-6.2333, 106.9833),
                       "Bandung Barat": (-6.75, 107.55), "Pangandaran": (-7.7, 108.65),
                       "Kota Bogor": (-6.5833, 106.7833), "Kota Sukabumi": (-6.9333, 106.9333),
                       "Kota Bandung": (-6.9167, 107.6), "Kota Cirebon": (-6.7333, 108.55),
                       "Kota Bekasi": (-6.2333, 106.9833), "Kota Depok": (-6.4, 106.8333),
                       "Kota Cimahi": (-6.8833, 107.55), "Kota Tasikmalaya": (-7.3333, 108.2167),
                       "Kota Banjar": (-7.3667, 108.55)},
        "DKI JAKARTA": {"Kepulauan Seribu": (-5.4667, 106.6),
                        "Kota Jakarta Selatan": (-6.3, 106.8),
                        "Kota Jakarta Timur": (-6.2333, 106.9),
                        "Kota Jakarta Pusat": (-6.1833, 106.8333),
                        "Kota Jakarta Barat": (-6.1667, 106.75),
                        "Kota Jakarta Utara": (-6.1333, 106.85)},
        "JAWA TENGAH": {"Cilacap": (-7.7, 109.0), "Banyumas": (-7.5, 109.25),
                       "Purbalingga": (-7.3833, 109.35), "Banjarnegara": (-7.3833, 109.6167),
                       "Kebumen": (-7.6667, 109.65), "Purworejo": (-7.7, 110.0167),
                       "Wonosobo": (-7.3667, 109.9167), "Magelang": (-7.5, 110.2167),
                       "Boyolali": (-7.3333, 110.6), "Klaten": (-7.7, 110.6),
                       "Sukoharjo": (-7.6667, 110.8333), "Wonogiri": (-7.9333, 110.9333),
                       "Karanganyar": (-7.65, 110.9667), "Sragen": (-7.4333, 111.0),
                       "Grobogan": (-7.05, 110.9167), "Blora": (-6.9667, 111.4),
                       "Rembang": (-6.7167, 111.35), "Pati": (-6.75, 111.0833),
                       "Kudus": (-6.8, 110.85), "Jepara": (-6.5833, 110.6667),
                       "Demak": (-6.8833, 110.6333), "Semarang": (-7.1667, 110.4333),
                       "Temanggung": (-7.2667, 110.1833), "Kendal": (-7.0167, 110.2),
                       "Batang": (-6.9167, 109.75), "Pekalongan": (-6.8833, 109.6667),
                       "Pemalang": (-7.05, 109.3833), "Tegal": (-6.85, 109.1333),
                       "Brebes": (-7.05, 109.0),
                       "Kota Magelang": (-7.4667, 110.2167), "Kota Surakarta": (-7.5667, 110.8333),
                       "Kota Salatiga": (-7.3333, 110.5), "Kota Semarang": (-6.9667, 110.4167),
                       "Kota Pekalongan": (-6.8833, 109.6667), "Kota Tegal": (-6.8667, 109.1333)},
        "D I YOGYAKARTA": {"Kulon Progo": (-7.7, 110.1667), "Bantul": (-7.9, 110.3333),
                          "Gunung Kidul": (-7.9667, 110.6), "Sleman": (-7.7, 110.35),
                          "Kota Yogyakarta": (-7.8, 110.3667)},
        "JAWA TIMUR": {"Pacitan": (-8.0, 111.1167), "Ponorogo": (-7.7, 111.4667),
                       "Trenggalek": (-8.05, 111.7), "Tulungagung": (-8.0667, 111.9),
                       "Blitar": (-8.0833, 112.1833), "Kediri": (-7.8333, 112.0333),
                       "Malang": (-7.9667, 112.6333), "Lumajang": (-8.1167, 113.2167),
                       "Jember": (-8.1667, 113.7), "Banyuwangi": (-8.2167, 114.3667),
                       "Bondowoso": (-7.9333, 113.8333), "Situbondo": (-7.7, 114.0),
                       "Probolinggo": (-7.75, 113.2167), "Pasuruan": (-7.6333, 112.9),
                       "Sidoarjo": (-7.45, 112.7), "Mojokerto": (-7.4667, 112.4333),
                       "Jombang": (-7.55, 112.2333), "Nganjuk": (-7.5333, 111.9),
                       "Madiun": (-7.6333, 111.5333), "Magetan": (-7.65, 111.3667),
                       "Ngawi": (-7.4167, 111.45), "Bojonegoro": (-7.2333, 111.8833),
                       "Tuban": (-6.9667, 112.0333), "Lamongan": (-7.1167, 112.1833),
                       "Gresik": (-7.15, 112.5667), "Bangkalan": (-7.0833, 112.8333),
                       "Sampang": (-7.0, 113.2333), "Pamekasan": (-7.0833, 113.4667),
                       "Sumenep": (-7.0, 113.85),
                       "Kota Kediri": (-7.8333, 112.0333), "Kota Blitar": (-8.1, 112.1667),
                       "Kota Malang": (-7.9667, 112.6333), "Kota Probolinggo": (-7.75, 113.2167),
                       "Kota Pasuruan": (-7.6333, 112.9), "Kota Madiun": (-7.6333, 111.5333),
                       "Kota Surabaya": (-7.25, 112.75), "Kota Batu": (-7.8667, 112.5167)},
        "BALI": {"Jembrana": (-8.3833, 114.6667), "Tabanan": (-8.4667, 115.0333),
                 "Badung": (-8.4833, 115.1833), "Gianyar": (-8.5167, 115.3167),
                 "Klungkung": (-8.5333, 115.4), "Bangli": (-8.45, 115.35),
                 "Karangasem": (-8.4167, 115.5833), "Buleleng": (-8.1167, 115.05),
                 "Kota Denpasar": (-8.65, 115.2167)},
    }

    # Cek apakah dataset utama tersedia (untuk extract list kab/kota)
    if not os.path.exists(PATH_DATA):
        print(f"  ⚠ Dataset utama tidak ditemukan, generate koordinat minimal (34 provinsi)")
        rows = []
        for prov, (lat, lon) in PROV_FALLBACK.items():
            rows.append({"Provinsi": prov, "Wilayah": f"DEFAULT_{prov}",
                        "Latitude": lat, "Longitude": lon})
        pd.DataFrame(rows).to_csv(path, index=False)
        return

    # Extract kab/kota dari dataset utama
    df = pd.read_csv(PATH_DATA)
    rows = []
    n_explicit = 0
    n_fallback = 0
    for _, r in df.iterrows():
        prov = str(r['Provinsi']).upper().strip()
        wil = str(r['Kab/Kota']).strip()
        coord = COORDS.get(prov, {}).get(wil)
        if coord is None:
            coord = PROV_FALLBACK.get(prov, (-3.0, 120.0))
            n_fallback += 1
        else:
            n_explicit += 1
        rows.append({"Provinsi": prov, "Wilayah": wil,
                    "Latitude": coord[0], "Longitude": coord[1]})

    pd.DataFrame(rows).drop_duplicates(subset=["Wilayah", "Provinsi"]).to_csv(path, index=False)
    print(f"  ✓ Generated {len(rows)} baris ({n_explicit} eksplisit, {n_fallback} fallback provinsi)")

if not os.path.exists(PATH_COORDS):
    print(f"  ⚠ Master koordinat tidak ditemukan, auto-generate...")
    generate_master_koordinat(PATH_COORDS)
else:
    # Cek apakah jumlah baris match dengan dataset utama
    df_check_coords = pd.read_csv(PATH_COORDS)
    df_check_data = pd.read_csv(PATH_DATA)
    if len(df_check_coords) < len(df_check_data) * 0.9:
        print(f"  ⚠ Master koordinat hanya {len(df_check_coords)} baris, butuh ~{len(df_check_data)} baris.")
        print(f"    Auto-regenerate dengan koordinat lengkap...")
        generate_master_koordinat(PATH_COORDS)
    else:
        print(f"  ✓ Master koordinat sudah ada: {PATH_COORDS} ({len(df_check_coords)} baris)")
print()


# ============================================================
# SETUP 3: VALIDASI DATASET UTAMA
# ============================================================
print("=" * 70)
print("SETUP 3: Validasi Dataset Utama")
print("=" * 70)
if not os.path.exists(PATH_DATA):
    print(f"  ✗ Dataset tidak ditemukan: {PATH_DATA}")
    print()
    print("CARA MENDAPATKAN DATASET:")
    print("  1. Download dari sumber BPS / repository internal")
    print("  2. Letakkan file CSV di: dataset/Klasifikasi Tingkat Kemiskinan di Indonesia.csv")
    print("  3. Atau ubah PATH_DATA di baris ~150 skrip ini")
    print()
    print("Kolom yang dibutuhkan (case-sensitive):")
    print("  - Provinsi")
    print("  - Kab/Kota")
    print("  - Persentase Penduduk Miskin (P0) Menurut Kabupaten/Kota (Persen)")
    print("  - Rata-rata Lama Sekolah Penduduk 15+ (Tahun)")
    print("  - Pengeluaran per Kapita Disesuaikan (Ribu Rupiah/Orang/Tahun)")
    print("  - Umur Harapan Hidup (Tahun)")
    print("  - Persentase rumah tangga yang memiliki akses terhadap sanitasi layak")
    print("  - Tingkat Pengangguran Terbuka")
    print("  - PDRB atas Dasar Harga Konstan menurut Pengeluaran (Rupiah)")
    sys.exit(1)
else:
    df_check = pd.read_csv(PATH_DATA)
    print(f"  ✓ Dataset ditemukan: {PATH_DATA}")
    print(f"    Shape: {df_check.shape[0]} baris × {df_check.shape[1]} kolom")
print()


# ============================================================
# SETUP 4: LOGGING CONFIGURATION
# ============================================================
logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('dataset/results/execution.log', encoding='utf-8')
    ],
    force=True
)


# ============================================================
# LANGKAH 1: IMPOR PUSTAKA (sudah dilakukan di atas)
# ============================================================
print("=" * 70)
print("LANGKAH 1: Impor Pustaka — SUDAH DILAKUKAN")
print("=" * 70)
print("  pandas, numpy, matplotlib, seaborn, sklearn, hdbscan,")
print("  scipy, scikit_posthocs, libpysal, esda")
print()


# ============================================================
# LANGKAH 2: MEMUAT DATASET
# ============================================================
logging.info("LANGKAH 2: Memuat Dataset")

df = pd.read_csv(PATH_DATA)
print(f"Ukuran dataset awal: {df.shape[0]} baris, {df.shape[1]} kolom\n")

FEATURES = [
    "Persentase Penduduk Miskin (P0) Menurut Kabupaten/Kota (Persen)",
    "Rata-rata Lama Sekolah Penduduk 15+ (Tahun)",
    "Pengeluaran per Kapita Disesuaikan (Ribu Rupiah/Orang/Tahun)",
    "Umur Harapan Hidup (Tahun)",
    "Persentase rumah tangga yang memiliki akses terhadap sanitasi layak",
    "Tingkat Pengangguran Terbuka",
    "PDRB atas Dasar Harga Konstan menurut Pengeluaran (Rupiah)"
]

FEATURE_MAPPING = {
    "Persentase Penduduk Miskin (P0) Menurut Kabupaten/Kota (Persen)": "Persentase_Penduduk_Miskin",
    "Rata-rata Lama Sekolah Penduduk 15+ (Tahun)": "Rata_rata_Lama_Sekolah",
    "Pengeluaran per Kapita Disesuaikan (Ribu Rupiah/Orang/Tahun)": "Pengeluaran_per_Kapita",
    "Umur Harapan Hidup (Tahun)": "UHH",
    "Persentase rumah tangga yang memiliki akses terhadap sanitasi layak": "Sanitasi_Layak",
    "Tingkat Pengangguran Terbuka": "TPT",
    "PDRB atas Dasar Harga Konstan menurut Pengeluaran (Rupiah)": "PDRB_Konstan",
}
MAPPED_FEATURES = list(FEATURE_MAPPING.values())

# ============================================================
# DOMAIN MAX + BOBOT PER FITUR
# ============================================================
# Normalisasi range: setiap fitur dinormalisasi ke [0,1] berdasarkan nilai maksimal domain
# Fitur POSITIF (makin tinggi makin baik): UHH, RLS, PDRB, Pengeluaran, Sanitasi
# Fitur NEGATIF (makin rendah makin baik): Kemiskinan, TPT

DOMAIN_MAX = {
    'UHH': 80,                       # tahun (standar WHO negara maju)
    'Rata_rata_Lama_Sekolah': 15,    # tahun (setara lulus SMA, standar OECD)
    'PDRB_Konstan': 1_000_000_000_000,  # 1 triliun rupiah (ceiling regional)
    'Persentase_Penduduk_Miskin': 50,    # 50% worst case scenario
    'Pengeluaran_per_Kapita': 25000,     # 25 ribu rupiah (middle income country)
    'Sanitasi_Layak': 100,               # 100% universal access (SDG 6)
    'TPT': 15,                           # 15% ambang krisis pengangguran
}

# Bobot per fitur (total = 1.0) — berdasarkan domain knowledge
# UHH paling penting (indikator kualitas hidup), PDRB kedua (ekonomi),
# TPT & RLS ketiga (pengangguran & pendidikan), sisanya sekunder
FEATURE_WEIGHTS = {
    'UHH': 0.25,                        # 25% — indikator kualitas hidup utama
    'PDRB_Konstan': 0.20,               # 20% — indikator ekonomi utama
    'TPT': 0.15,                         # 15% — pengangguran
    'Rata_rata_Lama_Sekolah': 0.15,      # 15% — pendidikan
    'Persentase_Penduduk_Miskin': 0.10,  # 10% — kemiskinan
    'Pengeluaran_per_Kapita': 0.10,      # 10% — daya beli
    'Sanitasi_Layak': 0.05,              # 5%  — infrastruktur
}

# Fitur positif (makin tinggi makin sejahtera)
POSITIVE_FEATURES = ['UHH', 'Rata_rata_Lama_Sekolah', 'PDRB_Konstan',
                     'Pengeluaran_per_Kapita', 'Sanitasi_Layak']
# Fitur negatif (makin rendah makin sejahtera)
NEGATIVE_FEATURES = ['Persentase_Penduduk_Miskin', 'TPT']

# Konversi numerik & imputasi median
for col in FEATURES:
    if df[col].dtype == object:
        df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '.'), errors='coerce')
    df[col] = df[col].fillna(df[col].median())

df = df[['Provinsi', 'Kab/Kota'] + FEATURES].copy()
df.rename(columns=FEATURE_MAPPING, inplace=True)

# Merge master koordinat
def _normalize_wilayah(s):
    s = str(s).upper().strip()
    s = re.sub(r'\s+', ' ', s)
    is_kota = s.startswith('KOTA ')
    s = re.sub(r'^(KABUPATEN|KAB\.?|KOTA)\s+', '', s).strip()
    s = re.sub(r'\s+', ' ', s).strip()
    return f"KOTA {s}" if is_kota else f"KAB. {s}"

df_coords = pd.read_csv(PATH_COORDS)
df['_key_w'] = df['Kab/Kota'].apply(_normalize_wilayah)
df['_key_p'] = df['Provinsi'].apply(lambda x: str(x).upper().strip())
df_coords['_key_w'] = df_coords['Wilayah'].apply(_normalize_wilayah)
df_coords['_key_p'] = df_coords['Provinsi'].apply(lambda x: str(x).upper().strip())

df = df.merge(
    df_coords[['_key_w', '_key_p', 'Latitude', 'Longitude']],
    on=['_key_w', '_key_p'], how='left'
).drop(columns=['_key_w', '_key_p'])

# Imputasi missing coords
missing_mask = df['Latitude'].isna()
if missing_mask.any():
    prov_mean = df.groupby('Provinsi')[['Latitude', 'Longitude']].transform('mean')
    df[['Latitude', 'Longitude']] = df[['Latitude', 'Longitude']].fillna(prov_mean)

jumlah_kosong = df[MAPPED_FEATURES].isnull().sum().sum()
print(f"Jumlah nilai kosong pada kolom fitur: {jumlah_kosong}")
print(f"Ukuran dataset setelah dibersihkan: {df.shape[0]} baris, {df.shape[1]} kolom\n")


# ============================================================
# LANGKAH 3: PRA-PEMROSESAN (Yeo-Johnson + IsolationForest)
# ============================================================
logging.info("LANGKAH 3: Pra-pemrosesan Data")

X_raw = df[MAPPED_FEATURES].values
pt = PowerTransformer(method='yeo-johnson', standardize=True)
X_scaled = pt.fit_transform(X_raw)

print("Statistik Deskriptif Fitur Terstandar (Yeo-Johnson):")
df_terstandar = pd.DataFrame(X_scaled, columns=MAPPED_FEATURES)
print(df_terstandar.describe().round(4))
print()

iso = IsolationForest(contamination=0.05, random_state=42)
outlier_labels = iso.fit_predict(X_scaled)
inliers_mask = outlier_labels == 1
df_normal = df[inliers_mask].copy()
df_anomali = df[~inliers_mask].copy()
X_normal_scaled = X_scaled[inliers_mask]

print(f"Total observasi (raw)     : {len(df)}")
print(f"Inliers (df_normal)       : {len(df_normal)} ({len(df_normal)/len(df)*100:.1f}%)")
print(f"Outliers (df_anomali)     : {len(df_anomali)} ({len(df_anomali)/len(df)*100:.1f}%)")
print()


# ============================================================
# LANGKAH 3.5: MORAN'S I PRE-CLUSTERING (SPATIAL CLUSTERABILITY CHECK)
# ============================================================
# Mengapa Moran's I sebagai tahap proses (bukan hanya evaluasi)?
# - Moran's I pre-clustering mengukur apakah data sudah punya struktur spasial
#   sebelum clustering dilakukan. Jika I ~ 0 (random), clustering spasial tidak akan
#   bermakna. Jika I > 0 (clustered), hasil clustering kemungkinan akan ter-spatially-clustered.
# - Dengan mengukur Moran's I SEBELUM dan SESUDAH clustering, kita bisa validasi
#   apakah clustering memperkuat atau melemahkan autokorelasi spasial.
# ============================================================
logging.info("LANGKAH 3.5: Moran's I Pre-Clustering (Spatial Clusterability Check)")

print("=" * 60)
print("LANGKAH 3.5: Moran's I Pre-Clustering")
print("=" * 60)
print("Tujuan: Verifikasi clusterability spasial SEBELUM clustering dilakukan.")
print("        Jika I > 0 dan p < 0.05, data punya struktur spasial yang signifikan.")
print()

# Subset: hanya baris dengan koordinat valid
df_spatial_pre = df_normal.dropna(subset=['Latitude', 'Longitude']).reset_index(drop=True)
coords_pre = df_spatial_pre[['Longitude', 'Latitude']].values

if len(df_spatial_pre) >= 10:
    w_pre = KNN.from_array(coords_pre, k=5)
    w_pre.transform = 'r'
    print(f"KNN weights: k=5, n={w_pre.n}")
    print()
    print("Moran's I Pre-Clustering (7 fitur kesejahteraan):")
    print(f"  {'Fitur':<30} {'I':>8} {'E[I]':>10} {'z':>10} {'p':>10} {'Interpretasi'}")
    print("  " + "-" * 90)

    moran_pre_results = {}
    for var_name in MAPPED_FEATURES:
        y = df_spatial_pre[var_name].values
        mi = Moran(y, w_pre, permutations=999)
        moran_pre_results[var_name] = {
            'I': float(mi.I), 'EI': float(mi.EI),
            'z': float(mi.z_sim), 'p': float(mi.p_sim)
        }
        if mi.I > 0 and mi.p_sim < 0.05:
            interp = "POSITIVE clustered"
        elif mi.I < 0 and mi.p_sim < 0.05:
            interp = "NEGATIVE dispersed"
        else:
            interp = "random (not significant)"
        print(f"  {var_name:<30} {mi.I:>8.4f} {mi.EI:>10.6f} {mi.z_sim:>10.4f} {mi.p_sim:>10.4f} {interp}")

    print()
    n_significant = sum(1 for v in moran_pre_results.values() if v['p'] < 0.05)
    print(f"Fitur dengan autokorelasi spasial signifikan: {n_significant}/{len(MAPPED_FEATURES)}")
    if n_significant >= 5:
        pass
    elif n_significant >= 3:
        print("⚠ Data memiliki struktur spasial moderat — clustering spasial cukup bermakna.")
    else:
        print("⚠ Data memiliki struktur spasial lemah — clustering mungkin tidak ter-spatially-clustered.")
    print()
else:
    print("⚠ Skip Moran's I pre-clustering — observasi spasial terlalu sedikit.")
    moran_pre_results = {}
    print()


# ============================================================
# LANGKAH 4: PENCARIAN MODEL OPTIMAL (HDBSCAN AUTO-SELECTION)
# HDBSCAN auto-selection dipakai sebagai satu-satunya metode penentuan K
# ============================================================
print("[3/4] 🔄 Menjalankan model Hybrid HDBSCAN-KMeans...")
logging.info("LANGKAH 4: Pencarian Model Optimal (HDBSCAN Auto-Selection)")

best_k = 0
best_labels_hdb = None
best_valid_clusters = []
best_mcs, best_ms = None, None

for mcs in range(5, 15):
    for ms in range(3, 8):
        hdb = hdbscan.HDBSCAN(min_cluster_size=mcs, min_samples=ms)
        hdb_labels = hdb.fit_predict(X_normal_scaled)
        valid_clusters = [lbl for lbl in np.unique(hdb_labels) if lbl != -1]
        n_noise = (hdb_labels == -1).sum()
        if 2 <= len(valid_clusters) <= 5:
            best_k = len(valid_clusters)
            best_valid_clusters = valid_clusters
            best_labels_hdb = hdb_labels
            best_mcs, best_ms = mcs, ms
            print(f"  ✓ DIPILIH: mcs={mcs}, ms={ms} → k={best_k}, noise={n_noise}")
            break
    if best_k > 0:
        break

K_OPTIMAL = best_k
print(f"\Jumlah klaster optimal (HDBSCAN auto): K = {K_OPTIMAL}\n")


# ============================================================
# LANGKAH 5: HYBRID HDBSCAN→KMEANS + WCVI + STABILITAS
# ============================================================
logging.info("LANGKAH 5: Hybrid HDBSCAN-KMeans + WCVI")

# Hitung centroid dari HDBSCAN density peaks
centroids = []
for cluster_id in best_valid_clusters:
    mask = best_labels_hdb == cluster_id
    centroids.append(np.mean(X_normal_scaled[mask], axis=0))
centroids_array = np.array(centroids)

kmeans_model = KMeans(n_clusters=K_OPTIMAL, init=centroids_array, n_init=1, random_state=42)
label_klaster = kmeans_model.fit_predict(X_normal_scaled)

df_normal["Klaster"] = label_klaster

CLUSTER_NAMES = {
    0: "Berkembang Industrial",
    1: "Berkembang Rentan",
    2: "Berkembang Seimbang",
    3: "Maju & Urbanized",
    -1: "Entitas Atipikal",
}
df_normal["Tipologi"] = df_normal["Klaster"].map(CLUSTER_NAMES)

print(f"Model Hybrid HDBSCAN-KMeans K={K_OPTIMAL} berhasil dilatih.")
print(f"\nJumlah daerah per klaster:")
print(df_normal["Klaster"].value_counts().sort_index())
print()

# WCVI components
def calculate_hopkins(X, random_state=42):
    d = X.shape[1]
    n = len(X)
    m = int(0.1 * n)
    rng = np.random.default_rng(random_state)
    nbrs = NearestNeighbors(n_neighbors=1).fit(X)
    rand_X = rng.choice(n, size=m, replace=False)
    ujd, wjd = [], []
    for j in range(m):
        u_dist, _ = nbrs.kneighbors(
            rng.uniform(np.amin(X, axis=0), np.amax(X, axis=0), d).reshape(1, -1),
            2, return_distance=True
        )
        ujd.append(u_dist[0][1])
        w_dist, _ = nbrs.kneighbors(X[rand_X[j]].reshape(1, -1), 2, return_distance=True)
        wjd.append(w_dist[0][1])
    H = sum(ujd) / (sum(ujd) + sum(wjd))
    return float(H) if not np.isnan(H) else 0.0

def calculate_r_squared(X, labels):
    grand_mean = np.mean(X, axis=0)
    ss_total = np.sum((X - grand_mean) ** 2)
    ss_within = 0
    for i in np.unique(labels):
        cluster_points = X[labels == i]
        cluster_centroid = np.mean(cluster_points, axis=0)
        ss_within += np.sum((cluster_points - cluster_centroid) ** 2)
    return float(1.0 - (ss_within / ss_total))

def calculate_rf_accuracy(X, labels):
    rf = RandomForestClassifier(n_estimators=100, random_state=42, oob_score=True)
    rf.fit(X, labels)
    return float(rf.oob_score_)

hopkins_score = calculate_hopkins(X_normal_scaled, random_state=42)
r_squared = calculate_r_squared(X_normal_scaled, label_klaster)
rf_accuracy = calculate_rf_accuracy(X_normal_scaled, label_klaster)

w1, w2, w3 = 0.30, 0.40, 0.30
wcvi_score = (w1 * hopkins_score) + (w2 * r_squared) + (w3 * rf_accuracy)

print(f"  Hopkins Tendency (H)    : {hopkins_score:.4f}  (w1={w1}, contribution={w1*hopkins_score:.4f})")
print(f"  R-Squared (EESS%)       : {r_squared*100:.2f}%  (w2={w2}, contribution={w2*r_squared:.4f})")
print(f"  RF OOB Accuracy         : {rf_accuracy*100:.2f}%  (w3={w3}, contribution={w3*rf_accuracy:.4f})")
print(f"  WCVI (composite)        : {wcvi_score:.4f}")
print()

# Stabilitas ARI (10-seed KMeans)
baseline_kmeans = KMeans(n_clusters=K_OPTIMAL, random_state=42, n_init=10)
baseline_labels = baseline_kmeans.fit_predict(X_normal_scaled)
ari_scores = []
for seed in range(1, 11):
    km_test = KMeans(n_clusters=K_OPTIMAL, random_state=seed, n_init=10)
    test_labels = km_test.fit_predict(X_normal_scaled)
    ari_scores.append(adjusted_rand_score(baseline_labels, test_labels))

ari_mean = float(np.mean(ari_scores))
ari_std = float(np.std(ari_scores))
print(f"  ARI Mean : {ari_mean:.4f}  (>0.8 = sangat stabil)")
print(f"  ARI Std  : {ari_std:.4f}  (<0.1 = konsisten)")
print()

# Feature Importance
rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
rf_model.fit(X_normal_scaled, label_klaster)
importances = rf_model.feature_importances_
indices = np.argsort(importances)[::-1]

for rank in range(len(MAPPED_FEATURES)):
    fitur_nama = MAPPED_FEATURES[indices[rank]]
    print(f"  Peringkat {rank+1}: {fitur_nama:<30} -> Importance: {importances[indices[rank]]:.4f}")
print()

final_labels = label_klaster


# ============================================================
# LANGKAH 5.5: NORMALISASI RANGE + BOBOT + COMPOSITE WELFARE SCORE
# ============================================================
# - Setiap fitur diberi bobot berbeda sesuai dataset
# - Normalisasi range ke [0,1] berdasarkan nilai maksimal domain
# - Composite Welfare Score = Σ (bobot × nilai_normalisasi)
# - Implementasi Opsi B: bobot untuk evaluasi saja, clustering tetap (sudah final)
# ============================================================
logging.info("LANGKAH 5.5: Normalisasi Range + Composite Welfare Score")

print("=" * 60)
print("LANGKAH 5.5: Normalisasi Range + Composite Welfare Score")
print("=" * 60)
print("Domain Max per Fitur:")
for feat, max_val in DOMAIN_MAX.items():
    bobot = FEATURE_WEIGHTS[feat]
    print(f"  {feat:<30} max={max_val:>15,}  bobot={bobot*100:.0f}%")
print()

# Fungsi normalisasi range
def normalize_feature(value, feature_name):
    """Normalisasi fitur ke [0,1] berdasarkan domain max.
    Fitur positif: value/max
    Fitur negatif: 1 - (value/max)
    """
    max_val = DOMAIN_MAX[feature_name]
    if max_val == 0:
        return 0.0
    if feature_name in NEGATIVE_FEATURES:
        return max(0.0, min(1.0, 1.0 - (value / max_val)))
    else:
        return max(0.0, min(1.0, value / max_val))

# Hitung normalisasi + composite score untuk setiap daerah
print("Menghitung Composite Welfare Score per daerah...")
welfare_scores = []
normalized_data = []

for idx, row in df_normal.iterrows():
    norm_values = {}
    score = 0.0
    for feat in MAPPED_FEATURES:
        norm_val = normalize_feature(row[feat], feat)
        norm_values[feat] = norm_val
        score += FEATURE_WEIGHTS[feat] * norm_val
    welfare_scores.append(score)
    normalized_data.append(norm_values)

df_normal['Welfare_Score'] = welfare_scores

# Tambahkan kolom normalisasi per fitur
for feat in MAPPED_FEATURES:
    df_normal[f'{feat}_norm'] = [nd[feat] for nd in normalized_data]

print(f"\nStatistik Composite Welfare Score:")
print(f"  Min  : {min(welfare_scores):.4f}")
print(f"  Mean : {np.mean(welfare_scores):.4f}")
print(f"  Max  : {max(welfare_scores):.4f}")
print(f"  Std  : {np.std(welfare_scores):.4f}")
print()

# Welfare score per klaster
print("Welfare Score per Klaster:")
for k in sorted(df_normal['Klaster'].unique()):
    subset = df_normal[df_normal['Klaster'] == k]
    tipologi = CLUSTER_NAMES.get(k, f"Cluster {k}")
    mean_score = subset['Welfare_Score'].mean()
    print(f"  Klaster {k} ({tipologi:<25}): mean={mean_score:.4f}, n={len(subset)}")
print()

# Simpan data dengan welfare score
df_normal.to_csv('dataset/processed/data_normal_with_scores.csv', index=False)
print()


# ============================================================
# LANGKAH 6: PROFILING & VISUALISASI AKHIR
# ============================================================
print("[4/4] 🔄 Membangun profil akhir untuk Dashboard...")
logging.info("LANGKAH 6: Profiling & Visualisasi")

df_scaled_normal = pd.DataFrame(X_normal_scaled, columns=MAPPED_FEATURES)
df_scaled_normal['Cluster'] = final_labels
centroid_scaled = df_scaled_normal.groupby('Cluster')[MAPPED_FEATURES].mean()
centroid_original = pt.inverse_transform(centroid_scaled.values)

profil_klaster = pd.DataFrame(centroid_original, columns=MAPPED_FEATURES, index=centroid_scaled.index)
profil_klaster.index = [CLUSTER_NAMES.get(int(i), f"Cluster {int(i)}") for i in profil_klaster.index]
sizes = df_scaled_normal['Cluster'].value_counts().sort_index()
profil_klaster['Jumlah Daerah'] = sizes.values

if len(df_anomali) > 0:
    anomali_scaled = pt.transform(df_anomali[MAPPED_FEATURES].values)
    anomali_centroid = np.mean(anomali_scaled, axis=0).reshape(1, -1)
    anomali_original = pt.inverse_transform(anomali_centroid)[0]
    anomali_series = pd.Series(anomali_original, index=MAPPED_FEATURES)
    anomali_series['Jumlah Daerah'] = len(df_anomali)
    anomali_series.name = "Klaster Spasial Eksklusif (Subsisten Tertinggal)"
    profil_klaster = pd.concat([profil_klaster, anomali_series.to_frame().T])

print(profil_klaster.round(2))
print()

profil_klaster.to_csv('dataset/results/tables/profiling_akhir.csv')
centroid_scaled_export = centroid_scaled.copy()
centroid_scaled_export.index = [CLUSTER_NAMES.get(int(i), f"Cluster {int(i)}") for i in centroid_scaled_export.index]
centroid_scaled_export.to_csv('dataset/results/tables/centroid_scaled_per_cluster.csv')


# Figur 1: Heatmap Korelasi
plt.figure(figsize=(8, 6))
corr = df[MAPPED_FEATURES].corr(method='spearman')
sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f", linewidths=0.5, cbar=True)
plt.title('Spearman Correlation Heatmap (Raw Data)', fontsize=12, fontweight='bold', pad=15)
plt.tight_layout()
plt.savefig('dataset/results/figures/heatmap_korelasi.png', dpi=300)
plt.close()

# Figur 2: PCA 2D Scatter
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_normal_scaled)
plt.figure(figsize=(9, 6))
cluster_labels_str = [CLUSTER_NAMES.get(lbl, f"Cluster {lbl}") for lbl in final_labels]
sns.scatterplot(x=X_pca[:, 0], y=X_pca[:, 1], hue=cluster_labels_str, palette='tab10',
                s=45, alpha=0.8, edgecolors='none')
plt.title('2D PCA Projection of Hybrid Clustering', fontsize=12, fontweight='bold', pad=15)
plt.xlabel(f'PCA Component 1 ({pca.explained_variance_ratio_[0]:.2%} Variance)')
plt.ylabel(f'PCA Component 2 ({pca.explained_variance_ratio_[1]:.2%} Variance)')
plt.legend(title='Tipologi Wilayah', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.savefig('dataset/results/figures/pca_clustering.png', dpi=300)
plt.close()

# Figur 3: Boxplot TPT
plt.figure(figsize=(8, 5))
sns.boxplot(x='Tipologi', y='TPT', data=df_normal, palette='tab10')
plt.title('Distribusi TPT per Tipologi Wilayah', fontsize=11, fontweight='bold', pad=10)
plt.xlabel('Tipologi Wilayah')
plt.ylabel('TPT (%)')
plt.xticks(rotation=15)
plt.tight_layout()
plt.savefig('dataset/results/figures/boxplot_tpt.png', dpi=300)
plt.close()

# Figur 4: Scatter PDRB vs TPT
plt.figure(figsize=(9, 6))
sns.scatterplot(x='PDRB_Konstan', y='TPT', hue='Tipologi', palette='tab10',
                data=df_normal, s=50, alpha=0.7)
plt.xscale('log')
plt.title('Paradoks Jawa-Sentris: PDRB vs Pengangguran Terbuka',
          fontsize=12, fontweight='bold', pad=15)
plt.xlabel('PDRB atas Dasar Harga Konstan (Rupiah)')
plt.ylabel('Tingkat Pengangguran Terbuka (%)')
plt.legend(title='Tipologi Wilayah', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.savefig('dataset/results/figures/scatter_pdrb_tpt.png', dpi=300)
plt.close()

# Simpan data
df_normal.to_csv('dataset/processed/data_normal.csv', index=False)
df_anomali.to_csv('dataset/processed/klaster_spasial_eksklusif.csv', index=False)
print()


# ============================================================
# LANGKAH 6.5: PETA CHOROPLETH (PROYEKSI GEOSPASIAL WILAYAH INDONESIA)
# ============================================================
# Mengapa Choropleth penting untuk HKI?
# - Visualisasi spasial hasil clustering pada peta Indonesia nyata
# - Memvalidasi secara visual bahwa klaster ter-spatially-clustered (pola regional)
# - Memberi "face validity" untuk claim inovasi: pembuat kebijakan bisa lihat langsung
#   wilayah mana yang masuk klaster tertentu (mis. "Maju & Urbanized" terkonsentrasi di Jawa)
#
# Sumber GeoJSON: TheMaggieSimpson/IndonesiaGeoJSON (GitHub)
# File: kota-kabupaten.json (~96 MB, 502 records polygon batas administrasi)
# ============================================================
logging.info("LANGKAH 6.5: Peta Choropleth (Proyeksi Geospasial)")

print("=" * 60)
print("LANGKAH 6.5: Peta Choropleth Wilayah Indonesia")
print("=" * 60)

GEOJSON_PATH = "dataset/kota-kabupaten.json"
GEOJSON_URL = "https://raw.githubusercontent.com/TheMaggieSimpson/IndonesiaGeoJSON/main/kota-kabupaten.json"

# Auto-download GeoJSON jika belum ada
if not os.path.exists(GEOJSON_PATH):
    print(f"  ⚠ File GeoJSON tidak ditemukan, mendownload dari GitHub...")
    print(f"    URL: {GEOJSON_URL}")
    print(f"    Ukuran: ~96 MB (mungkin butuh 1-2 menit)")
    try:
        response = requests.get(GEOJSON_URL, timeout=120)
        response.raise_for_status()
        with open(GEOJSON_PATH, 'wb') as f:
            f.write(response.content)
        size_mb = os.path.getsize(GEOJSON_PATH) / (1024 * 1024)
        print(f"  ✓ GeoJSON berhasil didownload: {size_mb:.1f} MB")
    except Exception as e:
        print(f"  ✗ Gagal download GeoJSON: {e}")
        print(f"    Skip choropleth, lanjut ke Langkah 7.")
        GEOJSON_PATH = None
else:
    size_mb = os.path.getsize(GEOJSON_PATH) / (1024 * 1024)
    print(f"  ✓ GeoJSON sudah ada: {GEOJSON_PATH} ({size_mb:.1f} MB)")

if GEOJSON_PATH and os.path.exists(GEOJSON_PATH):
    try:
        # Load GeoJSON
        print(f"\n  Loading GeoJSON dengan geopandas...")
        gdf = gpd.read_file(GEOJSON_PATH)
        print(f"  ✓ GeoJSON loaded: {len(gdf)} polygon kabupaten/kota")
        print(f"    Kolom: {list(gdf.columns)[:8]}...")

        # Normalisasi nama untuk matching dengan dataset
        # Strategi: gunakan NAME_2 (kab/kota) + NAME_1 (provinsi) dari GeoJSON
        # Match dengan Kab/Kota + Provinsi dari df_normal
        def normalize_for_match(s):
            """Normalisasi nama untuk matching: uppercase, strip, remove prefix."""
            s = str(s).upper().strip()
            s = re.sub(r'\s+', ' ', s)
            # Hapus prefix KABUPATEN/KAB./KOTA
            s = re.sub(r'^(KABUPATEN|KAB\.?|KOTA)\s+', '', s).strip()
            return s

        # Normalisasi nama provinsi (handle special cases)
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

        # Tambah kolom key untuk matching di GeoJSON
        gdf['_key_w'] = gdf['NAME_2'].apply(normalize_for_match)
        gdf['_key_p'] = gdf['NAME_1'].apply(normalize_prov)

        # Tambah kolom key untuk matching di df_normal
        df_normal['_key_w'] = df_normal['Kab/Kota'].apply(normalize_for_match)
        df_normal['_key_p'] = df_normal['Provinsi'].apply(normalize_prov)

        # Merge: GeoJSON + df_normal (left join, keep all polygons)
        gdf_merged = gdf.merge(
            df_normal[['_key_w', '_key_p', 'Klaster', 'Tipologi', 'TPT', 'PDRB_Konstan']],
            on=['_key_w', '_key_p'], how='left'
        )

        n_matched = gdf_merged['Klaster'].notna().sum()
        n_total = len(gdf_merged)
        print(f"\n  Matching GeoJSON dengan dataset:")
        print(f"    Polygon GeoJSON: {n_total}")
        print(f"    Berhasil match: {n_matched} ({n_matched/n_total*100:.1f}%)")
        print(f"    Tidak match: {n_total - n_matched} (akan tampil abu-abu)")

        # Warna klaster
        CLUSTER_COLORS = {
            0: '#E8505B',  # Berkembang Industrial - merah
            1: '#F18F01',  # Berkembang Rentan - oranye
            2: '#1E3A8A',  # Berkembang Seimbang - biru tua
            3: '#0F766E',  # Maju & Urbanized - hijau toska
        }
        CLUSTER_NAMES_SHORT = {
            0: 'Berkembang Industrial',
            1: 'Berkembang Rentan',
            2: 'Berkembang Seimbang',
            3: 'Maju & Urbanized',
        }

        # Plot choropleth
        fig, ax = plt.subplots(1, 1, figsize=(18, 12))

        # Plot polygon yang tidak match (abu-abu)
        gdf_no_match = gdf_merged[gdf_merged['Klaster'].isna()]
        if len(gdf_no_match) > 0:
            gdf_no_match.plot(ax=ax, color='#E5E7EB', edgecolor='white', linewidth=0.3)

        # Plot polygon per klaster
        for cluster_id in sorted(df_normal['Klaster'].unique()):
            subset = gdf_merged[gdf_merged['Klaster'] == cluster_id]
            if len(subset) > 0:
                subset.plot(ax=ax, color=CLUSTER_COLORS.get(cluster_id, '#888888'),
                           edgecolor='white', linewidth=0.3,
                           label=f'Klaster {cluster_id}: {CLUSTER_NAMES_SHORT.get(cluster_id, "")}')

        # Legend manual (karena geopandas plot tidak auto-legend dengan cara ini)
        import matplotlib.patches as mpatches
        legend_patches = []
        for cluster_id in sorted(df_normal['Klaster'].unique()):
            patch = mpatches.Patch(color=CLUSTER_COLORS.get(cluster_id, '#888888'),
                                   label=f'Klaster {cluster_id}: {CLUSTER_NAMES_SHORT.get(cluster_id, "")}')
            legend_patches.append(patch)
        legend_patches.append(mpatches.Patch(color='#E5E7EB', label='Tidak Terklasifikasi'))
        ax.legend(handles=legend_patches, title='Tipologi Spasial HKI',
                  fontsize=10, title_fontsize=11, loc='lower left')

        ax.set_title('Peta Choropleth Hasil Klasterisasi Kesejahteraan Wilayah Indonesia\n'
                     '(Hybrid HDBSCAN→KMeans dengan WCVI)',
                     fontsize=14, fontweight='bold', pad=15, color='#1E3A8A')
        ax.set_xlabel('Longitude', fontsize=10)
        ax.set_ylabel('Latitude', fontsize=10)
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig('dataset/results/figures/choropleth_indonesia.png', dpi=300, bbox_inches='tight')
        plt.close()
        print(f"\n  ✓ Peta choropleth disimpan: dataset/results/figures/choropleth_indonesia.png")

        # Choropleth kedua: TPT (variabel kontinyu)
        fig, ax = plt.subplots(1, 1, figsize=(18, 12))
        gdf_merged.plot(column='TPT', ax=ax, legend=True, cmap='YlOrRd',
                       missing_kwds={'color': '#E5E7EB', 'label': 'Tidak ada data'},
                       edgecolor='white', linewidth=0.3)
        ax.set_title('Peta Choropleth Tingkat Pengangguran Terbuka (TPT) per Kabupaten/Kota\n'
                     '(Skala Warna: Kuning=Rendah, Merah=Tinggi)',
                     fontsize=14, fontweight='bold', pad=15, color='#1E3A8A')
        ax.set_xlabel('Longitude', fontsize=10)
        ax.set_ylabel('Latitude', fontsize=10)
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig('dataset/results/figures/choropleth_tpt.png', dpi=300, bbox_inches='tight')
        plt.close()
        print(f"  ✓ Peta choropleth TPT disimpan: dataset/results/figures/choropleth_tpt.png")

        # Choropleth ketiga: PDRB (variabel kontinyu)
        fig, ax = plt.subplots(1, 1, figsize=(18, 12))
        gdf_merged['PDRB_Log10'] = np.log10(gdf_merged['PDRB_Konstan'].clip(lower=1))
        gdf_merged.plot(column='PDRB_Log10', ax=ax, legend=True, cmap='viridis',
                       missing_kwds={'color': '#E5E7EB', 'label': 'Tidak ada data'},
                       edgecolor='white', linewidth=0.3)
        ax.set_title('Peta Choropleth PDRB atas Dasar Harga Konstan (Log10) per Kabupaten/Kota\n'
                     '(Skala Warna: Ungu=Rendah, Kuning=Tinggi)',
                     fontsize=14, fontweight='bold', pad=15, color='#1E3A8A')
        ax.set_xlabel('Longitude', fontsize=10)
        ax.set_ylabel('Latitude', fontsize=10)
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig('dataset/results/figures/choropleth_pdrb.png', dpi=300, bbox_inches='tight')
        plt.close()
        print(f"  ✓ Peta choropleth PDRB disimpan: dataset/results/figures/choropleth_pdrb.png")

        # Cleanup kolom _key
        df_normal.drop(columns=['_key_w', '_key_p'], inplace=True, errors='ignore')

        print(f"\n  Total 3 peta choropleth berhasil dibuat:")
        print(f"    1. choropleth_indonesia.png (warna by klaster)")
        print(f"    2. choropleth_tpt.png (warna by TPT)")
        print(f"    3. choropleth_pdrb.png (warna by PDRB log10)")
        print()

    except Exception as e:
        print(f"\n  ✗ Error saat membuat choropleth: {e}")
        print(f"    Skip choropleth, lanjut ke Langkah 7.")
        print()


# ============================================================
# LANGKAH 7: ANALISIS LANJUTAN
# ============================================================
logging.info("LANGKAH 7: Analisis Lanjutan")

# Kruskal-Wallis
tpt_groups = [df_normal.loc[df_normal['Klaster'] == i, 'TPT'].values for i in range(K_OPTIMAL)]
kruskal_result = kruskal(*tpt_groups)
print(f"  H-statistic : {kruskal_result.statistic:.4f}")
print(f"  p-value     : {kruskal_result.pvalue:.6e}")
sig_kw = "Ya (p<0.05)" if kruskal_result.pvalue < 0.05 else "Tidak"
print(f"  Signifikan  : {sig_kw}\n")

# Dunn post-hoc
dunn_matrix = sp.posthoc_dunn(tpt_groups, p_adjust='bonferroni')
dunn_display = dunn_matrix.copy()
dunn_labels = [CLUSTER_NAMES.get(i, f"Cluster {i}") for i in range(K_OPTIMAL)]
dunn_display.index = dunn_labels
dunn_display.columns = dunn_labels
dunn_display.to_csv('dataset/results/tables/dunn_posthoc_tpt.csv')
print(dunn_display.round(6))
print()

# Spearman
spearman_result = spearmanr(df['PDRB_Konstan'].values, df['TPT'].values)
print(f"  Rho     : {spearman_result.statistic:.4f}")
print(f"  p-value : {spearman_result.pvalue:.6e}\n")

# Chi-Square + Cramer's V
jawa_provinces = ["JAWA BARAT", "JAWA TENGAH", "D I YOGYAKARTA", "JAWA TIMUR", "BANTEN", "DKI JAKARTA"]
df_normal['Is_Jawa'] = df_normal['Provinsi'].apply(
    lambda x: "Jawa" if str(x).upper() in jawa_provinces else "Luar Jawa"
)
crosstab = pd.crosstab(df_normal['Is_Jawa'], df_normal['Klaster'])
chi2, p_val, dof, _ = chi2_contingency(crosstab)
n = crosstab.values.sum()
min_dim = min(crosstab.shape) - 1
cramers_v = np.sqrt(chi2 / (n * min_dim))
print(f"  Chi2      : {chi2:.4f}")
print(f"  p-value   : {p_val:.6e}")
print(f"  Cramer's V: {cramers_v:.4f}")
v_interp = "KUAT" if cramers_v > 0.5 else "MODERAT" if cramers_v > 0.3 else "LEMAH"
print(f"  Interpretasi: asosiasi {v_interp}\n")

# Moran's I Post-Clustering (komparasi dengan pre-clustering di Langkah 3.5)
print("Komparasi dengan Moran's I Pre-Clustering (Langkah 3.5):")
print()
if 'Latitude' in df_normal.columns:
    df_spatial = df_normal.dropna(subset=['Latitude', 'Longitude']).reset_index(drop=True)
    coords = df_spatial[['Longitude', 'Latitude']].values
    w = KNN.from_array(coords, k=5)
    w.transform = 'r'
    moran_results = {}
    for var_name in ['TPT', 'PDRB_Konstan', 'Klaster']:
        y = df_spatial[var_name].values
        if var_name == 'Klaster':
            y = y.astype(float)
        mi = Moran(y, w, permutations=999)
        moran_results[var_name] = {'I': float(mi.I), 'EI': float(mi.EI),
                                   'z': float(mi.z_sim), 'p': float(mi.p_sim)}
        # Cari pre-clustering value untuk komparasi
        pre_val = moran_pre_results.get(var_name, {}).get('I', None)
        if pre_val is not None:
            delta = mi.I - pre_val
            delta_interp = "MEMPERKUAT" if delta > 0.01 else ("MELEMAHKAN" if delta < -0.01 else "stabil")
            print(f"  {var_name:15s}: I_post = {mi.I:.4f} | I_pre = {pre_val:.4f} | Δ = {delta:+.4f} [{delta_interp}]")
        else:
            print(f"  {var_name:15s}: I = {mi.I:.4f} | z = {mi.z_sim:.4f} | p = {mi.p_sim:.4f}")
    print()
    print("Catatan: Moran's I Klaster mengukur apakah hasil clustering ter-spatially-clustered.")
    print("         Jika I_klaster > 0 dan p < 0.05, klaster punya pola regional yang signifikan.")
print()



# ============================================================
# LANGKAH 7.5: NARRATIVE DATA EXPORT (untuk Dashboard Streamlit)
# ============================================================
# - Hasil & Evaluasi berisi sentences pemetaan
# - Hitung z-score per fitur vs centroid klaster
# - Identifikasi fitur dominan per daerah
# - Export CSV narrative-ready untuk dashboard
# ============================================================
logging.info("LANGKAH 7.5: Narrative Data Export")

print("=" * 60)
print("LANGKAH 7.5: Narrative Data Export")
print("=" * 60)

# Compute Welfare_Score and normalized features for anomalies (outliers)
df_anomali['Klaster'] = -1
df_anomali['Tipologi'] = "Entitas Atipikal"

welfare_scores_anomali = []
normalized_data_anomali = []

for idx, row in df_anomali.iterrows():
    norm_values = {}
    score = 0.0
    for feat in MAPPED_FEATURES:
        norm_val = normalize_feature(row[feat], feat)
        norm_values[feat] = norm_val
        score += FEATURE_WEIGHTS[feat] * norm_val
    welfare_scores_anomali.append(score)
    normalized_data_anomali.append(norm_values)

df_anomali['Welfare_Score'] = welfare_scores_anomali
for feat in MAPPED_FEATURES:
    df_anomali[f'{feat}_norm'] = [nd[feat] for nd in normalized_data_anomali]

# Combine normal and anomaly data
df_combined = pd.concat([df_normal, df_anomali], ignore_index=True)

# Hitung centroid + std per klaster (dalam skala asli, including cluster -1)
centroid_per_cluster = {}
std_per_cluster = {}
for k in sorted(df_combined['Klaster'].unique()):
    subset = df_combined[df_combined['Klaster'] == k]
    centroid_per_cluster[k] = subset[MAPPED_FEATURES].mean()
    std_per_cluster[k] = subset[MAPPED_FEATURES].std()

# Hitung z-score per fitur per daerah
z_score_data = []
for idx, row in df_combined.iterrows():
    k = row['Klaster']
    z_scores = {}
    for feat in MAPPED_FEATURES:
        centroid_val = centroid_per_cluster[k][feat]
        std_val = std_per_cluster[k][feat]
        if pd.notna(std_val) and std_val > 0:
            z_scores[feat] = (row[feat] - centroid_val) / std_val
        else:
            z_scores[feat] = 0.0
    z_score_data.append(z_scores)

# Buat DataFrame z-score
z_score_df = pd.DataFrame(z_score_data)
z_score_df.columns = [f'{feat}_zscore' for feat in MAPPED_FEATURES]

# Gabungkan dengan df_combined
df_narrative = pd.concat([df_combined.reset_index(drop=True), z_score_df], axis=1)

# Identifikasi fitur dominan per daerah (top-3 berdasarkan |z-score| × bobot)
dominant_features = []
for idx, row in df_narrative.iterrows():
    k = row['Klaster']
    feature_scores = []
    for feat in MAPPED_FEATURES:
        z = abs(row[f'{feat}_zscore'])
        weight = FEATURE_WEIGHTS[feat]
        rf_importance = importances[MAPPED_FEATURES.index(feat)]
        # Combined score: z-score × bobot × RF importance
        combined = z * weight * rf_importance
        feature_scores.append((feat, z, weight, rf_importance, combined))
    feature_scores.sort(key=lambda x: x[4], reverse=True)
    top3 = feature_scores[:3]
    dominant_features.append({
        'top1_feat': top3[0][0],
        'top1_z': top3[0][1],
        'top1_weight': top3[0][2],
        'top2_feat': top3[1][0],
        'top2_z': top3[1][1],
        'top3_feat': top3[2][0],
        'top3_z': top3[2][1],
    })

dominant_df = pd.DataFrame(dominant_features)
df_narrative = pd.concat([df_narrative, dominant_df], axis=1)

# Simpan narrative-ready data
df_narrative.to_csv('dataset/processed/narrative_data.csv', index=False)
print(f"  Kolom: {list(df_narrative.columns)[:15]}...")
print()

# Simpan juga centroid + std per klaster untuk dashboard
centroid_export = pd.DataFrame(centroid_per_cluster).T
centroid_export.index = [CLUSTER_NAMES.get(k, f"Cluster {k}") for k in centroid_export.index]
centroid_export.to_csv('dataset/results/tables/centroid_per_cluster.csv')

std_export = pd.DataFrame(std_per_cluster).T
std_export.index = [CLUSTER_NAMES.get(k, f"Cluster {k}") for k in std_export.index]
std_export.to_csv('dataset/results/tables/std_per_cluster.csv')

print(f"  - dataset/results/tables/centroid_per_cluster.csv")
print(f"  - dataset/results/tables/std_per_cluster.csv")
print()

# Simpan feature weights + domain max untuk dashboard
weights_export = pd.DataFrame([
    {'Feature': feat, 'Domain_Max': DOMAIN_MAX[feat], 'Weight': FEATURE_WEIGHTS[feat],
     'Type': 'Positive' if feat in POSITIVE_FEATURES else 'Negative',
     'RF_Importance': importances[MAPPED_FEATURES.index(feat)]}
    for feat in MAPPED_FEATURES
])
weights_export.to_csv('dataset/results/tables/feature_weights.csv', index=False)
print()



# ============================================================
print("=" * 70)
print("=" * 70)
print("Silakan jalankan dashboard dengan perintah:")
print("streamlit run dashboard/app.py")
print("=" * 70)
