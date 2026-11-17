
import pandas as pd
import os

# File paths
gps_file = "data/raw/delhi_gps_pings.csv"
store_file = "data/raw/delhi_store_locations.csv"

processed_folder = "data/processed"
reports_folder = "reports"

os.makedirs(processed_folder, exist_ok=True)
os.makedirs(reports_folder, exist_ok=True)

# Load datasets
gps = pd.read_csv(gps_file)
stores = pd.read_csv(store_file)

# Convert timestamps
gps["Timestamp"] = pd.to_datetime(gps["Timestamp"], errors="coerce")

# Remove invalid timestamps
gps = gps.dropna(subset=["Timestamp"]).copy()

# Extract date and hour
gps["Date"] = gps["Timestamp"].dt.date
gps["Hour"] = gps["Timestamp"].dt.hour

# Overall hourly footfall
hourly_footfall = (
    gps.groupby("Hour")
    .size()
    .reset_index(name="GPSPingCount")
    .sort_values("Hour")
)

hourly_footfall.to_csv(
    os.path.join(processed_folder, "hourly_footfall.csv"),
    index=False
)

# Store-wise hourly footfall using existing catchment analysis
catchment_file = "data/processed/gps_store_catchment_analysis.csv"
catchment = pd.read_csv(catchment_file)

# Reload GPS and assign each ping to stores within its catchment
from math import radians, sin, cos, asin, sqrt

def haversine(lat1, lon1, lat2, lon2):
    earth_radius = 6371000

    lat1, lon1, lat2, lon2 = map(
        radians, [lat1, lon1, lat2, lon2]
    )

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        sin(dlat / 2) ** 2
        + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    )

    return 2 * earth_radius * asin(sqrt(a))

store_hourly_records = []

for _, store in stores.iterrows():
    for _, ping in gps.iterrows():

        distance = haversine(
            store["Latitude"],
            store["Longitude"],
            ping["Latitude"],
            ping["Longitude"]
        )

        if distance <= store["CatchmentRadiusMeters"]:
            store_hourly_records.append({
                "StoreID": store["StoreID"],
                "StoreName": store["StoreName"],
                "Hour": ping["Hour"]
            })

store_hourly = pd.DataFrame(store_hourly_records)

store_hourly_footfall = (
    store_hourly.groupby(
        ["StoreID", "StoreName", "Hour"]
    )
    .size()
    .reset_index(name="GPSPingCount")
    .sort_values(["StoreID", "Hour"])
)

store_hourly_footfall.to_csv(
    os.path.join(processed_folder, "store_hourly_footfall.csv"),
    index=False
)

# Identify peak and lowest footfall hours
peak_row = hourly_footfall.loc[
    hourly_footfall["GPSPingCount"].idxmax()
]

low_row = hourly_footfall.loc[
    hourly_footfall["GPSPingCount"].idxmin()
]

# Generate report
report = f"""
GEOPULSE DAY 6: HOURLY FOOTFALL ANALYSIS
========================================

Total GPS Records: {len(gps)}
Total Retail Stores: {len(stores)}
Hours Analysed: {len(hourly_footfall)}

PEAK FOOTFALL HOUR
------------------
Hour: {int(peak_row['Hour']):02d}:00
GPS Pings: {int(peak_row['GPSPingCount'])}

LOWEST FOOTFALL HOUR
--------------------
Hour: {int(low_row['Hour']):02d}:00
GPS Pings: {int(low_row['GPSPingCount'])}

HOURLY FOOTFALL SUMMARY
-----------------------
{hourly_footfall.to_string(index=False)}

DATA LIMITATIONS
----------------
This analysis uses synthetic GPS records and approximate
simulated store coordinates in Delhi.

GPS ping counts represent simulated location activity,
not verified customer visits, transactions, or sales.

A single GPS ping can be counted for multiple stores
when their catchment areas overlap.
"""

with open(
    os.path.join(reports_folder, "hourly_footfall_report.txt"),
    "w",
    encoding="utf-8"
) as file:
    file.write(report)

print("GEOPULSE DAY 6 ANALYSIS COMPLETED")
print("=================================")
print(f"GPS Records: {len(gps)}")
print(f"Retail Stores: {len(stores)}")
print(f"Peak Footfall Hour: {int(peak_row['Hour']):02d}:00")
print(f"Peak GPS Pings: {int(peak_row['GPSPingCount'])}")
print(f"Lowest Footfall Hour: {int(low_row['Hour']):02d}:00")
print(f"Lowest GPS Pings: {int(low_row['GPSPingCount'])}")

print("\nOUTPUT FILES CREATED:")
print("- hourly_footfall.csv")
print("- store_hourly_footfall.csv")
print("- hourly_footfall_report.txt")

