# Design Specification Revision: SENUWU Dashboard UX/UI Enhancements

**Date**: 2026-07-15  
**Status**: Approved  
**Topic**: User Experience and Visual Redesign Refinement for SENUWU

---

## 1. Global Visual and Typography Guidelines
1. **Consistency of Rounded Corners (*Border Radius*)**:
   - Apply a consistent `border-radius: 8px` across all inputs, selectboxes, buttons, tables, drag-and-drop areas, and warning/success popup modals.
2. **Typography & Styling**:
   - Maintain the original fonts (Cinzel, Cormorant Garamond, Crimson Pro) and original colors.
   - All foreign/technical terms (in English) used in the Indonesian interface MUST be italicized (e.g., *machine learning*, *hybrid clustering*, *outliers*, *noise*, *drag-and-drop*, *oversampling*, *multiclass classification*, etc.).
3. **Card & Drop Shadow**:
   - Remove solid borders from validation cards and containers, replacing them with a very soft, blurry drop shadow to create a floating/depth effect: `box-shadow: 0 10px 30px rgba(92, 64, 51, 0.05);`.

---

## 2. Page-by-Page Specifications

### 2.1 Home Page (Beranda)
1. **Model Evaluation Section**:
   - Replace the three separate columns with a unified, elegant 2-column card layout.
     - **Left Column (Width: 35%)**:
       - Category text (small, uppercase Cinzel): "KEANDALAN SISTEM" in gold/brass (`#8a620b`).
       - Title (Cormorant Garamond): "Evaluasi Model" in soft black (`#1C1714`).
       - Status Indicator: "✦ Tervalidasi" in green (`#2E7D32`).
     - **Right Column (Width: 65%)**:
       - Refined narrative text: *"Untuk menjamin keandalan pemetaan, model ini dievaluasi menggunakan metrik statistika berbasis data resmi BPS tahun 2024."* (Clean, objective wording; removed overclaims like "secara ketat" and duplicates of "BPS 2024").
       - Inline list of validation metrics: **WCVI** ● **Hopkins Statistic** ● **ARI** ● **Random Forest** (styled in gold bold, separated by gold circular bullets, without any background boxes).
   - Remove all star ornaments or decorative elements from this section.

### 2.2 Search Page (Cari)
1. **Color Hierarchy**:
   - Change the color of narrative output subheaders (Ringkasan, Interpretasi, Karakteristik Klaster, Faktor yang Paling Berpengaruh, Kesimpulan) from gold to soft black (`#1C1714`) to ensure they do not clash with map cluster colors. Gold is only used for thin dividers.
2. **Dynamic Year Filter**:
   - Make the "Tahun Dataset" filter dynamic by querying unique year values directly from the database (`df['Tahun'].unique()`) to automatically support future dataset updates.
   - Inject a similar dynamic year selectbox to the Choropleth map on the Home page (Beranda) to sync the map data with the selected year.

### 2.3 Info Page (Metodologi & Profiling)
1. **Dynamic Background Copywriting**:
   - Update static copy to avoid absolute numbers like "514 kabupaten/kota" and "tahun 2024". The new phrasing is:
     > *"...SENUWU dikembangkan untuk menguji dinamika tersebut menggunakan data spasial berbasis klaster. Mengolah dataset resmi BPS lintas tahun yang mencakup seluruh kabupaten dan kota di Indonesia, pengelompokan ini mengintegrasikan tujuh indikator kesejahteraan utama..."*
   - Italicize the word *outliers* in step "03 Pengolahan Data".
2. **Feature Importance Plotly Bar Chart**:
   - Plot all 7 features horizontally.
   - Color them with a custom continuous brown gradient from Tan (`#D2B48C`) to Dark Brown (`#4A3B32`) based on the importance score. Hide the color bar.
   - Adjust left margin to `l=160` to prevent label clipping. Axis tick font color must be soft black (`#1C1714`).
   - Configure the hover tooltip with a cream background, 80% opacity (`rgba(243, 239, 233, 0.8)`), dark text (`#1C1714`), and a thin brass border (`#9C8B7A`).
3. **Cluster Profiling Table**:
   - Apply a soft black background (`#1C1714`) with white text to the table header row.
   - Retain the existing heatmap color gradients (`YlGn` and `YlOrRd`) inside cells.

### 2.4 Update Data Page
1. **Form Layout**:
   - Tab Names: Rename tabs to "Tambah Data Satuan" and "Unggah Dataset (CSV)".
   - Compact Layout: Reduce vertical spacing. Arrange input fields vertically in two columns:
     - **Left Column**: Provinsi, Kabupaten/Kota, Tahun.
     - **Right Column**: Latitude, Longitude.
2. **Minimalist Uploader**:
   - Design a minimal drag-and-drop file uploader area with a dashed border (`#9C8B7A`), a clean upload arrow icon, text *"Seret dan lepas file di sini atau klik untuk memilih file"*, and a rounded grey button *"Pilih File"*.
   - Remove the columns requirement box and the "Unduh Template CSV" button/text entirely.
3. **Centered Glassmorphism Modals**:
   - Centered dialog popups overlayed on a dark background with 25% opacity (`rgba(0, 0, 0, 0.25)`).
   - Glassmorphism effect with `backdrop-filter: blur(12px)`.
   - Soft warning colors: soft green (`#E8F5E9` background, `#2E7D32` text) for Success, soft red/orange (`#FFEBEE` background, `#C62828` text) for Warning/Error.
   - Professional, flowing copywriting for descriptions. Clear action buttons (with 8px border radius) and a close (X) button in the top-right corner.

### 2.5 Sidebar Menu
1. **Dividers & Menu Items**:
   - Keep the original ornate star dividers (`ui_ornate_divider()`), page icons, text fonts, and descriptions.
2. **Title & Version Text**:
   - Remove all icons from the title "SENUWU" (no bank icon) and the version text "Sistem Pemetaan v2.0" (no map-fill icon).
3. **Selected Page Indicator**:
   - Highlight the currently active page using a cream background (`#F3EFE9`) with dark text (`#1C1714`) and bold font weight to improve navigability.
