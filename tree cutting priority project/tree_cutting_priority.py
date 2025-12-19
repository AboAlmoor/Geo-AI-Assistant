"""
Tree Cutting Priority Analysis for Fire Creek
==============================================

This script calculates tree cutting priority for each zone in the cutting grid
based on five factors:
1. Tree Mortality (SBNFMortalityt)
2. Community Features (Communityfeatures)
3. Egress Routes (EgressRoutes)
4. Populated Areas (PopulatedAreast)
5. Electric Utilities (Transmission, SubTransmission, DistCircuits, Substations, PoleTopSubs)

The final output is a grid with priority values for each zone.
"""

import geopandas as gpd
import pandas as pd
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Set data directory
DATA_DIR = Path(r"C:/Users/baram/Desktop/Raster/data")
OUTPUT_DIR = Path(r"C:/Users/baram/Desktop/Raster/output")
OUTPUT_DIR.mkdir(exist_ok=True)

print("=" * 60)
print("Tree Cutting Priority Analysis - Fire Creek")
print("=" * 60)

# ============================================================================
# STEP 1: Load all shapefiles
# ============================================================================
print("\n[STEP 1] Loading shapefiles...")

# Load cutting grids (main analysis unit)
cutting_grids = gpd.read_file(DATA_DIR / "CuttingGrids.shp")
print(f"  - CuttingGrids: {len(cutting_grids)} zones loaded")

# Load tree mortality data
mortality = gpd.read_file(DATA_DIR / "SBNFMortalityt.shp")
print(f"  - SBNFMortalityt (Tree Mortality): {len(mortality)} features loaded")

# Load community features
community = gpd.read_file(DATA_DIR / "Communityfeatures.shp")
print(f"  - Communityfeatures: {len(community)} features loaded")

# Load egress routes
egress = gpd.read_file(DATA_DIR / "EgressRoutes.shp")
print(f"  - EgressRoutes: {len(egress)} features loaded")

# Load populated areas
populated = gpd.read_file(DATA_DIR / "PopulatedAreast.shp")
print(f"  - PopulatedAreast: {len(populated)} features loaded")

# Load electric utilities
transmission = gpd.read_file(DATA_DIR / "Transmission.shp")
subtransmission = gpd.read_file(DATA_DIR / "SubTransmission.shp")
dist_circuits = gpd.read_file(DATA_DIR / "DistCircuits.shp")
substations = gpd.read_file(DATA_DIR / "Substations.shp")
poletop_subs = gpd.read_file(DATA_DIR / "PoleTopSubs.shp")
print(f"  - Transmission: {len(transmission)} features loaded")
print(f"  - SubTransmission: {len(subtransmission)} features loaded")
print(f"  - DistCircuits: {len(dist_circuits)} features loaded")
print(f"  - Substations: {len(substations)} features loaded")
print(f"  - PoleTopSubs: {len(poletop_subs)} features loaded")

# Load town boundary for reference
town_boundary = gpd.read_file(DATA_DIR / "TownBoundary.shp")
print(f"  - TownBoundary: {len(town_boundary)} features loaded")

# ============================================================================
# STEP 2: Ensure all layers have the same CRS
# ============================================================================
print("\n[STEP 2] Checking and aligning coordinate reference systems...")

target_crs = cutting_grids.crs
print(f"  Target CRS: {target_crs}")

# Reproject all layers to match cutting grids
mortality = mortality.to_crs(target_crs)
community = community.to_crs(target_crs)
egress = egress.to_crs(target_crs)
populated = populated.to_crs(target_crs)
transmission = transmission.to_crs(target_crs)
subtransmission = subtransmission.to_crs(target_crs)
dist_circuits = dist_circuits.to_crs(target_crs)
substations = substations.to_crs(target_crs)
poletop_subs = poletop_subs.to_crs(target_crs)

print("  All layers reprojected to target CRS")

