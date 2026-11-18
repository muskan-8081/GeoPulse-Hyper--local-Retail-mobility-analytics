
import pandas as pd
import os

# Create output folders
os.makedirs("data/processed", exist_ok=True)
os.makedirs("reports", exist_ok=True)

# Load datasets
stores = pd.read_csv("data/raw/delhi_store_locations.csv")
hourly = pd.read_csv("data/processed/store_hourly_footfall.csv")

# Calculate store performance
performance = hourly.groupby(
    ["StoreID", "StoreName"]
).agg(
    TotalGPSPings=("GPSPingCount", "sum"),
    ActiveHours=("Hour", "nunique"),
    AverageHourlyPings=("GPSPingCount", "mean"),
    PeakHourlyPings=("GPSPingCount", "max")
).reset_index()

# Add store information
store_details = stores[
    ["StoreID", "StoreName", "StoreCategory", "Latitude", "Longitude"]
].drop_duplicates(subset=["StoreID"])

performance = performance.merge(
    store_details,
    on=["StoreID", "StoreName"],
    how="left"
)

# Rank stores
performance["PerformanceRank"] = (
    performance["TotalGPSPings"]
    .rank(method="dense", ascending=False)
    .astype(int)
)

# Classify performance
average_pings = performance["TotalGPSPings"].mean()

def classify_performance(value):
    if value >= average_pings * 1.2:
        return "High"
    elif value >= average_pings * 0.8:
        return "Medium"
    return "Low"

performance["PerformanceCategory"] = (
    performance["TotalGPSPings"].apply(classify_performance)
)

# Sort results
performance = performance.sort_values(
    "TotalGPSPings", ascending=False
)

# Save CSV
performance.to_csv(
    "data/processed/store_performance.csv",
    index=False
)

# Summary statistics
total_stores = len(performance)
total_pings = int(performance["TotalGPSPings"].sum())
average_store_pings = performance["TotalGPSPings"].mean()

top_store = performance.iloc[0]
lowest_store = performance.iloc[-1]

category_summary = (
    performance["PerformanceCategory"]
    .value_counts()
    .to_string()
)

# Generate report
report = f"""
DELHI RETAIL STORE PERFORMANCE REPORT
=====================================

Project: GeoPulse - Hyperlocal Retail Mobility Analytics

1. OVERALL SUMMARY
------------------
Total Stores: {total_stores}
Total GPS Pings: {total_pings}
Average GPS Pings per Store: {average_store_pings:.2f}

2. TOP PERFORMING STORE
----------------------
Store Name: {top_store['StoreName']}
Total GPS Pings: {top_store['TotalGPSPings']}
Rank: {top_store['PerformanceRank']}

3. LOWEST ACTIVITY STORE
------------------------
Store Name: {lowest_store['StoreName']}
Total GPS Pings: {lowest_store['TotalGPSPings']}

4. PERFORMANCE CATEGORY SUMMARY
-------------------------------
{category_summary}

5. STORE PERFORMANCE RANKING
----------------------------
{performance[
    ['PerformanceRank', 'StoreName', 'StoreCategory',
     'TotalGPSPings', 'ActiveHours',
     'AverageHourlyPings', 'PeakHourlyPings',
     'PerformanceCategory']
].to_string(index=False)}

6. METHODOLOGY AND LIMITATIONS
------------------------------
Performance is measured using simulated GPS pings
within store catchment areas.

High, Medium and Low categories are relative to the
average GPS activity across the simulated stores.

These values represent spatial activity, not actual
sales or verified customer visits. The dataset is
synthetic and store coordinates are approximate.

Average hourly pings are calculated across hours
where a store recorded at least one GPS ping.
"""

with open(
    "reports/store_performance_report.txt",
    "w",
    encoding="utf-8"
) as file:
    file.write(report)

# Display results
print("\nSTORE PERFORMANCE ANALYSIS COMPLETED")
print("-------------------------------------")
print(f"Total Stores: {total_stores}")
print(f"Total GPS Pings: {total_pings}")
print(f"Average Pings per Store: {average_store_pings:.2f}")
print(f"Top Store: {top_store['StoreName']}")
print(f"Lowest Activity Store: {lowest_store['StoreName']}")

print("\nSTORE PERFORMANCE RANKING")
print(
    performance[
        ["PerformanceRank", "StoreName",
         "TotalGPSPings", "PerformanceCategory"]
    ].to_string(index=False)
)

print("\nGenerated files:")
print("- data/processed/store_performance.csv")
print("- reports/store_performance_report.txt")
