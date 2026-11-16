
import pandas as pd
import math
import os

# Load datasets
gps = pd.read_csv("data/raw/delhi_gps_pings.csv")
stores = pd.read_csv("data/raw/delhi_store_locations.csv")

# Haversine distance calculation
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


# Create output folders
os.makedirs("data/processed", exist_ok=True)
os.makedirs("reports", exist_ok=True)

# Assign GPS pings to each store catchment
store_ping_sets = {}

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

    nearby_indices = set(
        gps.index[
            distances <= store["CatchmentRadiusMeters"]
        ]
    )

    store_ping_sets[store["StoreID"]] = nearby_indices


# Analyse store pairs
pair_results = []

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

        geometric_overlap = distance <= (radius1 + radius2)

        pings1 = store_ping_sets[store1["StoreID"]]
        pings2 = store_ping_sets[store2["StoreID"]]

        shared_pings = pings1.intersection(pings2)

        shared_count = len(shared_pings)

        percentage1 = (
            shared_count / len(pings1) * 100
            if len(pings1) > 0 else 0
        )

        percentage2 = (
            shared_count / len(pings2) * 100
            if len(pings2) > 0 else 0
        )

        average_shared_percentage = (
            (percentage1 + percentage2) / 2
        )

        if not geometric_overlap:
            risk = "No Geometric Overlap"
        elif average_shared_percentage >= 30:
            risk = "High"
        elif average_shared_percentage >= 10:
            risk = "Medium"
        else:
            risk = "Low"

        pair_results.append({
            "Store1": store1["StoreName"],
            "Store2": store2["StoreName"],
            "DistanceMeters": round(distance, 2),
            "GeometricOverlap": geometric_overlap,
            "SharedGPSPings": shared_count,
            "Store1SharedPercentage": round(percentage1, 2),
            "Store2SharedPercentage": round(percentage2, 2),
            "AverageSharedPercentage": round(
                average_shared_percentage, 2
            ),
            "CompetitionRisk": risk
        })


# Create pair analysis DataFrame
pair_df = pd.DataFrame(pair_results)

pair_df = pair_df.sort_values(
    by="AverageSharedPercentage",
    ascending=False
)

pair_df.to_csv(
    "data/processed/store_cannibalization_analysis.csv",
    index=False
)


# Store-level summary
summary_results = []

for _, store in stores.iterrows():

    store_id = store["StoreID"]

    own_pings = store_ping_sets[store_id]

    shared_total = 0

    for other_id, other_pings in store_ping_sets.items():
        if other_id != store_id:
            shared_total += len(own_pings.intersection(other_pings))

    summary_results.append({
        "StoreID": store_id,
        "StoreName": store["StoreName"],
        "StoreCategory": store["StoreCategory"],
        "GPSPingsWithinCatchment": len(own_pings),
        "SharedPingCountsAcrossOtherStores": shared_total
    })

summary_df = pd.DataFrame(summary_results)

summary_df.to_csv(
    "data/processed/store_cannibalization_summary.csv",
    index=False
)


# Generate report
overlap_pairs = pair_df[
    pair_df["GeometricOverlap"] == True
]

high_risk_pairs = pair_df[
    pair_df["CompetitionRisk"] == "High"
]

report = f"""
GEOPULSE - DAY 5 CANNIBALIZATION ANALYSIS
==========================================

Total GPS Records: {len(gps)}
Total Retail Stores: {len(stores)}
Total Store Pairs Analysed: {len(pair_df)}

Geometrically Overlapping Pairs: {len(overlap_pairs)}
High Spatial Competition Pairs: {len(high_risk_pairs)}

TOP 10 STORE PAIRS
-------------------
{pair_df.head(10).to_string(index=False)}

STORE LEVEL SUMMARY
--------------------
{summary_df.to_string(index=False)}

IMPORTANT NOTES
---------------
This analysis uses synthetic GPS data and approximate
store coordinates.

Shared GPS pings indicate spatial audience overlap.
They do not prove actual customer switching or
sales cannibalization.

Risk categories are analytical screening thresholds,
not validated commercial predictions.
"""

with open(
    "reports/cannibalization_report.txt",
    "w"
) as file:
    file.write(report)


# Display results
print("GEOPULSE DAY 5 ANALYSIS COMPLETED")
print("=================================")

print("GPS Records:", len(gps))
print("Retail Stores:", len(stores))
print("Store Pairs Analysed:", len(pair_df))
print("Overlapping Pairs:", len(overlap_pairs))
print("High Competition Pairs:", len(high_risk_pairs))

print("\nTOP 10 COMPETING STORE PAIRS:")
print(pair_df.head(10).to_string(index=False))

print("\nOUTPUT FILES CREATED SUCCESSFULLY!")