# ============================================================================
# STEP 3: Initialize priority scores dataframe
# ============================================================================
print("\n[STEP 3] Initializing priority calculation...")

# Create a copy of cutting grids for results
result = cutting_grids.copy()
result['mortality_score'] = 0.0
result['community_score'] = 0.0
result['egress_score'] = 0.0
result['populated_score'] = 0.0
result['utility_score'] = 0.0

# ============================================================================
# STEP 4: Calculate Tree Mortality Score
# ============================================================================
print("\n[STEP 4] Calculating Tree Mortality Score...")

# Check if mortality has Tot_mortal column (case-sensitive)
mort_col = None
for col in mortality.columns:
    if col.lower() == 'tot_mortal':
        mort_col = col
        break

if mort_col:
    # Spatial join to find mortality areas intersecting each grid
    for idx, grid in result.iterrows():
        grid_geom = grid.geometry
        # Find intersecting mortality areas
        intersects = mortality[mortality.geometry.intersects(grid_geom)]
        if len(intersects) > 0:
            # Calculate weighted mortality based on intersection area
            total_mortality = 0
            for _, mort in intersects.iterrows():
                intersection = grid_geom.intersection(mort.geometry)
                if not intersection.is_empty:
                    # Weight by intersection area proportion
                    area_ratio = intersection.area / grid_geom.area
                    total_mortality += mort[mort_col] * area_ratio
            result.at[idx, 'mortality_score'] = total_mortality
    
    # Normalize mortality score (0-100)
    max_mort = result['mortality_score'].max()
    if max_mort > 0:
        result['mortality_score'] = (result['mortality_score'] / max_mort) * 100
    print(f"  Mortality scores calculated (max raw: {max_mort:.2f})")
else:
    print("  Warning: 'Tot_mortal' column not found in mortality data")

# ============================================================================
# STEP 5: Calculate Community Features Score
# ============================================================================
print("\n[STEP 5] Calculating Community Features Score...")

# Check if community has weight column
weight_col = 'weight' if 'weight' in community.columns else None

for idx, grid in result.iterrows():
    grid_geom = grid.geometry
    # Find community features within or near the grid
    intersects = community[community.geometry.intersects(grid_geom)]
    if len(intersects) > 0:
        if weight_col:
            # Sum weights of intersecting features
            result.at[idx, 'community_score'] = intersects[weight_col].sum()
        else:
            # Count features if no weight
            result.at[idx, 'community_score'] = len(intersects)

# Normalize community score (0-100)
max_comm = result['community_score'].max()
if max_comm > 0:
    result['community_score'] = (result['community_score'] / max_comm) * 100
print(f"  Community scores calculated (max raw: {max_comm:.2f})")

# ============================================================================
# STEP 6: Calculate Egress Routes Score
# ============================================================================
print("\n[STEP 6] Calculating Egress Routes Score...")

# Check if egress has weight column
weight_col = 'weight' if 'weight' in egress.columns else None

for idx, grid in result.iterrows():
    grid_geom = grid.geometry
    # Find egress routes intersecting the grid
    intersects = egress[egress.geometry.intersects(grid_geom)]
    if len(intersects) > 0:
        if weight_col:
            # Calculate weighted length of routes in grid
            total_score = 0
            for _, route in intersects.iterrows():
                intersection = grid_geom.intersection(route.geometry)
                if not intersection.is_empty:
                    # Weight by length within grid
                    total_score += route[weight_col] * intersection.length
            result.at[idx, 'egress_score'] = total_score
        else:
            # Sum length of routes in grid
            total_length = 0
            for _, route in intersects.iterrows():
                intersection = grid_geom.intersection(route.geometry)
                if not intersection.is_empty:
                    total_length += intersection.length
            result.at[idx, 'egress_score'] = total_length

# Normalize egress score (0-100)
max_egress = result['egress_score'].max()
if max_egress > 0:
    result['egress_score'] = (result['egress_score'] / max_egress) * 100
