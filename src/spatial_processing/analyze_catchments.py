
import pandas as pd
import math
import os

# Load datasets
gps = pd.read_csv("data/raw/delhi_gps_pings.csv")
stores = pd.read_csv("data/raw/delhi_store_locations.csv")


# Calculate distance using Haversine formula
def calculate_distance(lat1, lon1, lat2, lon2):
    earth_radius = 6371000

    lat1, lon1, lat2, lon2 = map(
        math.radians, [lat1, lon1, lat2, lon2]
    )

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2)
        * math.sin(dlon / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return earth_radius * c


# Create output folder
os.makedirs("data/processed", exist_ok=True)
os.makedirs("reports", exist_ok=True)


# 1. Calculate distances between store pairs
distance_results = []

for i in range(len(stores)):
    for j in range(i + 1, len(stores)):

        store1 = stores.iloc[i]
        store2 = stores.iloc[j]

        distance = calculate_distance(
            store1["Latitude"],
            store1["Longitude"],
            store2["Latitude"],
            store2["Longitude"]
        )

        radius1 = store1["CatchmentRadiusMeters"]
        radius2 = store2["CatchmentRadiusMeters"]

        overlap = distance <= (radius1 + radius2)

        distance_results.append({
            "Store1": store1["StoreName"],
            "Store2": store2["StoreName"],
            "DistanceMeters": round(distance, 2),
            "CatchmentOverlap": overlap
        })

distance_df = pd.DataFrame(distance_results)

distance_df.to_csv(
    "data/processed/store_pair_distances.csv",
    index=False
)


# 2. Calculate GPS pings inside each store catchment
catchment_results = []

for _, store in stores.iterrows():

    distances = gps.apply(
        lambda point: calculate_distance(
            store["Latitude"],
            store["Longitude"],
            point["Latitude"],
            point["Longitude"]
        ),
        axis=1
    )

    nearby_pings = distances <= store["CatchmentRadiusMeters"]

    catchment_results.append({
        "StoreID": store["StoreID"],
        "StoreName": store["StoreName"],
        "StoreCategory": store["StoreCategory"],
        "GPSPingsWithinCatchment": int(nearby_pings.sum()),
        "CatchmentRadiusMeters": store["CatchmentRadiusMeters"]
    })

catchment_df = pd.DataFrame(catchment_results)

catchment_df.to_csv(
    "data/processed/gps_store_catchment_analysis.csv",
    index=False
)


# 3. Generate summary report
overlap_count = int(distance_df["CatchmentOverlap"].sum())

report = f"""
GEOPULSE - DAY 4 CATCHMENT ANALYSIS
====================================

Total GPS Records: {len(gps)}
Total Retail Stores: {len(stores)}
Total Store Pairs Analysed: {len(distance_df)}
Store Pairs with Overlapping Catchments: {overlap_count}

STORE FOOTFALL SUMMARY
----------------------
{catchment_df.to_string(index=False)}

Note:
This analysis uses synthetic GPS data and approximate
store coordinates. Overlap means the two circular
catchment radii intersect or touch.
GPS pings are counted independently for each store,
so the same ping may be counted for multiple stores.
"""

with open("reports/store_catchment_report.txt", "w") as file:
    file.write(report)

print("GEOPULSE DAY 4 ANALYSIS COMPLETED")
print("=================================")
print("GPS Records:", len(gps))
print("Retail Stores:", len(stores))
print("Store Pairs Analysed:", len(distance_df))
print("Overlapping Store Pairs:", overlap_count)
print("\nCatchment Analysis:")
print(catchment_df.to_string(index=False))
print("\nOutput files created successfully!")

