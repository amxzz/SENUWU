# SENUWU Feature Map

## 1. System Overview

SENUWU (Sistem Informasi Analitik Ketimpangan Wilayah) is an enterprise grade geospatial analytics and decision support platform engineered to model regional welfare polarization and provide empirical validation for regional development disparities (Java-centric vs Outer Java) across Indonesia.

The platform combines a hybrid unsupervised machine learning pipeline (Isolation Forest, HDBSCAN, and K-Means), rigorous spatial autocorrelation analysis (Moran's I), non-parametric post-hoc statistical hypothesis testing, and an interactive Academia-themed decision support dashboard built on Streamlit.

```
+-----------------------------------------------------------------------------------+
|                                  SENUWU PLATFORM                                  |
+-------------------------+-------------------------------+-------------------------+
|  Pillar 1: Data & ML    |  Pillar 2: Academia Interface |  Pillar 3: Narrative &  |
|  Analytical Pipeline    |  & Interactive Visualization  |  Decision Support Engine|
+-------------------------+-------------------------------+-------------------------+
| - Data Ingestion & Imput| - Volume I: Beranda           | - Z-Score Deviation     |
| - Yeo-Johnson Transform |   * Hero Display Section      |   Calculator            |
| - Isolation Forest      |   * Model Reliability Card    | - Determinant Feature   |
| - Pre-Clustering Spatial|   * Folium Choropleth Map     |   Ranking Matrix        |
|   Moran's I Check       |   * Cluster Overview Grid     | - Automated 5-Section   |
| - HDBSCAN Auto-Search   | - Volume II: Cari             |   Policy Dossier        |
| - Seeded K-Means (K=4)  |   * Cascading Filter Bar      | - Real-Time Geospatial  |
| - WCVI Metric Engine    |   * Region Dossier Card       |   Hover Summary         |
| - Random Forest OOB     |   * Structured Narrative      |                         |
| - ARI Stability Testing | - Volume III: Update Data     |                         |
| - Post-Hoc Hypothesis   |   * Single Region Predictor   |                         |
|   (Kruskal, Dunn, Chi2) |   * Batch CSV Ingestion       |                         |
| - Welfare Score Scaling |   * Glassmorphism Modals      |                         |
|                         | - Volume IV: Info             |                         |
|                         |   * Methodology Workflow      |                         |
|                         |   * Plotly Feature Importance |                         |
|                         |   * Profile Heatmap Matrix    |                         |
|                         |   * Academic Credits          |                         |
+-------------------------+-------------------------------+-------------------------+
|                      Pillar 4: Planned Novelty Roadmap                            |
|  * Counterfactual Policy Simulator  * Spatio-Temporal Disparity Tracking          |
|  * Automated Policy Brief Exporter  * Dynamic Adaptive Spatial Weights Matrix     |
|  * LLM-Augmented Policy Action Recommender                                        |
+-----------------------------------------------------------------------------------+
```

---

## 2. Pillar 1: Data and Machine Learning Pipeline

### 1.1 Data Ingestion and Validation
- **Source Dataset**: Official BPS socioeconomic data covering 514 regencies and cities across 34 Indonesian provinces (`dataset/Klasifikasi Tingkat Kemiskinan di Indonesia.csv`).
- **Feature Set**: 7 essential regional development indicators:
  1. `UHH` (Umur Harapan Hidup, Life Expectancy at Birth, Years): Positive indicator, weight = 25%, domain max = 80 years.
  2. `PDRB_Konstan` (Regional Gross Domestic Product at Constant Prices, IDR): Positive indicator, weight = 20%, domain max = IDR 1,000,000,000,000.
  3. `TPT` (Tingkat Pengangguran Terbuka, Open Unemployment Rate, %): Negative indicator, weight = 15%, domain max = 15%.
  4. `Rata_rata_Lama_Sekolah` (Mean Years of Schooling, Years): Positive indicator, weight = 15%, domain max = 15 years.
  5. `Persentase_Penduduk_Miskin` (Poverty Headcount Ratio P0, %): Negative indicator, weight = 10%, domain max = 50%.
  6. `Pengeluaran_per_Kapita` (Adjusted Real Per Capita Expenditure, Thousand IDR/Year): Positive indicator, weight = 10%, domain max = 25,000 (IDR 25 Million).
  7. `Sanitasi_Layak` (Access to Improved Sanitation, %): Positive indicator, weight = 5%, domain max = 100%.
- **Median Imputation**: Automatic null handling across all numerical indicator columns preserving robust medians.
- **Geographic Registry**: Automated master coordinate integration (`dataset/raw/master_koordinat_id.csv`) mapping latitude and longitude to 514 administrative units with provincial centroid fallbacks.

### 1.2 Transformation and Anomaly Filtering
- **Power Transformation**: Yeo-Johnson standardization (`PowerTransformer(method='yeo-johnson', standardize=True)`) to eliminate skewness and stabilize variance across indicators.
- **Isolation Forest Outlier Detection**: Identifies 26 spatial and socioeconomic anomalies (contamination = 0.05, 5.1% of dataset) isolated from the core developmental distribution, preventing distortion of cluster centroids.

### 1.3 Pre-Clustering Spatial Autocorrelation (Moran's I)
- **Spatial Weight Matrix**: Row-standardized K-Nearest Neighbors (KNN k=5) constructed from geographic coordinates.
- **Global Moran's I Verification**: Statistical confirmation that all 7 indicators exhibit significant positive spatial clustering prior to model execution (all p = 0.001, confirming regional dependency).

### 1.4 Hybrid Density-Centroid Clustering
- **HDBSCAN Parameter Grid Search**: Automated grid exploration across `min_cluster_size` in [5..14] and `min_samples` in [3..7]. Automatically selects `min_cluster_size=5` and `min_samples=3` to establish 4 stable density peaks.
- **Density-Seeded K-Means (K=4)**: Uses HDBSCAN density cluster centroids as deterministic initial seeds for K-Means, eliminating random initialization instability.

### 1.5 Multi-Metric Validity Assessment (WCVI)
- **Welfare Clustering Validity Index (WCVI)**: Proprietary composite metric formulation balancing three statistical dimensions:
  $$WCVI = (0.30 \times Hopkins) + (0.40 \times R^2) + (0.30 \times RF_{OOB})$$
  - *Hopkins Tendency (H)*: Measures clustering tendency against uniform randomness (H = 0.7183).
  - *R-Squared / EESS%*: Proportion of multivariate variance explained by cluster structure (R2 = 49.11%).
  - *Random Forest Out-of-Bag (OOB) Accuracy*: Classifiability of cluster boundaries across 100 estimators (OOB = 89.75%).
  - *Composite Score*: Verified at 0.6812.
- **Adjusted Rand Index (ARI) Stability**: 10-seed randomization test validating cluster persistence (Mean ARI = 0.8966, Std = 0.0405).

### 1.6 Post-Hoc Hypothesis Testing and Empirical Proofs
- **Java-Centric Paradox Proof (Spearman Rank Correlation)**: Positive correlation between PDRB and TPT (rho = 0.5056, p < 0.001), demonstrating that high economic capacity in urban centers is paradoxically coupled with high frictional unemployment.
- **Kruskal-Wallis and Dunn-Bonferroni Test**: Non-parametric ANOVA demonstrating highly significant variance in unemployment across clusters (H = 187.05, p < 0.001).
- **Spatial Association Test (Chi-Square and Cramer's V)**: Statistically confirms strong regional dependency between Java vs Outer Java location and welfare typology (Chi2 = 205.27, p < 0.001, Cramer's V = 0.6486).
- **Post-Clustering Moran's I**: Proves cluster assignments themselves are spatially clustered (I = 0.1788, z = 6.6863, p = 0.001).

### 1.7 Composite Welfare Score Computation
- Normalized multi-criteria scoring assigning each regency a single scalar score in [0.0, 1.0]:
  $$\text{Score} = \sum_{i=1}^7 w_i \times \text{norm}(x_i)$$
- Directional normalization: positive indicators scale as $x / \text{max}$, negative indicators scale as $1 - (x / \text{max})$.

---

## 3. Pillar 2: Academia Interface and Visualization Suite

### 2.1 Academia Design System
- **Typography**: Cormorant Garamond (display/hero headings), Crimson Pro (narrative body and reading text), Cinzel (action buttons, overline labels, and drop caps).
- **Color Identity**: Warm ivory/paper background (`#F9F6F0`), deep ink typography (`#1C1714`), antique brass and gold accents (`#8a620b`, `#9C8B7A`), and distinctive cluster typology badges.

### 2.2 Volume I: Beranda (Main Analytics Page)
- **Hero Display**: Formal academic framing outlining platform purpose and theoretical backing.
- **Model Reliability Card**: Two-column layout displaying system validation status, composite WCVI, Hopkins statistic, stability ARI, and Random Forest classification accuracy.
- **Interactive Geospatial Choropleth Map**:
  - Folium map engine integrating 502 simplified administrative polygons (`dataset/kota-kabupaten-simplified.json`, 2.1 MB optimized).
  - Dynamic year selector synchronized with the dataset.
  - Custom HTML hover tooltips displaying indicators and micro-narrative summaries.
- **Cluster Typology Overview**: 2x2 grid detailing the 4 primary clusters plus the atypical outlier classification.

### 2.3 Volume II: Cari (Regional Deep Dive)
- **Cascading Filter Bar**: Hierarchical selection by Year, Province, and Regency/City with automated state cleanup callbacks.
- **Dossier Header**: Cluster-colored identity card detailing primary statistics.
- **Intelligent Narrative Presentation**: Formatted academic dossier card presenting 5 sections of contextualized findings.

### 2.4 Volume III: Update Data Baru (Data Extension)
- **Tab 1: Single Region Entry**:
  - Structured 2-column input form capturing 7 indicators and coordinates.
  - Real-time Yeo-Johnson transformation and nearest centroid inference without retraining historical models.
  - Glassmorphism confirmation modal with animated blur background (`backdrop-filter: blur(12px)`).
- **Tab 2: Batch CSV Uploader**:
  - Drag and drop CSV file ingestion.
  - Automatic column header schema validation (verifying presence of required 7 indicators).
  - Glassmorphism batch preview modal reporting valid rows and predictions.

### 2.5 Volume IV: Info (Methodology & Credits)
- **Methodology Overview**: 5-stage visual workflow cards outlining the research pipeline.
- **Plotly Feature Importance Visualization**: Horizontal bar chart with copper-to-bronze gradient showing Random Forest feature contributions.
- **Cluster Profiling Matrix**: Pandas Styler dataframe with color gradients applied conditionally (green gradients for positive indicators, red gradients for negative indicators).
- **Academic Authorship & Supervision**: Credits for student developers and faculty supervisor.

---

## 4. Pillar 3: Automated Decision Support & Narrative Engine

### 3.1 Z-Score Relative Deviation Engine
- Computes standard deviation distance of each region's indicators relative to its assigned cluster centroid:
  $$z_i = \frac{x_i - \mu_{\text{cluster}, i}}{\sigma_{\text{cluster}, i}}$$
- Categorical translation:
  - $|z| \ge 2.0$: "sangat jauh di atas/bawah rata-rata klaster"
  - $|z| \ge 1.0$: "jauh di atas/bawah rata-rata klaster"
  - $|z| \ge 0.5$: "di atas/bawah rata-rata klaster"
  - $|z| < 0.5$: "mendekati / setara rata-rata klaster"

### 3.2 Dominant Welfare Determinant Selector
- Ranks indicator influence using compound score:
  $$\text{Score}_{\text{determinant}} = |z_i| \times w_i \times \text{Importance}_{\text{RF}, i}$$
- Selects top 3 dominant indicators per region explaining why that region belongs to its specific cluster.

### 3.3 Five-Section Policy Dossier Generator
1. **Ringkasan (Executive Summary)**: Overview of region, cluster membership, and composite score.
2. **Interpretasi Komparatif (Comparative Interpretation)**: Performance compared to national and cluster baselines.
3. **Karakteristik Klaster (Cluster Characteristics)**: Structural profile of the peer group.
4. **Faktor Paling Berpengaruh (Top Influencing Determinants)**: Top 3 table with directional indicators and weights.
5. **Rekomendasi Kebijakan (Policy Recommendations)**: Tailored policy prescriptions addressing specific regional bottlenecks.

---

## 5. Pillar 4: Planned Novelty Roadmap

The following high-impact novelties are scheduled for future development cycles:

### Novelty 1: Dynamic Counterfactual Policy Simulator (Sandbox Mode)
- **Concept**: Interactive policy sandbox enabling planners to adjust target indicators (e.g. reducing TPT by 2% or raising Sanitasi Layak to 90%) and observe real-time predicted shifts in Welfare Score and potential cluster transition.
- **Algorithmic Basis**: Projected Yeo-Johnson vector transformation and Euclidean distance recomputation against locked cluster centroids.
- **Value**: Transforms SENUWU from a descriptive diagnostic tool into a predictive policy simulation instrument.

### Novelty 2: Spatio-Temporal Disparity Tracking
- **Concept**: Longitudinal comparison module analyzing shifts across multiple years (e.g., 2021 to 2024).
- **Key Metrics**:
  - Delta Moran's I: Measuring whether spatial inequality is converging or diverging over time.
  - Markov Transition Matrix: Tracking probability of regions advancing from "Area Rentan" to "Transisi Seimbang" or "Sentra Industri".
- **Value**: Enables historical evaluation of regional autonomy programs and fiscal transfers (Dana Alokasi Khusus).

### Novelty 3: Automated Policy Brief Exporter
- **Concept**: One-click generation of publication-grade PDF and HTML regional dossiers.
- **Output Components**: Executive summary, radar comparison chart against national averages, choropleth snippet, and official policy recommendation table formatted for ministerial briefings.
- **Value**: Direct integration into public administration workflows without manual report preparation.

### Novelty 4: Adaptive Spatial Weights Matrix
- **Concept**: Upgrading the static KNN (k=5) spatial matrix to an adaptive multi-modal connectivity matrix combining:
  1. Geographic inverse distance contiguity.
  2. Economic gravity contiguity (inter-regional trade volume proxies).
  3. Insular connectivity (ferry and flight network graphs for archipelagic regions).
- **Value**: Eliminates artificial isolation artifacts for remote island regencies in Maluku and Papua.

### Novelty 5: LLM-Augmented Policy Action Recommender
- **Concept**: Integration of an agentic recommendation module that ingests the top-3 determinants, fiscal space categories, and regional typology to synthesize tailored, budget-feasible policy interventions aligned with RPJMN (Rencana Pembangunan Jangka Menengah Nasional) guidelines.
- **Value**: Replaces rule-based recommendation templates with deep, context-aware policy formulation.
