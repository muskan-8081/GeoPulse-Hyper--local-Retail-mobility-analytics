
import pandas as pd
import numpy as np
import os

# Create output folders
os.makedirs("data/processed", exist_ok=True)
os.makedirs("reports", exist_ok=True)

# Load GPS dataset
gps = pd.read_csv("data/raw/delhi_gps_pings.csv")

# Grid size in decimal degrees
GRID_SIZE = 0.005

# Assign each GPS record to a geographical grid cell
gps["GridLat"] = np.floor(
    gps["Latitude"] / GRID_SIZE
) * GRID_SIZE

gps["GridLon"] = np.floor(
    gps["Longitude"] / GRID_SIZE
) * GRID_SIZE

# Group GPS records by grid cell
hotspots = gps.groupby(
    ["GridLat", "GridLon"]
).agg(
    GPSPingCount=("DeviceID", "count"),
    UniqueDevices=("DeviceID", "nunique")
).reset_index()

# Calculate approximate grid centre coordinates
hotspots["CenterLatitude"] = (
    hotspots["GridLat"] + GRID_SIZE / 2
)

hotspots["CenterLongitude"] = (
    hotspots["GridLon"] + GRID_SIZE / 2
)

# Rank geographical areas by GPS activity
hotspots["HotspotRank"] = (
    hotspots["GPSPingCount"]
    .rank(method="dense", ascending=False)
    .astype(int)
)

# Classify activity using percentile thresholds
high_threshold = hotspots["GPSPingCount"].quantile(0.75)
low_threshold = hotspots["GPSPingCount"].quantile(0.25)

def classify_activity(count):
    if count >= high_threshold:
        return "High"
    elif count >= low_threshold:
        return "Medium"
    return "Low"

hotspots["ActivityLevel"] = (
    hotspots["GPSPingCount"].apply(classify_activity)
)

# Sort by GPS activity
hotspots = hotspots.sort_values(
    "GPSPingCount", ascending=False
)

# Select final columns
hotspots = hotspots[
    [
        "HotspotRank",
        "CenterLatitude",
        "CenterLongitude",
        "GPSPingCount",
        "UniqueDevices",
        "ActivityLevel"
    ]
]

# Save processed dataset
hotspots.to_csv(
    "data/processed/gps_hotspots.csv",
    index=False
)

# Calculate summary statistics
total_pings = len(gps)
total_cells = len(hotspots)
high_zones = (hotspots["ActivityLevel"] == "High").sum()
medium_zones = (hotspots["ActivityLevel"] == "Medium").sum()
low_zones = (hotspots["ActivityLevel"] == "Low").sum()

top_hotspot = hotspots.iloc[0]

# Generate report
report = f"""
DELHI GPS HOTSPOT ANALYSIS REPORT
=================================

Project: GeoPulse - Hyperlocal Retail Mobility Analytics

1. OVERALL SUMMARY
------------------
Total GPS Records: {total_pings}
Total Active Grid Cells: {total_cells}
Grid Cell Size: {GRID_SIZE} decimal degrees

2. HIGHEST ACTIVITY HOTSPOT
---------------------------
Hotspot Rank: {top_hotspot['HotspotRank']}
Latitude: {top_hotspot['CenterLatitude']:.6f}
Longitude: {top_hotspot['CenterLongitude']:.6f}
GPS Pings: {top_hotspot['GPSPingCount']}
Unique Devices: {top_hotspot['UniqueDevices']}

3. ACTIVITY ZONE DISTRIBUTION
-----------------------------
High Activity Zones: {high_zones}
Medium Activity Zones: {medium_zones}
Low Activity Zones: {low_zones}

4. TOP 10 GPS HOTSPOTS
---------------------
{hotspots.head(10).to_string(index=False)}

5. METHODOLOGY AND LIMITATIONS
------------------------------
GPS coordinates were grouped into geographical grid cells
using a grid size of 0.005 decimal degrees.

Each cell was ranked based on its GPS ping count.

Activity levels were classified using the 25th and
75th percentile thresholds.

The dataset is synthetic and represents simulated
GPS activity, not verified real-world customer movement
or actual retail footfall.

Grid cells are approximate geographic areas and their
physical dimensions vary slightly with latitude.
"""

with open(
    "reports/gps_hotspot_report.txt",
    "w",
    encoding="utf-8"
) as file:
    file.write(report)

# Display results
print("\nGPS HOTSPOT ANALYSIS COMPLETED")
print("--------------------------------")
print(f"Total GPS Records: {total_pings}")
print(f"Total Active Grid Cells: {total_cells}")
print(f"High Activity Zones: {high_zones}")
print(f"Medium Activity Zones: {medium_zones}")
print(f"Low Activity Zones: {low_zones}")

print("\nTOP 10 GPS HOTSPOTS")
print(hotspots.head(10).to_string(index=False))

print("\nGenerated files:")
print("- data/processed/gps_hotspots.csv")
print("- reports/gps_hotspot_report.txt")
