# SENUWU Technical Specification

## 1. Overview and System Objective

SENUWU (Sistem Informasi Analitik Ketimpangan Wilayah) is a decision support and geospatial intelligence platform designed to evaluate and interpret regional welfare disparities across 514 Indonesian regencies and municipalities.

The system addresses three critical analytical requirements:
1. Identifying distinct regional development typologies without assuming spherical cluster distributions or suffering from random initialization drift.
2. Validating the empirical hypothesis that Indonesian regional development exhibits strong spatial autocorrelation and structural polarization (the Java-centric paradox).
3. Translating multidimensional statistical indices into human-readable policy dossiers for government stakeholders and development planners.

---

## 2. Mathematical Formalisms and Algorithms

### 2.1 Feature Scaling: Yeo-Johnson Power Transformation
Because regional indicators (notably PDRB and Poverty Rates) exhibit heavy right and left skews that distort distance metrics, features are transformed via the Yeo-Johnson method:

$$\psi(\lambda, y) = 
\begin{cases} 
((y + 1)^\lambda - 1) / \lambda & \text{if } \lambda \neq 0, y \ge 0 \\
\ln(y + 1) & \text{if } \lambda = 0, y \ge 0 \\
-((-y + 1)^{2 - \lambda} - 1) / (2 - \lambda) & \text{if } \lambda \neq 2, y < 0 \\
-\ln(-y + 1) & \text{if } \lambda = 2, y < 0 
\end{cases}$$

Standardization to zero mean and unit variance follows immediately:
$$z = \frac{\psi(\lambda, y) - \mu_\psi}{\sigma_\psi}$$

### 2.2 Anomaly Isolation: Isolation Forest
Outliers are filtered prior to clustering to prevent boundary distortion:
- Algorithm: `IsolationForest(contamination=0.05, random_state=42)`
- Partitioning:
  - Inliers ($N=488$, 94.9%): Directed to the core clustering pipeline.
  - Outliers ($N=26$, 5.1%): Assigned directly to Cluster -1 ("Entitas Atipikal" / Subsisten Tertinggal).

### 2.3 Spatial Autocorrelation: Global Moran's I
Spatial dependency is quantified using an adjacency matrix based on row-standardized K-Nearest Neighbors ($k=5$):

$$I = \frac{N}{\sum_{i=1}^N \sum_{j=1}^N w_{ij}} \frac{\sum_{i=1}^N \sum_{j=1}^N w_{ij}(x_i - \bar{x})(x_j - \bar{x})}{\sum_{i=1}^N (x_i - \bar{x})^2}$$

Where:
- $N = 481$ (observations with valid spatial coordinates).
- $w_{ij}$ is the spatial weight between region $i$ and region $j$.
- Under null hypothesis of spatial randomness, $E[I] = -1 / (N - 1) = -0.002083$.
- Significance is evaluated via 999 Monte Carlo permutations.

### 2.4 Hybrid Density-Centroid Clustering
1. **Density Peak Extraction (HDBSCAN)**:
   - Parameter auto-selection evaluates parameter combinations for `min_cluster_size` in [5..14] and `min_samples` in [3..7].
   - Selected configuration: `min_cluster_size=5`, `min_samples=3`.
   - Identified valid clusters: $K = 4$ (excluding noise points).
   - Centroids $\mathbf{c}_k$ are calculated as the mean vector of dense core members for each cluster $k \in \{0, 1, 2, 3\}$.
2. **K-Means Convergence**:
   - Initial centroids: $\mathbf{C}^{(0)} = \{\mathbf{c}_0, \mathbf{c}_1, \mathbf{c}_2, \mathbf{c}_3\}$.
   - Algorithm: `KMeans(n_clusters=4, init=C0, n_init=1, random_state=42)`.
   - Guaranteed deterministic convergence without random restart divergence.

### 2.5 Validation Metrics and WCVI Formulation
The Welfare Clustering Validity Index (WCVI) is computed as:

$$WCVI = (w_1 \times H) + (w_2 \times R^2) + (w_3 \times \text{Acc}_{\text{RF\_OOB}})$$

Where:
1. **Hopkins Statistic ($H$)**:
   $$H = \frac{\sum_{i=1}^m u_i}{\sum_{i=1}^m u_i + \sum_{i=1}^m w_i}$$
   Where $u_i$ is the nearest neighbor distance from synthetic uniform random points to real points, and $w_i$ is nearest neighbor distance within real points. Baseline empirical result: $H = 0.7183$ (weight $w_1 = 0.30$).
