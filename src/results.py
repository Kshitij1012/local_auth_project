import pandas as pd
import numpy as np
import os

# Load data
df = pd.read_csv("data/clustered/clustered_data.csv")

# Count and calculate %
cluster_counts = df['Cluster'].value_counts(normalize=True).reset_index()
cluster_counts.columns = ['Cluster', 'Percentage']
cluster_counts['Cluster'] = cluster_counts['Cluster'].astype(int)
cluster_counts['authorities_to_select'] = np.maximum((cluster_counts['Percentage'] * 10).round().astype(int), 1)

# Select diverse authorities
selected = pd.DataFrame()
for _, row in cluster_counts.iterrows():
    subset = df[df['Cluster'] == row['Cluster']]
    diverse = subset.drop_duplicates(subset=['Spend_Quartile', 'Population_Quartile', 'IMD_Quartile'])
    selected = pd.concat([selected, diverse.head(row['authorities_to_select'])])

# Add selection reasoning
conditions = [
    (selected['IMD_Quartile'] == 4) & (selected['Spend_Quartile'] == 4),
    (selected['IMD_Quartile'] == 4) & (selected['Spend_Quartile'] == 3),
    (selected['IMD_Quartile'] == 3) & (selected['Spend_Quartile'] == 4),
    (selected['IMD_Quartile'] == 3) & (selected['Spend_Quartile'] == 3),
    (selected['IMD_Quartile'] == 2) & (selected['Spend_Quartile'] == 3),
    (selected['IMD_Quartile'] == 1) & (selected['Spend_Quartile'] == 1),
]

reasons = [
    "High deprivation & high spend",
    "High deprivation & moderate spend",
    "Moderate deprivation & high spend",
    "Balanced resources & need",
    "Efficient use in less deprived areas",
    "Low deprivation & low spend",
]

selected['reason_for_selection'] = np.select(conditions, reasons, default="Diverse profile")

# Add cluster reasoning
cluster_reason_map = {
    1: "Low spend and deprivation",
    2: "High population & diverse spend",
    3: "Balanced resource areas",
    4: "High deprivation, varied spend",
    5: "High spend & population"
}

selected['reason_for_cluster'] = selected['Cluster'].map(cluster_reason_map)

# Final output
final_report = selected[[
    'Local_authority_name', 'Spend_Quartile', 'Population_Quartile', 'IMD_Quartile',
    'Cluster', 'reason_for_selection', 'reason_for_cluster']]

os.makedirs("data/final", exist_ok=True)
final_report.to_csv("data/final/final_report.csv", index=False)
print("Stage 5 complete: Final report saved.")
