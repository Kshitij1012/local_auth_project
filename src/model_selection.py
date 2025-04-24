import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import mlflow
import mlflow.sklearn
import yaml

# === Load number of clusters from params.yaml === #
with open("params.yaml", "r") as f:
    params = yaml.safe_load(f)
    print("Params loaded:", params)
n_clusters = params["model_selection"]["n_clusters"]

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

# === Preprocess === #
cluster_data = df[[name_col, id_col] + cluster_cols].copy()
for col in cluster_cols:
    cluster_data[col] = pd.to_numeric(cluster_data[col], errors='coerce')
cluster_data = cluster_data.dropna()
cluster_data = cluster_data[(cluster_data[cluster_cols] != 0).all(axis=1)]

# === Standardise === #
scaler = StandardScaler()
cluster_scaled = scaler.fit_transform(cluster_data[cluster_cols])

# === MLflow Tracking  === #
with mlflow.start_run(run_name="kmeans_clustering"):

    kmeans = KMeans(n_clusters=n_clusters, n_init=25, random_state=123)
    cluster_data['Cluster'] = kmeans.fit_predict(cluster_scaled) + 1

    mlflow.log_param("n_clusters", kmeans.n_clusters)
    mlflow.log_metric("inertia", kmeans.inertia_)

    mlflow.sklearn.log_model(kmeans, artifact_path="kmeans_model")

    os.makedirs("data/model", exist_ok=True)
    cluster_data['Spend_Quartile'] = pd.qcut(cluster_data['Total_spend'], 4, labels=[1, 2, 3, 4])
    cluster_data['Population_Quartile'] = pd.qcut(cluster_data['Total_population'], 4, labels=[1, 2, 3, 4])
    cluster_data['IMD_Quartile'] = pd.qcut(cluster_data['IMD - Average score'], 4, labels=[1, 2, 3, 4])
    cluster_data.to_csv("data/model/clustered_data.csv", index=False)
    mlflow.log_artifact("data/model/clustered_data.csv")
    mlflow.log_metric("num_records_used", len(cluster_data))

    os.makedirs("plots", exist_ok=True)
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=cluster_data, x="Total_population", y="Total_spend", hue="Cluster", palette="Set2", s=100)
    plt.title("Cluster-wise Spend vs Population")
    plt.xlabel("Total Population")
    plt.ylabel("Total Spend")
    plt.tight_layout()
    scatter_path = "plots/cluster_scatter.png"
    plt.savefig(scatter_path)
    plt.close()
    mlflow.log_artifact(scatter_path)

    # === Final Selection Logic === #
    total_select = 10
    selected = []

    for cluster_id in sorted(cluster_data['Cluster'].unique()):
        group = cluster_data[cluster_data['Cluster'] == cluster_id]
        unique_diverse = group.drop_duplicates(subset=['Spend_Quartile', 'Population_Quartile', 'IMD_Quartile'])
        selected.append(unique_diverse.head(1))

<<<<<<< HEAD
selected_df = selected_df[[name_col, id_col, 'Cluster', 'Spend_Quartile', 'Population_Quartile', 'IMD_Quartile', 'reason_for_selection', 'reason_for_cluster']]
selected_df.to_csv("data/model/final_selection.csv", index=False)

print("Model selection, clustering, and authority shortlisting done.")
=======
    remaining = total_select - len(selected)
    if remaining > 0:
        remaining_pool = cluster_data[~cluster_data.index.isin(pd.concat(selected).index)]
        additional = remaining_pool.drop_duplicates(subset=['Spend_Quartile', 'Population_Quartile', 'IMD_Quartile'])
        selected.append(additional.head(remaining))

    selected_df = pd.concat(selected).head(total_select).copy()

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
    mlflow.log_artifact("data/model/final_selection.csv")

print("Model selection, clustering, and authority shortlisting done.")
>>>>>>> d54167e0 (Commit before pulling from remote)