2. **Multivariate Variance Ratio ($R^2$ / EESS%)**:
   $$R^2 = 1 - \frac{\sum_{k=1}^K \sum_{i \in C_k} \|\mathbf{x}_i - \mathbf{c}_k\|^2}{\sum_{i=1}^N \|\mathbf{x}_i - \bar{\mathbf{x}}\|^2}$$
   Baseline empirical result: $R^2 = 49.11\%$ (weight $w_2 = 0.40$).
3. **Random Forest Out-of-Bag Accuracy ($\text{Acc}_{\text{RF\_OOB}}$)**:
   Classification consistency of 100 decision trees predicting cluster labels from original indicators. Baseline empirical result: $\text{Acc}_{\text{RF\_OOB}} = 89.75\%$ (weight $w_3 = 0.30$).
4. **Composite Validity Score**:
   $$WCVI = (0.30 \times 0.7183) + (0.40 \times 0.4911) + (0.30 \times 0.8975) = \mathbf{0.6812}$$
5. **Adjusted Rand Index Stability**:
   $$\text{ARI} = \frac{\text{RI} - E[\text{RI}]}{\max(\text{RI}) - E[\text{RI}]}$$
   Evaluated over 10 random K-Means seeds: Mean ARI = 0.8966, Std = 0.0405.

### 2.6 Composite Welfare Score
To provide an interpretable scalar indicator of aggregate welfare:
$$\text{Score}_j = \sum_{i=1}^7 w_i \times v_{ij}$$

Where weights $w_i$ and domain bounds are:
- $UHH$: $w = 0.25$, $v = x / 80$
- $PDRB$: $w = 0.20$, $v = x / 1,000,000,000,000$
- $TPT$: $w = 0.15$, $v = 1 - (x / 15)$
- $RLS$: $w = 0.15$, $v = x / 15$
- $Kemiskinan$: $w = 0.10$, $v = 1 - (x / 50)$
- $Pengeluaran$: $w = 0.10$, $v = x / 25,000$
- $Sanitasi$: $w = 0.05$, $v = x / 100$

---

## 3. Data Contracts and Schemas

### 3.1 Raw Dataset Schema (`dataset/Klasifikasi Tingkat Kemiskinan di Indonesia.csv`)
| Column Name | Data Type | Constraints | Description |
|---|---|---|---|
| `Provinsi` | string | Non-null | Name of the province |
| `Kab/Kota` | string | Non-null | Name of regency or municipality |
| `Persentase_Penduduk_Miskin` | float64 | 0.0 <= x <= 100.0 | Poverty rate (%) |
| `Rata_rata_Lama_Sekolah` | float64 | >= 0.0 | Mean years of schooling |
| `Pengeluaran_per_Kapita` | float64 | >= 0.0 | Real per capita expenditure (in thousands) |
| `UHH` | float64 | >= 0.0 | Life expectancy at birth (years) |
| `Sanitasi_Layak` | float64 | 0.0 <= x <= 100.0 | Households with access to improved sanitation (%) |
| `TPT` | float64 | 0.0 <= x <= 100.0 | Open unemployment rate (%) |
| `PDRB_Konstan` | float64 | >= 0.0 | Constant price regional GDP |
| `Tahun` | int64 | Year (e.g. 2021, 2022, 2024) | Observation year |

### 3.2 Master Geographic Coordinate Schema (`dataset/raw/master_koordinat_id.csv`)
| Column Name | Data Type | Constraints | Description |
|---|---|---|---|
| `Provinsi` | string | Non-null | Standardized province name |
| `Kab/Kota` | string | Non-null | Standardized regency name |
| `Latitude` | float64 | -11.0 <= x <= 6.0 | Decimal latitude |
| `Longitude` | float64 | 95.0 <= x <= 141.0 | Decimal longitude |

### 3.3 Processed Analytical Schema (`dataset/processed/narrative_data.csv`)
Contains 37 columns including raw indicators, standardized values, cluster label, typology label, welfare score, normalized indicators, regional flags (`Is_Jawa`), and ranking fields.

---

## 4. Runtime Invariants and System Constraints

