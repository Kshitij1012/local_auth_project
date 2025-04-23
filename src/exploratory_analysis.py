import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# === Load Integrated Data === #
merged_path = "data/merged/merged_data.csv"
df = pd.read_csv(merged_path)

df.rename(columns={
    'Total_x': 'Total_spend',
    'Total_y': 'Total_population',
    'IMD - Average score ': 'IMD - Average score'  # Remove trailing space
}, inplace=True)

# === Check Shape & Unique Codes === #
print("Merged Data Shape:", df.shape)
print("Unique Local Authority Codes:", df['Local_authority_code'].nunique())

# === Summary Stats === #
summary = df[['Total_spend', 'Total_population', 'IMD - Average score']].describe()
print("\nSummary Statistics:\n", summary)

# === Data Quality Check: Missing & Zero === #
missing = df.isna().sum().to_frame(name="Missing")
zero = (df == 0).sum().to_frame(name="Zero")
quality_check = missing.join(zero)
print("\nData Quality Summary:\n", quality_check)

os.makedirs("data/explore", exist_ok=True)
quality_check.to_csv("data/explore/quality_summary.csv", index=True)

# === Determine Usable Columns for Clustering === #
threshold = 30  # Allow max 30 missing or zero
usable_cols = [col for col in df.columns 
               if df[col].isna().sum() <= threshold and (df[col] == 0).sum() <= threshold]
print("\nUsable Columns (<=30 NA & Zeros):", usable_cols)
pd.DataFrame({'usable_columns': usable_cols}).to_csv("data/explore/usable_columns.csv", index=False)

# === Plots Directory === #
os.makedirs("plots", exist_ok=True)

# === Histogram: Total Spend === #
plt.figure(figsize=(8, 5))
sns.histplot(df['Total_spend'].dropna(), bins=30, kde=False, color='skyblue')
plt.title("Distribution of Total Spend")
plt.xlabel("Total Spend")
plt.ylabel("Frequency")
plt.tight_layout()
plt.savefig("plots/total_spend_distribution.png")
plt.close()


# === Scatter Plot: Total Population vs Spend (colored by IMD quartile) === #
if 'IMD - Average score' in df.columns:
    df['IMD_Quartile'] = pd.qcut(df['IMD - Average score'], 4, labels=['Low', 'Mid-Low', 'Mid-High', 'High'])
    
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df,
                    x='Total_population',
                    y='Total_spend',
                    hue='IMD_Quartile',
                    palette='coolwarm',
                    s=80)
    plt.title("Population vs Spend by IMD Quartile")
    plt.xlabel("Total Population")
    plt.ylabel("Total Spend")
    plt.legend(title="IMD Quartile")
    plt.tight_layout()
    plt.savefig("plots/population_vs_spend_by_imd.png")
    plt.close()

    
# === Histogram: Total Population === #
plt.figure(figsize=(8, 5))
sns.histplot(df['Total_population'].dropna(), bins=30, kde=False, color='lightgreen')
plt.title("Distribution of Total Population")
plt.xlabel("Total Population")
plt.ylabel("Frequency")
plt.tight_layout()
plt.savefig("plots/total_population_distribution.png")
plt.close()

# === Histogram: IMD Average Score === #
plt.figure(figsize=(8, 5))
sns.histplot(df['IMD - Average score'].dropna(), bins=30, kde=False, color='orange')
plt.title("Distribution of IMD - Average Score")
plt.xlabel("IMD - Average Score")
plt.ylabel("Frequency")
plt.tight_layout()
plt.savefig("plots/imd_score_distribution.png")
plt.close()

# === Top 10 Housing Strategy Spend === #
if 'Housing strategy, advice and enabling_Total Expenditure (C3 = C1 + C2)' in df.columns:
    top10 = df.nlargest(10, 'Housing strategy, advice and enabling_Total Expenditure (C3 = C1 + C2)')
    plt.figure(figsize=(10, 6))
    sns.barplot(data=top10,
                x='Local_authority_code',
                y='Housing strategy, advice and enabling_Total Expenditure (C3 = C1 + C2)',
                palette="viridis")
    plt.title("Top 10 Authorities by Housing Strategy Expenditure")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("plots/top10_housing_strategy.png")
    plt.close()

# === Bar Chart: Under 25 Claimants === #
if 'Under 25' in df.columns:
    plt.figure(figsize=(12, 6))
    sns.barplot(data=df.sort_values(by='Under 25', ascending=False),
                x='Local_authority_code', y='Under 25')
    plt.title("Claimants Under 25 by Local Authority")
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig("plots/under25_claimants.png")
    plt.close()

print("Stage 3 complete: Exploratory analysis done and plots saved.")
