import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os


clustered_path = "data/model/clustered_data.csv"
final_selection_path = "data/model/final_selection.csv"

os.makedirs("data/results", exist_ok=True)
os.makedirs("plots", exist_ok=True)

cluster_df = pd.read_csv(clustered_path)
selected_df = pd.read_csv(final_selection_path)

# === Select One Authority for Briefing === #
briefing_df = selected_df.copy()
briefing_details = pd.merge(briefing_df, cluster_df, on=["Local_authority_code", "Local authority name", "Cluster"], how="left")

# === Save Briefing Sheet === #
briefing_details.to_excel("data/results/briefing.xlsx", index=False)

# === Plot 1: Spend vs Population Scatter with Clusters === #
plt.figure(figsize=(10, 6))
sns.scatterplot(data=cluster_df,
                x="Total_population", y="Total_spend",
                hue="Cluster", palette="Set2", s=100)
plt.title("Cluster-wise Spend vs Population")
plt.xlabel("Total Population")
plt.ylabel("Total Spend")
plt.legend(title="Cluster")
plt.tight_layout()
plt.savefig("plots/cluster_scatter.png")
plt.close()

# === Plot 2: Average Spend by Cluster === #
plt.figure(figsize=(8, 5))
avg_spend = cluster_df.groupby("Cluster")["Total_spend"].mean().reset_index()
sns.barplot(data=avg_spend, x="Cluster", y="Total_spend", palette="Set3")
plt.title("Average Total Spend by Cluster")
plt.xlabel("Cluster")
plt.ylabel("Average Spend")
plt.tight_layout()
plt.savefig("plots/spend_by_cluster.png")
plt.close()

# === Plot 3: Average IMD Score by Cluster === #
plt.figure(figsize=(8, 5))
avg_imd = cluster_df.groupby("Cluster")["IMD - Average score"].mean().reset_index()
sns.barplot(data=avg_imd, x="Cluster", y="IMD - Average score", palette="Set1")
plt.title("Average IMD Score by Cluster")
plt.xlabel("Cluster")
plt.ylabel("Average IMD Score")
plt.tight_layout()
plt.savefig("plots/bar_avg_imd.png")  
plt.close()

# === Plot 4: Stacked Bar Chart - Spend Quartile by Cluster === #
quartile_counts = cluster_df.groupby(["Cluster", "Spend_Quartile"]).size().reset_index(name="count")
quartile_pivot = quartile_counts.pivot(index="Cluster", columns="Spend_Quartile", values="count").fillna(0)
quartile_pivot.plot(kind="bar", stacked=True, figsize=(10, 6), colormap="Pastel1")
plt.title("Spend Quartile Distribution Across Clusters")
plt.xlabel("Cluster")
plt.ylabel("Count")
plt.tight_layout()
plt.savefig("plots/spend_quartiles_by_cluster.png")
plt.close()

print("Stage 5 complete: Results generated including briefing and charts.")
