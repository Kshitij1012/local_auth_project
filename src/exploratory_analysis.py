import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Load the merged dataset
merged_path = "data/merged/merged_data.csv"
df = pd.read_csv(merged_path)

# Inspect missing & zero values
zero_counts = (df == 0).sum()
na_counts = df.isna().sum()

quality_summary = pd.DataFrame({
    'Zero Values': zero_counts,
    'Missing Values': na_counts
})
print(quality_summary)

# Set a threshold and identify usable columns
threshold = 30
usable_columns = [col for col in df.columns if zero_counts[col] <= threshold and na_counts[col] <= threshold]

# Save summary and filtered columns
os.makedirs("data/explore", exist_ok=True)
quality_summary.to_csv("data/explore/quality_summary.csv")
pd.Series(usable_columns).to_csv("data/explore/usable_columns.csv", index=False)
print("✅ Stage 3 complete: Exploratory summary and usable columns saved.")