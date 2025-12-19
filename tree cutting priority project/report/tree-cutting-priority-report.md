# Tree Cutting Priority Analysis for Fire Creek

[![Python](https://img.shields.io/badge/Python-3.x-blue.svg)](https://www.python.org/)
[![GeoPandas](https://img.shields.io/badge/GeoPandas-Latest-green.svg)](https://geopandas.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> Spatial data analysis project for wildfire risk mitigation in the Fire Creek area

**Project:** Spatial Data Analysis - Homework 3  
**Authors:** Ameer Saleh & Bara Mhana  
**Date:** December 12, 2025

---

## 📋 Table of Contents

- [Executive Summary](#executive-summary)
- [Introduction](#1-introduction)
- [Data and Study Area](#2-data-and-study-area)
- [Methodology](#3-methodology)
- [Scoring Criteria](#4-scoring-criteria)
- [Priority Classification](#5-priority-classification)
- [Results and Analysis](#6-results-and-analysis)
- [Visualization and Outputs](#7-visualization-and-outputs)
- [Conclusions and Recommendations](#8-conclusions-and-recommendations)
- [Installation & Usage](#installation--usage)
- [Contributing](#contributing)
- [License](#license)

---

## Executive Summary

This project calculates and prioritizes tree cutting zones for wildfire risk mitigation in the Fire Creek area using Python-based spatial analysis with GeoPandas and matplotlib visualization.

**Key Results:**
- Zones Analyzed: 80 cutting grid zones
- Method: Multi-criteria decision analysis (MCDA) using five weighted factors
- Normalization: Scores scaled 0-100
- Priority Classes: High, Medium, Low

**Key Metrics:**
- Mean Priority Score: 29.37
- Maximum Priority Score: 60.73 (Grid 163)
- Standard Deviation: 13.71

**Distribution:**
- Critical Priority: 0 zones (0.0%)
- High Priority: 5 zones (6.3%)
- Medium Priority: 43 zones (53.8%)
- Low Priority: 32 zones (40.0%)

**Outputs:** Complete visualization with 3 analytical charts and spatial data files

## 1. Introduction

### 1.1 Objectives

The primary objective is to calculate tree cutting priority for each zone using Multi-Criteria Decision Analysis (MCDA) in Python/GeoPandas to support wildfire risk mitigation efforts in the Fire Creek area.

**Analysis Factors & Weights:**
- Tree Mortality: 30%
- Community Features: 15%
- Egress Routes: 20%
- Populated Areas: 20%
- Electric Utilities: 15%

### 1.2 Tools and Technologies

- Python 3.x - Core programming language
- GeoPandas - Spatial analysis and operations
- Pandas / NumPy - Data processing and mathematical operations
- Matplotlib - Charts and visualization generation
- QGIS 3.16+ - Geographic visualization and mapping
- Shapefile / GeoPackage - Spatial data formats

## 2. Data and Study Area

### 2.1 Study Area

**Location:** Fire Creek Area  
**Spatial Reference System:** EPSG:26711  
**Analysis Units:** 80 grid zones

### 2.2 Input Data Schema

| Dataset | Features | Description |
|---------|----------|-------------|
| CuttingGrids | 80 | Grid polygons defining cutting zones |
| SBNFMortality | 12 | Tree mortality polygons with total mortality values |
| CommunityFeature | 8 | Locations of critical community infrastructure |
| EgressRoutes | 6 | Emergency evacuation route lines |
| PopulatedAreas | 6 | Residential / populated area polygons |
| Electric Utilities | 5 layers | Transmission, SubTransmission, Distribution Circuits, Substations, PoleTopSubs |

## 3. Methodology

### 3.1 Analysis Workflow

```
Initial Dataset (80 Grid Zones + 5 Risk Factors)
↓
┌────────────────────────────────────────────┐
│ STEP 1: Load & Align CRS → EPSG:26711     │
└────────────────┬───────────────────────────┘
                 ↓
┌────────────────────────────────────────────┐
│ STEP 2: Calculate Mortality Score         │
│ → Spatial intersection with mortality data│
│ → Normalize 0-100                          │
└────────────────┬───────────────────────────┘
                 ↓
┌────────────────────────────────────────────┐
│ STEP 3: Calculate Community Score         │
│ → Count community features per zone       │
│ → Normalize 0-100                          │
└────────────────┬───────────────────────────┘
                 ↓
┌────────────────────────────────────────────┐
│ STEP 4: Calculate Egress Score            │
│ → Measure route coverage per zone         │
│ → Normalize 0-100                          │
└────────────────┬───────────────────────────┘
                 ↓
┌────────────────────────────────────────────┐
│ STEP 5: Calculate Populated Score         │
│ → Assess residential area exposure        │
│ → Normalize 0-100                          │
└────────────────┬───────────────────────────┘
                 ↓
┌────────────────────────────────────────────┐
│ STEP 6: Calculate Utility Score           │
│ → Evaluate 5 utility layer exposures      │
│ → Normalize 0-100                          │
└────────────────┬───────────────────────────┘
                 ↓
┌────────────────────────────────────────────┐
│ STEP 7: Apply Weighted MCDA               │
│ → Priority Score = Σ(weight × score)      │
│ → Final score range: 0-100                │
└────────────────┬───────────────────────────┘
                 ↓
┌────────────────────────────────────────────┐
│ STEP 8: Classify Priority                 │
│ → Low / Medium / High / Critical          │
└────────────────┬───────────────────────────┘
                 ↓
┌────────────────────────────────────────────┐
│ STEP 9: Generate Visualizations           │
│ → Bar Chart, Pie Chart, Top 10 Chart     │
└────────────────────────────────────────────┘
```

### 3.2 MCDA Approach

The analysis employs a weighted Multi-Criteria Decision Analysis approach where:
- Each factor is independently calculated and normalized to a 0-100 scale
- Weighted summation produces the final priority score
- Higher scores indicate higher priority for tree cutting operations

### 3.3 Normalization Formula

For each criterion, raw scores are normalized using:

```
Normalized Score = (Raw Score / Maximum Raw Score) × 100
```

This ensures all factors contribute proportionally to the final priority score regardless of their original measurement units.

## 4. Scoring Criteria

### 4.1 Overview of Criteria

| Criterion | Weight | Description |
|-----------|--------|-------------|
| Tree Mortality | 30% | Spatial intersection with mortality polygons |
| Community Features | 15% | Presence of critical community infrastructure |
| Egress Routes | 20% | Coverage of evacuation routes |
| Populated Areas | 20% | Exposure of residential areas |
| Electric Utilities | 15% | Exposure of utility infrastructure |

### 4.2 Criterion 1: Tree Mortality (30%)

**Rationale:** Dead and dying trees pose the highest direct fire risk, serving as fuel sources that can accelerate wildfire spread and intensity.

**Implementation:**
- Spatial intersection between cutting grids and mortality polygons
- Sum of total mortality values within each zone
- Higher mortality values indicate greater immediate risk

**Impact:** Primary driver of priority scores, reflecting direct fire hazard from dead vegetation.

### 4.3 Criterion 2: Community Features (15%)

**Rationale:** Protection of critical infrastructure including schools, fire stations, hospitals, and community centers is essential for public safety and emergency response capability.

**Implementation:**
- Count of community features within or near each zone
- Binary scoring for presence/absence of critical facilities
- Proximity weighting for features near zone boundaries

**Impact:** Ensures protection of community assets vital for evacuation and emergency services.

### 4.4 Criterion 3: Egress Routes (20%)

**Rationale:** Clear evacuation routes are life-critical during wildfire events. Tree removal along escape corridors prevents route blockage and ensures safe evacuation.

**Implementation:**
- Calculate length of egress routes passing through each zone
- Higher coverage indicates greater importance for evacuation safety
- Line intersection analysis with grid zones

**Impact:** Prioritizes zones that, if left unmanaged, could block evacuation pathways.

### 4.5 Criterion 4: Populated Areas (20%)

**Rationale:** Residential areas face direct threat from wildfire. Tree cutting creates defensible space around homes and reduces ember ignition risks.

**Implementation:**
- Measure overlap between populated area polygons and cutting zones
- Area-based scoring reflecting population exposure
- Higher scores for zones with greater residential coverage

**Impact:** Protects human life and property by creating fire breaks near homes.

### 4.6 Criterion 5: Electric Utilities (15%)

**Rationale:** Utility infrastructure poses dual risk: power lines can spark fires, and fires can damage critical electrical infrastructure causing widespread outages.

**Electric Utility Scoring Details:**

| Utility Type | Weight | Method |
|--------------|--------|--------|
| Transmission Lines | 3.0 | Length × weight × priority |
| SubTransmission Lines | 2.5 | Length × priority |
| Distribution Circuits | 2.0 | Length within zone |
| Substations | 3.0 | Fixed score × priority |
| Pole Top Substations | 2.0 | Count × fixed score |

**Implementation:**
- Multi-layer analysis across 5 utility datasets
- Weighted scoring based on voltage level and criticality
- Length-based calculations for linear features (power lines)
- Count-based calculations for point features (substations)

**Impact:** Reduces fire ignition risk from electrical equipment and protects power grid reliability.

## 5. Priority Classification

### 5.1 Classification System

| Priority Class | Score Range | Action Required | Description |
|----------------|-------------|-----------------|-------------|
| Critical | 75-100 | Immediate action | Emergency response within days |
| High | 50-74 | Near-term action | Schedule within current season |
| Medium | 25-49 | Scheduled maintenance | Address in annual work plan |
| Low | 0-24 | Routine monitoring | Monitor and reassess periodically |

### 5.2 Weighted Priority Formula

The final priority score for each zone is calculated as:

```
priority_score = (0.3 × mortality_score) +
                 (0.15 × community_score) +
                 (0.2 × egress_score) +
                 (0.2 × populated_score) +
                 (0.15 × utility_score)
```

Where each component score is normalized to 0-100 scale before weighting.

## 6. Results and Analysis

### 6.1 Priority Distribution

**Analysis Results:**

| Class | Count | Percentage | Cumulative |
|-------|-------|------------|------------|
| Critical | 0 | 0.0% | 0.0% |
| High | 5 | 6.3% | 6.3% |
| Medium | 43 | 53.8% | 60.0% |
| Low | 32 | 40.0% | 100.0% |
| **Total** | **80** | **100%** | **-** |

**Key Insights:**
- No zones reached critical threshold (75+), indicating manageable overall risk
- Only 5 zones (6.3%) require near-term action
- Majority (53.8%) fall into medium priority requiring scheduled maintenance
- 40% are low priority suitable for routine monitoring

![Tree Cutting Priority Analysis](../tree-cutting-priority-analysis.jpg)

### 6.2 Score Statistics

**Statistical Summary:**

| Metric | Value | Interpretation |
|--------|-------|----------------|
| Mean Priority Score | 29.37 | Average zone falls in medium-low range |
| Maximum Priority Score | 60.73 | Highest risk zone (Grid 163) |
| Minimum Priority Score | 8.16 | Lowest risk zone |
| Standard Deviation | 13.71 | Moderate variability across zones |
| Median | 26.45 | Central tendency near mean |

**Distribution Characteristics:**
- Right-skewed distribution with concentration in 20-40 score range
- No extreme outliers above 65 points
- Relatively consistent risk levels across most zones

### 6.3 High Priority Zones

**Top 5 Zones Requiring Near-Term Action:**

| Rank | Grid ID | Score | Class | Key Risk Factors |
|------|---------|-------|-------|------------------|
| 1 | 163 | 60.73 | High | High mortality, egress route coverage |
| 2 | 158 | 55.51 | High | Community features, utility exposure |
| 3 | 130 | 54.48 | High | Populated area proximity, mortality |
| 4 | 157 | 51.84 | High | Multiple utility layers, egress routes |
| 5 | 162 | 50.74 | High | Balanced risk across all factors |

**Operational Recommendations:**
- Grid 163 should be addressed first (highest score)
- All five zones should be scheduled within current fire season
- Field verification recommended for final work planning

### 6.4 Top 10 Priority Zones

**Extended Priority List:**

| Rank | Grid ID | Priority Score | Class | Notes |
|------|---------|----------------|-------|-------|
| 1 | 163 | 60.73 | High | Top priority |
| 2 | 158 | 55.51 | High | Secondary priority |
| 3 | 130 | 54.48 | High | Community protection focus |
| 4 | 157 | 51.84 | High | Utility corridor |
| 5 | 162 | 50.74 | High | Egress route critical |
| 6 | 168 | 48.69 | Medium | Near high threshold |
| 7 | 154 | 48.57 | Medium | Consider for early action |
| 8 | 172 | 47.73 | Medium | Moderate risk balanced |
| 9 | 124 | 47.21 | Medium | Monitor for escalation |
| 10 | 113 | 45.70 | Medium | Standard maintenance |

**Planning Considerations:**
- Zones 6-10 are medium priority but near high threshold
- Consider advancing zones 6-7 if resources permit
- Group adjacent zones for operational efficiency

### 6.5 Spatial Analysis
![Layers Visual](../visual-outputs/layers-visual.png)

**Spatial Patterns Observed:**
- High priority zones clustered in central-eastern portion of study area
- Spatial correlation with populated areas and utility corridors
- Linear patterns following egress routes and transmission lines
- Low priority zones concentrated in peripheral areas with less infrastructure

## 7. Visualization and Outputs

### 7.1 Chart Types

Three complementary visualizations were generated to support decision-making:

1. **Bar Chart - Grid Zones by Priority Class**
   - Shows count of zones in each priority category
   - Highlights the 43 medium-priority zones requiring scheduled attention
   - Confirms no critical zones requiring emergency response

2. **Pie Chart - Priority Class Distribution**
   - Percentage breakdown: Low (40%), Medium (53.8%), High (6.2%)
   - Visual representation of overall risk profile
   - Demonstrates manageable risk distribution

3. **Horizontal Bar Chart - Top 10 Highest Priority Zones**
   - Individual zone scores with Grid IDs
   - Color-coded by classification (orange for high, yellow for medium)
   - Facilitates crew assignment and work scheduling

### 7.2 Color Scheme

Consistent color coding used across all visualizations:

| Priority Class | Color | Application |
|----------------|-------|-------------|
| Critical | Red | Emergency zones (none in current analysis) |
| High | Orange | Near-term action (5 zones) |
| Medium | Yellow | Scheduled maintenance (43 zones) |
| Low | Green | Routine monitoring (32 zones) |

**Chart Output:** TreeCuttingPriority_Charts.png (300 DPI, publication quality)

### 7.3 QGIS Visualization
![Layers Names](../visual-outputs/layers-names.png)

**Loading Priority Results in QGIS**

**Method 1: Add Shapefile**
1. Layer → Add Layer → Add Vector Layer
2. Browse to TreeCuttingPriority_[timestamp].shp
3. Click Add to load into map canvas

**Method 2: Add GeoPackage**
1. Layer → Add Layer → Add Vector Layer
2. Select TreeCuttingPriority_[timestamp].gpkg
3. Choose layer from package if multiple layers present

**Styling by Priority Class**

**Categorized Symbology:**
- Right-click layer → Properties → Symbology
- Select "Categorized" renderer
- Field: prior_cls (priority class)
- Click "Classify" to auto-generate classes
- Assign colors:
  - Critical → Red, opacity 70%
  - High → Orange, opacity 70%
  - Medium → Yellow, opacity 60%
  - Low → Green, opacity 60%
- Adjust outline: Black, 0.5pt width

**Alternative: Graduated Colors**
- Field: priority_s (priority score)
- Mode: Pretty Breaks, 4 classes
- Color Ramp: RdYlGn (inverted - red high, green low)
- Manual adjustments for breakpoints: 0-25, 25-50, 50-75, 75-100

## 8. Conclusions and Recommendations

**Summary**

This GeoPandas-based spatial analysis successfully evaluated all 80 Fire Creek cutting zones using multi-criteria decision analysis. The systematic approach:

✓ Applied five weighted risk factors using industry-standard wildfire mitigation criteria  
✓ Normalized all scores to comparable 0-100 scale  
✓ Identified 5 high-priority zones requiring near-term action  
✓ Classified 43 zones for scheduled maintenance programs  
✓ Produced reproducible, data-driven results through documented Python workflows  
✓ Generated professional visualizations for stakeholder communication

**Strengths of Analysis:**
- **Objectivity** - Mathematical criteria eliminate subjective bias in prioritization
- **Transparency** - Weighted formula clearly documented and auditable
- **Spatial Intelligence** - Geographic relationships drive meaningful risk assessment
- **Actionable Results** - Clear priority classes support operational planning
- **Reproducibility** - Python code enables reanalysis with updated data

---

## Installation & Usage

### Prerequisites

```bash
# Required Python packages
pip install geopandas pandas numpy matplotlib
```

### Quick Start

```python
# Load the analysis results
import geopandas as gpd

# Load shapefile
gdf = gpd.read_file('TreeCuttingPriority_[timestamp].shp')

# Or load GeoPackage
gdf = gpd.read_file('TreeCuttingPriority_[timestamp].gpkg')

# View priority distribution
print(gdf['prior_cls'].value_counts())
```

### Running the Analysis

1. Prepare input datasets (CuttingGrids, SBNFMortality, etc.)
2. Ensure all layers are in EPSG:26711 CRS
3. Run the analysis script
4. View generated charts and outputs

### Output Files

- `TreeCuttingPriority_[timestamp].shp` - Shapefile with priority scores
- `TreeCuttingPriority_[timestamp].gpkg` - GeoPackage format
- `TreeCuttingPriority_Charts.png` - Visualization charts (300 DPI)

---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## License

This project is part of academic coursework for Spatial Data Analysis.

---

## Contact

**Authors:**  
- Ameer Saleh
- Bara Mhana

**Course:** Spatial Data Analysis  
**Assignment:** Homework 3 - Tree Cutting Priority Analysis

---

**END OF README**