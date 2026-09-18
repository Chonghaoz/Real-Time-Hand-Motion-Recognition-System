import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
from decision_tree_rule import feature, threshold, left_child, right_child, node_class, is_leaf, label_map, mean_vals, scale_vals

from data_processing import FEATURE_COLUMNS


label_map = {
    0: "ROTATE",
    1: "SHAKE",
    2: "STILL",
    3: "TRANSLATE"
}

def predict_one(raw_row):
    scaled = (raw_row - mean_vals) / scale_vals
    node = 0
    while not is_leaf[node]:
        f = feature[node]
        if scaled[f] <= threshold[node]:
            node = left_child[node]
        else:
            node = right_child[node]
    return label_map[node_class[node]]

# Read board-exported raw features
df = pd.read_csv("./debug/esp32_live_features_translate_2.csv")

# Store results
results = []

for i in range(len(df)):
    row = df.iloc[i][FEATURE_COLUMNS].to_numpy(dtype=float)
    pred = predict_one(row)
    results.append(pred)

# Count summary
total = len(results)
counts = pd.Series(results).value_counts()

print("===== Prediction Summary =====")
print("Total samples:", total)
print()

for action in ["ROTATE", "SHAKE", "STILL", "TRANSLATE"]:
    count = counts.get(action, 0)
    percent = count / total * 100
    print(f"{action}: {count} ({percent:.2f}%)")