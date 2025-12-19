# School Site Selection Using PostGIS and QGIS

![alt text](/model-builder.png)

---

## Assignment

**Task:** Find new areas suitable for building a new school.

**Selection Criteria:**
- Land use types should be unused, agricultural land, or commercial land.
- Area should be ≥ 5,000 m².
- No buildings should be on the land use parcels.
- Areas should be within 25 meters from the nearest road.

---

## Project Overview

This project identifies suitable locations for new school construction using spatial analysis in PostGIS and visualization in QGIS. The analysis applies multiple criteria including land use type, minimum area requirements, building conflicts, and proximity to road infrastructure.

**Objective:** Find optimal parcels for school development based on four key spatial and attribute criteria.

**Tools Used:**
- PostGIS (Spatial Database)
- QGIS (Geographic Visualization)
- SQL (Spatial Queries)

---

## Database Information

**Database Type:** PostgreSQL with PostGIS Extension    
**Total Tables:** 5 spatial layers

**Key Tables:**
- `landuse` - Land parcels with ownership and type information
- `buildings` - Building footprints
- `roads` - Road network
- `cistern` - Water infrastructure
- `sewage` - Sewage infrastructure

---

## Database Schema

### Landuse Table
| Column | Type | Description |
|--------|------|-------------|
| idd | integer | Primary key identifier |
| geom | geometry | Polygon geometry |
| id | integer | Secondary identifier |
| code | bigint | Land use code |
| owner | varchar | Property owner |
| type | varchar | Land use classification |
| sale | varchar | Sale status |
| no_of_appa | bigint | Number of apartments |
| area | double | Area in square meters |
| image | varchar | Reference image |

### Buildings Table
| Column | Type | Description |
|--------|------|-------------|
| idd | integer | Primary key identifier |
| geom | geometry | Polygon geometry |
| type | varchar | Building type |
| class | varchar | Building classification |
| area | double | Building area |
| owner | varchar | Building owner |
| address | varchar | Street address |

### Roads Table
| Column | Type | Description |
|--------|------|-------------|
| idd | integer | Primary key identifier |
| geom | geometry | Line geometry |
| type | varchar | Road type |
| name | varchar | Road name |
| length | double | Road length |
| avg_width | double | Average road width |
| condition | varchar | Road condition |

---

## Selection Criteria

The site selection process applies four sequential criteria:

### Criterion 1: Land Use Type
**Requirement:** Land must be classified as unused, agricultural, or commercial.

**SQL Implementation:**
```sql
WHERE type IN ('Un-Used', 'Agricultural Areas', 'Commercial Lands')
```

### Criterion 2: Minimum Area
**Requirement:** Parcel area must be ≥ 5000 m².

**SQL Implementation:**
```sql
AND ST_Area(geom) >= 5000
```

### Criterion 3: No Building Conflicts
**Requirement:** No existing buildings on the parcel.

**SQL Implementation:**
```sql
AND NOT EXISTS (
    SELECT 1 
    FROM buildings b 
    WHERE ST_Intersects(l.geom, b.geom)
)
```

### Criterion 4: Road Proximity
**Requirement:** Within 25 meters of nearest road.

**SQL Implementation:**
```sql
AND EXISTS (
    SELECT 1 
    FROM roads r 
    WHERE ST_DWithin(l.geom, r.geom, 25)
)
```

---

## Technical Implementation

### Complete SQL Query

```sql
-- Final query applying all four criteria
SELECT 
    l.idd,
    l.type,
    l.owner,
    l.area,
    l.geom,
    ST_Area(l.geom) as calculated_area
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
    l.area DESC;
```

### Save Results to New Table

```sql
CREATE TABLE final_school_locations AS
SELECT 
    l.idd,
    l.type,
    l.owner,
    l.area,
    l.geom,
    ST_Area(l.geom) as calculated_area
FROM 
    landuse l
WHERE 
    l.type IN ('Un-Used', 'Agricultural Areas', 'Commercial Lands')
    AND ST_Area(l.geom) >= 5000
    AND NOT EXISTS (
        SELECT 1 
        FROM buildings b 
        WHERE ST_Intersects(l.geom, b.geom)
    )
    AND EXISTS (
        SELECT 1 
        FROM roads r 
        WHERE ST_DWithin(l.geom, r.geom, 25)
    );
```

---

## Results Summary

### Filtering Progression

