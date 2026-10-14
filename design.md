# SENUWU UI/UX Design Specification (Stitch MCP)

## 1. Design Philosophy and Visual Identity

SENUWU adopts the **Academia / Classical Scholarship** design system. Unlike generic dashboard templates that prioritize neon gradients or clinical flat minimalism, SENUWU evokes the gravitas of academic institutions, peer-reviewed monographs, and cartographic atlases.

### Core Principles
- **Scholarly Authority**: Warm tactile surfaces reminiscent of archival paper and library reading rooms, balanced with modern information clarity.
- **Editorial Typography**: Pairing classical high-contrast serif display fonts with readable text serifs and regal Roman capital accents.
- **Dignified Accents**: Muted metallic gold, warm brass, and restrained typology colors that avoid abrasive primary hues.
- **Elevation and Texture**: Subtle atmospheric card shadows and glassmorphic blurs (`backdrop-filter: blur(12px)`) that elevate modals above the analytical plane.

---

## 2. Design Tokens and Variables

### 2.1 Color Tokens
```css
:root {
  /* Surface Tokens */
  --canvas-bg: #F9F6F0;          /* Warm archival ivory paper */
  --surface-card: #FFFFFF;       /* Crisp card container */
  --surface-secondary: #F3EFE9;  /* Inset panels and table headers */
  --surface-glass: rgba(255, 255, 255, 0.95); /* Modal glass surface */
  --backdrop-scrim: rgba(28, 23, 20, 0.40);   /* Deep walnut modal backdrop */

  /* Typography / Ink Tokens */
  --ink-primary: #1C1714;        /* Deep charcoal warm ink */
  --ink-secondary: #5C4033;      /* Warm roasted walnut */
  --ink-muted: #8A7968;          /* Muted parchment caption */
  --ink-inverse: #FFFFFF;        /* High-contrast white */

  /* Metallic and Accent Tokens */
  --accent-brass: #8A620B;       /* Antique warm brass */
  --accent-brass-dark: #6D4D09;  /* Pressed brass hover */
  --accent-brass-light: #D4AF37; /* Pale gold highlight */
  --accent-border: #E8DFD4;      /* Soft parchment border line */
  --accent-border-muted: #9C8B7A;/* Muted frame border */

  /* Cluster Typology Tokens */
  --cluster-urban: #0F766E;      /* Urban Maju: Deep Forest Teal */
  --cluster-balanced: #1E3A8A;   /* Transisi Seimbang: Oxford Navy */
  --cluster-industrial: #E8505B; /* Sentra Industri: Venetian Terracotta */
  --cluster-vulnerable: #F18F01; /* Area Rentan: Deep Amber */
  --cluster-atypical: #6B7280;   /* Entitas Atipikal: Muted Slate */
}
```

### 2.2 Typography System
```css
/* Display and Hero Headings */
--font-display: "Cormorant Garamond", Georgia, "Times New Roman", serif;

/* Body Text, Narratives, and Tables */
--font-body: "Crimson Pro", Georgia, serif;

/* Action Buttons, Overlines, and Micro-Labels */
--font-accent: "Cinzel", "Trajan Pro", serif;
```

#### Type Scale Specifications
| Role | Font Family | Size | Weight | Line Height | Letter Spacing |
|---|---|---|---|---|---|
| `display-1` (Hero) | Cormorant Garamond | 42px | 700 | 1.15 | -0.02em |
| `display-2` (Section) | Cormorant Garamond | 30px | 600 | 1.25 | -0.01em |
| `heading-1` (Card Title) | Cormorant Garamond | 24px | 600 | 1.30 | 0.00em |
| `body-large` (Lead) | Crimson Pro | 19px | 400 | 1.60 | 0.00em |
| `body-regular` (Text) | Crimson Pro | 16px | 400 | 1.65 | 0.00em |
| `body-small` (Caption) | Crimson Pro | 14px | 400 | 1.50 | 0.01em |
| `label-action` (Button) | Cinzel | 13px | 600 | 1.00 | 0.08em uppercase |
| `label-overline` | Cinzel | 11px | 700 | 1.20 | 0.12em uppercase |

### 2.3 Elevation, Borders, and Radii
- **Border Radius**: Universal component radius = `8px` (`border-radius: 8px`). Applied strictly across buttons, text inputs, dropdowns, cards, and modal windows.
- **Card Shadow**: `0 4px 16px rgba(28, 23, 20, 0.04)`.
- **Floating Shadow (Hover / Modal)**: `0 16px 36px rgba(28, 23, 20, 0.12)`.
- **Card Border**: `1px solid var(--accent-border)`.

---

## 3. Component Blueprints and Layout Specifications

### 3.1 Hero Section
```
+---------------------------------------------------------------------------------+
|  [VOLUME I: BERANDA]                                                            |
|                                                                                 |
|  SISTEM INFORMASI ANALITIK KETIMPANGAN WILAYAH                                 |
|  (Cormorant Garamond, 42px, Bold, #1C1714)                                      |
|                                                                                 |
|  Pemodelan geospasial multidimensi berbasis machine learning hybrid             |
|  dan pembuktian ketimpangan struktural wilayah Indonesia.                      |
|  (Crimson Pro, 18px, #5C4033)                                                    |
+---------------------------------------------------------------------------------+
```

