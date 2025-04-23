Project Overview
This project analyzes housing support and deprivation across UK local authorities using KMeans clustering and quartile analysis.

## Key Technologies
- Python (pandas, scikit-learn, matplotlib)
- DVC (for data versioning)
- MLflow (for experiment tracking)
- Git & GitHub (for version control)
- Google Cloud Storage (remote data storage)

## ML Model
Used KMeans clustering to group local authorities, followed by quartile-based shortlisting for interviews.

## Note on Data
Data files are tracked via DVC and **not included in this repo**. You’ll need access to the corresponding GCS bucket if authorized.

## MLflow Tracking
Experiment results (e.g., inertia score, selected authorities) were tracked using MLflow.

## Outputs
- `plots/` folder contains visualizations
- `data/model/` includes final authority shortlist
