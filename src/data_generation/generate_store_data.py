
import pandas as pd
from pathlib import Path

# Simulated retail stores in Delhi
stores = [
    ("STORE_001", "Connaught Coffee", 28.6315, 77.2167, "Coffee"),
    ("STORE_002", "Central Cafe", 28.6320, 77.2190, "Cafe"),
    ("STORE_003", "City Brew", 28.6139, 77.2090, "Coffee"),
    ("STORE_004", "South Point Cafe", 28.6150, 77.2120, "Cafe"),
    ("STORE_005", "Market Coffee", 28.5672, 77.2100, "Coffee"),
    ("STORE_006", "Green Cup", 28.5690, 77.2130, "Cafe"),
    ("STORE_007", "Metro Cafe", 28.6500, 77.2300, "Cafe"),
    ("STORE_008", "Urban Brew", 28.6520, 77.2330, "Coffee"),
    ("STORE_009", "Westside Coffee", 28.7041, 77.1025, "Coffee"),
    ("STORE_010", "Garden Cafe", 28.7020, 77.1050, "Cafe"),
    ("STORE_011", "Daily Beans", 28.6350, 77.2200, "Coffee"),
    ("STORE_012", "Coffee Corner", 28.6180, 77.2150, "Coffee"),
    ("STORE_013", "Morning Mug", 28.5720, 77.2080, "Cafe"),
    ("STORE_014", "Express Cafe", 28.6470, 77.2250, "Cafe"),
    ("STORE_015", "Bean House", 28.7000, 77.1100, "Coffee")
]

df = pd.DataFrame(
    stores,
    columns=[
        "StoreID",
        "StoreName",
        "Latitude",
        "Longitude",
        "StoreCategory"
    ]
)

df["CatchmentRadiusMeters"] = 500
df["City"] = "Delhi"

# Save dataset
project_root = Path(__file__).resolve().parents[2]
output_path = project_root / "data" / "raw" / "delhi_store_locations.csv"

output_path.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(output_path, index=False)

print("GEOPULSE STORE DATA GENERATED")
print("=" * 40)
print("Total stores:", len(df))
print("Unique store IDs:", df["StoreID"].nunique())
print("Store categories:", df["StoreCategory"].nunique())
print("Catchment radius: 500 metres")
print("Output file:", output_path)
print("\nFirst five records:")
print(df.head())
