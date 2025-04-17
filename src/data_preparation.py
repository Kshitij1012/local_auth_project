import pandas as pd
import os

# File path
file_path = "data/Dataset.xlsx"

# Load sheets
df_spend = pd.read_excel(file_path, sheet_name="HousingServicesSpend", header=None)
df_claimants = pd.read_excel(file_path, sheet_name="HousingBenefitClaimants")
df_population = pd.read_excel(file_path, sheet_name="PopulationEstimates")
df_imd = pd.read_excel(file_path, sheet_name="IndexOfMultipleDeprivation")

# --- Clean Multi-Level Header for Housing Spend ---
sub_headers = df_spend.iloc[0].astype(str).str.replace('\r|\n', '', regex=True)
main_headers = df_spend.columns.astype(str)
new_headers = []
current_main = ""
for main, sub in zip(main_headers, sub_headers):
    if not main.startswith("..."):
        current_main = main
    new_headers.append(f"{current_main}_{sub}" if sub else current_main)

df_spend = df_spend.drop(index=0)
df_spend.columns = new_headers

# Rename authority code column
df_spend = df_spend.rename(columns={df_spend.columns[0]: "Local_authority_code"})

# --- Harmonize Authority Names ---
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

# Replace function
def harmonize(df, col):
    df[col] = df[col].replace(authority_mapping)
    return df

# Harmonize across datasets
df_spend = harmonize(df_spend, df_spend.columns[1])
df_claimants = harmonize(df_claimants, "Local authority name")
df_population = harmonize(df_population, "local authority: district / unitary (as of April 2021)")
df_imd = harmonize(df_imd, "Local Authority District name (2019)")

# Save cleaned data
os.makedirs("data/cleaned", exist_ok=True)
df_spend.to_csv("data/cleaned/housing_spend_clean.csv", index=False)
df_claimants.to_csv("data/cleaned/housing_claimants_clean.csv", index=False)
df_population.to_csv("data/cleaned/population_estimates_clean.csv", index=False)
df_imd.to_csv("data/cleaned/imd_data_clean.csv", index=False)

print(" Stage 1 complete: Cleaned datasets saved.")