print(f"  Egress scores calculated (max raw: {max_egress:.2f})")

# ============================================================================
# STEP 7: Calculate Populated Areas Score
# ============================================================================
print("\n[STEP 7] Calculating Populated Areas Score...")

for idx, grid in result.iterrows():
    grid_geom = grid.geometry
    # Find populated areas intersecting the grid
    intersects = populated[populated.geometry.intersects(grid_geom)]
    if len(intersects) > 0:
        # Calculate intersection area as proportion of grid
        total_pop_area = 0
        for _, pop in intersects.iterrows():
            intersection = grid_geom.intersection(pop.geometry)
            if not intersection.is_empty:
                total_pop_area += intersection.area
        # Score based on proportion of grid that is populated
        result.at[idx, 'populated_score'] = (total_pop_area / grid_geom.area) * 100

# Normalize populated score (0-100)
max_pop = result['populated_score'].max()
if max_pop > 0:
    result['populated_score'] = (result['populated_score'] / max_pop) * 100
print(f"  Populated area scores calculated (max raw: {max_pop:.2f})")

# ============================================================================
# STEP 8: Calculate Electric Utilities Score
# ============================================================================
print("\n[STEP 8] Calculating Electric Utilities Score...")

# Combine all utility features with different weights
# Transmission lines: highest priority (weight 3)
# SubTransmission: medium-high priority (weight 2.5)
# Distribution circuits: medium priority (weight 2)
# Substations: high priority (weight 3)
# Pole top subs: medium priority (weight 2)

for idx, grid in result.iterrows():
    grid_geom = grid.geometry
    utility_score = 0
    
    # Transmission lines (weight 3)
    trans_intersects = transmission[transmission.geometry.intersects(grid_geom)]
    if len(trans_intersects) > 0:
        for _, line in trans_intersects.iterrows():
            intersection = grid_geom.intersection(line.geometry)
            if not intersection.is_empty:
                # Use weight column if available (case-insensitive)
                line_weight = 1
                if 'weight' in transmission.columns:
                    line_weight = line['weight'] if pd.notna(line['weight']) else 1
                utility_score += intersection.length * 3 * line_weight
    
    # SubTransmission lines (weight 2.5)
    subtrans_intersects = subtransmission[subtransmission.geometry.intersects(grid_geom)]
    if len(subtrans_intersects) > 0:
        for _, line in subtrans_intersects.iterrows():
            intersection = grid_geom.intersection(line.geometry)
            if not intersection.is_empty:
                # Use Priority column (case-sensitive)
                priority = 1
                if 'Priority' in subtransmission.columns:
                    priority = line['Priority'] if pd.notna(line['Priority']) else 1
                utility_score += intersection.length * 2.5 * priority
    
    # Distribution circuits (weight 2)
    dist_intersects = dist_circuits[dist_circuits.geometry.intersects(grid_geom)]
    if len(dist_intersects) > 0:
        for _, line in dist_intersects.iterrows():
            intersection = grid_geom.intersection(line.geometry)
            if not intersection.is_empty:
                utility_score += intersection.length * 2
    
    # Substations (weight 3) - point features
    sub_intersects = substations[substations.geometry.intersects(grid_geom)]
    if len(sub_intersects) > 0:
        for _, sub in sub_intersects.iterrows():
            # Use Priority column (case-sensitive)
            priority = 1
            if 'Priority' in substations.columns:
                priority = sub['Priority'] if pd.notna(sub['Priority']) else 1
            utility_score += 1000 * 3 * priority  # Fixed score for point features
    
    # Pole top subs (weight 2) - point features
    pole_intersects = poletop_subs[poletop_subs.geometry.intersects(grid_geom)]
    if len(pole_intersects) > 0:
        utility_score += len(pole_intersects) * 500 * 2  # Fixed score for each pole top sub
    
    result.at[idx, 'utility_score'] = utility_score

