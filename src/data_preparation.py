import pandas as pd
import os

# === Load Excel sheet === #
file_path = "data/Dataset.xlsx"
df_raw = pd.read_excel(file_path, sheet_name="HousingServicesSpend", header=None)

# === Step 1: Extract header rows === #
main_headers = df_raw.iloc[0].astype(str).str.replace(r"[\r\n]+", " ", regex=True).str.strip()
sub_headers = df_raw.iloc[1].astype(str).str.replace(r"[\r\n]+", " ", regex=True).str.strip()

# === Step 2: Construct final headers using R-like logic === #
final_headers = []
current_main = ""

for i in range(len(main_headers)):
    main = main_headers[i]
    sub = sub_headers[i]

    # If there's a valid main category in row 0, update it
    if main and main.lower() != "nan" and main.strip() != "":
        current_main = main.strip()

    # Clean subcategory
    sub = "" if sub.lower() == "nan" else sub.strip()

    if current_main == "" and sub != "":
        # Case: first few columns — no main, only sub
        combined = f"_{sub}"
    elif current_main != "" and sub != "":
        combined = f"{current_main}_{sub}"
    elif current_main != "":
        combined = current_main
    else:
        combined = f"Unnamed_{i}"

    final_headers.append(combined)

# === Step 3: Apply final headers and drop first two rows === #
df_spend = df_raw.iloc[2:].copy()
df_spend.columns = final_headers

# === Step 4: Rename authority code column === #
if "_Local_authority_code" in df_spend.columns:
    df_spend.rename(columns={"_Local_authority_code": "Local_authority_code"}, inplace=True)

# === Step 5: Load other sheets === #
df_claimants = pd.read_excel(file_path, sheet_name="HousingBenefitClaimants")
df_population = pd.read_excel(file_path, sheet_name="PopulationEstimates")
df_imd = pd.read_excel(file_path, sheet_name="IndexOfMultipleDeprivation")

# === Step 6: Harmonize Authority Names === #
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

def harmonize(df, col_name):
    df[col_name] = df[col_name].replace(authority_mapping)
    return df

# Apply harmonization
df_spend = harmonize(df_spend, df_spend.columns[2])  # Local authority name col
df_claimants = harmonize(df_claimants, "Local authority name")
df_population = harmonize(df_population, "local authority: district / unitary (as of April 2021)")
df_imd = harmonize(df_imd, "Local Authority District name (2019)")


os.makedirs("data/cleaned", exist_ok=True)
df_spend.to_csv("data/cleaned/housing_spend_clean.csv", index=False)
df_claimants.to_csv("data/cleaned/housing_claimants_clean.csv", index=False)
df_population.to_csv("data/cleaned/population_estimates_clean.csv", index=False)
df_imd.to_csv("data/cleaned/imd_data_clean.csv", index=False)

print("Headers cleaned and files saved successfully.")
