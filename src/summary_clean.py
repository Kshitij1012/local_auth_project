import pandas as pd

# File paths
paths = {
    "Housing Spend": "data/cleaned/housing_spend_clean.csv",
    "Housing Claimants": "data/cleaned/housing_claimants_clean.csv",
    "Population Estimates": "data/cleaned/population_estimates_clean.csv",
    "IMD Data": "data/cleaned/imd_data_clean.csv"
}

def summarize(name, path):
    print(f"\n{'='*60}")
    print(f"📘 Summary: {name}")
    print(f"{'='*60}")
    
    df = pd.read_csv(path, encoding='utf-8')

    print(f"Shape: {df.shape}")
    if len(df.columns) > 8:
        print(f"Columns: {list(df.columns[:8])} ... [+{len(df.columns)-8} more]")
    else:
        print(f"Columns: {list(df.columns)}")

    print("\nSample Rows:")
    print(df.head(3))

    numeric_cols = df.select_dtypes(include='number')
    if not numeric_cols.empty:
        print("\nNumeric Summary:")
        print(numeric_cols.describe().T[["mean", "std", "min", "max"]].round(2))
    else:
        print("No numeric columns to summarize.")

# Loop through all datasets with error handling
for name, path in paths.items():
    try:
        summarize(name, path)
    except FileNotFoundError:
        print(f"❌ File not found: {path}")
    except Exception as e:
        print(f"❌ Error while summarizing {name}: {e}")


import pandas as pd

df = pd.read_csv("data/merged/merged_data.csv")
print("Actual Columns in File:\n", df.columns.tolist())