# Normalize utility score (0-100)
max_util = result['utility_score'].max()
if max_util > 0:
    result['utility_score'] = (result['utility_score'] / max_util) * 100
print(f"  Utility scores calculated (max raw: {max_util:.2f})")

# ============================================================================
# STEP 9: Calculate Overall Priority Score
# ============================================================================
print("\n[STEP 9] Calculating Overall Tree Cutting Priority...")

# Define weights for each factor (can be adjusted based on requirements)
WEIGHTS = {
    'mortality': 0.30,      # 30% - Tree mortality is critical
    'community': 0.15,      # 15% - Community features protection
    'egress': 0.20,         # 20% - Egress routes for safety
    'populated': 0.20,      # 20% - Populated areas protection
    'utility': 0.15         # 15% - Electric utilities protection
}

print(f"  Weights applied:")
print(f"    - Tree Mortality: {WEIGHTS['mortality']*100:.0f}%")
print(f"    - Community Features: {WEIGHTS['community']*100:.0f}%")
print(f"    - Egress Routes: {WEIGHTS['egress']*100:.0f}%")
print(f"    - Populated Areas: {WEIGHTS['populated']*100:.0f}%")
print(f"    - Electric Utilities: {WEIGHTS['utility']*100:.0f}%")

# Calculate weighted priority score
result['priority_score'] = (
    result['mortality_score'] * WEIGHTS['mortality'] +
    result['community_score'] * WEIGHTS['community'] +
    result['egress_score'] * WEIGHTS['egress'] +
    result['populated_score'] * WEIGHTS['populated'] +
    result['utility_score'] * WEIGHTS['utility']
)

# Classify priority into categories
def classify_priority(score):
    if score >= 75:
        return 'Critical'
    elif score >= 50:
        return 'High'
    elif score >= 25:
        return 'Medium'
    else:
        return 'Low'

result['priority_class'] = result['priority_score'].apply(classify_priority)

# Assign numeric priority rank (1 = highest priority)
result['priority_rank'] = result['priority_score'].rank(ascending=False, method='min').astype(int)

# ============================================================================
# STEP 10: Output Results
# ============================================================================
print("\n[STEP 10] Saving results...")

# Find the grid column name (case-insensitive)
grid_col = None
for col in result.columns:
    if col.lower() == 'grid':
        grid_col = col
        break

# Ensure result is a GeoDataFrame with proper geometry
result = gpd.GeoDataFrame(result, geometry='geometry', crs=target_crs)

# Shorten column names for shapefile compatibility (max 10 characters)
# Create a mapping for column names
column_mapping = {
    'mortality_score': 'mort_score',
    'community_score': 'comm_score',
    'egress_score': 'egrs_score',
    'populated_score': 'pop_score',
    'utility_score': 'util_score',
    'priority_score': 'priority_s',
    'priority_class': 'prior_cls',
    'priority_rank': 'prior_rank'
}

# Rename columns
result_output = result.rename(columns=column_mapping)

# Select columns for output (with shortened names)
output_columns = [
    grid_col, 'geometry',
    'mort_score', 'comm_score', 'egrs_score', 
    'pop_score', 'util_score',
    'priority_s', 'prior_cls', 'prior_rank'
]

# Keep only columns that exist and are not None
output_columns = [col for col in output_columns if col is not None and col in result_output.columns]
output_gdf = gpd.GeoDataFrame(result_output[output_columns], geometry='geometry', crs=target_crs)

# Verify geometry is valid
print(f"  Output CRS: {output_gdf.crs}")
print(f"  Geometry type: {output_gdf.geometry.geom_type.unique()}")
print(f"  Total features: {len(output_gdf)}")

# Save as shapefile (use timestamp to avoid file lock issues)
from datetime import datetime
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

