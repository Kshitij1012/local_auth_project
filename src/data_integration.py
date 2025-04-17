import pandas as pd
import os

# Load Excel file
file_path = "data/Dataset.xlsx"
housing_spend = pd.read_excel(file_path, sheet_name="HousingServicesSpend", header=None)
housing_claimants = pd.read_excel(file_path, sheet_name="HousingBenefitClaimants")
population_estimates = pd.read_excel(file_path, sheet_name="PopulationEstimates")
imd_data = pd.read_excel(file_path, sheet_name="IndexOfMultipleDeprivation")

# --- CLEAN HOUSING SPEND HEADERS --- #
# Extract the first row (subcategories)
first_row = housing_spend.iloc[0].astype(str).str.replace(r"[\r\n]+", "", regex=True)
main_categories = housing_spend.iloc[1]

# Build new column names
new_column_names = []
current_main = ""
for i, value in enumerate(main_categories):
    if not str(value).startswith("..."):
        current_main = value
    sub = first_row[i]
    if sub != "nan":
        new_column_names.append(f"{current_main}_{sub}")
    else:
        new_column_names.append(str(current_main))

# Apply new column names and drop first two rows
housing_spend.columns = new_column_names
housing_spend = housing_spend.iloc[2:].copy()

# Rename identifier column
if "_Local_authority_code" in housing_spend.columns:
    housing_spend = housing_spend.rename(columns={"_Local_authority_code": "Local_authority_code"})

# Save cleaned datasets
os.makedirs("data/cleaned", exist_ok=True)
housing_spend.to_csv("data/cleaned/housing_spend_clean.csv", index=False)
housing_claimants.to_csv("data/cleaned/housing_claimants_clean.csv", index=False)
population_estimates.to_csv("data/cleaned/population_estimates_clean.csv", index=False)
imd_data.to_csv("data/cleaned/imd_data_clean.csv", index=False)

print("Stage 1 complete: Cleaned datasets saved.")