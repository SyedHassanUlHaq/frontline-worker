import pandas as pd

# Load CSV
df = pd.read_csv("pakistan.csv")

# Get unique amenities (drop NaN if present)
unique_amenities = df["amenity"].dropna().unique()

# Sort for readability
unique_amenities = sorted(unique_amenities)

# Print them
print("🩺 Unique amenities in the dataset:")
for amenity in unique_amenities:
    print("-", amenity)

print(f"\n✅ Found {len(unique_amenities)} unique amenities.")