output_shp = OUTPUT_DIR / f"TreeCuttingPriority_{timestamp}.shp"
output_gdf.to_file(output_shp, driver='ESRI Shapefile')
print(f"  Shapefile saved: {output_shp}")

# Also save as GeoPackage (better format, no column name limitations)
output_gpkg = OUTPUT_DIR / f"TreeCuttingPriority_{timestamp}.gpkg"
result.to_file(output_gpkg, driver='GPKG', layer='tree_cutting_priority')
print(f"  GeoPackage saved: {output_gpkg}")

# Save as CSV (without geometry)
output_csv = OUTPUT_DIR / "TreeCuttingPriority.csv"
result_df = result.drop(columns=['geometry'])
result_df.to_csv(output_csv, index=False)
print(f"  CSV saved: {output_csv}")

# ============================================================================
# STEP 11: Display Summary
# ============================================================================
print("\n" + "=" * 60)
print("TREE CUTTING PRIORITY ANALYSIS - SUMMARY")
print("=" * 60)

print("\nPriority Distribution:")
print(result['priority_class'].value_counts().to_string())

print("\nTop 10 Priority Zones:")
# Find the grid column name (case-insensitive)
grid_col = None
for col in result.columns:
    if col.lower() == 'grid':
        grid_col = col
        break
if grid_col:
    top_10 = result.nsmallest(10, 'priority_rank')[[grid_col, 'priority_score', 'priority_class', 'priority_rank']]
    print(top_10.to_string(index=False))
else:
    top_10 = result.nsmallest(10, 'priority_rank')[['priority_score', 'priority_class', 'priority_rank']]
    print(top_10.to_string(index=False))

print("\nScore Statistics:")
print(f"  Mean Priority Score: {result['priority_score'].mean():.2f}")
print(f"  Max Priority Score: {result['priority_score'].max():.2f}")
print(f"  Min Priority Score: {result['priority_score'].min():.2f}")
print(f"  Std Dev: {result['priority_score'].std():.2f}")

print("\nFactor Score Ranges:")
print(f"  Mortality: {result['mortality_score'].min():.2f} - {result['mortality_score'].max():.2f}")
print(f"  Community: {result['community_score'].min():.2f} - {result['community_score'].max():.2f}")
print(f"  Egress: {result['egress_score'].min():.2f} - {result['egress_score'].max():.2f}")
print(f"  Populated: {result['populated_score'].min():.2f} - {result['populated_score'].max():.2f}")
print(f"  Utility: {result['utility_score'].min():.2f} - {result['utility_score'].max():.2f}")

print("\n" + "=" * 60)
print("Analysis Complete!")
print(f"Output files saved to: {OUTPUT_DIR}")
print("=" * 60)

# ============================================================================
# STEP 12: Generate Visualization Charts
# ============================================================================
print("\n[STEP 12] Generating visualization charts...")

import matplotlib.pyplot as plt

# Set up the figure with 3 subplots
fig, axes = plt.subplots(1, 3, figsize=(18, 6))
fig.suptitle('Tree Cutting Priority Analysis - Fire Creek', fontsize=16, fontweight='bold')

# Define colors for priority classes
priority_colors = {
    'Critical': '#E53935',  # Red
    'High': '#FB8C00',      # Orange
    'Medium': '#FDD835',    # Yellow
    'Low': '#43A047'        # Green
}

# Ensure consistent order for priority classes
priority_order = ['Critical', 'High', 'Medium', 'Low']

# Get priority class counts
priority_counts = result['priority_class'].value_counts()
# Reindex to ensure all classes are present and in order
priority_counts = priority_counts.reindex(priority_order, fill_value=0)

# -------------------------
# Chart 1: Bar Chart - Number of Grids per Priority Class
# -------------------------
ax1 = axes[0]
bars1 = ax1.bar(priority_counts.index, priority_counts.values, 
                color=[priority_colors[c] for c in priority_counts.index],
                edgecolor='black', linewidth=1.2)

