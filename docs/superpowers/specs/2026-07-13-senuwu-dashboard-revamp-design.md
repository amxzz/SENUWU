# Design Specification: SENUWU Dashboard Revamp

**Date**: 2026-07-13  
**Status**: Proposed  
**Topic**: Streamlit Dashboard Revamp for SENUWU (Regional Inequality Analytical Information System)

---

## 1. Executive Summary
The purpose of this specification is to redesign and enhance the SENUWU Streamlit dashboard to address feedback from the thesis advisor. The main goals are to remove/replace low-performing metrics (specifically R-Square), present model validation metrics in a clear hierarchical layout, reduce textual density on the Info page, integrate interactive visualizations (Feature Importance), and provide an elegant data-backed cluster profiling table and classification notification.

---

## 2. Page-by-Page Requirements

### 2.1 Home Page (Beranda)
The layout is restructured to present model reliability upfront and guide users logically.

1. **Hero Section (Top of Page)**:
   - Big, elegant serif title using `Cormorant Garamond` font for "SENUWU (Sistem Informasi Analitik Ketimpangan Wilayah)".
   - Clean, professional introduction explaining the platform's purpose: a welfare-based cluster visualization tool for public and governmental policy planning.

2. **Model Approach & Reliability Metrics (Below Hero, Above Map)**:
   - **Methodology Summary**: Brief narrative explaining the Hybrid Clustering approach (HDBSCAN for structural/noise detection and K-Means for final stable allocation).
   - **Composite Validation Metric (WCVI)**:
     - Center-aligned large value: **`0.681`**
     - Text description immediately below: *"Within-Cluster Variance Index (WCVI) – skor komposit validitas klaster (sangat baik)"*.
   - **Three-Column Metrics (Below WCVI)**:
     - **Left Column**: 
       - Metric Name: **Hopkins Tendency**
       - Large Value: **`0.718`**
       - Description: *Menguji tendensi pembentukan klaster alami pada data (>0.5 menandakan data layak diklaster).*
     - **Middle Column**:
       - Metric Name: **Adjusted Rand Index (ARI)**
       - Large Value: **`0.897`**
       - Description: *Menguji konsistensi dan stabilitas hasil pengelompokan di berbagai simulasi acak.*
     - **Right Column**:
       - Metric Name: **Validasi Random Forest (OOB)**
       - Large Value: **`89.75%`**
       - Description: *Tingkat akurasi prediksi model Random Forest dalam mereproduksi label klaster.*

3. **Choropleth Map Visualization**:
   - Maintain the existing interactive Folium map visualization.

4. **Cluster Summary Cards**:
   - Maintain the existing 4-cluster summary cards layout at the bottom.

---

### 2.2 Info Page (Dokumentasi)
This page is redesigned to be academic yet visually engaging, reducing text density and removing the numeric metrics section.

1. **Background & Objective**:
   - Present context in clear paragraphs without bullet points. Source data is cited from BPS 2024 covering 514 regencies/cities.

2. **Processing Flow**:
   - Render a custom HTML horizontal flowchart block:
     `[Input: 7 Indikator BPS] ➔ [Tahap 1: HDBSCAN] ➔ [Tahap 2: K-Means] ➔ [Output: Visualisasi Peta]`
     styled with modern border cards and transition arrows.

3. **Feature Importance (New Section)**:
   - Interactive horizontal bar chart using Plotly showing RF importance values for each indicator:
     - *UHH*: 0.18996
     - *PDRB_Konstan*: 0.18907
     - *Persentase_Penduduk_Miskin*: 0.15334
     - *Rata_rata_Lama_Sekolah*: 0.15058
     - *Pengeluaran_per_Kapita*: 0.13610
     - *Sanitasi_Layak*: 0.09999
     - *TPT*: 0.08096
   - Palette coordinates with the theme (brass/crimson hues).

4. **Cluster Profiling**:
   - **Academic Summary Table**: Table displaying average (centroid) values for the 7 welfare indicators across the 4 clusters, formatted cleanly (Rp, %, Years) with soft background gradient colors (green for positive, red for negative indicators) for ease of comparison.
   - **Distinct Summaries**:
     - *Urban Maju*: High Life Expectancy (UHH), lowest poverty, but higher unemployment rate (TPT) due to urbanization pull.
     - *Sentra Industri*: High economic capacity (PDRB), high Life Expectancy (UHH), moderate poverty, and high unemployment (TPT).
     - *Transisi Seimbang*: Balanced growth, low poverty and unemployment, good sanitation and purchasing power.
     - *Area Rentan*: High poverty rate, lowest PDRB capacity, poor basic sanitation, and low formal unemployment (dominant agriculture/informal sector).

5. **Team Profile**:
   - Retain existing layout.

---

### 2.3 Search Page (Cari)
- Retain the textual analysis output.
- Wrap analysis results in premium cards/panels utilizing elegant styling, card metrics, and typography spacing to improve scannability.

---

### 2.4 Update Data Page (Update Data Baru)
- Retain the administrator authentication and data entry form.
- **Classification Output**: After saving, render a premium visual card color-coded according to the predicted cluster, showing the input metrics alongside the cluster centroids.

---

## 3. Implementation Checklist & Verification Plan
- **Verification**: Run the Streamlit application locally and verify that page styling matches the mockup specifications.
- **Data Consistency**: Ensure all hardcoded metrics (`WCVI`, `Hopkins`, `ARI`, `RF OOB`) map directly to the values inside `summary_metrics.csv` and `feature_weights.csv`.
