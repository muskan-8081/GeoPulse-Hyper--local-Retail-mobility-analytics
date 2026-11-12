
import numpy as np
import pandas as pd
from pathlib import Path

# Reproducibility
np.random.seed(42)

# Configuration
TOTAL_PINGS = 10_000
TOTAL_DEVICES = 500
CITY = "Delhi"
SIMULATION_DATE = "2026-11-10"

# Approximate coordinates of fictional retail activity zones in Delhi
# These are simulation anchors, not surveyed store locations.
activity_zones = [
    (28.6315, 77.2167),  # Central Delhi
    (28.6139, 77.2090),  # Central/South Delhi
    (28.5672, 77.2100),  # South Delhi
    (28.6500, 77.2300),  # East-central Delhi
    (28.7041, 77.1025),  # West/North-west Delhi
]

# Assign each GPS ping to an activity zone
zone_indices = np.random.choice(
    len(activity_zones),
    size=TOTAL_PINGS
)

latitudes = np.zeros(TOTAL_PINGS)
longitudes = np.zeros(TOTAL_PINGS)

for i, (zone_lat, zone_lon) in enumerate(activity_zones):
    mask = zone_indices == i
    count = mask.sum()

    # Simulate movement around each zone
    latitudes[mask] = zone_lat + np.random.normal(
        0, 0.003, count
    )
    longitudes[mask] = zone_lon + np.random.normal(
        0, 0.003, count
    )

# Generate anonymous device IDs
device_numbers = np.random.randint(
    1, TOTAL_DEVICES + 1, TOTAL_PINGS
)

device_ids = [
    f"DEVICE_{number:04d}"
    for number in device_numbers
]

# Simulate time-of-day activity:
# morning, afternoon, evening and night
time_periods = np.random.choice(
    ["morning", "afternoon", "evening", "night"],
    size=TOTAL_PINGS,
    p=[0.35, 0.20, 0.35, 0.10]
)

hours = np.zeros(TOTAL_PINGS, dtype=int)

for period, hour_range in {
    "morning": (7, 11),
    "afternoon": (11, 17),
    "evening": (17, 22),
    "night": (22, 24)
}.items():
    mask = time_periods == period
    hours[mask] = np.random.randint(
        hour_range[0], hour_range[1], mask.sum()
    )

minutes = np.random.randint(0, 60, TOTAL_PINGS)
seconds = np.random.randint(0, 60, TOTAL_PINGS)

timestamps = (
    pd.to_datetime(SIMULATION_DATE)
    + pd.to_timedelta(hours, unit="h")
    + pd.to_timedelta(minutes, unit="m")
    + pd.to_timedelta(seconds, unit="s")
)

# Create dataset
df = pd.DataFrame({
    "DeviceID": device_ids,
    "Latitude": latitudes.round(6),
    "Longitude": longitudes.round(6),
    "Timestamp": timestamps,
    "City": CITY
})

# Sort records chronologically
df = df.sort_values("Timestamp").reset_index(drop=True)

# Save CSV
output_path = (
    Path(__file__).resolve().parents[2]
    / "data" / "raw" / "delhi_gps_pings.csv"
)

output_path.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(output_path, index=False)

# Validation summary
print("GeoPulse GPS Dataset Generated Successfully!")
print("--------------------------------------------")
print("Total GPS records:", len(df))
print("Unique devices:", df["DeviceID"].nunique())
print("City:", CITY)
print("Missing values:", df.isnull().sum().sum())
print("Duplicate records:", df.duplicated().sum())
print("Output file:", output_path)
print("\nFirst five records:")
print(df.head())