# Add value labels on bars
for bar, count in zip(bars1, priority_counts.values):
    height = bar.get_height()
    ax1.annotate(f'{int(count)}',
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3),
                textcoords="offset points",
                ha='center', va='bottom',
                fontsize=12, fontweight='bold')

ax1.set_xlabel('Priority Class', fontsize=12)
ax1.set_ylabel('Number of Grid Zones', fontsize=12)
ax1.set_title('Grid Zones by Priority Class', fontsize=14, fontweight='bold')
ax1.set_ylim(0, max(priority_counts.values) * 1.15)
ax1.grid(axis='y', alpha=0.3)

# -------------------------
# Chart 2: Pie Chart - Percentage Distribution
# -------------------------
ax2 = axes[1]

# Filter out zero values for pie chart
non_zero_counts = priority_counts[priority_counts > 0]
pie_colors = [priority_colors[c] for c in non_zero_counts.index]

wedges, texts, autotexts = ax2.pie(non_zero_counts.values, 
                                    labels=non_zero_counts.index,
                                    colors=pie_colors,
                                    autopct='%1.1f%%',
                                    startangle=90,
                                    explode=[0.02] * len(non_zero_counts),
                                    shadow=True,
                                    textprops={'fontsize': 11})

# Style the percentage text
for autotext in autotexts:
    autotext.set_fontweight('bold')
    autotext.set_fontsize(10)

ax2.set_title('Priority Class Distribution', fontsize=14, fontweight='bold')

# Add legend with counts
legend_labels = [f'{label}: {count} zones' for label, count in zip(non_zero_counts.index, non_zero_counts.values)]
ax2.legend(wedges, legend_labels, loc='lower center', bbox_to_anchor=(0.5, -0.1), fontsize=10)

# -------------------------
# Chart 3: Bar Chart - Top 10 Priority Zones
# -------------------------
ax3 = axes[2]

# Get top 10 zones by priority score
top_10 = result.nsmallest(10, 'priority_rank').copy()

# Get grid identifiers
if grid_col:
    top_10_labels = top_10[grid_col].astype(str).values
else:
    top_10_labels = [f'Zone {i+1}' for i in range(len(top_10))]

top_10_scores = top_10['priority_score'].values
top_10_classes = top_10['priority_class'].values

# Create horizontal bar chart
bars3 = ax3.barh(range(len(top_10_labels)), top_10_scores,
                 color=[priority_colors[c] for c in top_10_classes],
                 edgecolor='black', linewidth=1.2)

ax3.set_yticks(range(len(top_10_labels)))
ax3.set_yticklabels([f'Grid {label}' for label in top_10_labels], fontsize=10)
ax3.invert_yaxis()  # Highest at top

# Add value labels on bars
for bar, score, cls in zip(bars3, top_10_scores, top_10_classes):
    width = bar.get_width()
    ax3.annotate(f'{score:.1f} ({cls})',
                xy=(width, bar.get_y() + bar.get_height() / 2),
                xytext=(5, 0),
                textcoords="offset points",
                ha='left', va='center',
                fontsize=9, fontweight='bold')

ax3.set_xlabel('Priority Score', fontsize=12)
ax3.set_ylabel('Grid Zone', fontsize=12)
ax3.set_title('Top 10 Highest Priority Zones', fontsize=14, fontweight='bold')
ax3.set_xlim(0, max(top_10_scores) * 1.25)
ax3.grid(axis='x', alpha=0.3)

# Adjust layout
plt.tight_layout()
plt.subplots_adjust(top=0.9)

# Save the figure
chart_path = OUTPUT_DIR / "TreeCuttingPriority_Charts.png"
plt.savefig(chart_path, dpi=300, bbox_inches='tight', facecolor='white')
print(f"  Charts saved: {chart_path}")

# Display the charts
plt.show()

print("\n" + "=" * 60)
print("Visualization Complete!")
print("=" * 60)