### 3.2 Model Reliability Card (Two-Column Layout)
The reliability card establishes scientific credibility at the top of the Beranda page:
```
+---------------------------------------------------------------------------------+
|  +-----------------------------+  +------------------------------------------+  |
|  | STATUS MODEL                |  | METRIK EVALUASI TERPADU                  |  |
|  |                             |  |                                          |  |
|  | [Terverifikasi Valid]       |  | Model hybrid HDBSCAN-KMeans dievaluasi   |  |
|  | WCVI Composite: 0.6812      |  | secara independen dengan metrik:        |  |
|  | Kategori: Kinerja Unggul    |  | * Hopkins Statistic: 0.7183              |  |
|  |                             |  | * R-Squared (EESS): 49.11%               |  |
|  |                             |  | * RF OOB Accuracy: 89.75%                |  |
|  |                             |  | * ARI Stability: 0.8966                  |  |
|  +-----------------------------+  +------------------------------------------+  |
+---------------------------------------------------------------------------------+
```
- **Left Column (35% width)**: Background `#F3EFE9`, border right `1px solid #E8DFD4`, contains large status indicator and composite WCVI badge.
- **Right Column (65% width)**: Background `#FFFFFF`, contains narrative context and clean bullet points for individual validation metrics.

### 3.3 Geospatial Choropleth Map with Custom Hover Tooltip
- **Map Base**: Minimal grayscale or light canvas cartographic tiles (CartoDB Positron) to prevent visual competition with choropleth polygons.
- **Polygon Styling**:
  - Fill opacity: 0.75.
  - Border: 0.5px solid `#FFFFFF`.
  - Highlight on hover: Fill opacity 0.95, weight 2px `#8A620B`.
- **Custom HTML Hover Card**:
  ```
  +-------------------------------------------------------------+
  |  KABUPATEN BOGOR (Jawa Barat)                               |
  |  [Sentra Industri] (Badge: Terracotta #E8505B)              |
  |  ---------------------------------------------------------  |
  |  Welfare Score: 0.5842                                      |
  |  PDRB Konstan : Rp 124,5 Triliun                            |
  |  TPT          : 8.88%                                       |
  |  Kemiskinan   : 7.25%                                       |
  |  UHH          : 71.4 Tahun                                  |
  |  ---------------------------------------------------------  |
  |  Kapasitas PDRB tinggi namun tertekan oleh pengangguran     |
  |  friksional perkotaan.                                      |
  +-------------------------------------------------------------+
  ```

### 3.4 Volume II: Regional Search and Narrative Dossier Card
- **Cascading Filter Bar**: Horizontal 3-column selector (Tahun, Provinsi, Kabupaten/Kota) with custom ivory backgrounds and brass focus rings.
- **Identity Header**: Top bar accented with 4px cluster-specific colored border.
- **5-Section Narrative Card**:
  - Section 1: Executive Summary with cluster badge.
  - Section 2: Comparative Performance Analysis.
  - Section 3: Peer Group Typology Characteristics.
  - Section 4: Top 3 Welfare Determinants Table (Indicator, Relative Deviation, Z-score Pill Badge).
  - Section 5: Concrete Policy Action Recommendations.

### 3.5 Volume III: Glassmorphism Confirmation Modals
```
+---------------------------------------------------------------------------------+
|  [Semi-transparent Scrim with 12px blur backdrop-filter]                        |
|                                                                                 |
|         +-------------------------------------------------------------+         |
|         | KONFIRMASI PENYIMPANAN DATA (Cinzel, 18px)                  |         |
|         |                                                             |         |
|         | Wilayah : Kota Surakarta                                    |         |
|         | Tahun   : 2026                                              |         |
|         | Prediksi: Urban Maju (Teal Badge)                           |         |
|         | Jarak Centroid: 0.2341 (Derajat Kemiripan: Tinggi)          |         |
|         |                                                             |         |
|         | [BATAL] (Border: #9C8B7A)    [SIMPAN PERMANEN] (Gold Brass) |         |
|         +-------------------------------------------------------------+         |
|                                                                                 |
+---------------------------------------------------------------------------------+
```

---

## 4. Stitch MCP Prompt Directives and Component Templates

When utilizing Stitch MCP to generate new frontend views, artifacts, or standalone HTML widgets for SENUWU, provide the following system instruction block:

```markdown
Role: Academia Design System UI Engineer
Theme: SENUWU Classical Academia

Design Directives:
1. Palette: Canvas #F9F6F0, Surface #FFFFFF, Secondary #F3EFE9, Ink #1C1714, Accent #8A620B.
2. Fonts: Display 'Cormorant Garamond', Body 'Crimson Pro', UI/Buttons 'Cinzel'.
3. Component Radii: Strictly 8px for all cards, buttons, inputs, and modals.
4. Punctuation Rule: Never generate em-dash or en-dash characters. Use hyphens (-), colons, or parentheses.
5. Cluster Colors:
   - Urban Maju: #0F766E
   - Transisi Seimbang: #1E3A8A
   - Sentra Industri: #E8505B
   - Area Rentan: #F18F01
   - Entitas Atipikal: #6B7280
6. Modals: Always use glassmorphism with backdrop-filter: blur(12px) and soft gold action buttons.
```

### 4.1 Sample Stitch Component Scaffold: Metric Badge
```html
<div style="
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 14px;
  border-radius: 8px;
  background: #F3EFE9;
  border: 1px solid #E8DFD4;
">
  <span style="
    font-family: 'Cinzel', serif;
    font-size: 11px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #5C4033;
  ">WCVI COMPOSITE</span>
  <span style="
    font-family: 'Cormorant Garamond', serif;
    font-size: 18px;
    font-weight: 700;
    color: #8A620B;
  ">0.6812</span>
</div>
```
