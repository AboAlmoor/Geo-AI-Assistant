# School Site Selection Using Spatial Analysis

**Project:** Spatial Data Analysis - Homework 1  
**Authors:** Ameer Saleh & Bara Mhana  
**Date:** December 1, 2025

---

## Table of Contents

- [Executive Summary](#executive-summary)
- [Introduction](#introduction)
- [Data and Study Area](#data-and-study-area)
- [Methodology](#methodology)
- [Selection Criteria](#selection-criteria)
- [Technical Implementation](#technical-implementation)
- [Results and Analysis](#results-and-analysis)
- [QGIS Visualization](#qgis-visualization)
- [Project Structure](#project-structure)
- [Conclusions and Recommendations](#conclusions-and-recommendations)

---

## Executive Summary

This project identifies suitable locations for new school construction using PostGIS spatial analysis and QGIS visualization. From 140 initial land parcels, **7 suitable sites** were identified totaling **52,779.20 m²** through systematic application of four selection criteria.

### Key Results

- 7 suitable parcels identified (5% success rate)
- Average parcel size: 7,539.89 m²
- 85.7% of sites directly adjacent to roads
- Mix of un-used (71.4%) and agricultural lands (28.6%)

### Model Builder (Work Flow)

![alt text](/model-builder.png)

---

## 1. Introduction

### 1.1 Objectives

Identify suitable land parcels for school construction using multi-criteria spatial analysis in PostGIS with the following requirements:

1. Land use types: Un-Used, Agricultural, or Commercial
2. Minimum area: 5,000 m²
3. No existing buildings on parcels
4. Within 25m of nearest road

### 1.2 Tools and Technologies

- **PostgreSQL + PostGIS** - Spatial database and analysis
- **QGIS 3.16+** - Geographic visualization
- **SQL** - Query development

---

## 2. Data and Study Area

### 2.1 Database Schema

#### Landuse Table (Primary dataset)

| Column | Type | Description |
|--------|------|-------------|
| idd | integer | Primary key |
| type | varchar | Land use classification |
| area | numeric | Parcel area (m²) |
| geom | geometry | Polygon geometry |

#### Buildings Table

| Column | Type | Description |
|--------|------|-------------|
| idd | integer | Primary key |
| geom | geometry | Building footprints |

#### Roads Table

| Column | Type | Description |
|--------|------|-------------|
| idd | integer | Primary key |
| name | varchar | Road name |
| geom | geometry | Road centerlines |

---

## 3. Methodology

### 3.1 Analysis Workflow

```
Initial Landuse (140 parcels)
        ↓
① Land Use Type Filter → 140 parcels
        ↓
② Area ≥ 5000 m² → 23 parcels
        ↓
③ No Buildings → 17 parcels
        ↓
④ Road Proximity ≤ 25m → 7 parcels (FINAL)
```

### 3.2 Sequential Filtering Approach

Each criterion progressively narrows the candidate set, ensuring all requirements are met while optimizing query performance.

---

## 4. Selection Criteria

### Criterion 1: Land Use Type

**Requirement:** Un-Used, Agricultural Areas, or Commercial Lands

```sql
WHERE type IN ('Un-Used', 'Agricultural Areas', 'Commercial Lands')
```

**Result:** 140 parcels retained

---

### Criterion 2: Minimum Area

**Requirement:** Area ≥ 5,000 m²

```sql
AND ST_Area(geom) >= 5000
```

**Result:** 23 parcels (83.6% eliminated)

---

### Criterion 3: No Buildings

**Requirement:** No building footprints intersecting parcels

```sql
AND NOT EXISTS (
    SELECT 1 FROM buildings b
    WHERE ST_Intersects(l.geom, b.geom)
)
```

**Result:** 17 parcels (26.1% eliminated)

---

### Criterion 4: Road Proximity

**Requirement:** Within 25m of nearest road

```sql
AND EXISTS (
    SELECT 1 FROM roads r
    WHERE ST_DWithin(l.geom, r.geom, 25)
)
```

**Result:** 7 parcels (58.8% eliminated)

---

## 5. Technical Implementation

### 5.1 Complete SQL Query

```sql
-- Final query applying all criteria
CREATE TABLE final_school_locations AS
SELECT
    l.idd,
    l.type,
    l.owner,
    l.area,
    l.geom,
    ST_Area(l.geom) as calculated_area,
    (SELECT MIN(ST_Distance(l.geom, r.geom))
     FROM roads r) as distance_to_nearest_road
FROM
    landuse l
WHERE
    -- Criterion 1: Land use type
    l.type IN ('Un-Used', 'Agricultural Areas', 'Commercial Lands')
    
    -- Criterion 2: Minimum area
    AND ST_Area(l.geom) >= 5000
    
    -- Criterion 3: No buildings
    AND NOT EXISTS (
        SELECT 1
        FROM buildings b
        WHERE ST_Intersects(l.geom, b.geom)
    )
    
    -- Criterion 4: Road proximity
    AND EXISTS (
        SELECT 1
        FROM roads r
        WHERE ST_DWithin(l.geom, r.geom, 25)
    )
ORDER BY
    ST_Area(l.geom) DESC;

-- Add primary key and spatial index
ALTER TABLE final_school_locations ADD PRIMARY KEY (idd);
CREATE INDEX idx_final_sites_geom ON final_school_locations USING GIST(geom);
```

---

## 6. Results and Analysis

### 6.1 Filtering Progression

| Step | View Name | Count | Criteria Applied |
|------|-----------|-------|------------------|
| 1 | suitable_landuse_types | 140 | TYPE IN (Un-Used, Agricultural, Commercial) |
| 2 | suitable_area_parcels | 23 | ST_Area(geom) ≥ 5,000 m² |
| 3 | parcels_without_buildings | 17 | NOT ST_Intersects with buildings |
| 4 | final_school_locations | 7 | ST_DWithin roads 25m |

**Overall Reduction:** 95.0% (140 → 7 parcels)

---

### 6.2 Final School Sites

| ID | Land Use Type | Area (m²) | Distance to Road (m) |
|----|---------------|-----------|----------------------|
| 20 | Agricultural Areas | 9,935.86 | 0.00 |
| 131 | Un-Used | 8,247.02 | 0.00 |
| 215 | Un-Used | 7,981.13 | 0.00 |
| 8 | Un-Used | 7,283.46 | 0.00 |
| 145 | Un-Used | 7,214.55 | 0.00 |
| 11 | Un-Used | 6,255.88 | 14.22 |
| 17 | Agricultural Areas | 5,861.30 | 0.00 |

---

### 6.3 Summary Statistics

#### Area Analysis

- Total Area: 52,779.20 m²
- Mean: 7,539.89 m²
- Minimum: 5,861.30 m²
- Maximum: 9,935.86 m²

#### Distance to Roads

- Mean: 2.03 m
- Sites adjacent to roads: 6 (85.7%)
- Maximum distance: 14.22 m

#### Land Use Distribution

| Land Use Type | Count | Total Area (m²) | Percentage |
|---------------|-------|-----------------|------------|
| Un-Used | 5 | 36,982.04 | 71.4% |
| Agricultural Areas | 2 | 15,797.16 | 28.6% |
| **Total** | **7** | **52,779.20** | **100%** |

---

## 7. QGIS Visualization

![alt text](/visual-outputs/layers-visual.png)
![alt text](/visual-outputs/layers-names.png)

### 7.1 Loading Data in QGIS

**Method 1: Direct PostGIS Connection**

1. Layer → Add Layer → Add PostGIS Layers
2. Create connection to database
3. Select final_school_locations table
4. Add to map

**Method 2: DB Manager**

1. Database → DB Manager → PostGIS
2. SQL Window → Execute query
3. Check "Load as new layer"

### 7.2 Map Styling

**Final School Sites:**
- Fill: Green (#4CAF50), 60% opacity
- Outline: Dark Green (#2E7D32), 1.5pt
- Labels: Site ID and area

**Supporting Layers:**
- Roads: Gray lines (1.5pt)
- Buildings: Red outlines (0.5pt)
- 25m Road Buffer: Blue dashed (40% opacity)

### 7.3 Map Layout Elements

- Title: "Suitable School Sites Analysis"
- Legend with all layers
- Scale bar and north arrow
- Data sources and projection info
- Results summary table

---

## 8. Conclusions and Recommendations

### 8.1 Summary

Successfully identified **7 suitable parcels** totaling **52,779 m²** through rigorous spatial analysis. All sites meet the four selection criteria and are development-ready with excellent road access.

### 8.2 Immediate Next Steps

1. **Site Verification** - Field visits to all 7 sites
2. **Environmental Assessment** - Phase I environmental studies
3. **Cost Analysis** - Land appraisals and development estimates
4. **Stakeholder Engagement** - Community consultation and owner contact

### 8.3 Future Enhancements

**Additional Analysis:**
- Multi-criteria decision analysis (MCDA) with weighted criteria
- Cost-benefit analysis integration
- Student population density mapping
- Environmental constraints (slopes, flood zones)
- Traffic and accessibility modeling

**Data Improvements:**
- Property values and ownership details
- Existing school locations and capacity
- Demographic and enrollment projections
- Utility infrastructure availability

---

**Report prepared by:** Ameer Saleh & Bara Mhana  
**Course:** Spatial Data Analysis  
**Assignment:** Homework 1 - Site Selection using PostGIS  
**Date:** December 1, 2025

---

*END OF REPORT*