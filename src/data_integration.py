import pandas as pd
import os

# === Load Cleaned CSV Files === #
spend_path = "data/cleaned/housing_spend_clean.csv"
claimants_path = "data/cleaned/housing_claimants_clean.csv"
population_path = "data/cleaned/population_estimates_clean.csv"
imd_path = "data/cleaned/imd_data_clean.csv"

housing_spend = pd.read_csv(spend_path)
housing_claimants = pd.read_csv(claimants_path)
population_estimates = pd.read_csv(population_path)
imd_data = pd.read_csv(imd_path)

# === Check Row Counts & Unique Authority Codes === #
print("Housing Spend -", housing_spend.shape, "Unique codes:", housing_spend['Local_authority_code'].nunique())
print("Housing Claimants -", housing_claimants.shape, "Unique codes:", housing_claimants['Local_authority_code'].nunique())
print("Population Estimates -", population_estimates.shape, "Unique codes:", population_estimates['Local_authority_code'].nunique())
print("IMD Data -", imd_data.shape, "Unique codes:", imd_data['Local_authority_code'].nunique())

# === Compare Mismatched Authority Codes === #
spend_codes = set(housing_spend['Local_authority_code'])
claimant_codes = set(housing_claimants['Local_authority_code'])
population_codes = set(population_estimates['Local_authority_code'])
imd_codes = set(imd_data['Local_authority_code'])

print("Spend not in Claimants:", spend_codes - claimant_codes)
print("Claimants not in Spend:", claimant_codes - spend_codes)
print("Spend not in Population:", spend_codes - population_codes)
print("Population not in Spend:", population_codes - spend_codes)
print("Spend not in IMD:", spend_codes - imd_codes)
print("IMD not in Spend:", imd_codes - spend_codes)

# === Harmonize Names Again (Safety) === #
authority_mapping = {
    "Aylesbury Vale": "Buckinghamshire",
    "South Bucks": "Buckinghamshire",
    "Chiltern": "Buckinghamshire",
    "Wycombe": "Buckinghamshire",
    "Corby": "North Northamptonshire",
    "East Northamptonshire": "North Northamptonshire",
    "Kettering": "North Northamptonshire",
    "Wellingborough": "North Northamptonshire",
    "Daventry": "West Northamptonshire",
    "Northampton": "West Northamptonshire",
    "South Northamptonshire": "West Northamptonshire"
}

def harmonize(df, col):
    df[col] = df[col].replace(authority_mapping)
    return df

housing_spend = harmonize(housing_spend, housing_spend.columns[2])
housing_claimants = harmonize(housing_claimants, "Local authority name")
population_estimates = harmonize(population_estimates, "local authority: district / unitary (as of April 2021)")
imd_data = harmonize(imd_data, "Local Authority District name (2019)")

# === Aggregate Numeric Columns === #
def aggregate(df, key):
    return df.groupby(key).agg(lambda x: x.sum(numeric_only=True) if x.dtype != 'O' else x.iloc[0]).reset_index()

housing_spend = aggregate(housing_spend, 'Local_authority_code')
housing_claimants = aggregate(housing_claimants, 'Local_authority_code')
population_estimates = aggregate(population_estimates, 'Local_authority_code')
imd_data = aggregate(imd_data, 'Local_authority_code')

# === Merge Datasets === #
merged = housing_spend.copy()
merged = pd.merge(merged, housing_claimants, on='Local_authority_code', how='left')
merged = pd.merge(merged, population_estimates, on='Local_authority_code', how='left')
merged = pd.merge(merged, imd_data, on='Local_authority_code', how='left')

# === Rename & Drop Unwanted Columns === #
if 'local authority: district / unitary (as of April 2021)' in merged.columns:
    merged.drop(columns=['local authority: district / unitary (as of April 2021)'], inplace=True)
if 'Local Authority District name (2019)' in merged.columns:
    merged.drop(columns=['Local Authority District name (2019)'], inplace=True)

# === Remove Problematic Row === #
merged = merged[merged['Local_authority_code'] != 'E06000053']

# === Convert Spend to Numeric === #
if 'Total_spend' in merged.columns:
    merged['Total_spend'] = pd.to_numeric(merged['Total_spend'], errors='coerce')

# === Save Merged Dataset === #
os.makedirs("data/merged", exist_ok=True)
merged.to_csv("data/merged/merged_data.csv", index=False)
print("Stage 2 complete: Data integrated and saved.")
