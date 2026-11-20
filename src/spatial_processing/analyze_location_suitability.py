
import pandas as pd
import numpy as np
import os

# Load datasets
hotspots = pd.read_csv("data/processed/gps_hotspots.csv")
stores = pd.read_csv("data/raw/delhi_store_locations.csv")

# Calculate distance using Haversine formula
def calculate_distance(lat1, lon1, lat2, lon2):
    earth_radius = 6371000

    lat1, lon1, lat2, lon2 = map(
        np.radians, [lat1, lon1, lat2, lon2]
    )

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        np.sin(dlat / 2) ** 2
        + np.cos(lat1) * np.cos(lat2)
        * np.sin(dlon / 2) ** 2
    )

    return 2 * earth_radius * np.arcsin(np.sqrt(a))


# Compare each hotspot with existing stores
results = []

for _, hotspot in hotspots.iterrows():

    distances = calculate_distance(
        stores["Latitude"].values,
        stores["Longitude"].values,
        hotspot["CenterLatitude"],
        hotspot["CenterLongitude"]
    )

    nearest_index = np.argmin(distances)
    nearest_distance = distances[nearest_index]

    nearby_stores = int((distances <= 500).sum())

    results.append({
        "HotspotRank": hotspot["HotspotRank"],
        "Latitude": hotspot["CenterLatitude"],
        "Longitude": hotspot["CenterLongitude"],
        "GPSPingCount": hotspot["GPSPingCount"],
        "UniqueDevices": hotspot["UniqueDevices"],
        "ActivityLevel": hotspot["ActivityLevel"],
        "NearestStore": stores.iloc[nearest_index]["StoreName"],
        "NearestStoreDistanceMeters": round(nearest_distance, 2),
        "NearbyStoresWithin500m": nearby_stores
    })


# Create analysis DataFrame
analysis = pd.DataFrame(results)

# Suitability score
analysis["SuitabilityScore"] = (
    analysis["GPSPingCount"].rank(pct=True) * 60
    + (1 - analysis["NearbyStoresWithin500m"] / 15) * 40
)

# Classify candidate locations
analysis["SuitabilityLevel"] = np.where(
    analysis["SuitabilityScore"] >= 70, "High",
    np.where(
        analysis["SuitabilityScore"] >= 40, "Medium", "Low"
    )
)

# Rank locations
analysis = analysis.sort_values(
    "SuitabilityScore", ascending=False
).reset_index(drop=True)

analysis["SuitabilityRank"] = range(1, len(analysis) + 1)

# Save output
os.makedirs("data/processed", exist_ok=True)
os.makedirs("reports", exist_ok=True)

analysis.to_csv(
    "data/processed/location_suitability.csv",
    index=False
)

# Generate report
with open("reports/location_suitability_report.txt", "w") as file:

    file.write("RETAIL LOCATION SUITABILITY ANALYSIS\n")
    file.write("=" * 45 + "\n\n")

    file.write(f"Total hotspots analyzed: {len(analysis)}\n")
    file.write(
        f"High suitability locations: "
        f"{(analysis['SuitabilityLevel'] == 'High').sum()}\n"
    )
    file.write(
        f"Medium suitability locations: "
        f"{(analysis['SuitabilityLevel'] == 'Medium').sum()}\n"
    )
    file.write(
        f"Low suitability locations: "
        f"{(analysis['SuitabilityLevel'] == 'Low').sum()}\n\n"
    )

    file.write("TOP 10 RECOMMENDED LOCATIONS\n")
    file.write("-" * 45 + "\n")

    file.write(
        analysis.head(10).to_string(index=False)
    )

    file.write(
        "\n\nNote: This analysis uses synthetic GPS data "
        "and simulated store locations. Suitability scores "
        "are exploratory indicators, not verified market demand."
    )

print("\nLOCATION SUITABILITY ANALYSIS COMPLETED")
print("Total hotspots analyzed:", len(analysis))
print("\nTOP 10 RECOMMENDED LOCATIONS")
print(
    analysis[
        [
            "SuitabilityRank",
            "Latitude",
            "Longitude",
            "GPSPingCount",
            "NearbyStoresWithin500m",
            "SuitabilityScore",
            "SuitabilityLevel"
        ]
    ].head(10).to_string(index=False)
)
print("\nOutput files created successfully.")
