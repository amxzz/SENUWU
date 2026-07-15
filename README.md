# Project HKI - Pemodelan Klasterisasi Kesejahteraan Hybrid

Proyek ini berisi *pipeline Machine Learning* (HDBSCAN-KMeans Hybrid) dan Dashboard Interaktif (Streamlit) untuk memetakan kesejahteraan wilayah di Indonesia.

## Prasyarat
- Python 3.10 atau lebih baru.

## Cara Instalasi & Menjalankan (Untuk Teman/Reviewer)

**1. Buat Virtual Environment (Opsional tapi Direkomendasikan)**
Buka terminal/CMD di dalam folder ini dan jalankan:
```bash
python -m venv .venv
```

**2. Aktifkan Virtual Environment**
- Windows: `.venv\Scripts\activate`
- Mac/Linux: `source .venv/bin/activate`

**3. Install Dependencies**
```bash
pip install -r requirements.txt
```

**4. Menjalankan Pipeline Model (Opsional)**
*Jika ingin melihat proses modeling dari awal hingga akhir dan meregenerasi data:*
```bash
python scripts/pemodelan_klasterisasi_kesejahteraan.py
```

**5. Menjalankan Dashboard Interaktif**
```bash
streamlit run dashboard/app.py
```
*(Setelah command dijalankan, browser akan otomatis terbuka di `http://localhost:8501`)*

## Struktur Folder
- `dashboard/`: Berisi skrip antarmuka UI Streamlit (`app.py`).
- `scripts/`: Berisi skrip ML inti (Clean Code).
- `dataset/`: Berisi raw data (GeoJSON, CSV), hasil olahan, dan visualisasi spasial.
- `Manual Hak Cipta...docx`: Dokumen publikasi/manual komprehensif.

*Enjoy testing!*
