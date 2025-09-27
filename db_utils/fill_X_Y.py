import pandas as pd

# Load CSV
df = pd.read_csv("pakistan.csv")

# Show how many missing before
print("🔍 Missing before fill:")
print(df[["X", "Y"]].isna().sum())

# Forward-fill missing X and Y from previous row
df[["X", "Y"]] = df[["X", "Y"]].fillna(method="ffill")

# Show how many missing after
print("\n✅ Missing after fill:")
print(df[["X", "Y"]].isna().sum())

# Save to new CSV
df.to_csv("pakistan_filled.csv", index=False)
print("\n💾 Saved cleaned file as pakistan_filled.csv")
