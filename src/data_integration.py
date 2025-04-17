import pandas as pd
import os

# Load cleaned CSVs
df_spend = pd.read_csv("data/cleaned/housing_spend_clean.csv")
df_claimants = pd.read_csv("data/cleaned/housing_claimants_clean.csv")
df_population = pd.read_csv("data/cleaned/population_estimates_clean.csv")
df_imd = pd.read_csv("data/cleaned/imd_data_clean.csv")

# Merge step-by-step on Local_authority_code
merged = df_spend.merge(df_claimants, on="Local_authority_code", how="left")
merged = merged.merge(df_population, on="Local_authority_code", how="left")
merged = merged.merge(df_imd, on="Local_authority_code", how="left")

# Save final merged data
os.makedirs("data/merged", exist_ok=True)
merged.to_csv("data/merged/merged_data.csv", index=False)

print("✅ Stage 2 complete: Merged data saved.")