import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

# === Load Data === #
df = pd.read_csv("data/merged/merged_data.csv")
df.rename(columns={
    'Total_x': 'Total_spend',
    'Total_y': 'Total_population',
    'IMD - Average score ': 'IMD - Average score',
    'IMD - Rank of average score ': 'IMD - Rank of average score'
}, inplace=True)

# === Columns for clustering === #
cluster_cols = [
    'Total_spend',
    'Housing strategy, advice and enabling_Total Expenditure  (C3 = C1 + C2)',
    'Total Homelessness_Total Expenditure  (C3 = C1 + C2)88',
    'Housing benefits administration_Total Expenditure  (C3 = C1 + C2)116',
    'TOTAL HOUSING SERVICES (GFRA only)_Total Expenditure  (C3 = C1 + C2)144',
    'Housing strategy, advice and enabling_Net Current Expenditure  (C7 = C3 - C6)',
    'Total Homelessness_Net Current Expenditure  (C7 = C3 - C6)92',
    'Total_population',
    'IMD - Average score',
    'IMD - Rank of average score',
    'Under 25', '25 to 34', '35 to 44', '45 to 49', '50 to 54',
    '55 to 59', '60 to 64', '65 to 69', '70 plus'
]

name_col = 'Local authority name'
id_col = 'Local_authority_code'

# === Select required columns === #
cluster_data = df[[name_col, id_col] + cluster_cols].copy()

# === Convert to numeric (cleaning '...' or errors) === #
for col in cluster_cols:
    cluster_data[col] = pd.to_numeric(cluster_data[col], errors='coerce')

# === Drop rows with any missing or zero values === #
cluster_data = cluster_data.dropna()
cluster_data = cluster_data[(cluster_data[cluster_cols] != 0).all(axis=1)]

# === Standardize === #
scaler = StandardScaler()
cluster_scaled = scaler.fit_transform(cluster_data[cluster_cols])

# === Clustering === #
kmeans = KMeans(n_clusters=5, n_init=25, random_state=123)
cluster_data['Cluster'] = kmeans.fit_predict(cluster_scaled) + 1

# === Quartile Analysis === #
cluster_data['Spend_Quartile'] = pd.qcut(cluster_data['Total_spend'], 4, labels=[1, 2, 3, 4])
cluster_data['Population_Quartile'] = pd.qcut(cluster_data['Total_population'], 4, labels=[1, 2, 3, 4])
cluster_data['IMD_Quartile'] = pd.qcut(cluster_data['IMD - Average score'], 4, labels=[1, 2, 3, 4])

# === Save clustered data === #
os.makedirs("data/model", exist_ok=True)
cluster_data.to_csv("data/model/clustered_data.csv", index=False)

# === Final Selection === #
total_select = 10
cluster_counts = cluster_data['Cluster'].value_counts(normalize=True).reset_index()
cluster_counts.columns = ['Cluster', 'Proportion']
cluster_counts['To_Select'] = (cluster_counts['Proportion'] * total_select).round().astype(int)
cluster_counts['To_Select'] = cluster_counts['To_Select'].apply(lambda x: max(1, x))

selected = []
for _, row in cluster_counts.iterrows():
    c = row['Cluster']
    n = int(row['To_Select'])
    group = cluster_data[cluster_data['Cluster'] == c]
    unique_quartiles = group.drop_duplicates(subset=['Spend_Quartile', 'Population_Quartile', 'IMD_Quartile'])
    selected.append(unique_quartiles.head(n))

selected_df = pd.concat(selected).head(total_select).copy()

# === Reasoning Columns === #
selected_df['reason_for_selection'] = np.select(
    [
        (selected_df['IMD_Quartile'] == 4) & (selected_df['Spend_Quartile'] == 4),
        (selected_df['IMD_Quartile'] == 4) & (selected_df['Spend_Quartile'] == 3),
        (selected_df['IMD_Quartile'] == 3) & (selected_df['Spend_Quartile'] == 4),
        (selected_df['IMD_Quartile'] == 3) & (selected_df['Spend_Quartile'] == 3),
        (selected_df['IMD_Quartile'] == 2) & (selected_df['Spend_Quartile'] == 3),
        (selected_df['IMD_Quartile'] == 1) & (selected_df['Spend_Quartile'] == 1)
    ],
    [
        "High deprivation & high spend",
        "High deprivation & moderate spend",
        "Moderate deprivation & high spend",
        "Moderate deprivation & moderate spend",
        "Low deprivation & moderate spend",
        "Low deprivation & low spend"
    ],
    default="Diverse mix including population and IMD"
)

selected_df['reason_for_cluster'] = selected_df['Cluster'].map({
    1: "Lowest spend & deprivation",
    2: "High population, diverse spend",
    3: "Moderate spend & population",
    4: "High deprivation, varying spend",
    5: "High spend & high population"
})

selected_df = selected_df[[name_col, id_col, 'Cluster', 'Spend_Quartile', 'Population_Quartile', 'IMD_Quartile', 'reason_for_selection', 'reason_for_cluster']]
selected_df.to_csv("data/model/final_selection.csv", index=False)

print("Model selection, clustering, and authority shortlisting done.")
