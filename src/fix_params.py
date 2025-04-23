import yaml

# Proper params dictionary
params = {
    "model_selection": {
        "n_clusters": 5
    }
}

# Write it cleanly without BOM
with open("params.yaml", "w", encoding="utf-8") as f:
    yaml.dump(params, f, default_flow_style=False)

print("Clean params.yaml file written.")