| Step | View Name | Count | Criteria Applied |
|------|-----------|-------|------------------|
| 1 | `suitable_landuse_types` | 140 | TYPE IN (Un-Used, Agricultural Areas, Commercial Lands) |
| 2 | `suitable_area_parcels` | 23 | ST_Area(geom) ≥ 5,000 m² |
| 3 | `parcels_without_buildings` | 17 | NOT ST_Intersects with buildings |
| 4 | `final_school_locations` | 7 | ST_DWithin roads 25m |

### 🏆 Final School Sites (7 Parcels)

| ID | Land Use Type | Area (m²) | Distance to Road (m) |
|----|---------------|-----------|----------------------|
| 20 | Agricultural Areas | 9,935.86 | 0.00 |
| 131 | Un-Used | 8,247.02 | 0.00 |
| 215 | Un-Used | 7,981.13 | 0.00 |
| 8 | Un-Used | 7,283.46 | 0.00 |
| 145 | Un-Used | 7,214.55 | 0.00 |
| 11 | Un-Used | 6,255.88 | 14.22 |
| 17 | Agricultural Areas | 5,861.30 | 0.00 |

### Summary by Land Use Type

| Land Use Type | Count | Total Area (m²) |
|---------------|-------|-----------------|
| Un-Used | 5 | 36,982.04 |
| Agricultural Areas | 2 | 15,797.16 |
| **Total** | **7** | **52,779.20** |

---

## Project Structure

```
school-site-selection/
│
├── school_data/
│   ├── shapeFiles/
|       ├── landuse.shp
│       ├── landuse.dbf
│       ├── landuse.prj
│       ├── landuse.shx
│       ├── buildings.shp
│       ├── buildings.dbf
│       ├── buildings.prj
│       ├── buildings.shx
│       ├── roads.shp
│       ├── roads.dbf
│       ├── roads.prj
│       └── roads.shx
│   
│
├── report/
│   ├── school-site-selection-report.docx
│   ├── school-site-selection-report.md
│   └── school-site-selection-report.pdf
│
├── visual-outputs/
│   ├── layers-names.png
│   └── layers-visual.png
│
├── assignment-school-question.png
├── model-builder.png
├── README.md
└── school-site-selection.qgz
```

---

## Getting Started

### Prerequisites

```bash
# Required software
- PostgreSQL 12+
- PostGIS 3.0+
- QGIS 3.16+
```

### Database Setup

```sql
-- Enable PostGIS extension
CREATE EXTENSION postgis;

-- Verify installation
SELECT PostGIS_Version();
```

### Running the Analysis

**Step 1:** Connect to your PostGIS database
```bash
psql -h localhost -U your_username -d your_database
```

**Step 2:** Execute the spatial query
```sql
-- Run the complete query from Technical Implementation section
```

**Step 3:** Verify results
```sql
SELECT COUNT(*) FROM final_school_locations;
```

**Step 4:** Export for QGIS
```sql
-- Results are automatically available for QGIS connection
```

---

## Workflow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    START: Landuse Table                      │
│                   (All land parcels)                         │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  CRITERION 1: Filter by Land Use Type                        │
│  → Un-Used, Agricultural Areas, Commercial Lands             │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  CRITERION 2: Filter by Minimum Area                         │
│  → Area >= 5000 m²                                           │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  CRITERION 3: Check for Building Conflicts                   │
│  → Exclude parcels with buildings (ST_Intersects)            │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  CRITERION 4: Check Road Proximity                           │
│  → Within 25m of roads (ST_DWithin)                          │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              RESULT: Suitable School Locations               │
│              → Export to QGIS for visualization              │
└─────────────────────────────────────────────────────────────┘
```

---

## Key Learnings

### Spatial Analysis Techniques

1. **Multi-Criteria Spatial Selection**
   - Sequential filtering improves query performance
   - Each criterion reduces candidate set progressively

2. **PostGIS Spatial Functions**
   - `ST_Area()` - Calculate polygon area
   - `ST_Intersects()` - Detect spatial overlap
   - `ST_DWithin()` - Distance-based proximity analysis

3. **Query Optimization**
   - Use `EXISTS` instead of `JOIN` for better performance
   - Spatial indexes critical for large datasets
   - Order criteria from most to least restrictive

---

## Author

**Ameer Saleh**  
Spatial Data Analysis Course  
School Site Selection using PostGIS

