import pandas as pd
import random

# Load your CSV file
df = pd.read_csv("pakistan_filled.csv")

# Collect all available (non-missing) opening_hours values
available_hours = df['opening_hours'].dropna().unique().tolist()

# Function to replace NaN with a random choice from available values
def fill_random_hours(val):
    if pd.isna(val):
        return random.choice(available_hours)
    return val

# Apply the function to the column
df['opening_hours'] = df['opening_hours'].apply(fill_random_hours)

# Save the updated CSV
df.to_csv("pakistan_filled_filled.csv", index=False)

print("✅ Missing opening_hours filled randomly and saved as your_file_filled.csv")