1. **Non-Refitting Rule for New Inference**:
   When new data is ingested via Volume III (single record or batch CSV), the system must never refit the Yeo-Johnson transformer or K-Means centroids. New observations must be transformed using the saved transformer instance and assigned to the nearest existing cluster centroid:
   $$k^* = \arg\min_k \|\psi_{\text{saved}}(\mathbf{x}_{\text{new}}) - \mathbf{c}_k\|^2$$
   Refitting on runtime data would alter historical cluster definitions, invalidating prior comparative reports.
2. **Fixed Indicator Weights and Domain Max**:
   The 7 indicator weights and domain maximum values are anchored in BPS and SDG standards. They must remain immutable during runtime unless authorized by a formal methodology revision.
3. **Deterministic Cluster Labeling**:
   The internal cluster numbers map strictly to the standardized public typologies:
   - `0`: "Sentra Industri" (Industrial Centers)
   - `1`: "Area Rentan" (Vulnerable Areas)
   - `2`: "Transisi Seimbang" (Balanced Transition)
   - `3`: "Urban Maju" (Advanced Urban)
   - `-1`: "Entitas Atipikal" (Atypical Outlier Entities)
4. **Headless Execution Compatibility**:
   All Matplotlib operations must set `matplotlib.use('Agg')` prior to importing `pyplot` to prevent display server errors in automated CI environments and background tasks.

---

## 5. Software Architecture and Component Model

```
senuwu/
├── .streamlit/
│   └── config.toml                  # Streamlit theme and server configuration
├── dashboard/
│   ├── app.py                       # Main Streamlit orchestration and routing
│   ├── assets/
│   │   └── academia_style.css       # Academia Design System CSS tokens
│   └── components/
│       ├── narrative.py             # Z-score relative deviation & NLG engine
│       └── ui_primitives.py         # Reusable UI HTML blocks
├── dataset/
│   ├── raw/                         # Raw datasets and coordinate registers
│   ├── processed/                   # Transformed datasets and narrative data
│   ├── results/                     # Diagnostic figures, tables, and logs
│   └── kota-kabupaten-simplified.json # 2.1 MB simplified geospatial polygons
├── docs/
│   └── superpowers/specs/           # Historical design records and revisions
├── scripts/
│   └── pemodelan_klasterisasi_kesejahteraan.py # Full ML training & testing pipeline
├── feature_map.md                   # Complete capability and roadmap inventory
├── spec.md                          # Technical specification (this document)
├── GEMINI.md                        # Project rules and agent coding constraints
├── design.md                        # Academia & Stitch MCP UI/UX design spec
├── requirements.txt                 # Pinned Python package dependencies
└── README.md                        # User and developer manual
```

---

## 6. Normative Specifications for Future Novelties

### 6.1 Counterfactual Policy Simulation Engine (`PolicySimulator`)
```python
class PolicySimulator:
    """Simulates counterfactual policy interventions on regional indicators."""
    
    def __init__(self, baseline_transformer: PowerTransformer, centroids: np.ndarray):
        self.transformer = baseline_transformer
        self.centroids = centroids

    def simulate_intervention(
        self, 
        current_features: dict[str, float], 
        deltas: dict[str, float]
    ) -> dict[str, any]:
        """Applies deltas to indicators, transforms features, and computes:
        1. Projected Composite Welfare Score
        2. Projected nearest cluster assignment
        3. Euclidean distance shift toward target cluster centroid
        """
        ...
```

### 6.2 Spatio-Temporal Disparity Tracking Engine
```python
class TemporalTrackingEngine:
    """Computes multi-year regional migration and spatial autocorrelation shifts."""
    
    def compute_temporal_shift(
        self, 
        df_year_t1: pd.DataFrame, 
        df_year_t2: pd.DataFrame
    ) -> dict[str, any]:
        """Calculates:
        1. Delta Moran's I across consecutive survey waves
        2. Markov transition matrix of cluster migrations
        3. Net welfare score momentum per province
        """
        ...
```

### 6.3 Automated Policy Brief Exporter
```python
class PolicyBriefExporter:
    """Renders standalone executive PDF/HTML policy briefs."""
    
    def render_dossier(
        self, 
        regency_data: pd.Series, 
        narrative_sections: dict[str, str], 
        radar_chart_bytes: bytes
    ) -> bytes:
        """Assembles a publication-grade PDF using ReportLab with Academia typography."""
        ...
```
