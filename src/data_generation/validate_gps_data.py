
import pandas as pd
from pathlib import Path

# Load GPS dataset
project_root = Path(__file__).resolve().parents[2]
file_path = project_root / "data" / "raw" / "delhi_gps_pings.csv"

df = pd.read_csv(file_path)

print("GEOPULSE GPS DATA VALIDATION")
print("=" * 40)

# 1. Check required columns
required_columns = ["DeviceID", "Latitude", "Longitude", "Timestamp", "City"]
missing_columns = [col for col in required_columns if col not in df.columns]

# 2. Missing values
missing_values = df.isnull().sum().sum()

# 3. Duplicate records
duplicate_records = df.duplicated().sum()

# 4. Coordinate validation for Delhi
invalid_latitude = (~df["Latitude"].between(28, 29)).sum()
invalid_longitude = (~df["Longitude"].between(76, 78)).sum()

# 5. Timestamp validation
timestamps = pd.to_datetime(df["Timestamp"], errors="coerce")
invalid_timestamps = timestamps.isnull().sum()

# 6. Unique devices
unique_devices = df["DeviceID"].nunique()

# Display results
print("Total GPS records:", len(df))
print("Unique devices:", unique_devices)
print("Missing values:", missing_values)
print("Duplicate records:", duplicate_records)
print("Invalid latitude:", invalid_latitude)
print("Invalid longitude:", invalid_longitude)
print("Invalid timestamps:", invalid_timestamps)
print("Missing required columns:", missing_columns)

# Save validation report
report_path = project_root / "reports" / "gps_validation_report.txt"
report_path.parent.mkdir(parents=True, exist_ok=True)

with open(report_path, "w") as report:
    report.write("GEOPULSE GPS VALIDATION REPORT\n")
    report.write("=" * 40 + "\n")
    report.write(f"Total records: {len(df)}\n")
    report.write(f"Unique devices: {unique_devices}\n")
    report.write(f"Missing values: {missing_values}\n")
    report.write(f"Duplicate records: {duplicate_records}\n")
    report.write(f"Invalid latitude: {invalid_latitude}\n")
    report.write(f"Invalid longitude: {invalid_longitude}\n")
    report.write(f"Invalid timestamps: {invalid_timestamps}\n")
    report.write(f"Missing columns: {missing_columns}\n")

print("\nValidation report saved:", report_path)
print("\nValidation completed!")
