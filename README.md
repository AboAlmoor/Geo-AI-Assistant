<div align="center">

# 🌍 Geo-AI-Assistant

###  Geospatial Data Analysis & Decision Support Systems

[![PostGIS](https://img.shields.io/badge/PostGIS-3.0+-blue.svg?style=flat-square&logo=postgresql)](https://postgis.net/)
[![Python](https://img.shields.io/badge/Python-3.8+-3776AB.svg?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![QGIS](https://img.shields.io/badge/QGIS-3.22+-589632.svg?style=flat-square&logo=qgis&logoColor=white)](https://qgis.org/)
[![GeoPandas](https://img.shields.io/badge/GeoPandas-1.0+-139C5A.svg?style=flat-square)](https://geopandas.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)

**Advanced spatial analytics portfolio demonstrating expertise in PostGIS, Python, and QGIS**  
**for real-world decision-making applications in urban planning, business intelligence, and risk management.**

[🚀 Quick Start](#-quick-start) • [📁 Projects](#-projects-overview) • [📖 Documentation](#-project-summaries) • [🛠️ Technologies](#-technologies)

</div>

---

## 📋 Table of Contents

- [🎯 Overview](#-overview)
- [⚡ Quick Start](#-quick-start)
- [📁 Projects Overview](#-projects-overview)
- [🛠️ Technologies](#-technologies)
- [✨ Key Features](#-key-features)
- [📦 Installation](#-installation)
- [📖 Project Summaries](#-project-summaries)
- [📊 Project Comparison](#-project-comparison)
- [🎓 Learning Outcomes](#-learning-outcomes)
- [👥 Authors](#-authors)
---

## 🎯 Overview

This repository showcases a comprehensive portfolio of professional geospatial analysis projects, demonstrating advanced expertise in **spatial data science**, **multi-criteria decision analysis (MCDA)**, and **GIS-based decision support systems**. Each project addresses real-world challenges in urban planning, business intelligence, and environmental risk management using industry-standard tools and methodologies.

### 🏆 Repository Highlights

| Feature | Description |
|---------|-------------|
| 📊 **Projects** | 3 complete end-to-end geospatial analysis projects |
| 🗄️ **Database** | PostGIS spatial queries with complex geometric operations |
| 🐍 **Automation** | Python scripts with GeoPandas for reproducible workflows |
| 🗺️ **Visualization** | Professional cartography and interactive QGIS projects |
| 📝 **Documentation** | Comprehensive technical reports and methodologies |
| 🎯 **Applications** | Business site selection, urban planning, risk assessment |

### 🌟 Why This Portfolio?

- **Real-World Applications:** Solves actual business and planning challenges
- **Industry Standards:** Uses professional GIS methodologies and best practices
- **Reproducible Research:** Fully documented workflows with data and code
- **Scalable Solutions:** Methodologies applicable to similar problems globally
- **Multi-Tool Proficiency:** Demonstrates expertise across SQL, Python, and GIS platforms

---

## ⚡ Quick Start

**Get started in 3 minutes:**

```bash
# 1. Clone the repository
git clone https://github.com/AboAlmoor/Geo-AI-Assistant.git
cd Geo-AI-Assistant

# 2. Install Python dependencies
pip install geopandas pandas numpy matplotlib

# 3. Explore projects
cd "ice cream project"     # PostGIS/QGIS project
cd "tree cutting priority project"  # Python automation project
```

**Or jump directly to:**
- 📖 [Ice Cream Site Selection Report](ice%20cream%20project/report/jen-barry-ice%20cream-report.md)
- 📖 [School Site Selection Report](school%20site%20select%20project/report/school-site-selection-report.md)
- 🐍 [Tree Cutting Python Script](tree%20cutting%20priority%20project/tree_cutting_priority.py)

---

## 📁 Projects Overview

### 🍦 Project 1: Ice Cream Business Site Selection

<table>
<tr>
<td><strong>Location</strong></td>
<td><code>ice cream project/</code></td>
</tr>
<tr>
<td><strong>Status</strong></td>
<td>✅ Complete</td>
</tr>
<tr>
<td><strong>Tools</strong></td>
<td>PostGIS • QGIS • SQL</td>
</tr>
<tr>
<td><strong>Domain</strong></td>
<td>Business Intelligence & Site Selection</td>
</tr>
<tr>
<td><strong>Complexity</strong></td>
<td>⭐⭐⭐ Advanced</td>
</tr>
</table>

**Business Challenge:**  
Identify optimal Pennsylvania locations for an ice cream business using multi-stage spatial filtering across demographic, infrastructure, and economic factors.

**Methodology:**  
7-criteria MCDA with staged filtering → 9 candidates → 7 near interstates → **4 optimal cities**

**Success Metrics:**
- ✅ 4 high-potential cities identified with 44% conversion rate
- ✅ Multi-layer spatial joins (counties, cities, infrastructure)
- ✅ Proximity analysis (20-mile interstates, 10-mile recreation)
- ✅ Demographic profiling (labor pool, population density)

**Key Technologies:**
- Spatial joins and geometric predicates
- Buffer analysis and distance calculations
- Multi-table attribute filtering
- Staged filtering workflow

📊 **[Full Documentation](ice%20cream%20project/README.md)** • 📝 **[Technical Report](ice%20cream%20project/report/jen-barry-ice%20cream-report.md)** • 🗺️ **[QGIS Project](ice%20cream%20project/ice%20cream.qgz)**

---

### 🏫 Project 2: School Site Selection Analysis

<table>
<tr>
<td><strong>Location</strong></td>
<td><code>school site select project/</code></td>
</tr>
<tr>
<td><strong>Status</strong></td>
<td>✅ Complete</td>
</tr>
<tr>
<td><strong>Tools</strong></td>
<td>PostGIS • QGIS • SQL</td>
</tr>
<tr>
<td><strong>Domain</strong></td>
<td>Urban Planning & Infrastructure</td>
</tr>
<tr>
<td><strong>Complexity</strong></td>
<td>⭐⭐⭐ Advanced</td>
</tr>
</table>

**Planning Challenge:**  
Identify suitable land parcels for new school construction using constraint-based spatial analysis and infrastructure proximity modeling.

**Methodology:**  
4-criteria sequential filtering → 140 parcels → attribute filter → conflict check → **7 suitable sites**

**Success Metrics:**
- ✅ 7 parcels identified (52,779 m² total development area)
- ✅ 5% success rate demonstrating rigorous filtering
- ✅ Average site: 7,540 m² (exceeds minimum by 50%)
- ✅ 85.7% directly adjacent to roads (excellent accessibility)

**Key Technologies:**
- Land use classification filtering
- Spatial overlay analysis (building conflicts)
- Distance-based proximity queries
- Area threshold validation

📊 **[Full Documentation](school%20site%20select%20project/README.md)** • 📝 **[Technical Report](school%20site%20select%20project/report/school-site-selection-report.md)** • 🗺️ **[QGIS Project](school%20site%20select%20project/school-site-selection.qgz)**

---

### 🌲 Project 3: Tree Cutting Priority - Wildfire Risk Assessment

<table>
<tr>
<td><strong>Location</strong></td>
<td><code>tree cutting priority project/</code></td>
</tr>
<tr>
<td><strong>Status</strong></td>
<td>✅ Complete</td>
</tr>
<tr>
<td><strong>Tools</strong></td>
<td>Python • GeoPandas • NumPy • Matplotlib</td>
</tr>
<tr>
<td><strong>Domain</strong></td>
<td>Environmental Risk Management</td>
</tr>
<tr>
<td><strong>Complexity</strong></td>
<td>⭐⭐⭐⭐ Expert</td>
</tr>
</table>

**Risk Management Challenge:**  
Prioritize tree removal across 80 zones in Fire Creek to mitigate wildfire risk using weighted multi-criteria decision analysis.

**Methodology:**  
5-factor weighted scoring → normalization (0-100) → classification → **80 prioritized zones**

**Success Metrics:**
- ✅ Complete spatial coverage (80 zones analyzed)
- ✅ Normalized scoring for fair comparison
- ✅ 4-tier priority classification (Low/Medium/High/Critical)
- ✅ Automated Python workflow (reproducible)
- ✅ Statistical visualization charts

**Key Technologies:**
- Weighted multi-criteria scoring
- Score normalization algorithms
- Spatial overlay operations (5 layers)
- Automated data processing pipeline
- Statistical analysis and visualization

📊 **[Full Documentation](tree%20cutting%20priority%20project/README.md)** • 🐍 **[Python Script](tree%20cutting%20priority%20project/tree_cutting_priority.py)** • 📊 **[Output Data](tree%20cutting%20priority%20project/output/)**

---

## � Project Comparison

| Feature | Ice Cream Site Selection | School Site Selection | Tree Cutting Priority |
|---------|-------------------------|----------------------|----------------------|
| **Primary Tool** | PostGIS + QGIS | PostGIS + QGIS | Python + GeoPandas |
| **Analysis Type** | Multi-stage filtering | Constraint-based | Weighted scoring |
| **Input Layers** | 4 layers | 5 layers | 10 layers |
| **Criteria Count** | 7 criteria | 4 criteria | 5 factors |
| **Output Type** | Point locations | Polygon parcels | Scored grid zones |
| **Results** | 4 cities | 7 parcels | 80 zones |
| **Automation Level** | Manual SQL | Manual SQL | Fully automated |
| **Best For Learning** | Spatial joins | Constraint analysis | Python automation |

---

## 🎓 Learning Outcomes

**After exploring these projects, you will understand:**

✅ **Spatial Database Management**
- PostGIS installation and configuration
- Importing and managing spatial data (shapefiles, GeoPackage)
- Creating spatial indexes for performance optimization

✅ **Advanced SQL & Spatial Queries**
- Complex multi-table joins with spatial predicates
- Buffer analysis and distance calculations
- Overlay operations (intersects, within, contains)
- Attribute filtering and aggregations

✅ **Multi-Criteria Decision Analysis**
- Criteria definition and weighting
- Scoring and normalization techniques
- Classification and ranking methods

✅ **Python Geospatial Automation**
- GeoPandas for spatial data manipulation
- Automated workflows for reproducible analysis
- Data export in multiple formats

✅ **Professional Cartography**
- QGIS styling and symbolization
- Layout design for presentations
- Creating publication-ready maps

---

## 📦 Installation

### Prerequisites

```bash
# Database
PostgreSQL 12+ with PostGIS 3.0+

# Python Environment
Python 3.8+
geopandas
pandas
numpy
matplotlib

# GIS Software
QGIS 3.22+
```

### Installation Steps

1. **Clone the repository:**
```bash
git clone https://github.com/AboAlmoor/Geo-AI-Assistant.git
cd Geo-AI-Assistant
```

2. **Install Python dependencies:**
```bash
pip install geopandas pandas numpy matplotlib
```

3. **Set up PostGIS database:**
```sql
CREATE DATABASE spatial_analysis;
CREATE EXTENSION postgis;
```

4. **Open QGIS projects:**
- Navigate to project folder and open `.qgz` files
- `ice cream project/ice cream.qgz`
- `school site select project/school-site-selection.qgz`

### Usage

**For PostGIS projects** (Ice Cream, School Selection):
1. Import shapefiles to PostGIS
2. Execute SQL queries sequentially
3. Visualize results in QGIS

**For Python projects** (Tree Cutting):
```bash
cd "tree cutting priority project"
python tree_cutting_priority.py
```

---

## 🛠️ Technologies

### Database & Query Languages
- Weighted scoring models
- Normalization techniques

---

## ✨ Key Features

### 🎯 Multi-Criteria Decision Analysis
All projects employ systematic MCDA methodologies with clear criteria, weighting schemes, and scoring systems.

### 📊 Professional Documentation
Each project includes:
- Comprehensive README with methodology
- Detailed technical reports
- Database schema documentation
- SQL query explanations

### 🗺️ Reproducible Workflows
- Well-structured project directories
- Documented data sources
- Reusable SQL queries
- Python scripts with comments

### 📈 Visual Outputs
- QGIS project files (.qgz) with professional styling
- Static map exports
- Charts and statistical visualizations
- Before/after comparison maps

---

## 🚀 Getting Started

### Prerequisites

```bash
# Database
PostgreSQL 12+ with PostGIS 3.0+

# Python Environment
Python 3.8+
geopandas
pandas
numpy
matplotlib

# GIS Software
QGIS 3.22+
```

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/AboAlmoor/Geo-AI-Assistant.git

```

2. **Install Python dependencies:**
```bash
pip install geopandas pandas numpy matplotlib
```

3. **Set up PostGIS database:**
```sql
CREATE DATABASE spatial_analysis;
CREATE EXTENSION postgis;
```

4. **Open QGIS projects:**
```bash
# Navigate to project folder and open .qgz files
ice cream project/ice cream.qgz
school site select project/school-site-selection.qgz
```

### Usage

Each project contains its own README with specific instructions. Generally:

1. **For PostGIS projects** (Ice Cream, School Selection):
   - Import shapefiles to PostGIS
   - Execute SQL queries sequentially
   - Visualize results in QGIS

2. **For Python projects** (Tree Cutting):
   ```bash
   cd "tree cutting priority project"
   python tree_cutting_priority.py
   ```

---

## 📑 Project Summaries

### Ice Cream Site Selection

**Problem:** Identify optimal Pennsylvania cities for ice cream business establishment  
**Approach:** Multi-stage spatial filtering with demographic and infrastructure criteria  
**Output:** 4 recommended cities with full justification

**Technical Highlights:**
- Spatial joins across 4 layers
- Buffer analysis (20-mile interstate, 10-mile recreation areas)
- Attribute filtering with multiple thresholds
- Stage-gate selection process

---

### School Site Selection

**Problem:** Find suitable land parcels for new school construction  
**Approach:** Constraint-based spatial analysis with land use and proximity criteria  
**Output:** 7 suitable parcels totaling 52,779 m²

**Technical Highlights:**
- Land use classification filtering
- Spatial overlay analysis (buildings exclusion)
- Distance-based selection (road proximity)
- Area threshold filtering

---

### Tree Cutting Priority

**Problem:** Prioritize tree removal zones for wildfire risk mitigation  
**Approach:** Weighted multi-criteria scoring with normalization  
**Output:** 80 prioritized zones with classification (Low/Medium/High/Critical)

**Technical Highlights:**
- 5-factor weighted scoring model
- Score normalization (0-100 scale)
- Automated Python workflow
- Statistical visualizations and charts

---

## 👥 Authors

<table>
<tr>
<td align="center">
<strong>Ameer Saleh</strong><br>
<sub>Developer</sub><br>
<br>
PostGIS • Python • QGIS<br>
</td>
<td align="center">
<strong>Bara Mhana</strong><br>
<sub>Developer</sub><br>
<br>
PostGIS • Python • QGIS<br>
</td>
</tr>
</table>

**Expertise Areas:**
- 🗄️ Spatial Database Design & Management (PostGIS)
- 🐍 Geospatial Python Programming (GeoPandas, Shapely)
- 🗺️ Professional GIS & Cartography (QGIS)
- 📊 Multi-Criteria Decision Analysis (MCDA)
- 🎯 Site Selection & Location Analysis
- 🌍 Urban Planning & Risk Assessment


## 🏆 Acknowledgments

- Projects completed as part of **Spatial Data Analysis** graduate coursework
- Data sources and attributions documented in individual project READMEs
- Special thanks to instructors and peers for valuable feedback and guidance
- Built with open-source GIS tools and libraries

---

<div align="center">

### 🌟 Star this repo if you find it helpful!

**Built with 🗺️ by Geospatial Data Scientists**

[![GitHub](https://img.shields.io/badge/View%20on-GitHub-181717?style=for-the-badge&logo=github)](https://github.com/AboAlmoor/Geo-AI-Assistant)

[⭐ View Projects](#-projects-overview) • [📖 Documentation](#-project-summaries) • [🚀 Quick Start](#-quick-start)

---

*Last Updated: December 2025 • Version 1.0*

</div>
