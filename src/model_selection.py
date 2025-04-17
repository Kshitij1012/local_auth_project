from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import pandas as pd
import os

# Load merged data and usable columns
df = pd.read_csv("data/merged/merged_data.csv")
usable_cols_df = pd.read_csv("data/explore/usable_columns.csv")
usable_cols = usable_cols_df.iloc[:, 0].dropna().tolist()

# Filter and clean data
cluster_data = df[usable_cols].copy()
cluster_data = cluster_data.dropna()
cluster_data = cluster_data[~(cluster_data == 0).any(axis=1)]

# Normalize data (excluding non-numeric ID columns)
numeric_cols = cluster_data.select_dtypes(include='number').columns
scaler = StandardScaler()
cluster_scaled = pd.DataFrame(scaler.fit_transform(cluster_data[numeric_cols]), columns=numeric_cols)

# KMeans clustering
kmeans = KMeans(n_clusters=5, random_state=42)
cluster_data['Cluster'] = kmeans.fit_predict(cluster_scaled)

# Quartile assignment
cluster_data['Spend_Quartile'] = pd.qcut(df['Total_spend'], 4, labels=False) + 1
cluster_data['Population_Quartile'] = pd.qcut(df['Total_population'], 4, labels=False) + 1
cluster_data['IMD_Quartile'] = pd.qcut(df['IMD - Average score'], 4, labels=False) + 1

# Save results
os.makedirs("data/clustered", exist_ok=True)
cluster_data.to_csv("data/clustered/clustered_data.csv", index=False)
print("Stage 4 complete: Clustering and quartile data saved.")